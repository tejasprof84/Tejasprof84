"""Smaller assets: isometric conv tensor cube, section divider, footer."""
import math
C30 = math.cos(math.radians(30))
CYAN, VIOLET, PINK, WHITE = '#24c6dc', '#8b6cff', '#ff5ea8', '#e8fbff'
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI',Inter,Helvetica,Arial,sans-serif"

# ════════════════════════════════════════════════════════════════════
# 1 · CONV TENSOR CUBE — a 4×4×4 input volume, a 3×3 kernel sliding
#     over the top slice, and the 2×2 feature map it produces.
# ════════════════════════════════════════════════════════════════════
W = H = 400
OX, OY, CELL, GAP = 200, 205, 28, 3
T = 6
def iso(x, y, z):
    return OX + (x - y) * C30, OY + (x + y) * .5 - z
def P(*pts):
    return ' '.join(f'{a:.1f},{b:.1f}' for a, b in (iso(*p) for p in pts))
def voxel(i, j, k, top='#3a2f9a', left='#241c66', right='#150f40', stroke=CYAN, so=.55, cls=''):
    x, y, z, s = i * CELL, j * CELL, k * CELL, CELL - GAP
    c = f' class="{cls}"' if cls else ''
    return (f'<g{c}><polygon points="{P((x,y+s,z),(x+s,y+s,z),(x+s,y+s,z+s),(x,y+s,z+s))}" fill="{left}"/>'
            f'<polygon points="{P((x+s,y,z),(x+s,y+s,z),(x+s,y+s,z+s),(x+s,y,z+s))}" fill="{right}"/>'
            f'<polygon points="{P((x,y,z+s),(x+s,y,z+s),(x+s,y+s,z+s),(x,y+s,z+s))}" fill="{top}" stroke="{stroke}" stroke-opacity="{so}" stroke-width=".8"/></g>')

out = []; a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a0824"/><stop offset="1" stop-color="#061f2b"/></linearGradient>'
  f'<radialGradient id="h"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".45"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>'
  '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
  f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="20"/></clipPath></defs>')
# kernel positions over the 4×4 top slice (stride 1 → 2×2 outputs)
POS = [(0, 0), (1, 0), (0, 1), (1, 1)]
def off(i, j):
    return (i - j) * C30 * CELL, (i + j) * .5 * CELL
kfs = ''.join(f'{q*25}%,{q*25+22}%{{transform:translate({off(*p)[0]:.1f}px,{off(*p)[1]:.1f}px)}}' for q, p in enumerate(POS))
css = [f'text{{font-family:{SANS}}}.mono{{font-family:{MONO}}}',
       f'.kern{{animation:kn {T}s cubic-bezier(.7,0,.3,1) infinite}}@keyframes kn{{{kfs}100%{{transform:translate(0,0)}}}}',
       '.beam{animation:bm 1.5s ease-in-out infinite}@keyframes bm{50%{opacity:.25}}',
       '.float{animation:fl 5s ease-in-out infinite}@keyframes fl{50%{transform:translateY(-7px)}}',
       '.halo{transform-box:fill-box;transform-origin:center;animation:hl 4s ease-in-out infinite}@keyframes hl{50%{transform:scale(1.12);opacity:.6}}']
for q in range(4):
    s = q * 25
    css.append(f'.o{q}{{animation:o{q} {T}s steps(1) infinite}}@keyframes o{q}{{0%{{fill:#1c1650}}{s+6}%{{fill:{CYAN}}}100%{{fill:{CYAN}}}}}')
a('<style>' + ''.join(css) + '</style>')
g = []; b = g.append
b('<g clip-path="url(#clip)">')
b(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
b(f'<ellipse class="halo" cx="{OX}" cy="{OY+60}" rx="170" ry="120" fill="url(#h)"/>')

# voxels, painter's order
for k in range(4):
    for s in range(7):
        for i in range(4):
            j = s - i
            if 0 <= j < 4:
                if k == 3:
                    b(voxel(i, j, k, top='#4a3bb8'))
                else:
                    b(voxel(i, j, k))
# kernel overlay on the top slice (3×3 footprint), sliding
z = 4 * CELL - GAP
x0, y0, s3 = 0, 0, 3 * CELL - GAP
b(f'<g class="kern"><polygon points="{P((x0,y0,z),(x0+s3,y0,z),(x0+s3,y0+s3,z),(x0,y0+s3,z))}" fill="{PINK}" fill-opacity=".35" stroke="{PINK}" stroke-width="2" filter="url(#glow)"/>')
for i in range(3):
    for j in range(3):
        cx, cy = iso(i * CELL + (CELL - GAP) / 2, j * CELL + (CELL - GAP) / 2, z)
        b(f'<text class="mono" x="{cx:.1f}" y="{cy+3.5:.1f}" font-size="9" fill="#fff" text-anchor="middle">{[1,0,-1][i]}</text>')
# beam from kernel centre up to the output map
kcx, kcy = iso(1.5 * CELL, 1.5 * CELL, z)
b(f'<line class="beam" x1="{kcx:.1f}" y1="{kcy:.1f}" x2="{kcx:.1f}" y2="{kcy-85:.1f}" stroke="{PINK}" stroke-width="2" stroke-dasharray="3 4"/></g>')
# output feature map (2×2), floating above
b('<g class="float">')
FZ = z + 85
for q, (i, j) in enumerate(POS):
    x, y = (i + 1) * CELL, (j + 1) * CELL
    s = CELL - GAP
    b(f'<polygon class="o{q}" points="{P((x,y,FZ),(x+s,y,FZ),(x+s,y+s,FZ),(x,y+s,FZ))}" fill="#1c1650" stroke="{CYAN}" stroke-width="1.2" filter="url(#glow)"/>')
lx, ly = iso(3 * CELL + 10, 1 * CELL, FZ)
b(f'<text class="mono" x="{lx+8:.0f}" y="{ly:.0f}" font-size="10.5" fill="{CYAN}">feature map 2×2</text></g>')
b(f'<text class="mono" x="22" y="{H-58}" font-size="11" fill="{CYAN}" letter-spacing="3">● CONV2D · 3×3 · STRIDE 1</text>')
b(f'<text class="mono" x="22" y="{H-40}" font-size="10.5" fill="#9fb4d9">input 4×4×4 · kernel slides → activations</text>')
b(f'<text class="mono" x="22" y="{H-22}" font-size="10.5" fill="#9fb4d9">edges · textures · parts · objects</text>')
b('</g>')
b(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="20" fill="none" stroke="{CYAN}" stroke-opacity=".3"/>')
a(''.join(g)); a('</svg>')
open('assets/tensor-cube.svg', 'w').write('\n'.join(out))

# ════════════════════════════════════════════════════════════════════
# 2 · DIVIDER — a signal pulse travelling along a line of layers
# ════════════════════════════════════════════════════════════════════
W, H = 1200, 28
d = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".2" stop-color="{CYAN}"/><stop offset=".8" stop-color="{VIOLET}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>'
     f'<linearGradient id="p" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".85" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
     '<filter id="glow" x="-10%" y="-200%" width="120%" height="500%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
     '<style>.pl{animation:pl 3.2s cubic-bezier(.6,0,.4,1) infinite}@keyframes pl{from{transform:translateX(-220px)}to{transform:translateX(1260px)}}'
     '.n{animation:n 3.2s linear infinite}@keyframes n{0%,100%{opacity:.35}}</style>',
     f'<rect x="0" y="13.5" width="{W}" height="1" fill="url(#l)" opacity=".7"/>']
for k in range(1, 12):
    x = k * 100
    delay = (x + 220) / 1480 * 3.2
    d.append(f'<g><rect x="{x-3}" y="11" width="6" height="6" transform="rotate(45 {x} 14)" fill="#0d1117" stroke="{CYAN if k<6 else VIOLET}"/>'
             f'<rect x="{x-3}" y="11" width="6" height="6" transform="rotate(45 {x} 14)" fill="{CYAN if k<6 else VIOLET}" opacity="0">'
             f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;.08;.3" dur="3.2s" begin="{delay:.2f}s" repeatCount="indefinite"/></rect></g>')
d.append('<rect class="pl" x="0" y="12.5" width="200" height="3" fill="url(#p)" filter="url(#glow)"/>')
d.append('</svg>')
open('assets/divider.svg', 'w').write('\n'.join(d))

# ════════════════════════════════════════════════════════════════════
# 3 · FOOTER — perspective grid falling away + signature line
# ════════════════════════════════════════════════════════════════════
W, H = 1200, 200
f = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0a24"/><stop offset="1" stop-color="#140f3c"/></linearGradient>'
     f'<radialGradient id="s" cx="50%" cy="100%" r="55%"><stop offset="0" stop-color="{PINK}" stop-opacity=".35"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>'
     f'<clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>',
     f'<style>text{{font-family:{MONO}}}.hl{{animation:hl 4s cubic-bezier(.55,0,1,.45) infinite}}@keyframes hl{{from{{transform:translateY(0);opacity:0}}20%{{opacity:.8}}to{{transform:translateY(-110px);opacity:0}}}}</style>',
     '<g clip-path="url(#c)">', f'<rect width="{W}" height="{H}" fill="url(#bg)"/>', f'<ellipse cx="600" cy="200" rx="620" ry="120" fill="url(#s)"/>']
HZ = 200
for k in range(-24, 25):   # grid rising toward the top (mirror of the hero floor)
    f.append(f'<line x1="{600+k*6}" y1="{HZ}" x2="{600+k*80}" y2="80" stroke="{CYAN}" stroke-opacity="{.35-abs(k)*.012:.3f}"/>')
for k in range(6):
    f.append(f'<line class="hl" style="animation-delay:-{k*4/6:.2f}s" x1="0" y1="{HZ}" x2="{W}" y2="{HZ}" stroke="{CYAN}" stroke-opacity=".6"/>')
f.append('<linearGradient id="fd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0a24"/><stop offset="1" stop-color="#0b0a24" stop-opacity="0"/></linearGradient><rect x="0" y="78" width="1200" height="70" fill="url(#fd)"/>')
f.append(f'<text x="600" y="60" font-size="13" fill="#cfd8ff" text-anchor="middle" letter-spacing="5">RETRIEVE  ·  MEASURE  ·  SHIP</text>')
f.append(f'<text x="600" y="84" font-size="10.5" fill="{CYAN}" text-anchor="middle" letter-spacing="3" opacity=".8">— TEJAS KUMAR S —</text>')
f.append('</g></svg>')
open('assets/footer.svg', 'w').write('\n'.join(f))
print('ok')
