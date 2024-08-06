from PIL import Image, ImageDraw

FILL = "#fff"
STROKE = "#000"


def center(draw: ImageDraw, text: str, top: int, width: int, **kwargs):
    _, _, w, _ = draw.textbbox((0, 0), text, **kwargs)
    draw.text(((width - w) / 2, top), text, FILL, stroke_fill=STROKE, **kwargs)


def render(width: int, height: int, text: str, font) -> Image.Image:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, "#fff", font=font)
    return img
