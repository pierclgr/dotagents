---
name: complexity-refactor
description: >-
  Deeply analyze a repository's computational complexity (algorithmic
  inefficiency, wasted runtime/memory) and architectural complexity (god
  objects, tight coupling, duplication, deep nesting, SOLID violations),
  then autonomously refactor the highest-leverage offenders — as pure,
  behavior-preserving changes verified end to end by the existing test
  suite, committing each step separately. Use this whenever the user says
  a codebase/file/function is "too complex", "a mess", "hard to
  maintain", "bloated", or "growing out of control", asks to "reduce
  complexity", "simplify the architecture", "clean up technical debt",
  "speed this up" / "optimize this" (algorithmic, not micro-benchmarking),
  "reduce coupling", or "break up this god class", or flags excessive
  duplication, deep nesting, or too many components/classes/functions for
  what the project actually does. Trigger even without the words
  "refactor" or "complexity" — e.g. "this file has gotten out of hand",
  "why is this so slow", "there's way too much going on in this module".
compatibility: >-
  Requires `git` and the target repo's test runner (whatever it uses).
  Uses language-specific static-analysis tools when already installed
  (e.g. radon/lizard for Python, eslint complexity rules for JS/TS,
  gocyclo for Go) but never installs new heavyweight tooling — falls back
  to manual reading and heuristics where no tool is present.
---

# Complexity Refactor

A codebase accrues two independent kinds of complexity as it grows:
**computational** (inefficient algorithms, wasted runtime/memory) and
**architectural** (too many moving parts, tangled dependencies, god
objects, duplication). This skill finds the highest-leverage instances of
both and refactors them — end to end, autonomously — while treating one
thing as non-negotiable: **the software's observable behavior does not
change.** Every change made here is a pure refactor — same inputs produce
the same outputs, the same side effects, the same public API — just
cheaper to run and simpler to reason about. Complexity goes down;
functionality does not move.

## The behavior-preservation invariant

This is what separates a refactor from a rewrite, and it is the guardrail
for everything below:

- Never change a function's or module's observable inputs/outputs, side
  effects, or public signatures as part of a complexity fix. If removing
  some complexity genuinely requires an API change, that is a design
  decision for the user to make, not you — surface it as a **deferred
  finding** (Phase 3) instead of making the call unilaterally.
- Every change must be verified by the test suite, not just argued for.
  Run the relevant tests, then the full suite, after each change and
  before moving to the next one. A change that is not verified green does
  not get to stay.
- If the code you are about to touch has no test covering its current
  behavior, that is a gap in the safety net, not a green light to proceed
  anyway. Close the gap first (Phase 0) instead of refactoring on faith.

## Phase 0 — Scope and establish a safety net

- Determine the target: the whole repo, or a path/module the user named.
  If it is a monorepo with clearly unrelated sub-projects and the user
  just said "the codebase," ask which one they mean rather than guessing.
- Detect the language(s) and how to run the test suite the same way you
  would for any repo task: check `pyproject.toml`/`pytest.ini`,
  `package.json`'s `scripts.test`, `go.mod`, `Cargo.toml`, `Gemfile`, etc.,
  and confirm the exact command rather than assuming — projects
  customize these.
- Check the working tree is clean (`git status --porcelain`). If it
  is not, stop and tell the user rather than refactoring on top of
  unrelated in-progress work.
- Run the full suite once to record a baseline. If it is already failing
  or will not run at all, stop and report that first — there is no way
  to distinguish a pre-existing failure from one you introduced, so
  refactoring on a broken baseline is unverifiable by construction.
- If the area you are about to touch has no tests at all, write minimal
  characterization tests first — enough to lock in current behavior for
  representative inputs and edge cases — before refactoring it. This is
  scoped to what you are actually changing; it is not a mandate to build
  out a full test suite for the whole repo.
- Decide where to work: if the current branch is a protected/base branch
  (`main`/`master`/`dev`), create a new branch before changing anything —
  use the target project's own branch-naming convention if its
  `AGENTS.md`/`CONVENTIONS.md` defines one for this kind of work,
  otherwise default to `refactor/<short_snake_case_slug>`. If you are
  already on a feature/fix branch (e.g. invoked mid-feature to clean up
  before a PR), just work there — do not force a new branch.

## Phase 1 — Map the repository

Build a picture of entry points, modules, layers, and which way
dependencies actually flow before deciding what to touch. Use the
`Explore` agent for this if the repo is large enough that reading it all
inline would be wasteful. From imports/requires, sketch which modules
depend on which — this is where dependency cycles, god modules (nearly
everything imports them, they import almost nothing), and suspiciously
high fan-in/fan-out modules surface, and they are prime architectural-
complexity candidates.

## Phase 2 — Deep complexity analysis

Read with both breadth (what does each major component do, how do they
connect) and depth (for anything that looks like a hotspot, trace its
actual callers and call frequency, not just the code in isolation). Use
whichever of these lenses applies — they are lenses, not a checklist:

**Architectural**

| Signal | Why it is complexity |
|---|---|
| God object/module | one class/file doing many unrelated jobs — every change risks touching unrelated behavior |
| Deep nesting / long functions | high cyclomatic complexity — hard to hold in your head, hard to test in isolation |
| Duplication | the same logic maintained in N places — fixes drift, bugs get patched once and not everywhere |
| Tight coupling / low cohesion | modules that reach into each other's internals — a local change ripples repo-wide |
| Dependency cycles | modules that mutually depend on each other — no clean layering |
| Deep inheritance / unneeded abstraction | indirection (factories of factories, one-implementation interfaces) that buys no real flexibility |
| Long parameter lists / primitive obsession | usually signals a missing concept that should be its own type |

**Computational**

| Pattern | Why it is costly |
|---|---|
| Nested loops over the same collection | often an accidental O(n²)+ where O(n) or O(n log n) is achievable |
| Repeated expensive work inside a loop | re-querying, re-parsing, or re-computing an invariant every iteration instead of once |
| List/array membership tests in hot paths | O(n) lookup where a set/dict/index would be O(1) |
| N+1 query patterns | one query per row instead of a single batched query |
| Unbounded loading into memory | reading a whole dataset/file where streaming or pagination would do |
| Recursive algorithms without memoization | recomputing overlapping subproblems, often exponentially |

Use whatever static-analysis tools are already installed to corroborate
and quantify what you find (e.g. radon/xenon/lizard for Python, an eslint
complexity rule or `jscpd` for JS/TS, `gocyclo` for Go) — do not install
new tooling for this; if nothing is available, rely on manual reading and
say so in the report rather than fabricating numbers.

For every candidate, trace where it is actually called from and at what
scale before recording it. A theoretically O(n²) loop over a list that
never holds more than five items is not a priority, and a "god class"
that is actually just a thin config holder is not one either. False
hotspots waste the one thing an autonomous pass cannot get back: trust in
the result.

## Phase 3 — Prioritize and decide what to touch autonomously

Score each candidate by complexity-reduction impact, risk of behavior
change, and effort, and work the high-impact, low-risk items first.

Some real findings are too large or risky for an unattended pass — e.g. a
fix that would require breaking a public API, splitting a package apart,
or changing a persisted data format. Do not force these through. Record
them as **deferred findings**, with why and a suggested next step,
instead of silently skipping them or, worse, making a unilateral call on
something that deserves a human in the loop.

## Phase 4 — Refactor, one target at a time

For each prioritized target, in order:

1. Name the specific complexity issue and the intended transformation in
   one or two lines — a lightweight design note, not a document.
2. If the code you are about to touch lacks coverage, add the
   characterization tests from Phase 0 for it now if you have not
   already.
3. Apply the transformation as a pure refactor: same inputs, same
   outputs, same side effects, same public signatures. If cutting the
   complexity truly requires changing the public surface, stop and defer
   this one (Phase 3) instead of changing behavior silently.
4. Run the targeted tests, then the full suite. If anything goes red, fix
   it within this step or roll the change back — never move to the next
   target on top of a failing suite.
5. Commit this change alone, following the project's/user's commit
   conventions. One commit per refactor, not one giant commit at the
   end — it keeps every step independently reviewable and revertable.
6. Re-measure the specific metric that motivated the change (cyclomatic
   complexity, an actual complexity-class improvement, duplicated lines
   removed) so the report can state a real delta, not just an assertion.

## Phase 5 — Final verification

Run the full suite once more end to end. Where static-analysis tools were
available in Phase 2, rerun them repo-wide to compare aggregate metrics
before and after. Confirm that no public API or observable behavior
changed — list any signature you touched; there should be none, and any
exception to that is worth calling out loudly rather than glossing over.

## Phase 6 — Report

Output the report directly in the conversation — do not write it to a
file unless asked. Use this structure:

```
# Complexity refactor: <repo/target name>

## Baseline
<test status before · key metrics before, per tool if available>

## Changes made
1. <file(s) — issue → transformation — metric before → after — commit>
2. ...

## Deferred findings
- <finding — why it was not auto-refactored — suggested next step>

## Final state
<test status after · aggregate metric deltas · any coverage gaps closed>
```

If a section is empty, write `_(none)_` rather than omitting it.

## When to stop and ask

- The target is ambiguous (a monorepo, unclear which sub-project).
- The baseline test suite is already failing, or will not run at all,
  and the target has real logic worth refactoring (not just config).
- The working tree is dirty.
- Behavior that needs to stay identical cannot be exercised by tests at
  all (e.g. it depends on production credentials or specific hardware) —
  do not guess at a characterization; ask how the user wants to verify it.

## Notes

- Never force-push or rewrite already-pushed history.
- Do not touch code adjacent to what you are refactoring just because it
  looks improvable too — mention it in deferred findings, do not fix it.
  Staying surgical is what makes an autonomous pass trustworthy.
- A repo with no test runner detectable at all is a genuine blocker for
  autonomously refactoring anything with real logic — report it rather
  than proceeding on faith across the whole repo.
