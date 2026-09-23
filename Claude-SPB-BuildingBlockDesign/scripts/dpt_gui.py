"""Launches the interactive double-pulse test GUI.

    python scripts/dpt_gui.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spb_bb.gui import main

if __name__ == "__main__":
    main()
