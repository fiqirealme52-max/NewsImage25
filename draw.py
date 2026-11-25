# News 25 — "The World in One Day — 25 November 2026"
# Template layout (proven in News 24 R4): 1024x1024, masthead title case,
# 3 leads + 10 mediums + 16 briefs = 29 stories, map pins, DATE CHECK.
# Scenes are drawn bright and concrete (places + things + people).
# All facts re-verified live 25 Nov 2026 before render (see report).
import sys
sys.path.insert(0, 'vendor')
from PIL import Image, ImageDraw, ImageFont
import random
random.seed(25)

W, H = 1024, 1024
INK = (26, 22, 18)
PAPER = (250, 246, 236)
RED = (164, 30, 26)
DARKRED = (128, 18, 16)
YELLOW = (252, 210, 65)
BORDER = (122, 106, 82)
CREAM = (244, 238, 226)
SKY = (205, 225, 240)
SEA = (140, 190, 220)
GREEN = (70, 130, 80)
GOLD = (212, 160, 60)

def lf(name, size):
    return ImageFont.truetype('/usr/share/fonts/truetype/liberation/' + name, size)

def nf(name, size):
    return ImageFont.truetype('/usr/share/fonts/truetype/noto/' + name, size)

def tracked_width(d, text, font, track):
    return sum(d.textlength(ch, font=font) for ch in text) + track * (len(text) - 1)

def draw_tracked(d, x, y, text, font, track, fill):
    # Draw with manual letter-spacing (negative track squeezes the line).
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=font, fill=fill)
        cx += d.textlength(ch, font=font) + track
    return cx

def fit_font(d, text, fname, sizes, max_w):
    for s in sizes:
        f = lf(fname, s)
        if d.textlength(text, font=f) <= max_w:
            return f, s
    f = lf(fname, sizes[-1])
    return f, sizes[-1]

def assert_fit(d, text, font, max_w, what):
    w = d.textlength(text, font=font)
    if w > max_w:
        sys.exit('OVERFLOW %s: %r width %d > %d' % (what, text, w, max_w))

def vgrad(d, x0, y0, x1, y1, c0, c1, steps=24):
    for i in range(steps):
        t = i / (steps - 1)
        c = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
        yy0 = y0 + (y1 - y0) * i // steps
        yy1 = y0 + (y1 - y0) * (i + 1) // steps
        d.rectangle([x0, yy0, x1, yy1], fill=c)

def glow(d, cx, cy, r, col=(252, 220, 130)):
    for rr in range(r, 0, -2):
        a = 1 - rr / float(r)
        cc = tuple(int(255 - (255 - col[k]) * a) for k in range(3))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=cc)

def moon(d, x, y, r=14):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 246, 224), outline=(150, 150, 130))
    d.ellipse([x - r + 4, y - r + 6, x - r + 8, y - r + 10], fill=(210, 205, 180))
    d.ellipse([x + 2, y + 3, x + 6, y + 7], fill=(210, 205, 180))

def stars(d, x0, y0, x1, y1, n=12):
    for _ in range(n):
        x = random.randint(x0, x1); y = random.randint(y0, y1)
        d.ellipse([x, y, x + 1, y + 1], fill=(250, 250, 240))

def sun(d, x, y, r=10):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(252, 220, 100), outline=(230, 180, 60))
    for a in range(0, 360, 45):
        import math
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([x + ca * (r + 2), y + sa * (r + 2), x + ca * (r + 6), y + sa * (r + 6)], fill=(230, 180, 60), width=2)

def person(d, x, y, h, skin=(232, 190, 150), shirt=(60, 90, 160), pants=(40, 40, 60)):
    # Head, torso, legs, one raised arm. y = feet, h = total height (works for h >= 10).
    head_h = max(4, h // 3)
    torso_h = max(5, h // 3)
    d.ellipse([x - 3, y - h, x + 3, y - h + head_h], fill=skin, outline=(120, 90, 70))
    d.rectangle([x - 4, y - h + head_h + 1, x + 4, y - h + head_h + 1 + torso_h], fill=shirt)
    d.line([x + 4, y - h + head_h + 3, x + 9, y - h + 2], fill=skin, width=2)
    leg_top = y - h + head_h + 1 + torso_h + 1
    if leg_top < y:
        d.rectangle([x - 4, leg_top, x, y], fill=pants)
        d.rectangle([x + 1, leg_top, x + 5, y], fill=pants)

def car(d, x, y, w, body=(210, 60, 45), win=(205, 225, 240)):
    d.rectangle([x, y, x + w, y + 8], fill=body)
    d.rectangle([x + w * 0.15, y - 6, x + w * 0.8, y + 2], fill=body)
    d.rectangle([x + w * 0.2, y - 4, x + w * 0.45, y], fill=win)
    d.rectangle([x + w * 0.5, y - 4, x + w * 0.75, y], fill=win)
    d.ellipse([x + 4, y + 7, x + 12, y + 15], fill=(30, 30, 30))
    d.ellipse([x + w - 12, y + 7, x + w - 4, y + 15], fill=(30, 30, 30))

def flames(d, x, y, w, h):
    for i in range(7):
        fx = x + i * (w // 7) + 3
        fh = h - i % 3 * 4
        d.polygon([(fx - 4, y + h), (fx, y + h - fh), (fx + 4, y + h)], fill=(250, 140, 40))
        d.polygon([(fx - 2, y + h), (fx, y + h - fh // 2), (fx + 2, y + h)], fill=(250, 210, 80))

def flame_tongues(d, x, y, w, h):
    for i in range(5):
        fx = x + i * (w // 5) + 3
        d.polygon([(fx - 3, y + h), (fx, y + h - h // 2 - 4), (fx + 3, y + h)], fill=(250, 170, 60))
        d.polygon([(fx - 1, y + h), (fx, y + h - h // 3), (fx + 1, y + h)], fill=(255, 230, 120))

def wisps(d, x, y, w, h, col=(160, 160, 155)):
    d.ellipse([x, y, x + w // 2, y + h // 2], outline=col, width=2)
    d.ellipse([x + w // 3, y + h // 3, x + w, y + h], outline=col, width=2)
    d.ellipse([x + w // 2, y + 2, x + w, y + h // 2 + 2], outline=col, width=2)

def smoke(d, x, y, w, h):
    d.ellipse([x, y, x + w // 3, y + h // 3], fill=(160, 155, 150))
    d.ellipse([x + w // 4, y + h // 4, x + w // 2 + w // 4, y + h // 2 + h // 4], fill=(180, 175, 170))
    d.ellipse([x + w // 2, y, x + w, y + h // 2], fill=(195, 190, 185))

def tag_chip(d, x, y, text, bg=INK, fg=(255, 255, 255), size=11):
    f = lf('LiberationSans-Bold.ttf', size)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + tw + 12, y + 16], radius=3, fill=bg)
    d.text((x + 6, y + 2), text, font=f, fill=fg)

def textwrap(d, text, font, max_w):
    lines = []
    for para in text.split(' '):
        if not lines or d.textlength(lines[-1] + ' ' + para, font=font) > max_w:
            lines.append(para)
        else:
            lines[-1] += ' ' + para
    return lines

# ---------- LEAD SCENES (new, bright) ----------

def scene_tokyo_red(d, x, y, w, h):
    # L1: Tokyo trading floor, giant red board, falling red bars, busy floor.
    # Sky window (right, 104px wide, full height): Tokyo Tower + skyline + clouds.
    vgrad(d, x, y, x + w, y + h, (252, 248, 240), (238, 232, 214))
    # Window right: pale blue sky, sun, clouds, grey skyline, Tokyo Tower.
    # (REUTERS chip covers x+w-65..x+w, y+8..y+24 — keep tower + sun clear of it.)
    d.rectangle([x + w - 104, y, x + w, y + 74], fill=SKY)
    sun(d, x + w - 88, y + 14, 8)
    d.ellipse([x + w - 100, y + 6, x + w - 66, y + 16], fill=(255, 255, 255))
    d.ellipse([x + w - 60, y + 30, x + w - 28, y + 38], fill=(255, 255, 255))
    # Skyline buildings along the window base.
    for bx, bw, bh in [(x + w - 102, 12, 26), (x + w - 70, 14, 22),
                       (x + w - 34, 12, 30), (x + w - 20, 16, 20)]:
        d.rectangle([bx, y + 74 - bh, bx + bw, y + 74], fill=(120, 130, 140))
        d.rectangle([bx + 3, y + 74 - bh + 4, bx + bw - 3, y + 74 - bh + 10], fill=(200, 220, 235))
        d.rectangle([bx + 3, y + 74 - bh + 14, bx + bw - 3, y + 74 - bh + 20], fill=(200, 220, 235))
    # Tokyo Tower, red-white lattice, left of the REUTERS chip zone.
    tx = x + w - 80
    d.polygon([(tx - 7, y + 74), (tx - 2, y + 40), (tx + 2, y + 40), (tx + 7, y + 74)], fill=(200, 60, 50))
    d.polygon([(tx - 2, y + 40), (tx, y + 26), (tx + 2, y + 40)], fill=(200, 60, 50))
    d.line([tx, y + 26, tx, y + 20], fill=(200, 60, 50), width=2)
    d.rectangle([tx - 5, y + 58, tx + 5, y + 62], fill=(255, 255, 255))
    d.rectangle([tx - 4, y + 46, tx + 4, y + 49], fill=(255, 255, 255))
    # Big red board, left (narrower to make room for the wider window).
    bw2, bh2 = w - 120, 68
    d.rectangle([x + 8, y + 6, x + 8 + bw2, y + 6 + bh2], fill=(255, 255, 255), outline=(180, 170, 150))
    f = lf('LiberationSans-Bold.ttf', 11)
    d.text((x + 12, y + 9), 'NIKKEI 225', font=f, fill=RED)
    # Falling red bars, wider.
    bars = [44, 38, 32, 26, 18, 10]
    for i, bh3 in enumerate(bars):
        bx2 = x + 14 + i * 32
        d.rectangle([bx2, y + 72 - bh3, bx2 + 22, y + 72], fill=RED)
    # Red down arrow at the end of the fall.
    ax = x + 14 + 5 * 32 + 26
    d.line([ax, y + 30, ax, y + 64], fill=RED, width=3)
    d.polygon([(ax - 6, y + 58), (ax + 6, y + 58), (ax, y + 68)], fill=RED)
    # Big red -3.30% chip on the board.
    f2 = lf('LiberationSans-Bold.ttf', 14)
    tw2 = d.textlength('-3.30%', font=f2)
    d.rectangle([x + 8 + bw2 - 78, y + 8, x + 8 + bw2 - 4, y + 24], fill=RED)
    d.text((x + 8 + bw2 - 78 + (74 - tw2) / 2, y + 9), '-3.30%', font=f2, fill=(255, 255, 255))
    # Floor.
    d.rectangle([x, y + 76, x + w, y + h], fill=(210, 180, 140))
    d.rectangle([x, y + 76, x + w, y + 78], fill=(180, 150, 110))
    # Four traders, clearly visible, standing on the floor (clear of the TOKYO chip).
    person(d, x + 78, y + 102, 30, shirt=(40, 40, 60), pants=(40, 40, 60))
    person(d, x + 125, y + 102, 32, shirt=(90, 30, 30), pants=(40, 40, 60))
    person(d, x + 195, y + 102, 30, shirt=(40, 80, 60), pants=(40, 40, 60))
    person(d, x + 265, y + 102, 32, shirt=(60, 60, 70), pants=(40, 40, 60))
    # Phone in trader 2's raised hand, paper in trader 3's hand.
    d.rectangle([x + 132, y + 72, x + 138, y + 80], fill=(240, 240, 235), outline=(120, 120, 115))
    d.rectangle([x + 202, y + 78, x + 212, y + 86], fill=(255, 255, 255), outline=(180, 180, 175))
    # Two trading desks in front of traders 2 and 4 (clear of the TOKYO chip).
    for dx in [x + 90, x + 230]:
        d.rectangle([dx, y + 88, dx + 70, y + 100], fill=(120, 80, 50))
        d.rectangle([dx, y + 88, dx + 70, y + 91], fill=(150, 105, 65))
        d.rectangle([dx + 40, y + 84, dx + 62, y + 88], fill=(255, 255, 255), outline=(180, 180, 175))
    # Red Sea label chip.
    tag_chip(d, x + 10, y + h - 20, 'TOKYO', bg=RED, size=10)

def scene_jeddah(d, x, y, w, h):
    # L2: Jeddah port, Red Sea, container ship, cranes, missile in the sky.
    vgrad(d, x, y, x + w, y + 56, (205, 230, 245), (240, 245, 250))
    sun(d, x + 140, y + 14, 10)
    # Clouds.
    d.ellipse([x + 16, y + 10, x + 60, y + 22], fill=(255, 255, 255))
    d.ellipse([x + 200, y + 8, x + 250, y + 20], fill=(255, 255, 255))
    # Missile crossing the blue sky with a smoke trail (left side, clear of the source chip).
    d.line([x + 8, y + 30, x + 76, y + 16], fill=(200, 200, 195), width=3)
    d.polygon([(x + 76, y + 16), (x + 88, y + 13), (x + 86, y + 20)], fill=(80, 80, 80))
    d.ellipse([x + 0, y + 26, x + 18, y + 38], fill=(225, 225, 220))
    # Dock cranes on the horizon.
    for cx in [x + 24, x + 120, x + 250]:
        d.line([cx, y + 56, cx, y + 18], fill=(70, 70, 75), width=3)
        d.line([cx, y + 18, cx + 34, y + 26], fill=(70, 70, 75), width=2)
        d.line([cx + 30, y + 26, cx + 30, y + 44], fill=(70, 70, 75), width=1)
    # Sea.
    vgrad(d, x, y + 56, x + w, y + h, (150, 200, 230), (95, 165, 205))
    d.line([x, y + 56, x + w, y + 56], fill=(255, 255, 255), width=1)
    # Container ship.
    sx, sy = x + 40, y + 66
    d.rectangle([sx, sy, sx + 190, sy + 16], fill=(50, 70, 95))
    conts = [RED, (60, 90, 160), (70, 130, 80), (220, 180, 40), (60, 90, 160), RED]
    for i, c in enumerate(conts):
        d.rectangle([sx + 6 + i * 30, sy - 16, sx + 6 + i * 30 + 28, sy], fill=c, outline=(255, 255, 255))
    d.rectangle([sx + 196, sy - 8, sx + 210, sy], fill=(230, 230, 225))
    # Saudi flag on a pole at right.
    d.line([x + w - 18, y + 52, x + w - 18, y + 84], fill=(70, 70, 70), width=2)
    d.rectangle([x + w - 18, y + 52, x + w - 4, y + 62], fill=(0, 110, 60))
    d.line([x + w - 16, y + 57, x + w - 6, y + 57], fill=(255, 255, 255), width=1)
    tag_chip(d, x + 10, y + h - 20, 'RED SEA', bg=(30, 90, 140), size=10)

def scene_courtroom(d, x, y, w, h):
    # L3: Brooklyn courtroom, bright, judge bench, jury, evidence table, full room.
    vgrad(d, x, y, x + w, y + h, (250, 243, 228), (238, 228, 208))
    # Window band top with sun.
    d.rectangle([x, y, x + w, y + 20], fill=SKY)
    sun(d, x + 150, y + 10, 7)
    d.rectangle([x, y + 20, x + w, y + 22], fill=(180, 160, 130))
    # US flag, left.
    fx, fy = x + 12, y + 28
    for i in range(5):
        d.rectangle([fx, fy + i * 3, fx + 34, fy + i * 3 + 2], fill=(200, 60, 50) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([fx, fy, fx + 14, fy + 8], fill=(40, 60, 140))
    # Judge bench, center (right of the GUILTY board), with wood paneling.
    d.rectangle([x + 136, y + 30, x + 216, y + 58], fill=(120, 80, 50))
    d.rectangle([x + 136, y + 30, x + 216, y + 36], fill=(150, 105, 65))
    for px in [x + 156, x + 176, x + 196]:
        d.line([px, y + 38, px, y + 56], fill=(90, 60, 35), width=1)
    # Scales of justice standing on the bench, left of the judge.
    d.line([x + 148, y + 34, x + 148, y + 50], fill=GOLD, width=2)
    d.line([x + 139, y + 37, x + 157, y + 37], fill=GOLD, width=2)
    d.polygon([(x + 136, y + 44), (x + 142, y + 44), (x + 139, y + 50)], fill=GOLD)
    d.polygon([(x + 154, y + 44), (x + 160, y + 44), (x + 157, y + 50)], fill=GOLD)
    d.ellipse([x + 145, y + 31, x + 151, y + 36], fill=GOLD)
    # Judge, bigger and clearly visible, black robe, white collar, gavel in hand.
    person(d, x + 184, y + 56, 28, skin=(232, 190, 150), shirt=(20, 20, 25), pants=(20, 20, 25))
    d.rectangle([x + 179, y + 38, x + 189, y + 42], fill=(255, 255, 255))
    d.line([x + 192, y + 34, x + 202, y + 30], fill=(120, 85, 50), width=3)
    d.rectangle([x + 200, y + 26, x + 208, y + 32], fill=(120, 85, 50))
    # Jury box, right: four figures in a row, bigger.
    d.rectangle([x + 240, y + 34, x + w - 10, y + 60], fill=(190, 170, 140))
    d.line([x + 240, y + 34, x + w - 10, y + 34], fill=(150, 130, 105), width=2)
    for jx in [x + 250, x + 270, x + 290, x + 309]:
        person(d, jx, y + 60, 22, shirt=(70, 90, 130), pants=(50, 50, 60))
    # GUILTY 10/12 board, top-left (wide enough for the full text).
    d.rectangle([x + 54, y + 26, x + 132, y + 44], fill=(255, 255, 255), outline=RED, width=2)
    f = lf('LiberationSans-Bold.ttf', 11)
    d.text((x + 58, y + 31), 'GUILTY 10/12', font=f, fill=RED)
    # Two lawyers standing behind the courtroom rail, below the GUILTY board — bigger.
    person(d, x + 70, y + 66, 19, shirt=(40, 40, 60), pants=(40, 40, 60))
    person(d, x + 106, y + 66, 19, shirt=(90, 30, 30), pants=(40, 40, 60))
    # Papers on the rail in front of each lawyer.
    d.rectangle([x + 62, y + 58, x + 78, y + 62], fill=(255, 255, 255), outline=(180, 180, 175))
    d.rectangle([x + 98, y + 58, x + 114, y + 62], fill=(255, 255, 255), outline=(180, 180, 175))
    # Courtroom rail with balusters across the middle.
    d.rectangle([x + 8, y + 62, x + w - 8, y + 66], fill=(120, 80, 50))
    for bx in range(x + 16, x + w - 8, 20):
        d.line([bx, y + 66, bx, y + 74], fill=(120, 80, 50), width=2)
    # Evidence table foreground: chips + phones + law books.
    d.rectangle([x + 20, y + 74, x + w - 20, y + h - 6], fill=(150, 105, 65))
    d.rectangle([x + 20, y + 74, x + w - 20, y + 78], fill=(180, 135, 85))
    for i, cx in enumerate([x + 40, x + 90, x + 140, x + 190, x + 240]):
        d.rectangle([cx, y + 80, cx + 34, y + 94], fill=(220, 220, 215), outline=(120, 120, 115))
        d.rectangle([cx + 5, y + 83, cx + 29, y + 88], fill=(40, 60, 90))
        d.rectangle([cx + 8, y + 90, cx + 26, y + 92], fill=(150, 150, 145))
    for i, bc in enumerate([(164, 30, 26), (60, 90, 60), (40, 60, 140)]):
        d.rectangle([x + 276, y + 79 + i * 5, x + 304, y + 83 + i * 5], fill=bc, outline=(255, 255, 255))
    tag_chip(d, x + 10, y + h - 20, 'BROOKLYN', bg=INK, size=10)

# ---------- MEDIUM SCENES (197x52) ----------

def scene_drones_day(d, x, y, w, h):
    # M4: Kyiv at dawn — bright skyline, many lit windows, drones, fire glow.
    vgrad(d, x, y, x + w, y + h, (255, 232, 195), (252, 205, 155))
    sun(d, x + 170, y + 12, 7)
    # Searchlight beams from the ground.
    d.line([x + 30, y + h - 6, x + 58, y + 4], fill=(255, 250, 200), width=2)
    d.line([x + 162, y + h - 6, x + 142, y + 6], fill=(255, 250, 200), width=2)
    glow(d, x + 30, y + h - 8, 6, (255, 240, 180))
    glow(d, x + 162, y + h - 8, 6, (255, 240, 180))
    # Buildings, lighter than before, with two rows of lit windows each.
    for bx, bw, bh in [(x + 4, 26, 22), (x + 34, 18, 30), (x + 56, 22, 16), (x + 82, 16, 26), (x + 102, 24, 18)]:
        d.rectangle([bx, y + h - bh - 6, bx + bw, y + h - 6], fill=(120, 110, 95))
        for wy in [y + h - bh - 3, y + h - bh + 7]:
            if wy + 4 < y + h - 6:
                for wx in range(bx + 3, bx + bw - 3, 6):
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 225, 140))
    # Fire at the base of the middle building.
    flame_tongues(d, x + 78, y + h - 20, 24, 14)
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(95, 88, 78))
    # Five drones with motion lines.
    for dx, dy in [(x + 62, y + 8), (x + 90, y + 14), (x + 140, y + 6), (x + 118, y + 10), (x + 28, y + 12)]:
        d.ellipse([dx, dy, dx + 8, dy + 4], fill=(50, 50, 55))
        d.line([dx, dy + 2, dx - 8, dy + 2], fill=(50, 50, 55), width=1)
        d.line([dx + 8, dy + 2, dx + 16, dy + 2], fill=(50, 50, 55), width=1)
    # Three solid fire bursts (filled, not rings).
    for cx, cy in [(x + 60, y + 20), (x + 150, y + 26), (x + 92, y + 30)]:
        d.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill=(250, 150, 50))
        d.ellipse([cx - 4, cy - 3, cx + 4, cy + 3], fill=(255, 210, 90))

def scene_factory_day(d, x, y, w, h):
    # M5: Cikande factory fire — grey plant, orange flames, smoke.
    vgrad(d, x, y, x + w, y + h, (240, 235, 220), (215, 205, 190))
    d.rectangle([x + 10, y + 12, x + w - 10, y + h - 8], fill=(170, 165, 155), outline=(120, 115, 105))
    d.rectangle([x + 10, y + 12, x + w - 10, y + 18], fill=(140, 135, 125))
    for wx in range(x + 16, x + w - 20, 14):
        d.rectangle([wx, y + 22, wx + 8, y + 30], fill=(230, 235, 240), outline=(110, 110, 105))
    d.rectangle([x + w - 22, y + 2, x + w - 16, y + 16], fill=(150, 145, 135))
    smoke(d, x + w - 30, y - 2, 24, 16)
    flames(d, x + 14, y + h - 18, w - 28, 12)
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(100, 95, 85))
    person(d, x + 30, y + h - 6, 12, shirt=(200, 60, 40))
    person(d, x + 160, y + h - 6, 12, shirt=(60, 90, 160))

def scene_shanghai(d, x, y, w, h):
    # M6: Shanghai party building, daylight, two officials on steps.
    vgrad(d, x, y, x + w, y + h, (205, 228, 242), (235, 240, 248))
    sun(d, x + w - 18, y + 10, 7)
    d.rectangle([x + 20, y + 12, x + w - 20, y + h - 6], fill=(205, 195, 175), outline=(140, 130, 115))
    d.rectangle([x + 20, y + 12, x + w - 20, y + 17], fill=RED)
    d.rectangle([x + 26, y + 22, x + 40, y + 30], fill=(230, 235, 240), outline=(120, 120, 115))
    d.rectangle([x + w - 40, y + 22, x + w - 26, y + 30], fill=(230, 235, 240), outline=(120, 120, 115))
    d.rectangle([x + w // 2 - 9, y + 30, x + w // 2 + 9, y + h - 6], fill=RED, outline=(120, 20, 16))
    d.rectangle([x + 60, y + h - 12, x + w - 60, y + h - 6], fill=(180, 170, 150))
    person(d, x + 66, y + h - 12, 12, shirt=(40, 40, 60), pants=(40, 40, 60))
    person(d, x + w - 66, y + h - 12, 12, shirt=(40, 40, 60), pants=(40, 40, 60))
    d.rectangle([x + 8, y + h - 6, x + w - 8, y + h], fill=(140, 135, 125))

def scene_solomon(d, x, y, w, h):
    # M7: Solomon Islands signing — table, two leaders, two flags, palm, sea.
    vgrad(d, x, y, x + w, y + h, (210, 232, 245), (240, 245, 250))
    sun(d, x + 20, y + 10, 7)
    vgrad(d, x, y + h - 10, x + w, y + h, (140, 195, 225), (100, 165, 205))
    # Palm tree, right.
    d.line([x + w - 16, y + h - 10, x + w - 14, y + 12], fill=(120, 90, 60), width=3)
    for a in range(5):
        import math
        ang = math.radians(200 + a * 35)
        d.line([x + w - 14, y + 12, x + w - 14 + int(14 * math.cos(ang)), y + 12 + int(10 * math.sin(ang))], fill=(50, 130, 70), width=2)
    # Two flags behind the table (right side, clear of the banner chip).
    d.line([x + 148, y + 8, x + 148, y + 30], fill=(70, 70, 70), width=1)
    d.rectangle([x + 148, y + 8, x + 164, y + 18], fill=(40, 60, 140))
    d.line([x + 168, y + 8, x + 168, y + 30], fill=(70, 70, 70), width=1)
    d.polygon([(x + 168, y + 8), (x + 180, y + 13), (x + 168, y + 18)], fill=(40, 120, 70))
    # Table with document.
    d.rectangle([x + 78, y + 34, x + 128, y + 40], fill=(150, 105, 65))
    d.rectangle([x + 94, y + 32, x + 112, y + 36], fill=(255, 255, 255), outline=(180, 180, 175))
    d.line([x + 97, y + 34, x + 109, y + 34], fill=(100, 100, 100), width=1)
    # Two leaders shaking hands.
    person(d, x + 84, y + 40, 13, shirt=(40, 60, 120), pants=(40, 40, 60))
    person(d, x + 122, y + 40, 13, shirt=(60, 90, 60), pants=(40, 40, 60))
    d.line([x + 93, y + 32, x + 113, y + 32], fill=(232, 190, 150), width=2)

def scene_garment(d, x, y, w, h):
    # M8: Dhaka garment factory — sewing line, workers, fabric rolls, $139 board.
    vgrad(d, x, y, x + w, y + h, (248, 242, 228), (235, 225, 205))
    # $139 board on the wall (middle, clear of the banner chip).
    d.rectangle([x + 64, y + 6, x + 112, y + 20], fill=(255, 255, 255), outline=(120, 115, 100))
    f = lf('LiberationSans-Bold.ttf', 11)
    d.text((x + 67, y + 8), '$139', font=f, fill=RED)
    # Fabric rolls, right.
    for i, c in enumerate([(200, 60, 50), (60, 90, 160), (220, 180, 40), (70, 130, 80)]):
        d.rectangle([x + w - 14 - i * 8, y + 8, x + w - 8 - i * 8, y + 30], fill=c, outline=(255, 255, 255))
    # Sewing table.
    d.rectangle([x + 8, y + 32, x + w - 8, y + 38], fill=(150, 105, 65))
    for mx in [x + 24, x + 70, x + 116]:
        d.rectangle([mx, y + 26, mx + 16, y + 32], fill=(120, 120, 125))
        d.rectangle([mx + 4, y + 30, mx + 12, y + 32], fill=(60, 60, 65))
    # Workers behind the table.
    person(d, x + 32, y + 32, 13, shirt=(200, 60, 50))
    person(d, x + 78, y + 32, 13, shirt=(220, 180, 40))
    person(d, x + 124, y + 32, 13, shirt=(60, 90, 160))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(190, 170, 140))

def scene_ucl(d, x, y, w, h):
    # M9: UCL night stadium, floodlit, two teams lining up.
    vgrad(d, x, y, x + w, y + 20, (140, 150, 190), (190, 190, 220))
    # Floodlight poles + glow.
    for px in [x + 12, x + w - 12]:
        d.line([px, y + 2, px, y + 16], fill=(60, 60, 70), width=2)
        glow(d, px, y + 4, 8, (255, 240, 180))
        d.ellipse([px - 2, y + 2, px + 2, y + 6], fill=(255, 255, 230))
    # UCL banner.
    d.rectangle([x + w // 2 - 18, y + 4, x + w // 2 + 18, y + 14], fill=(40, 60, 140))
    f = lf('LiberationSans-Bold.ttf', 9)
    d.text((x + w // 2 - 9, y + 5), 'UCL', font=f, fill=(255, 255, 255))
    # Pitch.
    d.rectangle([x, y + 20, x + w, y + h], fill=(70, 150, 80))
    d.rectangle([x, y + 20, x + w, y + h], outline=(255, 255, 255))
    d.line([x + w // 2, y + 20, x + w // 2, y + h], fill=(255, 255, 255), width=1)
    d.ellipse([x + w // 2 - 12, y + 28, x + w // 2 + 12, y + 44], outline=(255, 255, 255), width=1)
    d.ellipse([x + w // 2 - 2, y + 34, x + w // 2 + 2, y + 38], fill=(255, 255, 255))
    # Two teams lining up.
    for tx in [x + 30, x + 52, x + 74]:
        person(d, tx, y + 46, 11, shirt=(255, 255, 255), pants=(30, 30, 40))
    for tx in [x + w - 30, x + w - 52, x + w - 74]:
        person(d, tx, y + 46, 11, shirt=(200, 40, 40), pants=(30, 30, 40))

def scene_gaza(d, x, y, w, h):
    # M10: Gaza street, daylight — concrete buildings with LIT windows, minaret,
    # ambulance, smoke. Lit windows + minaret make it read at thumbnail size.
    vgrad(d, x, y, x + w, y + h, (210, 230, 245), (240, 244, 250))
    sun(d, x + w - 16, y + 10, 7)
    # Concrete buildings, warm sand-grey, with lit (yellow) + dark windows.
    for bx, bw, bh in [(x + 4, 34, 26), (x + 42, 28, 34), (x + 74, 30, 22)]:
        d.rectangle([bx, y + h - bh - 8, bx + bw, y + h - 8], fill=(178, 168, 148), outline=(120, 112, 100))
        wi = 0
        for wy in range(y + h - bh - 5, y + h - 12, 8):
            for wx in range(bx + 4, bx + bw - 4, 9):
                col = (255, 222, 130) if wi % 3 != 2 else (70, 70, 70)
                d.rectangle([wx, wy, wx + 5, wy + 4], fill=col)
                wi += 1
    # Minaret, right: tall tower with pointed top + balcony.
    d.rectangle([x + 112, y + 6, x + 120, y + h - 8], fill=(200, 190, 165), outline=(130, 120, 105))
    d.polygon([(x + 111, y + 6), (x + 121, y + 6), (x + 116, y + 0)], fill=(164, 30, 26))
    d.rectangle([x + 110, y + 14, x + 122, y + 17], fill=(150, 140, 120))
    d.rectangle([x + 114, y + 20, x + 118, y + 26], fill=(255, 222, 130))
    smoke(d, x + 64, y + 2, 20, 14)
    smoke(d, x + 130, y + 0, 16, 12)
    # Rubble pile at the base of the middle building.
    d.polygon([(x + 44, y + h - 8), (x + 56, y + h - 16), (x + 68, y + h - 8)], fill=(140, 135, 125))
    d.polygon([(x + 52, y + h - 8), (x + 60, y + h - 13), (x + 66, y + h - 8)], fill=(160, 155, 145))
    # Road.
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(110, 110, 110))
    d.line([x, y + h - 4, x + w, y + h - 4], fill=(255, 255, 255), width=1)
    # Ambulance, white van + red cross, headlights on.
    d.rectangle([x + 118, y + h - 24, x + 168, y + h - 8], fill=(255, 255, 255), outline=(150, 150, 145))
    d.rectangle([x + 134, y + h - 22, x + 144, y + h - 12], fill=RED)
    d.rectangle([x + 138, y + h - 25, x + 140, y + h - 9], fill=RED)
    d.ellipse([x + 124, y + h - 9, x + 130, y + h - 3], fill=(30, 30, 30))
    d.ellipse([x + 158, y + h - 9, x + 164, y + h - 3], fill=(30, 30, 30))
    d.ellipse([x + 166, y + h - 20, x + 170, y + h - 16], fill=(255, 225, 140))
    person(d, x + 96, y + h - 8, 12, shirt=(200, 60, 40))
    person(d, x + 186, y + h - 8, 12, shirt=(60, 90, 160))

def scene_sputnik(d, x, y, w, h):
    # M11: Space — bright Earth below, satellite with gold panels, radiation symbol.
    vgrad(d, x, y, x + w, y + h, (70, 110, 170), (40, 70, 120))
    stars(d, x + 4, y + 2, x + w - 4, y + 22, n=10)
    # Earth, big blue circle at the bottom (clipped to the scene, never below y+h).
    d.ellipse([x + 20, y + 30, x + w - 20, y + h], fill=(60, 130, 200))
    d.ellipse([x + 46, y + 36, x + 110, y + h], fill=(70, 150, 80))
    d.ellipse([x + 120, y + 42, x + 170, y + h], fill=(70, 150, 80))
    d.arc([x + 30, y + 34, x + 90, y + 48], 200, 340, fill=(255, 255, 255), width=2)
    # Satellite with gold solar panels.
    d.rectangle([x + 78, y + 8, x + 118, y + 16], fill=(200, 170, 80), outline=(150, 120, 50))
    d.rectangle([x + 88, y + 16, x + 108, y + 26], fill=(180, 180, 185), outline=(120, 120, 125))
    d.rectangle([x + 118, y + 8, x + 140, y + 16], fill=(200, 170, 80), outline=(150, 120, 50))
    # Yellow radiation symbol.
    d.ellipse([x + 150, y + 6, x + 166, y + 22], fill=(252, 210, 65), outline=(180, 140, 30))
    d.ellipse([x + 156, y + 12, x + 160, y + 16], fill=(30, 30, 30))
    d.line([x + 158, y + 8, x + 158, y + 12], fill=(30, 30, 30), width=2)
    # Ground station dish at bottom.
    d.arc([x + 6, y + h - 16, x + 26, y + h - 2], 180, 360, fill=(200, 200, 195), width=2)
    d.line([x + 16, y + h - 6, x + 16, y + h - 2], fill=(120, 120, 115), width=2)

def scene_whitehouse(d, x, y, w, h):
    # M12: White House with podium, document stack, containers, US flag.
    # (No dome — the White House has none; detail comes from pediment, columns,
    # windows, roof flag, steps, trees and lawn instead.)
    vgrad(d, x, y, x + w, y + h, (205, 228, 242), (238, 242, 248))
    sun(d, x + 40, y + 10, 7)
    # US flag on a pole, right.
    d.line([x + w - 14, y + 4, x + w - 14, y + 30], fill=(70, 70, 70), width=1)
    for i in range(4):
        d.rectangle([x + w - 14, y + 4 + i * 4, x + w - 2, y + 4 + i * 4 + 2], fill=(200, 60, 50) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x + w - 14, y + 4, x + w - 8, y + 10], fill=(40, 60, 140))
    # Trees flanking the building, with bushes at their feet.
    for tx in [x + 44, x + 150]:
        d.rectangle([tx - 1, y + 26, tx + 1, y + h - 8], fill=(90, 60, 35))
        d.ellipse([tx - 7, y + 12, tx + 7, y + 26], fill=(60, 120, 60))
        d.ellipse([tx - 5, y + 8, tx + 5, y + 18], fill=(80, 150, 80))
        d.ellipse([tx - 8, y + h - 12, tx - 2, y + h - 6], fill=(70, 130, 70))
        d.ellipse([tx + 2, y + h - 12, tx + 8, y + h - 6], fill=(70, 130, 70))
    # White House: white block, columns, pediment with round window.
    d.rectangle([x + 56, y + 18, x + 140, y + h - 8], fill=(250, 250, 248), outline=(180, 175, 165))
    d.polygon([(x + 56, y + 18), (x + 140, y + 18), (x + 98, y + 8)], fill=(240, 240, 235), outline=(180, 175, 165))
    d.ellipse([x + 94, y + 12, x + 102, y + 17], fill=(205, 225, 240), outline=(180, 175, 165))
    # Small flag on the pediment peak.
    d.line([x + 98, y + 8, x + 98, y + 1], fill=(70, 70, 70), width=1)
    d.rectangle([x + 98, y + 1, x + 106, y + 5], fill=(200, 60, 50))
    for cx in [x + 64, x + 80, x + 96, x + 112, x + 128]:
        d.rectangle([cx, y + 22, cx + 4, y + h - 10], fill=(230, 230, 225), outline=(180, 175, 165))
    # Windows flanking the central door.
    for wx in [x + 66, x + 122]:
        d.rectangle([wx, y + 26, wx + 8, y + 34], fill=(205, 225, 240), outline=(150, 150, 145))
        d.line([wx + 4, y + 26, wx + 4, y + 34], fill=(150, 150, 145), width=1)
    d.rectangle([x + 92, y + 36, x + 104, y + h - 8], fill=(60, 60, 65))
    # Lawn first, then steps in front of the door (drawn after, so they stay visible).
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(120, 150, 100))
    for i, sy in enumerate([y + h - 8, y + h - 6, y + h - 4]):
        d.rectangle([x + 86 - i * 2, sy, x + 110 + i * 2, sy + 2], fill=(200, 195, 185))
    # Podium + speaker, left.
    d.rectangle([x + 14, y + 34, x + 36, y + h - 8], fill=(120, 80, 50))
    person(d, x + 25, y + 34, 12, shirt=(40, 40, 60))
    # Document stack "SECTION 301", right.
    d.rectangle([x + 152, y + 36, x + 184, y + h - 8], fill=(255, 255, 255), outline=(150, 150, 145))
    for ly in range(y + 40, y + h - 12, 4):
        d.line([x + 156, ly, x + 180, ly], fill=(120, 120, 115), width=1)

def scene_cas_day(d, x, y, w, h):
    # M13: Lausanne — grey court block, gavel, trophy, red/green flag.
    vgrad(d, x, y, x + w, y + h, (220, 225, 235), (205, 210, 220))
    sun(d, x + w - 16, y + 10, 7)
    # Court block.
    d.rectangle([x + 30, y + 12, x + w - 30, y + h - 8], fill=(180, 175, 165), outline=(130, 125, 115))
    d.rectangle([x + 30, y + 12, x + w - 30, y + 18], fill=(150, 145, 135))
    for wx in range(x + 36, x + w - 40, 14):
        d.rectangle([wx, y + 22, wx + 8, y + 30], fill=(230, 235, 240), outline=(120, 120, 115))
    d.rectangle([x + w // 2 - 8, y + 34, x + w // 2 + 8, y + h - 8], fill=(90, 80, 70))
    # Gavel + trophy.
    d.line([x + 44, y + 36, x + 62, y + 30], fill=(120, 85, 50), width=3)
    d.rectangle([x + 40, y + 28, x + 50, y + 36], fill=(120, 85, 50))
    d.polygon([(x + w - 66, y + 34), (x + w - 58, y + 34), (x + w - 62, y + 44), (x + w - 66, y + 44)], fill=GOLD)
    d.rectangle([x + w - 66, y + 44, x + w - 58, y + 44], fill=GOLD)
    # Senegal flag (green-yellow-red vertical) on a pole, right.
    d.line([x + w - 16, y + 6, x + w - 16, y + 30], fill=(70, 70, 70), width=1)
    d.rectangle([x + w - 16, y + 6, x + w - 10, y + 16], fill=(0, 130, 60))
    d.rectangle([x + w - 10, y + 6, x + w - 4, y + 16], fill=(252, 210, 65))
    d.rectangle([x + w - 4, y + 6, x + w + 2, y + 16], fill=(200, 40, 40))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(150, 145, 135))

# ---------- MAP ----------
POLYS = [
    [(60, 24), (95, 18), (130, 22), (160, 14), (195, 18), (215, 26), (200, 34), (170, 30), (140, 38), (110, 32), (80, 36), (55, 30)],
    [(48, 32), (58, 30), (64, 40), (56, 46), (46, 42)],
    [(120, 38), (132, 40), (128, 48), (116, 46)],
    [(148, 22), (168, 24), (172, 30), (152, 32)],
    [(178, 18), (196, 16), (200, 26), (186, 28)],
    [(28, 42), (40, 40), (44, 50), (36, 56), (26, 50)],
    [(200, 40), (214, 42), (212, 50), (198, 48)],
    [(216, 26), (232, 24), (238, 32), (224, 36)],
    [(240, 40), (252, 38), (256, 46), (244, 50)],
    [(250, 52), (262, 50), (266, 58), (254, 60)],
    [(286, 44), (296, 42), (300, 50), (290, 54)],
    [(150, 54), (168, 56), (166, 64), (148, 62)],
    [(168, 62), (186, 60), (190, 68), (172, 70)],
    [(186, 70), (200, 68), (202, 76), (188, 78)],
    [(150, 64), (164, 66), (162, 74), (148, 72)],
    [(216, 58), (230, 56), (234, 64), (220, 66)],
    [(230, 68), (244, 66), (248, 74), (234, 76)],
]
PINS = [
    (1, 'Tokyo', 139.7, 35.7), (2, 'Jeddah', 39.2, 21.5), (3, 'Brooklyn', -74.0, 40.7),
    (4, 'Kyiv', 30.5, 50.4), (5, 'Cikande', 106.3, -6.2), (6, 'Shanghai', 121.5, 31.2),
    (7, 'Honiara', 160.0, -9.6), (8, 'Dhaka', 90.4, 23.8), (9, 'Paris', 2.35, 48.85),
    (10, 'Gaza City', 34.5, 31.5), (11, 'Berlin', 13.4, 52.5),
    (12, 'Washington', -77.0, 38.9), (13, 'Lausanne', 6.6, 46.5),
]

def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (90.0 - lat) / 180.0 * mh
    return x, y

def _inside(px, py, poly):
    # Ray-casting point-in-polygon.
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def draw_map(d, mx, my, mw, mh):
    d.rectangle([mx, my, mx + mw, my + mh], fill=(190, 210, 225), outline=BORDER)
    d.line([mx, my + mh // 2, mx + mw, my + mh // 2], fill=(160, 180, 200), width=1)
    # Dotted landmasses (like the finalists): 3px grid, 2px dots.
    for poly in POLYS:
        pts = [(mx + p[0] / 310.0 * mw, my + p[1] / 84.0 * mh) for p in poly]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, x1 = int(min(xs)), int(max(xs))
        y0, y1 = int(min(ys)), int(max(ys))
        for gx in range(x0, x1 + 1, 3):
            for gy in range(y0, y1 + 1, 3):
                if _inside(gx, gy, pts):
                    d.rectangle([gx, gy, gx + 1, gy + 1], fill=(175, 168, 145))
    pts = {}
    for num, name, lon, lat in PINS:
        px, py = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        pts[num] = (px, py)
    # Fan out pins that collide (Jeddah/Gaza, Paris/Berlin/Lausanne).
    fan = {2: (-8, -2), 10: (9, 3), 9: (-11, 0), 11: (6, -5), 13: (1, 7)}
    for num in fan:
        if num in pts:
            px, py = pts[num]
            dx, dy = fan[num]
            pts[num] = (px + dx, py + dy)
    for num, name, lon, lat in PINS:
        px, py = pts[num]
        d.line([px, py, px, py - 10], fill=INK, width=1)
        d.ellipse([px - 2, py - 13, px + 2, py - 9], fill=RED, outline=(255, 255, 255))
        f = lf('LiberationSans-Bold.ttf', 7)
        tw = d.textlength(str(num), font=f)
        d.text((px - tw / 2, py - 20), str(num), font=f, fill=INK)
    return pts

# ---------- DATA ----------
STRIP = [
    ('96', 'DRONES', 'LAUNCHED'),
    ('73', 'DRONES', 'DOWNED'),
    ('10', 'HUAWEI COUNTS', 'GUILTY'),
    ('26', 'CIKANDE', 'DEAD'),
    ('$139', 'BANGLADESH', 'WAGE'),
    ('74', 'LASHES IN', 'IRAN'),
]
REGIONS = [
    ('EUROPE', 6, 185, (40, 80, 160)), ('ASIA', 6, 190, (40, 130, 130)), ('AFRICA', 7, 230, (60, 130, 70)),
    ('MIDDLE EAST', 4, 118, (164, 30, 26)), ('N. AMERICA', 4, 98, (200, 120, 30)),
    ('LATIN AMERICA', 1, 88, (110, 80, 150)), ('GLOBAL', 1, 99, (100, 100, 100)),
]
LEADS = [
    (1, scene_tokyo_red, 'REUTERS', 'WED \u00b7 REPORTED', 'TOKYO \u00b7 MARKETS \u00b7 WED',
     'Tokyo gives back the surge',
     'Nikkei morning close 56,710 (-1,934, -3.30%); Advantest -12%, SoftBank -13%; Kospi -6.0%, Taiex -8.2% at midday. (Reuters)'),
    (2, scene_jeddah, 'REUTERS', 'WED \u00b7 REPORTED', 'JEDDAH \u00b7 RED SEA \u00b7 WED',
     'Houthis threaten Saudi ports',
     'Jeddah and all Saudi Red Sea ports targeted if Riyadh hits Hodeidah; coalition strikes Hodeidah, Saada, Amran; Brent $90.97. (Reuters)'),
    (3, scene_courtroom, 'DOJ', 'TUE \u00b7 CONFIRMED', 'BROOKLYN \u00b7 COURTS \u00b7 TUE',
     'Huawei guilty on 10 counts',
     'Convicted of bank fraud, wire fraud, Iran sanctions, money laundering, trade-secret theft; sentencing 14 Sep 2027. (DOJ, Reuters)'),
]
MEDIUMS = [
    (scene_drones_day, 'UKR AF', 'TUE \u00b7 REPORTED', 'DRONES', 'KYIV',
     '96 drones, 73 downed', 'Odesa 2 killed; Dymer toll 12'),
    (scene_factory_day, 'XINHUA', 'TUE \u00b7 CONFIRMED', 'FIRE', 'CIKANDE',
     '26 dead, 28 missing', 'Probe now criminal'),
    (scene_shanghai, 'REUTERS', 'TUE \u00b7 REPORTED', 'PROBE', 'SHANGHAI',
     'Shanghai chief probed', '4th Politburo member probed'),
    (scene_solomon, 'REUTERS', 'WED \u00b7 CONFIRMED', 'PACT', 'HONIARA',
     'Canberra wins Solomons pact', 'Canberra is defence partner'),
    (scene_garment, 'REUTERS', 'WED \u00b7 CONFIRMED', 'WAGE', 'DHAKA',
     'Garment wage +36% to $139', 'Smallest rise in a decade'),
    (scene_ucl, 'UEFA', 'WED \u00b7 FIXTURES', '', 'EUROPE',
     'Nine more UCL ties tonight', 'Liverpool, Bayern, PSG play'),
    (scene_gaza, 'REUTERS', 'TUE \u00b7 REPORTED', 'GAZA', 'GAZA CITY',
     'Hamas security chief killed', '7 killed Tuesday in Gaza'),
    (scene_sputnik, 'WDR', 'MON \u00b7 REPORTED', 'SPACE', 'BERLIN',
     "Intel: Russia's nuke satellite", 'Could launch within 60 days'),
    (scene_whitehouse, 'REUTERS', 'TUE \u00b7 REPORTED', 'TARIFFS', 'WASHINGTON',
     'New US tariffs imminent', 'Section 301 probe: 16 partners'),
    (scene_cas_day, 'REUTERS', 'TUE \u00b7 CONFIRMED', 'CAS', 'LAUSANNE',
     'CAS hands Senegal AFCON crown', 'Senegal 1-0 Morocco, 18 Jan'),
]
BRIEFS = [
    (14, 'EU\u2013Indonesia trade deal', 'RTR', 'SAT'),
    (15, 'EU eyes 3% tax on Big Tech', '', 'SAT'),
    (16, 'Iran flogs singer 74\u00d7', 'CNN', 'MON'),
    (17, 'Dragon splashes down', 'NASA', 'SAT'),
    (18, 'Mexico nabs Sinaloa chief', 'AP', 'SAT'),
    (19, 'Ebola doubles in Congo', '', '17 NOV'),
    (20, 'Ghana win amputee World Cup', '', 'SUN'),
    (21, 'Ethiopia polio drive: 11M kids', '', 'SAT'),
    (22, 'Nigeria settles \u20a61.23trn debt', '', 'MON'),
    (23, 'Gambia stops 491 migrants', '', 'FRI'),
    (24, 'UCL Tue: Madrid 5-1 PSV', 'UEFA', 'TUE'),
    (25, 'Congo Cessna: rebels claim kill', '', 'SUN'),
    (26, 'NATO AWACS to Poland', 'RTR', 'MON'),
    (27, 'Anthropic below $83 IPO price', '', 'TUE'),
    (28, 'Trump warns Iran of new strikes', '', 'MON'),
    (29, 'COP31: no pact, COP32 Addis', '', 'SUN'),
]
DATE_CHECK_BODY = (
    "Every story on this page happened or was first reported 17\u201325 November 2026, each carrying its day tag. "
    "Left out because they happened before 17 November: UN warns of a 'security vacuum' as Blue Helmets leave "
    "Lebanon and Western Sahara (UN briefing, 4 Nov) \u00b7 1M Afghan children face deadly malnutrition (UNICEF, 25 Aug) "
    "\u00b7 COP31 opened in Antalya (9 Nov). "
    "Wednesday's UCL results are not in \u2014 the nine ties kick off tonight; results come in round 2."
)
DATE_CHECK_FOOTER = (
    "Sources: Reuters \u00b7 AP \u00b7 UEFA.com \u00b7 Xinhua \u00b7 BBC \u00b7 CNN \u00b7 DOJ \u00b7 UN News \u00b7 "
    "CONFIRMED = verified \u00b7 OFFICIAL = authority \u00b7 REPORTED = as reported \u00b7 CLAIM = unverified \u00b7 "
    "TAGS: SAT 21 \u00b7 SUN 22 \u00b7 MON 23 \u00b7 TUE 24 \u00b7 WED 25 \u00b7 17 NOV"
)
TIMELINE = [
    'WED 25 NOV 00:46 UTC \u00b7 Drone hits Kyiv courtyard \u00b7 02:30 UTC \u00b7 Nikkei morning close 56,710 (-3.30%)',
    '08:00 UTC \u00b7 Ukraine AF: 73 of 96 drones downed \u00b7 WED 25 NOV \u00b7 Canberra wins Solomons pact; Dhaka lifts wage to $139',
    '13:30 GMT \u00b7 US core PCE + Q3 GDP due \u00b7 17:45 GMT \u00b7 UCL: Sabah\u2013Barcelona, Slavia\u2013Villarreal \u00b7 20:00 GMT \u00b7 seven more ties',
]

def chip_w(d, text, size):
    f = lf('LiberationSans-Bold.ttf', size)
    return d.textlength(text, font=f) + 12

def status_bg(status):
    if 'CONFIRMED' in status:
        return (60, 110, 60)
    if 'FIXTURES' in status:
        return (40, 60, 140)
    return (140, 90, 30)

def headline_lines(d, text, sizes, max_w):
    for s in sizes:
        f = lf('LiberationSerif-Bold.ttf', s)
        lines = textwrap(d, text, f, max_w)
        if len(lines) <= 2:
            return f, lines
    f = lf('LiberationSerif-Bold.ttf', sizes[-1])
    return f, textwrap(d, text, f, max_w)

# ---------- CANVAS ----------
img = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(img)
for _ in range(2600):
    x = random.randint(0, W - 1); y = random.randint(0, H - 1)
    d.point((x, y), fill=(232, 226, 212))

# Kicker row.
d.text((8, 8), 'THE WORLD IN ONE DAY', font=lf('LiberationSerif-Bold.ttf', 13), fill=INK)
f = lf('LiberationSerif-Bold.ttf', 13)
cnt = '29 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED'
d.text((1016 - d.textlength(cnt, font=f), 8), cnt, font=f, fill=INK)

# Masthead: title case. Measured 25 Nov 11:35 WIB — LiberationSerif-Bold caps at
# 76px (993px); NotoSerif-ExtraCondensedBold reaches 80px untracked (996px) and
# 84px with -2px tracking (~1000px <= 1008). Taller glyphs = more dominant
# masthead; condensed face is a standard newspaper display choice.
title = 'Wednesday 25 November 2026'
tf = nf('NotoSerif-ExtraCondensedBold.ttf', 84)
tsize = 84
tw = tracked_width(d, title, tf, -2)
if tw > 1008:
    sys.exit('MASTHEAD OVERFLOW: %d > 1008' % tw)
draw_tracked(d, 8, 26, title, tf, -2, INK)
deck = 'Tokyo gives back the surge \u00b7 Houthis threaten Jeddah \u00b7 Huawei guilty on 10 counts'
df, dsize = fit_font(d, deck, 'LiberationSerif-Italic.ttf', [22, 20, 18, 16], 1008)
d.text((8, 116), deck, font=df, fill=RED)
d.line([8, 144, 1016, 144], fill=INK, width=2)

# Strip of 6 numbers.
sy = 144
for i, (num, l1, l2) in enumerate(STRIP):
    cx = 8 + i * 168
    if i > 0:
        d.line([cx, sy + 6, cx, sy + 74], fill=BORDER, width=1)
    d.text((cx + 8, sy + 4), num, font=lf('LiberationSerif-Bold.ttf', 48), fill=RED)
    f12 = lf('LiberationSans-Bold.ttf', 12)
    assert_fit(d, l1, f12, 160, 'strip l1 %r' % l1)
    assert_fit(d, l2, f12, 160, 'strip l2 %r' % l2)
    d.text((cx + 8, sy + 56), l1, font=f12, fill=INK)
    d.text((cx + 8, sy + 70), l2, font=f12, fill=INK)
d.line([8, 224, 1016, 224], fill=INK, width=1)

# Region strip, coloured segments like the finalists.
rx = 8
for name, n, wseg, col in REGIONS:
    d.rectangle([rx, 224, rx + wseg, 252], fill=col)
    lab = '%s %d' % (name, n)
    for s in [13, 12, 11, 10, 9]:
        f = lf('LiberationSans-Bold.ttf', s)
        if d.textlength(lab, font=f) <= wseg - 4:
            break
    assert_fit(d, lab, f, wseg - 4, 'region %r' % lab)
    d.text((rx + (wseg - d.textlength(lab, font=f)) / 2, 232), lab, font=f, fill=(255, 255, 255))
    d.line([rx + wseg, 224, rx + wseg, 252], fill=(255, 255, 255), width=1)
    rx += wseg
assert rx == 1016, 'region widths sum %d != 1016' % rx
assert sum(n for _, n, _, _ in REGIONS) == 29, 'region counts != 29'
d.line([8, 252, 1016, 252], fill=INK, width=1)

# Timeline, 3 rows.
d.text((8, 258), 'THE DAY IN UTC', font=lf('LiberationSans-Bold.ttf', 11), fill=RED)
lab_w = d.textlength('THE DAY IN UTC', font=lf('LiberationSans-Bold.ttf', 11))
for i, row in enumerate(TIMELINE):
    f11 = lf('LiberationSans-Bold.ttf', 11)
    assert_fit(d, row, f11, 1016 - 8 - lab_w - 12, 'timeline row %d' % i)
    d.text((8 + lab_w + 12, 256 + i * 14), row, font=f11, fill=INK)
d.line([8, 296, 1016, 296], fill=INK, width=1)

# Leads, 3 cards.
for i, (num, fn, src, status, dateline, headline, decktxt) in enumerate(LEADS):
    x = 8 + i * 340
    y = 296
    d.rectangle([x, y, x + 328, y + 262], fill=(255, 255, 255), outline=BORDER)
    fn(d, x + 2, y + 2, 326, 106)
    d.rectangle([x + 2, y + 2, x + 328, y + 108], outline=BORDER)
    # Source chip, top-right of the scene.
    sw = chip_w(d, src, 11)
    tag_chip(d, x + 2 + 326 - 6 - sw, y + 2 + 6, src, bg=INK, size=11)
    # Dateline + status chip (assert they do not collide).
    df13 = lf('LiberationSans-Bold.ttf', 13)
    stw = chip_w(d, status, 11)
    if d.textlength(dateline, font=df13) + stw + 12 > 316:
        sys.exit('LEAD DATELINE OVERFLOW %r + %r' % (dateline, status))
    d.text((x + 6, y + 112), dateline, font=df13, fill=INK)
    tag_chip(d, x + 328 - 6 - stw, y + 112, status, bg=status_bg(status), size=11)
    # Headline, largest size that wraps to <=2 lines.
    hf, hlines = headline_lines(d, headline, [28, 26, 24], 316)
    if len(hlines) > 2:
        sys.exit('LEAD HEADLINE %d lines: %r' % (len(hlines), headline))
    hy = y + 132
    for ln in hlines:
        d.text((x + 6, hy), ln, font=hf, fill=INK)
        hy += 30
    # Deck, <=3 lines.
    df2 = lf('LiberationSerif-Regular.ttf', 13)
    dlines = textwrap(d, decktxt, df2, 316)
    if len(dlines) > 3:
        sys.exit('LEAD DECK %d lines: %r' % (len(dlines), decktxt))
    dy = y + 132 + len(hlines) * 30 + 4
    for ln in dlines:
        d.text((x + 6, dy), ln, font=df2, fill=INK)
        dy += 16
    # Number chip, bottom-right of the scene (top-left would cover scene titles).
    nw = chip_w(d, str(num), 11)
    tag_chip(d, x + 2 + 326 - 6 - nw, y + 2 + 106 - 22, str(num), bg=RED, size=11)

# Mediums, 2 rows x 5.
for i, (fn, src, status, banner, dateline, headline, sub) in enumerate(MEDIUMS):
    row, col = divmod(i, 5)
    x = 8 + col * 201
    y = 558 + row * 118
    d.rectangle([x, y, x + 197, y + 118], fill=(255, 255, 255), outline=BORDER)
    fn(d, x + 2, y + 2, 193, 48)
    d.rectangle([x + 2, y + 2, x + 195, y + 50], outline=BORDER)
    if banner:
        tag_chip(d, x + 6, y + 6, banner, bg=INK, size=9)
    # Dateline + status chip (assert they do not collide).
    df9 = lf('LiberationSans-Bold.ttf', 9)
    stw = chip_w(d, status, 8)
    if d.textlength(dateline, font=df9) + stw + 8 > 189:
        sys.exit('MEDIUM DATELINE OVERFLOW %r + %r' % (dateline, status))
    d.text((x + 4, y + 54), dateline, font=df9, fill=INK)
    tag_chip(d, x + 197 - 4 - stw, y + 54, status, bg=status_bg(status), size=8)
    # Headline, largest size that wraps to <=2 lines.
    hf, hlines = headline_lines(d, headline, [18, 17, 16], 189)
    if len(hlines) > 2:
        sys.exit('MEDIUM HEADLINE %d lines: %r' % (len(hlines), headline))
    hy = y + 68
    for ln in hlines:
        d.text((x + 4, hy), ln, font=hf, fill=INK)
        hy += 17
    # Sub, one line.
    sf = lf('LiberationSans-Regular.ttf', 13)
    assert_fit(d, sub, sf, 189, 'medium sub %r' % sub)
    d.text((x + 4, y + 104), sub, font=sf, fill=INK)

# Map + briefs.
d.text((8, 796), 'WHERE IT HAPPENED \u2014 PINS 1\u201313', font=lf('LiberationSans-Bold.ttf', 10), fill=INK)
draw_map(d, 8, 808, 322, 96)
pin_lines = [
    '1 Tokyo \u00b7 2 Jeddah \u00b7 3 Brooklyn \u00b7 4 Kyiv \u00b7 5 Cikande \u00b7 6 Shanghai',
    '7 Honiara \u00b7 8 Dhaka \u00b7 9 Paris \u00b7 10 Gaza City \u00b7 11 Berlin',
    '12 Washington \u00b7 13 Lausanne',
]
for i, ln in enumerate(pin_lines):
    f9 = lf('LiberationSans-Regular.ttf', 9)
    assert_fit(d, ln, f9, 318, 'pin line %d' % i)
    d.text((10, 908 + i * 12), ln, font=f9, fill=INK)

d.text((338, 796), 'ALSO ON \u2014 16 BRIEFS', font=lf('LiberationSans-Bold.ttf', 10), fill=INK)
for i, (num, text, src, tag) in enumerate(BRIEFS):
    col, r = divmod(i, 6)
    cx = 338 + col * 228
    by = 814 + r * 13
    if col == 1 and r >= 4:
        by += 13
    full = text + (' (%s, %s)' % (src, tag) if src else ' (%s)' % tag)
    f11 = lf('LiberationSans-Regular.ttf', 11)
    assert_fit(d, full, f11, 194, 'brief %d %r' % (num, full))
    d.text((cx, by), str(num), font=lf('LiberationSans-Bold.ttf', 11), fill=RED)
    d.text((cx + 22, by), full, font=f11, fill=INK)
# Deck line under brief 24 (col 1, row 3).
d.text((338 + 228 + 22, 814 + 3 * 13 + 13), 'Arsenal 1-1 \u00b7 City 2-2 \u00b7 Leipzig 3-1',
       font=lf('LiberationSans-Regular.ttf', 10), fill=INK)

# DATE CHECK.
d.rectangle([8, 948, 1016, 1022], outline=RED, width=2)
d.text((16, 952), 'DATE CHECK \u2014 EVERY STORY ON THIS PAGE', font=lf('LiberationSans-Bold.ttf', 12), fill=RED)
bf = lf('LiberationSans-Regular.ttf', 12)
blines = textwrap(d, DATE_CHECK_BODY, bf, 1000)
if len(blines) > 3:
    sys.exit('DATE CHECK %d lines' % len(blines))
by = 968
for ln in blines:
    d.text((16, by), ln, font=bf, fill=INK)
    by += 12
ff, fsize = fit_font(d, DATE_CHECK_FOOTER, 'LiberationSans-Bold.ttf', [12, 11, 10, 9, 8], 1000)
d.text((16, 1008), DATE_CHECK_FOOTER, font=ff, fill=INK)

img.save('entry.png')
print('OK entry.png %dx%d masthead %dpx footer %dpx' % (W, H, tsize, fsize))
print('regions sum %d briefs %d leads %d mediums %d' % (
    sum(n for _, n, _, _ in REGIONS), len(BRIEFS), len(LEADS), len(MEDIUMS)))
