#!/usr/bin/env bash
set -euo pipefail

# Resolve the directory this script lives in, so it can be run from anywhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

AGENTS_DIR="${HOME}/.agents"

# 1. Copy AGENTS.md, CONVENTIONS.md and skills/ into ~/.agents
mkdir -p "${AGENTS_DIR}"
cp "${SCRIPT_DIR}/AGENTS.md" "${AGENTS_DIR}/AGENTS.md"
cp "${SCRIPT_DIR}/CONVENTIONS.md" "${AGENTS_DIR}/CONVENTIONS.md"
cp -r "${SCRIPT_DIR}/skills" "${AGENTS_DIR}/skills"

# 2. Link ~/.agents into each tool's config directory.
# Each entry is "target_dir:link_name_for_AGENTS.md"
TARGETS=(
  ".claude:CLAUDE.md"
  ".pi:AGENTS.md"
  ".codex:AGENTS.md"
  ".cursor:AGENTS.md"
  ".config/opencode:AGENTS.md"
)

for entry in "${TARGETS[@]}"; do
  dir="${entry%%:*}"
  link_name="${entry##*:}"
  target_path="${HOME}/${dir}"

  mkdir -p "${target_path}"
  ln -sfn "${AGENTS_DIR}/AGENTS.md" "${target_path}/${link_name}"
  ln -sfn "${AGENTS_DIR}/skills" "${target_path}/skills"
done

echo "Setup complete."
