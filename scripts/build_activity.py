#!/usr/bin/env python3
"""Builds assets/activity.svg: a themed, animated contribution heatmap for the last year.
Uses the GitHub CLI (`gh api graphql`), so it works locally and in GitHub Actions (GH_TOKEN)."""
import json, subprocess, os
from datetime import date
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "emirmrkaljevic")
OUT = Path(__file__).resolve().parent.parent / "assets" / "activity.svg"
SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
LEVELS = ["#111a2b", "#0e4f5c", "#0e7490", "#06b6d4", "#67e8f9"]

Q = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
LVL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

def fetch():
    out = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={Q}", "-f", f"u={USER}"])
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def streaks(days):
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, cur)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            current += 1
        elif i == 0:
            continue  # today not counted yet
        else:
            break
    return longest, current

def main():
    cal = fetch()
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    total = cal["totalContributions"]
    longest, current = streaks(days)
    active = sum(1 for d in days if d["contributionCount"] > 0)
    best = max(days, key=lambda d: d["contributionCount"])
    W, X0, Y0, S, G = 1000, 40, 132, 14, 4
    cells = []
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            wd = date.fromisoformat(d["date"]).isoweekday() % 7
            x, y = X0 + wi * (S + G), Y0 + wd * (S + G)
            c = LEVELS[LVL.get(d["contributionLevel"], 0)]
            cells.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S}" rx="3.5" fill="{c}" style="animation-delay:{wi*0.025 + wd*0.03:.3f}s"><title>{d["date"]}: {d["contributionCount"]}</title></rect>')
    months, last = [], None
    for wi, w in enumerate(weeks):
        m = date.fromisoformat(w["contributionDays"][0]["date"]).strftime("%b")
        if m != last and wi < len(weeks) - 2:
            months.append(f'<text x="{X0 + wi*(S+G)}" y="{Y0-10}" class="mono" font-size="12" fill="#8b98ad">{m}</text>')
            last = m
    H = Y0 + 7 * (S + G) + 56
    stats = [(f"{total:,}", "contributions"), (f"{active}", "active days"), (f"{longest}d", "longest streak"), (f"{current}d", "current streak")]
    st = "".join(f'<text x="{X0 + i*235}" y="62" class="sans" font-size="30" font-weight="800" fill="#e6edf7">{v}<tspan class="mono" font-size="14" font-weight="400" fill="#8b98ad" dx="10">{l}</tspan></text>' for i, (v, l) in enumerate(stats))
    legend = "".join(f'<rect x="{W-60-5*20+i*20}" y="{H-34}" width="14" height="14" rx="3.5" fill="{c}"/>' for i, c in enumerate(LEVELS))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total} contributions in the last year">
<style>.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}
.hm rect{{animation:in .6s ease-out}} @keyframes in{{from{{opacity:.15}}to{{opacity:1}}}}
@media (prefers-reduced-motion: reduce){{.hm rect{{animation:none}}}}</style>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1424"/><stop offset="1" stop-color="#070b14"/></linearGradient></defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="url(#bg)" stroke="#1c2638" stroke-width="2"/>
{st}
{''.join(months)}
<g class="hm">{''.join(cells)}</g>
<text x="{X0}" y="{H-22}" class="mono" font-size="12" fill="#8b98ad">busiest day: {best['date']} · {best['contributionCount']} contributions · updated daily</text>
<text x="{W-60-5*20-10}" y="{H-22}" class="mono" font-size="12" fill="#8b98ad" text-anchor="end">less</text>{legend}<text x="{W-54}" y="{H-22}" class="mono" font-size="12" fill="#8b98ad">more</text>
</svg>
"""
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({total} contributions, longest {longest}, current {current})")

if __name__ == "__main__":
    main()
