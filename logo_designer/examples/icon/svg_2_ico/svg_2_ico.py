import sys
import os

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "Lib")))

import cairosvg
from PIL import Image

cairosvg.svg2png(url="icon.svg", write_to="icon.png", output_width=1024, output_height=1024)

img = Image.open("icon.png")

for k in range(4, 9):
    dim = 2 ** k
    img.save(f"output/icon_x{dim}.ico", format="ICO", sizes=[(dim, dim)])
