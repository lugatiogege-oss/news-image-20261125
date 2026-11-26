#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news front page, v4 (1024x1024 PNG).

Winning-template broadsheet: thin banner, huge date headline, red
subhead naming the top 3 stories, colour-coded region bar, a
large-number stat strip, 3 large illustrated leads, 6 smaller
illustrated stories, a schematic "WHERE IT HAPPENED" world map with
numbered pins, 12 numbered one-line briefs with PIL-drawn pictogram
icons, and a red DATE CHECK footer proving the date boundary.

Every story sits in its own hairline-bordered box with a clear
gutter between boxes (bento grid). All text is 18px or larger.
21 stories, all verified for Wednesday 25 November 2026 only:
Huawei (Tue 24 Nov) and COP31 (Sun 22 Nov) were REMOVED, the Riyadh
tower strike (Tue 24 Nov) is NOT in the Houthis item, which is a
Ras Tanura CLAIM only. No Krakow (Sat 7 Nov).

Deterministic: fixed fonts, fixed geometry, fixed image assets, no
randomness, no timestamps, no network. Running this script twice
produces byte-identical output. Only the Python standard library
and Pillow are used. All illustrations are AI-generated text-free
editorial art; every word on the page is drawn by this script.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 32
CW = W - 2 * MARGIN            # 960, content width
GAP = 8                        # gutter between boxes
SEC = 2                        # gap between sections

PAPER = (247, 242, 230)        # warm newsprint cream
INK = (18, 18, 18)             # near-black ink
NAVY = (27, 58, 92)            # navy headers and rules
RED = (185, 28, 28)            # breaking red
GREY = (74, 74, 70)            # secondary text
HAIR = (150, 148, 140)         # hairline grey
MAPFILL = (188, 196, 204)      # pale continents
CREAM = (247, 242, 230)
AMBER = (198, 108, 24)
TEAL = (24, 110, 96)
BROWN = (122, 72, 40)
BLUE = (52, 96, 168)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, path, size, max_w, min_size=18):
    """Largest font size at or below `size` that fits `max_w`."""
    while size > min_size:
        fnt = font(path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 1
    return font(path, min_size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to a pixel width. Returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, lines, fnt, fill, leading):
    """Draw wrapped lines starting at xy. Returns the y after the last line."""
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def box(d, x, y, w, h, outline=HAIR, width=1):
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=outline, width=width)


def band(img, y0, y1, tw, th):
    """Crop a horizontal band of the source and resize to (tw, th)."""
    return img.crop((0, y0, img.width, y1)).resize((tw, th), Image.LANCZOS)


def sq(img, x0, size):
    """Crop a square starting at x0 and resize to (size, size)."""
    return img.crop((x0, 0, x0 + img.height, img.height)).resize(
        (size, size), Image.LANCZOS)


# ---------------------------------------------------------------- data ---

REGIONS = [
    ("MIDDLE EAST", RED), ("ASIA", AMBER), ("EUROPE", NAVY),
    ("AMERICAS", TEAL), ("AFRICA", BROWN), ("OCEANIA", BLUE),
]

# (big number, label) — 6 stats, one line each (measured to fit 153px cells)
STATS = [
    ("2", "TANKERS"), ("-6.2%", "KOSPI"), ("9", "BOGOR"),
    ("31", "KILLED"), ("36%", "WAGE RISE"), ("74", "LASHES"),
]

# 3 large leads: (asset, crop band y0-y1, kicker, headline, summary)
LEADS = [
    ("hero.png", (700, 970), "MIDDLE EAST \u00b7 REPORTED",
     "TWO TANKERS MINED IN HORMUZ",
     "Two tankers struck naval mines, exploded and caught fire "
     "in the Strait of Hormuz."),
    ("feature-space.png", (350, 620), "ASIA \u00b7 REPORTED",
     "SHENZHOU-24 DOCKS WITH FIRST PAKISTANI IN SPACE",
     "China's Shenzhou-24 docked at its space station carrying "
     "Pakistan's first astronaut."),
    ("feature-tariffs.png", (600, 870), "TRADE \u00b7 REPORTED",
     "US PROPOSES TARIFFS ON 14 ECONOMIES",
     "US proposes tariffs on 14 economies, including a 10% duty "
     "on Brazilian aircraft."),
]

# 6 smaller illustrated stories:
# (asset, square x0, kicker, headline, summary)
SMALL = [
    ("feature-houthis.png", 320, "MIDDLE EAST \u00b7 CLAIM",
     "HOUTHIS CLAIM RAS TANURA STRIKE",
     "Houthis say they hit Ras Tanura refinery, fires claimed. "
     "Coalition: 4 drones downed, no hit confirmed."),
    ("feature-cartagena.png", 320, "AMERICAS \u00b7 REPORTED",
     "CARTAGENA HOSTAGES FREED",
     "Raid ends supermarket siege: all remaining hostages freed "
     "alive, one attacker killed."),
    ("feature-odesa.png", 640, "EUROPE \u00b7 REPORTED",
     "RUSSIA STRIKES ODESA AND KYIV",
     "Two killed, three hurt in Odesa region, a child among them; "
     "Kyiv flats hit, two hurt."),
    ("feature-kospi.png", 320, "ASIA \u00b7 REPORTED",
     "ASIAN CHIP STOCKS TUMBLE",
     "Kospi falls 6.2%; Samsung -9.9%, SK Hynix -11%."),
    ("feature-bogor.png", 320, "ASIA \u00b7 REPORTED",
     "BOGOR GOLD MINE FLOOD",
     "Flooded illegal gold mine in Bogor, West Java \u2014 "
     "9 dead, 17 still trapped."),
    ("feature-energy.png", 320, "EUROPE \u00b7 REPORTED",
     "UK ENERGY CAP TO RISE 26%",
     "UK energy price cap to rise 26% to \u00a32,166 a year "
     "from January (Ofgem)."),
]

# 12 numbered briefs: (icon kind, one-line text) — worded exactly as verified
BRIEFS = [
    ("drone", "Sudan RSF drone strikes kill 19"),
    ("flag", "Israel kills Hamas colonel Abuelouf in Gaza"),
    ("flame", "Cairo fuel-tanker fire kills 31"),
    ("lock", "CIA + ODNI hit by cyber breach"),
    ("paper", "Novaya Gazeta to close permanently"),
    ("balloon", "Macy's Thanksgiving Parade postponed to Saturday "
                "(first time in 100 years)"),
    ("coin", "Bangladesh garment minimum wage up 36% to $139/month"),
    ("chart", "US economy grew 4.3% in Q3, inflation 3.8% in October"),
    ("chip", "Jensen Huang returns to Nvidia \u2014 apologised to staff, "
            "in therapy"),
    ("mic", "Iranian singer Parastoo Ahmadi flogged 74 lashes"),
    ("bag", "UK retailer Next hit by cyber breach"),
    ("lens", "South Korea offers $375,000 reward to catch AI exam cheaters"),
]

# World map: rough continent polygons in (lon, lat)
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-80, 45), (-97, 25), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-145, 60)],
    [(-58, 64), (-45, 60), (-40, 70), (-55, 76), (-68, 70)],
    [(-80, 10), (-60, 8), (-50, 0), (-40, -5), (-35, -10), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -55), (-73, -40),
     (-75, -20), (-80, -5)],
    [(-10, 36), (-5, 44), (0, 50), (5, 58), (10, 60), (18, 56),
     (25, 60), (30, 55), (28, 45), (20, 40), (10, 38), (0, 36)],
    [(-18, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (51, 10), (48, 0), (40, -10), (35, -20),
     (30, -30), (20, -35), (15, -28), (12, -18), (13, -5), (9, 4),
     (-8, 5), (-15, 11)],
    [(30, 70), (45, 68), (60, 70), (75, 73), (90, 75), (110, 76),
     (130, 72), (150, 70), (160, 66), (162, 60), (155, 55), (140, 50),
     (130, 45), (120, 40), (110, 35), (100, 30), (95, 25), (90, 22),
     (85, 20), (80, 15), (75, 10), (70, 20), (60, 25), (55, 28),
     (50, 30), (45, 35), (40, 40), (35, 42), (30, 45), (30, 55),
     (35, 65)],
    [(95, 25), (100, 20), (105, 15), (110, 10), (115, 5), (120, -5),
     (125, -8), (130, -5), (135, 0), (130, 5), (120, 10), (110, 15)],
    [(113, -22), (120, -15), (130, -12), (140, -15), (150, -22),
     (150, -30), (145, -38), (140, -38), (130, -32), (120, -35),
     (113, -30)],
]

# Map pins: (brief number, display lon, lat, label dx, label dy).
# Two US-economy pins are nudged apart on the schematic map so their
# numbers do not collide (true locations: DC twice, NYC once).
# Label offsets were placed by hand so no two numbers overlap.
PINS = [
    (1, 32.5, 15.6, -30, 6), (2, 34.5, 31.5, 8, -9), (3, 31.2, 30.0, -34, -9),
    (4, -77.0, 38.9, 8, -9), (5, 37.6, 55.8, -30, -9),
    (6, -68.0, 40.7, 12, 9), (7, 90.4, 23.8, 8, -9),
    (8, -88.0, 38.9, -28, -9), (9, -122.0, 37.4, -30, -9),
    (10, 51.4, 35.7, 8, -9), (11, -0.1, 51.5, -30, -9),
    (12, 127.0, 37.5, 8, -9),
]


def icon(d, x, y, kind, s=24):
    """Draw a small pictogram in a s x s box at (x, y). Navy + red."""
    cx, cy = x + s // 2, y + s // 2
    if kind == "drone":
        d.rectangle([cx - 6, cy - 3, cx + 6, cy + 3], fill=NAVY)
        for dx, dy in ((-8, -6), (8, -6), (-8, 6), (8, 6)):
            d.ellipse([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3],
                      outline=NAVY, width=2)
        d.line([(cx - 4, cy + 3), (cx - 7, cy + 8)], fill=NAVY, width=2)
        d.line([(cx + 4, cy + 3), (cx + 7, cy + 8)], fill=NAVY, width=2)
    elif kind == "flag":
        d.line([(x + 5, y + 2), (x + 5, y + s - 2)], fill=NAVY, width=2)
        d.polygon([(x + 5, y + 3), (x + s - 2, y + 7), (x + 5, y + 11)],
                  fill=RED)
    elif kind == "flame":
        d.polygon([(cx, y + 1), (cx + 7, y + 11), (cx + 4, y + 18),
                   (cx - 4, y + 18), (cx - 7, y + 11)], fill=RED)
        d.polygon([(cx, y + 8), (cx + 3, y + 14), (cx - 3, y + 14)],
                  fill=AMBER)
    elif kind == "lock":
        d.arc([cx - 6, y + 2, cx + 6, y + 12], 180, 360, fill=NAVY, width=3)
        d.rectangle([cx - 8, y + 11, cx + 8, y + s - 2], fill=NAVY)
        d.ellipse([cx - 2, y + 14, cx + 2, y + 18], fill=CREAM)
    elif kind == "paper":
        d.rectangle([x + 4, y + 2, x + s - 4, y + s - 2], outline=NAVY, width=2)
        d.line([(x + 7, y + 7), (x + s - 7, y + 7)], fill=NAVY, width=3)
        for yy in (12, 16, 20):
            d.line([(x + 7, y + yy), (x + s - 7, y + yy)], fill=GREY, width=2)
    elif kind == "balloon":
        d.ellipse([cx - 7, y + 1, cx + 7, y + 13], outline=RED, width=2)
        d.line([(cx, y + 13), (cx, y + 21)], fill=NAVY, width=2)
        d.polygon([(cx - 3, y + 21), (cx + 3, y + 21), (cx, y + s - 2)],
                  outline=NAVY)
    elif kind == "coin":
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=AMBER, width=3)
        f = font(SANS_B, 14)
        t = "$"
        d.text((cx - d.textlength(t, font=f) / 2, cy - 8), t, font=f, fill=AMBER)
    elif kind == "chart":
        d.line([(x + 3, y + 18), (x + 9, y + 13), (x + 14, y + 15),
                (x + s - 3, y + 4)], fill=NAVY, width=3)
        d.polygon([(x + s - 3, y + 4), (x + s - 9, y + 5), (x + s - 4, y + 10)],
                  fill=RED)
    elif kind == "chip":
        d.rectangle([cx - 7, cy - 7, cx + 7, cy + 7], outline=NAVY, width=2)
        d.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=NAVY)
        for i in (-4, 0, 4):
            d.line([(cx + i, cy - 11), (cx + i, cy - 7)], fill=NAVY, width=2)
            d.line([(cx + i, cy + 7), (cx + i, cy + 11)], fill=NAVY, width=2)
            d.line([(cx - 11, cy + i), (cx - 7, cy + i)], fill=NAVY, width=2)
            d.line([(cx + 7, cy + i), (cx + 11, cy + i)], fill=NAVY, width=2)
    elif kind == "mic":
        d.ellipse([cx - 6, y + 1, cx + 6, y + 13], fill=NAVY)
        d.rectangle([cx - 3, y + 13, cx + 3, y + 21], fill=NAVY)
        d.line([(cx - 5, y + 21), (cx + 5, y + 21)], fill=NAVY, width=2)
    elif kind == "bag":
        d.polygon([(cx - 8, y + 7), (cx + 8, y + 7), (cx + 6, y + s - 2),
                   (cx - 6, y + s - 2)], outline=NAVY, width=2)
        d.arc([cx - 4, y + 2, cx + 4, y + 11], 180, 360, fill=RED, width=2)
    elif kind == "lens":
        d.ellipse([cx - 8, cy - 8, cx + 3, cy + 3], outline=NAVY, width=3)
        d.line([(cx + 2, cy + 2), (cx + 9, cy + 9)], fill=NAVY, width=3)


def section_header(d, y, text, fnt):
    """Section label on the left with a navy rule to the right edge."""
    d.text((MARGIN, y), text, font=fnt, fill=NAVY)
    lw = d.textlength(text, font=fnt)
    d.line([(MARGIN + lw + 12, y + 11), (W - MARGIN, y + 11)],
           fill=NAVY, width=2)
    return y + 22


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    assets = os.path.join(HERE, "assets")

    f_banner = font(SANS_B, 18)
    f_head = font(SERIF_B, 38)
    f_sub = font(SERIF, 19)
    f_region = font(SANS_B, 18)
    f_sec = font(SANS_B, 20)
    f_kick = font(SANS_B, 18)
    f_lead_head = font(SERIF_B, 22)
    f_lead_sum = font(SANS, 18)
    f_small_head = font(SERIF_B, 20)
    f_small_sum = font(SANS, 18)
    f_brief = font(SANS, 18)
    f_num = font(SANS_B, 18)
    f_map = font(SANS_B, 18)
    f_pin = font(SANS_B, 18)
    f_foot = font(SANS, 18)

    y = 8

    # ---------- thin top banner ----------
    d.rectangle([MARGIN, y, W - MARGIN, y + 18], fill=NAVY)
    banner = ("THE WORLD IN ONE DAY \u2014 21 STORIES \u00b7 6 REGIONS "
              "\u00b7 WEDNESDAY 25 NOVEMBER 2026")
    d.text(((W - d.textlength(banner, font=f_banner)) / 2, y),
           banner, font=f_banner, fill=CREAM)
    y += 18 + SEC

    # ---------- huge date headline ----------
    head = "Wednesday 25 November 2026"
    d.text(((W - d.textlength(head, font=f_head)) / 2, y),
           head, font=f_head, fill=INK)
    y += 38 + SEC

    # ---------- red subhead naming the top 3 stories ----------
    sub = ("Hormuz tankers mined \u00b7 Shenzhou-24 docks \u00b7 "
           "US proposes tariffs on 14 economies")
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, y),
           sub, font=f_sub, fill=RED)
    y += 18 + SEC

    # ---------- colour-coded region bar ----------
    total = 0
    parts = []
    for name, col in REGIONS:
        w = d.textlength(name, font=f_region) + 20
        parts.append((name, col, w))
        total += w
    total += 24 * (len(parts) - 1)
    x = (W - total) / 2
    for name, col, w in parts:
        d.rectangle([x + 2, y + 3, x + 14, y + 15], fill=col)
        d.text((x + 18, y), name, font=f_region, fill=INK)
        x += w + 24
    y += 18 + SEC

    # ---------- stat strip: 6 one-line stats ----------
    cell_w = (CW - 5 * GAP) / 6
    for i, (num, lab) in enumerate(STATS):
        cx0 = MARGIN + i * (cell_w + GAP)
        box(d, cx0, y, cell_w, 22)
        txt = num + " " + lab
        f = fit(d, txt, SANS_B, 22, cell_w - 8, min_size=18)
        d.text((cx0 + (cell_w - d.textlength(txt, font=f)) / 2, y + 1),
               txt, font=f, fill=INK)
    y += 22 + SEC

    # ---------- TOP STORIES header ----------
    y = section_header(d, y, "TOP STORIES", f_sec)

    # ---------- 3 large leads ----------
    lead_w = (CW - 2 * GAP) / 3
    lead_h = 202
    for i, (asset, (y0, y1), kicker, headl, summ) in enumerate(LEADS):
        x = MARGIN + i * (lead_w + GAP)
        box(d, x, y, lead_w, lead_h)
        src = Image.open(os.path.join(assets, asset))
        img.paste(band(src, y0, y1, int(lead_w) - 2, 32),
                  (int(x) + 1, y + 1))
        yy = y + 32 + 8
        d.text((x + 8, yy), kicker, font=f_kick, fill=RED)
        yy += 22
        lines = wrap(d, headl, f_lead_head, lead_w - 16)
        yy = text_block(d, (x + 8, yy), lines[:3], f_lead_head, INK, 26)
        lines = wrap(d, summ, f_lead_sum, lead_w - 16)
        text_block(d, (x + 8, yy + 2), lines[:3], f_lead_sum, GREY, 19)
    y += lead_h + SEC

    # ---------- 6 smaller illustrated stories: 3 cols x 2 rows ----------
    # Hybrid layout: 40px thumb top-left, kicker + headline beside it,
    # summary full-width below. Row heights measured from real wraps.
    small_w = (CW - 2 * GAP) / 3
    row_hs = [156, 137]
    for idx, (asset, x0, kicker, headl, summ) in enumerate(SMALL):
        row, col = divmod(idx, 3)
        x = MARGIN + col * (small_w + GAP)
        yy = y + sum(row_hs[:row]) + row * GAP
        box(d, x, yy, small_w, row_hs[row])
        src = Image.open(os.path.join(assets, asset))
        img.paste(sq(src, x0, 40), (int(x) + 8, int(yy) + 8))
        tx = x + 8 + 40 + 8
        tw = small_w - 8 - 40 - 8 - 8
        d.text((tx, yy + 8), kicker, font=f_kick, fill=RED)
        lines = wrap(d, headl, f_small_head, tw)
        text_block(d, (tx, yy + 30), lines[:2], f_small_head, INK, 24)
        lines = wrap(d, summ, f_small_sum, small_w - 16)
        text_block(d, (x + 8, yy + 80), lines[:4], f_small_sum, GREY, 19)
    y += sum(row_hs) + GAP + SEC

    # ---------- WHERE IT HAPPENED map strip ----------
    map_h = 48
    box(d, MARGIN, y, CW, map_h)
    lab = "WHERE IT HAPPENED"
    d.text((MARGIN + 10, y + 15), lab, font=f_map, fill=NAVY)
    mx0, mx1 = MARGIN + 210, W - MARGIN - 6
    my0 = y
    mw = mx1 - mx0

    def mx(lon):
        return mx0 + (lon + 180) / 360 * mw

    def my(lat):
        return my0 + 4 + (75 - lat) / 130 * (map_h - 8)

    for poly in CONTINENTS:
        pts = [(mx(lon), my(lat)) for lon, lat in poly]
        d.polygon(pts, fill=MAPFILL)
    for num, lon, lat, dx, dy in PINS:
        px, py = mx(lon), my(lat)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=NAVY)
        d.text((px + dx, py + dy), str(num), font=f_pin, fill=NAVY)
    y += map_h + SEC

    # ---------- MORE TODAY header + 12 numbered briefs, 2 columns ----------
    y = section_header(d, y, "MORE TODAY", f_sec)
    col_w = (CW - GAP) / 2
    row_hs = [28, 28, 44, 44, 44, 44]
    for idx, (kind, text) in enumerate(BRIEFS):
        row, col = divmod(idx, 2)
        x = MARGIN + col * (col_w + GAP)
        yy = y + sum(row_hs[:row]) + row * 2
        box(d, x, yy, col_w, row_hs[row])
        n = str(idx + 1)
        d.text((x + 8, yy + 5), n, font=f_num, fill=RED)
        icon(d, x + 30, yy + 2, kind, s=24)
        lines = wrap(d, text, f_brief, col_w - 30 - 24 - 10 - 8)
        text_block(d, (x + 30 + 24 + 10, yy + 5), lines[:2], f_brief,
                   INK, 19)
    y += sum(row_hs) + 5 * 2 + SEC

    # ---------- red DATE CHECK footer ----------
    foot_h = 38
    d.rectangle([MARGIN, y, W - MARGIN, y + foot_h], outline=RED, width=2)
    f1 = ("NOT 25 NOVEMBER \u2014 LEFT OUT: Huawei verdict (Tue 24 Nov) "
          "\u00b7 Riyadh strike, 11 hurt (Tue 24 Nov)")
    f2 = ("COP31 no deal (Sun 22 Nov) \u00b7 Kr\u00e1kow shooting "
          "(Sat 7 Nov) \u2014 Reuters, AP, AFP, Al Jazeera, WSJ, CNN")
    d.text((MARGIN + 10, y + 1), f1, font=f_foot, fill=RED)
    d.text((MARGIN + 10, y + 20), f2, font=f_foot, fill=INK)
    y += foot_h

    print("bottom y:", y, "of", H)
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
