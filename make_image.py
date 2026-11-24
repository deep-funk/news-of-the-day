#!/usr/bin/env python3
"""Render the 24 November 2026 front page. Deterministic, no clock/network."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 54
MEASURE = W - 2 * M
INK = "#101012"
PAPER = "#f8f3e6"
ACCENT = "#aa2020"
HAIR = "#c6c1b8"
GREY = "#605b53"
FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
BOLD = str(FONT_DIR / "LiberationSans-Bold.ttf")
REG = str(FONT_DIR / "LiberationSans-Regular.ttf")

LEAD = "Pacific nations go it alone as COP31 collapses"
CAPTION = "LONGEST-EVER UN CLIMATE TALKS END WITHOUT A DEAL"
COLUMNS = [
    ("CLIMATE", "Marshall Islands: 'We have been let down on all sides.'"),
    ("MARKETS", "Chips whipsaw as Nvidia's Huang returns"),
    ("ASIA", "Seoul names new unification and foreign ministers"),
]
BARS = (47, 71, 56, 93, 132, 102, 166, 121, 196, 154, 231, 180, 261, 216, 280, 242)

OUT = Path(__file__).resolve().parent / "entry.png"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def wrap(text: str, f: ImageFont.FreeTypeFont, measure: int) -> list[str]:
    lines: list[str] = []
    cur = ""
    for word in text.split():
        cand = (cur + " " + word).strip()
        if f.getlength(cand) <= measure or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def fit_lead(text: str, measure: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Start at 70, step down only until 2-3 wide lines with no lone word."""
    floor = 0.88 * measure
    for size in range(70, 30, -1):
        f = font(BOLD, size)
        lines = wrap(text, f, measure)
        if not 2 <= len(lines) <= 3:
            continue
        if any(len(line.split()) < 2 for line in lines):
            continue
        widest = max(f.getlength(line) for line in lines)
        if floor <= widest <= measure:
            return f, lines
    raise RuntimeError("no lead size fits")


def justify(d: ImageDraw.ImageDraw, f, line: str, x: int, y: int, measure: int) -> None:
    words = line.split()
    if len(words) == 1:
        d.text((x, y), line, font=f, fill=INK)
        return
    natural = sum(f.getlength(w) for w in words)
    gap = (measure - natural) / (len(words) - 1)
    cx = x
    for w in words:
        d.text((cx, y), w, font=f, fill=INK)
        cx += f.getlength(w) + gap


def main() -> None:
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    right = W - M

    d.rectangle((0, 0, W, 12), fill=INK)

    d.text((M, 40), "THE DAY", font=font(BOLD, 50), fill=INK)
    f_word = font(BOLD, 22)
    d.text((right - f_word.getlength("WORLD NEWS"), 44), "WORLD NEWS", font=f_word, fill=ACCENT)
    f_date = font(REG, 20)
    d.text((right - f_date.getlength("24 NOVEMBER 2026"), 74), "24 NOVEMBER 2026",
           font=f_date, fill=GREY)

    d.rectangle((M, 110, right, 113), fill=INK)

    f_lead, lines = fit_lead(LEAD, MEASURE)
    lead_top = 138
    lead_step = 84
    for i, line in enumerate(lines):
        y = lead_top + i * lead_step
        if i < len(lines) - 1:
            justify(d, f_lead, line, M, y, MEASURE)
        else:
            d.text((M, y), line, font=f_lead, fill=INK)

    y = lead_top + len(lines) * lead_step - (lead_step - 70) + 26
    d.rectangle((M, y, right, y), fill=HAIR)

    base = y + 22 + 280
    n = len(BARS)
    gap = 18.0
    bw = (MEASURE - gap * (n - 1)) / n
    for i, h in enumerate(BARS):
        x0 = M + i * (bw + gap)
        colour = ACCENT if i >= n - 3 else INK
        d.rectangle((round(x0), base - h, round(x0 + bw) - 1, base - 1), fill=colour)
    d.rectangle((M, base, right, base + 1), fill=INK)

    f_tick = font(REG, 12)
    for label, x in (("00", M), ("06", M + MEASURE / 3), ("12", M + MEASURE * 2 / 3)):
        d.text((round(x), base + 12), label, font=f_tick, fill=GREY)
    d.text((right - f_tick.getlength("18"), base + 12), "18", font=f_tick, fill=GREY)

    f_cap = font(REG, 17)
    d.text((M, base + 40), CAPTION, font=f_cap, fill=GREY)

    rule = base + 78
    d.rectangle((M, rule, right, rule + 3), fill=INK)

    gutter = 25
    col_w = (MEASURE - 2 * gutter) // 3
    col_top = rule + 26
    f_kick = font(BOLD, 13)
    f_body = font(REG, 21)
    for ci, (kicker, body) in enumerate(COLUMNS):
        x = M + ci * (col_w + gutter)
        d.rectangle((x, col_top + 4, x + 9, col_top + 13), fill=ACCENT)
        d.text((x + 16, col_top - 1), kicker, font=f_kick, fill=INK)
        by = col_top + 30
        for bline in wrap(body, f_body, col_w):
            d.text((x, by), bline, font=f_body, fill=INK)
            by += 28

    close = 920
    d.rectangle((M, close, right, close + 3), fill=INK)
    f_foot = font(REG, 17)
    foot = "DRAWN FROM THE DAY'S REPORTING \u00b7 NO NETWORK"
    d.text((M, close + 14), foot, font=f_foot, fill=GREY)

    img.save(OUT, "PNG", optimize=True)


if __name__ == "__main__":
    main()
