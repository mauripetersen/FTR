import sys
import os

__all__ = ["base_dir", "assets_dir", "configs_dir", "themes_dir", "projects_dir", "system_dir",
           "FTR_NAME_0", "FTR_NAME_1", "FTR_NAME_2", "FTR_MODULO_ELASTICIDADE"]

# Ensures base_dir for both cases (base_dir = "c:\FTR"):
if getattr(sys, 'frozen', False):
    base_dir: str = os.path.dirname(sys.executable)
else:
    base_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Folders:
assets_dir: str = os.path.join(base_dir, "assets")
configs_dir: str = os.path.join(base_dir, "configs")
themes_dir: str = os.path.join(configs_dir, "themes")
projects_dir: str = os.path.join(base_dir, "projects")
system_dir: str = os.path.join(base_dir, "system")

FTR_NAME_0: str = "FTR - Ferri Tractus Ratio"
FTR_NAME_1: str = "FTR"
FTR_NAME_2: str = "Ferri Tractus Ratio"
FTR_MODULO_ELASTICIDADE = 210000  # MPa
