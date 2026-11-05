"""สร้างหน้า "กำลังจัดทำ" ของบทที่ยังไม่มีสื่อ ใช้ภาพประกอบเดียวกับหน้ารวม (ดึงจาก index.html)
ใช้: python3 tools/make_placeholders.py   — เมื่อบทใดพร้อมแล้ว ให้วางไฟล์บทนั้นทับ <โฟลเดอร์>/index.html
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
art = lambda k: re.search(r'<!--ART:%s-->([\s\S]*?)<!--/ART-->' % k, html).group(1)

CH = [
    ('ch10-wave-optics', 'wave_optics', 'บทที่ 10', 'แสงเชิงคลื่น', 'Wave Optics', '#2A1F5C',
     ['แสงเป็นคลื่น', 'การแทรกสอดผ่านสลิตคู่', 'การเลี้ยวเบนผ่านสลิตเดี่ยว', 'เกรตติง']),
    ('ch11-ray-optics', 'ray_optics', 'บทที่ 11', 'แสงเชิงรังสี', 'Ray Optics', '#0F4747',
     ['การสะท้อนของแสง', 'กระจกโค้ง', 'การหักเหของแสง', 'เลนส์บาง']),
]
TPL = '''<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{num} {title} — ฟิสิกส์ของคลื่น ม.5</title>
<meta name="theme-color" content="#0B1F3A">
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@600;700;800&family=Kanit:wght@500;600&family=Sarabun:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;}}
body{{margin:0;min-height:100vh;background:#F7F2E7;color:#123A63;font-family:'Sarabun',system-ui,sans-serif;font-size:17px;line-height:1.6;
  display:flex;align-items:center;justify-content:center;padding:calc(env(safe-area-inset-top) + 20px) 16px calc(env(safe-area-inset-bottom) + 20px);}}
.box{{width:100%;max-width:640px;background:#fff;border:1px solid #E6DCC8;border-radius:22px;overflow:hidden;
  box-shadow:0 1px 2px rgba(11,31,58,.06),0 16px 40px -16px rgba(11,31,58,.3);}}
.art{{aspect-ratio:5/3;background:#0B1F3A;}} .art svg{{width:100%;height:100%;display:block;}}
.body{{padding:22px 24px 26px;}}
.num{{font-family:'Kanit',sans-serif;font-weight:600;color:#1E6091;}}
h1{{font-family:'Prompt',sans-serif;font-weight:800;font-size:clamp(2rem,7vw,2.6rem);margin:.1em 0 0;color:#0B1F3A;line-height:1.15;}}
.en{{font-family:'Prompt',sans-serif;font-weight:600;color:#3BA3C7;}}
.soon{{display:inline-block;margin:14px 0 6px;font-family:'Kanit',sans-serif;font-weight:600;font-size:.95rem;
  padding:.3em .9em;border-radius:999px;background:#FCEBC4;color:#8A5A00;}}
ul{{padding-left:1.2em;margin:.4em 0 1.2em;}}
a.back{{display:flex;justify-content:space-between;align-items:center;text-decoration:none;color:#fff;background:{btn};
  font-family:'Kanit',sans-serif;font-weight:600;padding:12px 16px;border-radius:14px;}}
</style>
</head>
<body>
<div class="box">
  <div class="art">{art}</div>
  <div class="body">
    <div class="num">{num}</div>
    <h1>{title}</h1>
    <div class="en">{en}</div>
    <span class="soon">กำลังจัดทำ</span>
    <p>หัวข้อที่จะมีในบทนี้</p>
    <ul>{items}</ul>
    <a class="back" href="../">← กลับหน้ารวมบทเรียน <span>⌂</span></a>
  </div>
</div>
</body>
</html>
'''
for folder, key, num, title, en, btn, items in CH:
    os.makedirs(os.path.join(ROOT, folder), exist_ok=True)
    p = os.path.join(ROOT, folder, 'index.html')
    if os.path.exists(p) and 'กำลังจัดทำ' not in open(p, encoding='utf8').read():
        print('ข้าม', folder, '(มีไฟล์บทจริงแล้ว)'); continue
    open(p, 'w', encoding='utf8').write(TPL.format(num=num, title=title, en=en, btn=btn, art=art(key),
                                                  items=''.join('<li>%s</li>' % i for i in items)))
    print('สร้าง', p)
