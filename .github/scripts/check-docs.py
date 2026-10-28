#!/usr/bin/env python3
"""Verificador de documentación para Bloo-Docs.

Comprueba, sin dependencias externas, que la documentación sea consistente:

1. Todos los enlaces relativos de los `.md` apuntan a archivos existentes.
2. Los bloques de código con ``` están balanceados.
3. No hay caracteres de reemplazo (U+FFFD) arrastrados por ediciones.

Uso:  python3 .github/scripts/check-docs.py
Sale con código 1 si hay fallos.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "node_modules", "vendor"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")


def iter_markdown_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def strip_code_blocks(text: str) -> str:
    """Elimina los bloques cercados para no confundir enlaces de ejemplo con reales."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def check_links(path: Path, text: str, errors: list[str]) -> None:
    for target in LINK_RE.findall(text):
        if target.startswith(EXTERNAL_PREFIXES) or target.startswith("#"):
            continue
        local = target.split("#", 1)[0]
        if not local:
            continue
        if not (path.parent / local).exists():
            rel = path.relative_to(ROOT)
            errors.append(f"{rel}: enlace roto -> {target}")


def check_fences(path: Path, text: str, errors: list[str]) -> None:
    fences = len(re.findall(r"^\s*```", text, flags=re.MULTILINE))
    if fences % 2 != 0:
        rel = path.relative_to(ROOT)
        errors.append(f"{rel}: bloque de código sin cerrar (``` impares: {fences})")


def check_replacement_chars(path: Path, raw: bytes, errors: list[str]) -> None:
    if b"\xef\xbf\xbd" in raw:
        rel = path.relative_to(ROOT)
        errors.append(f"{rel}: contiene caracteres de reemplazo (U+FFFD)")


def main() -> int:
    errors: list[str] = []
    files = iter_markdown_files()

    for path in files:
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        check_replacement_chars(path, raw, errors)
        check_fences(path, text, errors)
        check_links(path, strip_code_blocks(text), errors)

    # Los diagramas Mermaid sueltos deben tener extensión .mmd y no estar vacíos
    for path in sorted(ROOT.rglob("*.mmd")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.read_text(encoding="utf-8").strip():
            errors.append(f"{path.relative_to(ROOT)}: diagrama vacío")

    if errors:
        print(f"✗ {len(errors)} problema(s) en {len(files)} documentos:\n")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"✓ {len(files)} documentos verificados: enlaces, bloques de código y codificación correctos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
