#!/usr/bin/env python3
"""
render_heatmap_svg.py
Lê data/contributions.json e desenha a grade 53 semanas x 7 dias, com uma
revelação animada diagonal (roda uma vez e congela) + legenda + rodapé de stats.

Uso:
    python scripts/render_heatmap_svg.py
Saída:
    contrib-heatmap.svg na raiz do repositório
"""
import os
import json
import datetime as dt

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BOX = 13
GAP = 3.7        # BOX+GAP calibrado para o total bater com ascii(370)+info(540) do README
LEFT_PAD = 28   # espaço pros rótulos de dia da semana
TOP_PAD = 20    # espaço pros rótulos de mês
BOTTOM_PAD = 34  # legenda + stats
STAGGER = 0.012
DUR = 0.4
DAY_LABELS = ["", "Seg", "", "Qua", "", "Sex", ""]
MONTH_ABBR = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
              "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def load_data(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_grid(days):
    """Organiza os dias numa grade de 7 linhas (dia da semana) x N colunas
    (semanas), alinhado ao domingo, como o calendário do GitHub."""
    parsed = [
        {**d, "_dt": dt.date.fromisoformat(d["date"])}
        for d in days
    ]
    parsed.sort(key=lambda d: d["_dt"])

    first = parsed[0]["_dt"]
    # recua até o domingo anterior (weekday(): Mon=0..Sun=6 -> queremos Sun=0)
    offset = (first.weekday() + 1) % 7
    grid_start = first - dt.timedelta(days=offset)

    weeks = {}
    for d in parsed:
        delta = (d["_dt"] - grid_start).days
        week = delta // 7
        weekday = delta % 7
        weeks.setdefault(week, {})[weekday] = d

    return weeks, grid_start


def month_label_positions(weeks, grid_start):
    labels = []
    seen_months = set()
    for week_idx in sorted(weeks):
        day0 = weeks[week_idx].get(0)
        ref_date = day0["_dt"] if day0 else grid_start + dt.timedelta(weeks=week_idx)
        key = (ref_date.year, ref_date.month)
        if ref_date.day <= 7 and key not in seen_months:
            seen_months.add(key)
            labels.append((week_idx, MONTH_ABBR[ref_date.month - 1]))
    return labels


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(data, static=False):
    days = data["days"]
    stats = data["stats"]
    weeks, grid_start = build_grid(days)
    n_weeks = max(weeks) + 1

    width = LEFT_PAD + n_weeks * (BOX + GAP)
    height = TOP_PAD + 7 * (BOX + GAP) + BOTTOM_PAD

    parts = []

    for i, label in enumerate(DAY_LABELS):
        if not label:
            continue
        y = TOP_PAD + i * (BOX + GAP) + BOX - 2
        parts.append(
            f'<text x="0" y="{y}" font-size="9" fill="#8b949e" '
            f'font-family="SFMono-Regular, Consolas, monospace">{label}</text>'
        )

    for week_idx, label in month_label_positions(weeks, grid_start):
        x = LEFT_PAD + week_idx * (BOX + GAP)
        parts.append(
            f'<text x="{x}" y="12" font-size="9" fill="#8b949e" '
            f'font-family="SFMono-Regular, Consolas, monospace">{label}</text>'
        )

    max_delay = 0.0
    for week_idx in sorted(weeks):
        for weekday in range(7):
            d = weeks[week_idx].get(weekday)
            level = d["level"] if d else 0
            level = max(0, min(4, level))
            color = PALETTE[level]

            x = LEFT_PAD + week_idx * (BOX + GAP)
            y = TOP_PAD + weekday * (BOX + GAP)

            title = ""
            if d:
                count = d["count"] if d["count"] is not None else "?"
                title = f'<title>{escape_xml(str(count))} contribuições em {d["date"]}</title>'

            # atraso diagonal: cresce com (semana + dia da semana)
            delay = round((week_idx + weekday) * STAGGER, 3)
            max_delay = max(max_delay, delay)

            if static:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" '
                    f'fill="{color}">{title}</rect>'
                )
            else:
                parts.append(f'''<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2"
      fill="{color}" opacity="0">{title}
      <animate attributeName="opacity" from="0" to="1"
                begin="{delay}s" dur="{DUR}s" fill="freeze" />
    </rect>''')

    # legenda "Less -> More"
    legend_y = height - BOTTOM_PAD + 22
    legend_x = LEFT_PAD
    parts.append(
        f'<text x="{legend_x}" y="{legend_y}" font-size="9" fill="#8b949e" '
        f'font-family="SFMono-Regular, Consolas, monospace">Menos</text>'
    )
    lx = legend_x + 40
    for level, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx}" y="{legend_y - 9}" width="{BOX}" height="{BOX}" rx="2" fill="{color}" />')
        lx += BOX + GAP
    parts.append(
        f'<text x="{lx + 4}" y="{legend_y}" font-size="9" fill="#8b949e" '
        f'font-family="SFMono-Regular, Consolas, monospace">Mais</text>'
    )

    total = stats["total_contributions"]
    streak = stats["current_streak"]
    longest = stats["longest_streak"]
    footer = (
        f"{total} contribuições no último ano · sequência atual: {streak} dia(s) "
        f"· recorde: {longest} dia(s)"
    )
    parts.append(
        f'<text x="{width - LEFT_PAD}" y="{legend_y}" font-size="9" fill="#8b949e" '
        f'text-anchor="end" font-family="SFMono-Regular, Consolas, monospace">'
        f'{escape_xml(footer)}</text>'
    )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"
     width="{width}" height="{height}">
{chr(10).join(parts)}
</svg>
'''
    return svg


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(base_dir)
    data_path = os.path.join(repo_root, "data", "contributions.json")
    data = load_data(data_path)

    static = os.environ.get("STATIC") == "1"
    svg = build_svg(data, static=static)

    out_path = os.path.join(repo_root, "contrib-heatmap.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK -> {out_path}")


if __name__ == "__main__":
    main()
