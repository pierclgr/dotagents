# Deep and breadth code exploration

**Do extensive code analysis. Analyze execution stack trace entirely.** Explore what happens before, during and after.

When exploring code behaviour:
- Explore execution from start to end.
- Do deep and breadth exploration.
- Don't stop on the line/slice of code you think explains it.

When likely identified cause or explanation, *ALWAYS* check what happens before, in and after. Always continue tracing what happens next: constructors, post-init hooks, property accessors, downstream consumers. Only conclude after verifying full path.
