# agents

Personal configuration for AI coding agents (Claude Code and compatible
tools), shared across projects.

## Contents

- `AGENTS.md` — general, development, and documentation preferences.
- `CONVENTIONS.md` — code, naming, git, and PR conventions for new projects.
- `skills/deep-criticality-analysis/` — skill to run a whole-repo criticality
  analysis (bugs, code smells, risks, test-suite gaps).
- `skills/open-pr/` — skill to open a GitHub PR from the current branch,
  following the conventions above.
- `setup.sh` — installs this repo into `~/.agents` and symlinks it into each
  supported tool's config directory.

## Usage

Run the setup script to install:

```bash
./setup.sh
```

It copies `AGENTS.md`, `CONVENTIONS.md` and `skills/` into `~/.agents`, then
symlinks them into each supported tool's config directory:

- `~/.claude/CLAUDE.md`
- `~/.pi/AGENTS.md`
- `~/.codex/AGENTS.md`
- `~/.cursor/AGENTS.md`
- `~/.config/opencode/AGENTS.md`

Each tool loads its linked `AGENTS.md`/`CLAUDE.md` as global instructions and
its linked `skills/` directory as available skills.

**Warning:** the script is destructive. It deletes `~/.agents` entirely before
recreating it, and for each target it removes any pre-existing `skills/`
folder (if it's a real directory, not a symlink) before replacing it with a
symlink. Back up any local changes under those paths first.
