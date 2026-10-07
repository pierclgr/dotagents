---
name: assisted-code-review
description: >-
  Guide the user through their own review of a PR, a branch, or uncommitted
  changes, one file at a time, bottom-up: files with no internal imports first,
  then the files that use them. First shows a table of all added, modified and
  deleted files in review order, with a summary of each. Then presents each
  file with its diff and possible issues, answers the user's questions, and
  moves to the next file when the user says so, staging each reviewed file
  when the changes are uncommitted. Use this whenever the user wants to review
  changes themselves with your help, e.g. "let's review PR 42", "help me
  review my changes", "walk me through this branch file by file", "review my
  uncommitted files before I commit", "assisted review", even if they don't
  name the skill. Not for one-shot automated reviews where the user only wants
  a list of bugs.
compatibility: >-
  Requires `git` and Python 3.10+. PR review needs the GitHub CLI (`gh`),
  authenticated.
---

# Assisted Code Review

The user reviews the code; you assist. You set the order, show each file, point
out possible issues and answer questions. The user decides when a file is done.

The order is bottom-up so that, when a file comes up, every changed file it
uses was already reviewed: the user already knows the building blocks.

## 1. Pick the target

| Target      | User says, e.g.                 | Range                      |
|-------------|---------------------------------|----------------------------|
| PR          | "PR 42", a PR URL               | `<base>...<headRefOid>`    |
| Branch      | "branch feature/x", "my branch" | `<base>...<branch>`        |
| Uncommitted | "my changes", "before I commit" | working tree vs `HEAD`     |

If the user names no target: when `git status --porcelain` is not empty,
review the uncommitted changes; otherwise review the current branch. Say in
one line what you picked, so the user can correct you.

**PR.** Get the refs without touching the working tree:
```bash
gh pr view <n> --json title,baseRefName,headRefOid
git fetch origin <baseRefName> pull/<n>/head
```
Base is `origin/<baseRefName>`, head is `<headRefOid>`. If the PR branch is not
checked out, the user's editor shows different code: offer `gh pr checkout <n>`
(only when the working tree is clean).

**Branch.** Head is the branch. Base is the branch the user names. If they name
none and the branch is the current one, detect it with the `open-pr` skill's
script:
```bash
bash ~/.claude/skills/open-pr/scripts/detect_base_branch.sh
```
If that is not possible or it prints nothing, use the default branch:
`git symbolic-ref --short refs/remotes/origin/HEAD`.

## 2. Compute the review order

Run the bundled script (in this skill's `scripts/` directory) from the repo:
```bash
python3 ~/.claude/skills/assisted-code-review/scripts/review_order.py
python3 ~/.claude/skills/assisted-code-review/scripts/review_order.py --base <base> --head <head>
```
With no arguments it reads the uncommitted changes: staged, unstaged and
untracked. It prints JSON:
- `python`: changed Python files, already in review order. Each has `path`,
  `status`, `old_path` (renames), `depends_on` (changed files it imports,
  directly or through unchanged files) and `cycle` (files in the same import
  cycle; they stay next to each other).
- `other`: changed non-Python files, not sorted.
- `deleted`: deleted files.
- `unparsed`: Python files whose imports could not be read (e.g. syntax
  errors). Read their imports yourself and move them if needed.

Import matching is a heuristic. If, while reading the code, you see that the
order is clearly wrong, fix it.

Build the final order in three blocks:
1. **Code, bottom-up.** The `python` list as given, then the code files in
   other languages from `other` (JS/TS, Go, Rust, Java, shell, SQL, ...). For
   those, read the imports yourself and apply the same rule: a file comes after
   every changed file it imports, directly or through unchanged files; files in
   a cycle stay together; ties go by path.
2. **Deleted files**, from `deleted`.
3. **Non-code files** from `other`: docs, configs, data, lock files, etc.

## 3. Show the table

Read the diff of every file to write its summary:
- Uncommitted: `git diff HEAD -- <path>`. For untracked files, or when the repo
  has no commits yet, read the file.
- PR or branch: `git diff <base>...<head> -- <path>`. For a rename, pass
  `<old_path> <path>`.

Then show the table, using this format:

```markdown
**Review target:** <target>, <N> files

| # | Path              | Change   | Summary                                 |
|---|-------------------|----------|-----------------------------------------|
| 1 | `src/pkg/core.py` | modified | Math helpers. Adds `clamp()` for the API. |
| 2 | `src/pkg/api.py`  | added    | HTTP API. New `/limits` endpoint.         |
```
- Target: `PR #42 "<title>"`, `` branch `x` vs `main` `` or
  `uncommitted changes`.
- Change: `added`, `modified`, `deleted` or `renamed` (for renames, write
  `old → new` in the Path column).
- Summary: one or two short sentences: what the file is, then what the change
  brings. For files in an import cycle, add "import cycle with #5".

Then go straight to file #1.

## 4. Review one file at a time

Present the current file in this format, then stop and wait for the user:

````markdown
### <k>/<N> · `<path>` (<change>)

**What it is:** <role of the file in the codebase>
**What changed:** <the change in plain words; name the reviewed files it relies
on, e.g. "uses `clamp()` from #1">

```diff
<diff of the file>
```

**Possible issues:**
- `<path>:<line>`: <problem>. <why it matters>
````

**Diff.** Show the whole diff of the file. If it is very long (as a rough guide,
over 300 lines, e.g. a big new file), show the structure (classes, functions,
what each does) and the most important parts instead. Tell the user what you
left out; they can read it in their editor or ask for it.

**Possible issues.** Only real problems: bugs, missed edge cases, broken
contracts with callers or with files already reviewed, security risks, new
logic without tests, performance traps. Look beyond the diff when needed
(callers, imported files). Skip style nitpicks. If you are not sure, say
"possible" and why. If you find nothing, write "None found."; don't invent
issues to fill the section.

**Questions.** Then answer the user's questions:
- Base every answer on the code. Read other files when needed. Cite
  `path:line`.
- Don't change code unless the user asks. If they ask for a fix, make it and
  show it.
- If the user wants to jump to another file, skip one or change the order,
  follow them.

### Moving on

When the user says the file is done ("next", "ok", "done", "LGTM", ...):
1. **Uncommitted target only:** stage the file.
   ```bash
   git add -- <path>
   git add -- <old_path> <path>
   ```
   Use the second form for renames. `git add` also stages new files and
   deletions. Confirm in one line ("Staged `<path>`."). Staging marks what is
   reviewed: what is still unstaged at the end was not reviewed. So don't stage
   skipped files, and if you edit an already staged file on request, tell the
   user it now has unstaged changes. For PR or branch targets there is nothing
   to stage.
2. Present the next file in the same format.

## 5. Wrap up

After the last file, give a short wrap-up:
- Files reviewed and files skipped.
- Issues still open (fixes agreed but not done, open questions), with
  `path:line`.
- Uncommitted target: run `git status --short` and confirm the reviewed files
  are staged. Don't commit.
