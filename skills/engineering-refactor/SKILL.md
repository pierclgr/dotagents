---
name: engineering-refactor
description: >-
  Analyze a repository for software-engineering complexity (over-engineering,
  dead or unused code, unneeded abstraction, speculative options, too many
  classes or files, god objects, tight coupling, duplication, deep nesting,
  SOLID violations), report the findings to the user, ask which ones to
  implement, and only then simplify the implementation with the selected
  changes, verified by the existing test suite (one commit per change). Never
  implements anything before the user reviews the findings. Use when the user
  says code is "over-engineered", "overcomplicated", "bloated", "a mess",
  "hard to maintain", has "too many classes/files/layers", "too much
  abstraction", "dead code", "unused code" or "unused features", or asks to
  "simplify this", "simplify the implementation", "clean up tech debt",
  "reduce coupling" or "break up this god class". Not for algorithmic or
  runtime performance: use complexity-refactor for that.
compatibility: >-
  Requires `git` and the target repo's test runner (whatever it uses). Uses
  static-analysis tools only when already installed (e.g. vulture for Python,
  knip for JS/TS, the linter's unused-code rules) and never installs new
  tooling: falls back to manual reading and search where no tool is present.
---

# Engineering Refactor

Code often has more moving parts than the problem needs: unused code,
abstractions with one user, options nobody sets, many tiny classes, tangled
dependencies. This skill finds these cases and simplifies the implementation.
It works in three steps, and the user decides at the second one:

1. **Analyze and report**: find the findings and show them to the user.
2. **Ask**: the user reviews the findings and selects which ones to implement.
3. **Implement**: apply only the selected findings, verified by tests.

The skill is never autonomous from finding to implementation. No file is
changed before the user has selected the findings.

## Invariants

- **No implementation without selection.** Phases 0 to 3 are read-only. Change
  files only after the user answers the question in Phase 3, and only for the
  findings the user selected.
- **Behavior-preserving by default.** A fix keeps observable inputs/outputs,
  side effects and public signatures. A finding that would change them (e.g.
  removing a feature, an option or a public function) is marked
  **behavior change** in the report. It is implemented only if the user selects
  it, and then it is the user's decision: update the tests that covered the
  removed behavior and say so in the report.
- **Verified by tests.** Run the relevant tests, then the full suite, after
  each change. A change that is not verified green does not stay.
- **Delete only proven-unused code.** No static reference and no dynamic one
  (string lookups, reflection, `getattr`, decorators, plugin or entry-point
  registration, config files, serialization, templates). Public or exported
  code (library API, `__all__`, CLI commands, HTTP routes) is never proven
  unused from inside the repo: mark it **behavior change**.

## Phase 0 — Scope and baseline (read-only)

- Find the target: the whole repo or the path the user named. If it is a
  monorepo with unrelated sub-projects and the user only said "the codebase",
  ask which one.
- Find the language(s) and the exact test command (`pyproject.toml`,
  `pytest.ini`, `package.json` `scripts.test`, `go.mod`, `Cargo.toml`, etc.).
  Confirm it; do not assume.
- Check the working tree is clean (`git status --porcelain`). If not, stop and
  tell the user.
- Run the full suite once to record a baseline. If it fails or does not run,
  stop and report: a broken baseline cannot verify a refactor.

## Phase 1 — Map the repository

Find the entry points, the modules, the layers and the **public surface**
(what is exported or called from outside the repo). Sketch which module
imports which: this shows dependency cycles, god modules and high fan-in or
fan-out. If the repo is large, use a read-only exploration subagent if one is
available.

## Phase 2 — Analysis

Read with breadth (what each component does, how they connect) and depth (for
each candidate, trace its real callers and uses). The tables are lenses, not a
checklist.

For every function, class and module, also ask: **what is the simplest
implementation with the same behavior?** Compare it with what exists. If the
simpler version has clearly fewer lines, parts or concepts, and stays easy to
read (no code golf), it is a finding, even when no part of the code is dead.
Keep the flexibility that the code really uses today; drop the rest.

**Unneeded code and structure**

| Signal | Why it is complexity |
|---|---|
| Dead code | unused function, method, class, parameter, import, variable, file; unreachable branch; commented-out code; stale feature flag |
| Unused feature | code that runs but no user flow or caller needs it |
| Speculative generality | parameter, option or hook nobody sets; interface or base class with one implementation; plugin system with one plugin |
| Needless indirection | wrapper that only forwards; helper used once; layer that adds nothing; factory of factories |
| Over-fragmentation | many tiny classes or files for what one small module can do; class with one method or only static methods |
| Redundant defensive code | checks or error handling for cases that cannot happen |
| Reinvented wheel | custom code that repeats the standard library or a dependency already used; unused dependency |
| Rewritable more simply | same behavior possible with fewer lines, parts or concepts (e.g. a long loop that is a short expression; a class hierarchy that is one function) |

**Structure**

| Signal | Why it is complexity |
|---|---|
| God object/module | one class or file with many unrelated jobs |
| Deep nesting / long functions | high cyclomatic complexity: hard to read and to test |
| Duplication | same logic in N places: fixes drift |
| Tight coupling / low cohesion | modules use each other's internals: changes ripple |
| Dependency cycles | no clean layering |
| Deep inheritance | behavior spread over many levels; prefer composition |
| Long parameter lists / primitive obsession | a missing concept that should be its own type |

Use the static-analysis tools already installed to find and count candidates
(e.g. `vulture` for Python, `knip` for JS/TS, the linter's unused-code and
complexity rules, `jscpd` for duplication). Their output is a list of
suspects, not proof: dynamic features cause false positives. Do not install
new tools. If none is present, read and search manually and say so in the
report. Never invent numbers.

For every candidate, trace where it is used, and check the public surface from
Phase 1, before you record it. A "god class" that is a thin config holder, or
an interface called by a framework, is not a finding. False findings cost the
one thing an analysis cannot get back: the user's trust.

## Phase 3 — Report the findings and ask (stop here)

Show the findings in the conversation, not in a file, ordered by priority
(impact high to low, risk low to high). Give each finding an ID and these
fields:

- **Where**: file(s) and symbol(s).
- **Issue**: what is more complex than needed, and why.
- **Proposed change**: the simplest implementation, in one or two lines, with
  the size before and after (lines, classes, files).
- **Type**: `safe refactor` (behavior-preserving) or `behavior change`.
- **Impact / risk / effort**: low, medium or high, with a real number when
  you have one (lines, files, classes removed).

Use this layout:

```
# Engineering refactor findings: <repo/target name>

## Baseline
<test status · key metrics, per tool if available>

## Findings
| ID | Where | Issue | Proposed change | Type | Impact / risk / effort |
|---|---|---|---|---|---|

## Not analyzed
<areas skipped, tools missing, or things you could not verify — or _(none)_>
```

Then **ask the user which findings to implement**: all, a list of IDs, or
none. Wait for the answer. Do not start any change before it. If the user
asks questions or changes the list, answer and confirm the final list again.

## Phase 4 — Implement the selected findings, one at a time

Before the first change:

- If the current branch is `main`, `master` or `dev`, create a new branch.
  Use the project's branch convention if it has one for this work, otherwise
  `refactor/<short_snake_case_slug>`. If you are already on a feature or fix
  branch, work there.
- If the code to touch has no tests, write minimal characterization tests
  (representative inputs and edge cases). Limit this to what you change.

Then, for each selected finding, in the agreed order:

1. Apply the proposed change. Do not add a new abstraction unless the result
   is clearly simpler than before.
2. If the change needs more than the finding said (e.g. a `safe refactor`
   turns out to change the public surface), stop and ask the user.
3. Run the targeted tests, then the full suite. If anything fails, fix it in
   this step or roll the change back. Never go on top of a failing suite.
4. Commit this change alone, following the project's and user's commit
   conventions. One commit per finding.
5. Re-measure what motivated the change (lines, files, classes, dead symbols,
   cyclomatic complexity, duplicated lines). After deleting code, re-run the
   dead-code search: it can expose more.

## Phase 5 — Final verification

Run the full suite again. If tools were available in Phase 2, re-run them on
the whole target and compare with the baseline. Confirm that only the selected
findings changed the code, and that no public API or observable behavior
changed except in the `behavior change` findings the user selected.

## Phase 6 — Final report

Write the report in the conversation, not in a file, unless asked:

```
# Engineering refactor: <repo/target name>

## Baseline
<test status before · key metrics before>

## Changes made
1. <finding ID — file(s) — change — metric before → after — commit>
2. ...

## Findings not implemented
- <finding ID — reason (not selected / deferred) — suggested next step>

## Final state
<test status after · metric deltas · coverage gaps closed>
```

If a section is empty, write `_(none)_`.

## When to stop and ask

- The target is ambiguous (monorepo, unclear sub-project).
- The baseline suite fails or does not run, and the target has real logic.
- The working tree is dirty.
- The behavior to keep cannot be tested (e.g. needs production credentials or
  special hardware): ask how the user wants to verify it.

## Notes

- Never force-push or rewrite pushed history.
- Do not touch code next to your target just because it looks improvable:
  add it as a finding in the report instead. Staying surgical keeps the
  process trustworthy.
- A repo with no detectable test runner is a blocker for refactoring real
  logic: report it, do not proceed on faith.
- Performance problems (slow algorithms, wasted work) are out of scope: point
  the user to the complexity-refactor skill.
