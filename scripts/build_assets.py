#!/usr/bin/env python3
"""Generates the static animated SVGs used by the profile README (header, terminal,
project cards, footer). Run: python3 scripts/build_assets.py"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
BG0, BG1, LINE = "#070b14", "#0d1424", "#1c2638"
TEXT, MUTED = "#e6edf7", "#8b98ad"
CYAN, VIOLET, AMBER, MINT, ROSE = "#22d3ee", "#a78bfa", "#fbbf24", "#34d399", "#fb7185"

BASE_STYLE = f"""
.sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""

def save(name, svg):
    (OUT / name).write_text(svg.strip() + "\n", encoding="utf-8")
    print("wrote", name)

# ---------------------------------------------------------------- header
def header():
    roles = [
        ("Software Developer", "@ UniCredit", CYAN),
        ("Founder", "@ Skin to Scan", MINT),
        ("Builder", "@ TinyRex data tools", VIOLET),
        ("Maker", "@ PanelOS", AMBER),
    ]
    role_svg = ""
    for i, (a, b, c) in enumerate(roles):
        role_svg += (f'<text class="mono role" style="animation-delay:{i*3}s" x="72" y="262" font-size="28">'
                     f'<tspan fill="{MUTED}">&gt; </tspan><tspan fill="{TEXT}" font-weight="600">{a}</tspan>'
                     f'<tspan fill="{c}"> {b}</tspan></text>')
    chips = ["PL/SQL", "Oracle APEX", "Python", "AI / ML", "Automation"]
    chip_svg, x = "", 72
    for ch in chips:
        w = 18 + len(ch) * 10.2
        chip_svg += (f'<g><rect x="{x}" y="336" width="{w:.0f}" height="34" rx="17" fill="#ffffff08" stroke="{LINE}"/>'
                     f'<text class="mono" x="{x + w/2:.0f}" y="358" font-size="15" fill="{MUTED}" text-anchor="middle">{ch}</text></g>')
        x += w + 10
    eq = ""
    for i in range(7):
        h = 64
        eq += (f'<rect x="{1046 + i*11}" y="{116}" width="7" height="{h}" rx="2" fill="url(#eqg)" '
               f'style="animation-duration:{0.7 + (i*0.37)%0.6:.2f}s;animation-delay:-{i*0.23:.2f}s"/>')
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420" width="1200" height="420" role="img" aria-label="Hi, I'm Emir. Software developer, founder of Skin to Scan, builder of TinyRex and PanelOS.">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".28"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
  <radialGradient id="glow2" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{CYAN}" stop-opacity=".22"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
  <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="640" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{AMBER}"/>
    <animate attributeName="x1" values="0;640;0" dur="10s" repeatCount="indefinite"/>
    <animate attributeName="x2" values="640;1280;640" dur="10s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="eqg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
  <linearGradient id="art" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{ROSE}"><animate attributeName="stop-color" values="{ROSE};{VIOLET};{CYAN};{ROSE}" dur="9s" repeatCount="indefinite"/></stop>
    <stop offset="1" stop-color="{AMBER}"><animate attributeName="stop-color" values="{AMBER};{ROSE};{VIOLET};{AMBER}" dur="9s" repeatCount="indefinite"/></stop>
  </linearGradient>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity=".035"/></pattern>
  <clipPath id="card"><rect width="1200" height="420" rx="26"/></clipPath>
  <clipPath id="screen"><rect x="778" y="92" width="344" height="196" rx="10"/></clipPath>
</defs>
<style>{BASE_STYLE}
.role{{opacity:0;animation:role 12s infinite}}
@keyframes role{{0%{{opacity:0;transform:translateY(10px)}}3%,22%{{opacity:1;transform:translateY(0)}}25%,100%{{opacity:0;transform:translateY(-10px)}}}}
.cur{{animation:blink 1s steps(1) infinite}} @keyframes blink{{50%{{opacity:0}}}}
.pulse{{animation:pulse 2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.35;transform:scale(.7)}}}}
.eq rect{{transform-box:fill-box;transform-origin:bottom;animation:eq .9s ease-in-out infinite alternate}}
@keyframes eq{{0%{{transform:scaleY(.18)}}100%{{transform:scaleY(1)}}}}
.scan{{animation:scan 5s linear infinite}} @keyframes scan{{0%{{transform:translateY(0)}}100%{{transform:translateY(200px)}}}}
.float{{animation:float 6s ease-in-out infinite}} @keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
@media (max-width:640px){{.device,.chips{{display:none}} .left{{transform:translate(-27px,-60px) scale(1.4)}}}}
.prog{{animation:prog 14s linear infinite;transform-box:fill-box;transform-origin:left}} @keyframes prog{{0%{{transform:scaleX(.02)}}100%{{transform:scaleX(1)}}}}
</style>
<g clip-path="url(#card)">
  <rect width="1200" height="420" fill="url(#bg)"/>
  <rect width="1200" height="420" fill="url(#grid)"/>
  <circle cy="200" r="300" fill="url(#glow)"><animate attributeName="cx" values="260;420;260" dur="16s" repeatCount="indefinite"/></circle>
  <circle cx="960" cy="190" r="260" fill="url(#glow2)"><animate attributeName="r" values="240;290;240" dur="7s" repeatCount="indefinite"/></circle>
</g>
<rect x=".5" y=".5" width="1199" height="419" rx="26" fill="none" stroke="{LINE}"/>

<g class="left">
<circle class="pulse" cx="80" cy="88" r="6" fill="{MINT}"/>
<text class="mono" x="96" y="94" font-size="17" fill="{MUTED}">online <tspan fill="{LINE}">│</tspan> github.com/<tspan fill="{TEXT}">emirmrkaljevic</tspan></text>

<text class="sans" x="68" y="196" font-size="88" font-weight="800" letter-spacing="-2" fill="url(#name)">Hi, I'm Emir<tspan fill="{TEXT}">.</tspan></text>
{role_svg}
<text class="sans" x="72" y="310" font-size="21" fill="{MUTED}">Banking software by day. AI &amp; data products by night.</text>
<g class="chips">{chip_svg}</g>
</g>

<!-- PanelOS-style mini screen -->
<g class="device"><g class="float">
  <text class="mono" x="780" y="64" font-size="13" fill="{MUTED}" letter-spacing="1">PANELOS · LIVE</text>
  <rect x="764" y="76" width="372" height="226" rx="18" fill="#0a0f1a" stroke="#2a3650" stroke-width="2"/>
  <rect x="778" y="92" width="344" height="196" rx="10" fill="#04060b"/>
  <g clip-path="url(#screen)">
    <!-- gauges -->
    <g transform="translate(832 150)">
      <circle r="34" fill="none" stroke="{LINE}" stroke-width="8"/>
      <circle r="34" fill="none" stroke="{CYAN}" stroke-width="8" stroke-linecap="round" stroke-dasharray="213.6" transform="rotate(-90)">
        <animate attributeName="stroke-dashoffset" values="120;95;130;105;120" dur="6s" repeatCount="indefinite"/></circle>
      <text class="mono" y="4" font-size="17" font-weight="700" fill="{TEXT}" text-anchor="middle">47°</text>
      <text class="mono" y="58" font-size="11" fill="{MUTED}" text-anchor="middle" letter-spacing="2">CPU</text>
    </g>
    <g transform="translate(924 150)">
      <circle r="34" fill="none" stroke="{LINE}" stroke-width="8"/>
      <circle r="34" fill="none" stroke="{VIOLET}" stroke-width="8" stroke-linecap="round" stroke-dasharray="213.6" transform="rotate(-90)">
        <animate attributeName="stroke-dashoffset" values="90;125;80;110;90" dur="7s" repeatCount="indefinite"/></circle>
      <text class="mono" y="4" font-size="17" font-weight="700" fill="{TEXT}" text-anchor="middle">52°</text>
      <text class="mono" y="58" font-size="11" fill="{MUTED}" text-anchor="middle" letter-spacing="2">GPU</text>
    </g>
    <!-- album art + eq -->
    <rect x="976" y="112" width="66" height="66" rx="8" fill="url(#art)"/>
    <circle cx="1009" cy="145" r="15" fill="#04060b" opacity=".55"/><circle cx="1009" cy="145" r="4" fill="#ffffff" opacity=".7"/>
    <g class="eq">{eq}</g>
    <!-- now playing -->
    <text class="mono" x="796" y="236" font-size="12" fill="{MUTED}">♪ now playing</text>
    <text class="mono" x="1104" y="236" font-size="12" fill="{MUTED}" text-anchor="end">RAM 62%</text>
    <rect x="796" y="250" width="308" height="5" rx="2.5" fill="{LINE}"/>
    <rect class="prog" x="796" y="250" width="308" height="5" rx="2.5" fill="{AMBER}"/>
    <rect class="scan" x="778" y="88" width="344" height="3" fill="#ffffff" opacity=".05"/>
  </g>
  <path d="M928 302h44l10 26h-64z" fill="#0a0f1a" stroke="#2a3650" stroke-width="2"/>
  <rect x="900" y="326" width="100" height="8" rx="4" fill="#2a3650"/>
</g></g>
</svg>"""
    save("header.svg", svg)

# ---------------------------------------------------------------- terminal
def terminal():
    W, H, CYCLE = 680, 392, 16.0
    lines = [  # (kind, text-parts)
        ("cmd", "whoami"),
        ("out", [(TEXT, "emir"), (MUTED, " · developer · founder · builder")]),
        ("cmd", "cat now.txt"),
        ("out", [(CYAN, "▸ "), (TEXT, "Software Developer @ UniCredit")]),
        ("out", [(MUTED, "  PL/SQL · Oracle APEX · Jasper · Python")]),
        ("out", [(MINT, "▸ "), (TEXT, "Founder of Skin to Scan"), (MUTED, " · CNNs")]),
        ("out", [(VIOLET, "▸ "), (TEXT, "Shipping TinyRex"), (MUTED, " + "), (TEXT, "PanelOS")]),
        ("cmd", "cat creds.txt"),
        ("out", [(AMBER, "▸ "), (TEXT, "BSc Software Engineering · PCAP")]),
    ]
    body, y, t = "", 96, 0.4
    for kind, content in lines:
        if kind == "cmd":
            tw = len(content) * 0.09 + 0.2
            text_w = 28 + len(content) * 10.9
            k0, k1 = t / CYCLE, (t + tw) / CYCLE
            body += (f'<text class="mono" x="32" y="{y}" font-size="18" fill="{MINT}">$</text>'
                     f'<clipPath id="c{y}"><rect x="52" y="{y-20}" height="28" width="0">'
                     f'<animate attributeName="width" values="0;0;{text_w:.0f};{text_w:.0f};0" keyTimes="0;{k0:.3f};{k1:.3f};.97;1" dur="{CYCLE}s" repeatCount="indefinite"/></rect></clipPath>'
                     f'<text class="mono" x="52" y="{y}" font-size="18" fill="{TEXT}" clip-path="url(#c{y})">{content}</text>')
            t += tw + 0.35
        else:
            k0 = t / CYCLE
            spans = "".join(f'<tspan fill="{c}">{s}</tspan>' for c, s in content)
            body += (f'<text class="mono" x="52" y="{y}" font-size="18" opacity="0">{spans}'
                     f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{k0:.3f};{k0+0.01:.3f};.97;1" dur="{CYCLE}s" repeatCount="indefinite"/></text>')
            t += 0.25
        y += 31
    k0 = t / CYCLE
    body += (f'<text class="mono" x="32" y="{y}" font-size="18" fill="{MINT}" opacity="0">$ <tspan class="cur" fill="{TEXT}">█</tspan>'
             f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{k0:.3f};{k0+0.01:.3f};.97;1" dur="{CYCLE}s" repeatCount="indefinite"/></text>')
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="whoami: Software Developer at UniCredit, founder of Skin to Scan, building TinyRex and PanelOS. BSc Software Engineering, PCAP certified.">
<style>{BASE_STYLE}.cur{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}</style>
<defs><linearGradient id="tb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121a2b"/><stop offset="1" stop-color="{BG0}"/></linearGradient></defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="url(#tb)" stroke="{LINE}" stroke-width="2"/>
<path d="M1 46h{W-2}" stroke="{LINE}" stroke-width="2"/>
<circle cx="28" cy="24" r="7" fill="{ROSE}"/><circle cx="52" cy="24" r="7" fill="{AMBER}"/><circle cx="76" cy="24" r="7" fill="{MINT}"/>
<text class="mono" x="{W/2}" y="29" font-size="14" fill="{MUTED}" text-anchor="middle">emir@github: ~</text>
{body}
</svg>"""
    save("terminal.svg", svg)

# ---------------------------------------------------------------- project cards
def card(name, title, sub, accent, visual, label):
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 170" width="480" height="170" role="img" aria-label="{label}">
<style>{BASE_STYLE}
.a1{{animation:a1 3s ease-in-out infinite alternate}} @keyframes a1{{0%{{transform:translateY(0)}}100%{{transform:translateY(74px)}}}}
.up{{animation:up 6s linear infinite}} @keyframes up{{0%{{transform:translateY(0)}}100%{{transform:translateY(-96px)}}}}
.eq rect{{transform-box:fill-box;transform-origin:bottom;animation:eq .8s ease-in-out infinite alternate}} @keyframes eq{{0%{{transform:scaleY(.2)}}100%{{transform:scaleY(1)}}}}
.cell{{animation:cell 4.8s ease-in-out infinite;opacity:.15}} @keyframes cell{{0%,100%{{opacity:.15}}20%,45%{{opacity:1}}}}
</style>
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></linearGradient>
  <radialGradient id="gl" cx="1" cy="0" r="1"><stop offset="0" stop-color="{accent}" stop-opacity=".22"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  <clipPath id="cl"><rect width="480" height="170" rx="18"/></clipPath>
</defs>
<g clip-path="url(#cl)">
  <rect width="480" height="170" fill="url(#g)"/><rect width="480" height="170" fill="url(#gl)"/>
  <rect width="480" height="4" fill="{accent}"/>
</g>
<rect x="1" y="1" width="478" height="168" rx="17" fill="none" stroke="{LINE}" stroke-width="2"/>
<text class="sans" x="28" y="78" font-size="34" font-weight="800" fill="{TEXT}" letter-spacing="-.5">{title}</text>
<text class="mono" x="30" y="114" font-size="16" fill="{accent}">{sub}</text>
{visual}
</svg>"""
    save(f"card-{name}.svg", svg)

def cards():
    # Skin to Scan: lesion + scanning beam + detection brackets
    v_skin = f"""
<g transform="translate(330 30)">
  <rect width="120" height="110" rx="12" fill="#0b1220" stroke="{LINE}"/>
  <path d="M60 30c16-2 30 10 28 26s-12 28-30 26-28-12-26-28 12-22 28-24z" fill="#7a4b3a"/>
  <path d="M58 40c9 0 18 8 16 17s-8 15-18 14-15-8-13-17 7-14 15-14z" fill="#4a2a22"/>
  <g stroke="{MINT}" stroke-width="3" fill="none" stroke-linecap="round">
    <path d="M22 26v-10h12M98 26v-10h-12M22 84v10h12M98 84v10h-12"/></g>
  <g class="a1"><rect x="10" y="16" width="100" height="2" fill="{MINT}"/><rect x="10" y="4" width="100" height="14" fill="{MINT}" opacity=".12"/></g>
</g>"""
    rows = ""
    for i in range(10):
        w1, w2 = 30 + (i * 23) % 40, 20 + (i * 17) % 34
        rows += (f'<g transform="translate(0 {i*24})"><rect x="0" y="0" width="{w1}" height="8" rx="4" fill="{CYAN}" opacity=".85"/>'
                 f'<rect x="{w1+8}" y="0" width="{w2}" height="8" rx="4" fill="{VIOLET}" opacity=".6"/>'
                 f'<rect x="{w1+w2+16}" y="0" width="16" height="8" rx="4" fill="{MUTED}" opacity=".4"/></g>')
    v_rex = f"""
<g transform="translate(330 30)">
  <clipPath id="rc"><rect width="120" height="110" rx="12"/></clipPath>
  <rect width="120" height="110" rx="12" fill="#0b1220" stroke="{LINE}"/>
  <g clip-path="url(#rc)"><g class="up" transform="translate(12 14)">{rows}</g></g>
  <text class="mono" x="60" y="-8" font-size="12" fill="{MUTED}" text-anchor="middle">{{ json }}</text>
</g>"""
    bars = "".join(f'<rect x="{62 + i*9}" y="22" width="6" height="40" rx="2" fill="{AMBER}" style="animation-duration:{.6+(i*.29)%.5:.2f}s;animation-delay:-{i*.2:.1f}s"/>' for i in range(5))
    v_panel = f"""
<g transform="translate(320 34)">
  <rect width="134" height="86" rx="10" fill="#0a0f1a" stroke="#2a3650" stroke-width="2"/>
  <rect x="8" y="8" width="118" height="70" rx="6" fill="#04060b"/>
  <circle cx="34" cy="38" r="17" fill="none" stroke="{LINE}" stroke-width="5"/>
  <circle cx="34" cy="38" r="17" fill="none" stroke="{AMBER}" stroke-width="5" stroke-dasharray="106.8" stroke-linecap="round" transform="rotate(-90 34 38)">
    <animate attributeName="stroke-dashoffset" values="60;40;70;60" dur="5s" repeatCount="indefinite"/></circle>
  <text class="mono" x="34" y="42" font-size="11" fill="{TEXT}" text-anchor="middle">47°</text>
  <g class="eq">{bars}</g>
  <rect x="16" y="66" width="102" height="3" rx="1.5" fill="{LINE}"/><rect x="16" y="66" width="60" height="3" rx="1.5" fill="{AMBER}"><animate attributeName="width" values="4;102" dur="10s" repeatCount="indefinite"/></rect>
  <path d="M55 88h24l6 16h-36z" fill="#0a0f1a" stroke="#2a3650" stroke-width="2"/>
</g>"""
    cells = ""
    for r in range(3):
        for c in range(3):
            d = ((r * 3 + c) * 0.37) % 4.8
            cells += f'<rect class="cell" x="{c*36}" y="{r*36}" width="30" height="30" rx="7" fill="{VIOLET}" style="animation-delay:{d:.2f}s"/>'
    v_hatt = f'<g transform="translate(343 31)">{cells}</g>'

    card("skintoscan", "Skin to Scan", "AI skin-lesion screening", MINT, v_skin, "Skin to Scan: AI skin-lesion screening")
    card("tinyrex", "TinyRex", "pay-per-result data tools", CYAN, v_rex, "TinyRex: pay-per-result data tools on Apify")
    card("panelos", "PanelOS", "PC case screen, done right", AMBER, v_panel, "PanelOS: Windows app for small PC case screens")
    card("hatt", "HATT", "digital product studio", VIOLET, v_hatt, "HATT: digital product studio")

# ---------------------------------------------------------------- footer
def footer():
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 90" width="1200" height="90" role="img" aria-label="Thanks for stopping by.">
<style>{BASE_STYLE}</style>
<defs><linearGradient id="f" gradientUnits="userSpaceOnUse" x1="0" x2="600" spreadMethod="reflect">
<stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{AMBER}"/>
<animate attributeName="x1" values="0;600;0" dur="8s" repeatCount="indefinite"/><animate attributeName="x2" values="600;1200;600" dur="8s" repeatCount="indefinite"/></linearGradient></defs>
<rect x="100" y="20" width="1000" height="3" rx="1.5" fill="url(#f)"/>
<text class="mono" x="600" y="66" font-size="18" fill="{MUTED}" text-anchor="middle">build <tspan fill="{CYAN}">→</tspan> ship <tspan fill="{VIOLET}">→</tspan> learn <tspan fill="{AMBER}">→</tspan> repeat</text>
</svg>"""
    save("footer.svg", svg)

if __name__ == "__main__":
    header(); terminal(); cards(); footer()
