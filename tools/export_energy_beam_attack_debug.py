import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.systems.skills import export_energy_beam_attack_debug_previews


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    frames = export_energy_beam_attack_debug_previews()
    print(f"Exported Energy Beam attack debug previews for {len(frames)} frames.")


if __name__ == "__main__":
    main()
