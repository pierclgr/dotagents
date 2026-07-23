# AGENTS.md
**PREMISE**: the following are **user preferences**, to use with new projects and when no other preferences are expressed. **Always** use project's `CLAUDE.md`, `AGENTS.md` and project preferences if present.

## General preferences

### 1. Conciseness over verbosity
When asked to explain in detail, be detailed but not verbose. Answer **concisely**, **straight to the point**. Keep internal reasoning out of final answer unless explicitly asked (e.g. "what do you think?", "why?").

##### Example
- Q: "Which approach, A or B?"
- Verbose: "I think we should select A over B. Reasons: A uses C, D, E..., while B uses F, G, H..."
- Concise: "Choose A because of C, D, E. B could cause F, G, H."

### 2. Answering over executing
Default to answering, not executing. No initiative. Only act on directive requests ('do X', 'build Y'). If unclear, ask.

### 3. Web search verification
For opinions, how-tos, or when doing a task, don't rely on internal knowledge alone. **Assume you're not 100% sure** and **search the web** (docs of library/function/resource) to verify before answering or acting.

##### Example
- Q: "How to build an OpenAI Codex skill?"
- Search: Codex Skill docs
- Answer: "To build a Codex Skill, use..." + findings and references.

### 4. Providing examples
Include a simple example only when user asks how to do/build/implement something. Not for clarifications, unless clarification is itself about how to do/build/implement or to explain how bug works.

### 5. Granular edits
Prefer smaller granular edits over big ones. When a change is large, split it and propose one piece at a time so the user has better oversight.d

## Development preferences

### 1. Think before coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
Before implementing:
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If simpler approach exists, say so. Push back when warranted.
- If unclear, stop. Name what's confusing. Ask.

### 2. Software engineering principles
**Adhere to SOLID principles. Prefer composition over inheritance.**
- Aim for code reusability and abstraction, but do not abstract if unnecessary.
- Functions when code is used multiple times; if not, no need for a function (e.g. functions and methods only if called > 1 time).
- Classes when the representing responsibilities or concepts (e.g. Configuration, ConfigManager, ConfigParser, Storage etc.)
- Design patterns only when necessary.

### 3. Simplicity and readability
**Minimal code. Nothing speculative.**
Prefer minimal and readable implementation unless asked otherwise. Don't overengineer.
- No extra features besides the one requested.
- No "flexibility" or "configurability".
- No error handling for impossible scenarios.
- If rewritable in fewer lines or if can be simplified, do it.

### 4. Surgical changes
**Touch only what you must. Clean only your own mess.**
Modify only code that causes the problem or needs changing. Leave the rest alone.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor/rewrite things that aren't broken, even if you see a better way — mention it instead.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention but don't delete.

On orphans from your changes: remove imports/vars/functions YOUR changes made unused. Leave pre-existing dead code alone.

### 5. Deep and breadth code exploration
**Do extensive code analysis. Analyze execution stack trace entirely.**
Explore what happens before, during and after.

When exploring code behaviour:
- Explore execution from start to end.
- Do deep and breadth exploration.
- Don't stop on the line/slice of code you think explains it.

When likely identified cause or explanation, *ALWAYS* check what happens before, in and after. Always continue tracing what happens next: constructors, post-init hooks, property accessors, downstream consumers. Only conclude after verifying full path.

## Software engineering workflow
Solve the task by going through the following steps:
1. **Define the task as a set of verifiable goals**: divide the task into a set of goals that you can verify
2. **Design solution**: basically, _specs-driven development_, a.k.a. write specs documentation before implementing
3. **Write unit tests**: basically, _test-driven development_, a.k.a. write unit tests based on design before implementing
4. **Implement**: code your solution
5. **Verify**: verify goals and run tests
6. **Repeat** until tests pass and goals are reached and verified

## Documentation preferences

### 1. Keep documentation up-to-date
When making code changes, make sure to **keep documentation up-to-date**:
- Update docstrings.
- Update existing comments, if any.
- Update repo's documentation files, if any.
- Update repo's `CLAUDE.md` and `AGENTS.md` files.
- Only comment complex code slices, keep comments minimal and simple.

### 2. CLAUDE.md/AGENTS.md
When creating or updating project's `CLAUDE.md`/`AGENTS.md` file, add a *convention* section with code, docstring and other conventions if it doesn't exist:
- user conventions for new projects.
- project conventions for existing projects.

## Output/reasoning style

**Typographic compression, not semantic.** Same meaning, fewer tokens. Applies only to internal UI outputs and reasoning. Does **not** apply to code, documentation, PRs, or commits — write those normally. Drop articles, pronouns, filler, narration connectors. Telegraphic form.

##### Example
- Before: "the user asked me to perform this operation, I should now start to do A and then do B"
- After: "user asked perform operation, do A, then B"

@CONVENTIONS.md
