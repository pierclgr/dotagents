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
Keep every section **short and concise**, with no filler or repetition. In every section, describe only what the PR touches: the branch's own changes (`git log --first-parent --no-merges <base>..HEAD`), not those of merged branches like `main`, which had their own PR. Write each paragraph or bullet on one line, without wrapping.

Sections, each with a `##` header, in this order (skip empty ones, except Diagram):
- **Motivation**: why the PR exists, in one or two sentences
- **Diagram**: a mermaid diagram of the change (see below)
- **Code**, **Tests**, **Documentation**: one bullet per changed or added file, as `` `path/to/file`: description ``, smallest change (lines changed) first. Describe the idea in plain language, not the code edits: "Person now includes age computation and a new year field", not "Person class got a new method for computing the age"

#### Diagram
- A ` ```mermaid ` block built from the branch's real diff (`git diff <base>...HEAD`)
- Type that fits the change: `flowchart` (default), `sequenceDiagram` (call flow), `classDiagram` (classes), `erDiagram` (data model)
- For a `classDiagram`, use the UML relations, each arrow with a short label that names the call or the role:
  - `<|--` inheritance: a class subclasses another
  - `..|>` realization: a class implements an abstract base or interface
  - `*--` composition: a class creates and owns the other
  - `o--` aggregation: a class holds a shared object that it did not create
  - `-->` association: a class keeps the other in a field and calls it
  - `..>` dependency: a class uses or creates the other only inside a method
- New, modified and removed items marked (e.g. `classDef` or `(new)`)
- At most ~10 nodes with short labels; quote special characters so it renders
