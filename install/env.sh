# Source after ./setup:  . install/env.sh
# Puts repo-local pinned node/bun/python/uv/codex ahead of brew shims.

HACK_ENV_ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
export PATH="$HACK_ENV_ROOT/.local/bin:$HOME/.local/bin:$PATH"
unset HACK_ENV_ROOT
