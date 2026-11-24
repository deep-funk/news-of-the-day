#!/usr/bin/env python3
"""Publish entry.png to MAKEFUN_OUTPUT_DIR (default /output)."""

import os
import shutil
import sys
from pathlib import Path

src = Path(__file__).resolve().parent / "entry.png"
if not src.is_file():
    sys.exit(f"missing {src}; run python3 make_image.py first")

dest = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"
dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(src, dest)
os.chmod(dest, 0o644)
print(dest)
print(dest.stat().st_size)
