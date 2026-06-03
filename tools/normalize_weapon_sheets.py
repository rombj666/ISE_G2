from pathlib import Path
import statistics
import sys

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from settings import (  # noqa: E402
    GRAPPLE_ATTACK_CHARACTER_HEIGHT,
    GRAPPLE_ATTACK_FRAME_COUNT,
    GRAPPLE_DASH_FRAME_COUNT,
    GRAPPLE_IDLE_FRAME_COUNT,
    GRAPPLE_JUMP_FRAME_COUNT,
    GRAPPLE_WALK_FRAME_COUNT,
    HEAVY_ATTACK_CHARACTER_HEIGHT,
    HEAVY_ATTACK_FRAME_COUNT,
    HEAVY_DASH_FRAME_COUNT,
    HEAVY_IDLE_FRAME_COUNT,
    HEAVY_JUMP_FRAME_COUNT,
    HEAVY_WALK_FRAME_COUNT,
    LIGHT_ATTACK_CHARACTER_HEIGHT,
    LIGHT_ATTACK_FRAME_COUNT,
    LIGHT_DASH_FRAME_COUNT,
    LIGHT_IDLE_FRAME_COUNT,
    LIGHT_JUMP_FRAME_COUNT,
    LIGHT_WALK_FRAME_COUNT,
    SHIELD_ATTACK_CHARACTER_HEIGHT,
    SHIELD_ATTACK_FRAME_COUNT,
    SHIELD_DASH_FRAME_COUNT,
    SHIELD_IDLE_FRAME_COUNT,
    SHIELD_JUMP_FRAME_COUNT,
    SHIELD_WALK_FRAME_COUNT,
    SHOOTER_ATTACK_CHARACTER_HEIGHT,
    SHOOTER_ATTACK_FRAME_COUNT,
    SHOOTER_DASH_FRAME_COUNT,
    SHOOTER_IDLE_FRAME_COUNT,
    SHOOTER_JUMP_FRAME_COUNT,
    SHOOTER_WALK_FRAME_COUNT,
)

SOURCE_ANIMATIONS = PROJECT_ROOT / "assets" / "animations"
SOURCE_WEAPONS = PROJECT_ROOT / "assets" / "weapons"
OUTPUT_ANIMATIONS = PROJECT_ROOT / "assets" / "processed" / "animations"
OUTPUT_WEAPONS = PROJECT_ROOT / "assets" / "processed" / "weapons"
OUTPUT_DEBUG = PROJECT_ROOT / "assets" / "processed" / "debug"
REFERENCE_WEAPON = "light"
REFERENCE_STATE = "idle"

MANUAL_ATTACK_RECTS = {
    "light": [
        (80, 0, 360, 425),       # frame 1 - ready
        (620, 0, 410, 425),      # frame 2 - pull back
        (1220, 0, 650, 425),     # frame 3 - slash start
        (1900, 0, 730, 425),     # frame 4 - big slash
        (2600, 0, 600, 425),     # frame 5 - follow-through
        (3250, 0, 420, 425),     # frame 6 - return
    ],

    "heavy": [
        (20, 0, 340, 724),       # frame 1 - ready
        (370, 0, 280, 724),      # frame 2 - lift / wind-up
        (660, 0, 255, 724),      # frame 3 - swing start
        (980, 0, 510, 724),     # frame 4 - big heavy slash
        (1540, 0, 330, 724),     # frame 5 - follow-through
        (1890, 0, 360, 724),     # frame 6 - return
    ],

    "grapple": [
        (25, 0, 290, 724),       # frame 1 - ready
        (330, 0, 290, 724),      # frame 2 - pull hook back
        (640, 0, 360, 724),      # frame 3 - launch
        (1000, 0, 540, 724),     # frame 4 - full chain extension
        (1600, 0, 300, 724),     # frame 5 - retract
        (1870, 0, 285, 724),     # frame 6 - return
    ],

    "shield": [
        (0, 0, 240, 537),        # frame 1 - ready
        (280, 0, 200, 537),      # frame 2 - pull shield back
        (540, 0, 230, 537),      # frame 3 - step forward
        (780, 0, 320, 537),      # frame 4 - shield impact burst
        (1090, 0, 275, 537),     # frame 5 - follow-through
        (1330, 0, 225, 537),     # frame 6 - return
    ],

    "shooter": [
        (0, 0, 320, 724),        # frame 1 - ready
        (370, 0, 320, 724),      # frame 2 - aim
        (730, 0, 310, 724),      # frame 3 - pre-fire
        (1050, 0, 395, 724),      # frame 4 - fire shot / muzzle flash
        (1450, 0, 390, 724),     # frame 5 - recoil
        (1840, 0, 600, 724),     # frame 6 - return
    ],
}

MANUAL_IDLE_RECTS = {
    "light": None,
    "heavy": None,
    "shooter": [
        (0, 0, 378, 724),
        (382, 0, 373, 724),
        (729, 0, 370, 724),
        (1086, 0, 342, 724),
        (1413, 0, 352, 724),
        (1780, 0, 362, 724),
    ],
    "shield": None,
    "grapple": None,
}

MANUAL_JUMP_RECTS = {
    "light": None,
    "heavy": None,

    "shooter": [
        (0, 0, 279, 941),
        (279, 0, 279, 941),
        (558, 0, 279, 941),
        (837, 0, 246, 941),
        (1068, 0, 269, 916),
        (1360, 0, 277, 941),
    ],

    "shield": [
        (0, 0, 279, 941),
        (279, 0, 279, 941),
        (558, 0, 269, 941),
        (827, 0, 234, 941),
        (1088, 0, 260, 941),
        (1370, 0, 277, 941),
    ],

    "grapple": None,
}

MOVEMENT_CANVAS_SIZES = {
    "light": (96, 96),
    "heavy": (104, 104),
    "shooter": (96, 96),
    "shield": (104, 104),
    "grapple": (104, 104),
}

STATE_CANVAS_SIZES = {
    ("shooter", "jump"): (300, 260),
    ("shield", "jump"): (300, 260),
}

MOVEMENT_CHARACTER_HEIGHTS = {
    "light": 82,
    "heavy": 82,
    "shooter": 82,
    "shield": 88,
    "grapple": 86,
}

ATTACK_CANVAS_SIZES = {
    "light": (320, 220),
    "heavy": (360, 240),
    "shooter": (300, 220),
    "shield": (320, 220),
    "grapple": (420, 240),
}

ATTACK_CHARACTER_HEIGHTS = {
    "light": LIGHT_ATTACK_CHARACTER_HEIGHT,
    "heavy": HEAVY_ATTACK_CHARACTER_HEIGHT,
    "shooter": SHOOTER_ATTACK_CHARACTER_HEIGHT,
    "shield": SHIELD_ATTACK_CHARACTER_HEIGHT,
    "grapple": GRAPPLE_ATTACK_CHARACTER_HEIGHT,
}

FRAME_COUNTS = {
    ("light", "idle"): LIGHT_IDLE_FRAME_COUNT,
    ("light", "walk"): LIGHT_WALK_FRAME_COUNT,
    ("light", "jump"): LIGHT_JUMP_FRAME_COUNT,
    ("light", "dash"): LIGHT_DASH_FRAME_COUNT,
    ("light", "attack"): LIGHT_ATTACK_FRAME_COUNT,
    ("heavy", "idle"): HEAVY_IDLE_FRAME_COUNT,
    ("heavy", "walk"): HEAVY_WALK_FRAME_COUNT,
    ("heavy", "jump"): HEAVY_JUMP_FRAME_COUNT,
    ("heavy", "dash"): HEAVY_DASH_FRAME_COUNT,
    ("heavy", "attack"): HEAVY_ATTACK_FRAME_COUNT,
    ("shooter", "idle"): SHOOTER_IDLE_FRAME_COUNT,
    ("shooter", "walk"): SHOOTER_WALK_FRAME_COUNT,
    ("shooter", "jump"): SHOOTER_JUMP_FRAME_COUNT,
    ("shooter", "dash"): SHOOTER_DASH_FRAME_COUNT,
    ("shooter", "attack"): SHOOTER_ATTACK_FRAME_COUNT,
    ("shield", "idle"): SHIELD_IDLE_FRAME_COUNT,
    ("shield", "walk"): SHIELD_WALK_FRAME_COUNT,
    ("shield", "jump"): SHIELD_JUMP_FRAME_COUNT,
    ("shield", "dash"): SHIELD_DASH_FRAME_COUNT,
    ("shield", "attack"): SHIELD_ATTACK_FRAME_COUNT,
    ("grapple", "idle"): GRAPPLE_IDLE_FRAME_COUNT,
    ("grapple", "walk"): GRAPPLE_WALK_FRAME_COUNT,
    ("grapple", "jump"): GRAPPLE_JUMP_FRAME_COUNT,
    ("grapple", "dash"): GRAPPLE_DASH_FRAME_COUNT,
    ("grapple", "attack"): GRAPPLE_ATTACK_FRAME_COUNT,
}

SOURCE_PREFIXES = {
    "light": "light_weapon",
    "heavy": "heavy_weapon",
    "shooter": "shoot_weapon",
    "shield": "shield_weapon",
    "grapple": "grapple_weapon",
}

OUTPUT_PREFIXES = {
    "light": "light_weapon",
    "heavy": "heavy_weapon",
    "shooter": "shooter_weapon",
    "shield": "shield_weapon",
    "grapple": "grapple_weapon",
}


def remove_generated_background(image):
    image = image.convert("RGBA")
    pixels = image.load()
    width, height = image.size

    corner_colors = [
        pixels[0, 0],
        pixels[width - 1, 0],
        pixels[0, height - 1],
        pixels[width - 1, height - 1],
    ]

    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0:
                continue

            is_bright_grey = (
                red > 210
                and green > 210
                and blue > 210
                and abs(red - green) < 15
                and abs(green - blue) < 15
            )
            is_corner_background = any(
                abs(red - bg_red) <= 4
                and abs(green - bg_green) <= 4
                and abs(blue - bg_blue) <= 4
                for bg_red, bg_green, bg_blue, _ in corner_colors
            )

            if is_bright_grey or is_corner_background:
                pixels[x, y] = (red, green, blue, 0)

    return image


def visible_bounds(image):
    width, height = image.size
    min_x = width
    min_y = height
    max_x = -1
    max_y = -1
    alpha = image.getchannel("A")

    for y in range(height):
        for x in range(width):
            if alpha.getpixel((x, y)) > 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if max_x == -1:
        return None

    return min_x, min_y, max_x + 1, max_y + 1


def estimated_character_bounds(image):
    bounds = visible_bounds(image)
    if bounds is None:
        return None

    alpha = image.getchannel("A")
    row_counts = []
    for y in range(image.height):
        count = 0
        for x in range(image.width):
            if alpha.getpixel((x, y)) > 0:
                count += 1
        row_counts.append(count)

    max_row_count = max(row_counts)
    if max_row_count <= 0:
        return bounds

    threshold = max(6, int(max_row_count * 0.18))
    dense_rows = [index for index, count in enumerate(row_counts) if count >= threshold]
    if not dense_rows:
        return bounds

    top = min(dense_rows)
    bottom = max(dense_rows) + 1
    full_left, _, full_right, _ = bounds
    return full_left, top, full_right, bottom


def estimated_character_height(image):
    bounds = estimated_character_bounds(image)
    if bounds is None:
        return 1

    return max(1, bounds[3] - bounds[1])


def crop_slot(image, slot_box, padding):
    slot = image.crop(slot_box)
    bounds = visible_bounds(slot)
    if bounds is None:
        return slot, 1

    left, top, right, bottom = bounds
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(slot.width, right + padding)
    bottom = min(slot.height, bottom + padding)
    frame = slot.crop((left, top, right, bottom))
    return frame, estimated_character_height(frame)


def crop_visible_frame(image, padding):
    bounds = visible_bounds(image)
    if bounds is None:
        return image, 1

    left, top, right, bottom = bounds
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(image.width, right + padding)
    bottom = min(image.height, bottom + padding)
    frame = image.crop((left, top, right, bottom))
    return frame, estimated_character_height(frame)


def crop_manual_rect(source_image, rect, padding):
    x, y, width, height = rect
    frame = source_image.crop((x, y, x + width, y + height))
    frame = remove_generated_background(frame)
    return crop_visible_frame(frame, padding)


def draw_source_rect_debug(source_image, rects, output_path):
    debug_image = source_image.convert("RGBA")
    draw = ImageDraw.Draw(debug_image)

    for index, (x, y, width, height) in enumerate(rects, start=1):
        draw.rectangle((x, y, x + width - 1, y + height - 1), outline=(255, 0, 0, 255), width=4)
        text_y = max(0, y - 18)
        draw.text((x + 6, text_y), str(index), fill=(255, 0, 0, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    debug_image.save(output_path)


def equal_slot_rects(source_image, frame_count):
    rects = []
    for index in range(frame_count):
        slot_left = round(index * source_image.width / frame_count)
        slot_right = round((index + 1) * source_image.width / frame_count)
        rects.append((slot_left, 0, slot_right - slot_left, source_image.height))
    return rects


def median_processed_character_height(sheet_path, frame_count, canvas_size):
    if not sheet_path.exists():
        return None

    sheet = Image.open(sheet_path).convert("RGBA")
    heights = []
    for index in range(frame_count):
        left = index * canvas_size[0]
        frame = sheet.crop((left, 0, left + canvas_size[0], canvas_size[1]))
        heights.append(estimated_character_height(frame))

    return max(1, statistics.median(heights))


def collect_source_character_heights(source_path, frame_count, manual_rects=None):
    if not source_path.exists():
        return []

    source_image = Image.open(source_path)
    frames = []
    if manual_rects is not None:
        for rect in manual_rects:
            frame, character_height = crop_manual_rect(source_image, rect, padding=12)
            frames.append(character_height)
    else:
        sheet = remove_generated_background(source_image)
        for index in range(frame_count):
            slot_left = round(index * sheet.width / frame_count)
            slot_right = round((index + 1) * sheet.width / frame_count)
            _, character_height = crop_slot(
                sheet,
                (slot_left, 0, slot_right, sheet.height),
                padding=12,
            )
            frames.append(character_height)

    return frames


def get_reference_character_height():
    reference_name = f"{REFERENCE_WEAPON}_{REFERENCE_STATE}"
    reference_output_path = output_path_for(REFERENCE_WEAPON, REFERENCE_STATE)
    reference_canvas_size = MOVEMENT_CANVAS_SIZES[REFERENCE_WEAPON]
    reference_frame_count = FRAME_COUNTS[(REFERENCE_WEAPON, REFERENCE_STATE)]

    processed_height = median_processed_character_height(
        reference_output_path,
        reference_frame_count,
        reference_canvas_size,
    )
    if processed_height is not None:
        print("Reference size source:", reference_name)
        print("Reference file:", reference_output_path)
        print("Reference visible character height:", processed_height)
        return processed_height

    source_heights = collect_source_character_heights(
        source_path_for(REFERENCE_WEAPON, REFERENCE_STATE),
        reference_frame_count,
        MANUAL_IDLE_RECTS.get(REFERENCE_WEAPON),
    )
    if source_heights:
        reference_height = min(
            MOVEMENT_CHARACTER_HEIGHTS[REFERENCE_WEAPON],
            reference_canvas_size[1] - 2,
        )
        print("Reference size source:", reference_name)
        print("Reference visible character height:", reference_height)
        print("Reference source median before scaling:", statistics.median(source_heights))
        return reference_height

    raise FileNotFoundError(
        f"Could not determine reference size from {reference_name}"
    )


def draw_clean_debug(output_sheet, frame_count, canvas_size, output_path, reference_height=None):
    debug_image = output_sheet.copy()
    draw = ImageDraw.Draw(debug_image)
    baseline_y = canvas_size[1] - 2
    reference_top_y = baseline_y - reference_height if reference_height else None

    for index in range(frame_count):
        left = index * canvas_size[0]
        right = left + canvas_size[0] - 1
        draw.rectangle((left, 0, right, canvas_size[1] - 1), outline=(255, 0, 0, 255), width=3)
        draw.line((left, baseline_y, right, baseline_y), fill=(0, 255, 0, 255), width=3)
        if reference_top_y is not None:
            draw.line((left, reference_top_y, right, reference_top_y), fill=(0, 80, 255, 255), width=2)
        draw.text((left + 8, 8), str(index + 1), fill=(255, 0, 0, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    debug_image.save(output_path)


def normalize_sheet(
    source_path,
    output_path,
    frame_count,
    canvas_size,
    reference_character_height,
    padding=12,
    manual_rects=None,
    debug_name=None,
    process_name=None,
):
    if not source_path.exists():
        print(f"Missing source sheet: {source_path}")
        return False

    source_image = Image.open(source_path)
    cropped_frames = []
    visible_heights = []

    if debug_name:
        print("Creating debug for:", debug_name)
        print("source:", source_path)
        print("output:", output_path)

    if manual_rects is not None:
        if len(manual_rects) != frame_count:
            raise ValueError(
                f"{source_path.name} has {len(manual_rects)} manual rects, expected {frame_count}"
            )

        if debug_name:
            draw_source_rect_debug(
                source_image,
                manual_rects,
                OUTPUT_DEBUG / f"{debug_name}_source_rects.png",
            )

        for rect in manual_rects:
            frame, visible_height = crop_manual_rect(source_image, rect, padding)
            cropped_frames.append(frame)
            visible_heights.append(visible_height)
    else:
        if debug_name:
            draw_source_rect_debug(
                source_image,
                equal_slot_rects(source_image, frame_count),
                OUTPUT_DEBUG / f"{debug_name}_source_rects.png",
            )

        sheet = remove_generated_background(source_image)
        for index in range(frame_count):
            slot_left = round(index * sheet.width / frame_count)
            slot_right = round((index + 1) * sheet.width / frame_count)
            frame, visible_height = crop_slot(
                sheet,
                (slot_left, 0, slot_right, sheet.height),
                padding,
            )
            cropped_frames.append(frame)
            visible_heights.append(visible_height)

    median_height = max(1, statistics.median(visible_heights))
    scale_factor = reference_character_height / median_height
    max_fit_scale = min(
        canvas_size[0] / max(1, max(frame.width for frame in cropped_frames)),
        canvas_size[1] / max(1, max(frame.height for frame in cropped_frames)),
    )
    scale_factor = min(scale_factor, max_fit_scale)

    output_sheet = Image.new("RGBA", (canvas_size[0] * frame_count, canvas_size[1]), (0, 0, 0, 0))
    for index, frame in enumerate(cropped_frames):
        scaled_size = (
            max(1, round(frame.width * scale_factor)),
            max(1, round(frame.height * scale_factor)),
        )
        scaled_frame = frame.resize(scaled_size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        x = (canvas_size[0] - scaled_size[0]) // 2
        y = canvas_size[1] - scaled_size[1]
        canvas.alpha_composite(scaled_frame, (x, y))
        output_sheet.alpha_composite(canvas, (index * canvas_size[0], 0))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_sheet.save(output_path)
    if debug_name:
        draw_clean_debug(
            output_sheet,
            frame_count,
            canvas_size,
            OUTPUT_DEBUG / f"{debug_name}_clean_debug.png",
            reference_character_height,
        )

    print(f"source sheet path: {source_path}")
    print(f"output clean sheet path: {output_path}")
    if process_name:
        print("Processing:", process_name)
    print(f"frame count: {frame_count}")
    print(f"frame canvas size: {canvas_size[0]}x{canvas_size[1]}")
    print(f"reference character height: {reference_character_height}")
    print(f"estimated source character height: {median_height}")
    print(f"Scaled to reference height: {reference_character_height}")
    print(f"scale factor used: {scale_factor}")
    return True


def source_path_for(weapon, state):
    if state == "attack":
        return SOURCE_WEAPONS / f"{SOURCE_PREFIXES[weapon]}_attack.png"
    return SOURCE_ANIMATIONS / f"{SOURCE_PREFIXES[weapon]}_{state}.png"


def output_path_for(weapon, state):
    if state == "attack":
        return OUTPUT_WEAPONS / f"{weapon}_attack_clean.png"
    return OUTPUT_ANIMATIONS / f"{OUTPUT_PREFIXES[weapon]}_{state}_clean.png"


def draw_character_scale_comparison(reference_character_height):
    frames = []
    for weapon in ("light", "heavy", "shooter", "shield", "grapple"):
        canvas_size = MOVEMENT_CANVAS_SIZES[weapon]
        sheet_path = output_path_for(weapon, "idle")
        if not sheet_path.exists():
            print(f"Missing idle sheet for comparison: {sheet_path}")
            continue

        sheet = Image.open(sheet_path).convert("RGBA")
        frame = sheet.crop((0, 0, canvas_size[0], canvas_size[1]))
        frames.append((weapon, frame, canvas_size))

    if not frames:
        return

    padding = 24
    label_height = 18
    baseline_padding = 12
    max_height = max(frame.height for _, frame, _ in frames)
    width = sum(frame.width for _, frame, _ in frames) + padding * (len(frames) + 1)
    height = label_height + max_height + baseline_padding + 8
    baseline_y = label_height + max_height
    reference_top_y = baseline_y - reference_character_height

    comparison = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(comparison)
    draw.line((0, baseline_y, width, baseline_y), fill=(0, 180, 0, 255), width=3)
    draw.line((0, reference_top_y, width, reference_top_y), fill=(0, 80, 255, 255), width=2)

    x = padding
    for weapon, frame, _ in frames:
        y = baseline_y - frame.height
        comparison.alpha_composite(frame, (x, y))
        draw.rectangle((x, y, x + frame.width - 1, y + frame.height - 1), outline=(255, 0, 0, 255), width=2)
        draw.text((x, 2), weapon, fill=(0, 0, 0, 255))
        x += frame.width + padding

    OUTPUT_DEBUG.mkdir(parents=True, exist_ok=True)
    comparison.save(OUTPUT_DEBUG / "character_scale_comparison.png")


def main():
    reference_character_height = get_reference_character_height()
    print("Manual jump rects active for shooter:", bool(MANUAL_JUMP_RECTS.get("shooter")))
    print("Manual jump rects active for shield:", bool(MANUAL_JUMP_RECTS.get("shield")))
    processed_count = 0
    for weapon in ("light", "heavy", "shooter", "shield", "grapple"):
        for state in ("idle", "walk", "jump", "dash", "attack"):
            if state == "attack":
                canvas_size = ATTACK_CANVAS_SIZES[weapon]
            else:
                canvas_size = STATE_CANVAS_SIZES.get((weapon, state), MOVEMENT_CANVAS_SIZES[weapon])

            manual_rects = None
            debug_name = None

            if state == "attack":
                manual_rects = MANUAL_ATTACK_RECTS.get(weapon)
                debug_name = f"{weapon}_attack"
            elif state == "idle":
                manual_rects = MANUAL_IDLE_RECTS.get(weapon)
                debug_name = f"{weapon}_idle"
            elif state == "jump":
                manual_rects = MANUAL_JUMP_RECTS.get(weapon)
                if manual_rects:
                    debug_name = f"{weapon}_jump"
            else:
                manual_rects = None
                debug_name = None

            did_process = normalize_sheet(
                source_path_for(weapon, state),
                output_path_for(weapon, state),
                FRAME_COUNTS[(weapon, state)],
                canvas_size,
                reference_character_height,
                manual_rects=manual_rects,
                debug_name=debug_name,
                process_name=f"{weapon}_{state}",
            )
            if did_process:
                processed_count += 1

    draw_character_scale_comparison(reference_character_height)
    print(f"Processed sheets: {processed_count}")


if __name__ == "__main__":
    main()
