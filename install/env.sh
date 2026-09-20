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
_hack_npm_global_bin=""
_hack_npm_link="$HACK_ENV_ROOT/.local/bin/npm"
if [ -L "$_hack_npm_link" ]; then
  # npm -g installs into the pinned node's own bin dir; put it on PATH
  # so global tools (language servers, CLIs) resolve for editors too.
  _hack_npm_global_bin="$(dirname -- "$(readlink "$_hack_npm_link")")"
fi
export PATH="$HACK_ENV_ROOT/.local/bin:$HOME/.local/bin${_hack_npm_global_bin:+:$_hack_npm_global_bin}:$PATH"
unset HACK_ENV_ROOT _hack_env_src _hack_npm_link _hack_npm_global_bin
