import sys

sys.path.append("..\..\.venv\Lib\site-packages")

from PIL import Image, ImageDraw, ImageFont
import json


def main() -> None:
    theme_path = "../../configs/themes/dark.json"

    with open(theme_path, "r") as f:
        data = json.load(f)

    result = extract_key_values(data)

    n = len(result)
    dx = 800
    dy = 100

    wi = 2 * dx
    he = dy * n

    img = Image.new("RGB", (wi, he), color="#ffffff")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("cambria", 32)

    for i, (k, v) in enumerate(result):
        if type(v) is list:
            cont = len(v)
            for ix, item in enumerate(v):
                clr = f"#{item[1:7]}"
                draw.rectangle([dx * (1 + ix / cont), dy * i, dx * (1 + (ix + 1) / cont), dy * (i + 1)],
                               fill=clr, outline="#000000")
        else:
            clr = f"#{v[1:7]}"
            draw.rectangle([wi / 2, dy * i, wi, dy * (i + 1)], fill=clr, outline="#000000")

        text = k

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        rect = (0, dy * i, dx, dy * (i + 1))
        rect_x0, rect_y0, rect_x1, rect_y1 = rect
        rect_width = rect_x1 - rect_x0
        rect_height = rect_y1 - rect_y0

        text_pos = (rect_x0 + (rect_width - text_width) / 2, rect_y0 + (rect_height - text_height) / 2)

        draw.text(text_pos, text, fill="black", font=font)

    img.show()
    img.save("DarkMode.png")


def extract_key_values(d, parent_key='', result=None):
    if result is None:
        result = []

    for key, value in d.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            extract_key_values(value, full_key, result)
        else:
            result.append((full_key, value))

    return result


if __name__ == "__main__":
    main()
