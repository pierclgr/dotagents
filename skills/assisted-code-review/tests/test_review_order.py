"""Tests for scripts/review_order.py, run on temporary git repos."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT: Path = Path(__file__).resolve().parent.parent / "scripts" / "review_order.py"


class GitRepo:
    """Temporary git repository used by a test.

    Attributes:
        root: directory of the repository.
    """

    def __init__(self, root: Path) -> None:
        """Creates an empty repository on branch main.

        Args:
            root: directory of the repository.
        """
        self.root: Path = root
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> str:
        """Runs a git command in the repository.

        Args:
            *args: git arguments.

        Returns:
            The command stdout.
        """
        command: list[str] = ["git", "-c", "user.name=test", "-c", "user.email=test@test", *args]
        return subprocess.run(command, cwd=self.root, check=True, capture_output=True, text=True).stdout

    def write(self, files: dict[str, str]) -> None:
        """Writes files in the working tree.

        Args:
            files: file content by path.
        """
        for path, content in files.items():
            target: Path = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)

    def commit(self, files: dict[str, str]) -> None:
        """Writes files and commits all the changes.

        Args:
            files: file content by path.
        """
        self.write(files)
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", "commit")

    def review_order(self, *args: str, cwd: str = "") -> dict[str, list]:
        """Runs the script in the repository.

        Args:
            *args: script arguments.
            cwd: directory to run from, relative to the repository root.

        Returns:
            The parsed JSON output.
        """
        command: list[str] = [sys.executable, str(SCRIPT), *args]
        out: str = subprocess.run(command, cwd=self.root / cwd, check=True, capture_output=True, text=True).stdout
        return json.loads(out)


def paths(entries: list[dict[str, str]]) -> list[str]:
    """Returns the paths of output entries, in order.

    Args:
        entries: entries of one output section.

    Returns:
        The entry paths.
    """
    return [entry["path"] for entry in entries]


class ReviewOrderTest(unittest.TestCase):
    """End-to-end tests of the review order script."""

    def setUp(self) -> None:
        """Creates a temporary repository."""
        self.tmp: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
        self.repo: GitRepo = GitRepo(Path(self.tmp.name))

    def tearDown(self) -> None:
        """Deletes the temporary repository."""
        self.tmp.cleanup()

    def test_leaves_come_first(self) -> None:
        """a -> b -> c, d gives c, d, b, a."""
        self.repo.commit({"README.md": "readme\n"})
        self.repo.write({
            "a.py": "import b\n",
            "b.py": "import c\nfrom d import f\n",
            "c.py": "",
            "d.py": "def f():\n    pass\n",
        })
        result: dict[str, list] = self.repo.review_order()
        self.assertEqual(paths(result["python"]), ["c.py", "d.py", "b.py", "a.py"])
        self.assertEqual(result["python"][2]["depends_on"], ["c.py", "d.py"])
        self.assertEqual({entry["status"] for entry in result["python"]}, {"added"})

    def test_dependency_through_unchanged_file(self) -> None:
        """a imports unchanged x, x imports c: c comes before a."""
        self.repo.commit({"a.py": "", "c.py": "", "x.py": "import c\n"})
        self.repo.write({"a.py": "import x\n", "c.py": "VALUE = 1\n"})
        result: dict[str, list] = self.repo.review_order()
        self.assertEqual(paths(result["python"]), ["c.py", "a.py"])
        self.assertEqual(result["python"][1]["depends_on"], ["c.py"])
        self.assertEqual(result["python"][1]["status"], "modified")

    def test_import_cycle_kept_together(self) -> None:
        """a <-> b form a cycle, reviewed after their leaf z and before m."""
        self.repo.commit({"README.md": "readme\n"})
        self.repo.write({
            "a.py": "import b\n",
            "b.py": "import a\nimport z\n",
            "m.py": "import a\n",
            "z.py": "",
        })
        result: dict[str, list] = self.repo.review_order()
        self.assertEqual(paths(result["python"]), ["z.py", "a.py", "b.py", "m.py"])
        self.assertEqual(result["python"][1]["cycle"], ["b.py"])
        self.assertEqual(result["python"][2]["cycle"], ["a.py"])
        self.assertEqual(result["python"][0]["cycle"], [])

    def test_sections_for_deleted_and_other_files(self) -> None:
        """Deleted and non-Python files go in their own sections."""
        self.repo.commit({"old.py": "", "notes.md": "notes\n"})
        (self.repo.root / "old.py").unlink()
        self.repo.write({"notes.md": "new notes\n", "new.py": ""})
        result: dict[str, list] = self.repo.review_order()
        self.assertEqual(paths(result["python"]), ["new.py"])
        self.assertEqual(result["deleted"], [{"path": "old.py", "status": "deleted", "old_path": None}])
        self.assertEqual(result["other"], [{"path": "notes.md", "status": "modified", "old_path": None}])

    def test_branch_range_reads_head_revision(self) -> None:
        """Branch mode reads files from the head commit, not the disk."""
        self.repo.commit({"core.py": "def run():\n    return 1\n"})
        self.repo.git("switch", "-q", "-c", "feature")
        self.repo.git("mv", "core.py", "engine.py")
        self.repo.commit({"api.py": "from engine import run\n"})
        self.repo.git("switch", "-q", "main")
        result: dict[str, list] = self.repo.review_order("--base", "main", "--head", "feature")
        self.assertEqual(paths(result["python"]), ["engine.py", "api.py"])
        self.assertEqual(result["python"][0]["status"], "renamed")
        self.assertEqual(result["python"][0]["old_path"], "core.py")

    def test_relative_imports_and_src_layout(self) -> None:
        """Relative imports and src/ package imports are resolved."""
        self.repo.commit({"README.md": "readme\n"})
        self.repo.write({
            "src/pkg/__init__.py": "from .api import serve\n",
            "src/pkg/api.py": "from .core import X\n",
            "src/pkg/core.py": "X = 1\n",
            "tests/test_api.py": "from pkg.api import serve\n",
        })
        result: dict[str, list] = self.repo.review_order(cwd="tests")
        self.assertEqual(
            paths(result["python"]),
            ["src/pkg/core.py", "src/pkg/api.py", "src/pkg/__init__.py", "tests/test_api.py"],
        )

    def test_stdlib_and_package_internals_not_matched(self) -> None:
        """import json and import utils don't match tools/json.py or pkg/utils.py."""
        self.repo.commit({"README.md": "readme\n"})
        self.repo.write({
            "main.py": "import json\nimport utils\n",
            "pkg/__init__.py": "",
            "pkg/utils.py": "",
            "tools/json.py": "",
        })
        result: dict[str, list] = self.repo.review_order()
        main: dict = next(entry for entry in result["python"] if entry["path"] == "main.py")
        self.assertEqual(main["depends_on"], [])

    def test_ambiguous_import_picks_closest_file(self) -> None:
        """import utils from app/main.py matches app/utils.py, not lib/utils.py."""
        self.repo.commit({"README.md": "readme\n"})
        self.repo.write({"app/main.py": "import utils\n", "app/utils.py": "", "lib/utils.py": ""})
        result: dict[str, list] = self.repo.review_order()
        main: dict = next(entry for entry in result["python"] if entry["path"] == "app/main.py")
        self.assertEqual(main["depends_on"], ["app/utils.py"])

    def test_import_module_call_counts_as_import(self) -> None:
        """importlib.import_module("pkg.a") is an import of pkg/a.py."""
        self.repo.commit({"README.md": "readme\n"})
        self.repo.write({"a_test.py": 'import importlib\nmod = importlib.import_module("pkg.a")\n', "pkg/a.py": ""})
        result: dict[str, list] = self.repo.review_order()
        self.assertEqual(paths(result["python"]), ["pkg/a.py", "a_test.py"])

    def test_repo_without_commits(self) -> None:
        """Uncommitted mode works before the first commit."""
        self.repo.write({"a.py": "import b\n", "b.py": ""})
        result: dict[str, list] = self.repo.review_order()
        self.assertEqual(paths(result["python"]), ["b.py", "a.py"])

    def test_unparsed_file_reported(self) -> None:
        """A file with a syntax error is listed in unparsed."""
        self.repo.commit({"README.md": "readme\n"})
        self.repo.write({"bad.py": "def (:\n"})
        result: dict[str, list] = self.repo.review_order()
        self.assertEqual(paths(result["python"]), ["bad.py"])
        self.assertEqual(result["unparsed"], ["bad.py"])


if __name__ == "__main__":
    unittest.main()
