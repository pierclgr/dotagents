# Software engineering workflow

Use **specs-driven development**. The specs in the plan, reviewed and approved
by the user, are the source of truth for implementation.

Solve the task by going through the following steps:

1. **Define the specs**: write a plan based on the user requirements, with
   expected behavior, constraints and verifiable acceptance criteria. Follow
   the [planning guidance](planning.md).
2. **Review the plan with the user**: resolve open questions and agree on the
   specs and goals before implementing.
3. **Write tests first**: before implementation, use the specs and acceptance
   criteria to write tests. For a bug, first write a test that shows the bug.
   Keep tests **few and concise**: test only critical behavior, core logic,
   important error paths and regression risks. No wall of tests, not every
   possible line or case.
4. **Implement and iterate on the goals**: build the solution according to the
   approved plan. Check each outcome against the specs and adjust the
   implementation until each goal is met and the tests pass.
5. **Verify**: confirm that each goal is met and run the relevant new and
   existing tests. Passing tests alone does not establish that goals are met.
6. **Repeat**: fix issues and verify again until all goals are met, the specs
   are satisfied and the relevant tests pass.

Tests verify the specs; they do not replace them. Update tests when the user
changes the specs or when a refactor makes tests tied to implementation details
outdated. Preserve checks for required behavior, and fix implementation defects
instead of weakening tests to make them pass. For a refactor, run the tests
before and after: they must pass both times.

## Small tasks

For trivial or small tasks, use judgment: skip the full Q&A plan. State a
short plan instead, with a check for each step:

```text
1. [step] → verify: [check]
2. [step] → verify: [check]
```
