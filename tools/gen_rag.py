"""Isometric 3D RAG pipeline: ingest → chunk → embed → index → generate → answer.
Every solid is projected from real 3D coordinates; packets travel the floor conveyor."""
import math

W, H = 1200, 470
OX, OY = 120, 300          # screen position of world origin
C30, S30 = math.cos(math.radians(30)), .5
CYAN, VIOLET, PINK, WHITE = '#24c6dc', '#8b6cff', '#ff5ea8', '#e8fbff'
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI',Inter,Helvetica,Arial,sans-serif"
STEP = 112                  # world distance between stations (along x, -y)

def iso(x, y, z=0):
    return OX + (x - y) * C30, OY + (x + y) * S30 - z

def pts(*p):
    return ' '.join(f'{a:.1f},{b:.1f}' for a, b in (iso(*q) for q in p))

def shade(hexc, f):
    h = hexc.lstrip('#'); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    if f >= 1: r, g, b = (int(v + (255 - v) * (f - 1)) for v in (r, g, b))
    else: r, g, b = (int(v * f) for v in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'

def box(x, y, z, w, d, h, col, edge=CYAN, op=1, cls=''):
    """axis-aligned box; visible faces: top, +y (left), +x (right)."""
    s = f'<g class="{cls}" opacity="{op}">' if cls or op != 1 else '<g>'
    s += f'<polygon points="{pts((x,y+d,z),(x+w,y+d,z),(x+w,y+d,z+h),(x,y+d,z+h))}" fill="{shade(col,.62)}"/>'
    s += f'<polygon points="{pts((x+w,y,z),(x+w,y+d,z),(x+w,y+d,z+h),(x+w,y,z+h))}" fill="{shade(col,.38)}"/>'
    s += f'<polygon points="{pts((x,y,z+h),(x+w,y,z+h),(x+w,y+d,z+h),(x,y+d,z+h))}" fill="{shade(col,1.25)}"/>'
    # edges
    s += (f'<polyline points="{pts((x,y+d,z+h),(x,y+d,z),(x+w,y+d,z),(x+w,y,z),(x+w,y,z+h),(x,y,z+h),(x,y+d,z+h),(x+w,y+d,z+h),(x+w,y,z+h))}" '
          f'fill="none" stroke="{edge}" stroke-opacity=".75" stroke-width="1"/>')
    s += f'<line x1="{iso(x+w,y+d,z)[0]:.1f}" y1="{iso(x+w,y+d,z)[1]:.1f}" x2="{iso(x+w,y+d,z+h)[0]:.1f}" y2="{iso(x+w,y+d,z+h)[1]:.1f}" stroke="{edge}" stroke-opacity=".75"/>'
    return s + '</g>'

def station(t):
    return t * STEP, -t * STEP

out = []
a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs>')
a('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#07061a"/><stop offset=".6" stop-color="#120f3a"/><stop offset="1" stop-color="#062430"/></linearGradient>')
a(f'<radialGradient id="halo"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".55"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>')
a(f'<radialGradient id="halo2"><stop offset="0" stop-color="{CYAN}" stop-opacity=".45"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>')
a('<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
a(f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
a('</defs>')

dx, dy = C30 * 10, S30 * 10     # screen offset of +10 world units along x
css = [f'text{{font-family:{SANS}}}.mono{{font-family:{MONO}}}',
       '.flow{stroke-dasharray:6 10;animation:flow 1.2s linear infinite}@keyframes flow{to{stroke-dashoffset:-32}}',
       '.flowq{stroke-dasharray:3 7;animation:flow 1s linear infinite}',
       '.halo{transform-box:fill-box;transform-origin:center;animation:halo 3s ease-in-out infinite}@keyframes halo{50%{transform:scale(1.18);opacity:.55}}',
       '.blink{animation:bk 1.4s ease-in-out infinite}@keyframes bk{50%{opacity:.15}}',
       '.float{animation:fl 4s ease-in-out infinite}@keyframes fl{50%{transform:translateY(-8px)}}',
       '.type{transform:scaleX(0);transform-box:fill-box;transform-origin:left;animation:ty 6s cubic-bezier(.3,.7,.3,1) infinite}',
       '@keyframes ty{0%,10%{transform:scaleX(0)}40%,88%{transform:scaleX(1)}100%{transform:scaleX(1);opacity:0}}',
       '.chk{opacity:0;animation:ck 6s infinite}@keyframes ck{0%,42%{opacity:0}48%,90%{opacity:1}100%{opacity:0}}',
       '.lbl{animation:lb .9s both}@keyframes lb{from{opacity:0;transform:translateY(10px)}}']
for k in range(4):   # chunk slices drift apart then snap back
    css.append(f'.sl{k}{{animation:sl{k} 4s cubic-bezier(.6,0,.2,1) infinite}}'
               f'@keyframes sl{k}{{0%,15%,85%,100%{{transform:translate(0,0)}}45%,60%{{transform:translate({(k-1.5)*dx*.9:.1f}px,{(k-1.5)*dy*.9:.1f}px)}}}}')
for k in range(3):   # vector-db discs lift in sequence
    css.append(f'.dk{k}{{animation:dk 3s ease-in-out infinite;animation-delay:{k*.25}s}}')
css.append('@keyframes dk{50%{transform:translateY(-6px)}}')
a('<style>' + ''.join(css) + '</style>')

g = []
b = g.append
b('<g clip-path="url(#clip)">')
b(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

# isometric floor grid
for k in range(-8, 9):
    p1 = iso(-60 + k * 56, -60, 0); p2 = iso(-60 + k * 56, 60 - 6 * STEP - 120, 0)
b('<g stroke="#8fe9ff" stroke-opacity=".07">')
for k in range(-4, 30):
    u = -120 + k * 40
    b(f'<line x1="{iso(u,120)[0]:.0f}" y1="{iso(u,120)[1]:.0f}" x2="{iso(u,-720)[0]:.0f}" y2="{iso(u,-720)[1]:.0f}"/>')
for k in range(-4, 26):
    v = 120 - k * 40
    b(f'<line x1="{iso(-160,v)[0]:.0f}" y1="{iso(-160,v)[1]:.0f}" x2="{iso(760,v)[0]:.0f}" y2="{iso(760,v)[1]:.0f}"/>')
b('</g>')

# conveyor: a raised isometric strip joining all stations
x0, y0 = station(0); x5, y5 = station(5)
bw = 14
b(f'<polygon points="{pts((x0, y0 - bw, 0), (x5, y5 - bw, 0), (x5 + bw, y5, 0), (x0 + bw, y0, 0))}" fill="#0c0b26" stroke="{CYAN}" stroke-opacity=".25"/>')
path = f'M{iso(x0 + 4, y0 - 4)[0]:.1f},{iso(x0 + 4, y0 - 4)[1]:.1f} L{iso(x5 + 4, y5 - 4)[0]:.1f},{iso(x5 + 4, y5 - 4)[1]:.1f}'
b(f'<path class="flow" d="{path}" stroke="{CYAN}" stroke-width="2" fill="none" stroke-opacity=".8"/>')

# ── stations ────────────────────────────────────────────────────────
S = 66   # footprint
def base(t):
    x, y = station(t); return x - S / 2, y - S / 2

# 01 documents: three stacked pages, the top one floats
x, y = base(0)
for k in range(3):
    cls = 'float' if k == 2 else ''
    b(box(x + k * 3, y - k * 3, 6 + k * 16, S - 10, S - 4, 6, '#1d2a55', cls=cls))
xp, yp = x + 6, y - 6
for k in range(4):   # text lines on the top page
    p1 = iso(xp + 10, yp + 12 + k * 11, 44); p2 = iso(xp + 44 - (k % 2) * 12, yp + 12 + k * 11, 44)
    b(f'<g class="float"><line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="{WHITE}" stroke-opacity=".7" stroke-width="2"/></g>')

# 02 chunker: box sliced into four slabs that drift apart
x, y = base(1)
for k in range(4):
    b(box(x + k * (S / 4), y, 0, S / 4 - 2, S, 46, '#2a2170', cls=f'sl{k}'))

# 03 embedding model: cube with neuron dots on the top face
x, y = base(2)
b(f'<ellipse class="halo" cx="{iso(x+S/2,y+S/2,40)[0]:.0f}" cy="{iso(x+S/2,y+S/2,40)[1]:.0f}" rx="70" ry="44" fill="url(#halo2)"/>')
b(box(x, y, 0, S, S, 58, '#123a5a'))
for i in range(3):
    for j in range(3):
        px, py = iso(x + 14 + i * 19, y + 14 + j * 19, 58)
        b(f'<circle class="blink" style="animation-delay:{(i*3+j)*.13:.2f}s" cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{CYAN}" filter="url(#glow)"/>')

# 04 vector DB: three cylinder discs
x, y = station(3)
rx, ry = 1.2247 * 36, .7071 * 36
for k in range(3):
    z = k * 22
    cx, cy = iso(x, y, z)
    top = cy - 16
    b(f'<g class="dk{k}">'
      f'<path d="M{cx-rx:.1f},{cy:.1f} L{cx-rx:.1f},{top:.1f} A{rx:.1f},{ry:.1f} 0 0 0 {cx+rx:.1f},{top:.1f} L{cx+rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 0 1 {cx-rx:.1f},{cy:.1f}Z" fill="#1a1550" stroke="{VIOLET}" stroke-opacity=".8"/>'
      f'<ellipse cx="{cx:.1f}" cy="{top:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#3a2f9a" stroke="{CYAN}" stroke-opacity=".8"/>'
      f'<ellipse class="blink" style="animation-delay:{k*.3}s" cx="{cx:.1f}" cy="{top:.1f}" rx="{rx*.55:.1f}" ry="{ry*.55:.1f}" fill="none" stroke="{CYAN}" stroke-dasharray="3 4"/>'
      '</g>')

# 05 LLM: tall glowing block
x, y = base(4)
cxl, cyl = iso(x + S / 2, y + S / 2, 60)
b(f'<ellipse class="halo" cx="{cxl:.0f}" cy="{cyl:.0f}" rx="110" ry="80" fill="url(#halo)"/>')
b(box(x - 6, y - 6, 0, S + 12, S + 12, 92, '#3b2a9e', edge=PINK))
tx, ty = iso(x + S / 2, y + S / 2, 92)
b(f'<text class="mono" x="{tx:.0f}" y="{ty+5:.0f}" font-size="15" font-weight="700" fill="#fff" text-anchor="middle" transform="matrix(1,0,0,1,0,0)" letter-spacing="2">LLM</text>')
for k in range(5):   # "attention" bars on the right face
    p1 = iso(x + S + 6, y - 6 + 12 + k * 14, 18); p2 = iso(x + S + 6, y - 6 + 12 + k * 14, 18 + 20 + (k * 17) % 45)
    b(f'<line class="blink" style="animation-delay:{k*.2:.1f}s" x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="{PINK}" stroke-width="4" stroke-linecap="round"/>')

# 06 answer card: floating panel with typed lines + citation tick
x, y = station(5)
b('<g class="float">')
b(f'<polygon points="{pts((x-30,y+10,20),(x+30,y-50,20),(x+30,y-50,110),(x-30,y+10,110))}" fill="#0e0d2c" fill-opacity=".92" stroke="{CYAN}" stroke-opacity=".9"/>')
for k, frac in enumerate([.9, .75, .85, .5]):
    z = 92 - k * 16
    p1 = iso(x - 22, y + 2, z); p2 = iso(x - 22 + 52 * frac, y + 2 - 52 * frac, z)
    b(f'<line class="type" style="animation-delay:{k*.35:.2f}s" x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="{WHITE}" stroke-width="3" stroke-linecap="round" stroke-opacity=".85"/>')
cx, cy = iso(x + 18, y - 38, 30)
b(f'<g class="chk"><circle cx="{cx:.0f}" cy="{cy:.0f}" r="11" fill="{CYAN}" filter="url(#glow)"/><path d="M{cx-5:.0f} {cy:.0f} l4 4 l7 -8" stroke="#07061a" stroke-width="2.5" fill="none"/></g>')
b('</g>')

# query + retrieval arcs (above the conveyor)
qx, qy = iso(*station(2), 150)
ex, ey = iso(*station(2), 64)
b(f'<path class="flowq" d="M{ex-150:.0f},{ey-88:.0f} Q{ex-30:.0f},{ey-100:.0f} {ex:.0f},{ey:.0f}" stroke="{PINK}" stroke-width="2" fill="none"/>')
b(f'<circle cx="{ex-150:.0f}" cy="{ey-88:.0f}" r="4" fill="{PINK}" filter="url(#glow)"/>')
b(f'<text class="mono" x="{ex-160:.0f}" y="{ey-84:.0f}" font-size="12" fill="{PINK}" text-anchor="end" letter-spacing="1">query: “What does clause 4.2 say?”</text>')
dbx, dby = iso(*station(3), 80); llx, lly = iso(*station(4), 100)
b(f'<path class="flowq" d="M{dbx:.0f},{dby:.0f} Q{(dbx+llx)/2:.0f},{dby-90:.0f} {llx:.0f},{lly:.0f}" stroke="{CYAN}" stroke-width="2" fill="none"/>')
b(f'<text class="mono" x="{(dbx+llx)/2:.0f}" y="{dby-58:.0f}" font-size="11" fill="{CYAN}" text-anchor="middle" letter-spacing="1.5">top-k chunks + scores</text>')

# packets riding the conveyor (SMIL — works inside <img>)
for k in range(7):
    col = [CYAN, VIOLET, PINK][k % 3]
    b(f'<rect x="-5" y="-5" width="10" height="10" fill="{col}" transform="rotate(0)" filter="url(#glow)" opacity=".95">'
      f'<animateMotion dur="7s" begin="-{k*1:.1f}s" repeatCount="indefinite" path="{path}"/></rect>')

# labels under each station
LBL = [('01 · INGEST', 'PDF · CSV · web pages'), ('02 · CHUNK', 'recursive splitter'),
       ('03 · EMBED', 'Hugging Face / OpenAI'), ('04 · INDEX', 'Pinecone · FAISS'),
       ('05 · GENERATE', 'Groq LLM + context'), ('06 · ANSWER', 'grounded · cited')]
for t, (h1, h2) in enumerate(LBL):
    lx, ly = iso(*station(t)); ly += 70
    b(f'<g class="lbl" style="animation-delay:{t*.12:.2f}s"><line x1="{lx:.0f}" y1="{ly-26:.0f}" x2="{lx:.0f}" y2="{ly-14:.0f}" stroke="{CYAN}" stroke-opacity=".6"/>'
      f'<text class="mono" x="{lx:.0f}" y="{ly:.0f}" font-size="12.5" font-weight="700" fill="{WHITE}" text-anchor="middle" letter-spacing="1.5">{h1}</text>'
      f'<text class="mono" x="{lx:.0f}" y="{ly+18:.0f}" font-size="11" fill="#9fb4d9" text-anchor="middle">{h2}</text></g>')

# title
b(f'<text class="mono" x="40" y="46" font-size="12" fill="{CYAN}" letter-spacing="4">● RAG PIPELINE · ISOMETRIC VIEW</text>')
b(f'<text x="40" y="78" font-size="24" font-weight="800" fill="#fff">How my chatbots stay grounded</text>')
b(f'<text x="40" y="102" font-size="14" fill="#b9b4ea">Retrieve the right context first — then let the LLM answer, with sources.</text>')
for (x, y, ddx, ddy) in [(18, 18, 1, 1), (W - 18, 18, -1, 1), (18, H - 18, 1, -1), (W - 18, H - 18, -1, -1)]:
    b(f'<path d="M{x} {y + 20*ddy} V{y} H{x + 20*ddx}" fill="none" stroke="{CYAN}" stroke-width="2" stroke-opacity=".8"/>')
b('</g>')
b(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="{CYAN}" stroke-opacity=".25"/>')
a(''.join(g)); a('</svg>')
open('assets/rag-pipeline.svg', 'w').write('\n'.join(out))
print('rag-pipeline.svg', sum(len(x) for x in out) // 1024, 'KB')
