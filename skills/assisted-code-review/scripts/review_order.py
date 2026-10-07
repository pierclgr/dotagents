"""Sort changed files for a bottom-up code review.

Lists the files changed in a revision range (or in the working tree) and sorts
the changed Python files so that each file comes after every changed file it
imports, directly or through unchanged files. Imports include
``import_module("name")`` calls with a literal absolute name. Files in an
import cycle stay next to each other. Among files ready at the same time, the
smaller path comes first. Non-Python and deleted files are returned unsorted,
for the caller to place.

Import resolution is a heuristic: a module name is matched against the repo
files, using as import roots the repo root and every directory that is not a
regular package (no ``__init__.py``). Standard library names are skipped. If
several files match, the one closest to the importing file wins.

Usage:
    python3 review_order.py                            # uncommitted changes
    python3 review_order.py --base main --head feature # base...head changes

Output, JSON on stdout:
    python: changed Python files in review order. Each entry has ``path``,
        ``status`` (added, modified or renamed), ``old_path`` (before a
        rename), ``depends_on`` (changed files it imports, directly or through
        unchanged files) and ``cycle`` (other files in its import cycle).
    other: changed non-Python files, with ``path``, ``status``, ``old_path``.
    deleted: deleted files, same fields.
    unparsed: changed Python files whose imports could not be read.
"""

import argparse
import ast
import json
import os
import subprocess
import sys
import warnings
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

STATUS: dict[str, str] = {
    "A": "added",
    "D": "deleted",
    "M": "modified",
    "R": "renamed",
    "T": "modified",
    "U": "modified",
}


@dataclass
class Change:
    """A file changed in the reviewed range.

    Attributes:
        path: path of the file, relative to the repo root.
        status: added, modified, deleted or renamed.
        old_path: path before a rename, else None.
    """

    path: str
    status: str
    old_path: str | None = None


class ModuleIndex:
    """Maps Python import names to the repo files that define them.

    Attributes:
        modules: file by full dotted name from the repo root.
        by_suffix: files by every dotted name they can be imported with.
    """

    def __init__(self, paths: list[str]) -> None:
        """Indexes the given Python files.

        Args:
            paths: Python file paths, relative to the repo root.
        """
        packages: set[str] = {os.path.dirname(p) for p in paths if os.path.basename(p) == "__init__.py"}
        self.modules: dict[str, str] = {}
        self.by_suffix: dict[str, list[str]] = defaultdict(list)
        for path in sorted(paths):
            parts: list[str] = path.removesuffix(".py").split("/")
            if parts[-1] == "__init__":
                parts.pop()
            if not parts:
                continue
            self.modules[".".join(parts)] = path
            # a module is importable from the repo root or from any non-package directory
            for start in range(len(parts)):
                if start == 0 or "/".join(parts[:start]) not in packages:
                    self.by_suffix[".".join(parts[start:])].append(path)

    def imports_of(self, path: str, tree: ast.Module) -> set[str]:
        """Returns the repo files imported by a Python file.

        Args:
            path: path of the importing file.
            tree: parsed source of the importing file.

        Returns:
            Paths of the imported repo files, without ``path`` itself.
        """
        package: list[str] = path.split("/")[:-1]
        names: list[tuple[str, bool]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names += [(alias.name, False) for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names += [(f"{node.module}.{alias.name}", False) for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level <= len(package) + 1:
                base: list[str] = package[:len(package) + 1 - node.level] + ([node.module] if node.module else [])
                names += [(".".join(base + [alias.name]), True) for alias in node.names]
            elif (
                isinstance(node, ast.Call)
                and getattr(node.func, "attr", getattr(node.func, "id", None)) == "import_module"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and not node.args[0].value.startswith(".")
            ):
                names.append((node.args[0].value, False))
        found: set[str] = {file for name, relative in names if (file := self._find(name, path, relative))}
        found.discard(path)
        return found

    def _find(self, name: str, importer: str, relative: bool) -> str | None:
        """Returns the file defining the longest prefix of a dotted name.

        Args:
            name: dotted name, e.g. ``pkg.mod.func``.
            importer: path of the importing file, to break ties.
            relative: whether ``name`` comes from a relative import, so it is
                a full name from the repo root.

        Returns:
            The matching file, or None if no prefix of ``name`` is in the repo.
        """
        parts: list[str] = name.split(".")
        if not relative and parts[0] in sys.stdlib_module_names:
            return None
        for end in range(len(parts), 0, -1):
            prefix: str = ".".join(parts[:end])
            if relative and prefix in self.modules:
                return self.modules[prefix]
            if not relative and prefix in self.by_suffix:
                return max(self.by_suffix[prefix], key=lambda file: len(os.path.commonpath([file, importer])))
        return None


def git(*args: str, stdin: bytes | None = None) -> bytes:
    """Runs a git command.

    Args:
        *args: git arguments.
        stdin: data sent to the command input.

    Returns:
        The command stdout.
    """
    return subprocess.run(["git", *args], input=stdin, stdout=subprocess.PIPE, check=True).stdout


def split_z(out: bytes) -> list[str]:
    """Splits NUL-terminated git output.

    Args:
        out: git output produced with ``-z``.

    Returns:
        The output fields.
    """
    return out.decode().split("\0")[:-1]


def changed_files(base: str | None, head: str | None) -> list[Change]:
    """Lists the changed files.

    Args:
        base: base revision, or None for uncommitted changes.
        head: head revision, or None for uncommitted changes.

    Returns:
        The changed files, sorted by path.
    """
    untracked: list[str] = []
    if head is None:
        has_head: bool = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], stdout=subprocess.DEVNULL).returncode == 0
        # a repo without commits is compared to the empty tree
        diff_range: str = "HEAD" if has_head else git("hash-object", "-t", "tree", "/dev/null").decode().strip()
        untracked = split_z(git("ls-files", "-z", "--others", "--exclude-standard"))
    else:
        diff_range = f"{base}...{head}"
    fields: list[str] = split_z(git("diff", "--no-color", "--name-status", "-z", "-M", diff_range))
    changes: list[Change] = [Change(path, "added") for path in untracked]
    i: int = 0
    while i < len(fields):
        if fields[i].startswith("R"):
            changes.append(Change(fields[i + 2], "renamed", fields[i + 1]))
            i += 3
        else:
            changes.append(Change(fields[i + 1], STATUS[fields[i][0]]))
            i += 2
    return sorted(changes, key=lambda change: change.path)


def python_files(head: str | None) -> list[str]:
    """Lists all the Python files of the reviewed code.

    Args:
        head: head revision, or None for the working tree.

    Returns:
        The Python file paths, sorted.
    """
    if head is None:
        listed: list[str] = split_z(git("ls-files", "-z", "--cached", "--others", "--exclude-standard"))
        return sorted({path for path in listed if path.endswith(".py") and os.path.isfile(path)})
    return sorted(path for path in split_z(git("ls-tree", "-r", "-z", "--name-only", head)) if path.endswith(".py"))


def read_sources(head: str | None, paths: list[str]) -> dict[str, bytes]:
    """Reads files at a revision, or from the working tree.

    Args:
        head: head revision, or None for the working tree.
        paths: paths of the files to read.

    Returns:
        File content by path.
    """
    if head is None:
        return {path: Path(path).read_bytes() for path in paths}
    out: bytes = git("cat-file", "--batch", stdin="".join(f"{head}:{path}\n" for path in paths).encode())
    sources: dict[str, bytes] = {}
    pos: int = 0
    # each object is "<oid> <type> <size>\n<content>\n"
    for path in paths:
        header_end: int = out.index(b"\n", pos)
        size: int = int(out[pos:header_end].split()[2])
        sources[path] = out[header_end + 1:header_end + 1 + size]
        pos = header_end + size + 2
    return sources


def reach(start: str, graph: dict[str, set[str]], stop: set[str]) -> set[str]:
    """Returns the nodes reachable from a node.

    Args:
        start: node to start from.
        graph: neighbours of each node.
        stop: nodes that are collected but not walked past.

    Returns:
        The reachable nodes.
    """
    seen: set[str] = set()
    stack: list[str] = list(graph.get(start, ()))
    while stack:
        node: str = stack.pop()
        if node not in seen:
            seen.add(node)
            if node not in stop:
                stack.extend(graph.get(node, ()))
    return seen


def review_order(changed: list[str], imports: dict[str, set[str]]) -> list[tuple[str, set[str], set[str]]]:
    """Sorts changed files bottom-up: a file comes after the files it imports.

    Args:
        changed: changed file paths.
        imports: repo files imported by each repo file.

    Returns:
        ``(path, depends_on, cycle)`` for each changed file, in review order.
    """
    changed_set: set[str] = set(changed)
    direct: dict[str, set[str]] = {file: reach(file, imports, changed_set) & changed_set - {file} for file in changed}
    closure: dict[str, set[str]] = {file: reach(file, direct, set()) for file in changed}
    cycle: dict[str, set[str]] = {file: {other for other in closure[file] if file in closure[other]} - {file} for file in changed}
    order: list[str] = []
    done: set[str] = set()
    while len(order) < len(changed):
        first: str = min(file for file in changed if file not in done and closure[file] - cycle[file] - {file} <= done)
        group: list[str] = sorted(cycle[first] | {first})
        order += group
        done.update(group)
    return [(file, direct[file] - cycle[file], cycle[file]) for file in order]


def main() -> None:
    """Prints the review order of the changed files as JSON."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Sort changed files for a bottom-up code review.")
    parser.add_argument("--base", help="base revision, used with --head")
    parser.add_argument("--head", help="head revision, used with --base")
    args: argparse.Namespace = parser.parse_args()
    if bool(args.base) != bool(args.head):
        parser.error("--base and --head must be used together")
    os.chdir(git("rev-parse", "--show-toplevel").decode().strip())
    warnings.simplefilter("ignore", SyntaxWarning)

    changes: list[Change] = changed_files(args.base, args.head)
    paths: list[str] = python_files(args.head)
    index: ModuleIndex = ModuleIndex(paths)
    imports: dict[str, set[str]] = {}
    unparsed: set[str] = set()
    for path, source in read_sources(args.head, paths).items():
        try:
            imports[path] = index.imports_of(path, ast.parse(source))
        except (SyntaxError, ValueError):
            unparsed.add(path)

    by_path: dict[str, Change] = {change.path: change for change in changes}
    python: list[str] = [change.path for change in changes if change.status != "deleted" and change.path.endswith(".py")]
    result: dict[str, list] = {
        "python": [
            asdict(by_path[path]) | {"depends_on": sorted(depends_on), "cycle": sorted(cycle)}
            for path, depends_on, cycle in review_order(python, imports)
        ],
        "other": [asdict(change) for change in changes if change.status != "deleted" and not change.path.endswith(".py")],
        "deleted": [asdict(change) for change in changes if change.status == "deleted"],
        "unparsed": sorted(unparsed & set(python)),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
