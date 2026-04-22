"""NASA Astronomy Picture of the Day → e-ink renderer.

Uses the public APOD API (https://api.nasa.gov/). DEMO_KEY works for low volume;
set $NASA_API_KEY for a generous personal quota (free at api.nasa.gov).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from io import BytesIO
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .display import Display


APOD_URL = "https://api.nasa.gov/planetary/apod"
USER_AGENT = "einkd/0.1 (+https://github.com/Lucas8448/e-ink)"


@dataclass(frozen=True)
class Apod:
    title: str
    date: str
    explanation: str
    image_url: str
    copyright: Optional[str]
    media_type: str  # "image" or "video"


def _http_get(url: str, *, timeout: int = 30, retries: int = 4) -> bytes:
    """GET with exponential backoff for transient 5xx / network errors."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code < 500 or attempt == retries - 1:
                raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            if attempt == retries - 1:
                raise
        time.sleep(2 ** attempt)
    assert last is not None
    raise last


def fetch_apod(*, api_key: Optional[str] = None, on_date: Optional[date] = None) -> Apod:
    key = api_key or os.environ.get("NASA_API_KEY") or "DEMO_KEY"
    params = [f"api_key={key}", "thumbs=true"]
    if on_date is not None:
        params.append(f"date={on_date.isoformat()}")
    url = f"{APOD_URL}?{'&'.join(params)}"
    data = json.loads(_http_get(url))

    media_type = data.get("media_type", "image")
    # For videos APOD returns a still in `thumbnail_url` when thumbs=true.
    if media_type == "image":
        image_url = data.get("hdurl") or data["url"]
    else:
        image_url = data.get("thumbnail_url") or data.get("url", "")

    return Apod(
        title=data.get("title", "(untitled)"),
        date=data.get("date", ""),
        explanation=data.get("explanation", ""),
        image_url=image_url,
        copyright=data.get("copyright"),
        media_type=media_type,
    )


def fetch_image(url: str) -> Image.Image:
    return Image.open(BytesIO(_http_get(url, timeout=60))).convert("RGB")


def compose(apod: Apod, image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Letterbox the APOD image and overlay a translucent caption strip."""
    w, h = size
    canvas = Image.new("RGB", (w, h), "black")

    # Reserve a caption strip at the bottom (~14% of height).
    caption_h = max(60, int(h * 0.14))
    img_area_h = h - caption_h

    # Fit the picture into the upper area, preserving aspect.
    src = image
    sw, sh = src.size
    scale = min(w / sw, img_area_h / sh)
    new_size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
    resized = src.resize(new_size, Image.LANCZOS)
    canvas.paste(resized, ((w - new_size[0]) // 2, (img_area_h - new_size[1]) // 2))

    # Caption strip
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, h - caption_h, w, h], fill="white")
    title_font = _font(int(caption_h * 0.42), bold=True)
    meta_font = _font(int(caption_h * 0.26))

    pad = 14
    title = _truncate(apod.title, title_font, draw, w - 2 * pad)
    draw.text((pad, h - caption_h + pad - 4), title, fill="black", font=title_font)

    meta_bits = [apod.date]
    if apod.copyright:
        meta_bits.append(f"© {apod.copyright.strip()}")
    meta_bits.append("NASA APOD")
    meta = "  •  ".join(meta_bits)
    meta = _truncate(meta, meta_font, draw, w - 2 * pad)
    draw.text(
        (pad, h - int(caption_h * 0.40)),
        meta,
        fill=(60, 60, 60),
        font=meta_font,
    )

    return canvas


def render_today(*, api_key: Optional[str] = None, saturation: float = 0.7) -> Apod:
    apod = fetch_apod(api_key=api_key)
    if not apod.image_url:
        raise RuntimeError(f"APOD {apod.date} has no usable image (media_type={apod.media_type}).")
    img = fetch_image(apod.image_url)
    display = Display(saturation=saturation)
    composed = compose(apod, img, display.size)
    display.show_image(composed, fit=False)
    return apod


# ---------- helpers ---------------------------------------------------------

def _font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size=size)
    return ImageFont.load_default()


def _truncate(text: str, font, draw, max_width: int) -> str:
    if draw.textlength(text, font=font) <= max_width:
        return text
    ellipsis = "…"
    while text and draw.textlength(text + ellipsis, font=font) > max_width:
        text = text[:-1]
    return text + ellipsis
