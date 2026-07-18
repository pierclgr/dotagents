# Code, naming and documentation conventions

**PREMISE**: the following are **user preferences**, to use when no other standard is already in use and with new projects. **Always** use project's `CLAUDE.md`, `AGENTS.md` and project conventions if present.

## 1. Python preferences
- Docstring style: Google
- Coding convention: PEP8

## 2. File naming
- Default (when nothing specified): `snake_case.extension`
- Markdown: `UPPER_SNAKE_CASE.md`

## 3. Repository structure
- `docs/`: all documentation files (`.md`, `.pdf`, etc.)
- `src/`: all source code files (`.py`, etc.)
- `tests/`: all test files

## 4. Code comments
Starting letter *lowercase*, no ending period.

## 5. Git
### Branches
- `feature/snake_case`: for *feature*
- `fix/snake_case`: for *bug fixing*
- `model/model_name`: for *new AI models*

## 6. Markdown
- each line has *max* 80 chars
- do *not* line break commands in code blocks

### Commits
#### Message
- Use past tense (e.g. 'Added', 'Fixed', 'Modified' etc.)
- Short and compact message
- Indicate file(s) affected
- If too many changes, use only most significative

### Pull requests
#### Title
- Format: `TYPE: title`
- `TYPE` matches the type of the branch it merges (e.g. `feature/...` → `FEATURE:`, `fix/...` → `FIX:`)
- `title` is a short and compact summarizing title

#### Description
Structure the description in the following sections, each titled with a proper markdown header (e.g. `## Motivation`). Skip any section with no changes:
- **Motivation**: the motivation behind the PR
- **Code**: list of modifications made to the code
- **Tests**: list of modifications made to tests
- **Documentation**: list of modifications made to the documentation

General rules:
- No test plan
- No mention to coding agents (CLAUDE, CODEX, OPENCODE etc.)
- `CLAUDE.md` could be just a link to `AGENTS.md`; if so only edit `AGENTS.md`
