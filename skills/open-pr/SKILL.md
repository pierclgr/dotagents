---
name: open-pr
description: >-
  Open a GitHub pull request from the current branch to a target branch, with a
  title and body that follow the user's conventions. Use this whenever the user
  wants to open, create, raise, or submit a PR / pull request / MR from their
  branch — e.g. "open a PR", "open PR", "PR this", "PR this to develop",
  "create a pull request", "raise a PR against main", "submit this branch for
  review". If the user names
  a target branch, use it; if not, auto-detect the parent branch the current one
  was created from. Trigger even when the user doesn't say the word "skill".
compatibility: Requires `git` and the GitHub CLI (`gh`), authenticated (`gh auth status`).
---

# Open PR

Open a pull request from the current branch (the head) to a target branch (the
base), writing the title and description according to the user's conventions.

## When the target branch is given vs. not

- **User specified a target** (e.g. "PR this to `develop`") → that is the base.
- **User did not specify** → auto-detect the branch the current one was created
  from, using the bundled script (see below). Git has no real "parent branch",
  so this is a heuristic; if it can't be determined, fall back to the repository
  default branch (main/master) without asking.

## Workflow

Run these steps in order. Stop and report if a precondition fails.

### 1. Preconditions
- Confirm you're in a git repo: `git rev-parse --is-inside-work-tree`.
- Confirm `gh` is authenticated: `gh auth status` (if not, tell the user to run
  `gh auth login` — suggest they type `! gh auth login`).
- Get the current branch: `git rev-parse --abbrev-ref HEAD`. If it's the base
  branch itself (e.g. `main`), stop — there's nothing to PR.

### 2. Resolve the base branch
- If the user named a target branch, use it. Verify it exists
  (`git show-ref --verify -q refs/heads/<b>` or `refs/remotes/origin/<b>`); if
  it doesn't, tell the user rather than guessing.
- Otherwise run the detector (in this skill's own `scripts/` directory) and use
  its output:
  ```bash
  bash ~/.claude/skills/open-pr/scripts/detect_base_branch.sh
  ```
  If it prints a branch, that's the base. If it prints nothing, fall back to the
  repo default:
  ```bash
  gh repo view --json defaultBranchRef -q .defaultBranchRef.name
  ```
- Sanity check: base must differ from the current branch.

### 3. Check there's something to merge
- `git log --oneline <base>..HEAD`. If empty, stop — no commits to open a PR
  for. Also detect an existing PR: `gh pr view --json url,state` — if one is
  already open for this branch, report its URL instead of creating a duplicate.

### 4. Push the current branch
- Push automatically (the user opted into this): `git push -u origin HEAD`.
  This is safe and expected; no need to ask first.

### 5. Write title and body per conventions
Read the user's conventions and follow the **Pull requests** section:
```bash
cat ~/.claude/CONVENTIONS.md
```
Apply whatever the file specifies for PR **title** and **description**. If the
file is missing, or has no PR-specific rules, use the default format below.

To pick a title prefix / tone, use the commits (`git log <base>..HEAD`) and the
branch name (e.g. `feature/*`, `fix/*`) as signals for whether this is a feature
or a fix.

**Default format** (only when conventions don't specify one):
- Title: a short, imperative summary of the change.
- Body: a one-line headline of what the change does, then a bulleted list of the
  concrete changes. No test plan. No mention of AI/coding agents.

### 6. Create the PR
Create a ready (non-draft) PR. Pass the body via a temp file or `--body` to keep
formatting intact:
```bash
gh pr create --base <base> --head <current> --title "<title>" --body "<body>"
```
Then print the returned PR URL to the user.

## Notes
- Never invent commits or force-push. Only push the current branch as-is.
- If `gh pr create` reports the branch has no upstream / asks where to push, the
  push in step 4 should have handled it; re-run the push if needed.
- Keep the body faithful to the actual diff — summarize the real commits, don't
  speculate about intent beyond what the changes show.
