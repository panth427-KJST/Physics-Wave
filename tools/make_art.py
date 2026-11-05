"""make_art.py — สร้างภาพประกอบ SVG ของแต่ละบทจากการคำนวณจริง แล้วแทรกลงใน index.html
ใช้: python3 tools/make_art.py   (แทนที่ <!--ART:key--> ... <!--/ART--> ใน index.html)
"""
import math, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEEP = '#0B1F3A'; OCEAN = '#123A63'; WAVE = '#1E6091'; CREST = '#3BA3C7'; FOAM = '#7FD8E8'
SUN = '#F4B740'; CORAL = '#E8654A'; OK = '#12B886'

def poly(pts): return 'M' + ' L'.join('%.1f,%.1f' % p for p in pts)
def frange(a, b, s):
    out, x = [], a
    while x <= b + 1e-9: out.append(x); x += s
    return out

def wrap(body, extra_defs=''):
    return ('<svg viewBox="0 0 400 240" xmlns="http://www.w3.org/2000/svg" role="img" '
            'preserveAspectRatio="xMidYMid slice" stroke-linecap="round" stroke-linejoin="round">'
            '<defs>%s</defs>%s</svg>') % (extra_defs, body)

# ---------------------------------------------------------------- บทที่ 9 คลื่น
def art_waves():
    g = '<linearGradient id="bg9" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0E2A4D"/><stop offset="1" stop-color="#0B1F3A"/></linearGradient>'
    b = ['<rect width="400" height="240" fill="url(#bg9)"/>']
    # วงคลื่นแผ่จากแหล่งกำเนิดจุด (มองจากด้านบน) มุมขวาบน — λ คงที่, ความเข้มลดตามระยะ
    cx, cy = 330, 62
    for i, r in enumerate(range(10, 260, 18)):
        op = max(0.06, 0.55 - r/480)
        b.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="1.6" opacity="%.2f"/>' % (cx, cy, r, CREST, op))
    b.append('<circle cx="%d" cy="%d" r="4" fill="%s"/>' % (cx, cy, SUN))
    # คลื่นตามขวาง + อนุภาค (y = A sin(kx)) แถบล่าง
    y0, A, lam = 168, 26, 120
    b.append('<line x1="0" y1="%d" x2="400" y2="%d" stroke="%s" stroke-width="1" stroke-dasharray="4 6" opacity=".45"/>' % (y0, y0, FOAM))
    b.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly([(x, y0 - A*math.sin(2*math.pi*x/lam)) for x in frange(0, 400, 2)]), FOAM))
    for x in frange(10, 395, 15):
        y = y0 - A*math.sin(2*math.pi*x/lam)
        hit = abs(x - 145) < 1
        b.append('<circle cx="%.1f" cy="%.1f" r="%s" fill="%s"/>' % (x, y, 5.5 if hit else 3.2, CORAL if hit else '#CDEFF6'))
    # ลูกศรการสั่นของอนุภาค (ตั้งฉาก) และทิศคลื่น (ขนานแกน)
    xs = 145
    b.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2" opacity=".9"/>' % (xs + 12, y0 - A + 2, xs + 12, y0 + A - 2, CORAL))
    for yy, d in [(y0 - A, 1), (y0 + A, -1)]:
        b.append('<path d="M%d,%d l-5,%d l10,0 z" fill="%s"/>' % (xs + 12, yy, 8*d, CORAL))
    b.append('<line x1="24" y1="214" x2="120" y2="214" stroke="%s" stroke-width="2.5"/>' % SUN)
    b.append('<path d="M128,214 l-10,-5 l0,10 z" fill="%s"/>' % SUN)
    # วงเล็บ λ ระหว่างสันสองสัน
    c1 = lam/4 + lam; c2 = c1 + lam
    yb = y0 - A - 14
    b.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1.6"/>' % (c1, yb, c2, yb, SUN))
    for xx in (c1, c2):
        b.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1.6"/>' % (xx, yb - 5, xx, yb + 5, SUN))
    b.append('<text x="%.1f" y="%d" fill="%s" font-family="Prompt, sans-serif" font-weight="700" font-size="16" text-anchor="middle">λ</text>' % ((c1 + c2)/2, yb - 7, SUN))
    return wrap(''.join(b), g)

# ---------------------------------------------------------------- บทที่ 10 แสงเชิงคลื่น (สลิตคู่)
def art_wave_optics():
    g = '<linearGradient id="bg10" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1A1440"/><stop offset="1" stop-color="#0B1F3A"/></linearGradient>'
    b = ['<rect width="400" height="240" fill="url(#bg10)"/>']
    LAM_COL = '#9D7BFF'                     # แสงสีเดียว
    # หน้าคลื่นระนาบเข้าทางซ้าย
    for x in range(14, 96, 16):
        b.append('<line x1="%d" y1="24" x2="%d" y2="216" stroke="%s" stroke-width="1.6" opacity=".55"/>' % (x, x, LAM_COL))
    # ฉากกั้นที่มีสลิตคู่
    xb, s1, s2, gap = 104, 100, 140, 6
    for ya, yb_ in [(14, s1 - gap), (s1 + gap, s2 - gap), (s2 + gap, 226)]:
        b.append('<rect x="%d" y="%d" width="7" height="%d" rx="1.5" fill="#D8DEE9"/>' % (xb - 3, ya, yb_ - ya))
    # หน้าคลื่นวงกลมจากแต่ละสลิต (ครึ่งวงกลมด้านขวา) λ = 16
    lam = 16
    for sy in (s1, s2):
        for r in range(lam, 260, lam):
            b.append('<path d="M%.1f,%.1f A%d,%d 0 0 1 %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.1" opacity="%.2f"/>' %
                     (xb + 4, sy - r, r, r, xb + 4, sy + r, LAM_COL, max(0.08, 0.5 - r/520)))
    # ฉากรับแสง: ความเข้ม I(y) = cos²(π d sinθ/λ) · sinc²(π a sinθ/λ)  (สเกลเพื่อการแสดงผล)
    xs, L = 340, 236                        # ระยะสลิตถึงฉาก (หน่วยภาพ)
    d, a = s2 - s1, 9
    yc = (s1 + s2)/2
    b.append('<rect x="%d" y="10" width="22" height="220" rx="3" fill="#060B18"/>' % (xs - 2))
    for y in frange(12, 228, 1.0):
        th = math.atan((y - yc)/L)
        beta = math.pi*a*math.sin(th)/lam*1.0
        env = 1.0 if abs(beta) < 1e-9 else (math.sin(beta)/beta)**2
        I = (math.cos(math.pi*d*math.sin(th)/lam))**2*env
        if I > 0.02:
            b.append('<rect x="%d" y="%.1f" width="18" height="1.1" fill="%s" opacity="%.2f"/>' % (xs, y, LAM_COL, min(1, I*1.05)))
    # กราฟความเข้มด้านขวาของฉาก
    pts = []
    for y in frange(12, 228, 1.0):
        th = math.atan((y - yc)/L); beta = math.pi*a*math.sin(th)/lam
        env = 1.0 if abs(beta) < 1e-9 else (math.sin(beta)/beta)**2
        I = (math.cos(math.pi*d*math.sin(th)/lam))**2*env
        pts.append((364 + 30*I, y))
    b.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (poly(pts), SUN))
    return wrap(''.join(b), g)

# ---------------------------------------------------------------- บทที่ 11 แสงเชิงรังสี (เลนส์นูน)
def art_ray_optics():
    g = ('<linearGradient id="bg11" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#103A3A"/><stop offset="1" stop-color="#0B1F3A"/></linearGradient>'
         '<linearGradient id="lens" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7FD8E8" stop-opacity=".25"/><stop offset=".5" stop-color="#CFF4FA" stop-opacity=".55"/><stop offset="1" stop-color="#7FD8E8" stop-opacity=".25"/></linearGradient>')
    b = ['<rect width="400" height="240" fill="url(#bg11)"/>']
    ax, lx, f = 120, 200, 56                 # แกนมุขสำคัญ y, ตำแหน่งเลนส์ x, ความยาวโฟกัส
    u, ho = 140, 54                          # ระยะวัตถุ, ความสูงวัตถุ
    v = 1/(1/f - 1/u); hi = -ho*v/u          # สมการเลนส์บาง: ภาพจริงหัวกลับ
    xo, xi = lx - u, lx + v
    yo, yi = ax - ho, ax - hi
    # แกนมุขสำคัญ + จุดโฟกัส
    b.append('<line x1="8" y1="%d" x2="392" y2="%d" stroke="#8FA7BF" stroke-width="1.2" stroke-dasharray="5 5"/>' % (ax, ax))
    for x, t in [(lx - f, 'F'), (lx + f, 'F'), (lx - 2*f, '2F'), (lx + 2*f, '2F')]:
        b.append('<circle cx="%d" cy="%d" r="2.6" fill="#D8DEE9"/>' % (x, ax))
        b.append('<text x="%d" y="%d" fill="#B9C8D8" font-family="Prompt, sans-serif" font-weight="600" font-size="11" text-anchor="middle">%s</text>' % (x, ax + 16, t))
    # เลนส์นูน
    H = 92
    b.append('<path d="M%d,%d Q%d,%d %d,%d Q%d,%d %d,%d Z" fill="url(#lens)" stroke="%s" stroke-width="1.4"/>' %
             (lx, ax - H, lx + 22, ax, lx, ax + H, lx - 22, ax, lx, ax - H, FOAM))
    # วัตถุ (ลูกศรสีเหลือง) และภาพ (ลูกศรสีส้ม)
    def arrow_v(x, y1, y2, col):
        d = -1 if y2 < y1 else 1
        return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3"/>'
                '<path d="M%.1f,%.1f l-6,%d l12,0 z" fill="%s"/>') % (x, y1, x, y2 - d*6, col, x, y2, -d*10, col)
    b.append(arrow_v(xo, ax, yo, SUN))
    b.append(arrow_v(xi, ax, yi, CORAL))
    # รังสีหลัก 3 เส้น (จากยอดวัตถุ)
    rays = []
    # 1) ขนานแกน → หักเหผ่าน F ด้านหลัง → ผ่านยอดภาพ
    rays.append([(xo, yo), (lx, yo), (xi, yi)])
    # 2) ผ่านจุดกลางเลนส์ไม่หักเห
    rays.append([(xo, yo), (xi, yi)])
    # 3) ผ่าน F ด้านหน้า → หักเหขนานแกน → ผ่านยอดภาพ
    ylens = ax + ho*f/(u - f)                     # รังสีจากยอดวัตถุผ่าน F ไปตัดเลนส์ที่ใต้แกน ho·f/(u−f)
    rays.append([(xo, yo), (lx, ylens), (xi, ylens)])
    cols = [SUN, '#FFE29A', '#F7C46B']
    for pts, c in zip(rays, cols):
        b.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.7" opacity=".95"/>' % (poly(pts), c))
        # ต่อรังสีเลยภาพออกไปเล็กน้อย
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        t = 40/math.hypot(x2 - x1, y2 - y1)
        b.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.7" opacity=".55"/>' % (x2, y2, x2 + (x2 - x1)*t, y2 + (y2 - y1)*t, c))
    return wrap(''.join(b), g), dict(v=v, hi=hi, ylens=ylens)

# ---------------------------------------------------------------- ตรวจความถูกต้องของรังสี
ART11, info = art_ray_optics()
f, u, ho, lx, ax = 56, 140, 54, 200, 120
v = info['v']; hi = info['hi']
assert abs(1/u + 1/v - 1/f) < 1e-12                       # สมการเลนส์
assert hi < 0                                             # ภาพหัวกลับ
# รังสี 1 หลังเลนส์ต้องผ่าน F' : เส้นจาก (lx, ax−ho) ไป (lx+v, ax−hi) ผ่าน (lx+f, ax)
y_at_F = (ax - ho) + ((ax - hi) - (ax - ho))*(f/v)
assert abs(y_at_F - ax) < 1e-9
# รังสี 3 ก่อนเลนส์ต้องผ่าน F : เส้นจาก (lx−u, ax−ho) ไป (lx, ylens) ผ่าน (lx−f, ax)
y_at_F2 = (ax - ho) + (info['ylens'] - (ax - ho))*((u - f)/u)
assert abs(y_at_F2 - ax) < 1e-9
# รังสี 3 หลังเลนส์ขนานแกน ไปถึงยอดภาพพอดี
assert abs(info['ylens'] - (ax - hi)) < 1e-9
print('ray optics ok: v = %.1f, image height = %.1f (หัวกลับ, เล็กลง)' % (v, hi))

ARTS = {'waves': art_waves(), 'wave_optics': art_wave_optics(), 'ray_optics': ART11}

p = os.path.join(ROOT, 'index.html')
html = open(p, encoding='utf8').read()
for k, svg in ARTS.items():
    html, n = re.subn(r'<!--ART:%s-->[\s\S]*?<!--/ART-->' % k, '<!--ART:%s-->%s<!--/ART-->' % (k, svg), html)
    assert n == 1, k
open(p, 'w', encoding='utf8').write(html)
print('แทรกภาพ', len(ARTS), 'ภาพ')
