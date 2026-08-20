#!/usr/bin/env python3
"""Regenera MANIFEST.csv con tamaño y SHA-256 de los ficheros versionados.

Se excluyen los productos generados (figures/, generated_metrics.tex) y el
propio MANIFEST.csv, de modo que el manifiesto describe únicamente las
entradas del artefacto.
"""
from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {"MANIFEST.csv"}


SKIP_DIRS = {".git", "__pycache__", "figures", ".pytest_cache"}
SKIP_NAMES = {".DS_Store", "generated_metrics.tex"}


def tracked_files() -> list[str]:
    """Lista los ficheros del artefacto.

    Usa `git ls-files` cuando el directorio es un repositorio, y recurre a un
    recorrido del arbol en caso contrario, para que el manifiesto pueda
    regenerarse tambien desde el paquete de entrega, que no es un repositorio.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        if out:
            return sorted(p for p in out if p and p not in EXCLUDE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    found = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.name in SKIP_NAMES or path.suffix == ".pyc":
            continue
        text = rel.as_posix()
        if text in EXCLUDE:
            continue
        found.append(text)
    return sorted(found)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    rows = []
    for rel in tracked_files():
        p = ROOT / rel
        if not p.is_file():
            continue
        rows.append({"path": rel, "size_bytes": p.stat().st_size, "sha256": sha256(p)})

    with (ROOT / "MANIFEST.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["path", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"MANIFEST.csv regenerado con {len(rows)} ficheros")


if __name__ == "__main__":
    main()
