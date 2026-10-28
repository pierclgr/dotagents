# AGENTS.md
**PREMISE**: the following are **user preferences**, to use with new projects and when no other preferences are expressed. **Always** use project's `CLAUDE.md`, `AGENTS.md` and project preferences if present.

## General preferences

### 1. Conciseness over verbosity
When asked to explain in detail, be detailed but not verbose. Answer **concisely**, **straight to the point**. Keep internal reasoning out of final answer unless explicitly asked (e.g. "what do you think?", "why?"). Do NOT add you considerations or observations unless critical or unless you're asked to do so.

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
Prefer smaller granular edits over big ones. When a change is large, split it and propose one piece at a time so the user has better oversight.

## Development preferences

### 1. Think before coding
**Don't assume. Don't hide confusion. Surface tradeoffs.** Before implementing:
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If simpler approach exists, say so. Push back when warranted.
- If unclear, stop. Name what's confusing. Ask.

### 2. Software engineering principles
**Adhere to SOLID and clean code principles. Prefer composition over inheritance.**
- Aim for code reusability and abstraction, but do not abstract if unnecessary.
- Functions when code is used multiple times; if not, no need for a function (e.g. functions and methods only if called > 1 time).
- Classes when the representing responsibilities or concepts (e.g. Configuration, ConfigManager, ConfigParser, Storage etc.)
- Fields and methods: private if used only by the class, protected if used only
  by the class and its subclasses, public if used elsewhere too.
- Design patterns only when necessary.
- Meaningful names: use variable and function names that actually represent what the variable holds and what the function does.
- No magic numbers: put fixed values in named constants.
- Guard clauses: handle bad cases first and return early. Avoid deep nesting.
- Single level of abstraction (SLAP): keep all statements in a function at the same level of abstraction. Don't mix high-level steps with low-level details.
- DRY (Don't Repeat Yourself): keep each rule in one place. Don't copy it.
- Testable code: keep logic separate from I/O (files, print, network), so you can test it alone.
- Clear errors: error messages say what went wrong and show the bad value.

### 3. Simplicity
**Minimal code. Nothing speculative.** Prefer minimal and readable implementation unless asked otherwise. Don't overengineer.
- No extra features besides the one requested.
- No "flexibility" or "configurability" unless requested.
- No "dead" methods that are unused by current requests, write only what we need.

### 4. Readability
**Maintain human-readable code.** Prefer instructions split on multiple lines over one-line instructions.
- List comprehensions and one-line ifs only when not complex.
- Prefer clarity over fewer lines.
- Split complex one-line instructions into multiple lines.

### 5. Surgical changes
**Touch only what you must. Clean only your own mess.** Modify only code that causes the problem or needs changing. Leave the rest alone.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor/rewrite things that aren't broken. If you see a better way, mention it instead.
- If you notice unrelated dead code, mention but don't delete.

On orphans from your changes: remove imports/vars/functions YOUR changes made unused. Leave pre-existing dead code alone.

### 6. Deep and breadth code exploration
**Do extensive code analysis. Analyze execution stack trace entirely.** Explore what happens before, during and after.

When exploring code behaviour:
- Explore execution from start to end.
- Do deep and breadth exploration.
- Don't stop on the line/slice of code you think explains it.

When likely identified cause or explanation, *ALWAYS* check what happens before, in and after. Always continue tracing what happens next: constructors, post-init hooks, property accessors, downstream consumers. Only conclude after verifying full path.

## Planning
When writing a plan, include:
1. **Class architecture blueprint**:
   - a Mermaid class diagram of the classes and their relations.
   - a blueprint of each class: fields and method signatures, with no
     implementation. Each field and method has a short description of what it
     holds or does. Example:
     ```python
     class Person:
         name: str  # first name of the person
         surname: str  # last name of the person
         birth: date  # date of birth

         @property
         def age(self) -> int: ...  # age in years, computed from birth
     ```
2. **Pseudocode**: pseudocode of the implementation, especially of the biggest methods, functions and code slices

## Software engineering workflow
Solve the task by going through the following steps:
1.  **Design solution**: basically, _specs-driven development_, a.k.a. write tech specs documentation given the user requirements before implementing
2. **Define the task as a set of verifiable goals**: divide the task into a set of goals that you can verify
3. **Write unit tests**: basically, _test-driven development_, a.k.a. write unit tests based on the verifiable goals you defined at step 2.
4. **Implement**: code your solution
5. **Verify**: verify goals and run tests
6. **Repeat** until tests pass and goals are reached and verified

**IMPORTANT**: the tests must be a way for you to verify and reach the implementation goal, they're not the source of truth. This means that you *can* and *must* modify the test book when the user asks you to refactor and change the implementation. This avoids adapting the new implementation to the old tests that were written for the old implementation.

## Documentation preferences

### 1. Keep documentation up-to-date
When making code changes, make sure to **keep documentation up-to-date**:
- Update docstrings.
- Update existing comments, if any.
- Update repo's documentation files, if any.
- Update repo's `CLAUDE.md` and `AGENTS.md` files.
- Comment often to keep code readable for humans.

### 2. CLAUDE.md/AGENTS.md
When creating or updating project's `CLAUDE.md`/`AGENTS.md` file, add a *convention* section with code, docstring and other conventions if it doesn't exist:
- user conventions for new projects.
- project conventions for existing projects.

## Writing style

### 1. Clarity, simplicity and conciseness
Focus on making answers and outputs as clear as possible to a human, don't use fancy works and don't try  to sound too sophisticated just for the sake of it.

Write in an English level comparable to CEFR A2-B1. Respect this level for the vocabulary,  the composition of sentence, the phrasing and the prose. Keep using technical terms (e.g. commit, branch, Machine Learning etc.) but explain things using ASD-STE100. This will be crucial for me to understand better.

### 2. BE SHORT
Reduce length and complexity of your writing to the essential.

## Reasoning style
### 1. Typographic compression, not semantic
Same meaning, fewer tokens. Applies exclusively to reasoning. Drop articles, pronouns, filler, narration connectors. Telegraphic form.

##### Example
- Before: "the user asked me to perform this operation, I should now start to do A and then do B"
- After: "user asked perform operation, do A, then B"

## Conventions

@CONVENTIONS.md
