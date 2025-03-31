from PIL import Image, ImageDraw, ImageFont
import json


def main() -> None:
    palette_path = "../../configs/themes/palettes.json"

    with open(palette_path, "r") as f:
        data = json.load(f)

    result = extract_key_values(data)

    wi = 800
    he = 2000
    n = len(result)
    dx = wi / 2
    dy = he / n

    img = Image.new("RGB", (wi, he), color="#ffffff")
    draw = ImageDraw.Draw(img)
    # font = ImageFont.load_default()
    font = ImageFont.truetype("cambria", 24)

    for i, (k, v) in enumerate(result):
        draw.rectangle([wi / 2, dy * i, wi, dy * (i + 1)], fill=f"#{v[1:7]}", outline="#000000")
        draw.text((30, dy * (i + .45)), k, fill="#000000", font=font)

    img.show()
    img.save("palettes.png")


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
