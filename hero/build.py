#!/usr/bin/env python3
"""Renders the profile header: my PanelOS Signature theme, fed with GitHub numbers
instead of sensor readings, put back onto the photo of the screen in my PC.

  PANELOS_THEMES=/path/to/panelos/design/themes-v2 python3 hero/build.py

Needs: Pillow, numpy, the `gh` CLI (GH_TOKEN in CI).
"""
import importlib.util, json, os, subprocess, sys, urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "assets" / "panel.jpg"
USER = os.environ.get("PROFILE_USER", "emirmrkaljevic")
THEMES = Path(os.environ.get("PANELOS_THEMES", HERE.parent.parent / "panelos" / "design" / "themes-v2"))

# Screen corners in hero/photo.jpg (TL, TR, BR, BL), measured by hand.
QUAD = [(955, 357), (2094, 299), (2061, 1010), (1015, 1045)]
CROP = (700, 170, 2480, 1190)          # final header framing
OUT_W = 1600


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
    # progress bar = how far through the year we are
    doy = date.today().timetuple().tm_yday
    ylen = 366 if date.today().year % 4 == 0 else 365
    clock = {doy: f"day {doy}", ylen: f"{ylen}"}
    r._fmt_clock = lambda sec: clock.get(int(sec), str(int(sec)))

    sensors = {"cpu_label": "COMMITS", "gpu_label": "ACTIVE DAYS", "cpu_temp": 1001, "gpu_temp": 1002}
    media = {"title": now["title"], "artist": now["subtitle"],
             "position_sec": doy, "duration_sec": ylen, "playing": True}
    img = r.render_theme("signature", sensors, width=1440, height=960, media=media)
    socials = json.loads((HERE / "socials.json").read_text(encoding="utf-8"))
    return find_me(r, img, socials)


def find_me(r, img, socials, accent=(0xC9, 0xA2, 0x4A)):
    """A 'FIND ME' block in the empty top-right of the panel, built from the
    theme's own fonts, colours and label helpers so it reads as a native widget."""
    img = img.convert("RGBA")
    W, H = img.size
    d = ImageDraw.Draw(img)
    x = r._signature_song_x(W)
    top = 0.099 * H                                   # cap line of the COMMITS label
    play_font = r._font(r.SIG_TEXT, H * r._SIG_PLAY)
    text_font = r._font(r.SIG_LIGHT, H * r._SIG_ARTIST)
    note_font = r._font(r.SIG_LIGHT, H * r._SIG_TIME)
    # header: accent dot + tracked caps, same recipe as PLAYING
    word = "FIND ME"
    ink_h = r._ink_h(play_font, word)
    dot = max(2, int(ink_h * 0.32))
    cy = top + ink_h / 2.0
    d.ellipse((x, cy - dot, x + dot * 2, cy + dot), fill=accent)
    px = x + dot * 3
    track = play_font.size * 0.22
    r._soft_label_shadow(img, px, top, word, play_font, track)
    r._tracked(d, px, top, word, play_font, accent, track)
    cap = r._ink_h(text_font, "H")
    icon = int(round(cap * 1.55))
    row_top = top + ink_h + 0.068 * H
    step = 0.086 * H
    for i, item in enumerate(socials):
        y = row_top + i * step
        mark = Image.open(HERE / "icons" / f"{item['icon']}.png").convert("RGBA").resize((icon, icon), Image.LANCZOS)
        tint = Image.new("RGBA", mark.size, (*r._SIG_LABEL, 0))
        tint.putalpha(mark.getchannel("A").point(lambda a: int(a * 0.92)))
        img.alpha_composite(tint, (int(x), int(round(y + cap / 2 - icon / 2))))
        tx = x + icon + 0.022 * W
        r._soft_label_shadow(img, tx, y, item["text"], text_font, 0.0)
        end = r._ink(d, tx, y, item["text"], text_font, r._SIG_WHITE)
        if item.get("note"):
            nx = tx + text_font.getlength(item["text"]) + 0.018 * W
            ny = y + cap - r._ink_h(note_font, "H")
            r._soft_label_shadow(img, nx, ny, item["note"], note_font, 0.0)
            r._ink(d, nx, ny, item["note"], note_font, r._SIG_SUB)
    return img.convert("RGB")


# ---------------------------------------------------------------- photo
def perspective_coeffs(dst, src):
    """Coefficients for Image.transform: maps output (dst quad) -> input (src rect)."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def composite(panel):
    photo = Image.open(HERE / "photo.jpg").convert("RGB")
    W, H = photo.size
    pw, ph = panel.size
    # an LCD shot on a phone: a touch soft, lifted blacks, slightly cool whites
    lcd = panel.convert("RGB")
    lcd = Image.eval(lcd, lambda v: min(255, int(7 + 250 * (v / 255) ** 0.9 * 1.04)))
    lcd = ImageEnhance.Color(lcd).enhance(1.18)
    arr = np.asarray(lcd).astype(float)
    arr[..., 2] *= 1.04
    arr[..., 0] *= 0.98
    lcd = Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
    coeffs = perspective_coeffs(QUAD, [(0, 0), (pw, 0), (pw, ph), (0, ph)])
    warped = lcd.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    mask = Image.new("L", (pw, ph), 255).transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    warped = warped.filter(ImageFilter.GaussianBlur(1.1))
    mask = mask.filter(ImageFilter.GaussianBlur(1.4))
    # blank out the old picture a few px past the panel edge (the LCD has a thin black border)
    from PIL import ImageDraw
    cx = sum(x for x, _ in QUAD) / 4; cy = sum(y for _, y in QUAD) / 4
    grow = [(x + (6 if x > cx else -3), y + (4 if y > cy else -4)) for x, y in QUAD]
    old = Image.new("L", (W, H), 0)
    ImageDraw.Draw(old).polygon(grow, fill=255)
    photo = Image.composite(Image.new("RGB", (W, H), (9, 9, 16)), photo, old.filter(ImageFilter.GaussianBlur(1.5)))
    out = Image.composite(warped, photo, mask)
    # light spill onto the bezel
    glow = Image.composite(warped, Image.new("RGB", (W, H)), mask).filter(ImageFilter.GaussianBlur(28))
    outside = 1.0 - np.asarray(mask, float)[..., None] / 255.0
    out = Image.fromarray(np.clip(np.asarray(out, float) + np.asarray(glow, float) * 0.30 * outside, 0, 255).astype("uint8"))
    # sensor noise so the screen sits in the same photo
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 3.2, (H, W, 1))
    a = np.asarray(out, float)
    m = np.asarray(mask, float)[..., None] / 255.0
    out = Image.fromarray(np.clip(a + noise * m, 0, 255).astype("uint8"))
    out = out.crop(CROP)
    out = out.resize((OUT_W, round(OUT_W * out.height / out.width)), Image.LANCZOS)
    return out


def main():
    n = github_numbers()
    actors = apify_actors()
    now = json.loads((HERE / "now.json").read_text(encoding="utf-8"))
    out = composite(render_panel(n, now, actors))
    OUT.parent.mkdir(exist_ok=True)
    out.save(OUT, quality=86, optimize=True, progressive=True)
    print(json.dumps({k: v for k, v in n.items() if k not in ("weekly", "daily90")}), "actors", actors)


if __name__ == "__main__":
    main()
