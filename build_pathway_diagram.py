from PIL import Image, ImageDraw, ImageFont
import os

W, H = 2000, 1330
NAVY = (18, 39, 56)
BLUE = (29, 92, 153)
GOLD = (212, 160, 23)
GOLD_FILL = (255, 209, 102)
WHITE = (255, 255, 255)
BODY = (58, 69, 87)
LINE = (196, 206, 218)
LIGHT = (244, 246, 249)

FD = "/usr/share/fonts/truetype/liberation/"
def font(n, s):
    return ImageFont.truetype(os.path.join(FD, n), s)

f_label = font("LiberationSans-Bold.ttf", 31)
f_box   = font("LiberationSans-Bold.ttf", 37)
f_note  = font("LiberationSans-Regular.ttf", 29)
f_final = font("LiberationSans-Bold.ttf", 47)

img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)

def center_text(txt, f, cx, y, fill):
    w = d.textlength(txt, font=f)
    d.text((cx - w / 2, y), txt, font=f, fill=fill)

def box(x0, y0, x1, y1, fill, outline, width=3, radius=16):
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def arrow(x0, y0, x1, y1, color=LINE, width=5, head=16):
    d.line([x0, y0, x1, y1], fill=color, width=width)
    d.polygon([(x1 - head, y1 - head), (x1 + head, y1 - head), (x1, y1 + head // 2)], fill=color)

# ---- two routes -------------------------------------------------------
top_y0, top_y1 = 40, 250
lx0, lx1 = 110, 950
rx0, rx1 = 1050, 1890

box(lx0, top_y0, lx1, top_y1, LIGHT, BLUE, 4)
center_text("ROUTE A", f_label, (lx0 + lx1) / 2, top_y0 + 30, BLUE)
center_text("Transport Canada approved", f_box, (lx0 + lx1) / 2, top_y0 + 78, NAVY)
center_text("training program", f_box, (lx0 + lx1) / 2, top_y0 + 122, NAVY)
center_text("earns about 18 months credit", f_note, (lx0 + lx1) / 2, top_y0 + 172, GOLD)

box(rx0, top_y0, rx1, top_y1, LIGHT, BLUE, 4)
center_text("ROUTE B", f_label, (rx0 + rx1) / 2, top_y0 + 30, BLUE)
center_text("Direct entry — build all", f_box, (rx0 + rx1) / 2, top_y0 + 78, NAVY)
center_text("experience on the job", f_box, (rx0 + rx1) / 2, top_y0 + 122, NAVY)
center_text("no program credit", f_note, (rx0 + rx1) / 2, top_y0 + 172, BODY)

# ---- converge ---------------------------------------------------------
merge_y = 330
lcx, rcx = (lx0 + lx1) / 2, (rx0 + rx1) / 2
cx = W / 2
d.line([lcx, top_y1, lcx, merge_y], fill=LINE, width=5)
d.line([rcx, top_y1, rcx, merge_y], fill=LINE, width=5)
d.line([lcx, merge_y, rcx, merge_y], fill=LINE, width=5)

steps = [
    ("Build the remaining experience", "logging every task as you go"),
    ("Complete the task list", "70% of AWM 566 Appendix B items"),
    ("Pass the examinations", "technical knowledge + CAR regulatory"),
    ("Apply for the licence", "Form 24-0083"),
]

bx0, bx1 = 430, 1570
y = 400
step_h = 150
gap = 52

arrow(cx, merge_y, cx, y - 10)

for title, note in steps:
    box(bx0, y, bx1, y + step_h, WHITE, LINE, 3)
    center_text(title, f_box, cx, y + 32, NAVY)
    center_text(note, f_note, cx, y + 86, BODY)
    y += step_h
    arrow(cx, y, cx, y + gap - 10)
    y += gap

# ---- final ------------------------------------------------------------
box(bx0, y, bx1, y + 130, NAVY, NAVY, 3)
center_text("LICENSED AME", f_final, cx, y + 38, GOLD_FILL)

out = "/tmp/claude-0/-home-user-landing-page/70629628-72c9-56b7-812c-bb091a1b055d/scratchpad/pathway-diagram.png"
img.save(out, "PNG", optimize=True)
print(out, img.size)
