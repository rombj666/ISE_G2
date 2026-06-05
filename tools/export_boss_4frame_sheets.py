from pathlib import Path
import shutil

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SELECTED_FRAME_INDICES = (0, 1, 3, 5)
SOURCE_FRAME_COUNT = 6

SHEETS = (
    (
        PROJECT_ROOT / "assets" / "boss" / "hand_slam_warning.png",
        PROJECT_ROOT / "assets" / "boss" / "hand_slam_warning_original_6frames.png",
    ),
    (
        PROJECT_ROOT / "assets" / "boss" / "boss_hit_effect.png",
        PROJECT_ROOT / "assets" / "boss" / "boss_hit_effect_original_6frames.png",
    ),
)


def export_four_frame_sheet(path, backup_path):
    sheet = pygame.image.load(str(path)).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // SOURCE_FRAME_COUNT
    frame_height = sheet_height

    if sheet_width % SOURCE_FRAME_COUNT != 0:
        raise ValueError(f"{path} width {sheet_width} is not divisible by {SOURCE_FRAME_COUNT}")

    if not backup_path.exists():
        shutil.copy2(path, backup_path)
    else:
        print("[BACKUP EXISTS]", backup_path)

    frames = []
    for frame_index in SELECTED_FRAME_INDICES:
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        source_rect = pygame.Rect(frame_index * frame_width, 0, frame_width, frame_height)
        frame.blit(sheet, (0, 0), source_rect)
        frames.append(frame)

    new_sheet = pygame.Surface((frame_width * len(frames), frame_height), pygame.SRCALPHA)
    for output_index, frame in enumerate(frames):
        new_sheet.blit(frame, (output_index * frame_width, 0))

    pygame.image.save(new_sheet, str(path))

    print("[EXPORT 4-FRAME SHEET]", path)
    print("original size:", (sheet_width, sheet_height))
    print("original frame size:", (frame_width, frame_height))
    print("selected frames:", tuple(index + 1 for index in SELECTED_FRAME_INDICES))
    print("new sheet size:", new_sheet.get_size())
    print("new frame count:", len(frames))
    print("backup:", backup_path)


def main():
    pygame.init()
    try:
        pygame.display.init()
        pygame.display.set_mode((1, 1), flags=pygame.HIDDEN)
        for path, backup_path in SHEETS:
            export_four_frame_sheet(path, backup_path)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
