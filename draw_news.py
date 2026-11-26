#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news front page (1024x1024 PNG).

Broadsheet redesign: newsprint cream paper, serif headlines, hairline
rules, masthead furniture, AI-generated hero art composited in, a
two-column feature grid, and a "MORE TODAY" digest with ten short items.

Deterministic: fixed fonts, fixed geometry, fixed hero asset, no
randomness, no timestamps, no network. Running this script twice
produces byte-identical output. Only the Python standard library and
Pillow are used. The hero art (assets/hero.png) is an AI-generated,
text-free editorial illustration of two tankers ablaze in the Strait
of Hormuz; every word on the page is drawn by this script.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 32
CW = W - 2 * MARGIN            # 960, content width
COL_W = 468                    # feature column width
COL_GAP = 24

PAPER = (247, 242, 230)        # warm newsprint cream
INK = (18, 18, 18)             # near-black ink
NAVY = (27, 58, 92)            # navy headers and rules
RED = (185, 28, 28)            # breaking red
GREY = (74, 74, 70)            # secondary text
HAIR = (150, 148, 140)         # hairline grey
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, path, size, max_w, min_size=20):
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


def section_label(draw, y, text, fnt):
    """Label on the left with a hairline rule continuing to the right edge."""
    draw.text((MARGIN, y), text, font=fnt, fill=NAVY)
    lw = draw.textlength(text, font=fnt)
    draw.line([(MARGIN + lw + 12, y + 11), (W - MARGIN, y + 11)],
              fill=NAVY, width=2)
    return y + 28


# --- the five feature stories: (kicker, headline, one-line summary) ---
FEATURES = [
    ("MIDDLE EAST", "HOUTHIS HIT SAUDI OIL AND RIYADH",
     "Aramco's Ras Tanura refinery attacked; fires reported. "
     "Riyadh strike injured 11."),
    ("SPACE", "FIRST PAKISTANI IN SPACE",
     "China's Shenzhou-24 docked at its space station with "
     "Pakistan's first astronaut."),
    ("TECHNOLOGY", "HUAWEI FOUND GUILTY IN U.S. COURT",
     "Guilty of trade-secret theft conspiracy and bank fraud; "
     "cleared of racketeering."),
    ("AMERICAS", "CARTAGENA HOSTAGES FREED",
     "Raid ends supermarket siege: all remaining hostages freed "
     "alive, one attacker killed."),
    ("EUROPE", "RUSSIA STRIKES ODESA AND KYIV",
     "Two killed, three hurt in Odesa region, a child among them; "
     "Kyiv flats hit, two hurt."),
]

# --- the digest: ten short items, worded exactly as verified ---
DIGEST = [
    "COP31 climate talks failed to reach agreement "
    "(Pope Leo XIV voiced concern)",
    "Sudan: RSF drone strikes killed 19 civilians, wounded 20",
    "Israel killed Hamas colonel Mohammad Abuelouf in Gaza",
    "Fuel tanker fire near Cairo killed at least 31",
    "US spy agencies hit by cyber breach \u2014 CIA and the Director "
    "of National Intelligence's office breached, unclassified data taken",
    "Russia: independent newspaper Novaya Gazeta to close permanently",
    "Macy's Thanksgiving Parade postponed by weather \u2014 "
    "first time in 100 years",
    "Bangladesh: garment minimum wage up 36% to $139 a month",
    "US proposes new tariffs \u2014 10% duty on Brazilian aircraft",
    "US economy grew 4.3% in Q3, inflation 3.8% in October",
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_title = font(SERIF_B, 52)
    f_date = font(SANS_B, 38)
    f_furn = font(SANS_B, 18)
    f_kicker = font(SANS_B, 18)
    f_label = font(SANS_B, 20)
    f_feat_head = font(SERIF_B, 24)
    f_feat_sum = font(SANS, 19)
    f_hero_sum = font(SANS, 20)
    f_digest = font(SANS, 18)

    # ---------- masthead ----------
    d.line([(MARGIN, 12), (W - MARGIN, 12)], fill=INK, width=3)
    d.text((MARGIN, 20), "VOL. I \u2014 NO. 330", font=f_furn, fill=NAVY)
    furn_c = "25 NOVEMBER 2026"
    d.text(((W - d.textlength(furn_c, font=f_furn)) / 2, 20),
           furn_c, font=f_furn, fill=NAVY)
    furn_r = "ONE DAY. THE WHOLE WORLD."
    d.text((W - MARGIN - d.textlength(furn_r, font=f_furn), 20),
           furn_r, font=f_furn, fill=NAVY)
    title = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(title, font=f_title)) / 2, 44),
           title, font=f_title, fill=NAVY)
    date = "WEDNESDAY 25 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=f_date)) / 2, 100),
           date, font=f_date, fill=RED)
    d.line([(MARGIN, 146), (W - MARGIN, 146)], fill=INK, width=2)
    d.line([(MARGIN, 151), (W - MARGIN, 151)], fill=INK, width=2)

    # ---------- hero: AI art band, flames + both tankers + sea ----------
    hero = Image.open(os.path.join(HERE, "assets", "hero.png"))
    hero_band = hero.crop((0, 640, 1920, 960)).resize((CW, 160),
                                                      Image.LANCZOS)
    hero_y = 158
    img.paste(hero_band, (MARGIN, hero_y))
    d.rectangle([MARGIN, hero_y, W - MARGIN, hero_y + 160],
                outline=INK, width=2)

    # ---------- hero headline + summary, left aligned ----------
    d.text((MARGIN, 326), "BREAKING", font=f_kicker, fill=RED)
    hero_head = "TWO OIL TANKERS HIT BY MINES IN STRAIT OF HORMUZ"
    f_hero_head = fit(d, hero_head, SERIF_B, 32, CW)
    d.text((MARGIN, 348), hero_head, font=f_hero_head, fill=NAVY)
    hero_sum = ("Iran's Revolutionary Guard said two tankers struck naval "
                "mines, exploded and caught fire while transiting an "
                "unauthorised route.")
    lines = wrap(d, hero_sum, f_hero_sum, CW)
    text_block(d, (MARGIN, 386), lines, f_hero_sum, INK, 24)

    # ---------- feature grid: two columns, then the last story full width --
    feat_y = 442
    row_h = 104
    d.line([(MARGIN + COL_W + COL_GAP // 2, feat_y),
            (MARGIN + COL_W + COL_GAP // 2, feat_y + 2 * row_h - 8)],
           fill=HAIR, width=1)
    col_x = [MARGIN, MARGIN + COL_W + COL_GAP]
    for idx, (kicker, head, summ) in enumerate(FEATURES[:4]):
        row, col = divmod(idx, 2)
        x = col_x[col]
        yy = feat_y + row * row_h
        d.text((x, yy), kicker, font=f_kicker, fill=RED)
        f_head = fit(d, head, SERIF_B, 24, COL_W, min_size=21)
        d.text((x, yy + 22), head, font=f_head, fill=INK)
        lines = wrap(d, summ, f_feat_sum, COL_W)
        text_block(d, (x, yy + 52), lines, f_feat_sum, GREY, 24)
        d.line([(MARGIN, yy + 100), (W - MARGIN, yy + 100)],
               fill=HAIR, width=1)
    # last story spans both columns
    kicker, head, summ = FEATURES[4]
    yy = feat_y + 2 * row_h
    d.text((MARGIN, yy), kicker, font=f_kicker, fill=RED)
    f_head = fit(d, head, SERIF_B, 24, CW, min_size=21)
    d.text((MARGIN, yy + 22), head, font=f_head, fill=INK)
    lines = wrap(d, summ, f_feat_sum, CW)
    text_block(d, (MARGIN, yy + 52), lines, f_feat_sum, GREY, 24)

    # ---------- digest: ten short items ----------
    y = section_label(d, 734, "MORE TODAY", f_label)
    for item in DIGEST:
        d.rectangle([MARGIN, y + 6, MARGIN + 8, y + 14], fill=RED)
        lines = wrap(d, item, f_digest, CW - 24)
        y = text_block(d, (MARGIN + 24, y), lines, f_digest, INK, 22)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")


if __name__ == "__main__":
    main()
