"""gen.py — สร้าง quiz-wave-phase.html จาก bank.py (รูปคำนวณจากสมการจริง)
ระบบตามคู่มือ §7, §8, §25: ยืนยันตัวตน → ทำข้อสอบจับเวลา → บันทึกแบบกันซ้ำ (submitId)
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import BANK, FIG4_THETA

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quiz-wave-phase.html')
FOAM = '#7FD8E8'; CREST = '#3BA3C7'; SUN = '#F4B740'; CORAL = '#E8654A'; GREY = '#8FA7BF'

def poly(p): return 'M' + ' L'.join('%.1f,%.1f' % q for q in p)
def T(x, y, s, size=15, col='#fff', anc='middle', w=700, fam='Prompt'):
    return '<text x="%.1f" y="%.1f" fill="%s" font-family="%s" font-size="%s" font-weight="%s" text-anchor="%s">%s</text>' % (x, y, col, fam, size, w, anc, s)
def L(x1, y1, x2, y2, col, w=2, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s/>' % (x1, y1, x2, y2, col, w, d)
def arrowhead(x, y, ang, col, s=10):
    a1, a2 = ang + math.pi - .42, ang + math.pi + .42
    return '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (x, y, x + s*math.cos(a1), y + s*math.sin(a1), x + s*math.cos(a2), y + s*math.sin(a2), col)
def arrow(x1, y1, x2, y2, col, w=2.2, both=False):
    a = math.atan2(y2 - y1, x2 - x1); s = 10
    o = L(x1 + (s*.7*math.cos(a) if both else 0), y1 + (s*.7*math.sin(a) if both else 0), x2 - s*.7*math.cos(a), y2 - s*.7*math.sin(a), col, w)
    o += arrowhead(x2, y2, a, col)
    if both: o += arrowhead(x1, y1, a + math.pi, col)
    return o
def svg(W, H, body): return '<svg viewBox="0 0 %d %d" width="%d" stroke-linecap="round">%s</svg>' % (W, H, W, body)

# ---------- รูป f4: คลื่นไปทางขวา จุด A–D (หาทิศการเคลื่อนที่) ----------
def fig4():
    W, H = 420, 190; x0, y0, A, lam = 20, 100, 52, 230
    xs = lambda th: x0 + th/(2*math.pi)*lam
    b = [L(10, y0, 410, y0, 'rgba(143,167,191,.5)', 1.5, '6 6')]
    b.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly([(x, y0 - A*math.sin(2*math.pi*(x - x0)/lam)) for x in [x0 + i*1.5 for i in range(int(390/1.5))]]), FOAM))
    for th, nm in zip(FIG4_THETA, 'ABCD'):
        x = xs(th); y = y0 - A*math.sin(th)
        b.append('<circle cx="%.1f" cy="%.1f" r="7" fill="%s"/>' % (x, y, SUN))
        if abs(math.sin(th)) > 0.5:                       # สัน/ท้อง/ใกล้สัน: ป้ายเหนือหรือใต้จุด
            dx, dy = 0, (-14 if math.sin(th) > 0 else 26)
        else:                                              # ที่สมดุล: วางป้ายฝั่งที่เส้นคลื่นไม่ผ่าน
            dx, dy = -14, (-12 if math.cos(th) > 0 else 24)
        b.append(T(x + dx, y + dy, nm, 16, '#fff'))
    b.append(arrow(290, 22, 400, 22, CREST, 2.6) + T(282, 27, 'ทิศของคลื่น', 13, CREST, 'end', 600, 'Kanit'))
    return svg(W, H, ''.join(b))

# ---------- รูป f9: λ = 40 cm, P และ Q ห่าง 30 cm ----------
def fig9():
    W, H = 420, 200; x0, y0, A, lam = 40, 108, 50, 240         # 240 หน่วยภาพ = 40 cm
    b = [L(20, y0, 405, y0, 'rgba(143,167,191,.5)', 1.5, '6 6')]
    b.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly([(x, y0 - A*math.sin(2*math.pi*(x - x0)/lam)) for x in [x0 + i*1.5 for i in range(int(360/1.5))]]), FOAM))
    c1, c2 = x0 + lam/4, x0 + 5*lam/4
    yb = y0 - A - 22
    b.append(L(c1, y0 - A - 8, c1, yb - 8, GREY, 1.2, '3 4') + L(c2, y0 - A - 8, c2, yb - 8, GREY, 1.2, '3 4'))
    b.append(arrow((c1 + c2)/2 - 34, yb, c1, yb, SUN) + arrow((c1 + c2)/2 + 34, yb, c2, yb, SUN))
    b.append(T((c1 + c2)/2, yb + 5, '40 cm', 14, SUN))
    xP, xQ = x0, x0 + lam*30/40                                  # P ที่สมดุล, Q ห่าง 30 cm (= 3λ/4 → ท้องคลื่น)
    for x, nm in [(xP, 'P'), (xQ, 'Q')]:
        y = y0 - A*math.sin(2*math.pi*(x - x0)/lam)
        b.append('<circle cx="%.1f" cy="%.1f" r="7" fill="%s"/>' % (x, y, CORAL))
        b.append(T(x - 12, y - 10, nm, 16, CORAL, 'end') if nm == 'P' else T(x + 12, y + 6, nm, 16, CORAL, 'start'))
    yq = y0 + A + 26
    b.append(L(xP, y0 + 8, xP, yq + 8, GREY, 1.2, '3 4') + L(xQ, y0 + A + 10, xQ, yq + 8, GREY, 1.2, '3 4'))
    b.append(arrow((xP + xQ)/2 - 30, yq, xP, yq, '#fff') + arrow((xP + xQ)/2 + 30, yq, xQ, yq, '#fff'))
    b.append(T((xP + xQ)/2, yq + 5, '30 cm', 14, '#fff'))
    return svg(W, H, ''.join(b))

FIGS = {'f4': fig4(), 'cap4': 'คลื่นในเส้นเชือกเคลื่อนที่ไปทางขวา ณ ขณะหนึ่ง',
        'f9': fig9(), 'cap9': 'ความยาวคลื่น 40 cm · P และ Q ห่างกัน 30 cm'}

bank_js = json.dumps([{k: v for k, v in it.items() if k in ('cat', 't', 'q', 'o', 'a', 'e', 'calc', 'fig', 'fix') and v is not None}
                      for it in BANK], ensure_ascii=False, indent=0)
tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quiz_tpl.html'), encoding='utf8').read()
html = tpl.replace('/*__BANK__*/[]', bank_js).replace('/*__FIGS__*/{}', json.dumps(FIGS, ensure_ascii=False))
assert '/*__' not in html
open(OUT, 'w', encoding='utf8').write(html)
print('เขียน', OUT, '%.1f KB' % (len(html.encode())/1024), '· คลัง', len(BANK), 'ข้อ')
