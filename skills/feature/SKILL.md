---
name: feature
description: >-
  Fully implement a feature end-to-end starting from nothing but a
  plain-language description of what it should do: scan the repo for
  context, branch off `dev` (or `main`/`master` if there's no `dev`), break
  the feature down into small nuclear sub-features, plan the
  implementation, then build, test, commit, and push each sub-feature in
  turn until the whole feature is done — finishing by opening a PR. Use
  this whenever the user wants a feature "implemented", "built", "added", or
  shipped end-to-end rather than just sketched out or edited in place — e.g.
  "/feature add CSV export to the reports page", "implement dark mode
  support end to end", "build out the notifications feature described
  below and open a PR when it's done". Trigger on the explicit `/feature`
  invocation as well as on natural-language requests for a full
  description-to-PR implementation, even without the word "skill".
compatibility: >-
  Requires `git`. Opening the PR at the end delegates to the `open-pr`
  skill, which requires the GitHub CLI (`gh`), authenticated.
---

# Feature

Take a feature from a plain-language description all the way to an open
pull request: understand the repo, branch, decompose the feature into small
independently-shippable pieces, plan, then implement/test/commit/push each
piece in turn, and open the PR at the end.

## Respect conventions throughout — check this before anything else

Every decision below (branch naming, commit messages, code style, test
placement, PR format, and how autonomously to operate) should follow
whatever the project and user have already established, rather than a
default baked into this skill. Before scanning the repo, check, in order of
precedence:

1. The target project's own `AGENTS.md` (project conventions win over
   everything else).
2. Any user-level conventions or instructions that apply across projects
   (e.g. a global preferences/conventions file you have access to), for
   things like branch naming, commit style, and how autonomously to
   operate.

In particular, look for any stated preference on **how autonomously to
operate** — e.g. whether to check in before large or multi-step changes.
If one exists, follow it, including at exactly which points it says to
pause. If nothing is stated either way, run the whole pipeline (branch
through opened PR) autonomously, without pausing for approval — only
stopping for the genuine blockers listed in "When to stop" below.

## 1. Deep repo scan

Understand where this feature sits before touching anything. Map the
project's structure and architecture, identify the modules/layers the
feature will touch, and find existing patterns to mirror (how similar
features are structured, tested, and documented elsewhere in the
codebase). Also note the project's code standards and conventions — a
`CONVENTIONS.md`/`AGENTS.md` convention section, linter/formatter config,
or just the prevailing style in the code — so every sub-feature you build
adheres to them.

If the description leaves real ambiguity — multiple reasonable
interpretations of scope, behavior, or where it belongs — stop and ask now.
This is independent of the autonomy setting above: guessing wrong here
wastes the entire pipeline that follows, so always clarify genuine
ambiguity before branching.

## 2. Create the feature branch

Determine the base branch, preferring the most up-to-date ref available:

```bash
git fetch origin
for ref in origin/dev dev origin/main main origin/master master; do
  git show-ref --verify -q "refs/remotes/$ref" 2>/dev/null && { base_ref="$ref"; break; }
  git show-ref --verify -q "refs/heads/$ref" 2>/dev/null && { base_ref="$ref"; break; }
done
```

`base_branch` (the name to later target as the PR base) is `base_ref` with
any `origin/` prefix stripped — i.e. `dev` if a `dev` branch exists at all
(local or remote), otherwise `main`, otherwise `master`. If none exist,
stop and ask rather than guessing a base.

Derive a short (3-6 word) snake_case slug summarizing the feature and
prefix it per the active branch-naming convention (the project's own if
stated, otherwise `feature/snake_case`). E.g. "add CSV export to the
reports page" → `feature/csv_export_reports_page`.

Before creating it, check for collisions
(`git show-ref --verify -q refs/heads/<branch>` and the `origin/` remote
equivalent) — if it already exists, stop and ask whether to resume it or
pick a different name, rather than silently reusing or overwriting it.
Also check the working tree is clean (`git status --porcelain`) — if it
isn't, stop and tell the user rather than stashing or discarding their
in-progress work.

```bash
git checkout -b "$branch" "$base_ref"
```

## 3. Break the feature into nuclear sub-features

Using the scan from step 1, decompose the feature into the smallest pieces
that are each independently implementable, testable, and committable —
ordered so foundational pieces (data model, core logic) come before what
depends on them (UI, wiring). Track them with TaskCreate, one task per
nuclear sub-feature, so progress stays visible and auditable as the
pipeline runs.

## 4. Plan the implementation

For each nuclear sub-feature, work out which files it touches, the concrete
approach, and what tests it needs. Keep this plan lightweight — task
descriptions and your own reasoning are enough; don't write it to a
committed planning document unless the project already keeps one for this
purpose.

## 5-7. Implement, test, commit, and push each sub-feature, then repeat

For each sub-feature, in the order planned:

1. Implement it adhering to the repository's code standards, architecture,
   and conventions, matching the style and patterns found in step 1.
2. Add or update tests that exercise it, and keep documentation (docstrings,
   comments, README/docs, the project's `AGENTS.md` convention sections)
   up to date with what changed.
3. Run the relevant tests/build. If something fails, fix it before moving
   on. If it still won't pass after a real effort, stop and report the
   specific failure rather than pushing broken code or silently skipping
   it.
4. Stage and commit only the files for this sub-feature — one commit per
   nuclear piece, not one giant commit at the end. Write the message per
   the project's/user's commit conventions (if none stated: past tense,
   short, compact, naming the file(s) affected).
5. Push: `git push -u origin "$branch"` the first time, `git push` after.
6. Mark the corresponding task complete and move to the next sub-feature.

Repeat until every nuclear sub-feature is implemented, tested, committed,
and pushed.

## 8. Open the PR

Once everything is committed and pushed, run the full test/build suite once
more as a final sanity check. Then invoke the `open-pr` skill with
`base_branch` (from step 2) as the target — it already knows how to read
the project's PR conventions and write the title/body, so don't duplicate
that logic here. Report the returned PR URL to the user.

## When to stop and ask (regardless of the autonomy setting)

- The feature description is genuinely ambiguous (step 1).
- No recognizable base branch exists, the working tree is dirty, the
  target branch name already exists, or there's no `origin` remote / `gh`
  isn't authenticated.
- You're invoked while already on a non-base branch (e.g. mid-feature) —
  ask whether to resume that work or start fresh, rather than assuming.
- A sub-feature's tests won't pass after real effort.
- The scan reveals the feature already exists or conflicts with other
  in-flight work.

## Notes

- Never force-push or rewrite already-pushed history without being asked.
- A repo with no test runner at all is a gap to note, not a reason to block
  forever — implement carefully and say so when reporting progress.
