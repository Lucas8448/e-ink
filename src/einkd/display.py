"""Thin wrapper around the Pimoroni `inky` library.

Auto-detects the Inky Impression via the HAT EEPROM and exposes a tiny API:

    d = Display()
    d.show_image(pil_image)
    d.show_text("Hello")
    d.clear()
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class DisplayInfo:
    name: str
    width: int
    height: int
    colour: str


class Display:
    def __init__(self, *, saturation: float = 0.6) -> None:
        from inky.auto import auto  # imported lazily so non-Pi machines can still import

        self._inky = auto(ask_user=False, verbose=False)
        self._saturation = saturation

    @property
    def info(self) -> DisplayInfo:
        i = self._inky
        return DisplayInfo(
            name=type(i).__name__,
            width=i.width,
            height=i.height,
            colour=getattr(i, "colour", "unknown"),
        )

    @property
    def size(self) -> tuple[int, int]:
        return self._inky.width, self._inky.height

    def show_image(self, image: Image.Image, *, fit: bool = True) -> None:
        """Push a PIL image to the panel. With ``fit=True`` the image is
        letterboxed to fill the panel preserving aspect ratio."""
        target = self._fit(image) if fit else image.convert("RGB")
        self._inky.set_image(target, saturation=self._saturation)
        self._inky.show()

    def show_text(
        self,
        text: str,
        *,
        font_path: Optional[Path] = None,
        size: int = 64,
        bg: str = "white",
        fg: str = "black",
    ) -> None:
        w, h = self.size
        canvas = Image.new("RGB", (w, h), bg)
        font = self._load_font(font_path, size)
        draw = ImageDraw.Draw(canvas)
        wrapped = self._wrap(text, font, draw, w - 40)
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, align="center", spacing=8)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.multiline_text(
            ((w - tw) / 2 - bbox[0], (h - th) / 2 - bbox[1]),
            wrapped,
            font=font,
            fill=fg,
            align="center",
            spacing=8,
        )
        self.show_image(canvas, fit=False)

    def clear(self, colour: str = "white") -> None:
        w, h = self.size
        self.show_image(Image.new("RGB", (w, h), colour), fit=False)

    def _fit(self, image: Image.Image) -> Image.Image:
        w, h = self.size
        src = image.convert("RGB")
        sw, sh = src.size
        scale = min(w / sw, h / sh)
        new_size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
        resized = src.resize(new_size, Image.LANCZOS)
        canvas = Image.new("RGB", (w, h), "white")
        canvas.paste(resized, ((w - new_size[0]) // 2, (h - new_size[1]) // 2))
        return canvas

    @staticmethod
    def _load_font(font_path: Optional[Path], size: int) -> ImageFont.ImageFont:
        candidates: list[Path] = []
        if font_path is not None:
            candidates.append(Path(font_path))
        candidates += [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        for c in candidates:
            if c.exists():
                return ImageFont.truetype(str(c), size=size)
        return ImageFont.load_default()

    @staticmethod
    def _wrap(text: str, font, draw, max_width: int) -> str:
        out_lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                out_lines.append("")
                continue
            line = words[0]
            for word in words[1:]:
                trial = f"{line} {word}"
                if draw.textlength(trial, font=font) <= max_width:
                    line = trial
                else:
                    out_lines.append(line)
                    line = word
            out_lines.append(line)
        return "\n".join(out_lines)
