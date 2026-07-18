#!/usr/bin/env bash
# detect the base (target) branch for a PR opened from the current branch
#
# git has no native "parent branch" concept, so this uses a layered heuristic
# (first match wins):
#   1. gh's own configured merge base (branch.<current>.gh-merge-base)
#   2. the nearest local branch whose tip is an ancestor of HEAD -- the branch
#      HEAD was stacked directly on top of (handles feature-on-feature stacks;
#      siblings and an advanced main are excluded, their tips are not ancestors)
#   3. among conventional base branches that exist (repo default plus
#      main/master/develop/...), the one HEAD most recently diverged from
#   4. the repository default branch
#
# prints the detected base branch name to stdout, or nothing if undetectable

set -euo pipefail

current="$(git rev-parse --abbrev-ref HEAD)"

# 1. honor gh's own configured base if present
configured="$(git config --get "branch.${current}.gh-merge-base" 2>/dev/null || true)"
if [ -n "$configured" ]; then
  printf '%s\n' "$configured"
  exit 0
fi

# 2. nearest local branch HEAD is stacked on (its tip is an ancestor of HEAD);
#    the nearest one has the fewest commits between it and HEAD
best_branch=""
best_dist=""
while IFS= read -r b; do
  [ "$b" = "$current" ] && continue
  git merge-base --is-ancestor "refs/heads/$b" HEAD 2>/dev/null || continue
  dist="$(git rev-list --count "refs/heads/${b}..HEAD" 2>/dev/null || echo 0)"
  # dist 0 means it shares HEAD's tip, not a distinct parent
  [ "$dist" = "0" ] && continue
  if [ -z "$best_dist" ] || [ "$dist" -lt "$best_dist" ]; then
    best_dist="$dist"
    best_branch="$b"
  fi
done < <(git for-each-ref --format='%(refname:short)' refs/heads/)
if [ -n "$best_branch" ]; then
  printf '%s\n' "$best_branch"
  exit 0
fi

# repository default branch via origin/HEAD (set at clone or `git remote set-head`)
default=""
if git symbolic-ref -q refs/remotes/origin/HEAD >/dev/null 2>&1; then
  default="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')"
fi

# 3. nearest divergence among conventional base branches
best_branch=""
best_dist=""
for c in "$default" main master develop development dev trunk; do
  [ -z "$c" ] && continue
  [ "$c" = "$current" ] && continue
  # resolve to an existing ref, preferring the local branch over its remote copy
  if git show-ref --verify -q "refs/heads/$c"; then
    ref="$c"
  elif git show-ref --verify -q "refs/remotes/origin/$c"; then
    ref="origin/$c"
  else
    continue
  fi
  mb="$(git merge-base HEAD "$ref" 2>/dev/null || true)"
  [ -z "$mb" ] && continue
  dist="$(git rev-list --count "${mb}..HEAD" 2>/dev/null || echo 0)"
  # dist 0 means HEAD is already contained in this branch, a descendant not a parent
  [ "$dist" = "0" ] && continue
  if [ -z "$best_dist" ] || [ "$dist" -lt "$best_dist" ]; then
    best_dist="$dist"
    best_branch="$c"
  fi
done
if [ -n "$best_branch" ]; then
  printf '%s\n' "$best_branch"
  exit 0
fi

# 4. fall back to the default branch (unless it is the current branch itself)
if [ -n "$default" ] && [ "$default" != "$current" ]; then
  printf '%s\n' "$default"
fi
