#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news front page, v5 (800x1024 PNG).

TOTAL REDESIGN (v5) of the make.fun news-image entry.

Design (from v5-design-brief.md): one dominant lead (Hormuz), two large
secondary (Shenzhou-24, US tariffs), six medium secondary, news briefs with
REAL mini illustrations, dotted/pale world map with numbered pins, red
DATE CHECK footer. Warm ivory paper, six-column grid, 12px gutters,
~28px side margins. Serif headlines (DejaVu Serif Bold), sans body
(DejaVu Sans). Four type sizes only: 34 / 28 / 22 / 18. All text >= 18px.
Every story in its own hairline-bordered box with >= 12px internal
padding. No text outside its box, no text touching a border, no
illustration covering text.

SPACE NOTE (measured, 2026-11-26): at 800x1024 with >= 18px text and the
researcher's FULL summaries, the canvas cannot hold all 25 stories with
real whitespace -- the full 25-story build needs 3184px of height against
1012px available, and even the 9-feature core (3 leads + 6 medium, no
briefs, no map) overflows by 439px with full art/metas, and by 119px in
its most stripped form (no metas, no medium art/kickers, no region bar,
single-line stats, short footer). The brief's own rule applies: CUT
BEFORE SHRINKING. This build therefore shows 6 stories -- all 3 leads
plus medium S1/S2/S4 (best regional breadth: Middle East, Latin America,
Africa; Kospi -6.2% and US GDP 4.3% survive in the stat strip) -- with
full summaries, real art, the complete header and the DATE CHECK footer.
Cut: medium S3/S5/S6, all 16 briefs (cut order B16, B11, B15, B14, B9,
B13, B6, B12, then the rest) and the world map. Per-story source lines
are omitted (the footer credits Reuters, AP, AFP, Al Jazeera, WSJ, CNN).
CONFIG below records what is shown; the script prints the exact height
budget and refuses to render overflowing.

Deterministic: fixed fonts, fixed geometry, fixed image assets, fixed
grain seed, no timestamps, no network. Running this script twice
produces byte-identical output. Only the Python standard library and
Pillow are used. All illustrations are AI-generated text-free editorial
art; every word on the page is drawn by this script.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 800, 1024
MX = 28                      # side margins
TOP, BOT = 10, 10
CW = W - 2 * MX              # 744, content width
GAP = 12                     # gutter between boxes
SEC = 6                      # gap between sections
PAD = 12                     # internal box padding

PAPER = (247, 242, 230)      # warm ivory / cream paper
INK = (18, 18, 18)           # near-black ink
NAVY = (27, 58, 92)          # dark navy
BURG = (139, 30, 35)         # burgundy (accents, kickers)
RED = (185, 28, 28)          # breaking red (DATE CHECK outline)
GREY = (74, 74, 70)          # secondary text
HAIR = (168, 164, 152)       # hairline borders
GOLD = (176, 141, 87)        # muted gold
MAPFILL = (190, 196, 202)    # pale continents
AMBER = (198, 108, 24)
TEAL = (24, 110, 96)
BROWN = (122, 72, 40)
BLUE = (52, 96, 168)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_I = os.path.join(FONT_DIR, "DejaVuSerif-Italic.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# --- type sizes: 34 / 28 / 22 / 18 only -------------------------------
SZ_DATE, SZ_MAST, SZ_LEAD, SZ_BODY = 34, 28, 22, 18
# leading per size
LD = {34: 38, 28: 32, 22: 25, 18: 21}     # headlines / kickers
LD_BODY = 19                              # 18px body summaries


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


def text_block(draw, xy, lines, fnt, fill, leading):
    """Draw wrapped lines starting at xy. Returns y after the last line."""
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def box(d, x, y, w, h, outline=HAIR, width=1):
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=outline, width=width)


def cover(src, tw, th):
    """Centre-crop the source to the target aspect, then resize."""
    sw, sh = src.size
    ta, sa = tw / th, sw / sh
    if sa > ta:  # source wider: crop left/right
        nw = int(sh * ta)
        x0 = (sw - nw) // 2
        src = src.crop((x0, 0, x0 + nw, sh))
    else:        # source taller: crop top/bottom
        nh = int(sw / ta)
        y0 = (sh - nh) // 2
        src = src.crop((0, y0, sw, y0 + nh))
    return src.resize((tw, th), Image.LANCZOS)


# mini-abuelouf.png has a ~110px warm-ivory border baked in; crop it out
# (art region measured 2026-11-26: x 110..1810, y 110..1170 of 1920x1280).
ABUELOUF_CROP = (110, 110, 1810, 1170)


def art(name, tw, th):
    """Load an asset and cover-crop it to (tw, th)."""
    src = Image.open(os.path.join(HERE, "assets", name))
    if name == "mini-abuelouf.png":
        src = src.crop(ABUELOUF_CROP)
    return cover(src, tw, th)


# ---------------------------------------------------------------- data ---

REGIONS = [
    ("MIDDLE EAST", BURG), ("ASIA", AMBER), ("EUROPE", NAVY),
    ("AMERICAS", TEAL), ("AFRICA", BROWN), ("OCEANIA", BLUE),
]

# 6 verified stats: (number, label) -- two-line cells
STATS = [
    ("2", "TANKERS"), ("-6.2%", "KOSPI"), ("31", "KILLED"),
    ("4.3%", "US GDP"), ("$94.61", "BRENT"), ("\u00a32,166", "UK CAP"),
]

# Stories: (tag, asset, kicker, headline, summary, meta, lon, lat)
# kicker = "REGION \u00b7 CATEGORY"; meta = source / attribution note.
LEAD = (
    "L1", "hero.png", "MIDDLE EAST \u00b7 CONFLICT",
    "Iran says two tankers hit mines in Hormuz",
    "Iran's Revolutionary Guards say two tankers struck naval mines, "
    "exploded and caught fire in the Strait of Hormuz.",
    "Reuters \u00b7 Iranian claim, unverified \u00b7 Brent rose 3.5%",
    56.5, 26.5,
)

SECONDARY = [
    ("L2", "feature-space.png", "ASIA \u00b7 SCIENCE / SPACE",
     "Shenzhou-24 docks with first Pakistani in space",
     "China's Shenzhou-24 launched and docked at Tiangong carrying "
     "Muhammad Zeeshan Ali, the first Pakistani in orbit.",
     "Xinhua / China Manned Space Agency", 100.3, 40.9),
    ("L3", "feature-tariffs.png", "NORTH AMERICA / GLOBAL \u00b7 ECONOMY",
     "US proposes tariffs on 14 economies",
     "Washington proposes new tariffs on 14 trading partners over "
     "excess factory capacity, including 10% on Brazilian aircraft.",
     "Reuters \u00b7 Proposes, not imposes \u00b7 Hearing 14 Jan 2027",
     -77.0, 38.9),
]

MEDIUM = [
    ("S1", "feature-houthis.png", "MIDDLE EAST \u00b7 CONFLICT",
     "Houthis claim Ras Tanura refinery strike",
     "Houthis say they hit Saudi Arabia's largest refinery, causing "
     "fires; coalition says four drones were downed, no hit confirmed.",
     "Reuters \u00b7 Claim", 50.2, 26.6),
    ("S2", "feature-cartagena.png", "LATIN AMERICA \u00b7 CRIME",
     "Cartagena hostages freed in dawn raid",
     "Security forces stormed an \u00c9xito supermarket, freeing all "
     "remaining hostages alive; one gunman was killed.",
     "Reuters / AP", -75.5, 10.4),
    ("S3", "feature-kospi.png", "ASIA \u00b7 ECONOMY",
     "Asian chip stocks tumble as Kospi falls 6.2%",
     "South Korea's Kospi fell 6.2% to a 10-month low; Samsung fell "
     "9.9% and SK Hynix 11%.",
     "WSJ / CNN / Yonhap", 127.0, 37.5),
    ("S4", "feature-cairo.png", "AFRICA \u00b7 DISASTER",
     "Cairo fuel-tanker fire kills 31",
     "A fuel tanker overturned and exploded on Cairo's Ring Road, "
     "killing 31 people and injuring 21.",
     "CNN / AP / BBC", 31.2, 30.0),
    ("S5", "feature-macys.png", "NORTH AMERICA \u00b7 CULTURE",
     "Macy's Thanksgiving Parade postponed to Saturday",
     "The New York parade was postponed for the first time in 100 "
     "years as a nor'easter threatened 60 mph gusts.",
     "WSJ / NY Post / The Times", -74.0, 40.7),
    ("S6", "feature-gdp.png", "NORTH AMERICA \u00b7 ECONOMY",
     "US economy grew 4.3% as inflation hit 3.8%",
     "US Q3 GDP was revised up to 4.3% annualised, while October PCE "
     "inflation rose to 3.8%.",
     "Reuters / CNN (BEA)", -80.0, 36.0),
]

# Briefs in display order B1..B16. CUT_ORDER is the brief's cut order;
# CONFIG["briefs"] lists the tags actually shown (subset, in order).
BRIEFS = [
    ("B1", "mini-sudan.png", "AFRICA \u00b7 CONFLICT",
     "Sudan RSF drone strikes kill 19",
     "RSF drones hit homes in Damazin, Blue Nile state, killing 19 "
     "civilians and wounding 20, a rights group said.",
     "Reuters", 34.5, 11.8),
    ("B2", "mini-abuelouf.png", "MIDDLE EAST \u00b7 CONFLICT",
     "Israel kills Hamas colonel Abuelouf in Gaza",
     "An Israeli airstrike early Wednesday killed Hamas security "
     "chief Mohammad Abuelouf, his wife and two children.",
     "Reuters", 34.5, 31.5),
    ("B3", "feature-energy.png", "EUROPE \u00b7 ECONOMY",
     "UK energy cap to rise 26% to \u00a32,166",
     "Ofgem announced the energy price cap rises 26% from January, "
     "adding \u00a3443 a year for a typical household.",
     "Ofgem via Morningstar / The Times", -0.1, 51.5),
    ("B4", "feature-bogor.png", "ASIA \u00b7 DISASTER",
     "Bogor gold mine flood: 9 dead, 17 trapped",
     "Rescuers recovered nine bodies from a flooded illegal gold mine "
     "in Bogor; 17 miners are still believed trapped.",
     "AP", 106.8, -6.6),
    ("B5", "mini-bangladesh.png", "ASIA \u00b7 ECONOMY",
     "Bangladesh garment wage up 36% to $139",
     "Bangladesh's wage board set garment workers' minimum pay at "
     "17,000 taka a month after weeks of protests.",
     "AFP / Reuters", 90.4, 23.8),
    ("B6", "mini-abrego.png", "N. AMERICA / EUROPE \u00b7 POLITICS",
     "Abrego Garcia lands in Spain",
     "Kilmar Abrego Garcia arrived in Madrid after voluntarily "
     "leaving the US, ending a near-two-year deportation battle.",
     "Reuters / AP / NPR", -3.7, 40.4),
    ("B7", "mini-hodeidah.png", "MIDDLE EAST \u00b7 CONFLICT",
     "Coalition jets strike Hodeidah port",
     "The Saudi-led coalition struck Yemen's Hodeidah port early "
     "Wednesday after ordering civilians to evacuate.",
     "Saudi Press Agency / Al Jazeera", 42.8, 14.8),
    ("B8", "mini-trump-rutte.png", "N. AMERICA / EUROPE \u00b7 POLITICS",
     "Trump and NATO chief warn Russia on Ukraine",
     "Trump and Mark Rutte met at Mar-a-Lago and urged Russia not to "
     "take actions that widen the Ukraine war.",
     "Reuters", -80.0, 26.8),
    ("B9", "mini-lille.png", "EUROPE \u00b7 SPORT",
     "Lille stun Bayern in Champions League",
     "Lille beat Bayern Munich 2\u20131; holders PSG were held 2\u20132 "
     "by Roma, ending their perfect record.",
     "UEFA", 3.1, 50.6),
    ("B10", "mini-nvidia.png", "NORTH AMERICA \u00b7 BUSINESS",
     "Nvidia slides as S&P warns on rating",
     "S&P put Nvidia's AA credit rating on watch for a downgrade "
     "over governance; shares fell 3.9% to $149.30.",
     "Reuters / Barron's", -121.5, 37.2),
    ("B11", "mini-anthropic.png", "NORTH AMERICA \u00b7 BUSINESS",
     "Anthropic sinks further below IPO price",
     "Anthropic shares slid further below their $83 IPO price amid "
     "the AI sell-off, trading near $77 on Wednesday.",
     "MarketWatch", -122.4, 37.8),
    ("B12", "mini-brent.png", "GLOBAL \u00b7 ECONOMY",
     "Brent oil jumps 3.5% to $94.61",
     "Brent crude settled at $94.61 a barrel on Wednesday as Gulf "
     "attacks stoked supply fears.",
     "Reuters", None, None),
    ("B13", "mini-nigeria.png", "AFRICA \u00b7 CONFLICT",
     "Militants kill at least 30 in Nigeria",
     "Suspected militants killed at least 30 people and burned homes "
     "in villages in Nigeria's Niger state, residents said.",
     "Reuters", 6.0, 10.0),
    ("B14", "mini-syria.png", "MIDDLE EAST \u00b7 CONFLICT",
     "IS attack kills two in Syria's Hasaka",
     "An Islamic State attack on a security headquarters in Hasaka "
     "killed two Syrian security personnel and wounded five.",
     "Reuters (Syrian state TV)", 40.7, 36.5),
    ("B15", "mini-next.png", "EUROPE \u00b7 CRIME",
     "Ransomware gang lists Next as victim",
     "The N0n ransomware group listed UK retailer Next on its leak "
     "site, claiming 233GB of data.",
     "ransomware.live / Orbitaley \u00b7 Unverified gang claim",
     0.5, 51.8),
    ("B16", "mini-eu.png", "EUROPE \u00b7 POLITICS",
     "EU proposes \u20ac45bn more for Ukraine",
     "Von der Leyen told the European Parliament the EU should give "
     "Ukraine \u20ac45bn more support in 2027.",
     "European Commission (Strasbourg)", 7.8, 48.6),
]

# Brief cut order from the brief (first = cut first). Remaining briefs
# are cut weakest-first if still over budget.
CUT_ORDER = ["B16", "B11", "B15", "B14", "B9", "B13", "B6", "B12",
             "B10", "B8", "B7", "B5", "B4", "B3", "B2", "B1"]

# ---- CONFIG: what this build shows (tuned to fit 800x1024 cleanly) ---
CONFIG = {
    "region_bar": True,     # colour-coded region bar under the subhead
    "stat_two_line": True,  # stat strip: number over label (else 1 line)
    "lead_image_w": 200,    # lead image width (3:2)
    "sec_band": 36,         # secondary image band height
    "med_band": 28,         # medium image band height (0 = no image)
    "med_kicker": True,     # medium stories show kicker line
    "show_meta": False,     # per-story source line (footer credits sources)
    "footer_short": True,   # compressed DATE CHECK wording
    "show_map": False,      # WHERE IT HAPPENED map (cut for space)
    "medium": ["S1", "S2", "S4"],  # medium tags shown (see note above)
    "briefs": [],           # brief tags shown, in display order
}

FOOTER_LINES_SHORT = [
    ("NOT 25 NOV \u2014 LEFT OUT: Huawei verdict (Tue 24) \u00b7 Riyadh "
     "strike, 11 hurt (Tue 24) \u00b7 COP31 no deal (Sun 22) \u00b7 "
     "Kr\u00e1kow shooting (Sat 7)", RED),
    ("ALSO: Odesa/Kyiv \u00b7 CIA+ODNI \u00b7 Novaya Gazeta \u00b7 Huang "
     "apology \u00b7 Ahmadi flogging \u00b7 Korea AI-cheater reward "
     "(23\u201324 Nov; Novaya Gazeta 30 Oct)", INK),
    ("Sources: Reuters, AP, AFP, Al Jazeera, WSJ, CNN", GREY),
]

FOOTER_LINES = [
    ("NOT 25 NOVEMBER \u2014 LEFT OUT: Huawei verdict (Tue 24 Nov) \u00b7 "
     "Riyadh tower strike, 11 hurt (Tue 24 Nov) \u00b7 COP31 no deal "
     "(Sun 22 Nov) \u00b7 Kr\u00e1kow shooting (Sat 7 Nov)", RED),
    ("ALSO LEFT OUT: Odesa/Kyiv strikes (Tue 24 Nov) \u00b7 CIA + ODNI "
     "breach (Tue 24 Nov) \u00b7 Novaya Gazeta closure (30 Oct) \u00b7 "
     "Jensen Huang apology (Mon 23 Nov) \u00b7 Parastoo Ahmadi flogging "
     "(Mon 23 Nov) \u00b7 South Korea AI-cheater reward (Mon 23 Nov)",
     INK),
    ("Sources: Reuters, AP, AFP, Al Jazeera, WSJ, CNN", GREY),
]

# World map: rough continent polygons in (lon, lat) (from v4).
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


# ------------------------------------------------------------- layout ---

class Layout:
    """Measures every section from real text wraps, then draws."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.img = Image.new("RGB", (W, H), PAPER)
        self.d = ImageDraw.Draw(self.img)
        self.y = TOP
        self.log = []
        self.story_no = 0
        self.shown = []   # (number, tag, lon, lat) for map pins

    # -- fonts ------------------------------------------------------
    def f(self, path, size):
        return font(path, size)

    def note(self, name, h):
        self.log.append((name, h))

    def next_no(self, tag, lon, lat):
        self.story_no += 1
        if lon is not None:
            self.shown.append((self.story_no, tag, lon, lat))
        return self.story_no

    # -- header -----------------------------------------------------
    def banner(self, n_stories, n_regions):
        d = self.d
        txt = ("THE WORLD IN ONE DAY \u2014 %d STORIES \u00b7 %d REGIONS "
               "\u00b7 WEDNESDAY 25 NOVEMBER 2026" % (n_stories, n_regions))
        fnt = self.f(SANS_B, SZ_BODY)
        if d.textlength(txt, font=fnt) > CW:
            txt = ("THE WORLD IN ONE DAY \u2014 %d STORIES \u00b7 %d REGIONS "
                   "\u00b7 25 NOVEMBER 2026" % (n_stories, n_regions))
        d.rectangle([MX, self.y, W - MX, self.y + 20], fill=NAVY)
        d.text(((W - d.textlength(txt, font=fnt)) / 2, self.y + 1),
               txt, font=fnt, fill=PAPER)
        self.note("banner", 20)
        self.y += 20 + 4

    def masthead(self):
        d = self.d
        fnt = self.f(SERIF_B, SZ_MAST)
        txt = "THE WORLD IN ONE DAY"
        d.text(((W - d.textlength(txt, font=fnt)) / 2, self.y),
               txt, font=fnt, fill=INK)
        self.y += LD[SZ_MAST] + 2
        fnt = self.f(SERIF_B, SZ_DATE)
        txt = "Wednesday, 25 November 2026"
        d.text(((W - d.textlength(txt, font=fnt)) / 2, self.y),
               txt, font=fnt, fill=INK)
        self.y += LD[SZ_DATE] + 2
        fnt = self.f(SERIF_I, SZ_BODY)
        txt = ("Hormuz tankers mined \u00b7 Shenzhou-24 docks "
               "\u00b7 US tariffs on 14 economies")
        d.text(((W - d.textlength(txt, font=fnt)) / 2, self.y),
               txt, font=fnt, fill=BURG)
        self.y += LD[SZ_BODY] + 4
        self.note("masthead+date+subhead", self.y - TOP - 24)

    def region_bar(self):
        if not self.cfg["region_bar"]:
            return
        d = self.d
        fnt = self.f(SANS_B, SZ_BODY)
        parts, total = [], 0
        for name, col in REGIONS:
            w = d.textlength(name, font=fnt) + 20
            parts.append((name, col, w))
            total += w
        total += 24 * (len(parts) - 1)
        x = (W - total) / 2
        for name, col, w in parts:
            d.rectangle([x + 2, self.y + 3, x + 14, self.y + 15], fill=col)
            d.text((x + 18, self.y), name, font=fnt, fill=INK)
            x += w + 24
        self.note("region bar", LD[SZ_BODY])
        self.y += LD[SZ_BODY] + 4

    def stat_strip(self):
        d = self.d
        two = self.cfg["stat_two_line"]
        cell_w = (CW - 5 * GAP) / 6
        h = 48 if two else 26
        f_num = self.f(SANS_B, SZ_BODY)
        f_lab = self.f(SANS, SZ_BODY)
        for i, (num, lab) in enumerate(STATS):
            x = MX + i * (cell_w + GAP)
            box(d, x, self.y, cell_w, h)
            if two:
                d.text((x + (cell_w - d.textlength(num, font=f_num)) / 2,
                        self.y + 3), num, font=f_num, fill=NAVY)
                d.text((x + (cell_w - d.textlength(lab, font=f_lab)) / 2,
                        self.y + 24), lab, font=f_lab, fill=GREY)
            else:
                txt = num + " " + lab
                d.text((x + (cell_w - d.textlength(txt, font=f_num)) / 2,
                        self.y + 3), txt, font=f_num, fill=INK)
        self.note("stat strip", h)
        self.y += h + SEC

    # -- stories ----------------------------------------------------
    def kicker_text(self, num, kicker):
        if not kicker and num is None:
            return ""
        if num is None:
            return kicker
        if not kicker:
            return "%d" % num
        return "%d \u00b7 %s" % (num, kicker)

    def kicker_line(self, d, x, y, num, kicker, w):
        txt = self.kicker_text(num, kicker)
        if not txt:
            return y
        fnt = self.f(SANS_B, SZ_BODY)
        lines = wrap(d, txt, fnt, w)
        return text_block(d, (x, y), lines, fnt, BURG, LD[SZ_BODY])

    def kicker_h(self, d, num, kicker, w):
        """Pixel height of the (possibly multi-line) kicker, incl. gap."""
        txt = self.kicker_text(num, kicker)
        if not txt:
            return 0
        fnt = self.f(SANS_B, SZ_BODY)
        return len(wrap(d, txt, fnt, w)) * LD[SZ_BODY] + 4

    def lead(self, story):
        d = self.d
        tag, asset, kicker, headl, summ, meta, lon, lat = story
        num = self.next_no(tag, lon, lat)
        iw = self.cfg["lead_image_w"]
        ih = int(iw * 2 / 3)
        tx = MX + PAD + iw + 10
        tw = W - MX - PAD - tx
        f_head = self.f(SERIF_B, SZ_LEAD)
        f_sum = self.f(SANS, SZ_BODY)
        f_meta = self.f(SANS, SZ_BODY)
        hl = wrap(d, headl, f_head, tw)
        sl = wrap(d, summ, f_sum, tw)
        ml = wrap(d, meta, f_meta, tw)
        knum = num if self.cfg["show_map"] else None
        text_h = (self.kicker_h(d, knum, "TOP STORY \u00b7 " + kicker, tw)
                  + len(hl) * LD[SZ_LEAD] + 4
                  + len(sl) * LD_BODY
                  + (4 + len(ml) * LD_BODY if self.cfg["show_meta"] else 0))
        h = max(ih, text_h) + 2 * PAD
        box(d, MX, self.y, CW, h)
        self.img.paste(art(asset, iw, ih), (MX + PAD, self.y + (h - ih) // 2))
        yy = self.y + PAD
        yy = self.kicker_line(d, tx, yy,
                              num if self.cfg["show_map"] else None,
                              "TOP STORY \u00b7 " + kicker, tw)
        yy += 4
        yy = text_block(d, (tx, yy), hl, f_head, INK, LD[SZ_LEAD])
        yy += 4
        yy = text_block(d, (tx, yy), sl, f_sum, GREY, LD_BODY)
        if self.cfg["show_meta"]:
            yy += 4
            text_block(d, (tx, yy), ml, f_meta, NAVY, LD_BODY)
        self.note("lead %s" % tag, h)
        self.y += h + SEC

    def secondary(self, stories):
        d = self.d
        cell_w = (CW - GAP) / 2
        band = self.cfg["sec_band"]
        f_kick = self.f(SANS_B, SZ_BODY)
        f_head = self.f(SERIF_B, SZ_BODY)
        f_sum = self.f(SANS, SZ_BODY)
        heights = []
        for s in stories:
            tag, asset, kicker, headl, summ, meta, lon, lat = s
            tw = cell_w - 2 * PAD
            hl = wrap(d, headl, f_head, tw)
            sl = wrap(d, summ, f_sum, tw)
            ml = wrap(d, meta, f_sum, tw)
            knum = 1 if self.cfg["show_map"] else None
            heights.append(band + 6
                           + self.kicker_h(d, knum, kicker, tw)
                           + len(hl) * LD[SZ_BODY] + 4
                           + len(sl) * LD_BODY
                           + (4 + len(ml) * LD_BODY
                              if self.cfg["show_meta"] else 0)
                           + PAD)
        h = max(heights)
        for i, s in enumerate(stories):
            tag, asset, kicker, headl, summ, meta, lon, lat = s
            num = self.next_no(tag, lon, lat)
            x = MX + i * (cell_w + GAP)
            box(d, x, self.y, cell_w, h)
            self.img.paste(art(asset, int(cell_w) - 2, band),
                           (int(x) + 1, self.y + 1))
            tw = cell_w - 2 * PAD
            yy = self.y + band + 6
            yy = self.kicker_line(d, x + PAD, yy,
                                  num if self.cfg["show_map"] else None,
                                  kicker, tw)
            yy += 4
            yy = text_block(d, (x + PAD, yy),
                            wrap(d, headl, f_head, tw), f_head, INK,
                            LD[SZ_BODY])
            yy += 4
            yy = text_block(d, (x + PAD, yy),
                            wrap(d, summ, f_sum, tw), f_sum, GREY, LD_BODY)
            if self.cfg["show_meta"]:
                yy += 4
                text_block(d, (x + PAD, yy), wrap(d, meta, f_sum, tw),
                           f_sum, NAVY, LD_BODY)
        self.note("secondary L2+L3", h)
        self.y += h + SEC

    def medium(self, stories):
        d = self.d
        cell_w = (CW - 2 * GAP) / 3
        band = self.cfg["med_band"]
        show_kick = self.cfg["med_kicker"]
        f_head = self.f(SERIF_B, SZ_BODY)
        f_sum = self.f(SANS, SZ_BODY)
        # measure each row from real wraps; each row is as tall as its
        # tallest story (grid stays aligned)
        nrows = (len(stories) + 2) // 3
        row_h = []
        for r in range(nrows):
            hh = 0
            for s in stories[r * 3:(r + 1) * 3]:
                tag, asset, kicker, headl, summ, meta, lon, lat = s
                tw = cell_w - 2 * PAD
                hl = wrap(d, headl, f_head, tw)
                sl = wrap(d, summ, f_sum, tw)
                ml = wrap(d, meta, f_sum, tw)
                th = (((band + 6) if band else 0)
                      + (self.kicker_h(
                            d, 1 if self.cfg["show_map"] else None,
                            kicker, tw)
                         if show_kick else 0)
                      + len(hl) * LD[SZ_BODY] + 4
                      + len(sl) * LD_BODY
                      + (4 + len(ml) * LD_BODY
                         if self.cfg["show_meta"] else 0)
                      + PAD)
                hh = max(hh, th)
            row_h.append(hh)
        for idx, s in enumerate(stories):
            r, c = divmod(idx, 3)
            tag, asset, kicker, headl, summ, meta, lon, lat = s
            num = self.next_no(tag, lon, lat)
            x = MX + c * (cell_w + GAP)
            yy0 = self.y + sum(row_h[:r]) + r * GAP
            box(d, x, yy0, cell_w, row_h[r])
            if band:
                self.img.paste(art(asset, int(cell_w) - 2, band),
                               (int(x) + 1, int(yy0) + 1))
            tw = cell_w - 2 * PAD
            yy = yy0 + (band + 6 if band else PAD)
            if show_kick:
                yy = self.kicker_line(
                    d, x + PAD, yy,
                    num if self.cfg["show_map"] else None, kicker, tw)
                yy += 4
            yy = text_block(d, (x + PAD, yy),
                            wrap(d, headl, f_head, tw), f_head, INK,
                            LD[SZ_BODY])
            yy += 4
            yy = text_block(d, (x + PAD, yy),
                            wrap(d, summ, f_sum, tw), f_sum, GREY, LD_BODY)
            if self.cfg["show_meta"]:
                yy += 4
                text_block(d, (x + PAD, yy), wrap(d, meta, f_sum, tw),
                           f_sum, NAVY, LD_BODY)
        self.note("medium x%d" % len(stories),
                  sum(row_h) + (len(row_h) - 1) * GAP)
        self.y += sum(row_h) + (len(row_h) - 1) * GAP + SEC

    def briefs(self, tags):
        d = self.d
        if not tags:
            return
        items = [b for b in BRIEFS if b[0] in tags]
        cell_w = (CW - GAP) / 2
        f_head = self.f(SERIF_B, SZ_BODY)
        f_sum = self.f(SANS, SZ_BODY)
        # brief box: mini image left, headline + summary right
        iw, ih = 72, 48
        rows = (len(items) + 1) // 2
        row_h = []
        for r in range(rows):
            hh = 0
            for s in items[r * 2:(r + 1) * 2]:
                tag, asset, kicker, headl, summ, meta, lon, lat = s
                tw = cell_w - 2 * PAD - iw - 8
                hl = wrap(d, headl, f_head, tw)
                sl = wrap(d, summ, f_sum, tw)
                th = (PAD + self.kicker_h(
                    d, 1 if self.cfg["show_map"] else None, kicker, tw)
                      + len(hl) * LD[SZ_BODY] + 4
                      + len(sl) * LD_BODY + PAD)
                hh = max(hh, th, ih + 2 * PAD)
            row_h.append(hh)
        for idx, s in enumerate(items):
            r, c = divmod(idx, 2)
            tag, asset, kicker, headl, summ, meta, lon, lat = s
            num = self.next_no(tag, lon, lat)
            x = MX + c * (cell_w + GAP)
            yy0 = self.y + sum(row_h[:r]) + r * GAP
            box(d, x, yy0, cell_w, row_h[r])
            self.img.paste(art(asset, iw, ih),
                           (int(x) + PAD, int(yy0) + PAD))
            tx = x + PAD + iw + 8
            tw = cell_w - 2 * PAD - iw - 8
            yy = yy0 + PAD
            yy = self.kicker_line(d, tx, yy,
                                  num if self.cfg["show_map"] else None,
                                  kicker, tw)
            yy += 4
            yy = text_block(d, (tx, yy), wrap(d, headl, f_head, tw),
                            f_head, INK, LD[SZ_BODY])
            yy += 4
            text_block(d, (tx, yy), wrap(d, summ, f_sum, tw), f_sum,
                       GREY, LD_BODY)
        self.note("briefs x%d" % len(items), sum(row_h) + (rows - 1) * GAP)
        self.y += sum(row_h) + (rows - 1) * GAP + SEC

    def section_head(self, text):
        d = self.d
        fnt = self.f(SANS_B, SZ_BODY)
        d.text((MX, self.y), text, font=fnt, fill=NAVY)
        lw = d.textlength(text, font=fnt)
        d.line([(MX + lw + 12, self.y + 11), (W - MX, self.y + 11)],
               fill=NAVY, width=2)
        self.y += LD[SZ_BODY] + 4

    # -- map --------------------------------------------------------
    def world_map(self):
        d = self.d
        self.section_head("WHERE IT HAPPENED")
        map_h = 64
        box(d, MX, self.y, CW, map_h)
        mx0, mx1 = MX + 6, W - MX - 6
        mw = mx1 - mx0
        my0, my1 = self.y + 4, self.y + map_h - 4

        def px(lon):
            return mx0 + (lon + 180) / 360 * mw

        def py(lat):
            return my0 + (75 - lat) / 130 * (my1 - my0)

        # dotted graticule
        for lon in range(-150, 181, 30):
            x = px(lon)
            for yy in range(int(my0), int(my1), 6):
                d.point((x, yy), fill=(205, 200, 188))
        for lat in range(-60, 76, 30):
            yy = py(lat)
            for xx in range(int(mx0), int(mx1), 6):
                d.point((xx, yy), fill=(205, 200, 188))
        for poly in CONTINENTS:
            pts = [(px(lon), py(lat)) for lon, lat in poly]
            d.polygon(pts, fill=MAPFILL)
        # pins: number in a small navy disc; label offset chosen per pin
        # so no two numbers overlap (offsets hand-tuned for shown set)
        offsets = {
            1: (10, -10), 2: (10, -10), 3: (-26, -10), 4: (10, 6),
            5: (10, -10), 6: (10, -10), 7: (10, -10), 8: (-26, 6),
            9: (10, -10), 10: (10, -10), 11: (-26, -10), 12: (10, 6),
            13: (10, -10), 14: (10, -10), 15: (-26, 6), 16: (10, -10),
            17: (10, -10), 18: (-26, -10), 19: (10, 6), 20: (10, -10),
            21: (-26, -10), 22: (10, -10), 23: (10, -10), 24: (-26, 6),
            25: (10, -10),
        }
        f_pin = self.f(SANS_B, SZ_BODY)
        for num, tag, lon, lat in self.shown:
            x, yy = px(lon), py(lat)
            d.ellipse([x - 9, yy - 9, x + 9, yy + 9], fill=NAVY)
            t = str(num)
            d.text((x - d.textlength(t, font=f_pin) / 2, yy - 9),
                   t, font=f_pin, fill=PAPER)
            dx, dy = offsets.get(num, (10, -10))
            # (label offsets reserved for a future legend; numbers sit
            # inside the discs, so no label can collide with story text)
        self.note("map", LD[SZ_BODY] + 4 + map_h)
        self.y += LD[SZ_BODY] + 4 + map_h + SEC

    # -- footer -----------------------------------------------------
    def footer(self):
        d = self.d
        fnt = self.f(SANS, SZ_BODY)
        f_b = self.f(SANS_B, SZ_BODY)
        lines = []
        for txt, col in (FOOTER_LINES_SHORT if self.cfg["footer_short"]
                         else FOOTER_LINES):
            fnt2 = f_b if col is RED else fnt
            lines.extend((ln, col, fnt2)
                         for ln in wrap(d, txt, fnt2, CW - 2 * PAD))
        h = PAD + len(lines) * LD_BODY + PAD
        d.rectangle([MX, self.y, W - MX, self.y + h], outline=RED, width=2)
        yy = self.y + PAD
        for ln, col, fnt2 in lines:
            d.text((MX + PAD, yy), ln, font=fnt2, fill=col)
            yy += LD_BODY
        self.note("footer (%d lines)" % len(lines), h)
        self.y += h

    # -- grain ------------------------------------------------------
    def grain(self):
        rng = random.Random(20261125)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        for _ in range(2600):
            x = rng.randrange(W)
            y = rng.randrange(H)
            v = rng.choice([(0, 0, 0, 7), (255, 255, 255, 7),
                            (120, 100, 60, 6)])
            od.point((x, y), fill=v)
        self.img = Image.alpha_composite(self.img.convert("RGBA"),
                                         overlay).convert("RGB")
        self.d = ImageDraw.Draw(self.img)


def build(cfg):
    L = Layout(cfg)
    med = [s for s in MEDIUM if s[0] in cfg["medium"]]
    shown_tags = ["L1", "L2", "L3"] + [s[0] for s in med] + cfg["briefs"]
    n_regions = len({r for s in [LEAD] + SECONDARY + med
                     for r in [s[2].split(" \u00b7 ")[0]]} |
                    {b[2].split(" \u00b7 ")[0]
                     for b in BRIEFS if b[0] in cfg["briefs"]})
    L.banner(len(shown_tags), n_regions)
    L.masthead()
    L.region_bar()
    L.stat_strip()
    L.lead(LEAD)
    L.secondary(SECONDARY)
    L.medium(med)
    if cfg["briefs"]:
        L.section_head("NEWS BRIEFS")
        L.briefs(cfg["briefs"])
    if cfg["show_map"]:
        L.world_map()
    L.footer()
    L.grain()
    total = L.y + BOT
    print("=== height budget (canvas %dx%d, limit %d) ===" % (W, H, H - BOT))
    for name, h in L.log:
        print("  %-28s %4d" % (name, h))
    print("  %-28s %4d  (bottom y=%d, limit %d)"
          % ("TOTAL incl. margins", total, L.y, H - BOT))
    print("stories shown: %d (%s)"
          % (len(shown_tags), ", ".join(shown_tags)))
    if L.y > H - BOT:
        raise SystemExit("OVERFLOW by %dpx -- cut more (see CUT_ORDER)"
                         % (L.y - (H - BOT)))
    return L.img


def main():
    img = build(CONFIG)
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
