# Software engineering workflow

Solve the task by going through the following steps:
1.  **Design solution**: basically, _specs-driven development_, a.k.a. write tech specs documentation given the user requirements before implementing
2. **Define the task as a set of verifiable goals**: divide the task into a set of goals that you can verify
3. **Write unit tests**: basically, _test-driven development_, a.k.a. write unit tests based on the verifiable goals you defined at step 2.
4. **Implement**: code your solution
5. **Verify**: verify goals and run tests
6. **Repeat** until tests pass and goals are reached and verified

**IMPORTANT**: the tests must be a way for you to verify and reach the implementation goal, they're not the source of truth. This means that you *can* and *must* modify the test book when the user asks you to refactor and change the implementation. This avoids adapting the new implementation to the old tests that were written for the old implementation.
