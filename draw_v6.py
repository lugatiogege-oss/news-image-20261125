#!/usr/bin/env python3
"""Render the fixed news-image v6 (option B) front page, 1024x1024.

Deterministic: no randomness, no timestamps. Two runs must be byte-identical.
Usage: python3 draw_v6.py  -> writes entry.png next to this script.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OWNER = os.path.join(ASSETS, "owner")

# ---------- colours ----------
PAPER = "#f7f1e3"
PANEL = "#fffdf6"
INK = "#111111"
NAVY = "#0d1b3e"
DARKRED = "#8b1a1a"
BURGUNDY = "#7a1f2b"
GOLD = "#b7791f"
GREEN = "#1e7a34"
ORANGE = "#d96c00"
BLUE = "#1f4e79"
GREY = "#555555"
HAIRLINE = "#b9ad8f"
STAT_BORDER = "#c9bfa5"
RED = "#a31621"
WHITE = "#ffffff"

W, H = 1024, 1024
X0, X1 = 20, 1004          # content span, width 984
CW = X1 - X0

LIB = "/usr/share/fonts/truetype/liberation"
DEJAVU = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    """Liberation first, DejaVu fallback if a file is missing."""
    for base in (LIB, DEJAVU):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)      # noqa: E731
SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s)    # noqa: E731
SANS = lambda s: font("LiberationSans-Regular.ttf", s)       # noqa: E731
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)        # noqa: E731


def wrap(draw, text, fnt, max_w, max_lines=None):
    """Greedy word wrap measured with font.getlength. Truncates the last
    allowed line with an ellipsis if the text does not fit."""
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
            if max_lines and len(lines) == max_lines:
                # cur is overflow: ellipsise the last kept line instead
                t = lines[-1]
                while t and draw.textlength(t + "…", font=fnt) > max_w:
                    t = t[:-1]
                lines[-1] = t + "…"
                return lines
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        t = lines[-1]
        while t and draw.textlength(t + "…", font=fnt) > max_w:
            t = t[:-1]
        lines[-1] = t + "…"
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading, align="left", width=None):
    for ln in lines:
        if align == "center":
            lx = x + (width - draw.textlength(ln, font=fnt)) / 2
        elif align == "right":
            lx = x + width - draw.textlength(ln, font=fnt)
        else:
            lx = x
        draw.text((lx, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def letterspaced(draw, text, x, y, fnt, fill, tracking=2):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += draw.textlength(ch, font=fnt) + tracking
    return cx


def fit_crop(path, tw, th, precrop_bottom=None):
    im = Image.open(path).convert("RGB")
    if precrop_bottom is not None:
        w, h = im.size
        im = im.crop((0, int(h * (1 - precrop_bottom)), w, h))
    return ImageOps.fit(im, (tw, th), Image.LANCZOS, centering=(0.5, 0.5))


def square_thumb(path, size=30):
    im = Image.open(path).convert("RGB")
    return ImageOps.fit(im, (size, size), Image.LANCZOS, centering=(0.5, 0.5))


def number_circle(draw, cx, cy, d, number, fill, size):
    draw.ellipse([cx - d / 2, cy - d / 2, cx + d / 2, cy + d / 2], fill=fill)
    fnt = SANS_B(size)
    t = str(number)
    tw = draw.textlength(t, font=fnt)
    th = fnt.getbbox(t)[3] - fnt.getbbox(t)[1]
    draw.text((cx - tw / 2, cy - th / 2 - 1), t, font=fnt, fill=WHITE)


def tag_pill(draw, x, y, text, bg, size=10, h=16):
    fnt = SANS_B(size)
    tw = draw.textlength(text, font=fnt)
    w = int(tw) + 12
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    th = fnt.getbbox(text)[3] - fnt.getbbox(text)[1]
    draw.text((x + 6, y + (h - th) / 2 - 1), text, font=fnt, fill=WHITE)
    return w


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # outer navy frame, 6px
    d.rectangle([0, 0, W - 1, H - 1], outline=NAVY, width=6)

    # ---------- masthead y 12-38, rule y 42 ----------
    # small navy globe icon at left
    gx, gy, gr = 20, 12, 13  # centre (33, 25), r 13
    cx, cy = gx + gr, gy + gr
    d.ellipse([gx, gy, gx + 2 * gr, gy + 2 * gr], outline=NAVY, width=2)
    d.ellipse([cx - 5, gy + 1, cx + 5, gy + 2 * gr - 1], outline=NAVY, width=1)
    d.line([gx + 1, cy, gx + 2 * gr - 1, cy], fill=NAVY, width=1)
    d.arc([gx + 3, gy + 3, gx + 2 * gr - 3, gy + 2 * gr - 3], 300, 60,
          fill=NAVY, width=1)
    letterspaced(d, "THE WORLD IN ONE DAY", 54, 13, SERIF_B(22), NAVY, tracking=2)
    right = "21 STORIES · 5 REGIONS · ALL FROM WEDNESDAY 25 NOVEMBER 2026"
    rf = SANS_B(13)
    d.text((X1 - d.textlength(right, font=rf), 18), right, font=rf, fill=NAVY)
    d.line([X0, 42, X1, 42], fill=NAVY, width=2)

    # ---------- date / subhead ----------
    df = SERIF_B(54)
    date = "Wednesday 25 November 2026"
    d.text(((W - d.textlength(date, font=df)) / 2, 50), date, font=df, fill=INK)
    sf = SERIF_I(19)
    sub = "Tanker attacks, space milestone and new trade tensions dominate global headlines"
    d.text(((W - d.textlength(sub, font=sf)) / 2, 110), sub, font=sf, fill=INK)

    # ---------- stat strip y 138-210 ----------
    stats = [
        ("2", "TANKERS", "hit by mines in Hormuz", BLUE),
        ("-6.2%", "KOSPI", "Asia markets down sharply", GREEN),
        ("+26%", "UK ENERGY", "price cap rises in Jan", ORANGE),
        ("31", "KILLED", "Cairo fuel-tanker fire", DARKRED),
        ("4.3%", "US GDP", "economy grew in Q3", GREEN),
        ("$94.61", "BRENT", "oil jumps 3.5%", BLUE),
    ]
    bw, gap = 157, 8
    sx = X0 + 1  # 6*157 + 5*8 = 982 -> 21..1003
    for i, (val, lab, sub_l, accent) in enumerate(stats):
        bx = sx + i * (bw + gap)
        d.rectangle([bx, 138, bx + bw, 210], fill=PANEL, outline=STAT_BORDER, width=1)
        d.rectangle([bx, 138, bx + bw, 142], fill=accent)
        vf = SANS_B(26)
        d.text((bx + (bw - d.textlength(val, font=vf)) / 2, 148), val,
               font=vf, fill=NAVY)
        lf = SANS_B(11)
        d.text((bx + (bw - d.textlength(lab, font=lf)) / 2, 178), lab,
               font=lf, fill=INK)
        uf = SANS(11)
        d.text((bx + (bw - d.textlength(sub_l, font=uf)) / 2, 193), sub_l,
               font=uf, fill=GREY)

    # ---------- region bar y 218-244 ----------
    segs = [("EUROPE 5", 5, BLUE), ("M. EAST 4", 4, DARKRED),
            ("AFRICA 3", 3, GOLD), ("ASIA 4", 4, GREEN),
            ("AMERICAS 5", 5, ORANGE)]
    widths = [234, 187, 141, 188, 234]  # proportional to 5/4/3/4/5 of 984
    rx = X0
    rf2 = SANS_B(14)
    for (label, _n, colour), wseg in zip(segs, widths):
        d.rectangle([rx, 218, rx + wseg, 244], fill=colour)
        d.text((rx + (wseg - d.textlength(label, font=rf2)) / 2, 223),
               label, font=rf2, fill=WHITE)
        rx += wseg

    # ---------- top stories row (3 cols, w 321) ----------
    top = [
        dict(num=1, tag="TOP STORY", tag_bg=NAVY, kicker="MIDDLE EAST • HORMUZ",
             headline="Two Tankers Hit by Mines in Hormuz",
             desc="Iran says two tankers struck naval mines in the Strait of Hormuz, exploding and catching fire.",
             loc="Strait of Hormuz | Reuters", pill="REPORTED", pill_bg=BLUE,
             photo="tanker.png"),
        dict(num=2, tag="SPACE", tag_bg=NAVY, kicker="ASIA • SHENZHOU-24",
             headline="China Sends Pakistan's First Astronaut to Space",
             desc="Shenzhou-24 docks with Tiangong station, marking Pakistan's first astronaut in orbit.",
             loc="Beijing | Xinhua", pill="OFFICIAL", pill_bg=RED,
             photo="space.png"),
        dict(num=3, tag="TRADE", tag_bg=NAVY, kicker="AMERICAS • TARIFFS",
             headline="US Proposes Tariffs on 14 Economies",
             desc="China faces a 20% cap, EU 15%; Brazil aircraft 10%. Hearings begin 25 January.",
             loc="Washington | Reuters", pill="PROPOSED", pill_bg=BURGUNDY,
             photo="ship.png"),
    ]
    col_w, col_gap = 321, 10
    for i, s in enumerate(top):
        x = X0 + i * (col_w + col_gap)
        ph = fit_crop(os.path.join(OWNER, s["photo"]), col_w, 140)
        img.paste(ph, (x, 252))
        d.rectangle([x, 252, x + col_w, 392], outline=HAIRLINE, width=1)
        # category tag top-left on photo
        tf = SANS_B(12)
        tw = d.textlength(s["tag"], font=tf)
        d.rectangle([x + 6, 258, x + 6 + tw + 12, 258 + 18], fill=s["tag_bg"])
        d.text((x + 12, 260), s["tag"], font=tf, fill=WHITE)
        d.text((x, 398), s["kicker"], font=SANS_B(12), fill=DARKRED)
        hl = wrap(d, s["headline"], SERIF_B(23), col_w, max_lines=2)
        draw_lines(d, hl, x, 414, SERIF_B(23), INK, 24)
        dl = wrap(d, s["desc"], SANS(13), col_w, max_lines=3)
        draw_lines(d, dl, x, 464, SANS(13), INK, 14)
        # footer y 510-532
        number_circle(d, x + 8, 521, 16, s["num"], NAVY, 10)
        d.text((x + 20, 515), s["loc"], font=SANS(11), fill=GREY)
        pf = SANS_B(10)
        pw = int(d.textlength(s["pill"], font=pf)) + 12
        tag_pill(d, x + col_w - pw, 513, s["pill"], s["pill_bg"], size=10, h=16)

    # ---------- secondary row (5 cols, w 190) ----------
    sec = [
        dict(num=4, tag="ENERGY", kicker="M. EAST • RAS TANURA",
             headline="Houthis Claim Ras Tanura Refinery Strike",
             desc="Houthis say they hit the Saudi refinery; coalition says 4 drones downed, no hit confirmed.",
             loc="Saudi Arabia | Reuters", pill="CLAIM", pill_bg=ORANGE,
             photo="refinery.png", precrop=None),
        dict(num=5, tag="SECURITY", kicker="S. AMERICA • CARTAGENA",
             headline="Hostages Freed in Supermarket Siege",
             desc="All hostages released after hours-long standoff.",
             loc="Cartagena | Reuters", pill="RESOLVED", pill_bg=GREEN,
             photo="supermarket.png", precrop=None),
        dict(num=6, tag="CONFLICT", kicker="M. EAST • HODEIDAH",
             headline="Coalition Jets Strike Hodeidah Port",
             desc="Saudi-led coalition jets hit Houthi targets at the Red Sea port.",
             loc="Yemen | SPA", pill="ATTACK", pill_bg=RED,
             photo="hodeidah.png", precrop=0.65),
        dict(num=7, tag="ECONOMY", kicker="ASIA • STOCKS",
             headline="Asian Chip Stocks Tumble",
             desc="Kospi falls 6.2%; Samsung down 9.9%.",
             loc="Seoul | Reuters", pill="MARKETS", pill_bg=BURGUNDY,
             photo="stocks.png", precrop=None),
        dict(num=8, tag="DISASTER", kicker="ASIA • BOGOR",
             headline="Illegal Gold Mine Floods Bogor",
             desc="9 dead, 17 still missing in West Java.",
             loc="Bogor | AP", pill="DISASTER", pill_bg=ORANGE,
             photo="gold.png", precrop=None),
    ]
    sw, sgap = 190, 8
    sx2 = X0 + 1  # 5*190 + 4*8 = 982
    for i, s in enumerate(sec):
        x = sx2 + i * (sw + sgap)
        ph = fit_crop(os.path.join(OWNER, s["photo"]), sw, 90,
                      precrop_bottom=s["precrop"])
        img.paste(ph, (x, 544))
        d.rectangle([x, 544, x + sw, 634], outline=HAIRLINE, width=1)
        tf = SANS_B(10)
        tw = d.textlength(s["tag"], font=tf)
        d.rectangle([x + 5, 549, x + 5 + tw + 10, 549 + 15], fill=NAVY)
        d.text((x + 10, 550), s["tag"], font=tf, fill=WHITE)
        d.text((x, 640), s["kicker"], font=SANS_B(10), fill=DARKRED)
        hl = wrap(d, s["headline"], SERIF_B(17), sw, max_lines=2)
        draw_lines(d, hl, x, 654, SERIF_B(17), INK, 19)
        dl = wrap(d, s["desc"], SANS(12), sw, max_lines=3)
        draw_lines(d, dl, x, 694, SANS(12), INK, 11)
        number_circle(d, x + 7, 739, 14, s["num"], NAVY, 9)
        d.text((x + 17, 734), s["loc"], font=SANS(10), fill=GREY)
        pf = SANS_B(9)
        pw = int(d.textlength(s["pill"], font=pf)) + 10
        tag_pill(d, x + sw - pw, 732, s["pill"], s["pill_bg"], size=9, h=14)

    # ---------- bottom section y 762-962 ----------
    # LEFT: MORE TODAY x 20-628
    d.rectangle([X0, 762, 628, 962], fill=PANEL, outline=HAIRLINE, width=1)
    d.rectangle([X0, 762, 628, 788], fill=NAVY)
    d.text((X0 + 10, 767), "MORE TODAY — 13 MORE STORIES",
           font=SANS_B(14), fill=WHITE)

    briefs = [
        ("Cairo fuel-tanker fire kills 31, injures 21", "feature-cairo.png"),
        ("Sudan RSF drone strikes kill 19, wounds 20", "mini-sudan.png"),
        ("Israel kills Hamas colonel Abuelouf in Gaza", "mini-abuelouf.png"),
        ("UK energy cap to rise 26% to £2,166", "feature-energy.png"),
        ("Bangladesh garment wage up 36% to $139", "mini-bangladesh.png"),
        ("Abrego Garcia lands in Spain", "mini-abrego.png"),
        ("Trump and NATO chief warn Russia on Ukraine", "mini-trump-rutte.png"),
        ("Lille stun Bayern in Champions League", "mini-lille.png"),
        ("Nvidia slides as S&P warns on rating", "mini-nvidia.png"),
        ("Militants kill at least 30 in Nigeria", "mini-nigeria.png"),
        ("Macy's Parade postponed to Saturday", "feature-macys.png"),
        ("US economy grew 4.3% as inflation hit 3.8%", "feature-gdp.png"),
        ("UK retailer Next hit by cyber breach", "mini-next.png"),
    ]
    cols = [briefs[0:5], briefs[5:9], briefs[9:13]]
    col_x = [28, 228, 428]
    for ci, col in enumerate(cols):
        for ri, (headline, thumb) in enumerate(col):
            y = 792 + ri * 34
            th = square_thumb(os.path.join(ASSETS, thumb), 30)
            img.paste(th, (col_x[ci], y))
            d.rectangle([col_x[ci], y, col_x[ci] + 30, y + 30],
                        outline=HAIRLINE, width=1)
            tx = col_x[ci] + 36
            tw_ = 192 - 36
            lines = wrap(d, headline, SANS_B(11), tw_, max_lines=2)
            draw_lines(d, lines, tx, y + 1, SANS_B(11), INK, 13)

    # RIGHT: WORLD MAP x 636-1004
    d.rectangle([636, 762, X1, 962], fill=PANEL, outline=HAIRLINE, width=1)
    d.rectangle([636, 762, X1, 788], fill=NAVY)
    d.text((636 + 10, 767), "WORLD MAP: KEY EVENTS", font=SANS_B(13), fill=WHITE)
    map_path = os.path.join(OWNER, "map-clean.png")
    map_img = Image.open(map_path).convert("RGB")
    mw, mh = map_img.size  # 2240x1120
    DW, DH = 368, 174
    map_disp = ImageOps.fit(map_img, (DW, DH), Image.LANCZOS, centering=(0.5, 0.5))
    map_x, map_y = 636, 788
    img.paste(map_disp, (map_x, map_y))
    d.rectangle([map_x, map_y, map_x + DW, map_y + DH], outline=HAIRLINE, width=1)

    # pin transform: same fit as ImageOps.fit (centre crop)
    scale = max(DW / mw, DH / mh)
    sw_, sh_ = mw * scale, mh * scale
    off_x, off_y = (sw_ - DW) / 2, (sh_ - DH) / 2

    def lonlat_to_display(lon, lat):
        fx = (lon + 180.0) / 360.0 * mw
        fy = (90.0 - lat) / 180.0 * mh
        return fx * scale - off_x, fy * scale - off_y

    pins = [
        # (num, lon, lat, nudge_x, nudge_y, fill)
        (1, 56.5, 26.5, 0, -10, RED),        # Hormuz
        (2, 116.4, 39.9, -5, -3, GREEN),     # Beijing
        (3, -77.0, 38.9, 0, 0, ORANGE),      # Washington
        (4, 50.1, 26.6, 5, 6, RED),          # Ras Tanura
        (5, -75.5, 10.4, 0, 0, ORANGE),      # Cartagena
        (6, 42.9, 14.8, -6, 3, RED),         # Hodeidah
        (7, 127.0, 37.5, 4, 3, GREEN),       # Seoul
        (8, 106.8, -6.6, 0, 0, GREEN),       # Bogor
    ]
    for num, lon, lat, nx, ny, fill in pins:
        px, py = lonlat_to_display(lon, lat)
        px += nx
        py += ny
        ax, ay = map_x + px, map_y + py
        d.ellipse([ax - 8, ay - 8, ax + 8, ay + 8], fill=fill, outline=WHITE, width=1)
        fnt = SANS_B(11)
        t = str(num)
        tw = d.textlength(t, font=fnt)
        th = fnt.getbbox(t)[3] - fnt.getbbox(t)[1]
        d.text((ax - tw / 2, ay - th / 2 - 1), t, font=fnt, fill=WHITE)

    # ---------- footer y 970-1018 ----------
    d.rectangle([X0, 970, X1, 1018], outline=RED, width=2)
    fx0, fx1 = X0 + 8, X1 - 8
    fw = fx1 - fx0
    lead = "DATE CHECK  "
    body = ("Excluded: Huawei verdict (Tue 24 Nov) · Riyadh tower strike (Tue 24 Nov) · "
            "COP31 no deal (Sun 22 Nov) · Kraków shooting (Sat 7 Nov) · "
            "Odesa/Kyiv strikes (Tue 24 Nov) · CIA breach (Tue 24 Nov) · "
            "Ahmadi flogging (Mon 23 Nov) · S. Korea exam reward (Mon 23 Nov) · "
            "Novaya Gazeta closure (30 Oct) · Huang apology (23–24 Nov)")
    bf = SANS_B(11)
    uf = SANS(11)
    # wrap line 1 as bold lead + regular body, measured jointly
    words = body.split()
    lines1 = []
    cur_bold = lead
    cur = ""
    # first line starts with the bold lead; measure lead + words together
    first = True
    for w in words:
        trial = (cur + " " + w).strip()
        meas = (d.textlength(lead, font=bf) if first else 0) + \
            d.textlength(trial, font=uf)
        if meas <= fw:
            cur = trial
        else:
            lines1.append((first, cur))
            cur, first = w, False
    if cur:
        lines1.append((first, cur))
    y = 973
    for is_first, ln in lines1:
        if is_first:
            d.text((fx0, y), lead, font=bf, fill=RED)
            d.text((fx0 + d.textlength(lead, font=bf), y), ln, font=uf, fill=INK)
        else:
            d.text((fx0, y), ln, font=uf, fill=INK)
        y += 13
    src = "Sources: Reuters, AFP, AP, BBC, CNN, Al Jazeera, Bloomberg, WSJ, Ofgem, Xinhua, SPA, UEFA"
    d.text((fx0, y), src, font=SANS(11), fill=INK)
    tag = "— A global snapshot. In one day. —"
    tf2 = SERIF_I(11)
    d.text((fx1 - d.textlength(tag, font=tf2), y), tag, font=tf2, fill=INK)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    with open(out, "rb") as f:
        print("sha256:", hashlib.sha256(f.read()).hexdigest())
    print("size:", os.path.getsize(out), "bytes;", img.size)


if __name__ == "__main__":
    main()
