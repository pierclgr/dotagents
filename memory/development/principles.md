# Development principles

## Software engineering principles
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

## Simplicity
**Minimal code. Nothing speculative.** Prefer minimal and readable implementation unless asked otherwise. Don't overengineer.
- No extra features besides the one requested.
- No "flexibility" or "configurability" unless requested.
- No "dead" methods that are unused by current requests, write only what we need.

## Readability
**Maintain human-readable code.** Prefer instructions split on multiple lines over one-line instructions.
- List comprehensions and one-line ifs only when not complex.
- Prefer clarity over fewer lines.
- Split complex one-line instructions into multiple lines.

## Surgical changes
**Touch only what you must. Clean only your own mess.** Modify only code that causes the problem or needs changing. Leave the rest alone.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor/rewrite things that aren't broken. If you see a better way, mention it instead.
- If you notice unrelated dead code, mention but don't delete.

On orphans from your changes: remove imports/vars/functions YOUR changes made unused. Leave pre-existing dead code alone.

## Granular edits
Prefer smaller granular edits over big ones. When a change is large, split it and propose one piece at a time so the user has better oversight.
