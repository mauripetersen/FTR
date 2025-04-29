from enum import StrEnum
import sys
import os

__version__ = "1.0.0"

__all__ = ["SectionType", "SupportType", "LoadType",
           "base_dir",
           "assets_dir", "fonts_dir", "icon_dir", "images_dir",
           "configs_dir", "languages_dir", "themes_dir",
           "projects_dir", "system_dir",
           "FTR_NAME_0", "FTR_NAME_1", "FTR_NAME_2", "__version__"]


class SectionType(StrEnum):
    """
    "R" = Rectangle

    "I" = I-shape

    "T" = T-shape
    """
    R = "R"
    I = "I"
    T = "T"


class SupportType(StrEnum):
    """
    "roller" = 2 degrees of freedom

    "pinned" = 1 degree of freedom

    "fixed" = 0 degrees of freedom
    """
    Roller = "roller"
    Pinned = "pinned"
    Fixed = "fixed"


class LoadType(StrEnum):
    """
    "PL" = Point Load

    "DL" = Distributed Load
    """
    PL = "PL"
    DL = "DL"


# Ensures base_dir for both cases (base_dir = "c:\FTR"):
if getattr(sys, 'frozen', False):
    base_dir: str = os.path.dirname(sys.executable)
else:
    base_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Folders:
assets_dir: str = os.path.join(base_dir, "assets")
fonts_dir: str = os.path.join(assets_dir, "fonts")
icon_dir: str = os.path.join(assets_dir, "icon")
images_dir: str = os.path.join(assets_dir, "images")

configs_dir: str = os.path.join(base_dir, "configs")
languages_dir: str = os.path.join(configs_dir, "languages")
themes_dir: str = os.path.join(configs_dir, "themes")

projects_dir: str = os.path.join(base_dir, "projects")
system_dir: str = os.path.join(base_dir, "system")

FTR_NAME_0: str = "FTR - Ferri Tractus Ratio"
FTR_NAME_1: str = "FTR"
FTR_NAME_2: str = "Ferri Tractus Ratio"
