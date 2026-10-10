#!/usr/bin/env python3
"""Renders the profile header: my PanelOS Signature theme, fed with GitHub numbers
instead of sensor readings, as a flat screenshot. It is cut into tiles so the
links on the screen can be clicked, and the README block between the hero
markers is rewritten to match.

  PANELOS_THEMES=/path/to/panelos/design/themes-v2 python3 hero/build.py

Needs: Pillow, numpy, the `gh` CLI (GH_TOKEN in CI).
"""
import importlib.util, json, os, re, subprocess, sys, urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TILES = ROOT / "assets" / "hero"
README = ROOT / "README.md"
USER = os.environ.get("PROFILE_USER", "emirmrkaljevic")
THEMES = Path(os.environ.get("PANELOS_THEMES", HERE.parent.parent / "panelos" / "design" / "themes-v2"))

W, H = 1440, 960          # the screen, landscape Signature layout
DOCK_H = 168              # link strip under the theme, same screen
BEZEL = 14                # thin plain bezel
BG = (19, 19, 22)         # flat ground instead of album art
BEZEL_RGB = (8, 8, 9)
ACCENT = (0xC9, 0xA2, 0x4A)
GRID_WEEKS = 16
SPLIT_Y = 0.676           # row cut, in an empty band of both columns
PANELOS_URL = "https://emirmrkaljevic.github.io/panelos-site/"


# ---------------------------------------------------------------- data
def gql(query, **vars):
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in vars.items():
        args += ["-f", f"{k}={v}"]
    return json.loads(subprocess.check_output(args))["data"]


REFRESH_MSG = "Refresh the panel"


def refresh_commits_by_day(since):
    """Header-refresh commits that GitHub attributed to me (the first two, before
    they moved to the bot identity). They are not real activity, so they get
    subtracted from the numbers. Keyed by local calendar date."""
    out = {}
    try:
        raw = subprocess.check_output(
            ["gh", "api", "--paginate",
             f"repos/{USER}/{USER}/commits?author={USER}&since={since}&per_page=100",
             "--jq", f'.[] | select(.commit.message | startswith("{REFRESH_MSG}")) | .commit.author.date'],
            text=True)
    except Exception as e:
        print("warning: could not list refresh commits:", e, file=sys.stderr)
        return out
    for line in raw.split():
        d = datetime.fromisoformat(line.replace("Z", "+00:00")).astimezone().date().isoformat()
        out[d] = out.get(d, 0) + 1
    return out


def github_numbers():
    d = gql("""query($u:String!){user(login:$u){
      repositories(privacy:PUBLIC, ownerAffiliations:OWNER){totalCount}
      contributionsCollection{totalCommitContributions
        contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}""", u=USER)["user"]
    cc = d["contributionsCollection"]
    weeks = [[dict(x) for x in w["contributionDays"]] for w in cc["contributionCalendar"]["weeks"]]
    days = [x for w in weeks for x in w]
    # Emir's choice: count every commit, including the daily refresh commits
    fake = {}
    removed = 0
    for x in days:
        k = min(fake.get(x["date"], 0), x["contributionCount"])
        x["contributionCount"] -= k
        removed += k
    counts = [x["contributionCount"] for x in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    weekly = [sum(x["contributionCount"] for x in w) for w in weeks]
    return {
        "commits": max(0, cc["totalCommitContributions"] - removed),
        "contributions": max(0, cc["contributionCalendar"]["totalContributions"] - removed),
        "active_days": sum(1 for c in counts if c),
        "longest": longest,
        "repos": d["repositories"]["totalCount"],
        "weekly": weekly,
        "daily90": counts[-90:],
        "grid": [[x["contributionCount"] for x in w] for w in weeks[-GRID_WEEKS:]],
        "refresh_excluded": removed,
    }


def apify_actors():
    try:
        with urllib.request.urlopen("https://api.apify.com/v2/store?username=tinyrex&limit=1", timeout=20) as r:
            return json.load(r)["data"]["total"]
    except Exception:
        return None


def smooth(xs, k):
    xs = np.asarray(xs, float)
    if len(xs) < k:
        return xs
    return np.convolve(xs, np.ones(k) / k, mode="valid")


# ---------------------------------------------------------------- PanelOS
def load_renderer(status_word):
    """Import the real PanelOS theme renderer. The Signature theme hard-codes the
    word PLAYING, so a temporary copy swaps that one literal before import."""
    text = (THEMES / "render.py").read_text(encoding="utf-8")
    needle = 'status = "PLAYING" if media.get("playing", True) else "PAUSED"'
    assert needle in text, "PanelOS theme changed; update load_renderer()"
    tmp = THEMES / "_profile_render.py"   # same folder, so fonts and assets resolve
    tmp.write_text(text.replace(needle, f"status = {status_word!r}"), encoding="utf-8")
    try:
        spec = importlib.util.spec_from_file_location("panelos_render", tmp)
        r = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(r)
    finally:
        tmp.unlink(missing_ok=True)
    return r


def render_panel(n, now, actors):
    r = load_renderer(now.get("status", "NOW SHIPPING"))
    series = {1: smooth(n["weekly"], 3), 4: smooth(n["daily90"], 7)}

    def spark_points(w, h, seed=0):
        ys = series.get(seed)
        if ys is None or len(ys) < 2 or max(ys) == 0:
            return [(0, h * .6), (w, h * .6)]
        ys = ys / max(ys)
        return [(i / (len(ys) - 1) * w, h * (0.92 - 0.84 * y)) for i, y in enumerate(ys)]

    # The theme formats sensor values; point those formatters at GitHub numbers.
    big = {1001: str(n["commits"]), 1002: str(n["active_days"])}
    r._fmt_temp = lambda v: big.get(int(v), f"{v:.0f}")
    r._metric_sub = lambda s, lk, wk, spaced: ("last 12 months" if lk == "cpu_load"
                                              else f"longest streak {n['longest']}d")
    pairs = [("REPOS", str(n["repos"]))]
    if actors:
        pairs.append(("ACTORS", str(actors)))
    pairs.append(("SYNC", date.today().strftime("%d %b").upper().lstrip("0")))
    r._stat_pairs = lambda s: pairs
    r._spark_points = spark_points
    # Screenshot look: flat ground, crisp lines. No scrim, no spark glow, and no
    # pause glyph (nothing is playing here).
    r._signature_scrim = lambda im, portrait, accent: im
    r._spark_glow = lambda size, box, color, seed: (
        Image.new("RGBA", size, (0, 0, 0, 0)), max(2, int(round((box[3] - box[1]) * 0.09))))
    r._signature_pause = lambda *a, **k: None
    # progress bar = how far through the year we are
    doy = date.today().timetuple().tm_yday
    ylen = 366 if date.today().year % 4 == 0 else 365
    clock = {doy: f"day {doy}", ylen: f"{ylen}"}
    r._fmt_clock = lambda sec: clock.get(int(sec), str(int(sec)))

    sensors = {"cpu_label": "COMMITS", "gpu_label": "ACTIVE DAYS", "cpu_temp": 1001, "gpu_temp": 1002}
    media = {"title": now["title"], "artist": now["subtitle"],
             "position_sec": doy, "duration_sec": ylen, "playing": True}
    cover = Image.new("RGB", (64, 64), BG)
    img = r.render_theme("signature", sensors, cover=cover, width=W, height=H, media=media)
    img = heatmap(r, img.convert("RGBA"), n["grid"])
    socials = json.loads((HERE / "socials.json").read_text(encoding="utf-8"))
    screen = Image.new("RGBA", (W, H + DOCK_H), (*BG, 255))
    screen.alpha_composite(img, (0, 0))
    dock(r, screen, socials)
    return screen, socials, r._signature_song_x(W)


def _mix(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def _header(r, img, d, x, top, word):
    """Accent dot + tracked caps, the same recipe the theme uses for PLAYING."""
    font = r._font(r.SIG_TEXT, H * r._SIG_PLAY)
    ink_h = r._ink_h(font, word)
    dot = max(2, int(ink_h * 0.32))
    cy = top + ink_h / 2.0
    d.ellipse((x, cy - dot, x + dot * 2, cy + dot), fill=ACCENT)
    r._tracked(d, x + dot * 3, top, word, font, ACCENT, font.size * 0.22)
    return ink_h


def heatmap(r, img, grid):
    """Contribution grid in the empty top right, where album art would sit."""
    d = ImageDraw.Draw(img)
    x0 = r._signature_song_x(W)
    top = 0.099 * H                                   # cap line of the COMMITS label
    ink_h = _header(r, img, d, x0, top, f"LAST {len(grid)} WEEKS")
    right = 0.905 * W
    pitch = (right - x0) / len(grid)
    cell = pitch * 0.80
    gy = top + ink_h + 0.062 * H
    vals = sorted(v for w in grid for v in w if v)
    def level(v):
        if not v or not vals:
            return 0
        rank = sum(1 for x in vals if x <= v) / len(vals)
        return 1 + min(3, int(rank * 4 - 1e-9))
    shades = [_mix(BG, (255, 255, 255), 0.07)] + [_mix(BG, ACCENT, t) for t in (0.32, 0.55, 0.78, 1.0)]
    rad = max(2, int(cell * 0.16))
    for i, week in enumerate(grid):
        for j, v in enumerate(week):
            x = x0 + i * pitch
            y = gy + j * pitch
            d.rounded_rectangle((x, y, x + cell, y + cell), radius=rad, fill=shades[level(v)])
    total = sum(sum(w) for w in grid)
    font = r._font(r.SIG_LIGHT, H * r._SIG_TIME)
    ty = gy + 7 * pitch + 0.026 * H
    r._ink(d, x0, ty, f"{total} contributions", font, r._SIG_SUB)
    # legend, right aligned with the grid
    lx = x0 + (len(grid) - 1) * pitch + cell
    sw = cell * 0.62
    for k in range(4, -1, -1):
        lx -= sw
        d.rounded_rectangle((lx, ty, lx + sw, ty + sw), radius=max(1, rad // 2), fill=shades[k])
        lx -= sw * 0.35
    return img


def dock(r, screen, socials):
    """Link strip at the bottom of the screen: five equal cells."""
    d = ImageDraw.Draw(screen)
    y0 = H
    line = _mix(BG, (255, 255, 255), 0.10)
    d.line((0.04 * W, y0, 0.96 * W, y0), fill=line, width=2)
    font = r._font(r.SIG_LIGHT, H * r._SIG_ARTIST)
    cap = r._ink_h(font, "H")
    icon = int(round(cap * 1.6))
    cw = W / len(socials)
    for i, item in enumerate(socials):
        if i:
            d.line((i * cw, y0 + DOCK_H * 0.30, i * cw, y0 + DOCK_H * 0.72), fill=line, width=2)
        label = item["label"]
        tw = font.getlength(label)
        gap = 0.012 * W
        x = i * cw + (cw - (icon + gap + tw)) / 2
        cy = y0 + DOCK_H * 0.51
        mark = Image.open(HERE / "icons" / f"{item['icon']}.png").convert("RGBA").resize((icon, icon), Image.LANCZOS)
        tint = Image.new("RGBA", mark.size, (*r._SIG_LABEL, 0))
        tint.putalpha(mark.getchannel("A"))
        screen.alpha_composite(tint, (int(round(x)), int(round(cy - icon / 2))))
        r._ink(d, x + icon + gap, cy - cap / 2, label, font, r._SIG_WHITE)


def bezel(screen):
    """Plain dark frame with rounded corners; outside the corners is transparent."""
    sw, sh = screen.size
    fw, fh = sw + 2 * BEZEL, sh + 2 * BEZEL
    ss = 4                                           # supersampled corner masks
    outer = Image.new("L", (fw * ss, fh * ss), 0)
    ImageDraw.Draw(outer).rounded_rectangle((0, 0, fw * ss - 1, fh * ss - 1), radius=26 * ss, fill=255)
    inner = Image.new("L", (sw * ss, sh * ss), 0)
    ImageDraw.Draw(inner).rounded_rectangle((0, 0, sw * ss - 1, sh * ss - 1), radius=8 * ss, fill=255)
    frame = Image.new("RGBA", (fw, fh), (*BEZEL_RGB, 255))
    frame.paste(screen.convert("RGB"), (BEZEL, BEZEL), inner.resize((sw, sh), Image.LANCZOS))
    frame.putalpha(outer.resize((fw, fh), Image.LANCZOS))
    return frame


# ---------------------------------------------------------------- tiles
def tiles(frame, socials, now, song_x):
    """Three rows. Rows 1-2: stats on the left, contribution grid / now shipping
    on the right. Row 3: one tile per link. Every row is taller than a line of
    text even on a phone, and images are top-aligned, so rows meet with no gap."""
    fw, fh = frame.size
    sx = int(round(BEZEL + song_x - 0.035 * W))
    sy = int(round(BEZEL + SPLIT_Y * H))
    dy = BEZEL + H
    ship = now.get("url", "https://apify.com/tinyrex")
    rows = [
        [((0, 0, sx, sy), PANELOS_URL, "GitHub numbers on my PanelOS screen: commits and active days over the last 12 months"),
         ((sx, 0, fw, sy), f"https://github.com/{USER}", "My contribution grid for the last weeks")],
        [((0, sy, sx, dy), PANELOS_URL, "Active days, repos, Apify actors, last sync"),
         ((sx, sy, fw, dy), ship, f"Now shipping: {now['title']}, {now['subtitle']}")],
    ]
    cuts = [0] + [int(round(BEZEL + (i + 1) * W / len(socials))) for i in range(len(socials) - 1)] + [fw]
    rows.append([((cuts[i], dy, cuts[i + 1], fh), it["url"], it["label"]) for i, it in enumerate(socials)])
    TILES.mkdir(parents=True, exist_ok=True)
    for old in TILES.glob("*.png"):
        old.unlink()
    html = []
    for ri, row in enumerate(rows):
        parts = []
        total = 0.0
        for ci, (box, url, alt) in enumerate(row):
            name = f"r{ri + 1}{'abcdefgh'[ci]}.png"
            frame.crop(box).save(TILES / name, optimize=True)
            pct = int((box[2] - box[0]) / fw * 100000) / 1000      # floor, so a row never wraps
            total += pct
            parts.append(f'<a href="{url}"><img src="./assets/hero/{name}" width="{pct}%" align="top" alt="{alt}"></a>')
        html.append("".join(parts))
    return "<p>" + "<br>".join(html) + "</p>"


def write_readme(block):
    text = README.read_text(encoding="utf-8")
    new = re.sub(r"<!-- hero:start -->.*?<!-- hero:end -->",
                 lambda m: f"<!-- hero:start -->\n{block}\n<!-- hero:end -->", text, flags=re.S)
    assert "<!-- hero:start -->" in new, "README has no hero markers"
    README.write_text(new, encoding="utf-8")


def main():
    n = github_numbers()
    actors = apify_actors()
    now = json.loads((HERE / "now.json").read_text(encoding="utf-8"))
    screen, socials, song_x = render_panel(n, now, actors)
    frame = bezel(screen)
    if os.environ.get("HERO_FULL"):
        frame.save(os.environ["HERO_FULL"])
    write_readme(tiles(frame, socials, now, song_x))
    print(json.dumps({k: v for k, v in n.items() if k not in ("weekly", "daily90", "grid")}), "actors", actors)


if __name__ == "__main__":
    main()
