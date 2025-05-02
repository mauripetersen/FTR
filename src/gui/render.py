from PIL import Image, ImageDraw, ImageTk
import math

from config import Theme, SupportType
from project import Node, Support, Load, PLLoad, DLLoad
from manager import FontManager

__all__ = ["update_image"]


def generate_image(element: Node | Support | Load, clr: str) -> Image:
    if isinstance(element, Node):
        r, b = element.imgDims.values()

        img = Image.new("RGBA", (2 * (r + b), 2 * (r + b)))
        dwg = ImageDraw.Draw(img)

        pc = (r + b, r + b)
        dwg.circle(pc, radius=r, fill=clr, width=0)

        return img
    elif isinstance(element, Support):
        side, dy = element.imgDims.values()

        dx = side / 3
        wi = 5 * dx
        height = side * math.sqrt(3) / 2
        width = 1

        img = Image.new("RGBA", (int(wi), int(wi)))
        dwg = ImageDraw.Draw(img)

        match element.type:
            case SupportType.Roller:
                dwg.line((wi / 2, 0, 4 * dx, height), fill=clr, width=width)
                dwg.line((wi / 2, 0, dx, height), fill=clr, width=width)
                dwg.line((dx, height, 4 * dx, height), fill=clr, width=width)

                dwg.line((0, height, wi, height), fill=clr, width=width)
                dwg.line((0, height + dy, wi, height + dy), fill=clr, width=width)
            case SupportType.Pinned:
                dwg.line((wi / 2, 0, 4 * dx, height), fill=clr, width=width)
                dwg.line((wi / 2, 0, dx, height), fill=clr, width=width)
                dwg.line((dx, height, 4 * dx, height), fill=clr, width=width)

                dwg.line((0, height, wi, height), fill=clr, width=width)
                for k in range(5):
                    dwg.line((k * dx, height + dy, (k + 1) * dx, height), fill=clr, width=width)
            case SupportType.Fixed:
                dwg.line((0, 0, wi, 0), fill=clr, width=width)
                for k in range(5):
                    dwg.line((k * dx, dy, (k + 1) * dx, 0), fill=clr, width=width)
        return img
    elif isinstance(element, PLLoad):
        ImageDraw.ImageDraw.font = FontManager.get_pillow_font("Segoe UI Semibold", 20)
        width = 2

        Fx_len, Fx_ax, Fx_ay = element.imgDims["Fx"].values()
        Fy_len, Fy_ax, Fy_ay = element.imgDims["Fy"].values()
        Mz_rPt, Mz_r, Mz_ax, Mz_ay = element.imgDims["Mz"].values()
        border = element.imgDims["border"]

        side = int(2 * (max(Fx_len, Fy_len, Mz_r) + border))
        pc = (side / 2, side / 2)

        img = Image.new("RGBA", (side, side))
        dwg = ImageDraw.Draw(img)

        if element.Fx != 0:
            if element.Fx > 0:
                p1 = (pc[0] - Fx_len, pc[1])
                p2 = (pc[0] - Fx_ax, pc[1] - Fx_ay)
                p3 = (pc[0] - Fx_ax, pc[1] + Fx_ay)
                dwg.text((pc[0] - Fx_len / 2, pc[1] - 15), text=f"{element.Fx} kN", fill=clr, anchor="ms")
            else:
                p1 = (pc[0] + Fx_len, pc[1])
                p2 = (pc[0] + Fx_ax, pc[1] - Fx_ay)
                p3 = (pc[0] + Fx_ax, pc[1] + Fx_ay)
                dwg.text((pc[0] + Fx_len / 2, pc[1] - 15), text=f"{element.Fx} kN", fill=clr, anchor="ms")

            dwg.line((*pc, *p1), fill=clr, width=width)
            dwg.line((*pc, *p2), fill=clr, width=width)
            dwg.line((*pc, *p3), fill=clr, width=width)
        if element.Fy != 0:
            if element.Fy > 0:
                p1 = (pc[0], pc[1] + Fy_len)
                p2 = (pc[0] - Fy_ax, pc[1] + Fy_ay)
                p3 = (pc[0] + Fy_ax, pc[1] + Fy_ay)
                dwg.text((pc[0], pc[1] + Fy_len + 10), text=f"{element.Fy} kN", fill=clr, anchor="mt")
            else:
                p1 = (pc[0], pc[1] - Fy_len)
                p2 = (pc[0] - Fy_ax, pc[1] - Fy_ay)
                p3 = (pc[0] + Fy_ax, pc[1] - Fy_ay)
                dwg.text((pc[0], pc[1] - Fy_len - 10), text=f"{element.Fy} kN", fill=clr, anchor="ms")

            dwg.line((*pc, *p1), fill=clr, width=width)
            dwg.line((*pc, *p2), fill=clr, width=width)
            dwg.line((*pc, *p3), fill=clr, width=width)
        if element.Mz != 0:
            img_Mz = Image.new("RGBA", (2 * (Mz_r + border), 2 * (Mz_r + border)))
            dwg_Mz = ImageDraw.Draw(img_Mz)

            p0 = (border + Mz_r, border + Mz_r)
            p1 = (border, border)
            p2 = (2 * Mz_r + border, 2 * Mz_r + border)
            pa1 = (2 * Mz_r + border, Mz_r + border)
            if element.Mz > 0:
                pa2 = (2 * Mz_r + border - Mz_ax, Mz_r + border + Mz_ay)
                pa3 = (2 * Mz_r + border + Mz_ax, Mz_r + border + Mz_ay)
                start = 0
                end = 270
                angle = -45
            else:
                pa2 = (2 * Mz_r + border - Mz_ax, Mz_r + border - Mz_ay)
                pa3 = (2 * Mz_r + border + Mz_ax, Mz_r + border - Mz_ay)
                start = 90
                end = 360
                angle = 45

            dwg_Mz.circle(p0, radius=Mz_rPt, fill=clr, width=0)
            dwg_Mz.arc((*p1, *p2), start=start, end=end, fill=clr, width=width)
            dwg_Mz.line((*pa1, *pa2), fill=clr, width=width)
            dwg_Mz.line((*pa1, *pa3), fill=clr, width=width)
            img_Mz = img_Mz.rotate(angle=angle, resample=Image.Resampling.BICUBIC)

            dwg_Mz = ImageDraw.Draw(img_Mz)
            dwg_Mz.text((Mz_r + border, 0), text=f"{element.Mz} kN.m", fill=clr, anchor="mt")

            pt_ins = int(pc[0] - img_Mz.width / 2), int(pc[1] - img_Mz.height / 2)
            img.paste(img_Mz, pt_ins, mask=img_Mz)
        return img
    elif isinstance(element, DLLoad):
        return None
    return None


def update_image(element: Node | Support | Load) -> list[ImageTk.PhotoImage] | None:
    if isinstance(element, Node):
        img0 = generate_image(element, Theme.CAD.nodes[0])
        img1 = generate_image(element, Theme.CAD.nodes[1])
        return [ImageTk.PhotoImage(img0), ImageTk.PhotoImage(img1)]
    elif isinstance(element, Support):
        img = generate_image(element, Theme.CAD.supports)
        return [ImageTk.PhotoImage(img)]
    elif isinstance(element, PLLoad):
        img0 = generate_image(element, Theme.CAD.loads[0])
        img1 = generate_image(element, Theme.CAD.loads[1])
        return [ImageTk.PhotoImage(img0), ImageTk.PhotoImage(img1)]
    elif isinstance(element, DLLoad):
        return None
    return None
