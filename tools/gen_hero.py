"""Hero banner: rotating 3D embedding-space sphere + perspective grid + cycling typed line.
Pure SVG + CSS keyframes (GitHub renders these inside <img>). No JS, no web fonts."""
import math, random
random.seed(7)

W, H = 1200, 420
CX, CY, R = 905, 190, 150          # sphere centre / radius
TILT = math.radians(20)            # camera looks slightly down on the sphere
DUR = 22                           # seconds per full rotation
STEPS = 36

CYAN, VIOLET, PINK = '#24c6dc', '#8b6cff', '#ff5ea8'
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI',Inter,Helvetica,Arial,sans-serif"

def proj(x, y, z):
    """rotate about X by TILT, then orthographic-with-slight-perspective."""
    y2 = y * math.cos(TILT) - z * math.sin(TILT)
    z2 = y * math.sin(TILT) + z * math.cos(TILT)
    p = 1 + z2 / (R * 5)           # mild perspective
    return CX + x * p, CY - y2 * p, z2

out = []
a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs>')
a('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#07061a"/><stop offset=".55" stop-color="#141040"/><stop offset="1" stop-color="#05222e"/></linearGradient>')
a(f'<linearGradient id="tx" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#bfefff"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>')
a(f'<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".55"/></linearGradient>')
a(f'<radialGradient id="core" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{CYAN}" stop-opacity=".55"/><stop offset=".5" stop-color="{VIOLET}" stop-opacity=".18"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>')
a('<radialGradient id="sun" cx="50%" cy="100%" r="60%"><stop offset="0" stop-color="#ff5ea8" stop-opacity=".35"/><stop offset="1" stop-color="#ff5ea8" stop-opacity="0"/></radialGradient>')
a('<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
a('<filter id="bigglow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
a(f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
a('</defs>')

# ── CSS ─────────────────────────────────────────────────────────────
css = []
c = css.append
c(f'text{{font-family:{SANS}}} .mono{{font-family:{MONO}}}')
c('.hl{animation:hl 5s cubic-bezier(.55,0,1,.45) infinite}')
c('@keyframes hl{from{transform:translateY(0);opacity:0}15%{opacity:.8}to{transform:translateY(180px);opacity:.9}}')
c('.scan{animation:scan 6s linear infinite}@keyframes scan{from{transform:translateX(-240px)}to{transform:translateX(1440px)}}')
c('.blink{animation:blink 1s steps(2) infinite}@keyframes blink{50%{opacity:0}}')
c('.ring{transform-origin:905px 190px;animation:ring 16s linear infinite}@keyframes ring{to{transform:rotate(360deg)}}')
c('.ringr{transform-origin:905px 190px;animation:ring 24s linear infinite reverse}')
c('.pulse{transform-origin:905px 190px;animation:pulse 4s ease-in-out infinite}@keyframes pulse{50%{transform:scale(1.08);opacity:.7}}')
c('.rise{animation:rise 1.2s cubic-bezier(.16,1,.3,1) both}@keyframes rise{from{opacity:0;transform:translateY(24px)}}')
c('.d1{animation-delay:.15s}.d2{animation-delay:.3s}.d3{animation-delay:.45s}')
# typed lines: 4 phrases, each owns 1/4 of a 16s cycle; width reveal via clip rect scaleX
PHRASES = ['Building production-grade RAG pipelines',
           'Agentic AI · LangChain + LangGraph + MCP',
           'Computer Vision · YOLO · transfer learning',
           'Shipping models: notebook → FastAPI → Docker']
T = 16
for i in range(4):
    s = i * 25
    c(f'.ph{i}{{opacity:0;animation:ph{i} {T}s linear infinite}}')
    c(f'@keyframes ph{i}{{{s}%{{opacity:1}}{s+24.9}%{{opacity:1}}{s+25}%{{opacity:0}}}}' if i else
      f'@keyframes ph{i}{{0%{{opacity:1}}24.9%{{opacity:1}}25%,100%{{opacity:0}}}}')
    # typing reveal (steps) then hold then erase
    c(f'.cl{i}{{transform:scaleX(0);animation:cl{i} {T}s steps(1) infinite}}')
    frames = []
    n = len(PHRASES[i])
    # 0 → 12% of the slot: type; 12 → 21: hold; 21 → 24: erase
    for k in range(n + 1):
        pct = s + 12 * k / n
        frames.append(f'{pct:.3f}%{{transform:scaleX({k/n:.4f})}}')
    for k in range(9):
        pct = s + 21 + 3 * k / 8
        frames.append(f'{pct:.3f}%{{transform:scaleX({1 - k/8:.4f})}}')
    c(f'@keyframes cl{i}{{' + ''.join(frames) + '}')

# sphere points: every latitude ring gets one keyframe track; points on the ring differ only by delay
rings = []
lats = [-60, -38, -16, 6, 28, 50, 70]
for li, lat in enumerate(lats):
    phi = math.radians(lat)
    kf = []
    for s in range(STEPS + 1):
        th = 2 * math.pi * s / STEPS
        x = R * math.cos(phi) * math.sin(th)
        y = R * math.sin(phi)
        z = R * math.cos(phi) * math.cos(th)
        px, py, pz = proj(x, y, z)
        depth = (pz / R + 1) / 2            # 0 back … 1 front
        sc = .55 + depth * .9
        op = .18 + depth * .82
        kf.append(f'{100*s/STEPS:.2f}%{{transform:translate({px-0:.1f}px,{py:.1f}px) scale({sc:.2f});opacity:{op:.2f}}}')
    c(f'.p{li}{{animation:p{li} {DUR}s linear infinite}}@keyframes p{li}{{' + ''.join(kf) + '}')
    rings.append(phi)
a('<style>' + ''.join(css) + '</style>')

g = []
b = g.append
b(f'<g clip-path="url(#clip)">')
b(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
# faint star dust
for _ in range(90):
    x, y = random.uniform(0, W), random.uniform(0, 250)
    b(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{random.uniform(.4,1.3):.1f}" fill="#cfe9ff" opacity="{random.uniform(.15,.6):.2f}"/>')
# horizon glow
b(f'<ellipse cx="{W/2}" cy="262" rx="720" ry="120" fill="url(#sun)"/>')

# ── perspective floor ───────────────────────────────────────────────
HZ, VX = 262, W / 2
b('<g opacity=".75">')
b(f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#floor)" opacity=".25"/>')
for k in range(-26, 27):
    x2 = VX + k * 95
    b(f'<line x1="{VX + k*6:.1f}" y1="{HZ}" x2="{x2:.1f}" y2="{H}" stroke="{CYAN}" stroke-opacity="{.5 - abs(k)*.012:.3f}" stroke-width="1"/>')
for k in range(8):   # horizontal lines flowing toward the viewer
    b(f'<line class="hl" style="animation-delay:-{k*5/8:.3f}s" x1="0" y1="{HZ}" x2="{W}" y2="{HZ}" stroke="{CYAN}" stroke-width="1.2" stroke-opacity=".7"/>')
b(f'<line x1="0" y1="{HZ}" x2="{W}" y2="{HZ}" stroke="{PINK}" stroke-width="1.5" stroke-opacity=".7" filter="url(#glow)"/>')
b('</g>')

# ── 3D embedding sphere ─────────────────────────────────────────────
b(f'<circle class="pulse" cx="{CX}" cy="{CY}" r="{R*1.25}" fill="url(#core)"/>')
# static latitude ellipses (invariant under rotation about the vertical axis)
for phi in rings:
    y = R * math.sin(phi); rr = R * math.cos(phi)
    _, cyy, _ = proj(0, y, 0)
    b(f'<ellipse cx="{CX}" cy="{cyy:.1f}" rx="{rr:.1f}" ry="{rr*math.sin(TILT):.1f}" fill="none" stroke="{CYAN}" stroke-opacity=".16"/>')
b(f'<ellipse cx="{CX}" cy="{CY}" rx="{R}" ry="{R}" fill="none" stroke="{VIOLET}" stroke-opacity=".35"/>')
# orbit rings with satellites (tilted, rotating)
b(f'<g class="ring"><ellipse cx="{CX}" cy="{CY}" rx="{R*1.42}" ry="{R*.34}" fill="none" stroke="{CYAN}" stroke-opacity=".45" stroke-dasharray="2 7" transform="rotate(-18 {CX} {CY})"/>'
  f'<circle cx="{CX + R*1.42*math.cos(math.radians(-18)):.1f}" cy="{CY + R*1.42*math.sin(math.radians(-18)):.1f}" r="4" fill="{CYAN}" filter="url(#glow)"/></g>')
b(f'<g class="ringr"><ellipse cx="{CX}" cy="{CY}" rx="{R*1.22}" ry="{R*.5}" fill="none" stroke="{PINK}" stroke-opacity=".35" stroke-dasharray="1 5" transform="rotate(28 {CX} {CY})"/>'
  f'<circle cx="{CX - R*1.22*math.cos(math.radians(28)):.1f}" cy="{CY - R*1.22*math.sin(math.radians(28)):.1f}" r="3.2" fill="{PINK}" filter="url(#glow)"/></g>')
# rotating points — three "clusters" by colour, like an embedding space
cols = [CYAN, VIOLET, PINK, '#e8fbff']
for li, phi in enumerate(rings):
    n = max(6, int(22 * math.cos(phi)))
    for k in range(n):
        delay = -DUR * k / n - random.uniform(0, DUR / n * .6)
        col = cols[(k * 7 + li * 3) // 5 % 4]
        rr = random.choice([2.2, 2.6, 3.2])
        b(f'<circle class="p{li}" style="animation-delay:{delay:.2f}s" r="{rr}" fill="{col}"/>')
# query vector: a bright point + beam to the sphere centre
b(f'<g filter="url(#glow)"><line x1="{CX}" y1="{CY}" x2="{CX-R*1.7:.0f}" y2="{CY-R*.95:.0f}" stroke="#fff" stroke-opacity=".5" stroke-dasharray="3 5"/>'
  f'<circle cx="{CX-R*1.7:.0f}" cy="{CY-R*.95:.0f}" r="5" fill="#fff"/></g>')
b(f'<text class="mono" x="{CX-R*1.7-6:.0f}" y="{CY-R*.95-14:.0f}" font-size="11" fill="#cfefff" text-anchor="middle" letter-spacing="1.5">QUERY ⟶ top-k</text>')
b(f'<text class="mono" x="{CX}" y="{CY+R+44}" font-size="11" fill="{CYAN}" text-anchor="middle" letter-spacing="3" opacity=".8">EMBEDDING SPACE · 768-d → 3-d</text>')

# ── text block ──────────────────────────────────────────────────────
b(f'<g class="rise"><text class="mono" x="64" y="92" font-size="13" fill="{CYAN}" letter-spacing="4">● AI / ML ENGINEER · BENGALURU</text></g>')
b(f'<g class="rise d1" filter="url(#bigglow)"><text x="60" y="170" font-size="72" font-weight="800" fill="url(#tx)" letter-spacing="-1">Tejas Kumar S</text></g>')
b(f'<g class="rise d2"><text x="64" y="208" font-size="19" fill="#d7d3ff" letter-spacing=".5">Generative AI  ·  RAG  ·  Agentic AI  ·  Computer Vision</text></g>')
# terminal line with cycling typed phrases
b(f'<g class="rise d3"><rect x="60" y="226" width="520" height="40" rx="8" fill="#0a0a22" fill-opacity=".72" stroke="{CYAN}" stroke-opacity=".35"/>')
b(f'<text class="mono" x="78" y="252" font-size="15" fill="{PINK}">$</text>')
for i, p in enumerate(PHRASES):
    wpx = len(p) * 9.05
    b(f'<clipPath id="cp{i}"><rect class="cl{i}" x="96" y="230" width="{wpx:.0f}" height="32" style="transform-origin:96px 0"/></clipPath>')
    b(f'<g class="ph{i}"><text class="mono" x="96" y="252" font-size="15" fill="#e6fbff" clip-path="url(#cp{i})">{p}</text></g>')
b(f'<rect class="blink" x="562" y="238" width="8" height="17" fill="{CYAN}"/></g>')

# scan line sweeping across the banner
b(f'<rect class="scan" x="0" y="0" width="180" height="{H}" fill="{CYAN}" opacity=".05"/>')
# HUD corners
for (x, y, dx, dy) in [(18, 18, 1, 1), (W - 18, 18, -1, 1), (18, H - 18, 1, -1), (W - 18, H - 18, -1, -1)]:
    b(f'<path d="M{x} {y + 22*dy} V{y} H{x + 22*dx}" fill="none" stroke="{CYAN}" stroke-width="2" stroke-opacity=".8"/>')
b(f'<text class="mono" x="40" y="{H-30}" font-size="10.5" fill="#9fb4d9" letter-spacing="2">github.com/Tejasprof84</text>')
b('</g>')
b(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="{CYAN}" stroke-opacity=".25"/>')
a(''.join(g))
a('</svg>')
open('assets/hero.svg', 'w').write('\n'.join(out))
print('hero.svg', sum(len(x) for x in out) // 1024, 'KB')
