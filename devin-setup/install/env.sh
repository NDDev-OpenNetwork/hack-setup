# Source after ./setup:  . install/env.sh
# Puts repo-local pinned node/bun/python/uv/codex ahead of brew shims.
# Resolve the sourced file. $0 is the shell name under bash `. env.sh`.

_hack_env_src=""
if [ -n "${BASH_VERSION:-}" ]; then
  _hack_env_src="${BASH_SOURCE[0]}"
elif [ -n "${ZSH_VERSION:-}" ]; then
  # eval hides zsh %x from bash's parser
  eval '_hack_env_src="${(%):-%x}"'
else
  printf '%s\n' "install/env.sh: source from bash or zsh" >&2
  unset _hack_env_src
  return 1 2>/dev/null || exit 1
fi

if [ -z "${_hack_env_src}" ]; then
  printf '%s\n' "install/env.sh: cannot resolve this file" >&2
  unset _hack_env_src
  return 1 2>/dev/null || exit 1
fi

HACK_ENV_ROOT="$(CDPATH= cd -- "$(dirname -- "${_hack_env_src}")/.." && pwd)" || {
  printf '%s\n' "install/env.sh: cannot resolve repo root" >&2
  unset _hack_env_src HACK_ENV_ROOT
  return 1 2>/dev/null || exit 1
}
# HACK_USER_BIN mirrors module 30's override — default ~/.local/bin.
export PATH="$HACK_ENV_ROOT/.local/bin:${HACK_USER_BIN:-$HOME/.local/bin}:$HOME/.bun/bin:$PATH"
unset HACK_ENV_ROOT _hack_env_src

# Devin session law: bypass mode is the YOLO projection — there is no
# config-file key for the default permission mode, only the env var /
# --permission-mode flag / /bypass slash command.
export DEVIN_PERMISSION_MODE="bypass"
