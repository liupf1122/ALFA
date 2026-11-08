#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
# Resolve conda without requiring an activated shell environment.
conda_bin="${CONDA_EXE:-}"
if [[ ! -x "$conda_bin" ]]; then
  conda_bin="$(command -v conda || true)"
fi
if [[ -z "$conda_bin" ]]; then
  echo "找不到 conda，请先将 conda 加入 PATH。" >&2
  exit 1
fi
exec "$conda_bin" run --no-capture-output -n aging python -u "$project_dir/scripts/run.py" train "$@"
