"""Render public-only GitHub intelligence. No credentials or third-party stats service."""
from collections import Counter
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
import json
import xml.etree.ElementTree as ET

USER = "nazirreally"
TARGET = Path("assets/obsidian-intelligence.svg")
BG, CARD, BORDER, RED, HI, WHITE, MUTED = (
    "#09090B", "#18181B", "#27272A", "#B91C1C", "#EF4444", "#FAFAFA", "#A1A1AA"
)
LEVELS = ["#27272A", "#581C1C", "#7F1D1D", RED, HI]


def get(url):
    req = Request(url, headers={"User-Agent": "obsidian-profile-refresh/1.0"})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def api(path):
    return json.loads(get("https://api.github.com" + path))


class Calendar(HTMLParser):
    """Extract the published day/intensity attributes, not inferred commit counts."""

    def __init__(self):
        super().__init__()
        self.days = {}

    def handle_starttag(self, tag, attrs):
        if tag not in {"td", "rect"}:
            return
        a = dict(attrs)
        if "data-date" not in a or "data-level" not in a:
            return
        day = date.fromisoformat(a["data-date"])
        level = int(a["data-level"])
        if not 0 <= level <= 4:
            raise ValueError("Unexpected GitHub contribution level")
        if day in self.days and self.days[day] != level:
            raise ValueError("Conflicting calendar values")
        self.days[day] = level


def read_calendar(html, today):
    parser = Calendar()
    parser.feed(html)
    start = today - timedelta(days=364)
    days = {d: v for d, v in parser.days.items() if start <= d <= today}
    if len(days) < 350:
        raise ValueError("Incomplete contribution calendar; retain previous snapshot")
    return days


def public_inventory():
    repos = []
    page = 1
    while True:
        batch = api(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("Unexpected repository response")
        repos.extend(r for r in batch if not r["private"] and not r["archived"] and not r["fork"])
        if len(batch) < 100:
            break
        page += 1
    langs = Counter()
    for repo in repos:
        values = api(f"/repos/{USER}/{repo['name']}/languages")
        if not isinstance(values, dict) or any(type(n) is not int or n < 0 for n in values.values()):
            raise ValueError("Invalid language response")
        langs.update(values)
    return repos, langs


def render(repos, langs, days, today):
    def text(x, y, s, size=16, color=WHITE, weight=400):
        return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
                f'font-weight="{weight}">{escape(str(s))}</text>')

    def rect(x, y, w, h, fill=CARD, stroke=BORDER):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="{stroke}"/>'

    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="420" viewBox="0 0 1120 420" role="img" aria-labelledby="title desc">',
           '<title id="title">Public GitHub intelligence</title>',
           '<desc id="desc">Actual public repository statistics, source-byte language distribution and published contribution intensity.</desc>',
           rect(0, 0, 1120, 420, BG), '<g font-family="Arial,Helvetica,sans-serif">',
           text(24, 32, "GITHUB INTELLIGENCE / PUBLIC SNAPSHOT", 15, MUTED, 700)]
    for i, (value, label) in enumerate([(len(repos), "ACTIVE OWNED REPOS"),
                                        (sum(r["stargazers_count"] for r in repos), "TOTAL REPO STARS"),
                                        (sum(r["forks_count"] for r in repos), "TOTAL REPO FORKS")]):
        x = 24 + 362 * i
        out += [rect(x, 48, 348, 70), text(x+14, 94, value, 38, WHITE, 700),
                text(x+105, 86, label, 13, MUTED, 700)]
    out += [text(24, 148, "CONTRIBUTION INTENSITY / LAST 365 DAYS", 14, MUTED, 700)]
    start = today - timedelta(days=364)
    sunday = start - timedelta(days=(start.weekday()+1)%7)
    for d, level in sorted(days.items()):
        delta = (d-sunday).days
        x, y = 24 + (delta//7)*13, 163 + (delta%7)*13
        out.append(rect(x, y, 10, 10, LEVELS[level], "none"))
    out += [text(24, 270, "Less", 12, MUTED)]
    for i, c in enumerate(LEVELS):
        out.append(rect(61+i*15, 259, 11, 11, c, "none"))
    out += [text(141, 270, "More", 12, MUTED),
            text(24, 294, "GitHub-published levels; blank days are unavailable.", 13, MUTED)]
    total = sum(langs.values())
    out += [text(752, 148, "LANGUAGES / SOURCE BYTES", 14, MUTED, 700)]
    if total:
        entries = langs.most_common(5)
        other = total - sum(n for _, n in entries)
        if other:
            entries.append(("Other", other))
        for i, (name, n) in enumerate(entries):
            y = 169 + 32*i
            out += [text(752, y, name, 13), text(1030, y, f"{n/total:.1%}", 13, MUTED),
                    rect(752, y+5, 332, 7, BORDER, "none"),
                    rect(752, y+5, 332*n/total, 7, HI if i == 0 else MUTED, "none")]
    else:
        out.append(text(752, 175, "No language bytes reported", 14, MUTED))
    out += [text(24, 369, "PUBLIC OWNED NON-FORK, NON-ARCHIVED REPOSITORIES", 12, MUTED, 700),
            text(24, 393, f"Source: GitHub REST + public contribution calendar · UTC {today.isoformat()}", 13, MUTED),
            '</g></svg>']
    content = "\n".join(out) + "\n"
    ET.fromstring(content)
    return content


def main():
    today = date.today()
    repos, langs = public_inventory()
    days = read_calendar(get(f"https://github.com/users/{USER}/contributions"), today)
    content = render(repos, langs, days, today)
    # Replace only after all sources have succeeded and the SVG parses.
    temp = TARGET.with_suffix(".tmp")
    temp.write_text(content, encoding="utf-8")
    temp.replace(TARGET)


if __name__ == "__main__":
    main()
