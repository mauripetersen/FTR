import sys
import os

__all__ = ["base_dir", "assets_dir", "configs_dir", "themes_dir", "projects_dir", "system_dir",
           "FTR_NAME", "FTR_MODULO_ELASTICIDADE"]

# Ensures base_dir for both cases (base_dir = "c:\FTR"):
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Folders:
assets_dir = os.path.join(base_dir, "assets")
configs_dir = os.path.join(base_dir, "configs")
themes_dir = os.path.join(configs_dir, "themes")
projects_dir = os.path.join(base_dir, "projects")
system_dir = os.path.join(base_dir, "system")

FTR_NAME = "FTR - Ferri Tractus Ratio"
FTR_MODULO_ELASTICIDADE = 210000  # MPa
