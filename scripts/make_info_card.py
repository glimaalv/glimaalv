#!/usr/bin/env python3
"""
make_info_card.py
Gera um SVG estilo "neofetch" com cargo, stack e uma bio, cada linha
aparecendo em sequência com fade + slide.

Uso:
    python scripts/make_info_card.py
Saída:
    info-card.svg na raiz do repositório

Defina STATIC=1 no ambiente para gerar um frame já congelado (sem animação),
útil para prévias rápidas.
"""
import os
import textwrap

# --- Dados do card (edite aqui) -------------------------------------------
USERNAME = "glimaalv"
TITLE = f"{USERNAME}@github"

FIELDS = [
    ("Cargo", "Desenvolvedor Full Stack Freelancer"),
    ("Stack", "Java, JavaScript, Node.js, Spring Boot, MySQL, Git"),
    ("Foco atual", "Buscando minha 1a vaga como Software Engineer / Software Developer"),
    ("Treino", "Praticando problem-solving no LeetCode"),
]

BIO = (
    "I'm a software developer with a curiosity for learning and improving. "
    "I focus on writing clean, well structured and reusable code, I enjoy "
    "collaborating and sharing knowledge with my friends. Now i'm trying to "
    "earn my first job as a software engineer, I also enjoy devising my own "
    "solutions for everyday challenges. In addition, I am committed to "
    "enhancing my skills on LeetCode to refine my problem-solving abilities."
)

# --- Estilo -----------------------------------------------------------------
WIDTH = 540
THEME = os.environ.get("THEME", "dark")  # "dark" ou "light"

if THEME == "light":
    KEY_COLOR = "#1a7f37"
    VALUE_COLOR = "#24292f"
    BIO_COLOR = "#57606a"
    TITLE_BAR_COLOR = "#f6f8fa"
    TITLE_TEXT_COLOR = "#24292f"
    BG_COLOR = "#ffffff"
    BORDER_COLOR = "#d0d7de"
else:
    KEY_COLOR = "#39d353"
    VALUE_COLOR = "#c9d1d9"
    BIO_COLOR = "#8b949e"
    TITLE_BAR_COLOR = "#161b22"
    TITLE_TEXT_COLOR = "#c9d1d9"
    BG_COLOR = "#0d1117"
    BORDER_COLOR = "#30363d"

FONT = "SFMono-Regular, Consolas, Menlo, monospace"

LINE_H = 24
BIO_LINE_H = 15
PAD_X = 18
TITLE_H = 34
STAGGER = 0.18
DUR = 0.5
STATIC = os.environ.get("STATIC") == "1"


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def animated_group(inner: str, index: int) -> str:
    if STATIC:
        return f'<g>{inner}</g>'
    begin = round(index * STAGGER, 3)
    return f'''<g opacity="0" transform="translate(-14,0)">
      <animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="{DUR}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate"
                          from="-14 0" to="0 0" begin="{begin}s" dur="{DUR}s"
                          fill="freeze" additive="replace" />
      {inner}
    </g>'''


def build_svg() -> str:
    y = TITLE_H + LINE_H
    body_parts = []
    idx = 0

    CHAR_W_VALUE = 7.8  # aproximação da largura de um caractere monoespaçado em font-size 13
    for key, value in FIELDS:
        key_e = escape_xml(key)
        value_x = PAD_X + len(key_e) * 8 + 14
        avail_px = WIDTH - PAD_X - value_x
        max_chars = max(10, int(avail_px / CHAR_W_VALUE))

        wrapped_value_lines = textwrap.wrap(value, width=max_chars) or [""]

        # 1ª linha: "Chave: valor..." lado a lado
        first_line_e = escape_xml(wrapped_value_lines[0])
        inner = (
            f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="13" '
            f'font-weight="bold" fill="{KEY_COLOR}">{key_e}:</text>'
            f'<text x="{value_x}" y="{y}" font-family="{FONT}" '
            f'font-size="13" fill="{VALUE_COLOR}">{first_line_e}</text>'
        )
        body_parts.append(animated_group(inner, idx))
        y += LINE_H
        idx += 1

        # linhas extras (se o valor não coube numa linha só), alinhadas sob o valor
        for extra in wrapped_value_lines[1:]:
            extra_e = escape_xml(extra)
            inner = (
                f'<text x="{value_x}" y="{y}" font-family="{FONT}" '
                f'font-size="13" fill="{VALUE_COLOR}">{extra_e}</text>'
            )
            body_parts.append(animated_group(inner, idx))
            y += LINE_H
            idx += 1

    y += 8
    sep_inner = f'<line x1="{PAD_X}" y1="{y}" x2="{WIDTH - PAD_X}" y2="{y}" stroke="{BORDER_COLOR}" />'
    body_parts.append(animated_group(sep_inner, idx))
    y += 20
    idx += 1

    wrapped = textwrap.wrap(BIO, width=64)
    for line in wrapped:
        inner = (
            f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="11.5" '
            f'fill="{BIO_COLOR}">{escape_xml(line)}</text>'
        )
        body_parts.append(animated_group(inner, idx))
        y += BIO_LINE_H
        idx += 1

    height = y + 18

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}"
     width="{WIDTH}" height="{height:.0f}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1:.0f}" rx="8"
        fill="{BG_COLOR}" stroke="{BORDER_COLOR}" />
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{TITLE_H}" rx="8"
        fill="{TITLE_BAR_COLOR}" />
  <rect x="0.5" y="{TITLE_H - 8}" width="{WIDTH - 1}" height="8" fill="{TITLE_BAR_COLOR}" />
  <circle cx="20" cy="{TITLE_H/2}" r="5" fill="#ff5f56" />
  <circle cx="38" cy="{TITLE_H/2}" r="5" fill="#ffbd2e" />
  <circle cx="56" cy="{TITLE_H/2}" r="5" fill="#27c93f" />
  <text x="{WIDTH/2}" y="{TITLE_H/2}" text-anchor="middle" dominant-baseline="central"
        font-family="{FONT}" font-size="12.5" fill="{TITLE_TEXT_COLOR}">{escape_xml(TITLE)}</text>
  {"".join(body_parts)}
</svg>
'''
    return svg


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(base_dir)
    suffix = "light" if THEME == "light" else "dark"
    out_path = os.path.join(repo_root, f"info-card-{suffix}.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(build_svg())
    print(f"OK -> {out_path}")


if __name__ == "__main__":
    main()
