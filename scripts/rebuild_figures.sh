#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  for candidate in \
    /opt/homebrew/opt/python@3.13/bin/python3.13 \
    /opt/homebrew/opt/python@3.14/bin/python3.14 \
    python3
  do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" - <<'PY' >/dev/null 2>&1
import matplotlib.pyplot
import numpy
import pandas
PY
      then
        PYTHON_BIN="$candidate"
        break
      fi
    fi
  done
fi

if [[ -z "$PYTHON_BIN" ]]; then
  echo "No Python runtime with matplotlib, numpy and pandas was found." >&2
  exit 1
fi

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-${TMPDIR:-/tmp}/mplconfig_tfm}"

"$PYTHON_BIN" scripts/build_figures.py
