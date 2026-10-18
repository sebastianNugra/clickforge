"""Genera assets/icon.ico: un rayo naranja sobre fondo oscuro estilo ClickForge."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
SIZES = [16, 24, 32, 48, 64, 128, 256]


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (23, 24, 31, 255))
    d = ImageDraw.Draw(img)
    m = max(2, size // 8)  # margen

    # botón/vidrio redondeado
    d.rounded_rectangle([m // 2, m // 2, size - m // 2, size - m // 2],
                        radius=size // 5, fill=(58, 61, 74, 255),
                        outline=(154, 160, 180, 255), width=max(1, size // 32))

    # rayo (símbolo de "click rápido")
    w = size - 2 * m
    bolt = [
        (m + w * 0.55, m + w * 0.05),
        (m + w * 0.20, m + w * 0.55),
        (m + w * 0.45, m + w * 0.55),
        (m + w * 0.35, m + w * 0.95),
        (m + w * 0.80, m + w * 0.40),
        (m + w * 0.52, m + w * 0.40),
    ]
    d.polygon(bolt, fill=(74, 222, 128, 255))
    return img


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    images = [draw_icon(s) for s in SIZES]
    images[-1].save(OUT, format="ICO", sizes=[(s, s) for s in SIZES],
                    append_images=images[:-1])
    print(f"Icono generado en {OUT}")


if __name__ == "__main__":
    main()
