# Documentation preferences

### 1. Code as documentation
Use a **code as documentation** approach. The code is the source of truth and
the main documentation of the codebase.

Still keep documentation files (`README.md`, `AGENTS.md`, `CLAUDE.md`,
`memory/` files, repo docs, etc.). Make them **extremely concise and
minimal**. Put in them only:
- Information for the humans who operate the code (tutorials, guides, brief
  explanations).
- Information that is not clear from the code.

### 2. Keep documentation up-to-date
When making code changes, make sure to **keep documentation up-to-date**:
- Update docstrings.
- Update existing comments, if any.
- Update repo's documentation files, if any.
- Update repo's `CLAUDE.md` and `AGENTS.md` files.
- Update relevant project or user `memory/` files, if any.
- Comment often to keep code readable for humans.
- Make changes to the documentation, `CLAUDE.md`/`AGENTS.md` and `memory/`.
files only if necessary and relevant, and keep changes concise.

### 3. Instructions and memory
Keep project conventions and learnings in the project's `memory/` directory.
Use the user-level `memory/` directory for user preferences and learnings.
Keep project-specific instructions in project-level `CLAUDE.md` or `AGENTS.md`.
Keep user-level instructions in user-level files. Do not duplicate memory
contents in either.
