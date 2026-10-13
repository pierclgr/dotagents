# agents

Personal configuration for AI coding agents (Claude Code and compatible tools), shared across projects.

## Contents

- `AGENTS.md` — general, development, and documentation preferences.
- `CONVENTIONS.md` — code, naming, git, and PR conventions for new projects.
- `skills/assisted-code-review/` — skill to review a PR, a branch or uncommitted changes with the agent's help, one file at a time, bottom-up (files without internal imports first). Tests: `python3 -m unittest discover -s skills/assisted-code-review/tests`.
- `skills/deep-criticality-analysis/` — skill to run a whole-repo criticality analysis (bugs, code smells, risks, test-suite gaps).
- `skills/open-pr/` — skill to open a GitHub PR from the current branch, following the conventions above.
- `agents/claude/ORCHESTRATOR.md` — main session agent for a software engineering workflow: product owner and orchestrator of subagents, gives one feature to each planner subagent (Opus, `xhigh` effort). Run with `claude --agent orchestrator`.
- `agents/claude/PLANNER.md` — subagent that plans one feature from start to end and delegates its research and implementation to researcher and coder subagents; reports only to the orchestrator (Opus, `xhigh` effort).
- `agents/claude/CODER.md` — subagent that plans the implementation of a feature or a single element in plan mode, implements it, and reports only to its planner (Sonnet, `xhigh` effort).
- `agents/claude/RESEARCHER.md` — subagent that explores the documentation, the codebase or the web as its planner asks, and reports only to the planner (Haiku, `xhigh` effort).
- `agents/codex/` — the same four agents as `.toml` files for Codex (`orchestrator.toml`, `planner.toml`, `coder.toml`, `researcher.toml`).
- `agents/opencode/` — the same four agents as `.md` files for OpenCode. All use `opencode-go/deepseek-v4.1-flash`, with the effort set in the model variant: `max` for the orchestrator and planner, `high` for the coder, `low` for the researcher. The orchestrator is a primary agent, the others are subagents. The plan mode and build mode lines are reworded, because OpenCode has no mode switch for custom agents.
- `setup.sh` — installs this repo into `~/.agents` and symlinks it into each supported tool's config directory.

## Usage

Run the setup script to install:

```bash
./setup.sh
```

It copies `AGENTS.md`, `CONVENTIONS.md`, `skills/` and `agents/` into `~/.agents`, then symlinks them into each supported tool's config directory:

- `~/.claude/CLAUDE.md`
- `~/.pi/AGENTS.md`
- `~/.codex/AGENTS.md`
- `~/.cursor/AGENTS.md`
- `~/.config/opencode/AGENTS.md`

Each tool loads its linked `AGENTS.md`/`CLAUDE.md` as global instructions, its linked `skills/` directory as available skills and its linked `agents/` directory as available agents. Each tool's `agents/` links to its own subfolder: `~/.claude/agents` → `agents/claude/`, `~/.codex/agents` → `agents/codex/`, `~/.config/opencode/agents` → `agents/opencode/`. Pi and Cursor get no `agents/` link.

**Warning:** the script is destructive. It deletes `~/.agents` entirely before recreating it, and for each target it removes any pre-existing `skills/` and `agents/` folders (if they're real directories, not symlinks) before replacing them with symlinks. Back up any local changes under those paths first.
