# agents

Personal configuration for AI coding agents (Claude Code and compatible
tools), shared across projects.

## Contents

- `AGENTS.md` — general, development, and documentation preferences.
- `CONVENTIONS.md` — code, naming, git, and PR conventions for new projects.
- `skills/open-pr/` — skill to open a GitHub PR from the current branch,
  following the conventions above.

## Usage

Claude Code (and compatible agents) load `AGENTS.md`/`CONVENTIONS.md` as
global instructions and `skills/` as available skills.
