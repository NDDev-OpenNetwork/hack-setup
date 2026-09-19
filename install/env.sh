# Source after ./setup:  . install/env.sh
# Puts the repo-local pinned Codex binary ahead of bun/npm/brew shims.

HACK_ENV_ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
export PATH="$HACK_ENV_ROOT/.local/bin:$HOME/.local/bin:$PATH"
unset HACK_ENV_ROOT
