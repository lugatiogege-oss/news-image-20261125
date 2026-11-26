#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news front page (1024x1024 PNG).

Deterministic: fixed fonts, fixed geometry, no randomness, no timestamps,
no network. Running this script twice produces byte-identical output.
Only the Python standard library and Pillow are used.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36

PAPER = (247, 243, 234)      # off-white paper
INK = (20, 20, 20)          # near-black ink
NAVY = (27, 58, 92)         # navy headers
RED = (193, 39, 45)         # breaking red
GREY = (90, 90, 88)         # secondary text
LIGHT_NAVY = (233, 238, 243)
SKY = (205, 222, 235)
SEA = (27, 58, 92)
ORANGE = (232, 116, 31)
GOLD = (240, 178, 44)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


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


def text_block(draw, xy, lines, fnt, fill, leading, align="left", anchor_x=None):
    """Draw wrapped lines starting at xy. Returns the y after the last line."""
    x, y = xy
    for line in lines:
        if align == "center":
            lx = anchor_x - draw.textlength(line, font=fnt) / 2
        else:
            lx = x
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += leading
    return y


def flame(draw, cx, base_y, w, h, color):
    """A simple flat flame: stacked triangles, deterministic."""
    draw.polygon(
        [(cx - w / 2, base_y), (cx, base_y - h), (cx + w / 2, base_y)],
        fill=color,
    )
    draw.polygon(
        [(cx - w / 4, base_y), (cx, base_y - h * 0.62), (cx + w / 4, base_y)],
        fill=(255, 214, 90),
    )


def smoke(draw, cx, cy, r, color=(120, 120, 118)):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def draw_tanker_scene(draw, x0, y0, x1, y1):
    """Flat illustration for the hero, drawn inside [x0,y0,x1,y1].

    Band height is 124 px. Layout, all inside the band:
    sky 0-68, sea 68-124, hull 68-100, containers 44-68,
    bridge tower 12-68, flames rise at most 38 px above the deck.
    """
    bh = y1 - y0
    sea_y = y0 + 68
    deck_y = y0 + 44
    # sky and sea
    draw.rectangle([x0, y0, x1, sea_y], fill=SKY)
    draw.rectangle([x0, sea_y, x1, y1], fill=SEA)
    # sun, top right
    draw.ellipse([x1 - 84, y0 + 10, x1 - 44, y0 + 50], fill=GOLD)
    # waves
    for wx in range(x0 + 18, x1 - 20, 64):
        draw.line([(wx, y1 - 18), (wx + 34, y1 - 18)], fill=WHITE, width=4)
        draw.line([(wx + 12, y1 - 8), (wx + 46, y1 - 8)],
                  fill=(150, 180, 205), width=4)
    # tanker hull: deck line at sea_y, hull below it
    draw.polygon(
        [(x0 + 80, sea_y), (x1 - 190, sea_y), (x1 - 140, sea_y + 32),
         (x0 + 130, sea_y + 32)],
        fill=(34, 34, 36),
    )
    # deck containers, sitting on the hull's top edge
    draw.rectangle([x0 + 110, deck_y, x0 + 290, sea_y], fill=RED)
    draw.rectangle([x0 + 300, deck_y, x0 + 460, sea_y], fill=NAVY)
    draw.rectangle([x0 + 470, deck_y, x0 + 590, sea_y], fill=(60, 110, 70))
    # bridge tower at the stern (right), base on the hull
    draw.rectangle([x1 - 180, y0 + 12, x1 - 140, sea_y], fill=WHITE)
    draw.rectangle([x1 - 180, y0 + 12, x1 - 140, y0 + 30], fill=NAVY)
    # flames above the deck (never above the band top)
    flame(draw, x0 + 200, deck_y, 64, 38, ORANGE)
    flame(draw, x0 + 380, deck_y, 52, 32, RED)
    flame(draw, x0 + 530, deck_y, 44, 28, ORANGE)
    # small smoke puffs drifting to the side of the flames, never on top
    smoke(draw, x0 + 236, y0 + 6, 7)
    smoke(draw, x0 + 166, y0 + 13, 6)
    smoke(draw, x0 + 414, y0 + 6, 7)
    smoke(draw, x0 + 348, y0 + 13, 6)
    smoke(draw, x0 + 562, y0 + 6, 6)
    smoke(draw, x0 + 500, y0 + 13, 5)
    # naval mine in the water, lower left
    mx, my = x0 + 46, y1 - 22
    draw.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=INK)
    for dx, dy in [(-13, 0), (13, 0), (0, -13), (0, 13),
                   (-9, -9), (9, -9), (-9, 9), (9, 9)]:
        draw.line([(mx + dx * 0.6, my + dy * 0.6), (mx + dx, my + dy)],
                  fill=INK, width=3)


def icon_refinery(draw, x, y, s):
    """Oil refinery towers with a flame."""
    draw.rectangle([x + 6, y + s - 34, x + 20, y + s - 4], fill=NAVY)
    draw.rectangle([x + 26, y + s - 44, x + 40, y + s - 4], fill=NAVY)
    draw.rectangle([x + 46, y + s - 28, x + 58, y + s - 4], fill=NAVY)
    draw.rectangle([x + 2, y + s - 6, x + 62, y + s - 1], fill=INK)
    flame(draw, x + 33, y + s - 44, 16, 24, ORANGE)


def icon_rocket(draw, x, y, s):
    """Rocket rising past stars."""
    draw.polygon([(x + 32, y + 2), (x + 42, y + 24), (x + 22, y + 24)],
                 fill=NAVY)
    draw.rectangle([x + 22, y + 24, x + 42, y + 46], fill=RED)
    draw.polygon([(x + 22, y + 46), (x + 14, y + 58), (x + 22, y + 52)],
                 fill=ORANGE)
    draw.polygon([(x + 42, y + 46), (x + 50, y + 58), (x + 42, y + 52)],
                 fill=ORANGE)
    flame(draw, x + 32, y + 58, 14, 18, GOLD)
    draw.ellipse([x + 4, y + 6, x + 12, y + 14], fill=GOLD)
    draw.ellipse([x + 52, y + 16, x + 58, y + 22], fill=GOLD)


def icon_court(draw, x, y, s):
    """Courthouse columns."""
    draw.polygon([(x + 4, y + 14), (x + 32, y + 2), (x + 60, y + 14)],
                 fill=NAVY)
    for cx in (10, 24, 38, 50):
        draw.rectangle([x + cx, y + 18, x + cx + 5, y + 46], fill=NAVY)
    draw.rectangle([x + 2, y + 46, x + 62, y + 52], fill=INK)
    draw.rectangle([x + 8, y + 52, x + 56, y + 57], fill=INK)


def icon_shop(draw, x, y, s):
    """Supermarket storefront with a shield."""
    draw.rectangle([x + 4, y + 18, x + 60, y + 54], fill=NAVY)
    draw.rectangle([x + 9, y + 24, x + 55, y + 34], fill=WHITE)
    draw.rectangle([x + 25, y + 38, x + 39, y + 54], fill=WHITE)
    draw.rectangle([x + 4, y + 11, x + 60, y + 18], fill=RED)
    draw.polygon([(x + 44, y + 2), (x + 58, y + 6), (x + 58, y + 17),
                  (x + 51, y + 23), (x + 44, y + 17)], fill=GOLD)


def icon_city(draw, x, y, s):
    """City buildings with a red explosion burst (kept clear of the text)."""
    draw.rectangle([x + 4, y + 24, x + 22, y + 58], fill=NAVY)
    draw.rectangle([x + 26, y + 12, x + 44, y + 58], fill=NAVY)
    draw.rectangle([x + 48, y + 32, x + 62, y + 58], fill=NAVY)
    for wx in (9, 31, 52):
        for wy in (28, 40):
            draw.rectangle([x + wx, y + wy, x + wx + 6, y + wy + 6],
                           fill=GOLD)
    cx, cy = x + 46, y + 10
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=ORANGE)


ICONS = {
    "refinery": icon_refinery,
    "rocket": icon_rocket,
    "court": icon_court,
    "shop": icon_shop,
    "city": icon_city,
}

STORIES = [
    ("refinery", "HOUTHIS HIT SAUDI OIL AND RIYADH",
     "Aramco's Ras Tanura refinery attacked; fires reported. "
     "Riyadh strike injured 11."),
    ("rocket", "FIRST PAKISTANI IN SPACE",
     "China's Shenzhou-24 docked at its space station with "
     "Pakistan's first astronaut."),
    ("court", "HUAWEI FOUND GUILTY IN U.S. COURT",
     "Guilty of trade-secret theft conspiracy and bank fraud; "
     "cleared of racketeering."),
    ("shop", "CARTAGENA HOSTAGES FREED",
     "Raid ends supermarket siege: all remaining hostages freed "
     "alive, one attacker killed."),
    ("city", "RUSSIA STRIKES ODESA AND KYIV",
     "Two killed, three hurt in Odesa region, a child among them; "
     "Kyiv flats hit, two hurt."),
]

TICKER = [
    "COP31 climate talks fail to reach agreement \u2014 Pope Leo XIV voices concern",
    "Sudan: RSF drone strikes kill 19 civilians, wound 20",
    "Israel kills Hamas colonel Mohammad Abuelouf in Gaza",
    "Fuel tanker fire near Cairo kills at least 31",
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_title = font(SERIF_B, 58)
    f_date = font(SANS_B, 44)
    f_hero_head = font(SANS_B, 42)
    f_hero_sum = font(SANS, 23)
    f_tag = font(SANS_B, 22)
    f_strip_head = font(SANS_B, 22)
    f_strip_sum = font(SANS, 19)
    f_section = font(SANS_B, 22)
    f_tick_head = font(SANS_B, 21)
    f_tick = font(SANS, 20)

    # ---------- masthead ----------
    d.line([(MARGIN, 18), (W - MARGIN, 18)], fill=INK, width=4)
    title = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(title, font=f_title)) / 2, 30),
           title, font=f_title, fill=NAVY)
    date = "WEDNESDAY 25 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=f_date)) / 2, 104),
           date, font=f_date, fill=RED)
    d.line([(MARGIN, 158), (W - MARGIN, 158)], fill=INK, width=2)
    d.line([(MARGIN, 163), (W - MARGIN, 163)], fill=INK, width=2)

    # ---------- hero panel ----------
    hx0, hy0, hx1, hy1 = MARGIN, 176, W - MARGIN, 492
    d.rectangle([hx0, hy0, hx1, hy1], outline=NAVY, width=3, fill=LIGHT_NAVY)
    draw_tanker_scene(d, hx0 + 3, hy0 + 3, hx1 - 3, hy0 + 127)
    tag = "BREAKING"
    tw = d.textlength(tag, font=f_tag)
    d.rectangle([hx0 + 14, hy0 + 14, hx0 + 14 + tw + 24, hy0 + 14 + 34],
                fill=RED)
    d.text((hx0 + 26, hy0 + 18), tag, font=f_tag, fill=WHITE)
    hero_head = "TWO OIL TANKERS HIT BY MINES IN STRAIT OF HORMUZ"
    lines = wrap(d, hero_head, f_hero_head, hx1 - hx0 - 48)
    y = text_block(d, (0, hy0 + 136), lines, f_hero_head, NAVY, 50,
                   align="center", anchor_x=W / 2)
    hero_sum = ("Iran's Revolutionary Guard said two tankers struck naval mines, "
                "exploded and caught fire while transiting an unauthorised route.")
    lines = wrap(d, hero_sum, f_hero_sum, hx1 - hx0 - 80)
    text_block(d, (0, y + 4), lines, f_hero_sum, INK, 30,
               align="center", anchor_x=W / 2)

    # ---------- section label (rule starts after the measured text) ----------
    label = "ALSO TODAY"
    lw = d.textlength(label, font=f_section)
    d.text((MARGIN, 506), label, font=f_section, fill=NAVY)
    d.line([(MARGIN + lw + 14, 517), (W - MARGIN, 517)], fill=NAVY, width=2)

    # ---------- story strips: icon + headline + one-line summary ----------
    strip_h, strip_gap = 56, 5
    y = 534
    for icon, head, summ in STORIES:
        d.rectangle([MARGIN, y, W - MARGIN, y + strip_h], outline=NAVY,
                    width=2, fill=WHITE)
        ICONS[icon](d, MARGIN + 8, y + 4, 48)
        tx = MARGIN + 72
        d.text((tx, y + 4), head, font=f_strip_head, fill=INK)
        d.text((tx, y + 30), summ, font=f_strip_sum, fill=GREY)
        y += strip_h + strip_gap

    # ---------- ticker strip ----------
    tx0, ty0, tx1, ty1 = MARGIN, 848, W - MARGIN, 1006
    d.rectangle([tx0, ty0, tx1, ty1], fill=NAVY)
    d.text((tx0 + 16, ty0 + 10), "THE REST OF THE DAY",
           font=f_tick_head, fill=GOLD)
    y = ty0 + 40
    for item in TICKER:
        d.ellipse([tx0 + 18, y + 8, tx0 + 26, y + 16], fill=RED)
        d.text((tx0 + 36, y), item, font=f_tick, fill=WHITE)
        y += 28

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")


if __name__ == "__main__":
    main()
