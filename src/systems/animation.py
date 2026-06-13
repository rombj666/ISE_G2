from pathlib import Path

import pygame
from PIL import Image, ImageSequence

try:
    import numpy as np
except ImportError:
    np = None


def load_gif_frames(path, colorkey=None):
    path = Path(path)
    if not path.exists():
        print(f"Warning: GIF animation missing: {path}")
        return []

    frames = []

    try:
        with Image.open(path) as gif:
            for gif_frame in ImageSequence.Iterator(gif):
                frame = gif_frame.convert("RGBA")

                if colorkey is not None:
                    key_r, key_g, key_b = colorkey
                    pixels = []
                    for red, green, blue, alpha in frame.getdata():
                        if red == key_r and green == key_g and blue == key_b:
                            pixels.append((red, green, blue, 0))
                        else:
                            pixels.append((red, green, blue, alpha))
                    frame.putdata(pixels)

                surface = pygame.image.fromstring(
                    frame.tobytes(),
                    frame.size,
                    frame.mode,
                ).convert_alpha()

                frames.append(surface)
    except (OSError, pygame.error) as error:
        print(f"Warning: Could not load GIF animation {path}: {error}")
        return []

    return frames


def remove_checker_background_from_frame(frame):
    frame = frame.copy()
    if np is not None:
        rgb = pygame.surfarray.pixels3d(frame)
        alpha = pygame.surfarray.pixels_alpha(frame)
        red = rgb[:, :, 0]
        green = rgb[:, :, 1]
        blue = rgb[:, :, 2]
        bright_grey_mask = (
            (red > 210) &
            (green > 210) &
            (blue > 210) &
            (np.abs(red.astype(int) - green.astype(int)) < 15) &
            (np.abs(green.astype(int) - blue.astype(int)) < 15)
        )
        alpha[bright_grey_mask] = 0
        del rgb
        del alpha
        return frame

    width = frame.get_width()
    height = frame.get_height()
    frame.lock()

    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = frame.get_at((x, y))
            is_bright_grey = (
                red > 210 and
                green > 210 and
                blue > 210 and
                abs(red - green) < 15 and
                abs(green - blue) < 15
            )

            if alpha > 0 and is_bright_grey:
                frame.set_at((x, y), (red, green, blue, 0))

    frame.unlock()
    return frame


def auto_crop_frame(frame, padding=6):
    width = frame.get_width()
    height = frame.get_height()
    min_x = width
    min_y = height
    max_x = -1
    max_y = -1

    frame.lock()
    for y in range(height):
        for x in range(width):
            if frame.get_at((x, y)).a > 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    frame.unlock()

    if max_x == -1:
        return frame

    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = min(width - 1, max_x + padding)
    max_y = min(height - 1, max_y + padding)

    crop_rect = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    return frame.subsurface(crop_rect).copy()


def scale_to_target_box(frame, target_size):
    target_width, target_height = target_size
    if target_width <= 0 or target_height <= 0:
        return frame

    scale = target_height / frame.get_height()
    scaled_width = max(1, int(frame.get_width() * scale))
    scaled_height = max(1, int(frame.get_height() * scale))

    if scaled_width > target_width:
        scale = target_width / frame.get_width()
        scaled_width = target_width
        scaled_height = max(1, int(frame.get_height() * scale))

    scaled_frame = pygame.transform.smoothscale(frame, (scaled_width, scaled_height))
    boxed_frame = pygame.Surface(target_size, pygame.SRCALPHA)
    x = (target_width - scaled_width) // 2
    y = target_height - scaled_height
    boxed_frame.blit(scaled_frame, (x, y))
    return boxed_frame


def scale_to_content_box_in_canvas(frame, content_size, canvas_size):
    content_frame = scale_to_target_box(frame, content_size)
    canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
    x = (canvas_size[0] - content_frame.get_width()) // 2
    y = canvas_size[1] - content_frame.get_height()
    canvas.blit(content_frame, (x, y))
    return canvas


def load_sprite_sheet(
    path,
    frame_count,
    remove_checker_background=True,
    auto_crop=True,
    target_size=None,
    crop_mode="content",
    padding=6,
    colorkey=None,
):
    if target_size is None:
        print("Warning: target_size missing for auto sprite sheet loader")
        return []

    if colorkey is not None:
        print("Warning: colorkey is ignored by auto sprite sheet loader")

    return load_ai_sprite_sheet(
        path,
        expected_frame_count=frame_count,
        target_size=target_size,
        remove_checker_background=remove_checker_background,
        padding=padding,
        crop_mode=crop_mode if auto_crop else "full_frame",
    )


def load_fixed_frame_sheet(
    path,
    frame_count,
    frame_width=None,
    frame_height=None,
    debug_name=None,
    target_size=None,
):
    path = Path(path)
    if debug_name:
        print(f"{debug_name} path: {path}")
        print(f"{debug_name} exists: {path.exists()}")

    if not path.exists():
        print(f"Missing fixed-frame sprite sheet: {path}")
        return []

    try:
        sheet = pygame.image.load(str(path)).convert_alpha()
    except (OSError, pygame.error) as error:
        print(f"Warning: Could not load fixed-frame sprite sheet {path}: {error}")
        return []

    sheet_width, sheet_height = sheet.get_size()
    if frame_count <= 0:
        print(f"Warning: invalid frame count {frame_count}: {path}")
        return []

    source_frame_width = sheet_width // frame_count
    source_frame_height = sheet_height
    if source_frame_width <= 0:
        print(f"Warning: sprite sheet too narrow for {frame_count} frames: {path}")
        return []

    if sheet_width % frame_count != 0:
        print(
            f"Warning: sheet width {sheet_width} is not evenly divisible by "
            f"{frame_count}: {path}"
        )

    if target_size is None and frame_width and frame_height:
        target_size = (frame_width, frame_height)

    if debug_name:
        print(f"{debug_name} sheet size: {sheet_width}x{sheet_height}")
        print(f"{debug_name} frame count: {frame_count}")
        print(
            f"{debug_name} calculated frame size: "
            f"{source_frame_width}x{source_frame_height}"
        )

    frames = []
    for index in range(frame_count):
        left = round(index * sheet_width / frame_count)
        right = round((index + 1) * sheet_width / frame_count)
        frame_rect = pygame.Rect(left, 0, right - left, source_frame_height)

        frame = sheet.subsurface(frame_rect).copy()
        if target_size and frame.get_size() != target_size:
            frame = scale_to_target_box(frame, target_size)

        if debug_name:
            alpha_bounds = frame.get_bounding_rect()
            print(
                f"{debug_name} frame {index} size: "
                f"{frame.get_size()} alpha bounds: {alpha_bounds}"
            )

        frames.append(frame)

    print(f"Loaded fixed-frame sprite sheet: {path}")
    print(f"Frame count: {len(frames)}")
    print(f"Source frame size: {source_frame_width}x{source_frame_height}")
    if target_size:
        print(f"Frame canvas size: {target_size[0]}x{target_size[1]}")
    return frames


def get_visible_bounds(frame, left, right, padding):
    width = frame.get_width()
    height = frame.get_height()
    if np is not None:
        alpha = pygame.surfarray.pixels_alpha(frame)
        visible_points = np.argwhere(alpha[left:right, :] > 0)
        del alpha

        if visible_points.size == 0:
            return None

        min_y = int(visible_points[:, 1].min())
        max_y = int(visible_points[:, 1].max())
        return pygame.Rect(
            max(0, left - padding),
            max(0, min_y - padding),
            min(width, right + padding) - max(0, left - padding),
            min(height, max_y + padding + 1) - max(0, min_y - padding),
        )

    min_y = height
    max_y = -1

    frame.lock()
    for x in range(left, right):
        for y in range(height):
            if frame.get_at((x, y)).a > 0:
                min_y = min(min_y, y)
                max_y = max(max_y, y)
    frame.unlock()

    if max_y == -1:
        return None

    return pygame.Rect(
        max(0, left - padding),
        max(0, min_y - padding),
        min(width, right + padding) - max(0, left - padding),
        min(height, max_y + padding + 1) - max(0, min_y - padding),
    )


def pad_rect(rect, max_width, max_height, padding_x=0, padding_y=0, min_x=0, max_x=None):
    if max_x is None:
        max_x = max_width

    left = max(min_x, rect.left - padding_x)
    top = max(0, rect.top - padding_y)
    right = min(max_x, rect.right + padding_x)
    bottom = min(max_height, rect.bottom + padding_y)
    return pygame.Rect(left, top, right - left, bottom - top)


def get_visible_bounds_in_rect(frame, search_rect):
    width = frame.get_width()
    height = frame.get_height()
    search_rect = search_rect.clip(pygame.Rect(0, 0, width, height))

    if np is not None:
        alpha = pygame.surfarray.pixels_alpha(frame)
        visible_points = np.argwhere(
            alpha[
                search_rect.left:search_rect.right,
                search_rect.top:search_rect.bottom,
            ] > 0
        )
        del alpha

        if visible_points.size == 0:
            return None

        min_x = int(visible_points[:, 0].min()) + search_rect.left
        max_x = int(visible_points[:, 0].max()) + search_rect.left
        min_y = int(visible_points[:, 1].min()) + search_rect.top
        max_y = int(visible_points[:, 1].max()) + search_rect.top
        return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    min_x = width
    min_y = height
    max_x = -1
    max_y = -1

    frame.lock()
    for x in range(search_rect.left, search_rect.right):
        for y in range(search_rect.top, search_rect.bottom):
            if frame.get_at((x, y)).a > 0:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    frame.unlock()

    if max_x == -1:
        return None

    return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)


def detect_visible_column_groups(
    sheet,
    padding=8,
    min_component_area=100,
    merge_gap=20,
    min_column_pixels=1,
):
    width = sheet.get_width()
    height = sheet.get_height()
    visible_columns = []

    sheet.lock()
    for x in range(width):
        visible_pixel_count = 0
        for y in range(height):
            if sheet.get_at((x, y)).a > 0:
                visible_pixel_count += 1
        if visible_pixel_count >= min_column_pixels:
            visible_columns.append(x)
    sheet.unlock()

    if not visible_columns:
        return []

    groups = []
    group_left = visible_columns[0]
    previous_x = visible_columns[0]

    for x in visible_columns[1:]:
        if x - previous_x <= merge_gap:
            previous_x = x
            continue

        groups.append((group_left, previous_x + 1))
        group_left = x
        previous_x = x

    groups.append((group_left, previous_x + 1))

    crop_rects = []
    for left, right in groups:
        rect = get_visible_bounds(sheet, left, right, padding)
        if rect is None:
            continue
        if rect.width * rect.height < min_component_area:
            continue
        crop_rects.append(rect)

    return crop_rects


def get_visible_column_counts(sheet):
    if np is not None:
        alpha = pygame.surfarray.pixels_alpha(sheet)
        counts = np.count_nonzero(alpha > 0, axis=1).tolist()
        del alpha
        return counts

    width = sheet.get_width()
    height = sheet.get_height()
    counts = []

    sheet.lock()
    for x in range(width):
        visible_pixel_count = 0
        for y in range(height):
            if sheet.get_at((x, y)).a > 0:
                visible_pixel_count += 1
        counts.append(visible_pixel_count)
    sheet.unlock()

    return counts


def detect_visible_column_groups_from_counts(
    sheet,
    column_counts,
    padding=8,
    min_component_area=100,
    merge_gap=20,
    min_column_pixels=1,
):
    visible_columns = [
        x for x, visible_pixel_count in enumerate(column_counts)
        if visible_pixel_count >= min_column_pixels
    ]

    if not visible_columns:
        return []

    groups = []
    group_left = visible_columns[0]
    previous_x = visible_columns[0]

    for x in visible_columns[1:]:
        if x - previous_x <= merge_gap:
            previous_x = x
            continue

        groups.append((group_left, previous_x + 1))
        group_left = x
        previous_x = x

    groups.append((group_left, previous_x + 1))

    crop_rects = []
    for left, right in groups:
        rect = get_visible_bounds(sheet, left, right, padding)
        if rect is None:
            continue
        if rect.width * rect.height < min_component_area:
            continue
        crop_rects.append(rect)

    return crop_rects


def detect_slot_frame_rects(sheet, expected_frame_count, padding=8, min_component_area=100):
    rects = []
    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()

    for index in range(expected_frame_count):
        left = round(index * sheet_width / expected_frame_count)
        right = round((index + 1) * sheet_width / expected_frame_count)
        rect = get_visible_bounds(sheet, left, right, padding)

        if rect is None or rect.width * rect.height < min_component_area:
            rect = pygame.Rect(left, 0, right - left, sheet_height)

        rects.append(rect)

    return rects


def has_poor_frame_detection(crop_rects, sheet_width, expected_frame_count):
    if len(crop_rects) != expected_frame_count:
        return True

    expected_width = sheet_width / expected_frame_count
    widths = [rect.width for rect in crop_rects]
    if not widths:
        return True

    too_small = min(widths) < expected_width * 0.35
    too_merged = max(widths) > expected_width * 2.25
    return too_small or too_merged


def merge_closest_frame_groups(crop_rects, expected_frame_count):
    crop_rects = sorted(crop_rects, key=lambda rect: rect.x)

    while len(crop_rects) > expected_frame_count:
        closest_gap_index = 0
        closest_gap = None

        for index in range(len(crop_rects) - 1):
            gap = crop_rects[index + 1].left - crop_rects[index].right
            if closest_gap is None or gap < closest_gap:
                closest_gap = gap
                closest_gap_index = index

        left_rect = crop_rects[closest_gap_index]
        right_rect = crop_rects[closest_gap_index + 1]
        merged_rect = left_rect.union(right_rect)
        crop_rects[closest_gap_index:closest_gap_index + 2] = [merged_rect]

    return crop_rects


def choose_best_frame_candidate(candidate, sheet_width, expected_frame_count):
    if not candidate:
        return [], None

    detected = len(candidate)
    expected_width = sheet_width / expected_frame_count
    selected = candidate
    if detected > expected_frame_count:
        selected = merge_closest_frame_groups(candidate, expected_frame_count)

    selected = sorted(selected, key=lambda rect: rect.x)
    widths = [rect.width for rect in selected]
    if not widths:
        return [], None

    too_wide_count = sum(width > expected_width * 1.25 for width in widths)
    too_narrow_count = sum(width < expected_width * 0.30 for width in widths)
    width_spread = max(widths) - min(widths)
    missing_frames = max(0, expected_frame_count - detected)
    extra_frames = max(0, detected - expected_frame_count)
    largest_width = max(widths)

    score = (
        missing_frames,
        too_wide_count,
        too_narrow_count,
        width_spread,
        extra_frames,
        largest_width,
    )
    return selected, score


def load_ai_sprite_sheet(
    path,
    expected_frame_count,
    target_size,
    remove_checker_background=True,
    padding=8,
    min_component_area=100,
    merge_gap=20,
    crop_mode="content",
    attack_padding_x=None,
    attack_padding_y=None,
    attack_content_target_size=None,
    attack_character_height=None,
):
    path = Path(path)
    if not path.exists():
        print(f"Missing sprite sheet: {path}")
        return []

    try:
        sheet = pygame.image.load(str(path)).convert_alpha()
    except (OSError, pygame.error) as error:
        print(f"Warning: Could not load sprite sheet {path}: {error}")
        return []

    if remove_checker_background:
        sheet = remove_checker_background_from_frame(sheet)

    if crop_mode == "slot_content":
        print(f"Loaded AI sprite sheet: {path}")
        print(f"Sheet size: {sheet.get_width()}x{sheet.get_height()}")
        print(f"Expected frame count: {expected_frame_count}")
        print("Crop mode: slot_content")

        frames = []
        for index in range(expected_frame_count):
            slot_left = round(index * sheet.get_width() / expected_frame_count)
            slot_right = round((index + 1) * sheet.get_width() / expected_frame_count)
            slot_rect = pygame.Rect(slot_left, 0, slot_right - slot_left, sheet.get_height())
            content_rect = get_visible_bounds_in_rect(sheet, slot_rect)
            if content_rect is None or content_rect.width * content_rect.height < min_component_area:
                content_rect = slot_rect
            else:
                content_rect = pad_rect(
                    content_rect,
                    sheet.get_width(),
                    sheet.get_height(),
                    padding,
                    padding,
                    min_x=slot_rect.left,
                    max_x=slot_rect.right,
                )

            print(f"slot_content frame {index}:")
            print(f"slot rect: {slot_rect}")
            print(f"content crop rect: {content_rect}")
            frame = sheet.subsurface(content_rect).copy()
            frame = scale_to_target_box(frame, target_size)
            print(f"final frame size: {frame.get_width()}x{frame.get_height()}")
            frames.append(frame)

        return frames

    if crop_mode == "slot_attack_content":
        print(f"Loaded AI sprite sheet: {path}")
        print(f"Sheet size: {sheet.get_width()}x{sheet.get_height()}")
        print(f"Expected frame count: {expected_frame_count}")
        print("Crop mode: slot_attack_content")

        frames = []
        content_size = attack_content_target_size or target_size
        for index in range(expected_frame_count):
            slot_left = round(index * sheet.get_width() / expected_frame_count)
            slot_right = round((index + 1) * sheet.get_width() / expected_frame_count)
            slot_rect = pygame.Rect(slot_left, 0, slot_right - slot_left, sheet.get_height())
            content_rect = get_visible_bounds_in_rect(sheet, slot_rect)
            if content_rect is None or content_rect.width * content_rect.height < min_component_area:
                content_rect = slot_rect
            else:
                content_rect = pad_rect(
                    content_rect,
                    sheet.get_width(),
                    sheet.get_height(),
                    padding,
                    padding,
                    min_x=slot_rect.left,
                    max_x=slot_rect.right,
                )

            print(f"slot_attack_content frame {index}:")
            print(f"slot rect: {slot_rect}")
            print(f"content crop rect: {content_rect}")
            frame = sheet.subsurface(content_rect).copy()
            frame = scale_to_content_box_in_canvas(frame, content_size, target_size)
            print(f"final frame size: {frame.get_width()}x{frame.get_height()}")
            frames.append(frame)

        return frames

    if crop_mode == "slot_attack_fixed_scale":
        print(f"Loaded AI sprite sheet: {path}")
        print(f"Sheet size: {sheet.get_width()}x{sheet.get_height()}")
        print(f"Expected frame count: {expected_frame_count}")
        print("Crop mode: slot_attack_fixed_scale")

        cropped_frames = []
        visible_heights = []
        for index in range(expected_frame_count):
            slot_left = round(index * sheet.get_width() / expected_frame_count)
            slot_right = round((index + 1) * sheet.get_width() / expected_frame_count)
            slot_rect = pygame.Rect(slot_left, 0, slot_right - slot_left, sheet.get_height())
            visible_rect = get_visible_bounds_in_rect(sheet, slot_rect)
            if visible_rect is None or visible_rect.width * visible_rect.height < min_component_area:
                visible_rect = slot_rect
                crop_rect = slot_rect
            else:
                crop_rect = pad_rect(
                    visible_rect,
                    sheet.get_width(),
                    sheet.get_height(),
                    padding,
                    padding,
                    min_x=slot_rect.left,
                    max_x=slot_rect.right,
                )

            visible_height = max(1, visible_rect.height)
            print(f"slot_attack_fixed_scale frame {index}:")
            print(f"slot rect: {slot_rect}")
            print(f"visible crop rect: {crop_rect}")
            print(f"visible height: {visible_height}")
            cropped_frames.append(sheet.subsurface(crop_rect).copy())
            visible_heights.append(visible_height)

        sorted_heights = sorted(visible_heights)
        midpoint = len(sorted_heights) // 2
        if len(sorted_heights) % 2 == 0:
            median_height = (sorted_heights[midpoint - 1] + sorted_heights[midpoint]) / 2
        else:
            median_height = sorted_heights[midpoint]

        if attack_character_height is None or median_height <= 0:
            shared_scale_factor = 1
        else:
            shared_scale_factor = attack_character_height / median_height

        print(f"median height: {median_height}")
        print(f"shared scale factor: {shared_scale_factor}")

        frames = []
        for frame in cropped_frames:
            scaled_width = max(1, int(frame.get_width() * shared_scale_factor))
            scaled_height = max(1, int(frame.get_height() * shared_scale_factor))
            scaled_frame = pygame.transform.smoothscale(frame, (scaled_width, scaled_height))
            canvas = pygame.Surface(target_size, pygame.SRCALPHA)
            x = (target_size[0] - scaled_width) // 2
            y = target_size[1] - scaled_height
            canvas.blit(scaled_frame, (x, y))
            print(f"final frame size: {canvas.get_width()}x{canvas.get_height()}")
            frames.append(canvas)

        return frames

    crop_rects = []
    selected_threshold = None
    best_candidate = []
    best_score = None
    column_counts = get_visible_column_counts(sheet)

    for min_column_pixels in (1, 3, 5, 8, 12, 16, 24, 32, 48, 64, 80, 96, 128, 160):
        candidate = detect_visible_column_groups_from_counts(
            sheet,
            column_counts,
            padding,
            min_component_area,
            merge_gap,
            min_column_pixels,
        )
        selected_candidate, score = choose_best_frame_candidate(
            candidate,
            sheet.get_width(),
            expected_frame_count,
        )
        if score is None:
            continue

        score_with_threshold = score[:3] + (min_column_pixels,) + score[3:]
        if best_score is None or score_with_threshold < best_score:
            best_candidate = selected_candidate
            best_score = score_with_threshold
            selected_threshold = min_column_pixels

    crop_rects = best_candidate
    detected_count = len(crop_rects)

    print(f"Loaded AI sprite sheet: {path}")
    print(f"Sheet size: {sheet.get_width()}x{sheet.get_height()}")
    print(f"Expected frame count: {expected_frame_count}")
    print(f"Detected frame count: {detected_count}")
    print(f"Column pixel threshold: {selected_threshold}")
    print(f"Crop mode: {crop_mode}")

    if detected_count < expected_frame_count:
        print("Warning: Detected fewer frames than expected; using detected frames only")

    if detected_count >= expected_frame_count and has_poor_frame_detection(crop_rects, sheet.get_width(), expected_frame_count):
        print("Warning: Detected uneven frame groups; keeping auto-detected crops")

    if detected_count > expected_frame_count:
        crop_rects = sorted(crop_rects, key=lambda rect: rect.width * rect.height, reverse=True)
        crop_rects = crop_rects[:expected_frame_count]

    crop_rects = sorted(crop_rects, key=lambda rect: rect.x)
    if crop_mode == "attack_content":
        pad_x = padding if attack_padding_x is None else attack_padding_x
        pad_y = padding if attack_padding_y is None else attack_padding_y
        padded_rects = []
        for index, rect in enumerate(crop_rects):
            padded_rect = pad_rect(
                rect,
                sheet.get_width(),
                sheet.get_height(),
                pad_x,
                pad_y,
            )
            print(f"attack_content frame {index}:")
            print(f"content rect: {rect}")
            print(f"padded attack rect: {padded_rect}")
            padded_rects.append(padded_rect)
        crop_rects = padded_rects
    elif crop_mode == "full_frame":
        crop_rects = [
            pygame.Rect(rect.x, 0, rect.width, sheet.get_height())
            for rect in crop_rects
        ]

    frames = []

    for index, rect in enumerate(crop_rects):
        print(f"Crop rect {index}: {rect}")
        frame = sheet.subsurface(rect).copy()
        if crop_mode == "attack_content" and attack_content_target_size is not None:
            frame = scale_to_content_box_in_canvas(frame, attack_content_target_size, target_size)
        else:
            frame = scale_to_target_box(frame, target_size)
        print(f"Final frame size {index}: {frame.get_width()}x{frame.get_height()}")
        frames.append(frame)

    return frames
