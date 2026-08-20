#!/usr/bin/env bash
# Verifica que el artefacto reproduce exactamente las métricas publicadas en la memoria.
#
#   scripts/verify_reproduction.sh
#
# Regenera figuras y generated_metrics.tex desde los CSV incluidos y compara el
# resultado con reference/generated_metrics.expected.tex. Sale con código 0 si
# coinciden byte a byte y con código 1 si aparece cualquier divergencia.
set -euo pipefail

cd "$(dirname "$0")/.."

EXPECTED="reference/generated_metrics.expected.tex"
ACTUAL="generated_metrics.tex"

if [[ ! -f "$EXPECTED" ]]; then
  echo "FALTA el fichero de referencia: $EXPECTED" >&2
  exit 1
fi

echo "== Regenerando figuras y métricas =="
scripts/rebuild_figures.sh >/dev/null

echo "== Comparando con la referencia publicada =="
if diff -u "$EXPECTED" "$ACTUAL"; then
  echo
  echo "OK: el artefacto reproduce exactamente las métricas de la memoria."
  exit 0
fi

echo
echo "FALLO: las métricas regeneradas no coinciden con la referencia." >&2
echo "Revisa los CSV de data/ y la versión de scripts/build_figures.py." >&2
exit 1
