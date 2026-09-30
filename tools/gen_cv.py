"""YOLO-style detection loop: grid scan → candidate boxes → NMS keeps the best → labelled result.
A synthetic street scene (drawn, no photos) on the left; the step list + IoU diagram on the right."""
W, H = 1200, 450
T = 9  # seconds per loop
CYAN, VIOLET, PINK, WHITE, AMBER = '#24c6dc', '#8b6cff', '#ff5ea8', '#e8fbff', '#ffc857'
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI',Inter,Helvetica,Arial,sans-serif"
FX, FY, FW, FH = 40, 90, 700, 330   # camera frame

out = []; a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs>')
a('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#07061a"/><stop offset=".6" stop-color="#120f3a"/><stop offset="1" stop-color="#062430"/></linearGradient>')
a('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1650"/><stop offset="1" stop-color="#3a2064"/></linearGradient>')
a('<linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#15142e"/><stop offset="1" stop-color="#0b0a1c"/></linearGradient>')
a(f'<linearGradient id="scan" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".35"/></linearGradient>')
a('<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
a(f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
a(f'<clipPath id="frame"><rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" rx="10"/></clipPath>')
a('</defs>')

def kf(name, stops):
    return f'@keyframes {name}{{' + ''.join(f'{p}{{{v}}}' for p, v in stops) + '}'

css = [f'text{{font-family:{SANS}}}.mono{{font-family:{MONO}}}',
       f'.scanbar{{animation:sb {T}s linear infinite}}' + kf('sb', [('0%', 'transform:translateX(-120px);opacity:1'), ('16%', f'transform:translateX({FW}px);opacity:1'), ('17%,100%', f'transform:translateX({FW}px);opacity:0')]),
       f'.grid{{animation:gd {T}s linear infinite}}' + kf('gd', [('0%', 'opacity:0'), ('4%,16%', 'opacity:1'), ('24%,100%', 'opacity:0')]),
       f'.cand{{opacity:0;animation:cd {T}s linear infinite}}' + kf('cd', [('0%,17%', 'opacity:0'), ('22%,46%', 'opacity:1'), ('54%,100%', 'opacity:0')]),
       f'.bestd{{opacity:0;animation:bd {T}s linear infinite}}' + kf('bd', [('0%,17%', 'opacity:0'), ('22%,50%', 'opacity:1'), ('53%,100%', 'opacity:0')]),
       f'.best{{opacity:0;animation:bs {T}s cubic-bezier(.2,.9,.3,1) infinite;transform-box:fill-box;transform-origin:center}}' + kf('bs', [('0%,50%', 'opacity:0;transform:scale(1.08)'), ('56%,94%', 'opacity:1;transform:scale(1)'), ('100%', 'opacity:0')]),
       f'.cnt1{{animation:c1 {T}s steps(1) infinite}}' + kf('c1', [('0%', 'opacity:0'), ('22%', 'opacity:1'), ('52%,100%', 'opacity:0')]),
       f'.cnt2{{opacity:0;animation:c2 {T}s steps(1) infinite}}' + kf('c2', [('0%', 'opacity:0'), ('52%', 'opacity:1'), ('97%,100%', 'opacity:0')]),
       '.blink{animation:bk 1s steps(2) infinite}@keyframes bk{50%{opacity:0}}']
# the four steps light up in turn
windows = [(0, 17), (17, 48), (48, 56), (56, 96)]
for i, (s, e) in enumerate(windows):
    css.append(f'.st{i}{{animation:st{i} {T}s linear infinite}}' +
               kf(f'st{i}', [('0%', 'opacity:.35'), (f'{max(s-.1,0)}%', 'opacity:.35'), (f'{s+.1 if s else 0}%', 'opacity:1'), (f'{e}%', 'opacity:1'), (f'{e+.2}%,100%', 'opacity:.35')]))
    css.append(f'.sb{i}{{transform-box:fill-box;transform-origin:left;animation:sbar{i} {T}s linear infinite}}' +
               kf(f'sbar{i}', [('0%', 'transform:scaleX(0)'), (f'{s}%', 'transform:scaleX(0)'), (f'{e}%', 'transform:scaleX(1)'), (f'{e+.2}%,100%', 'transform:scaleX(0)')]))
a('<style>' + ''.join(css) + '</style>')

g = []; b = g.append
b('<g clip-path="url(#clip)">')
b(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
b(f'<text class="mono" x="40" y="46" font-size="12" fill="{CYAN}" letter-spacing="4">● COMPUTER VISION · OBJECT DETECTION</text>')
b(f'<text x="40" y="76" font-size="24" font-weight="800" fill="#fff">Detect → suppress duplicates → keep the best box</text>')

# ── camera frame / scene ────────────────────────────────────────────
b(f'<g clip-path="url(#frame)">')
b(f'<rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" fill="url(#sky)"/>')
HZ = FY + 190
# skyline with windows
import random; random.seed(3)
x = FX - 10
while x < FX + FW:
    w = random.randint(40, 90); h = random.randint(60, 160)
    b(f'<rect x="{x}" y="{HZ-h}" width="{w}" height="{h}" fill="#221c56" stroke="#3b3190" stroke-width="1"/>')
    for wy in range(HZ - h + 10, HZ - 8, 16):
        for wx in range(x + 7, x + w - 8, 13):
            if random.random() < .3:
                b(f'<rect x="{wx}" y="{wy}" width="5" height="7" fill="{AMBER}" opacity="{random.uniform(.25,.8):.2f}"/>')
    x += w + random.randint(2, 10)
# road in perspective
VX = FX + FW / 2
b(f'<polygon points="{FX},{FY+FH} {FX+FW},{FY+FH} {FX+FW},{HZ} {FX},{HZ}" fill="url(#road)"/>')
b(f'<polygon points="{VX-40},{HZ} {VX+40},{HZ} {FX+FW+160},{FY+FH} {FX-160},{FY+FH}" fill="#1c1a3c"/>')
for k in range(6):
    t0, t1 = k / 6, (k + .45) / 6
    y0, y1 = HZ + (FY + FH - HZ) * t0 ** 1.6, HZ + (FY + FH - HZ) * t1 ** 1.6
    b(f'<polygon points="{VX-1-3*t0},{y0:.0f} {VX+1+3*t0},{y0:.0f} {VX+1+6*t1},{y1:.0f} {VX-1-6*t1},{y1:.0f}" fill="{AMBER}" opacity=".6"/>')
b(f'<rect x="{FX}" y="{HZ}" width="{FW}" height="3" fill="{PINK}" opacity=".35"/>')
# car (left)
cx, cy = FX + 70, FY + 240
b(f'<g><path d="M{cx} {cy+48} q0 -22 20 -26 l30 -26 q8 -6 22 -6 h60 q12 0 20 8 l24 24 q34 2 40 20 v12 z" fill="#2ec4ff" fill-opacity=".85" stroke="#9feaff"/>'
  f'<path d="M{cx+56} {cy+18} l20 -18 h52 l20 18 z" fill="#0b1a3a" stroke="#9feaff" stroke-opacity=".6"/>'
  f'<circle cx="{cx+52}" cy="{cy+50}" r="15" fill="#0a0a18" stroke="#9feaff"/><circle cx="{cx+170}" cy="{cy+50}" r="15" fill="#0a0a18" stroke="#9feaff"/>'
  f'<rect x="{cx+206}" y="{cy+24}" width="10" height="6" fill="{AMBER}" filter="url(#glow)"/></g>')
# person (centre)
px, py = FX + 390, FY + 150
b(f'<g fill="#ff8fc6"><circle cx="{px}" cy="{py+14}" r="13"/><rect x="{px-16}" y="{py+31}" width="32" height="58" rx="12"/>'
  f'<rect x="{px-14}" y="{py+84}" width="11" height="60" rx="5"/><rect x="{px+3}" y="{py+84}" width="11" height="60" rx="5"/>'
  f'<rect x="{px-28}" y="{py+36}" width="10" height="46" rx="5" transform="rotate(12 {px-23} {py+36})"/><rect x="{px+18}" y="{py+36}" width="10" height="46" rx="5" transform="rotate(-14 {px+23} {py+36})"/></g>')
# traffic light (right)
tx, ty = FX + 548, FY + 40
b(f'<rect x="{tx+14}" y="{ty+100}" width="8" height="150" fill="#3a3470"/>'
  f'<rect x="{tx}" y="{ty}" width="36" height="104" rx="8" fill="#141233" stroke="#6b61d8"/>'
  f'<circle cx="{tx+18}" cy="{ty+20}" r="10" fill="#ff4d6d" opacity=".25"/><circle cx="{tx+18}" cy="{ty+52}" r="10" fill="{AMBER}" opacity=".25"/>'
  f'<circle cx="{tx+18}" cy="{ty+84}" r="10" fill="#3dff9e" filter="url(#glow)"/>')

# YOLO grid + scan bar
b('<g class="grid">')
for i in range(1, 10):
    b(f'<line x1="{FX+i*FW/10:.0f}" y1="{FY}" x2="{FX+i*FW/10:.0f}" y2="{FY+FH}" stroke="{CYAN}" stroke-opacity=".35"/>')
for j in range(1, 5):
    b(f'<line x1="{FX}" y1="{FY+j*FH/5:.0f}" x2="{FX+FW}" y2="{FY+j*FH/5:.0f}" stroke="{CYAN}" stroke-opacity=".35"/>')
b('</g>')
b(f'<rect class="scanbar" x="{FX}" y="{FY}" width="120" height="{FH}" fill="url(#scan)"/>')

# detections: (x, y, w, h, label, score, colour)
OBJ = [(cx - 6, cy - 22, 238, 90, 'car', .93, CYAN),
       (px - 34, py - 6, 68, 158, 'person', .91, PINK),
       (tx - 8, ty - 8, 52, 122, 'traffic light', .88, AMBER)]
JIT = [(10, -8, 14, 6, .64), (-12, 7, -8, 14, .52), (6, 5, -16, -10, .71)]
for (x, y, w, h, lab, sc, col) in OBJ:
    for k, (jx, jy, jw, jh, s2) in enumerate(JIT):
        b(f'<g class="cand" style="animation-delay:{k*.08:.2f}s"><rect x="{x+jx}" y="{y+jy}" width="{w+jw}" height="{h+jh}" fill="none" stroke="{col}" stroke-opacity=".6" stroke-dasharray="5 4"/>'
          f'<text class="mono" x="{x+jx+4+k*30}" y="{y+jy+h+jh-5}" font-size="10" fill="{col}" opacity=".85">{s2:.2f}</text></g>')
    b(f'<rect class="bestd" x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{col}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    tw = len(f'{lab} {sc:.2f}') * 7.4 + 12
    b(f'<g class="best"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" fill-opacity=".08" stroke="{col}" stroke-width="2.5" filter="url(#glow)"/>'
      f'<rect x="{x-1.2}" y="{y-20}" width="{tw:.0f}" height="20" fill="{col}"/>'
      f'<text class="mono" x="{x+6}" y="{y-6}" font-size="12" font-weight="700" fill="#07061a">{lab} {sc:.2f}</text></g>')
b('</g>')
b(f'<rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" rx="10" fill="none" stroke="{CYAN}" stroke-opacity=".5"/>')
b(f'<circle class="blink" cx="{FX+18}" cy="{FY+18}" r="5" fill="#ff4d6d"/><text class="mono" x="{FX+30}" y="{FY+22}" font-size="11" fill="#fff" letter-spacing="2">REC · 640×640</text>')

# ── right panel ─────────────────────────────────────────────────────
RX = 780
b(f'<text class="mono" x="{RX}" y="{FY+14}" font-size="12" fill="#9fb4d9" letter-spacing="3">PIPELINE</text>')
STEPS = [('01', 'Grid scan', 'image split into cells'), ('02', 'Candidates', 'boxes + confidence'),
         ('03', 'NMS', 'drop overlaps, IoU > 0.5'), ('04', 'Result', 'one box per object')]
for i, (n, h1, h2) in enumerate(STEPS):
    y = FY + 36 + i * 50
    b(f'<g class="st{i}"><text class="mono" x="{RX}" y="{y+14}" font-size="12" fill="{CYAN}">{n}</text>'
      f'<text x="{RX+34}" y="{y+14}" font-size="16" font-weight="700" fill="#fff">{h1}</text>'
      f'<text class="mono" x="{RX+34}" y="{y+32}" font-size="11" fill="#9fb4d9">{h2}</text></g>'
      f'<rect x="{RX}" y="{y+40}" width="360" height="1" fill="#ffffff" opacity=".1"/><rect class="sb{i}" x="{RX}" y="{y+40}" width="360" height="2" fill="{CYAN}"/>')
# box counter
y = FY + 250
b(f'<text class="mono" x="{RX}" y="{y}" font-size="11" fill="#9fb4d9" letter-spacing="2">BOXES</text>')
b(f'<text class="cnt1" x="{RX}" y="{y+34}" font-size="30" font-weight="800" fill="#fff">12 <tspan font-size="14" fill="#9fb4d9" font-weight="400">candidates</tspan></text>')
b(f'<text class="cnt2" x="{RX}" y="{y+34}" font-size="30" font-weight="800" fill="{CYAN}">3 <tspan font-size="14" fill="#9fb4d9" font-weight="400">kept after NMS</tspan></text>')
# IoU diagram
ix, iy = RX + 250, FY + 238
b(f'<rect x="{ix}" y="{iy}" width="54" height="54" fill="{CYAN}" fill-opacity=".15" stroke="{CYAN}"/>'
  f'<rect x="{ix+26}" y="{iy+22}" width="54" height="54" fill="{PINK}" fill-opacity=".15" stroke="{PINK}"/>'
  f'<rect x="{ix+26}" y="{iy+22}" width="28" height="32" fill="#fff" fill-opacity=".55"/>'
  f'<text class="mono" x="{ix+40}" y="{iy+96}" font-size="11" fill="#fff" text-anchor="middle">IoU = A∩B / A∪B</text>')
b(f'<text class="mono" x="{RX}" y="{FY+FH}" font-size="11" fill="#9fb4d9">YOLO11n · OpenCV</text>')
for (x, y, dx, dy) in [(18, 18, 1, 1), (W - 18, 18, -1, 1), (18, H - 18, 1, -1), (W - 18, H - 18, -1, -1)]:
    b(f'<path d="M{x} {y + 20*dy} V{y} H{x + 20*dx}" fill="none" stroke="{CYAN}" stroke-width="2" stroke-opacity=".8"/>')
b('</g>')
b(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="{CYAN}" stroke-opacity=".25"/>')
a(''.join(g)); a('</svg>')
open('assets/cv-detection.svg', 'w').write('\n'.join(out))
print('cv-detection.svg', sum(len(x) for x in out) // 1024, 'KB')
