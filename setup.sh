#!/usr/bin/env bash
set -euo pipefail

# Resolve the directory this script lives in, so it can be run from anywhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

AGENTS_DIR="${HOME}/.agents"

# 1. Link AGENTS.md, CONVENTIONS.md, skills/ and agents/ into ~/.agents
rm -rf "${AGENTS_DIR}"
mkdir -p "${AGENTS_DIR}"
ln -sfn "${SCRIPT_DIR}/AGENTS.md" "${AGENTS_DIR}/AGENTS.md"
ln -sfn "${SCRIPT_DIR}/CONVENTIONS.md" "${AGENTS_DIR}/CONVENTIONS.md"
ln -sfn "${SCRIPT_DIR}/skills" "${AGENTS_DIR}/skills"
ln -sfn "${SCRIPT_DIR}/agents" "${AGENTS_DIR}/agents"

# 2. Link ~/.agents into each tool's config directory.
# Each entry is "target_dir:link_name_for_AGENTS.md:agents_subfolder"
# An empty agents_subfolder means no agents/ link for that tool.
TARGETS=(
  ".claude:CLAUDE.md:claude"
  ".pi:AGENTS.md:"
  ".codex:AGENTS.md:codex"
  ".cursor:AGENTS.md:"
  ".config/opencode:AGENTS.md:opencode"
)

for entry in "${TARGETS[@]}"; do
  IFS=: read -r dir link_name agents_subfolder <<< "${entry}"
  target_path="${HOME}/${dir}"

  mkdir -p "${target_path}"
  ln -sfn "${AGENTS_DIR}/AGENTS.md" "${target_path}/${link_name}"

  for folder in skills agents; do
    source_path="${AGENTS_DIR}/${folder}"
    # agents/ is split per tool: link only the tool's own subfolder
    if [ "${folder}" = "agents" ]; then
      [ -n "${agents_subfolder}" ] || continue
      source_path="${source_path}/${agents_subfolder}"
    fi
    folder_path="${target_path}/${folder}"
    # ln -sfn nests the symlink inside an existing real directory instead of
    # replacing it, so remove it first
    if [ -d "${folder_path}" ]; then
      rm -rf "${folder_path}"
    fi
    ln -sfn "${source_path}" "${folder_path}"
  done
done

echo "Setup complete."
