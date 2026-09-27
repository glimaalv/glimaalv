#!/usr/bin/env python3
"""
fetch_contributions.py
Busca o calendário PÚBLICO de contribuições do GitHub (sem token, sem GraphQL API)
em https://github.com/users/<username>/contributions e salva um resumo em JSON.

Uso:
    python scripts/fetch_contributions.py
Saída:
    data/contributions.json
"""
import os
import re
import json
import datetime as dt
import requests
from bs4 import BeautifulSoup

USERNAME = "glimaalv"
URL = f"https://github.com/users/{USERNAME}/contributions"
HEADERS = {
    # um User-Agent "de navegador" evita bloqueios bobos de bot
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

TOOLTIP_COUNT_RE = re.compile(r"([\d,]+)\s+contribution")


def fetch_html() -> str:
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # 1ª passada: cada dia é um <td class="ContributionCalendar-day">
    # com data-date, data-level e um id.
    cells = soup.select("td.ContributionCalendar-day[data-date]")
    days = {}
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        cell_id = cell.get("id")
        if not date:
            continue
        days[date] = {
            "date": date,
            "level": int(level) if level is not None else 0,
            "count": None,
            "_id": cell_id,
        }

    # 2ª passada: <tool-tip for="ID">N contributions on ...</tool-tip>
    # traz a contagem exata.
    id_to_date = {d["_id"]: date for date, d in days.items() if d["_id"]}
    for tip in soup.select("tool-tip[for]"):
        target_id = tip.get("for")
        date = id_to_date.get(target_id)
        if not date:
            continue
        text = tip.get_text(strip=True)
        if text.lower().startswith("no contributions"):
            days[date]["count"] = 0
            continue
        m = TOOLTIP_COUNT_RE.search(text)
        if m:
            days[date]["count"] = int(m.group(1).replace(",", ""))

    # remove o campo interno _id antes de exportar
    for d in days.values():
        d.pop("_id", None)

    return sorted(days.values(), key=lambda d: d["date"])


def compute_stats(days):
    counted = [d["count"] if d["count"] is not None else 0 for d in days]
    total = sum(counted)

    best_day = max(days, key=lambda d: (d["count"] or 0), default=None)

    # sequência atual: anda de trás pra frente a partir do dia mais recente
    current_streak = 0
    for d in reversed(days):
        c = d["count"] or 0
        if c > 0:
            current_streak += 1
        else:
            break

    # maior sequência já registrada
    longest_streak = 0
    running = 0
    for d in days:
        c = d["count"] or 0
        if c > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    monthly_totals = {}
    for d in days:
        month = d["date"][:7]  # "YYYY-MM"
        monthly_totals[month] = monthly_totals.get(month, 0) + (d["count"] or 0)

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
    }


def main():
    html = fetch_html()
    days = parse_days(html)

    if not days:
        raise RuntimeError(
            "Não encontrei nenhuma célula de contribuição. "
            "O GitHub pode ter mudado o HTML da página — confira os seletores "
            "usados em parse_days()."
        )

    stats = compute_stats(days)

    payload = {
        "username": USERNAME,
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }

    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(base_dir)
    out_path = os.path.join(repo_root, "data", "contributions.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"OK -> {out_path} ({len(days)} dias, {stats['total_contributions']} contribuições)")


if __name__ == "__main__":
    main()
