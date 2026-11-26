#!/usr/bin/env python3
"""News 25 edge revision — one-day broadsheet, drawn from scratch with PIL.

Wednesday 25 November 2026, 34 verified stories. One dominant idea: the three
lead scenes form ONE connected triptych band — a single continuous illustration
spanning the lead row, dawn-to-dusk left to right, one shared horizon.
Deterministic: no randomness, no timestamps, no network.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 222)
INK = (26, 26, 26)
RED = (179, 35, 27)
NAVY = (14, 30, 58)
NAVY2 = (20, 44, 84)
GOLD = (214, 164, 60)
TEAL = (18, 110, 110)
GREEN = (34, 110, 60)
CREAM = (247, 241, 222)
WHITE = (255, 255, 255)
DARK = (20, 20, 20)

F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_NOTO_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
F_NOTO_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
F_SANS_I = "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf"
F_DEJA = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_DEJA_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        try:
            _cache[key] = ImageFont.truetype(path, size)
        except OSError:
            _cache[key] = ImageFont.truetype(F_DEJA, size)
    return _cache[key]


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines that each fit max_w."""
    words = s.split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def fit_lines(draw, s, f, max_w, max_lines, min_size=8):
    """Wrap text; shrink font until it fits in max_lines. Returns (lines, font)."""
    size = f.size
    while size >= min_size:
        ff = font(f.path, size) if hasattr(f, "path") else f
        lines = wrap(draw, s, ff, max_w)
        if len(lines) <= max_lines:
            return lines, ff
        size -= 1
    ff = font(f.path, min_size) if hasattr(f, "path") else f
    return wrap(draw, s, ff, max_w)[:max_lines], ff


def draw_wrapped(draw, x, y, lines, f, fill, leading=None, align="left", width=None):
    """Draw lines; returns y after the last line."""
    lh = leading if leading is not None else int(f.size * 1.18)
    for ln in lines:
        if align == "center" and width is not None:
            lx = x + (width - draw.textlength(ln, font=f)) / 2
        elif align == "right" and width is not None:
            lx = x + width - draw.textlength(ln, font=f)
        else:
            lx = x
        draw.text((lx, y), ln, font=f, fill=fill)
        y += lh
    return y


def chip(draw, x, y, label, bg, fg=WHITE, size=8, pad_x=4, h=12):
    f = font(F_SANS_B, size)
    w = int(draw.textlength(label, font=f)) + pad_x * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    draw.text((x + pad_x, y + 1), label, font=f, fill=fg)
    return w


CHIP_COLORS = {"CONFIRMED": (34, 110, 60), "OFFICIAL": (30, 70, 140),
               "REPORTED": (179, 35, 27), "CLAIM": (200, 110, 20)}


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- data
KPI = [
    ("-6.2%", "KOSPI (L1)"),
    ("145", "DRONES DOWNED, SAMARA (L2)"),
    ("$93.60", "BRENT, +2.4% (L3)"),
    ("+4.9%", "AUSTRALIA CPI (M10)"),
    ("+36%", "BANGLADESH WAGE (M11)"),
    ("\u00a32,166", "UK ENERGY CAP (M13)"),
]

REGIONS = [("ASIA", 6, (180, 90, 40)), ("EUROPE", 6, (40, 90, 160)),
           ("MIDDLE EAST", 4, (200, 60, 60)), ("AFRICA", 6, (60, 140, 60)),
           ("AMERICAS", 8, (160, 40, 120)), ("OCEANIA", 4, (30, 130, 130))]

FIELDS = [("War", 8), ("Disaster", 4), ("Justice", 3), ("Diplomacy", 3),
          ("Security", 2), ("Tech", 2), ("Markets", 1), ("Economy", 1),
          ("Labour", 1), ("Space", 1), ("Energy", 1), ("Sport", 1),
          ("Culture", 1), ("Rights", 1), ("Society", 1), ("Crime", 1),
          ("Trade", 1), ("Health", 1)]

TIMELINE = [
    ("00:18", "Shenzhou-24 lifts off"),
    ("01:38", "M5.9 quake, Balleny Is."),
    ("03:56", "Shenzhou-24 docks"),
    ("08:47", "M5.5 quake off Taiwan"),
    ("15:00", "5t explosives, Iowa"),
    ("18:15", "EU-Balkans press conf."),
]

LEADS = [
    dict(num="L1", tag="WED \u00b7 ASIA", chip="REPORTED",
         head="Asia's chip rout",
         deck="Kospi minus 6.2 percent as AI doubts hit chip stocks; Nikkei minus 2.78 percent, Taiex minus 4.8 percent.",
         wim="Investors doubt the AI spending boom will pay off."),
    dict(num="L2", tag="WED \u00b7 EUROPE", chip="REPORTED",
         head="Drones hit two Volga refineries",
         deck="Syzran and Kuibyshev ablaze overnight; 1 killed; Russia says 145 drones downed over Samara.",
         wim="Ukraine's drone war now reaches Russia's Volga oil heartland."),
    dict(num="L3", tag="WED \u00b7 MIDDLE EAST", chip="REPORTED",
         head="Two tankers ablaze in Hormuz",
         deck="Mines strike ships in the strait; six tankers hit since Tuesday; Brent jumps 2.4 percent to 93.60 dollars.",
         wim="Six tankers mined in two days \u2014 Brent jumps 2.4 percent."),
]

MEDIUMS = [
    dict(num="M4", tag="WED", chip="CONFIRMED",
         head="Solomons pick Canberra",
         deck="Treaty names Australia primary security partner; no foreign base; China deal left behind."),
    dict(num="M5", tag="WED", chip="REPORTED",
         head="Houthis claim refinery hit",
         deck="Ras Tanura, 550,000 barrels per day: coalition downs 4 drones; strike unconfirmed; oil jumps."),
    dict(num="M6", tag="WED", chip="REPORTED",
         head="Gaza strike kills Hamas security chief",
         deck="Abu al-Ouf, 47, his wife and two daughters die at dawn in Shati camp."),
    dict(num="M7", tag="WED", chip="CONFIRMED",
         head="Judges: drop Netanyahu bribery charge",
         deck="Court doubts Case 4000 evidence; Case 2000 may not be a crime; no ruling yet."),
    dict(num="M8", tag="WED", chip="REPORTED",
         head="Russia hits Ukraine's grid again",
         deck="Power out in five regions; DTEK plant halted; Zaporizhzhia nuclear plant on backup \u2014 17th time this year."),
    dict(num="M9", tag="WED", chip="REPORTED",
         head="Fighting traps Ebola teams",
         deck="WHO pulls staff from Ituri hospital under fire; 5,775 dead in outbreak."),
    dict(num="M10", tag="WED", chip="OFFICIAL",
         head="Australia inflation jumps to 4.9 percent",
         deck="CPI up from 4.3 percent; trimmed mean 3.8 percent; monthly plus 0.5 percent."),
    dict(num="M11", tag="WED", chip="CONFIRMED",
         head="Bangladesh garment wage plus 36 percent",
         deck="17,000 taka (139 dollars) from 1 Dec; smallest rise in a decade; 4 to 2 vote."),
    dict(num="M12", tag="WED", chip="CONFIRMED",
         head="Pakistan's first astronaut reaches Tiangong",
         deck="Shenzhou-24 docks 3.5 hours after launch; Zeeshan Ali, 40, first foreigner aboard."),
    dict(num="M13", tag="WED", chip="OFFICIAL",
         head="UK energy bills up 26 percent",
         deck="Price cap 2,166 pounds from January; plus 443 pounds a year; about 20 million households hit."),
]

# (number, headline, chip)
BRIEFS = [
    ("14", "CIA\u2013ODNI breached \u2014 no classified data taken", "REPORTED"),
    ("15", "5 tons of explosives detonated in Iowa", "REPORTED"),
    ("16", "M5.9 quake near Balleny Islands", "OFFICIAL"),
    ("17", "Met still institutionally racist, review finds", "REPORTED"),
    ("18", "EU hosts six Balkan leaders in Brussels", "OFFICIAL"),
    ("19", "Morocco vows to appeal CAS ruling", "REPORTED"),
    ("20", "Nollywood legend Pete Edochie dies, 79", "CONFIRMED"),
    ("21", "47,000 women killed by partners in 2025 \u2014 UN", "OFFICIAL"),
    ("22", "81.5m Americans travel for Thanksgiving", "REPORTED"),
    ("23", "Abrego Garcia lands in Spain", "REPORTED"),
    ("24", "19 killed in RSF drone strikes in Sudan", "REPORTED"),
    ("25", "Congo plane missing; rebels claim shoot-down", "CLAIM"),
    ("26", "Colombia frees all hostages in supermarket siege", "REPORTED"),
    ("27", "6 dead, ~20 trapped in Indonesia mine flood", "REPORTED"),
    ("28", "Libya vows revenge for naval officers' deaths", "REPORTED"),
    ("29", "Poland seeks permanent US base", "REPORTED"),
    ("30", "Dell revenue doubles on AI servers", "REPORTED"),
    ("31", "N. Korea expels Swiss diplomat", "REPORTED"),
    ("32", "US readies tariffs on China, EU", "REPORTED"),
    ("33", "Australia passes online safety law", "REPORTED"),
    ("34", "M5.5 quake off Taiwan's east coast", "OFFICIAL"),
]

DATE_CHECK = ("Every story on this page happened, was first reported, or was still "
    "developing on Wednesday 25 November 2026. Wires to 19:00 UTC. Left out because "
    "they happened earlier: Huawei convicted in Brooklyn (Tue 24); CAS gives AFCON "
    "title back to Senegal (Tue 24); Trump pardons turkeys Freedom and Feathers "
    "(Tue 24); Houthi drone hits Riyadh PIF Tower, 11 hurt (Tue 24); US consumer "
    "confidence 103.3 (Tue 24); Microsoft \u2018Code Red\u2019 memos (Tue 24); "
    "Pentagon scolds Canada (Mon 23); UK sanctions Houthis (Tue 24); Emir of Daura "
    "suspended (Tue 24); Sooryavanshi 204 off 53 (Tue 24); UK heat deaths 5,258 "
    "(Tue 24); Dow closes above 50,000 (Tue 24); WHO chief\u2019s Cuba fuel-blockade "
    "call (Tue 24); Ethiopia polio drive (Sat 21); Ghana vaccine labs (18 Nov); "
    "Colombia 7.4 quake (Aug); Venezuela debt framework (Tue 24).")

SOURCES = ("Sources: Reuters, AP, BBC, CNN, AFP, Ofgem, ABS, UN Women, UNODC, USGS, "
    "Xinhua, CMSA, EC, Consilium, NYT, Radio Nigeria, CWA, TaiwanPlus, AAA, OneTurn. "
    "Every drawing original.")

# map pins: (number, lat, lon)
PINS = [("L1", 37.57, 126.98), ("L2", 53.20, 50.15), ("L3", 26.50, 56.30),
        ("M4", -35.28, 149.13), ("M5", 26.65, 50.10), ("M6", 31.50, 34.47),
        ("M7", 31.77, 35.21), ("M8", 50.45, 30.52), ("M9", 1.70, 30.00),
        ("M10", -33.87, 151.21), ("M11", 23.81, 90.41), ("M12", 39.73, 98.52),
        ("M13", 51.51, -0.13)]


# ---------------------------------------------------------------- scenes
def draw_triptych(d, img, x, y, w, h):
    """One continuous dawn-to-dusk band across the lead row.

    Sky gradient flows left to right: bright morning (L1) -> dark night (L2)
    -> orange dusk (L3). One thin continuous horizon line runs the whole width.
    Thin cream dividers split panels; smoke and drones cross them.
    """
    band = Image.new("RGB", (w, h))
    bd = ImageDraw.Draw(band)
    ox, oy = x, y
    x, y = 0, 0  # band-local coordinates from here on; pasted at (ox, oy)
    # sky: piecewise gradient stops (x fraction, color)
    stops = [(0.00, (245, 216, 150)), (0.26, (250, 198, 110)),
             (0.36, (16, 32, 62)), (0.60, (13, 27, 54)),
             (0.70, (198, 108, 48)), (1.00, (230, 128, 44))]
    for px in range(w):
        t = px / max(1, w - 1)
        c = stops[0][1]
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                c = lerp(c0, c1, f)
                break
        bd.line([(px, 0), (px, h)], fill=c)
    # stars in the night third
    stars = [(0.38, 0.10), (0.42, 0.22), (0.46, 0.08), (0.50, 0.16),
             (0.54, 0.06), (0.58, 0.20), (0.44, 0.30), (0.56, 0.32),
             (0.36, 0.28), (0.62, 0.12)]
    for sx, sy in stars:
        r = 2
        cx, cy = int(sx * w), int(sy * h)
        bd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 250, 220))
    # ground and water: one thin continuous horizon line, per-panel ground
    x1 = w // 3
    x2 = 2 * w // 3
    # L1: trading-floor / street slate; L2: Volga water, dark navy;
    # L3: Hormuz water, dark orange-brown
    bd.rectangle([x, y + 92, x + x1, y + h], fill=(52, 56, 66))
    bd.rectangle([x + x1, y + 92, x + x2, y + h], fill=(10, 18, 34))
    bd.rectangle([x + x2, y + 92, x + w, y + h], fill=(64, 34, 20))
    bd.line([x, y + 92, x + w, y + 92], fill=(16, 16, 22), width=2)
    # --- L1: trading floor + skyline (left third) ---
    x1 = w // 3
    # red board
    bd.rectangle([x + 14, y + 10, x + x1 - 90, y + 52], fill=(179, 35, 27))
    bd.text((x + 22, y + 14), "-6.2%", font=font(F_SANS_B, 26), fill=WHITE)
    bd.text((x + 22, y + 40), "KOSPI", font=font(F_SANS_B, 9), fill=(255, 220, 200))
    # candlestick chart, falling left to right
    cx0, cy0 = x + 16, y + 62
    candles = [(0, 0, 8, 14), (14, 6, 8, 10), (28, 12, 8, 12), (42, 20, 8, 9),
               (56, 26, 8, 11), (70, 34, 8, 8), (84, 40, 8, 10), (98, 46, 8, 9)]
    for dx, dy, cw, ch in candles:
        bd.rectangle([cx0 + dx, cy0 + dy, cx0 + dx + cw, cy0 + dy + ch],
                     fill=(200, 40, 30))
        bd.line([cx0 + dx + cw // 2, cy0 + dy - 5, cx0 + dx + cw // 2,
                 cy0 + dy + ch + 5], fill=(200, 40, 30), width=1)
    bd.line([(cx0, cy0 - 2), (cx0 + 108, cy0 + 28)], fill=(120, 20, 16), width=2)
    # skyline + fab silhouette on the horizon, standing on the ground line
    for bx, bw, bh in [(x + 130, 22, 26), (x + 156, 16, 34), (x + 176, 26, 20),
                       (x + 206, 14, 30), (x + 224, 20, 24), (x + 248, 18, 28)]:
        bd.rectangle([bx, y + 92 - bh, bx + bw, y + 92], fill=(40, 52, 84))
    # three traders pointing at the board, standing on the ground
    # (skin heads + white shirts read against the bright morning sky)
    for tx in (x + 262, x + 282, x + 300):
        bd.ellipse([tx, y + 60, tx + 9, y + 69], fill=(232, 190, 150))
        bd.polygon([(tx + 1, y + 70), (tx + 8, y + 70), (tx + 10, y + 92),
                    (tx - 1, y + 92)], fill=(30, 32, 40))
        bd.rectangle([tx + 2, y + 72, tx + 7, y + 86], fill=WHITE)
        bd.line([(tx + 8, y + 76), (tx + 20, y + 64)], fill=(30, 32, 40), width=2)
    # --- L2: night refineries (middle third) ---
    x2 = 2 * w // 3
    # refinery towers, standing on the waterline, lit windows
    for tx, th in [(x + x1 + 26, 44), (x + x1 + 118, 52)]:
        top = y + 92 - th
        bd.rectangle([tx, top, tx + 34, y + 92], fill=(52, 52, 66))
        bd.rectangle([tx + 8, top - 12, tx + 26, top], fill=(52, 52, 66))
        for wy in range(top + 8, y + 88, 12):
            bd.rectangle([tx + 4, wy, tx + 8, wy + 4], fill=(255, 200, 90))
            bd.rectangle([tx + 22, wy, tx + 26, wy + 4], fill=(255, 200, 90))
        # fireball on top, with glow
        fx, fy = tx + 17, top - 20
        bd.ellipse([fx - 13, fy - 13, fx + 13, fy + 13], fill=(255, 140, 30))
        bd.ellipse([fx - 8, fy - 8, fx + 8, fy + 8], fill=(255, 210, 90))
        # smoke drifting up-right from the fireball
        for k, (sx, sy, sr) in enumerate([(16, -6, 7), (26, -14, 8), (34, -22, 9)]):
            bd.ellipse([fx + sx - sr, fy + sy - sr, fx + sx + sr, fy + sy + sr],
                       fill=(80, 80, 95))
    # water reflection streaks
    for i, rx in enumerate(range(x1 + 20, x2 - 20, 26)):
        bd.rectangle([x + rx, y + h - 26 + (i % 2) * 8, x + rx + 16,
                      y + h - 23 + (i % 2) * 8], fill=(255, 140, 40))
    # drones
    for dx, dy in [(x + x1 + 70, y + 26), (x + x1 + 150, y + 18),
                   (x + x1 + 200, y + 34)]:
        bd.ellipse([dx - 4, dy - 3, dx + 4, dy + 3], fill=(10, 10, 14))
        bd.line([dx - 9, dy - 5, dx + 9, dy - 5], fill=(200, 200, 200), width=1)
        bd.line([dx - 9, dy + 5, dx + 9, dy + 5], fill=(200, 200, 200), width=1)
    # --- L3: dusk tankers (right third) ---
    # sun disc
    sx, sy = x + x2 + 150, y + 30
    bd.ellipse([sx - 20, sy - 20, sx + 20, sy + 20], fill=(255, 190, 80))
    # cliffs both sides, down to the bottom of the band
    bd.polygon([(x + x2 + 4, y + h), (x + x2 + 4, y + 66),
                (x + x2 + 52, y + h)], fill=(30, 18, 14))
    bd.polygon([(x + w - 4, y + h), (x + w - 4, y + 74),
                (x + w - 56, y + h)], fill=(30, 18, 14))
    # two tankers sitting in the water, flames above the hulls
    for tx, tl in [(x + x2 + 58, 92), (x + x2 + 176, 84)]:
        bd.rectangle([tx, y + 74, tx + tl, y + 92], fill=(20, 20, 26))
        bd.rectangle([tx + tl - 26, y + 60, tx + tl - 8, y + 74],
                     fill=(40, 40, 48))
        fx = tx + tl // 2
        bd.polygon([(fx - 12, y + 74), (fx, y + 48), (fx + 12, y + 74)],
                   fill=(255, 150, 30))
        bd.ellipse([fx - 8, y + 52, fx + 8, y + 68], fill=(255, 200, 70))
        # flame reflection on the water under each tanker
        bd.line([tx + 10, y + 100, tx + 50, y + 100], fill=(255, 140, 40), width=3)
        bd.line([tx + 20, y + 108, tx + 44, y + 108], fill=(255, 180, 70), width=2)
    # mine silhouette in the water, orange rim + glint so it reads
    mx, my = x + x2 + 150, y + h - 22
    bd.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(16, 16, 20))
    bd.ellipse([mx - 7, my - 7, mx + 7, my + 7], outline=(255, 140, 40), width=1)
    for ang in range(0, 360, 45):
        import math as _m
        ex = mx + int(10 * _m.cos(_m.radians(ang)))
        ey = my + int(10 * _m.sin(_m.radians(ang)))
        bd.line([mx, my, ex, ey], fill=(30, 30, 36), width=2)
    bd.ellipse([mx - 3, my - 4, mx - 1, my - 2], fill=(255, 200, 90))
    # warship silhouette on the water, light grey against the dark water
    bd.rectangle([x + w - 130, y + 100, x + w - 96, y + 108],
                 fill=(150, 150, 160))
    bd.rectangle([x + w - 122, y + 92, x + w - 112, y + 100],
                 fill=(150, 150, 160))
    # --- thin cream dividers ---
    bd.line([(x + x1, y), (x + x1, y + h)], fill=CREAM, width=2)
    bd.line([(x + x2, y), (x + x2, y + h)], fill=CREAM, width=2)
    # --- elements crossing the dividers: smoke wisps + one drone ---
    # L2 smoke drifting left over the first divider
    for i, (wx, wy, r) in enumerate([(-16, 18, 9), (-8, 26, 11), (2, 34, 8)]):
        bd.ellipse([x + x1 + wx - r, y + wy - r, x + x1 + wx + r, y + wy + r],
                   fill=(40, 40, 48))
    # L3 smoke drifting left over the second divider
    for i, (wx, wy, r) in enumerate([(-14, 30, 10), (-4, 38, 12), (6, 46, 8)]):
        bd.ellipse([x + x2 + wx - r, y + wy - r, x + x2 + wx + r, y + wy + r],
                   fill=(52, 32, 24))
    # a drone crossing the second divider
    dx, dy = x + x2 + 4, y + 52
    bd.ellipse([dx - 4, dy - 3, dx + 4, dy + 3], fill=(10, 10, 14))
    bd.line([dx - 9, dy - 5, dx + 9, dy - 5], fill=(220, 220, 220), width=1)
    img.paste(band, (ox, oy))


def medium_scene(d, idx, x, y, w, h):
    """Bold color-block scene per medium card. One background block + 2-4
    big simple shapes; must read instantly at thumbnail size."""
    scenes = {
        0: (30, 90, 150), 1: (230, 120, 50), 2: (90, 90, 95),
        3: (196, 164, 110), 4: (14, 30, 58), 5: (46, 120, 70),
        6: (120, 180, 220), 7: (240, 200, 60), 8: (70, 60, 140),
        9: (120, 120, 125),
    }
    bg = scenes[idx]
    d.rectangle([x, y, x + w, y + h], fill=bg)
    if idx == 0:  # signing ceremony: flags + table
        d.rectangle([x + 8, y + h - 16, x + w - 8, y + h - 8], fill=(120, 70, 30))
        d.polygon([(x + 18, y + 8), (x + 46, y + 8), (x + 46, y + 26),
                   (x + 18, y + 26)], fill=(0, 40, 110))
        d.polygon([(x + w - 46, y + 8), (x + w - 18, y + 8), (x + w - 18, y + 26),
                   (x + w - 46, y + 26)], fill=(0, 90, 60))
        d.ellipse([x + w // 2 - 12, y + 12, x + w // 2 + 12, y + 30],
                  fill=(255, 255, 255))
        d.polygon([(x + w // 2 - 10, y + 30), (x + w // 2 + 10, y + 30),
                   (x + w // 2 + 6, y + h - 16), (x + w // 2 - 6, y + h - 16)],
                  fill=(30, 30, 34))
    elif idx == 1:  # refinery dawn: towers + missile streaks
        for tx in (x + 14, x + 44, x + 74):
            d.rectangle([tx, y + 12, tx + 16, y + h - 8], fill=(60, 40, 30))
        d.line([(x + 10, y + 8), (x + 60, y + 30)], fill=(255, 255, 255), width=2)
        d.line([(x + 100, y + 6), (x + 60, y + 34)], fill=(255, 255, 255), width=2)
        d.ellipse([x + w - 26, y + 8, x + w - 8, y + 26], fill=(60, 60, 66))
    elif idx == 2:  # ambulance at dawn
        d.rectangle([x + 10, y + h - 22, x + w - 10, y + h - 6], fill=(240, 240, 235))
        d.rectangle([x + 14, y + h - 18, x + w - 40, y + h - 10], fill=(210, 30, 30))
        d.ellipse([x + 22, y + h - 8, x + 30, y + h], fill=(20, 20, 20))
        d.ellipse([x + w - 34, y + h - 8, x + w - 26, y + h], fill=(20, 20, 20))
        d.rectangle([x + w - 34, y + 8, x + w - 12, y + 26], fill=(90, 60, 40))
    elif idx == 3:  # courtroom scales
        d.rectangle([x + w // 2 - 2, y + 8, x + w // 2 + 2, y + h - 10],
                    fill=(40, 30, 20))
        d.line([(x + w // 2 - 26, y + 12), (x + w // 2 + 26, y + 12)],
               fill=(40, 30, 20), width=3)
        d.polygon([(x + w // 2 - 32, y + 12), (x + w // 2 - 20, y + 12),
                   (x + w // 2 - 26, y + 28)], fill=(214, 164, 60))
        d.polygon([(x + w // 2 + 20, y + 12), (x + w // 2 + 32, y + 12),
                   (x + w // 2 + 26, y + 28)], fill=(214, 164, 60))
        d.ellipse([x + w // 2 - 4, y + 6, x + w // 2 + 4, y + 14], fill=(214, 164, 60))
    elif idx == 4:  # grid down: lightning bolt
        d.polygon([(x + w // 2 + 8, y + 4), (x + w // 2 - 12, y + h // 2 + 4),
                   (x + w // 2 - 2, y + h // 2 + 4), (x + w // 2 - 8, y + h - 4),
                   (x + w // 2 + 12, y + h // 2 - 2), (x + w // 2 + 2, y + h // 2 - 2)],
                  fill=(255, 220, 60))
        d.rectangle([x + 8, y + h - 12, x + w - 8, y + h - 6], fill=(8, 8, 12))
    elif idx == 5:  # jungle clinic: tent + cross
        d.polygon([(x + 10, y + h - 10), (x + w // 2, y + 8), (x + w - 10, y + h - 10)],
                  fill=(240, 240, 235))
        d.rectangle([x + w // 2 - 8, y + 16, x + w // 2 - 2, y + 30], fill=(200, 30, 30))
        d.rectangle([x + w // 2 - 13, y + 21, x + w // 2 + 3, y + 27], fill=(200, 30, 30))
        d.rectangle([x + 12, y + h - 14, x + 34, y + h - 6], fill=(30, 70, 40))
    elif idx == 6:  # supermarket price tags
        d.rectangle([x + 10, y + 8, x + w - 10, y + 22], fill=(255, 255, 255))
        d.text((x + 14, y + 10), "$  $  $", font=font(F_SANS_B, 11), fill=(179, 35, 27))
        d.rectangle([x + w // 2 - 10, y + 26, x + w // 2 + 10, y + h - 8],
                    fill=(30, 60, 120))
        d.ellipse([x + w // 2 - 7, y + 26, x + w // 2 + 7, y + 36], fill=(240, 200, 140))
    elif idx == 7:  # factory: machines + fabric rolls
        for fx in (x + 10, x + 40, x + 70):
            d.rectangle([fx, y + 16, fx + 22, y + h - 10], fill=(40, 40, 46))
        for fx, col in [(x + 14, (220, 60, 60)), (x + 44, (60, 140, 220)),
                        (x + 74, (240, 200, 60))]:
            d.ellipse([fx, y + 6, fx + 14, y + 14], fill=col)
        d.rectangle([x + w - 34, y + 6, x + w - 8, y + 20], fill=(255, 255, 255))
        d.text((x + w - 32, y + 8), "$139", font=font(F_SANS_B, 9), fill=(179, 35, 27))
    elif idx == 8:  # rocket launch
        d.polygon([(x + w // 2 - 8, y + 6), (x + w // 2 + 8, y + 6),
                   (x + w // 2 + 6, y + 34), (x + w // 2 - 6, y + 34)],
                  fill=(240, 240, 235))
        d.polygon([(x + w // 2 - 6, y + 34), (x + w // 2 + 6, y + 34),
                   (x + w // 2 + 12, y + 44), (x + w // 2 - 12, y + 44)],
                  fill=(255, 150, 40))
        d.rectangle([x + 8, y + h - 12, x + 16, y + h - 4], fill=(60, 60, 66))
        d.rectangle([x + w - 16, y + h - 12, x + w - 8, y + h - 4], fill=(60, 60, 66))
        d.ellipse([x + 12, y + 8, x + 22, y + 18], fill=(255, 220, 120))
    else:  # energy bill: red bill
        d.rectangle([x + w // 2 - 26, y + 6, x + w // 2 + 26, y + h - 8],
                    fill=(255, 255, 255))
        d.rectangle([x + w // 2 - 22, y + 10, x + w // 2 + 22, y + 24],
                    fill=(179, 35, 27))
        d.text((x + w // 2 - 20, y + 12), "\u00a32,166", font=font(F_SANS_B, 11),
               fill=WHITE)
        d.line([(x + w // 2 - 18, y + 30), (x + w // 2 + 18, y + 30)],
               fill=(120, 120, 120), width=1)
        d.line([(x + w // 2 - 18, y + 36), (x + w // 2 + 6, y + 36)],
               fill=(120, 120, 120), width=1)


# continent polygons as (lon, lat) — coarse, reads as a world map at a glance
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 76),
     (-80, 73), (-75, 72), (-70, 62), (-65, 60), (-60, 52), (-55, 47),
     (-70, 42), (-75, 35), (-80, 32), (-81, 26), (-90, 21), (-95, 19),
     (-97, 16), (-92, 15), (-86, 13), (-83, 9), (-79, 9), (-85, 11),
     (-90, 14), (-95, 16), (-105, 20), (-110, 23), (-115, 28), (-120, 34),
     (-125, 40), (-125, 49), (-130, 55), (-140, 60), (-155, 58), (-165, 60)],
    [(-58, 64), (-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74),
     (-30, 76), (-45, 76), (-58, 72)],
    [(-79, 9), (-75, 11), (-72, 12), (-64, 11), (-60, 9), (-52, 5), (-50, 0),
     (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-55, -35),
     (-62, -41), (-66, -47), (-70, -54), (-74, -50), (-73, -40), (-72, -30),
     (-70, -20), (-77, -12), (-81, -6), (-80, 0)],
    [(-17, 15), (-16, 20), (-15, 25), (-10, 30), (-5, 35), (0, 36), (10, 37),
     (20, 32), (30, 31), (32, 31), (35, 28), (38, 22), (40, 15), (42, 11),
     (46, 11), (51, 12), (48, 5), (42, 0), (40, -5), (38, -10), (36, -18),
     (33, -26), (28, -33), (20, -35), (16, -30), (13, -20), (12, -12),
     (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 50), (3, 52),
     (7, 54), (8, 57), (10, 59), (5, 60), (5, 62), (12, 64), (18, 66),
     (25, 70), (30, 70), (32, 66), (30, 62), (28, 58), (24, 58), (21, 55),
     (18, 54), (12, 54), (8, 55), (3, 53), (-2, 51), (-5, 50), (-10, 48),
     (-10, 42), (-9, 38)],
    [(30, 36), (36, 36), (36, 32), (39, 31), (43, 29), (48, 30), (52, 28),
     (56, 26), (60, 25), (64, 25), (67, 24), (70, 21), (73, 17), (76, 10),
     (78, 8), (80, 10), (84, 18), (88, 22), (92, 21), (95, 16), (98, 12),
     (100, 7), (103, 2), (105, 9), (107, 11), (109, 13), (106, 20),
     (108, 18), (110, 20), (112, 22), (114, 22), (116, 23), (118, 25),
     (120, 28), (122, 30), (122, 33), (124, 35), (126, 38), (127, 40),
     (130, 42), (132, 43), (135, 44), (138, 46), (140, 48), (142, 50),
     (142, 55), (140, 59), (137, 62), (135, 66), (132, 70), (128, 71),
     (124, 72), (120, 73), (115, 73), (110, 74), (105, 76), (100, 77),
     (95, 76), (90, 75), (85, 74), (80, 73), (75, 72), (70, 71), (68, 70),
     (65, 69), (62, 68), (58, 68), (55, 66), (52, 65), (48, 63), (44, 60),
     (40, 58), (38, 55), (36, 52), (34, 50), (32, 48), (30, 46), (30, 42),
     (28, 40), (28, 38)],
    [(114, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (140, -17), (136, -15), (135, -12), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
    [(95, 5), (98, 8), (100, 6), (102, 2), (104, -2), (106, -6), (110, -7),
     (114, -8), (118, -8), (120, -10), (124, -9), (128, -8), (132, -4),
     (136, -2), (140, -4), (138, -8), (132, -8), (126, -6), (120, -4),
     (114, -2), (108, 0), (102, 4), (98, 8)],
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 37), (140, 39),
     (141, 42), (140, 44), (138, 45), (136, 43), (134, 40), (132, 37),
     (130, 34)],
]


def draw_map(d, x, y, w, h):
    """Dark dotted world map with numbered red pins + nudges for collisions."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=NAVY)
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)

    def proj(lon, lat):
        px = (lon + 180.0) / 360.0 * w
        py = (85.0 - lat) / 145.0 * h
        return px, py

    for poly in CONTINENTS:
        md.polygon([proj(lon, lat) for lon, lat in poly], fill=255)
    step = 8
    for gy in range(step // 2, h, step):
        for gx in range(step // 2, w, step):
            if mask.getpixel((gx, gy)):
                d.ellipse([x + gx - 2, y + gy - 2, x + gx + 2, y + gy + 2],
                          fill=(235, 228, 205))
    # pins with nudges for collisions (leader line to true position)
    nudges = {"M6": (-15, -9), "M7": (15, 9), "M5": (-17, 9), "L3": (15, -9),
              "M10": (15, 9), "M4": (-15, -10)}
    for num, lat, lon in PINS:
        px, py = proj(lon, lat)
        nx, ny = nudges.get(num, (0, 0))
        cx, cy = x + px + nx, y + py + ny
        if (nx, ny) != (0, 0):
            d.line([x + px, y + py, cx, cy], fill=(255, 255, 255), width=1)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                  outline=WHITE, width=1)
        f = font(F_SANS_B, 8)
        tw = d.textlength(num, font=f)
        d.text((cx - tw / 2, cy - 5), num, font=f, fill=WHITE)


# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 24
    CW = W - 2 * MX  # 976
    y = 8

    # kicker
    f_kick = font(F_SANS_B, 13)
    d.text((MX, y), "THE WORLD IN ONE DAY", font=f_kick, fill=RED)
    count_line = "34 STORIES \u00b7 6 REGIONS \u00b7 WEDNESDAY 25 NOVEMBER 2026"
    f_cnt = font(F_SANS_B, 12)
    d.text((W - MX - d.textlength(count_line, font=f_cnt), y), count_line,
           font=f_cnt, fill=INK)
    y += 18
    d.line([(MX, y), (W - MX, y)], fill=INK, width=2)
    y += 5

    # masthead (76pt Liberation Serif Bold; must fit within 1008px)
    mast = "Wednesday 25 November 2026"
    msize = 76
    while msize > 60:
        fm = font(F_SERIF_B, msize)
        if d.textlength(mast, font=fm) <= 1000:
            break
        msize -= 1
    mw = d.textlength(mast, font=fm)
    d.text(((W - mw) / 2, y), mast, font=fm, fill=INK)
    print("masthead size", msize, "width", round(mw))
    y += msize + 2

    # subline
    sub = "Asia's chip rout \u00b7 Drones hit two Volga refineries \u00b7 Two tankers ablaze in Hormuz"
    fs = font(F_SERIF_I, 19)
    sw = d.textlength(sub, font=fs)
    d.text(((W - sw) / 2, y), sub, font=fs, fill=RED)
    y += 24

    # KPI strip: 6 boxes
    kpi_y, kpi_h = y, 49
    bw = (CW - 5 * 6) / 6
    for i, (num, label) in enumerate(KPI):
        bx = MX + i * (bw + 6)
        d.rectangle([bx, kpi_y, bx + bw, kpi_y + kpi_h], outline=INK, width=1)
        fn = font(F_NOTO_B, 25)
        nw = d.textlength(num, font=fn)
        d.text((bx + (bw - nw) / 2, kpi_y + 2), num, font=fn, fill=RED)
        fl = font(F_SANS_B, 9)
        lab_lines = wrap(d, label, fl, bw - 8)
        ly = kpi_y + 29
        for ln in lab_lines[:2]:
            lw = d.textlength(ln, font=fl)
            d.text((bx + (bw - lw) / 2, ly), ln, font=fl, fill=INK)
            ly += 10
    y = kpi_y + kpi_h + 5

    # region strip
    f_reg = font(F_SANS_B, 12)
    parts, total_w = [], 0
    for name, n, col in REGIONS:
        parts.append((name, n, col))
        total_w += d.textlength(f"{name} {n}", font=f_reg) + 14
    total_w += (len(parts) - 1) * 22
    rx = (W - total_w) / 2
    for name, n, col in parts:
        d.ellipse([rx, y + 3, rx + 8, y + 11], fill=col)
        rx += 12
        txt = f"{name} {n}"
        d.text((rx, y), txt, font=f_reg, fill=INK)
        rx += d.textlength(txt, font=f_reg) + 22
    y += 14

    # fields strip
    f_fld = font(F_SANS, 11)
    fld = "18 FIELDS \u2014 " + " \u00b7 ".join(f"{n} {c}" for n, c in FIELDS)
    fw = d.textlength(fld, font=f_fld)
    if fw > CW:
        f_fld = font(F_SANS, 10)
        fw = d.textlength(fld, font=f_fld)
    d.text(((W - fw) / 2, y), fld, font=f_fld, fill=(90, 60, 50))
    print("fields width", round(fw))
    y += 12

    # timeline band
    tl_y, tl_h = y, 34
    d.rounded_rectangle([MX, tl_y, MX + CW, tl_y + tl_h], radius=4, fill=NAVY)
    f_tl = font(F_SANS_B, 11)
    d.text((MX + 10, tl_y + 10), "THE DAY IN UTC", font=f_tl, fill=(255, 210, 90))
    cell_w = (CW - 130) / 6
    for i, (t, label) in enumerate(TIMELINE):
        cx = MX + 130 + i * cell_w
        d.text((cx, tl_y + 5), t, font=font(F_SANS_B, 12), fill=(255, 210, 90))
        fl = font(F_SANS, 10)
        for j, ln in enumerate(wrap(d, label, fl, cell_w - 8)[:2]):
            d.text((cx, tl_y + 19 + j * 10), ln, font=fl, fill=WHITE)
    y = tl_y + tl_h + 5

    # ---- lead row: ONE continuous triptych band, then three text columns
    scene_h = 118
    draw_triptych(d, img, MX, y, CW, scene_h)
    band_y = y
    y += scene_h + 4
    col_w = CW / 3
    lead_text_top = y
    lead_bottom = y
    for i, lead in enumerate(LEADS):
        cx = MX + i * col_w
        tx, tw = cx + 6, col_w - 12
        # headline (2 lines max)
        fh = font(F_NOTO_B, 19)
        hl, fh = fit_lines(d, lead["head"], fh, tw, 2)
        hy = draw_wrapped(d, tx, y, hl, fh, INK, leading=20)
        # deck (3 lines max)
        fd = font(F_SANS, 11)
        dl, fd = fit_lines(d, lead["deck"], fd, tw, 3)
        dy = draw_wrapped(d, tx, hy + 2, dl, fd, INK, leading=12)
        # WHY IT MATTERS (2 lines max, italic red)
        fw2 = font(F_NOTO_I, 11)
        wl, fw2 = fit_lines(d, lead["wim"], fw2, tw, 2)
        wy = draw_wrapped(d, tx, dy + 2, wl, fw2, RED, leading=12)
        # tag row
        ftag = font(F_SANS_B, 9)
        d.text((tx, wy + 4), f"{lead['num']} \u00b7 {lead['tag']}", font=ftag, fill=INK)
        chip(d, tx + tw - 62, wy + 3, lead["chip"], CHIP_COLORS[lead["chip"]])
        lead_bottom = max(lead_bottom, wy + 17)
        if i < 2:
            d.line([(cx + col_w, y - 2), (cx + col_w, wy + 16)], fill=(200, 190, 170),
                   width=1)
    y = lead_bottom + 4
    print("lead row ends y =", y, "scene share =", round(scene_h / (y - band_y), 3))

    # ---- mediums: 2 rows x 5
    med_gap = 8
    med_w = (CW - 4 * med_gap) / 5
    med_row_h = 116
    for row in range(2):
        ry = y
        for col in range(5):
            idx = row * 5 + col
            m = MEDIUMS[idx]
            mx = MX + col * (med_w + med_gap)
            d.rectangle([mx, ry, mx + med_w, ry + med_row_h], outline=(200, 190, 170),
                        width=1)
            sh = 38
            medium_scene(d, idx, mx + 1, ry + 1, med_w - 2, sh)
            ty = ry + sh + 4
            fh = font(F_NOTO_B, 12)
            hl, fh = fit_lines(d, m["head"], fh, med_w - 10, 2)
            ty = draw_wrapped(d, mx + 5, ty, hl, fh, INK, leading=13)
            fd = font(F_SANS, 9)
            dl, fd = fit_lines(d, m["deck"], fd, med_w - 10, 3)
            if len(wrap(d, m["deck"], fd, med_w - 10)) > 3:
                print("WARN medium deck truncated:", m["num"])
            ty = draw_wrapped(d, mx + 5, ty + 1, dl, fd, INK, leading=11)
            ftag = font(F_SANS_B, 8)
            d.text((mx + 5, ry + med_row_h - 13), f"{m['num']} \u00b7 {m['tag']}",
                   font=ftag, fill=INK)
            chip(d, mx + med_w - 56, ry + med_row_h - 14, m["chip"],
                 CHIP_COLORS[m["chip"]], size=7, h=11)
        y = ry + med_row_h + 4
    print("mediums end y =", y)

    # ---- ALSO ON: 21 briefs, 3 columns x 7 rows
    f_ao = font(F_SANS_B, 12)
    d.text((MX, y), "ALSO ON \u2014 21 MORE STORIES, WEDNESDAY 25 NOVEMBER", font=f_ao,
           fill=INK)
    y += 15
    d.line([(MX, y), (W - MX, y)], fill=INK, width=1)
    y += 2
    ao_top = y
    col_w2 = CW / 3
    f_num = font(F_SANS_B, 10)
    f_br = font(F_SANS, 10)
    for i, (num, head, ch) in enumerate(BRIEFS):
        col, r = divmod(i, 7)
        bx = MX + col * col_w2
        by = ao_top + r * 12
        d.text((bx, by), num, font=f_num, fill=RED)
        hw = d.textlength(head, font=f_br)
        max_hw = col_w2 - 24 - 54
        fb = f_br
        if hw > max_hw:
            fb = font(F_SANS, 9)
            hw = d.textlength(head, font=fb)
        if hw > max_hw:
            print("WARN brief too wide:", num, head, round(hw), "max", round(max_hw))
        d.text((bx + 22, by), head, font=fb, fill=INK)
        chip(d, bx + col_w2 - 54, by, ch, CHIP_COLORS[ch], size=7, h=11)
    y = ao_top + 7 * 12 + 4
    print("also-on ends y =", y)

    # ---- map band: dotted map + legend
    map_y, map_h = y, 104
    draw_map(d, MX, map_y, 700, map_h)
    lx = MX + 712
    d.text((lx, map_y), "REGIONS & PINS", font=font(F_SANS_B, 11), fill=INK)
    ly = map_y + 18
    for name, n, col in REGIONS:
        d.ellipse([lx, ly + 2, lx + 8, ly + 10], fill=col)
        pins = {"ASIA": "L1, 11, 12", "EUROPE": "L2, 8, 13",
                "MIDDLE EAST": "L3, 5, 6, 7", "AFRICA": "M9",
                "AMERICAS": "\u2014", "OCEANIA": "M4, 10"}[name]
        d.text((lx + 12, ly), f"{name}  {n} stories \u00b7 pins {pins}",
               font=font(F_SANS, 10), fill=INK)
        ly += 13
    d.text((lx, ly + 1), "Pins = lead & medium story numbers",
           font=font(F_SANS_I, 9) if os.path.exists(
               "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf")
           else font(F_SANS, 9), fill=(90, 60, 50))
    y = map_y + map_h + 5
    print("map ends y =", y)

    # ---- DATE CHECK
    dc_y = y
    f_dc_t = font(F_SANS_B, 11)
    f_dc = font(F_SANS, 9)
    dc_lines = wrap(d, DATE_CHECK, f_dc, CW - 20)
    dc_h = 18 + len(dc_lines) * 11 + 4
    d.rectangle([MX, dc_y, MX + CW, dc_y + dc_h], outline=RED, width=2)
    d.text((MX + 10, dc_y + 4), "DATE CHECK", font=f_dc_t, fill=RED)
    draw_wrapped(d, MX + 10, dc_y + 18, dc_lines, f_dc, INK, leading=11)
    print("date check lines:", len(dc_lines), "height", dc_h)
    y = dc_y + dc_h + 4

    # ---- footer
    f_ft = font(F_SANS, 9)
    src_lines = wrap(d, SOURCES, f_ft, CW)
    y = draw_wrapped(d, MX, y, src_lines, f_ft, (90, 60, 50), leading=11)
    leg = ("CONFIRMED officially verified  \u00b7  OFFICIAL from an authority  \u00b7  "
           "REPORTED press report, not yet confirmed  \u00b7  CLAIM one party's claim, unverified")
    y = draw_wrapped(d, MX, y + 1, wrap(d, leg, f_ft, CW), f_ft, (90, 60, 50),
                     leading=11)
    print("final y =", y, "bottom slack =", H - y)
    assert y <= H - 2, f"OVERFLOW: final y {y} exceeds {H}"
    return img


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    img = build()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=False)
    raw = open(path, "rb").read()
    print("saved", path, len(raw), "bytes, md5",
          hashlib.md5(raw).hexdigest())
    assert len(raw) <= 1048576, "over 1 MiB cap"
    assert img.size == (1024, 1024)
    # crops for zoom-checking (aligned to printed section boundaries)
    crops = {
        "crop-triptych.png": (0, 260, 1024, 400),
        "crop-leads.png": (0, 390, 1024, 480),
        "crop-med1.png": (0, 470, 1024, 600),
        "crop-med2.png": (0, 590, 1024, 720),
        "crop-also.png": (0, 710, 1024, 830),
        "crop-map.png": (0, 820, 1024, 1024),
    }
    for name, box in crops.items():
        img.crop(box).save(os.path.join(out_dir, name))
        print("crop", name, box)


if __name__ == "__main__":
    main()
