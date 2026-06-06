import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from settings import HAND_SLAM_WARNING_SCALE
from src.entities.boss import BOSS_ASSETS, HAND_SLAM_WARNING_RECTS, PaleCoreBoss


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    loader = PaleCoreBoss.__new__(PaleCoreBoss)
    frames = loader.load_manual_rect_sheet(
        BOSS_ASSETS["hand_slam_warning"],
        HAND_SLAM_WARNING_RECTS,
        scale=HAND_SLAM_WARNING_SCALE,
        debug_name="hand_slam_warning",
        write_debug=True,
    )
    print("Exported hand slam warning debug previews for", len(frames), "frames.")


if __name__ == "__main__":
    main()
