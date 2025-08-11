# TFG

'''
contains global constants or settings (text needs work)
'''

from pathlib import Path
from datetime import datetime

# Physical constants:
P_ATM = 101325      # Pa

# Directories:
PROJECT_ROOT =Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"
EXPORT_FOLDER = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
EXPORT_DIR = ASSETS_DIR / EXPORT_FOLDER
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
