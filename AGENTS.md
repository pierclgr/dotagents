# AGENTS.md

**PREMISE**: the following are **user preferences**, to use with new 
projects and when no other preferences are expressed. 
**Always** prioritize project-level `CLAUDE.md`, `AGENTS.md`, `memory/` guidance 
and preferences if present. If user and project preferences/guidances
conflict, always prefer the project ones.

## Memory

The user-level [`memory/`](memory/) directory contains memorized context,
learnings, information, preferences and instructions. Individual repositories
may also have a `memory/` directory for project-specific context and learnings.
Both can contain instructions that are not repeated in `AGENTS.md` or
`CLAUDE.md`.

Before starting any task, you **MUST** explore these directories and files. Read 
the files that define general behavior and those relevant to the task, then 
follow their applicable instructions.

The user-level directory is organized as follows:

```text
memory/
├── communication.md             # response style and communication to use
├── reasoning.md                 # reasoning preferences to use
├── research.md                  # preferences for research and verification
├── conventions/
│   ├── general.md               # general conventions
│   ├── code_comments.md         # comment style
│   ├── file_naming.md           # file naming rules
│   ├── repository_structure.md  # project directory layout
│   ├── languages/
│   │   ├── markdown.md          # Markdown formatting
│   │   └── python.md            # Python conventions
│   └── tools/
│       └── git.md               # branches, commits and pull requests
└── development/
    ├── code_exploration.md      # code analysis and tracing
    ├── documentation.md         # documentation and memory maintenance
    ├── planning.md              # instructions to follow when writing a plan
    ├── principles.md            # design and implementation principles
    └── workflow.md              # development and verification steps
```

Keep this map up to date when memory files are added, moved or removed.
Add relevant information and learnings to the appropriate user-level or
project-level memory files.

Do not duplicate memory contents in `CLAUDE.md` or `AGENTS.md`.

## Communication
@memory/communication.md
