# Git

### Branches
- `feature/snake_case`: for *feature*
- `fix/snake_case`: for *bug fixing*
- `model/model_name`: for *new AI models*

### Worktrees
- When working with branches, use git worktrees
- Ideally (not strict), use one dedicated branch and worktree for each feature
- Store worktrees under `<cwd>/.worktrees/`

### .gitignore
- Use master `<cwd>/.gitignore` for `.worktrees/`, root items and project-wide patterns (e.g. files/folders that are in many parts of the project); 
- Use the item's parent folder for local rules: `/c` in `a/b/.gitignore` ignores `a/b/c`

### Commits
#### Message
- Use past tense (e.g. 'Added', 'Fixed', 'Modified' etc.)
- Short and compact message (1 sentence)
- Indicate file(s) affected
- If too many changes, use only most significative

### Pull requests
#### Title
- Format: `TYPE: title`
- `TYPE` matches the type of the branch it merges (e.g. `feature/...` → `FEATURE:`, `fix/...` → `FIX:`)
- `title` is a short and compact summarizing title

#### Description
Structure the description in the following sections, each titled with a proper markdown header (e.g. `## Motivation`). Skip any section with no change:
- **Motivation**: the motivation behind the PR
- **Code**: list of modifications made to the code
- **Tests**: list of modifications made to tests
- **Documentation**: list of modifications made to the documentation

A PR description must be clear but also concise and readable, not too long. Do *not* wrap lines at a column limit: write each paragraph and each bullet on a single line, full length.
