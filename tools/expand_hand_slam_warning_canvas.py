import os
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.entities.boss import PaleCoreBoss


SOURCE_PATH = PROJECT_ROOT / "assets" / "boss" / "hand_slam_warning.png"
BACKUP_PATH = PROJECT_ROOT / "assets" / "boss" / "hand_slam_warning_original.png"
UNCUT_SOURCE_PATH = (
    PROJECT_ROOT
    / "assets"
    / "boss"
    / "hand_slam_warning_original_6frames.png"
)
DEBUG_PATH = (
    PROJECT_ROOT
    / "assets"
    / "processed"
    / "debug"
    / "hand_slam_warning_expanded_source_rects.png"
)

FRAME_COUNT = 4
OUTPUT_FRAME_WIDTH = 700
OUTPUT_WIDTH = OUTPUT_FRAME_WIDTH * FRAME_COUNT
OUTPUT_RECTS = [
    (0, 120, 700, 360),
    (700, 120, 700, 360),
    (1400, 120, 700, 360),
    (2100, 120, 700, 360),
]


def draw_debug_preview(sheet):
    debug_surface = sheet.copy()
    font = pygame.font.Font(None, 42)
    colors = [
        (255, 80, 80),
        (80, 255, 120),
        (80, 180, 255),
        (255, 230, 80),
    ]

    for index, rect_values in enumerate(OUTPUT_RECTS):
        rect = pygame.Rect(*rect_values)
        color = colors[index]
        pygame.draw.rect(debug_surface, color, rect, 4)
        label = font.render(str(index + 1), True, (0, 0, 0))
        label_background = label.get_rect(topleft=(rect.x + 10, rect.y + 10)).inflate(14, 10)
        pygame.draw.rect(debug_surface, color, label_background)
        debug_surface.blit(label, label.get_rect(center=label_background.center))

    DEBUG_PATH.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(debug_surface, str(DEBUG_PATH))


def expand_sheet():
    if not BACKUP_PATH.exists():
        shutil.copy2(SOURCE_PATH, BACKUP_PATH)
        print("Saved hand slam warning backup:", BACKUP_PATH)
    else:
        print("Using existing hand slam warning backup:", BACKUP_PATH)

    extraction_path = UNCUT_SOURCE_PATH if UNCUT_SOURCE_PATH.exists() else BACKUP_PATH
    source = pygame.image.load(str(extraction_path)).convert_alpha()
    source_width, source_height = source.get_size()
    source_frame_width = source_width // FRAME_COUNT
    if source_frame_width <= 0:
        raise ValueError(f"Invalid hand slam warning source size: {source.get_size()}")

    loader = PaleCoreBoss.__new__(PaleCoreBoss)
    output = pygame.Surface((OUTPUT_WIDTH, source_height), pygame.SRCALPHA)

    for index in range(FRAME_COUNT):
        source_x = index * source_frame_width
        source_width_for_frame = (
            source_width - source_x
            if index == FRAME_COUNT - 1
            else source_frame_width
        )
        source_rect = pygame.Rect(
            source_x,
            0,
            source_width_for_frame,
            source_height,
        )
        frame = pygame.Surface(source_rect.size, pygame.SRCALPHA)
        frame.blit(source, (0, 0), source_rect)
        frame = loader.force_boss_transparency(frame, f"hand_slam_warning_expand_{index}")

        visible_bounds = frame.get_bounding_rect(min_alpha=1)
        destination_x = (
            index * OUTPUT_FRAME_WIDTH
            + OUTPUT_FRAME_WIDTH // 2
            - visible_bounds.centerx
        )
        output.blit(frame, (destination_x, 0))

    pygame.image.save(output, str(SOURCE_PATH))
    draw_debug_preview(output)

    print("Hand slam warning extraction source:", extraction_path)
    print("Expanded hand slam warning sheet:", SOURCE_PATH)
    print("Original size:", source.get_size())
    print("Expanded size:", output.get_size())
    print("Frame slots:", FRAME_COUNT, "x", (OUTPUT_FRAME_WIDTH, source_height))
    print("Exported expanded source rect preview:", DEBUG_PATH)


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    expand_sheet()


if __name__ == "__main__":
    main()
