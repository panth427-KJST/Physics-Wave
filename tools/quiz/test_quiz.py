"""ทดสอบ quiz-wave-phase.html เชิงพฤติกรรม (จำลองเซิร์ฟเวอร์ GAS ด้วย page.route)"""
import json, os, sys, time
sys.path.insert(0, '/home/claude/ch09/tools')
from harness import attach, collect_errors
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(HERE, 'quiz-wave-phase.html')
SHOTS = os.path.join(HERE, 'shots'); os.makedirs(SHOTS, exist_ok=True)
ok = True
def check(c, m):
    global ok; print(('ผ่าน  ' if c else 'ไม่ผ่าน ') + m); ok &= bool(c)

class Server:
    """จำลอง Code.gs: lookup / save (กันซ้ำด้วย submitId) / verify"""
    def __init__(self, fail_saves=0):
        self.rows = {}; self.calls = []; self.fail_saves = fail_saves
    def __call__(self, route):
        body = json.loads(route.request.post_data); self.calls.append(body)
        a = body.get('action')
        if a == 'lookup':
            return route.fulfill(status=200, body=json.dumps({'status': 'found', 'sid': '99999', 'room': '5/1', 'no': '1', 'name': 'นักเรียน ทดสอบ'}))
        if a == 'save':
            sid = body['submitId']
            if sid not in self.rows: self.rows[sid] = body          # ★ เขียนลงชีตแล้ว
            if self.fail_saves > 0:                                   # แต่คำตอบกลับหาย (เน็ตหลุด)
                self.fail_saves -= 1; return route.abort()
            return route.fulfill(status=200, body=json.dumps({'status': 'success', 'attempt': len(self.rows), 'counted': True}))
        if a == 'verify':
            return route.fulfill(status=200, body=json.dumps({'status': 'found' if body['submitId'] in self.rows else 'notfound', 'attempt': 1}))
        route.fulfill(status=200, body='{}')

def open_page(p, srv, device=None):
    ctx = p.chromium.launch().new_context(**(p.devices[device] if device else {'viewport': {'width': 1280, 'height': 900}}))
    pg = ctx.new_page(); attach(pg); pg.route('**script.google.com**', srv)
    errs = []; collect_errors(pg, errs)
    pg.goto(URL); pg.wait_for_timeout(500)
    return pg, errs

def login_start(pg):
    pg.fill('#in-sid', '99999'); pg.click('#btnLookup'); pg.wait_for_selector('#confirmBox', state='visible')
    pg.click('text=ยืนยันและเริ่มทำแบบทดสอบ'); pg.wait_for_timeout(300)

def answer_all(pg, mode):
    n = pg.evaluate('activeQuiz.length')
    for i in range(n):
        a = pg.evaluate('activeQuiz[cur].a')
        if mode == 'right': pg.click('#qOpts .opt >> nth=%d' % a)
        elif mode == 'wrong': pg.click('#qOpts .opt >> nth=%d' % ((a + 1) % 4))
        pg.click('#btnNextQ'); pg.wait_for_timeout(60)
    pg.wait_for_timeout(600)

with sync_playwright() as p:
    # ---------- 1) สุ่ม 20 รอบ: ครบ 3/3/4 · สลับตัวเลือกแล้วเฉลยยังถูก (เทียบด้วยข้อความ) ----------
    srv = Server(); pg, errs = open_page(p, srv)
    r = pg.evaluate('''(()=>{const out=[];for(let k=0;k<20;k++){const A=buildActiveQuiz();
        const c={1:0,2:0,3:0};let good=true,uniq=new Set();
        A.forEach(q=>{c[q.cat]++;uniq.add(q.q);const orig=QUIZ_BANK.find(b=>b.q===q.q);
          if(q.o[q.a]!==orig.o[orig.a]) good=false; if(q.o.slice().sort().join()!==orig.o.slice().sort().join()) good=false;});
        out.push({c,good,n:A.length,u:uniq.size});}return out;})()''')
    check(all(x['c'] == {'1': 3, '2': 3, '3': 4} and x['n'] == 10 and x['u'] == 10 for x in r), 'สุ่ม 20 รอบ ได้ 3/3/4 = 10 ข้อไม่ซ้ำทุกครั้ง')
    check(all(x['good'] for x in r), 'สลับตัวเลือกแล้ว เฉลยยังชี้ข้อความคำตอบที่ถูก (เทียบด้วยข้อความ ไม่ใช่ index)')
    fixed_ok = pg.evaluate('''(()=>{for(let k=0;k<30;k++){for(const q of buildActiveQuiz()){if(q.fix){const o=QUIZ_BANK.find(b=>b.q===q.q);if(q.o.join()!==o.o.join())return false;}}}return true;})()''')
    check(fixed_ok, 'ข้อตัวเลข/ป้ายในรูป ไม่ถูกสลับตัวเลือก')
    calc_easy = pg.evaluate('QUIZ_BANK.filter(q=>q.calc).every(q=>q.cat===3) && !QUIZ_BANK.some(q=>q.cat===4)')
    check(calc_easy, 'ข้อคำนวณทั้งหมดเป็นระดับง่าย (หมวด 3) ไม่มีหมวดคำนวณปานกลาง')

    # ---------- 2) ถูกหมด → 10 · บันทึก 1 ครั้ง payload ครบ ----------
    pg.screenshot(path=os.path.join(SHOTS, 'd-info.png'))
    login_start(pg); answer_all(pg, 'right')
    check(pg.inner_text('#rScore') == '10', 'ตอบถูกทุกข้อ → 10/10')
    saves = [c for c in srv.calls if c['action'] == 'save']
    need = {'action', 'sid', 'room', 'no', 'name', 'quiz', 'score', 'chapter', 'device', 'submitId'}
    check(len(saves) == 1 and need <= set(saves[0]) and saves[0]['quiz'] == 'wave-phase' and saves[0]['chapter'] == 'คลื่น',
          'ส่งบันทึก 1 ครั้ง payload ครบ 10 ช่อง (quiz = wave-phase, chapter = คลื่น)')
    check(saves[0]['device'].endswith('· ไม่สลับหน้าจอ'), 'สตริงอุปกรณ์ต่อท้าย "· ไม่สลับหน้าจอ" → %s' % saves[0]['device'])
    check('saved' in pg.get_attribute('#saveStatus', 'class'), 'แสดงสถานะบันทึกสำเร็จ')
    pg.click('#revBtn'); pg.wait_for_timeout(200)
    check(pg.locator('.rev-item').count() == 10 and pg.locator('.tag.good').count() == 10, 'เฉลยรายข้อแสดงครบ 10 ข้อ ตอบถูก 10')
    pg.screenshot(path=os.path.join(SHOTS, 'd-result.png'), full_page=True)
    check(not errs, 'ไม่มี JS error' + ('' if not errs else ': ' + '; '.join(errs[:3])))

    # ---------- 3) ผิดหมด → 0 · ข้ามหมด → 0 + skip 10 · ทำใหม่ได้ submitId ใหม่ ----------
    srv2 = Server(); pg2, errs2 = open_page(p, srv2)
    login_start(pg2); answer_all(pg2, 'wrong')
    check(pg2.inner_text('#rScore') == '0', 'ตอบผิดทุกข้อ → 0/10')
    pg2.goto(URL); pg2.wait_for_timeout(300); login_start(pg2); answer_all(pg2, 'skip')
    check(pg2.inner_text('#rScore') == '0' and pg2.inner_text('#bdSkip') == '10', 'ข้ามทุกข้อ → 0/10 และนับไม่ทันตอบ 10')
    ids = [c['submitId'] for c in srv2.calls if c['action'] == 'save']
    check(len(ids) == 2 and ids[0] != ids[1], 'ทำแบบทดสอบใหม่ได้ submitId ใหม่ (ไม่ถูกบล็อกการทำซ้ำ)')

    # ---------- 4) เน็ตหลุด 1 ครั้ง → retry ด้วย submitId เดิม · ชีตได้แถวเดียว ----------
    srv3 = Server(fail_saves=1); pg3, _ = open_page(p, srv3)
    login_start(pg3); answer_all(pg3, 'right'); pg3.wait_for_timeout(800)
    s3 = [c['submitId'] for c in srv3.calls if c['action'] == 'save']
    check(len(s3) == 2 and s3[0] == s3[1] and len(srv3.rows) == 1 and 'saved' in pg3.get_attribute('#saveStatus', 'class'),
          'ส่งไม่สำเร็จ 1 ครั้ง → retry ด้วย submitId เดิม ชีตได้ 1 แถว แสดงสำเร็จ')

    # ---------- 5) เน็ตหลุด 2 ครั้ง → ปุ่มตรวจสอบสถานะ (ไม่ใช่ส่งซ้ำ) → verify พบ ----------
    srv4 = Server(fail_saves=2); pg4, _ = open_page(p, srv4)
    login_start(pg4); answer_all(pg4, 'right'); pg4.wait_for_timeout(800)
    txt = pg4.inner_text('#saveStatus')
    check('ตรวจสอบสถานะ' in txt and 'ส่งซ้ำ' not in txt, 'ล้มเหลว 2 ครั้ง → แสดงปุ่ม "ตรวจสอบสถานะการบันทึก"')
    pg4.screenshot(path=os.path.join(SHOTS, 'd-verify.png'))
    pg4.click('#saveStatus button'); pg4.wait_for_timeout(500)
    v = [c for c in srv4.calls if c['action'] == 'verify']
    check(len(v) == 1 and len(srv4.rows) == 1 and 'saved' in pg4.get_attribute('#saveStatus', 'class'),
          'กดตรวจสอบ → verify พบข้อมูล แสดงสำเร็จ ชีตยังมี 1 แถว')

    # ---------- 6) ระบบสลับหน้าจอ ----------
    srv5 = Server(); pg5, _ = open_page(p, srv5)
    login_start(pg5)
    pg5.evaluate('startedAt=Date.now()-10000')
    sim = '''(ms)=>{onLeave(); awayAt=Date.now()-ms; onReturn(); return switchCount;}'''
    c1 = [pg5.evaluate(sim, 400) for _ in range(3)]
    check(c1[-1] == 0, 'ออกจากหน้า 0.4 วิ สามครั้ง → ไม่นับ')
    pg5.evaluate('startedAt=Date.now()-500')
    check(pg5.evaluate(sim, 2500) == 0, 'ช่วงผ่อนผัน 2 วิแรก → ไม่นับ')
    pg5.evaluate('startedAt=Date.now()-10000')
    check(pg5.evaluate(sim, 2500) == 1 and pg5.is_visible('#guardWarn') and not pg5.evaluate('submitted'),
          'ออกจากหน้า 2.5 วิ ครั้งที่ 1 → เตือน ยังทำต่อได้')
    pg5.screenshot(path=os.path.join(SHOTS, 'd-warn.png'))
    pg5.evaluate(sim, 3000); pg5.wait_for_timeout(500)
    sv = [c for c in srv5.calls if c['action'] == 'save']
    check(pg5.evaluate('submitted') and len(sv) == 1 and 'สลับหน้าจอ 2 ครั้ง' in sv[0]['device'] and pg5.is_visible('#autoNote'),
          'ครั้งที่ 2 → ส่งอัตโนมัติ บันทึก "%s"' % (sv[0]['device'].split('· ')[-1] if sv else '-'))

    # ---------- 7) ภาพบนมือถือ + ข้อที่มีรูป + ไม่ล้นจอ ----------
    srv6 = Server(); pg6, errs6 = open_page(p, srv6, 'iPhone 13')
    pg6.screenshot(path=os.path.join(SHOTS, 'm-info.png'))
    login_start(pg6)
    for fig in ('f4', 'f9'):
        pg6.evaluate('''(f)=>{const i=QUIZ_BANK.findIndex(q=>q.fig===f);activeQuiz[cur]=withShuffledOptions(QUIZ_BANK[i]);loadQ();}''', fig)
        pg6.wait_for_timeout(250)
        pg6.screenshot(path=os.path.join(SHOTS, 'm-%s.png' % fig))
    ov = pg6.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
    check(ov <= 0, 'มือถือ: ไม่มีส่วนล้นด้านข้าง (%dpx)' % ov)
    check(not errs6, 'มือถือ: ไม่มี JS error')

src = open(os.path.join(HERE, 'quiz-wave-phase.html'), encoding='utf8').read()
check("addEventListener('blur'" not in src and "addEventListener('focus'" not in src and 'onblur' not in src,
      'โค้ดไม่มีตัวดัก blur/focus')
print('\nสรุป:', 'ผ่านทั้งหมด' if ok else 'มีข้อไม่ผ่าน')
