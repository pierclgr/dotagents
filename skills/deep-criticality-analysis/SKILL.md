---
name: deep-criticality-analysis
description: Run a deep criticality analysis of a repository — execute its unit tests, deeply analyze the code and repo structure for bugs, code smells, future-risk patterns, and security issues, then assess the test suite itself for missing/weak tests and coverage gaps, and output a concise severity-ranked report. Use this skill whenever the user asks for a "deep criticality analysis", a "critical analysis" of a repo/repository/codebase, to "audit this codebase", "find bugs and risks", do a "health check" on a repo, ask "what's wrong with this codebase", or requests a full review of an entire repository for problems and future risks — even when they don't use the exact phrase "criticality analysis". Trigger it for any whole-repo quality/risk/correctness review that goes beyond a single-file diff review.
---

# Deep Criticality Analysis

A whole-repository criticality analysis: run the tests, read the code deeply, judge the test suite, and deliver a concise severity-ranked report. This is broader and deeper than a diff review — it assesses the repo's health as a whole and looks for things that will cause problems later, not just what changed last.

## What this skill produces

A single concise report, output directly in the conversation (do **not** write it to a file unless the user asks). The report has four parts:

1. **Test results** — runner used, counts, notable failures.
2. **Findings** — ranked Critical → Low, each tagged with a category, a `file:line`, and a short fix suggestion.
3. **Test-suite assessment** — missing tests, improvable tests, uncovered areas.
4. **Top recommendations** — the 3–5 highest-leverage fixes.

Signal density is the whole point. A criticality report that buries real risks under verbose prose gets skimmed and ignored, which defeats the purpose. Keep each finding to ~2–3 lines: enough to locate and understand the problem, not an essay.

## Scope and conduct

Operate on the repo the user points at — the current working directory if unspecified, or a path they name. If the target isn't a repository (no recognizable project structure), say so and ask before proceeding.

This is a **read-only** analysis. The only side-effect you create is running the test suite (and only the test runner's own artifacts). Do not modify source, config, or tests. Do not install heavyweight dependencies; if tests need deps that aren't present, note it as a finding rather than scaffolding an environment.

State your assumptions explicitly as you go — which runner you picked, which modules you treated as entry points, what you considered in vs. out of scope. If something is ambiguous, pick the most likely interpretation and say so rather than stopping.

## Phase 1 — Detect the stack and test runner

Identify the language(s), build tooling, and test runner by looking at manifest/config files at the repo root. Use this map as a starting point and adapt to what you actually find:

| Signal | Runner |
|---|---|
| `pyproject.toml`, `setup.cfg`, `pytest.ini`, `tox.ini` with pytest config | `pytest` (fallback `python -m unittest`) |
| `package.json` | read `scripts.test`; resolve to jest / vitest / mocha / playwright / node-tap as configured |
| `go.mod` | `go test ./...` |
| `Cargo.toml` | `cargo test` |
| `pom.xml` | `mvn test` |
| `build.gradle` / `build.gradle.kts` | `gradle test` (or `./gradlew test`) |
| `Gemfile` + `spec/` | `rspec` |
| `Rakefile` + `test/` (Ruby, no rspec) | `rake test` |
| `composer.json` + `phpunit.xml` | `phpunit` |
| `*.csproj` / `*.sln` | `dotnet test` |
| `deno.json` / `deno.jsonc` | `deno test` |
| `mix.exs` | `mix test` |
| `CMakeLists.txt` + `CTestTestfile.cmake` | `ctest` |

Projects customize, so verify rather than assume — read the relevant manifest (e.g. `package.json` `scripts.test`, `tox.ini` envs, `pyproject.toml` `[tool.pytest]`) to confirm the exact command and options. If multiple ecosystems are present, run each one and label results by suite. If no runner is detectable, record it as a `test-gap` finding and move on to static analysis.

## Phase 2 — Run the unit tests

Run the detected command and capture: total / pass / fail / error / skip counts, the names and error messages of failing tests, and rough duration.

**Report and continue, always.** Test failures and errors are data, not blockers — they become findings (usually `bug` or `test-gap`). A runner that won't start, missing deps, or a suite that hangs are themselves findings about repo health. Never abort the whole analysis because the tests are broken; the static analysis and test-suite assessment still deliver value. If a suite hangs, time it out, record what you saw, and proceed.

## Phase 3 — Deep code and repo analysis

First map the structure: top-level directories, entry points, configuration, dependency manifests, and where the tests live. This map guides where to read deeply.

Then read the key modules with **breadth and depth**. Breadth: understand what each major component does and how they connect. Depth: for anything that looks risky, trace the full execution path from start to end — constructors, init hooks, property accessors, callers, downstream consumers, error paths. Don't conclude from the single line that looked suspicious; verify what happens before, in, and after. Many real bugs live in the gap between what a function does and what its callers assume it does.

Hunt across four categories. These are lenses, not a checklist — use whichever applies:

- **bug** — logic errors, off-by-one, unchecked/null returns, race conditions, resource leaks (files/connections/locks not released), swallowed or incorrect error handling, wrong comparison operators, mutable default arguments, identity-vs-equality mistakes.
- **code-smell** — duplication, god-objects, deep nesting, magic values, tight coupling, dead/unreachable code, functions doing too much.
- **future-risk** — patterns that work today but will break under change or scale: hardcoded paths/values, missing input validation, deprecated APIs, unbounded growth (lists/caches that never evict), assumptions that won't hold at scale, clusters of `TODO`/`FIXME`/`HACK`, config that should be external, missing retries/timeouts on I/O.
- **security** — injection (SQL/command/template), unsafe deserialization, secret handling (logged secrets, committed keys), path traversal, missing auth/authz checks, unsafe regex (ReDoS), SSRF.

For every candidate finding, verify the full path before recording it. False positives erode trust in the whole report; a finding that doesn't actually hold is worse than one missing.

## Phase 4 — Assess the test suite

You now have real context: you know what the code does, where the risky paths are, and which tests passed or failed. Use that context to judge the tests themselves, not in isolation. This is the part a generic coverage tool can't do.

Look for three things:

- **Missing tests** — critical paths or branches with no test at all. Cross-reference the modules you analyzed in Phase 3 against what the test files actually exercise. Pay special attention to the risky paths you found: a race condition, an error branch, or a validation gap with no test is a `test-gap` finding and often raises the severity of the underlying code finding.
- **Improvable tests** — tests that exist but are weak: absent or trivial assertions (`assert True`, `assert result` with no shape check), testing implementation details instead of behavior, brittle/over-mocked tests that break on refactors, missing boundary/edge cases, flaky or time-dependent tests, tests that can't fail, tests that swallow errors.
- **Uncovered areas** — modules, functions, or error branches you touched in Phase 3 that no test reaches.

Tag all of these `test-gap`. Where a test gap connects to a concrete code finding from Phase 3, say so explicitly (e.g. "the resource leak in `server.py:142` has no test exercising the early-return path that triggers it") — that linkage is the most actionable output of the whole analysis.

## Phase 5 — Write the report

Output the report in the conversation. Do not write a file. Use exactly this structure:

```
# Criticality analysis: <repo name>

## Test results
<runner(s) used · counts (total/pass/fail/error/skip) · duration>
<notable failures, one line each — test name + error>

## Findings
### Critical
- <severity · category · file:line — one-line description → short fix suggestion>
### High
- ...
### Medium
- ...
### Low
- ...

## Test-suite assessment
**Missing tests**
- ...
**Improvable tests**
- ...
**Uncovered areas**
- ...

## Top recommendations
1. ...
2. ...  (3–5 highest-leverage fixes)
```

Keep findings to ~2–3 lines each. The format per finding is:

`severity · category · file:line — description → fix suggestion`

Severity guidance:
- **Critical** — will cause incorrect behavior, data loss, or a security breach in normal use. Fix now.
- **High** — likely bug or significant risk that will bite under realistic conditions.
- **Medium** — real issue but bounded impact, or a smell that materially hurts maintainability.
- **Low** — minor smell, stylistic, or low-likelihood risk.

If a section is empty, write `_(none found)_` rather than omitting it — an explicit "nothing here" is more useful than silence, because the reader knows you checked.

Aim for a report a maintainer can act on in one read: real issues, located precisely, with a fix direction each — and an honest account of where the test suite leaves them exposed.