---
name: complexity-refactor
description: >-
  Deeply analyze a repository's computational complexity (algorithmic inefficiency, wasted runtime/memory), report the findings to the user, ask which ones to implement, and only then refactor the selected ones — as pure, behavior-preserving changes verified end to end by the existing test suite, committing each step separately. Never implements anything before the user reviews the findings. Use when users say code is "slow", ask to "speed this up" / "optimize this" (algorithmic, not micro-benchmarking) or "why is this so slow", or flag an accidental O(n²), repeated expensive work in a loop, N+1 queries, or unbounded memory use. Not for design or implementation complexity (over-engineering, dead code, god objects, coupling, duplication, deep nesting): use engineering-refactor for that.
compatibility: >-
  Requires `git` and the target repo's test runner (whatever it uses). Uses profilers, benchmarks or timing tests when already available to confirm and measure hotspots, but never installs new heavyweight tooling — falls back to reading the code and reasoning about complexity classes where none is present.
---

# Complexity Refactor

A codebase accrues **computational** complexity as it grows: inefficient algorithms, wasted runtime and memory. This skill finds the highest-leverage instances, reports them to the user, and — only for the findings the user selects — refactors them, while treating one thing as non-negotiable: **the software's observable behavior does not change.** Every change made here is a pure refactor — same inputs produce the same outputs, the same side effects, the same public API — just cheaper to run. Cost goes down; functionality does not move.

It works in three steps, and the user decides at the second one:

1. **Analyze and report**: find the findings and show them to the user.
2. **Ask**: the user reviews the findings and selects which ones to implement.
3. **Implement**: apply only the selected findings, verified by tests.

The skill is never autonomous from finding to implementation. No file is changed before the user has selected the findings.

Design and implementation complexity (over-engineering, dead code, god objects, coupling, duplication, deep nesting) is out of scope: it belongs to the `engineering-refactor` skill.

## The behavior-preservation invariant

This is what separates a refactor from a rewrite, and it is the guardrail for everything below:

- No implementation without selection. Phases 0 to 3 are read-only. Change files only after the user answers the question in Phase 3, and only for the findings the user selected.
- Never change a function's or module's observable inputs/outputs, side effects, or public signatures as part of a complexity fix. If removing some complexity genuinely requires an API change, that is a design decision for the user to make, not you — mark that finding **behavior change** in the report (Phase 3). It is implemented only if the user selects it.
- Every change must be verified by the test suite, not just argued for. Run the relevant tests, then the full suite, after each change and before moving to the next one. A change that is not verified green does not get to stay.
- If the code you are about to touch has no test covering its current behavior, that is a gap in the safety net, not a green light to proceed anyway. Close the gap first (Phase 4) instead of refactoring on faith.

## Phase 0 — Scope and baseline (read-only)

- Determine the target: the whole repo, or a path/module the user named. If it is a monorepo with clearly unrelated sub-projects and the user just said "the codebase," ask which one they mean rather than guessing.
- Detect the language(s) and how to run the test suite the same way you would for any repo task: check `pyproject.toml`/`pytest.ini`, `package.json`'s `scripts.test`, `go.mod`, `Cargo.toml`, `Gemfile`, etc., and confirm the exact command rather than assuming — projects customize these.
- Check the working tree is clean (`git status --porcelain`). If it is not, stop and tell the user rather than refactoring on top of unrelated in-progress work.
- Run the full suite once to record a baseline. If it is already failing or will not run at all, stop and report that first — there is no way to distinguish a pre-existing failure from one you introduced, so refactoring on a broken baseline is unverifiable by construction.

## Phase 1 — Map the repository

Build a picture of entry points, the main data flows, and where the data is large before deciding what to look at: request handlers, batch jobs, loops over datasets, database access. Use a read-only exploration subagent for this if one is available and the repo is large enough that reading it all inline would be wasteful. This is where hot paths and the real input sizes surface.

## Phase 2 — Deep complexity analysis

Read with both breadth (what does each major component do, how do they connect) and depth (for anything that looks like a hotspot, trace its actual callers and call frequency, not just the code in isolation). Use whichever of these patterns applies — they are lenses, not a checklist:

| Pattern | Why it is costly |
|---|---|
| Nested loops over the same collection | often an accidental O(n²)+ where O(n) or O(n log n) is achievable |
| Repeated expensive work inside a loop | re-querying, re-parsing, or re-computing an invariant every iteration instead of once |
| List/array membership tests in hot paths | O(n) lookup where a set/dict/index would be O(1) |
| N+1 query patterns | one query per row instead of a single batched query |
| Unbounded loading into memory | reading a whole dataset/file where streaming or pagination would do |
| Recursive algorithms without memoization | recomputing overlapping subproblems, often exponentially |

Use whatever profilers, benchmarks or timing tests the repo already has to confirm and quantify what you find — do not install new tooling for this; if nothing is available, reason from the code (complexity class, input size, call frequency) and say so in the report rather than fabricating numbers.

For every candidate, trace where it is actually called from and at what scale before recording it. A theoretically O(n²) loop over a list that never holds more than five items is not a priority. False hotspots waste the one thing an analysis cannot get back: trust in the result.

## Phase 3 — Report the findings and ask (stop here)

Show the findings in the conversation, not in a file, ordered by priority (impact high to low, risk low to high). Give each finding an ID and these fields:

- **Where**: file(s) and function(s).
- **Issue**: the costly pattern, with its current complexity class or cost, and the real scale it runs at.
- **Proposed change**: the transformation and the expected complexity class or cost, in one or two lines.
- **Type**: `safe refactor` (behavior-preserving) or `behavior change` (e.g. needs an API change, a package split or a persisted-format change).
- **Impact / risk / effort**: low, medium or high.

Use this layout:

```
# Complexity findings: <repo/target name>

## Baseline
<test status · timing/benchmark numbers if available>

## Findings
| ID | Where | Issue | Proposed change | Type | Impact / risk / effort |
|---|---|---|---|---|---|

## Not analyzed
<areas skipped, tools missing, or things you could not verify — or _(none)_>
```

Then **ask the user which findings to implement**: all, a list of IDs, or none. Wait for the answer. Do not start any change before it. If the user asks questions or changes the list, answer and confirm the final list again.

## Phase 4 — Implement the selected findings, one at a time

Before the first change:

- If the current branch is a protected/base branch (`main`/`master`/`dev`), create a new branch — use the target project's own branch-naming convention if its `AGENTS.md`/`CONVENTIONS.md` defines one for this kind of work, otherwise default to `refactor/<short_snake_case_slug>`. If you are already on a feature/fix branch (e.g. invoked mid-feature to clean up before a PR), just work there — do not force a new branch.
- If the area you are about to touch has no tests at all, write minimal characterization tests first — enough to lock in current behavior for representative inputs and edge cases. This is scoped to what you are actually changing; it is not a mandate to build out a full test suite for the whole repo.

Then, for each selected finding, in the agreed order:

1. Apply the proposed change. A `safe refactor` keeps the same inputs, outputs, side effects and public signatures. If it turns out to need a public change that the finding did not say, stop and ask the user instead of changing behavior silently.
2. Run the targeted tests, then the full suite. If anything goes red, fix it within this step or roll the change back — never move to the next finding on top of a failing suite.
3. Commit this change alone, following the project's/user's commit conventions. One commit per finding, not one giant commit at the end — it keeps every step independently reviewable and revertable.
4. Re-measure the specific metric that motivated the change (an actual complexity-class improvement, measured time or memory on a representative input) so the report can state a real delta, not just an assertion.

## Phase 5 — Final verification

Run the full suite once more end to end. Where benchmarks or timing tests were available in Phase 2, rerun them to compare before and after. Confirm that only the selected findings changed the code, and that no public API or observable behavior changed except in the `behavior change` findings the user selected — list any signature you touched and call out any exception loudly rather than glossing over it.

## Phase 6 — Final report

Output the report directly in the conversation — do not write it to a file unless asked. Use this structure:

```
# Complexity refactor: <repo/target name>

## Baseline
<test status before · key metrics before, if available>

## Changes made
1. <finding ID — file(s) — issue → transformation — metric before → after — commit>
2. ...

## Findings not implemented
- <finding ID — reason (not selected / deferred) — suggested next step>

## Final state
<test status after · metric deltas · any coverage gaps closed>
```

If a section is empty, write `_(none)_` rather than omitting it.

## When to stop and ask

- The target is ambiguous (a monorepo, unclear which sub-project).
- The baseline test suite is already failing, or will not run at all, and the target has real logic worth refactoring (not just config).
- The working tree is dirty.
- Behavior that needs to stay identical cannot be exercised by tests at all (e.g. it depends on production credentials or specific hardware) — do not guess at a characterization; ask how the user wants to verify it.

## Notes

- Never force-push or rewrite already-pushed history.
- Do not touch code adjacent to what you are refactoring just because it looks improvable too — add it as a finding in the report, do not fix it. Staying surgical is what makes the process trustworthy.
- Design and implementation problems (over-engineering, dead code, god objects, coupling, duplication) are out of scope: point the user to the `engineering-refactor` skill.
- A repo with no test runner detectable at all is a genuine blocker for refactoring anything with real logic — report it rather than proceeding on faith across the whole repo.
