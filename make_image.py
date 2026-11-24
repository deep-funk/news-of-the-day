#!/usr/bin/env python3
"""Render the 24 November 2026 news image: a missing-poster for the COP31 deal."""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 56
MEASURE = W - 2 * M
PAPER = "#eee6d4"
INK = "#141210"
RED = "#ba1e1c"
FRAME_FILL = "#e2d8c4"
FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
NARROW = str(FONT_DIR / "LiberationSansNarrow-Bold.ttf")
BOLD = str(FONT_DIR / "LiberationSans-Bold.ttf")
REG = str(FONT_DIR / "LiberationSans-Regular.ttf")
OUT = Path(__file__).resolve().parent / "entry.png"

LEFT = [
    ("LAST SEEN", "Antalya, Türkiye — 22 Nov, late"),
    ("HEIGHT", "1.5 °C, give or take a bracket"),
    ("MARKS", "Square brackets, square jaws"),
]
RIGHT = [
    ("WITNESSES", "190 nations, 92,000 delegates"),
    ("BELIEVED", "Still on the premises"),
    ("REWARD", "A livable planet"),
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def fit_missing(text: str, measure: int) -> tuple[ImageFont.FreeTypeFont, float]:
    """Shrink from 200pt by 2 until the tracked word fits the measure."""
    for size in range(200, 30, -2):
        f = font(NARROW, size)
        width = sum(f.getlength(c) for c in text) + 10 * (len(text) - 1)
        if width <= measure:
            return f, width
    raise RuntimeError("MISSING does not fit")


def main() -> None:
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    right = W - M

    # Top bar and appeal header.
    d.rectangle((0, 0, W, 13), fill=INK)
    f_small = font(BOLD, 17)
    d.text((M, 44), "PUBLIC APPEAL  ·  TUESDAY 24 NOVEMBER 2026", font=f_small, fill=RED)
    d.text((right - f_small.getlength("CASE No. COP31"), 44), "CASE No. COP31",
           font=f_small, fill=INK)

    # MISSING, tracked one glyph at a time.
    word = "MISSING"
    f_word, _ = fit_missing(word, MEASURE)
    x = float(M)
    for ch in word:
        d.text((x, 74), ch, font=f_word, fill=INK)
        x += f_word.getlength(ch) + 10
    word_bottom = 74 + f_word.getbbox(word)[3]

    y = word_bottom + 14
    d.rectangle((M, y, right, y + 5), fill=INK)
    y += 11
    d.rectangle((M, y, right, y + 1), fill=INK)
    frame_top = y + 2 + 26
    frame_bottom = frame_top + 404

    # Frame.
    d.rectangle((M, frame_top, right, frame_bottom), fill=FRAME_FILL)
    d.rectangle((M, frame_top, right, frame_bottom), outline=INK, width=5)

    # Spotlight cone.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.polygon([(512, frame_top + 8), (300, frame_bottom - 8), (724, frame_bottom - 8)],
               fill=(255, 255, 255, 52))
    gd.polygon([(512, frame_top + 8), (362, frame_bottom - 8), (662, frame_bottom - 8)],
               fill=(255, 255, 255, 120))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    # Empty lectern.
    top = frame_bottom - 132
    d.rectangle((400, frame_bottom - 16, 624, frame_bottom - 7), fill=INK)
    d.rectangle((504, frame_bottom - 46, 520, frame_bottom - 12), fill=INK)
    d.polygon([(430, top), (594, top), (669, frame_bottom - 40), (357, frame_bottom - 40)],
              fill=INK)
    d.polygon([(430, top + 2), (594, top + 2), (664, frame_bottom - 43), (362, frame_bottom - 43)],
              fill="#2b2521")

    # Dead microphone lying on the lectern top.
    d.rectangle((455, top + 5, 536, top + 12), fill=INK)
    d.ellipse((536, top, 556, top + 20), fill=INK)
    d.ellipse((541, top + 5, 548, top + 12), fill="#6d6356")

    # Caption.
    f_caption = font(BOLD, 20)
    d.text((512, frame_bottom + 16), "One (1) climate deal, cover decision, unsigned",
           font=f_caption, fill=INK, anchor="ma")

    # Detail columns.
    col_w = 430
    rows_top = frame_bottom + 56
    f_label = font(BOLD, 15)
    f_value = font(REG, 19)
    for ci, rows in enumerate((LEFT, RIGHT)):
        x0 = M + ci * (col_w + 52)
        for ri, (label, value) in enumerate(rows):
            ry = rows_top + ri * 44
            d.text((x0, ry), label, font=f_label, fill=RED)
            d.text((x0, ry + 18), value, font=f_value, fill=INK)

    # Return line.
    y = rows_top + 3 * 44 + 18
    d.rectangle((M, y, right, y + 3), fill=INK)
    f_return = font(BOLD, 26)
    d.text((M, y + 18), "IF FOUND, RETURN TO: THE PACIFIC", font=f_return, fill=INK)
    f_quiet = font(BOLD, 17)
    d.text((right - f_quiet.getlength("NO QUESTIONS ASKED"), y + 52),
           "NO QUESTIONS ASKED", font=f_quiet, fill=INK)

    # Rubber stamp, rotated, pasted semi-transparent.
    f_stamp = font(NARROW, 88)
    text = "NO DEAL"
    tb = f_stamp.getbbox(text)
    pad = 30
    sw, sh = tb[2] - tb[0] + 2 * pad, tb[3] - tb[1] + 2 * pad
    stamp = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle((0, 0, sw - 1, sh - 1), outline=RED, width=8)
    sd.rectangle((20, 20, sw - 21, sh - 21), outline=RED, width=8)
    sd.text((sw / 2 - (tb[0] + tb[2]) / 2, sh / 2 - (tb[1] + tb[3]) / 2), text,
            font=f_stamp, fill=RED, anchor="mm")
    stamp = stamp.rotate(9, resample=Image.BICUBIC, expand=True)
    stamp.putalpha(stamp.getchannel("A").point(lambda v: v * 85 // 100))
    img.paste(stamp, (596, 236), stamp)
    d = ImageDraw.Draw(img)
    d.rectangle((M, frame_top, right, frame_bottom), outline=INK, width=5)

    # Grain.
    random.seed(7)
    px = img.load()
    for _ in range(26_000):
        gx, gy = random.randrange(W), random.randrange(H)
        r, g, b = px[gx, gy]
        px[gx, gy] = (
            max(0, min(255, r + random.randint(-7, 5))),
            max(0, min(255, g + random.randint(-7, 5))),
            max(0, min(255, b + random.randint(-7, 5))),
        )

    img = img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.NONE)
    img.save(OUT, "PNG", optimize=True)


if __name__ == "__main__":
    main()
