#!/usr/bin/env python3
"""
make_ascii_svg.py
Converte scripts/source-prepped.png em um SVG monocromático de arte ASCII
que "digita" (wipe da esquerda pra direita) linha por linha, uma vez só.

Uso:
    python scripts/make_ascii_svg.py
Saída:
    <username>-ascii.svg na raiz do repositório
"""
import os
import numpy as np
from PIL import Image

# --- Configuração ---------------------------------------------------------
USERNAME = "glimaalv"
INPUT_IMAGE = "source-prepped.png"
COLS = 80           # largura em caracteres
ROWS = 44           # altura em caracteres
TARGET_WIDTH_PX = 370   # combina com a largura usada no README (2 colunas na tabela)
CHAR_W = TARGET_WIDTH_PX / COLS
FONT_SIZE = CHAR_W / 0.6
CHAR_H = FONT_SIZE * 1.0
THEME = os.environ.get("THEME", "dark")  # "dark" ou "light"
FILL_COLOR = "#57606a" if THEME == "light" else "#8b949e"  # ajustado por tema p/ contraste
BG = "transparent"
ROW_DURATION = 0.9            # segundos para cada linha "digitar"
ROW_STAGGER = 0.045           # atraso entre o início de uma linha e a próxima
CURSOR_COLOR = "#1a7f37" if THEME == "light" else "#39d353"

# rampa: claro/vazio (espaço) -> escuro/denso
RAMP = " .`:-=+*cs#%@"


def load_brightness_grid(path: str, cols: int, rows: int) -> np.ndarray:
    img = Image.open(path).convert("L")
    # caracteres de terminal não são quadrados; corrige a proporção
    img = img.resize((cols, rows), Image.LANCZOS)
    return np.asarray(img, dtype=np.float32)


def brightness_to_char(v: float) -> str:
    # v: 0 (preto) .. 255 (branco/fundo)
    idx = int(round((255 - v) / 255 * (len(RAMP) - 1)))
    idx = max(0, min(len(RAMP) - 1, idx))
    return RAMP[idx]


def build_rows(grid: np.ndarray):
    rows = []
    for r in range(grid.shape[0]):
        line = "".join(brightness_to_char(v) for v in grid[r])
        rows.append(line)
    return rows


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(rows) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H + 20

    defs = []
    body = []

    for i, line in enumerate(rows):
        y = 15 + i * CHAR_H
        clip_id = f"clip{i}"
        begin = round(i * ROW_STAGGER, 3)

        # clipPath com um retângulo que anima de largura 0 até a largura total
        defs.append(f'''
    <clipPath id="{clip_id}">
      <rect x="0" y="{y - CHAR_H}" height="{CHAR_H + 2}" width="0">
        <animate attributeName="width" from="0" to="{width}"
                  begin="{begin}s" dur="{ROW_DURATION}s"
                  fill="freeze" calcMode="linear" />
      </rect>
    </clipPath>''')

        safe_line = escape_xml(line)
        body.append(
            f'    <text x="0" y="{y}" clip-path="url(#{clip_id})" '
            f'font-family="SFMono-Regular, Consolas, Menlo, monospace" '
            f'font-size="{FONT_SIZE}" fill="{FILL_COLOR}" '
            f'xml:space="preserve">{safe_line}</text>'
        )

        # "cursor" que percorre a linha junto com o wipe
        cursor_w = 2
        body.append(f'''    <rect x="0" y="{y - CHAR_H + 1}" width="{cursor_w}" height="{CHAR_H - 2}" fill="{CURSOR_COLOR}">
      <animate attributeName="x" from="0" to="{width - cursor_w}"
                begin="{begin}s" dur="{ROW_DURATION}s"
                fill="freeze" calcMode="linear" />
      <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.92;1"
                begin="{begin}s" dur="{ROW_DURATION}s" fill="freeze" />
    </rect>''')

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}"
     width="{width:.0f}" height="{height:.0f}">
  <defs>{"".join(defs)}
  </defs>
  <g>
{chr(10).join(body)}
  </g>
</svg>
'''
    return svg


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(base_dir)
    input_path = os.path.join(base_dir, INPUT_IMAGE)

    grid = load_brightness_grid(input_path, COLS, ROWS)
    rows = build_rows(grid)
    svg = build_svg(rows)

    suffix = "light" if THEME == "light" else "dark"
    out_path = os.path.join(repo_root, f"{USERNAME}-ascii-{suffix}.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK -> {out_path}")


if __name__ == "__main__":
    main()
