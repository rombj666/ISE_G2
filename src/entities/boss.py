import math
import random
from pathlib import Path

import numpy as np
import pygame

from settings import (
    BOSS_BEAM_ATTACK_SCALE,
    BOSS_BEAM_READY_SCALE,
    BOSS_BEAM_SOURCE_ANCHOR,
    BOSS_HEAD_SCALE,
    BOSS_HIT_EFFECT_SCALE,
    BOSS_ROOM_HEIGHT,
    BOSS_ROOM_MAX_X,
    BOSS_ROOM_MAX_Y,
    BOSS_ROOM_MIN_X,
    BOSS_ROOM_MIN_Y,
    BOSS_ROOM_WIDTH,
    HAND_SLAM_WARNING_ANIM_SPEED,
    HAND_SLAM_WARNING_SCALE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEBUG_OUTPUT_DIR = PROJECT_ROOT / "assets" / "processed" / "debug"
BOSS_ASSET_DIR = PROJECT_ROOT / "assets" / "boss"
BOSS_WRITE_DEBUG_PREVIEWS = False
BOSS_ASSETS = {
    "arena_background": BOSS_ASSET_DIR / "boss_arena_background.png",
    "main_body": BOSS_ASSET_DIR / "boss_main_body.png",
    "hand": BOSS_ASSET_DIR / "boss_hand.png",
    "hit_effect": BOSS_ASSET_DIR / "boss_hit_effect_clean.png",
    "core_standby": BOSS_ASSET_DIR / "core_standby.png",
    "hand_slam_warning": BOSS_ASSET_DIR / "hand_slam_warning.png",
    "hand_slam_down": BOSS_ASSET_DIR / "hand_slam_down.png",
    "lunar_shard_warning": BOSS_ASSET_DIR / "lunar_shard_warning.png",
    "lunar_shard_fall": BOSS_ASSET_DIR / "lunar_shard_fall.png",
    "beam_ready": BOSS_ASSET_DIR / "boss_beam_ready_clean.png",
    "beam_attack": BOSS_ASSET_DIR / "boss_beam_attack_clean.png",
    "moon_orb_spawn": BOSS_ASSET_DIR / "moon_orb_spawn.png",
    "moon_orb_fly": BOSS_ASSET_DIR / "moon_orb_fly.png",
}
BOSS_ROOM_BACKGROUND_RECT = pygame.Rect(BOSS_ROOM_MIN_X, BOSS_ROOM_MIN_Y, BOSS_ROOM_WIDTH, BOSS_ROOM_HEIGHT)
BOSS_MAIN_BODY_RECT = pygame.Rect(0, 0, 1, 1)
BOSS_ARENA_LEFT = BOSS_ROOM_MIN_X
BOSS_ARENA_RIGHT = BOSS_ROOM_MAX_X
BOSS_ARENA_TOP = BOSS_ROOM_MIN_Y
BOSS_ARENA_BOTTOM = BOSS_ROOM_MAX_Y
BOSS_ASSEMBLY_OFFSET_X = 130
BOSS_CORE_ROOM_RATIO_X = 0.46
BOSS_CORE_Y = 330
BOSS_HAND_MAX_HP = 150
BOSS_HAND_SCALE = 1.45
BOSS_HAND_SLAM_SCALE = 1.85
BOSS_HAND_BASE_SIZE = (260, 220)
BOSS_LEFT_HAND_OFFSET = (-340, 200)
BOSS_RIGHT_HAND_OFFSET = (340, 200)
BOSS_HAND_VISUAL_SIZE = (
    round(BOSS_HAND_BASE_SIZE[0] * BOSS_HAND_SCALE),
    round(BOSS_HAND_BASE_SIZE[1] * BOSS_HAND_SCALE),
)
BOSS_CORE_TARGET_SIZE = (160, 140)
BOSS_CORE_FRAME_COUNT = 6
BOSS_CORE_FRAME_DURATION = 0.12
BOSS_PROJECTILE_TARGET_SIZE = (180, 120)
BOSS_GROUND_TARGET_SIZE = (320, 220)
BOSS_SHARD_WARNING_TARGET_SIZE = (160, 110)
BOSS_SHARD_FALL_TARGET_SIZE = (180, 220)
BOSS_HAND_WARNING_TARGET_SIZE = (300, 160)
BOSS_HIT_EFFECT_TARGET_SIZE = (180, 150)
BOSS_HAND_TARGET_SIZE = (
    round(BOSS_HAND_BASE_SIZE[0] * BOSS_HAND_SLAM_SCALE),
    round(BOSS_HAND_BASE_SIZE[1] * BOSS_HAND_SLAM_SCALE),
)
BOSS_BEAM_READY_SIZE = (260, 180)
BOSS_BEAM_ATTACK_SIZE = (280, 190)
BOSS_BEAM_WIDTH = 96
BOSS_BEAM_GLOW_WIDTH = 190
BOSS_BEAM_TOP_Y = 80
BOSS_BEAM_FLOOR_Y = 650
BOSS_BEAM_READY_DURATION = 0.45
BOSS_BEAM_FIRE_DURATION = 1.35
BOSS_BEAM_COLOR_INNER = (230, 255, 255, 235)
BOSS_BEAM_COLOR_MID = (105, 235, 255, 175)
BOSS_BEAM_COLOR_OUTER = (50, 145, 255, 65)
BOSS_BEAM_START_OFFSET_X = 0
BOSS_BEAM_START_OFFSET_Y = 72
BOSS_HEAD_MIDBOTTOM_OFFSET_Y = 150
BOSS_VULNERABLE_GLOW_SPEED = 4.8
BOSS_VULNERABLE_GLOW_RADIUS = 122
BOSS_VULNERABLE_SPARK_COUNT = 12
HAND_SLAM_WARNING_TIME = 1.0
HAND_SLAM_FALL_TIME = 1.1
HAND_SLAM_RECOVER_TIME = 0.5
HAND_SLAM_START_OFFSET_Y = -520
HAND_SLAM_DAMAGE = 25
HAND_SLAM_COOLDOWN = 4.0
HAND_SLAM_TARGET_FLOOR_Y = 650

MANUAL_BOSS_PROJECTILE_RECTS = None
MANUAL_BOSS_GROUND_RECTS = None
MANUAL_BOSS_BEAM_RECTS = None

# Adjust these rects manually if frame position/crop is wrong.
# Format: (x, y, width, height)
BOSS_EFFECT_FRAME_COUNTS = {
    "slam_warning": 4,
    "boss_hit_effect": 4,
    "beam_ready": 6,
    "beam_attack": 6,
    "moon_orb_spawn": 4,
}

BOSS_EFFECT_CONFIG = {
    "moon_orb_spawn": {
        "category": "projectile",
        "target_size": BOSS_PROJECTILE_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_PROJECTILE_RECTS,
        "debug_name": "boss_projectile_spawn",
    },
    "moon_orb_fly": {
        "category": "projectile",
        "target_size": BOSS_PROJECTILE_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_PROJECTILE_RECTS,
        "debug_name": "boss_projectile",
    },
    "lunar_shard_warning": {
        "category": "ground",
        "target_size": BOSS_SHARD_WARNING_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_GROUND_RECTS,
        "debug_name": "boss_ground",
    },
    "lunar_shard_fall": {
        "category": "ground",
        "target_size": BOSS_SHARD_FALL_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_GROUND_RECTS,
        "debug_name": "boss_ground_fall",
    },
    "hand_slam_warning": {
        "category": "ground",
        "target_size": BOSS_HAND_WARNING_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_GROUND_RECTS,
        "debug_name": "boss_ground_slam_warning",
    },
    "hand_slam_down": {
        "category": "ground",
        "target_size": BOSS_HAND_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_GROUND_RECTS,
        "debug_name": "boss_ground_slam_down",
    },
    "boss_hit_effect": {
        "category": "hit",
        "target_size": BOSS_HIT_EFFECT_TARGET_SIZE,
        "manual_rects": None,
        "debug_name": "boss_hit_effect",
    },
}


class BossHandPart:
    def __init__(self, name, anchor_position, image):
        self.name = name
        self.max_hp = BOSS_HAND_MAX_HP
        self.current_hp = self.max_hp
        self.anchor_position = anchor_position
        self.rect = image.get_rect(center=anchor_position) if image is not None else pygame.Rect(0, 0, 140, 110)
        self.rect.center = anchor_position
        self.visible = True
        self.is_alive = True
        self.can_slam = True
        self.slam_cooldown_timer = 0
        self.is_slamming = False
        self.slam_warning_active = False
        self.slam_target_x = anchor_position[0]
        self.slam_target_y = anchor_position[1]
        self.slam_warning_pos = anchor_position
        self.slam_rect = self.rect.copy()
        self.slam_timer = 0
        self.slam_warning_elapsed = 0
        self.slam_phase = "idle"
        self.slam_hit = False
        self.slam_landed = False

    def reset(self, anchor_position, image):
        self.current_hp = self.max_hp
        self.anchor_position = anchor_position
        self.rect = image.get_rect(center=anchor_position) if image is not None else pygame.Rect(0, 0, 140, 110)
        self.rect.center = anchor_position
        self.visible = True
        self.is_alive = True
        self.can_slam = True
        self.slam_cooldown_timer = 0
        self.cancel_slam()

    def cancel_slam(self):
        self.is_slamming = False
        self.slam_warning_active = False
        self.slam_phase = "idle"
        self.slam_timer = 0
        self.slam_warning_elapsed = 0
        self.slam_hit = False
        self.slam_landed = False
        self.slam_warning_pos = self.anchor_position
        self.slam_rect = self.rect.copy()


class PaleCoreBoss:
    """Map 8 boss using the lunar core as the vulnerable damage target."""

    FRAME_COUNTS = {
        "moon_orb_spawn": 4,
        "moon_orb_fly": 4,
        "lunar_shard_warning": 4,
        "lunar_shard_fall": 4,
        "hand_slam_warning": BOSS_EFFECT_FRAME_COUNTS["slam_warning"],
        "hand_slam_down": 6,
        "boss_hit_effect": BOSS_EFFECT_FRAME_COUNTS["boss_hit_effect"],
    }

    def __init__(self):
        self.max_hp = 500
        self.current_hp = self.max_hp
        self.phase = 1
        self.state = "idle"
        self.defeated = False
        self.active = False
        self.attack_count = 0
        self.attacks_since_weakpoint = 0
        self.attack_index = 0
        self.active_attack_skills = []
        self.last_skill_signature = None
        self.same_skill_repeat_count = 0
        self.current_attack_duration = 0
        self.state_timer = 1.2
        self.frame_timer = 0
        self.frame_index = 0
        self.core_frame_timer = 0
        self.current_core_frame = 0
        self.last_debug_core_frame = None
        self.float_timer = 0
        self.float_offset_y = 0
        self.has_printed_missing_asset_warning = False

        self.arena_rect = pygame.Rect(
            BOSS_ARENA_LEFT,
            BOSS_ARENA_TOP,
            BOSS_ARENA_RIGHT - BOSS_ARENA_LEFT,
            BOSS_ARENA_BOTTOM - BOSS_ARENA_TOP,
        )
        self.boss_room_background_rect = BOSS_ROOM_BACKGROUND_RECT.copy()
        self.body_rect = BOSS_MAIN_BODY_RECT.copy()
        self.base_core_center = (
            BOSS_ROOM_MIN_X + round(BOSS_ROOM_WIDTH * BOSS_CORE_ROOM_RATIO_X) + BOSS_ASSEMBLY_OFFSET_X,
            BOSS_CORE_Y,
        )
        self.core_center = self.base_core_center
        self.weakpoint_rect = pygame.Rect(0, 0, 1, 1)
        self.weakpoint_rect.center = self.core_center
        self.left_hand_anchor = self.get_hand_anchor("left")
        self.right_hand_anchor = self.get_hand_anchor("right")
        self.weakpoint_open = False
        self.weakpoint_hit_cooldown = 0
        self.hit_effect_timer = 0
        self.boss_hit_effects = []
        self.phase2_hands_ready = False
        self.last_core_invulnerable_print = None

        self.boss_room_background = None
        self.boss_room_background_source_size = None
        self.boss_main_body = None
        self.boss_core_image = None
        self.boss_core_frames = []
        self.boss_head_rect = pygame.Rect(0, 0, 1, 1)
        self.boss_core_rect = pygame.Rect(0, 0, 1, 1)
        self.boss_hand = None
        self.boss_hand_left = None
        self.boss_hand_right = None
        self.boss_attack_hand_left = None
        self.boss_attack_hand_right = None
        self.boss_slam_hand_frames = []
        self.boss_beam_ready_frames = []
        self.boss_beam_attack_frames = []
        self.left_hand = None
        self.right_hand = None
        self.boss_image = None
        self.animations = {}
        self.boss_slam_warning_frames = []
        self.boss_hit_effect_frames = []
        self.moon_orbs = []
        self.shards = []
        self.hand_slams = []
        self.core_beam_rect = None
        self.core_beam_draw_rect = None
        self.core_beam_origin = self.core_center
        self.core_beam_ready_timer = 0
        self.core_beam_fire_timer = 0
        self.core_beam_facing = 1
        self.core_beam_active = False
        self.player_hit_cooldown = 0
        self.load_assets()
        self.print_startup_debug()

    def load_assets(self):
        background_path = BOSS_ASSETS["arena_background"]
        main_body_path = BOSS_ASSETS["main_body"]
        hand_path = BOSS_ASSETS["hand"]
        hand_slam_path = BOSS_ASSETS["hand_slam_down"]
        beam_ready_path = BOSS_ASSETS["beam_ready"]
        beam_attack_path = BOSS_ASSETS["beam_attack"]

        self.boss_room_background = self.load_boss_single_image("arena_background", self.boss_room_background_rect.size)
        if self.boss_room_background is not None:
            self.boss_room_background_source_size = self.boss_room_background.get_size()

        self.boss_main_body = self.load_boss_single_image("main_body", scale=BOSS_HEAD_SCALE)
        self.boss_image = self.boss_main_body

        self.boss_core_frames = self.load_fixed_frame_sheet(
            BOSS_ASSETS["core_standby"],
            BOSS_CORE_FRAME_COUNT,
            target_size=BOSS_CORE_TARGET_SIZE,
            debug_name="core_standby",
        )
        print("[BOSS CORE ASSET]", BOSS_ASSETS["core_standby"])
        if self.boss_core_frames:
            self.boss_core_image = self.boss_core_frames[0]
            self.boss_core_rect = self.boss_core_image.get_rect(center=self.base_core_center)
            self.weakpoint_rect = self.boss_core_rect.copy()
            print("[LOAD ANIM]", "core_standby", len(self.boss_core_frames), self.boss_core_frames[0].get_size())
        else:
            self.boss_core_image = self.create_lunar_core_surface(BOSS_CORE_TARGET_SIZE)
            self.boss_core_frames = [self.boss_core_image]
            self.boss_core_rect = pygame.Rect(0, 0, *BOSS_CORE_TARGET_SIZE)
            self.boss_core_rect.center = self.base_core_center
            self.weakpoint_rect = self.boss_core_rect.copy()
            print("[BOSS ASSET MISSING]", "core_standby", BOSS_ASSETS["core_standby"])

        if self.boss_image is not None:
            self.boss_head_rect = self.boss_image.get_rect()
            self.boss_head_rect.midbottom = (self.boss_core_rect.centerx, self.boss_core_rect.top + BOSS_HEAD_MIDBOTTOM_OFFSET_Y)
            self.body_rect = self.boss_head_rect.copy()
            self.left_hand_anchor = self.get_hand_anchor("left")
            self.right_hand_anchor = self.get_hand_anchor("right")

        self.boss_hand = self.load_boss_single_image("hand", BOSS_HAND_VISUAL_SIZE)
        if self.boss_hand is not None:
            self.boss_hand_left = self.boss_hand
            self.boss_hand_right = pygame.transform.flip(self.boss_hand, True, False)
        self.left_hand = BossHandPart("left", self.left_hand_anchor, self.boss_hand_left)
        self.right_hand = BossHandPart("right", self.right_hand_anchor, self.boss_hand_right)
        self.boss_slam_hand_frames = self.load_fixed_frame_sheet(
            hand_slam_path,
            self.FRAME_COUNTS["hand_slam_down"],
            target_size=BOSS_HAND_TARGET_SIZE,
            debug_name="boss_hand_slam_png",
        )
        if self.boss_slam_hand_frames:
            self.boss_attack_hand_right = self.boss_slam_hand_frames[0]
            self.boss_attack_hand_left = pygame.transform.flip(self.boss_attack_hand_right, True, False)

        self.boss_beam_ready_frames = self.load_fixed_frame_sheet(
            beam_ready_path,
            BOSS_EFFECT_FRAME_COUNTS["beam_ready"],
            scale=BOSS_BEAM_READY_SCALE,
            debug_name="boss_beam_ready",
        )
        self.boss_beam_attack_frames = self.load_fixed_frame_sheet(
            beam_attack_path,
            BOSS_EFFECT_FRAME_COUNTS["beam_attack"],
            scale=BOSS_BEAM_ATTACK_SCALE,
            debug_name="boss_beam_attack",
        )
        self.boss_slam_warning_frames = self.load_fixed_frame_sheet(
            BOSS_ASSETS["hand_slam_warning"],
            BOSS_EFFECT_FRAME_COUNTS["slam_warning"],
            scale=HAND_SLAM_WARNING_SCALE,
            debug_name="boss_slam_warning_frames",
        )
        self.animations["hand_slam_warning"] = self.boss_slam_warning_frames
        self.boss_hit_effect_frames = self.load_fixed_frame_sheet(
            BOSS_ASSETS["hit_effect"],
            BOSS_EFFECT_FRAME_COUNTS["boss_hit_effect"],
            scale=BOSS_HIT_EFFECT_SCALE,
            debug_name="boss_hit_effect_frames",
        )
        self.animations["boss_hit_effect"] = self.boss_hit_effect_frames
        self.animations["moon_orb_spawn"] = self.load_fixed_frame_sheet(
            BOSS_ASSETS["moon_orb_spawn"],
            BOSS_EFFECT_FRAME_COUNTS["moon_orb_spawn"],
            target_size=BOSS_PROJECTILE_TARGET_SIZE,
            debug_name="boss_moon_orb_spawn",
        )

        for name, frame_count in self.FRAME_COUNTS.items():
            if name in ("hand_slam_down", "hand_slam_warning", "boss_hit_effect", "moon_orb_spawn"):
                continue
            config = BOSS_EFFECT_CONFIG.get(name, {})
            self.animations[name] = self.load_boss_effect_sheet(
                self.get_boss_asset_path(name),
                frame_count,
                config.get("target_size", BOSS_GROUND_TARGET_SIZE),
                config.get("manual_rects"),
                config.get("debug_name", name),
            )

        print("[BOSS BEAM USES]", BOSS_ASSETS["beam_ready"], BOSS_ASSETS["beam_attack"])

    def get_boss_asset_path(self, effect_name):
        mapping = {
            "moon_orb_spawn": "moon_orb_spawn",
            "moon_orb_fly": "moon_orb_fly",
            "lunar_shard_warning": "lunar_shard_warning",
            "lunar_shard_fall": "lunar_shard_fall",
            "hand_slam_warning": "hand_slam_warning",
            "hand_slam_down": "hand_slam_down",
            "boss_hit_effect": "hit_effect",
        }
        key = mapping.get(effect_name, effect_name)
        return BOSS_ASSETS.get(key, PROJECT_ROOT / "assets" / "boss" / f"{effect_name}.png")

    def load_boss_single_image(self, key, target_size=None, scale=1.0):
        path = BOSS_ASSETS[key]
        if not path.exists():
            print("[BOSS ASSET MISSING]", key, path)
            return None
        try:
            image = pygame.image.load(path).convert_alpha()
        except pygame.error as exc:
            print("[BOSS ASSET MISSING]", key, path, exc)
            return None

        original_size = image.get_size()
        if key != "arena_background":
            image = self.force_boss_transparency(image, key)
        if target_size is not None:
            image = pygame.transform.smoothscale(image, target_size)
        elif scale != 1.0:
            scaled_size = (
                max(1, round(image.get_width() * scale)),
                max(1, round(image.get_height() * scale)),
            )
            image = pygame.transform.smoothscale(image, scaled_size)
        print("[BOSS ASSET LOAD]", key, path, "OK", original_size)
        static_debug_names = {
            "arena_background": "boss_arena_background",
            "main_body": "boss_main_body",
            "hand": "boss_hand",
        }
        if key in static_debug_names:
            print("[LOAD STATIC]", static_debug_names[key], image.get_size())
            print("[BOSS LOAD]", static_debug_names[key], image.get_flags(), image.get_size())
        return image

    def load_image(self, path):
        if not path.exists():
            print("PaleCoreBoss missing asset:", path)
            return None
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as exc:
            print("PaleCoreBoss failed to load asset:", path, exc)
            return None

    def force_boss_transparency(self, surface, debug_name):
        if surface.get_flags() & pygame.SRCALPHA and surface.get_bounding_rect(min_alpha=1) != surface.get_rect():
            return surface

        width, height = surface.get_size()
        if width <= 0 or height <= 0:
            return surface

        samples = self.get_boss_border_samples(surface)
        if not self.samples_look_like_box_background(samples):
            return surface

        cleaned = surface.copy()
        removed_pixels = 0
        rgb = pygame.surfarray.pixels3d(cleaned)
        alpha = pygame.surfarray.pixels_alpha(cleaned)
        for color in self.get_boss_background_keys(samples):
            key = np.array((color.r, color.g, color.b), dtype=np.int16)
            diff = np.abs(rgb.astype(np.int16) - key)
            mask = (alpha >= 120) & (diff[:, :, 0] <= 42) & (diff[:, :, 1] <= 42) & (diff[:, :, 2] <= 42)
            removed_pixels += int(np.count_nonzero(mask))
            alpha[mask] = 0
        del rgb
        del alpha

        if removed_pixels:
            print("[BOSS ALPHA FIX]", debug_name, removed_pixels)
        return cleaned

    def get_boss_border_samples(self, surface):
        width, height = surface.get_size()
        points = []
        sample_count = 12
        for index in range(sample_count):
            x = round(index * (width - 1) / max(1, sample_count - 1))
            y = round(index * (height - 1) / max(1, sample_count - 1))
            points.extend(((x, 0), (x, height - 1), (0, y), (width - 1, y)))
        return [surface.get_at(point) for point in points]

    def samples_look_like_box_background(self, samples):
        if not samples:
            return False
        opaque_samples = [sample for sample in samples if sample.a >= 120]
        if len(opaque_samples) < max(6, len(samples) // 3):
            return False
        light_matching = sum(1 for sample in opaque_samples if self.is_white_or_checker_color(sample))
        if light_matching >= max(6, len(samples) // 3):
            return True
        dominant_matching = 0
        for sample in opaque_samples:
            dominant_matching = max(
                dominant_matching,
                sum(1 for other in opaque_samples if self.color_distance(sample, other) <= 42),
            )
        return dominant_matching >= max(6, len(samples) // 3)

    def is_white_or_checker_color(self, color):
        spread = max(color.r, color.g, color.b) - min(color.r, color.g, color.b)
        near_white = color.r >= 228 and color.g >= 228 and color.b >= 228
        light_gray = color.r >= 170 and color.g >= 170 and color.b >= 170 and spread <= 26
        return near_white or light_gray

    def get_boss_background_keys(self, samples):
        keys = []
        for sample in samples:
            if sample.a < 120:
                continue
            if not self.is_white_or_checker_color(sample):
                matching = sum(1 for other in samples if other.a >= 120 and self.color_distance(sample, other) <= 42)
                if matching < max(6, len(samples) // 3):
                    continue
            if any(self.color_distance(sample, existing) <= 42 for existing in keys):
                continue
            keys.append(sample)
            if len(keys) >= 6:
                break
        return keys

    def color_distance(self, color, sample):
        return abs(color.r - sample.r) + abs(color.g - sample.g) + abs(color.b - sample.b)

    def create_lunar_core_surface(self, size):
        surface = pygame.Surface(size, pygame.SRCALPHA)
        center = (size[0] // 2, size[1] // 2)
        outer_radius = min(size) // 2 - 8
        pygame.draw.circle(surface, (35, 105, 145, 165), center, outer_radius)
        pygame.draw.circle(surface, (70, 205, 245, 215), center, round(outer_radius * 0.68))
        pygame.draw.circle(surface, (230, 255, 255, 235), center, round(outer_radius * 0.36))
        pygame.draw.circle(surface, (150, 245, 255, 235), center, outer_radius, 3)
        for index in range(8):
            angle = index * math.tau / 8
            start = (
                round(center[0] + math.cos(angle) * outer_radius * 0.55),
                round(center[1] + math.sin(angle) * outer_radius * 0.55),
            )
            end = (
                round(center[0] + math.cos(angle) * outer_radius * 0.92),
                round(center[1] + math.sin(angle) * outer_radius * 0.92),
            )
            pygame.draw.line(surface, (210, 255, 255, 155), start, end, 2)
        return surface

    def load_fixed_frame_sheet(
        self,
        path,
        frame_count,
        scale=1.0,
        target_size=None,
        debug_name=None,
        preserve_original_canvas=False,
    ):
        print("Boss fixed sheet file path:", path)
        print("Boss fixed frame count:", frame_count)
        if not path.exists():
            print("[BOSS ASSET MISSING]", debug_name or path.stem, path)
            return []
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except pygame.error as exc:
            print("[BOSS ASSET MISSING]", debug_name or path.stem, path, exc)
            return []

        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        frames = []
        for index in range(frame_count):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            source_rect = pygame.Rect(index * frame_width, 0, frame_width, frame_height)
            frame.blit(sheet, (0, 0), source_rect)
            if not preserve_original_canvas:
                frame = self.force_boss_transparency(frame, f"{debug_name or path.stem}_{index}")
            if not preserve_original_canvas and target_size is not None:
                frame = pygame.transform.smoothscale(frame, target_size)
            elif not preserve_original_canvas and scale != 1.0:
                scaled_size = (
                    max(1, round(frame_width * scale)),
                    max(1, round(frame_height * scale)),
                )
                frame = pygame.transform.smoothscale(frame, scaled_size)
            frames.append(frame)

        print("[BOSS ASSET LOAD]", debug_name or path.stem, path, "OK", len(frames))
        print("[LOAD]", path, "frames:", len(frames), "frame_size:", frames[0].get_size() if frames else None)
        print("Loaded fixed boss sheet:", path)
        print("Sheet size:", sheet.get_size())
        print("Frame size:", frames[0].get_size() if frames else None)
        if debug_name == "core_standby" and frames:
            print("[BOSS LOAD]", "core_standby frames", len(frames), frames[0].get_flags(), frames[0].get_size())
        if debug_name and BOSS_WRITE_DEBUG_PREVIEWS:
            source_rects = [pygame.Rect(i * frame_width, 0, frame_width, frame_height) for i in range(frame_count)]
            self.draw_source_rect_debug(sheet, source_rects, DEBUG_OUTPUT_DIR / f"{debug_name}_source_rects.png")
            self.draw_clean_debug(frames, DEBUG_OUTPUT_DIR / f"{debug_name}_clean_debug.png")
        return frames

    def load_manual_rect_sheet(self, path, rects, scale=1.0, debug_name=None):
        print("Boss manual rect sheet file path:", path)
        print("Boss manual rect frame count:", len(rects))
        if not path.exists():
            print("[BOSS ASSET MISSING]", debug_name or path.stem, path)
            return []
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except pygame.error as exc:
            print("[BOSS ASSET MISSING]", debug_name or path.stem, path, exc)
            return []

        frames = []
        source_rects = []
        for rect in rects:
            x, y, width, height = rect
            source_rect = pygame.Rect(x, y, width, height)
            frame = pygame.Surface((width, height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), source_rect)
            if scale != 1.0:
                frame = pygame.transform.smoothscale(
                    frame,
                    (max(1, round(width * scale)), max(1, round(height * scale))),
                )
            frames.append(frame)
            source_rects.append(source_rect)

        print("[MANUAL RECT LOAD]", path, "frames:", len(frames), "rects:", rects)
        print("[LOAD]", path, "frames:", len(frames), "frame_size:", frames[0].get_size() if frames else None)
        if debug_name and BOSS_WRITE_DEBUG_PREVIEWS:
            self.draw_source_rect_debug(sheet, source_rects, DEBUG_OUTPUT_DIR / f"{debug_name}_source_rects.png")
            self.draw_clean_debug(frames, DEBUG_OUTPUT_DIR / f"{debug_name}_clean_debug.png")
        return frames

    def load_boss_effect_sheet(
        self,
        path,
        frame_count,
        target_size,
        manual_rects=None,
        debug_name=None,
    ):
        print("Boss effect file path:", path)
        print("Boss effect frame count:", frame_count)
        print("Boss effect slicing:", "equal_horizontal_full_height")
        print("Boss effect target output size:", target_size)
        sheet = self.load_image(path)
        if sheet is None:
            return []

        source_rects = manual_rects or self.make_equal_source_rects(sheet, frame_count)
        frames = []
        for index, source_rect in enumerate(source_rects):
            raw_frame = pygame.Surface(source_rect.size, pygame.SRCALPHA)
            raw_frame.blit(sheet, (0, 0), source_rect)
            raw_frame = self.force_boss_transparency(raw_frame, f"{debug_name or path.stem}_{index}")
            frames.append(pygame.transform.smoothscale(raw_frame, target_size))

        print("Loaded boss effect sheet:", path)
        print("Sheet size:", sheet.get_size())
        print("Frame count:", len(frames))
        print("Frame size:", frames[0].get_size() if frames else None)
        if debug_name and BOSS_WRITE_DEBUG_PREVIEWS:
            self.draw_source_rect_debug(sheet, source_rects, DEBUG_OUTPUT_DIR / f"{debug_name}_source_rects.png")
            self.draw_clean_debug(frames, DEBUG_OUTPUT_DIR / f"{debug_name}_clean_debug.png")
        return frames

    def make_equal_source_rects(self, sheet, frame_count):
        frame_width = sheet.get_width() // frame_count
        if frame_width <= 0 or sheet.get_width() % frame_count != 0:
            print(
                "WARNING: Boss effect sheet width is not evenly divisible by frame count:",
                sheet.get_size(),
                "frames:",
                frame_count,
            )
            frame_width = max(1, sheet.get_width() // frame_count)

        rects = []
        for index in range(frame_count):
            rects.append(pygame.Rect(index * frame_width, 0, frame_width, sheet.get_height()))
        return rects

    def draw_source_rect_debug(self, sheet, source_rects, output_path):
        DEBUG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        debug_surface = sheet.copy()
        colors = [
            (255, 80, 80),
            (80, 255, 120),
            (80, 180, 255),
            (255, 230, 80),
            (220, 110, 255),
            (255, 150, 60),
        ]
        for index, rect in enumerate(source_rects):
            pygame.draw.rect(debug_surface, colors[index % len(colors)], rect, 4)
        pygame.image.save(debug_surface, output_path)

    def draw_clean_debug(self, frames, output_path):
        DEBUG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if not frames:
            return
        frame_width, frame_height = frames[0].get_size()
        debug_surface = pygame.Surface((frame_width * len(frames), frame_height), pygame.SRCALPHA)
        for index, frame in enumerate(frames):
            debug_surface.blit(frame, (index * frame_width, 0))
            pygame.draw.rect(
                debug_surface,
                (255, 255, 255),
                pygame.Rect(index * frame_width, 0, frame_width, frame_height),
                1,
            )
        pygame.image.save(debug_surface, output_path)

    def print_startup_debug(self):
        print("PaleCoreBoss asset folder:", BOSS_ASSET_DIR)
        print("PaleCoreBoss asset folder exists:", BOSS_ASSET_DIR.exists())
        print("PaleCoreBoss boss image loaded:", self.boss_image is not None)
        print("PaleCoreBoss room background loaded:", self.boss_room_background is not None)
        print("PaleCoreBoss main body loaded:", self.boss_main_body is not None)
        print("PaleCoreBoss hand loaded:", self.boss_hand is not None)
        print("[BOSS ROOM BOUNDS]", BOSS_ROOM_MIN_X, BOSS_ROOM_MAX_X, BOSS_ROOM_MIN_Y, BOSS_ROOM_MAX_Y)
        print("[BOSS ROOM SIZE]", BOSS_ROOM_WIDTH, BOSS_ROOM_HEIGHT)
        print("[BOSS BG SIZE]", self.boss_room_background_source_size, "scaled to", self.boss_room_background.get_size() if self.boss_room_background else None)
        print("[BOSS CORE RECT]", self.boss_core_rect)
        print("[BOSS HEAD RECT]", self.boss_head_rect)
        print("[CORE FRAME INDEX]", self.current_core_frame)
        print("[WEAK POINT IMAGE REMOVED] using lunar core glow")
        if self.left_hand is not None and self.right_hand is not None:
            print("[LEFT HAND POS]", self.left_hand.rect)
            print("[RIGHT HAND POS]", self.right_hand.rect)
        print("Boss projectile frames loaded:", len(self.animations.get("moon_orb_fly", [])))
        print("Boss ground effect frames loaded:", len(self.animations.get("lunar_shard_warning", [])))
        print("Boss hand slam PNG frames loaded:", len(self.boss_slam_hand_frames))
        print("Boss beam ready frames loaded:", len(self.boss_beam_ready_frames))
        print("[CORE VULNERABLE]", self.core_vulnerable)
        print(
            "[BOSS HIT EFFECT FRAMES]",
            len(self.boss_hit_effect_frames),
            self.boss_hit_effect_frames[0].get_size() if self.boss_hit_effect_frames else None,
        )
        print(
            "[HAND SLAM WARNING FRAMES]",
            len(self.boss_slam_warning_frames),
            self.boss_slam_warning_frames[0].get_size() if self.boss_slam_warning_frames else None,
        )
        print("Boss beam attack frames loaded:", len(self.boss_beam_attack_frames))
        for name in self.FRAME_COUNTS:
            if name == "hand_slam_down":
                continue
            print(f"PaleCoreBoss {name} frames loaded:", len(self.animations.get(name, [])))

    def reset(self):
        self.current_hp = self.max_hp
        self.phase = 1
        self.state = "idle"
        self.defeated = False
        self.active = False
        self.attack_count = 0
        self.attacks_since_weakpoint = 0
        self.attack_index = 0
        self.active_attack_skills = []
        self.last_skill_signature = None
        self.same_skill_repeat_count = 0
        self.current_attack_duration = 0
        self.state_timer = 1.2
        self.frame_timer = 0
        self.frame_index = 0
        self.core_frame_timer = 0
        self.current_core_frame = 0
        self.last_debug_core_frame = None
        self.float_timer = 0
        self.float_offset_y = 0
        self.update_core_anchor()
        self.weakpoint_open = False
        self.weakpoint_hit_cooldown = 0
        self.hit_effect_timer = 0
        self.boss_hit_effects.clear()
        self.phase2_hands_ready = False
        self.last_core_invulnerable_print = None
        self.reset_hands()
        self.moon_orbs.clear()
        self.shards.clear()
        self.hand_slams.clear()
        self.core_beam_rect = None
        self.core_beam_draw_rect = None
        self.core_beam_origin = self.core_center
        self.core_beam_ready_timer = 0
        self.core_beam_fire_timer = 0
        self.core_beam_facing = 1
        self.core_beam_active = False
        self.player_hit_cooldown = 0

    def reset_hands(self):
        if self.left_hand is not None:
            self.left_hand.reset(self.left_hand_anchor, self.boss_hand_left)
        if self.right_hand is not None:
            self.right_hand.reset(self.right_hand_anchor, self.boss_hand_right)

    def should_exist_on_map(self, map_id):
        return map_id == 8

    def should_draw_background(self, map_id, player):
        return self.should_exist_on_map(map_id) and player.rect.centerx >= BOSS_ROOM_MIN_X

    def update_activation(self, map_id, player):
        if not self.should_exist_on_map(map_id) or self.defeated:
            self.active = False
            return

        if player.rect.colliderect(self.arena_rect.inflate(400, 300)):
            if not self.active:
                print("PaleCoreBoss activated")
            self.active = True

    def update(self, dt, player):
        if not self.active or self.defeated:
            return

        if self.current_hp <= self.max_hp * 0.5:
            if self.phase != 2:
                self.phase = 2
                self.prepare_phase2_hands()
            else:
                self.phase = 2

        self.float_timer += dt
        self.float_offset_y = math.sin(self.float_timer * 1.4) * 4
        self.update_core_anchor()
        self.update_hands(dt)

        self.frame_timer += dt
        if self.frame_timer >= 0.12:
            self.frame_timer = 0
            self.frame_index += 1
        self.update_core_animation(dt)

        self.weakpoint_hit_cooldown = max(0, self.weakpoint_hit_cooldown - dt)
        self.hit_effect_timer = max(0, self.hit_effect_timer - dt)
        self.player_hit_cooldown = max(0, self.player_hit_cooldown - dt)
        self.state_timer -= dt

        self.update_moon_orbs(dt, player)
        self.update_shards(dt, player)
        self.update_hand_slams(dt, player)
        self.update_core_beam(dt, player)
        self.update_boss_hit_effects(dt)

        if self.state_timer > 0:
            return

        if self.state == "idle":
            self.start_next_attack(player)
        elif self.state == "weakpoint_open":
            self.close_weakpoint()
        else:
            self.finish_attack()

    def start_next_attack(self, player):
        self.clear_attack_effects()
        if self.attacks_since_weakpoint >= 3:
            self.attacks_since_weakpoint = 0
            self.open_weakpoint()
            return

        chosen_skills = self.choose_attack_skills()
        self.active_attack_skills = chosen_skills
        self.state = "attack_cycle"
        self.frame_index = 0
        self.attack_count += 1
        self.attacks_since_weakpoint += 1
        self.current_attack_duration = 2.0 if self.phase == 1 else 1.8
        if "core_beam" in chosen_skills:
            self.current_attack_duration = max(
                self.current_attack_duration,
                BOSS_BEAM_READY_DURATION + BOSS_BEAM_FIRE_DURATION + 0.2,
            )
        self.state_timer = self.current_attack_duration
        print("PaleCoreBoss attack skills:", chosen_skills, "phase:", self.phase)

        for skill_name in chosen_skills:
            if skill_name == "moon_orb":
                self.spawn_moon_orbs(player)
            elif skill_name == "lunar_shard":
                self.spawn_shards(player)
            elif skill_name == "hand_slam":
                self.spawn_hand_slam(player)
            elif skill_name == "core_beam":
                self.start_core_beam(player)

    def clear_attack_effects(self):
        self.active_attack_skills = []
        self.moon_orbs.clear()
        self.shards.clear()
        self.core_beam_rect = None
        self.core_beam_draw_rect = None
        self.core_beam_active = False
        self.core_beam_ready_timer = 0
        self.core_beam_fire_timer = 0

    def choose_attack_skills(self):
        if self.phase == 1:
            phase1_skills = ["moon_orb", "lunar_shard"]
            chosen_skills = [random.choice(phase1_skills)]
        else:
            phase2_skills = ["core_beam", "moon_orb", "lunar_shard"]
            if self.get_available_slam_hands():
                phase2_skills.append("hand_slam")
            skill_count = random.choice([1, 2])
            chosen_skills = random.sample(phase2_skills, min(skill_count, len(phase2_skills)))

        signature = tuple(sorted(chosen_skills))
        if signature == self.last_skill_signature:
            self.same_skill_repeat_count += 1
        else:
            self.same_skill_repeat_count = 1

        if self.same_skill_repeat_count > 2:
            chosen_skills = self.reroll_attack_skills(chosen_skills)
            signature = tuple(sorted(chosen_skills))
            self.same_skill_repeat_count = 1

        self.last_skill_signature = signature
        return chosen_skills

    def reroll_attack_skills(self, previous_skills):
        previous_signature = tuple(sorted(previous_skills))
        for _ in range(8):
            if self.phase == 1:
                phase1_skills = ["moon_orb", "lunar_shard"]
                chosen_skills = [random.choice(phase1_skills)]
            else:
                phase2_skills = ["core_beam", "moon_orb", "lunar_shard"]
                if self.get_available_slam_hands():
                    phase2_skills.append("hand_slam")
                skill_count = random.choice([1, 2])
                chosen_skills = random.sample(phase2_skills, min(skill_count, len(phase2_skills)))
            if tuple(sorted(chosen_skills)) != previous_signature:
                return chosen_skills
        return previous_skills

    def start_core_beam(self, player):
        target_x = max(BOSS_ROOM_MIN_X + 80, min(player.rect.centerx, BOSS_ROOM_MAX_X - 80))
        impact_y = self.find_first_solid_surface_top_below(target_x, player)
        origin_y = max(90, self.boss_head_rect.bottom - 20)
        self.core_beam_origin = (
            target_x + BOSS_BEAM_START_OFFSET_X,
            origin_y,
        )
        beam_top = self.core_beam_origin[1]
        beam_height = max(120, impact_y - beam_top)
        self.core_beam_rect = pygame.Rect(
            self.core_beam_origin[0] - BOSS_BEAM_WIDTH // 2,
            beam_top,
            BOSS_BEAM_WIDTH,
            beam_height,
        )
        self.core_beam_draw_rect = self.core_beam_rect.copy()
        self.core_beam_ready_timer = BOSS_BEAM_READY_DURATION
        self.core_beam_fire_timer = BOSS_BEAM_FIRE_DURATION
        self.core_beam_active = False

    def finish_attack(self):
        self.state = "idle"
        self.active_attack_skills = []
        self.core_beam_rect = None
        self.core_beam_draw_rect = None
        self.core_beam_active = False
        self.core_beam_ready_timer = 0
        self.core_beam_fire_timer = 0
        self.core_beam_ready_timer = 0
        self.core_beam_fire_timer = 0
        self.current_attack_duration = 0
        self.state_timer = 0.5 if self.phase == 2 else 1.0

    def open_weakpoint(self):
        self.state = "weakpoint_open"
        self.weakpoint_open = True
        self.frame_index = 0
        self.state_timer = 3.2
        print("PaleCoreBoss weakpoint open")
        print("[CORE VULNERABLE]", self.core_vulnerable)

    def close_weakpoint(self):
        self.state = "idle"
        self.weakpoint_open = False
        self.state_timer = 0.8
        print("PaleCoreBoss weakpoint closed")
        print("[CORE VULNERABLE]", self.core_vulnerable)

    def spawn_moon_orbs(self, player):
        count = 5 if self.phase == 2 else 3
        for index in range(count):
            spread = 130
            start_x = self.core_center[0] - spread * (count - 1) // 2
            start = (start_x + index * spread, self.core_center[1] - 110)
            dx = player.rect.centerx - start[0]
            dy = player.rect.centery - start[1]
            distance = max(1, math.hypot(dx, dy))
            speed = 260 if self.phase == 2 else 210
            velocity = (dx / distance * speed, dy / distance * speed)
            self.moon_orbs.append({
                "rect": pygame.Rect(start[0], start[1], 34, 34),
                "vel": velocity,
                "timer": 4.0,
                "damage": 13 if self.phase == 2 else 10,
                "hit": False,
            })

    def spawn_shards(self, player):
        count = 8 if self.phase == 2 else 4
        spacing = 150 if self.phase == 2 else 170
        start_x = player.rect.centerx - spacing * (count - 1) / 2
        for index in range(count):
            x = round(start_x + index * spacing)
            self.shards.append({
                "warning": pygame.Rect(x - 24, 625, 48, 24),
                "rect": pygame.Rect(x - 18, -140, 36, 120),
                "timer": 2.8,
                "warning_timer": 0.65,
                "damage": 16,
                "hit": False,
            })

    def spawn_hand_slam(self, player):
        hand = random.choice(self.get_available_slam_hands()) if self.get_available_slam_hands() else None
        if hand is None:
            return

        target_x = max(BOSS_ROOM_MIN_X + 80, min(player.rect.centerx, BOSS_ROOM_MAX_X - 80))
        target_y = self.find_first_solid_surface_top_below(target_x, player)
        slam_spawn_y = target_y + HAND_SLAM_START_OFFSET_Y

        image = self.get_hand_slam_image(hand)
        hand.slam_rect = image.get_rect(midtop=(target_x, slam_spawn_y)) if image is not None else pygame.Rect(target_x - 160, slam_spawn_y, 320, 260)
        hand.slam_target_x = target_x
        hand.slam_target_y = target_y
        hand.slam_warning_pos = (target_x, target_y)
        hand.slam_timer = HAND_SLAM_WARNING_TIME
        hand.slam_warning_elapsed = 0
        hand.slam_phase = "warning"
        hand.slam_warning_active = True
        hand.is_slamming = True
        hand.visible = False
        hand.slam_hit = False
        hand.slam_landed = False
        hand.slam_cooldown_timer = HAND_SLAM_COOLDOWN
        print("[HAND SLAM START]", hand.name, target_x, target_y)

    def find_first_solid_surface_top_below(self, target_x, player):
        floor_y = max(player.rect.bottom, HAND_SLAM_TARGET_FLOOR_Y)
        return min(BOSS_ROOM_MAX_Y, floor_y)

    def update_moon_orbs(self, dt, player):
        for orb in self.moon_orbs:
            orb["timer"] -= dt
            orb["rect"].x += int(orb["vel"][0] * dt)
            orb["rect"].y += int(orb["vel"][1] * dt)
            if not orb["hit"] and orb["rect"].colliderect(player.rect):
                self.damage_player(player, orb["damage"])
                orb["hit"] = True
                orb["timer"] = 0
        self.moon_orbs = [orb for orb in self.moon_orbs if orb["timer"] > 0]

    def update_shards(self, dt, player):
        for shard in self.shards:
            shard["timer"] -= dt
            shard["warning_timer"] -= dt
            if shard["warning_timer"] <= 0:
                shard["rect"].y += int((460 if self.phase == 2 else 380) * dt)
                if not shard["hit"] and shard["rect"].colliderect(player.rect):
                    self.damage_player(player, shard["damage"])
                    shard["hit"] = True
        self.shards = [shard for shard in self.shards if shard["timer"] > 0 and shard["rect"].top < SCREEN_HEIGHT + 220]

    def update_hand_slams(self, dt, player):
        for hand in self.get_hands():
            if hand is None or not hand.is_slamming:
                continue

            hand.slam_timer -= dt
            if hand.slam_phase == "warning":
                hand.slam_warning_elapsed += dt
                if hand.slam_timer <= 0:
                    hand.slam_phase = "falling"
                    hand.slam_warning_active = False
                    hand.slam_timer = HAND_SLAM_FALL_TIME
                continue

            if hand.slam_phase == "falling":
                progress = 1 - max(0, hand.slam_timer) / HAND_SLAM_FALL_TIME
                start_y = hand.slam_target_y + HAND_SLAM_START_OFFSET_Y
                target_bottom = hand.slam_target_y + 36
                hand.slam_rect.midtop = (
                    hand.slam_target_x,
                    round(start_y + (target_bottom - hand.slam_rect.height - start_y) * progress),
                )
                if not hand.slam_hit and hand.slam_rect.colliderect(player.rect):
                    self.damage_player(player, HAND_SLAM_DAMAGE)
                    hand.slam_hit = True
                if hand.slam_timer <= 0:
                    hand.slam_rect.bottom = target_bottom
                    hand.slam_phase = "recover"
                    hand.slam_timer = HAND_SLAM_RECOVER_TIME
                    hand.slam_landed = True
                continue

            if hand.slam_phase == "recover" and hand.slam_timer <= 0:
                print("[HAND SLAM END]", hand.name)
                hand.cancel_slam()
                if hand.is_alive:
                    hand.visible = True
                    hand.rect.center = hand.anchor_position
                    print("[HAND RETURN]", hand.name)

    def update_core_beam(self, dt, player):
        if "core_beam" not in self.active_attack_skills or self.core_beam_rect is None:
            return

        if self.core_beam_ready_timer > 0:
            self.core_beam_ready_timer = max(0, self.core_beam_ready_timer - dt)
            self.core_beam_active = False
            return

        self.core_beam_fire_timer = max(0, self.core_beam_fire_timer - dt)
        self.core_beam_active = self.core_beam_fire_timer > 0
        if self.core_beam_active and self.core_beam_rect.colliderect(player.rect):
            self.damage_player(player, 18)

    def get_hands(self):
        return [self.left_hand, self.right_hand]

    def get_available_slam_hands(self):
        if self.phase != 2:
            return []
        return [
            hand for hand in self.get_hands()
            if hand is not None
            and hand.is_alive
            and hand.can_slam
            and not hand.is_slamming
            and hand.slam_cooldown_timer <= 0
        ]

    def update_hands(self, dt):
        for hand in self.get_hands():
            if hand is None:
                continue
            hand.slam_cooldown_timer = max(0, hand.slam_cooldown_timer - dt)

    def prepare_phase2_hands(self):
        if self.phase2_hands_ready:
            return
        self.phase2_hands_ready = True
        self.reset_hands()
        print("[CORE INVULNERABLE]", self.core_invulnerable)

    @property
    def core_invulnerable(self):
        return self.phase == 2 and any(hand is not None and hand.is_alive for hand in self.get_hands())

    @property
    def core_vulnerable(self):
        return self.weakpoint_open and not self.core_invulnerable

    def take_hand_damage_at_rect(self, hit_rect, amount):
        if not self.active or self.defeated or self.phase != 2:
            return None

        for hand in self.get_hands():
            if hand is None or not hand.is_alive:
                continue
            target_rect = hand.slam_rect if hand.is_slamming else hand.rect
            if not hit_rect.colliderect(target_rect):
                continue
            self.damage_hand(hand, amount)
            return hand
        return None

    def damage_hand(self, hand, amount):
        hand.current_hp = max(0, hand.current_hp - amount)
        self.spawn_boss_hit_effect(hand.rect.center)
        print("[BOSS HAND HIT]", hand.name, hand.current_hp)
        if hand.current_hp > 0:
            return

        hand.is_alive = False
        hand.visible = False
        hand.can_slam = False
        hand.cancel_slam()
        print("[BOSS HAND DESTROYED]", hand.name)
        print("[CORE INVULNERABLE]", self.core_invulnerable)

    def update_core_anchor(self):
        self.core_center = (
            self.base_core_center[0],
            round(self.base_core_center[1] + self.float_offset_y),
        )
        self.weakpoint_rect.center = self.core_center
        self.boss_core_rect.center = self.core_center
        if self.boss_head_rect.width > 1:
            self.boss_head_rect.midbottom = (self.boss_core_rect.centerx, self.boss_core_rect.top + BOSS_HEAD_MIDBOTTOM_OFFSET_Y)
        self.body_rect = self.boss_head_rect.copy()
        self.left_hand_anchor = self.get_hand_anchor("left")
        self.right_hand_anchor = self.get_hand_anchor("right")
        if self.left_hand is not None:
            self.left_hand.anchor_position = self.left_hand_anchor
            if self.left_hand.visible and not self.left_hand.is_slamming:
                self.left_hand.rect.center = self.left_hand_anchor
        if self.right_hand is not None:
            self.right_hand.anchor_position = self.right_hand_anchor
            if self.right_hand.visible and not self.right_hand.is_slamming:
                self.right_hand.rect.center = self.right_hand_anchor

    def get_hand_anchor(self, side):
        boss_head_rect = getattr(self, "boss_head_rect", None)
        body_center = boss_head_rect.center if boss_head_rect is not None and boss_head_rect.width > 1 else self.base_core_center
        offset = BOSS_LEFT_HAND_OFFSET if side == "left" else BOSS_RIGHT_HAND_OFFSET
        return (body_center[0] + offset[0], body_center[1] + offset[1])

    def get_floating_pos(self, pos):
        return (pos[0], round(pos[1] + self.float_offset_y))

    def damage_player(self, player, amount):
        if self.player_hit_cooldown > 0:
            return
        player.take_damage(amount)
        self.player_hit_cooldown = 0.45

    def take_damage(self, amount):
        if self.defeated or self.weakpoint_hit_cooldown > 0:
            return False
        if not self.core_vulnerable:
            print("[CORE INVULNERABLE]")
            return False
        if self.last_core_invulnerable_print != False:
            print("[CORE INVULNERABLE]", False)
            self.last_core_invulnerable_print = False

        self.current_hp = max(0, self.current_hp - amount)
        self.weakpoint_hit_cooldown = 0.2
        self.hit_effect_timer = 0.42
        self.spawn_boss_hit_effect(self.core_center)
        print(f"PaleCoreBoss weakpoint hit for {amount}. HP: {self.current_hp}/{self.max_hp}")

        if self.current_hp <= 0:
            self.current_hp = 0
            self.defeated = True
            self.active = False
            self.state = "defeated"
            self.weakpoint_open = False
            print("PaleCoreBoss defeated")
        return True

    def get_current_effect_frame(self, animation_name):
        frames = self.animations.get(animation_name, [])
        if not frames:
            return None
        return frames[self.frame_index % len(frames)]

    def spawn_boss_hit_effect(self, center):
        if not self.boss_hit_effect_frames:
            return
        self.boss_hit_effects.append({
            "center": center,
            "timer": len(self.boss_hit_effect_frames) * 0.08,
            "elapsed": 0,
        })

    def update_boss_hit_effects(self, dt):
        for effect in self.boss_hit_effects:
            effect["timer"] -= dt
            effect["elapsed"] += dt
        self.boss_hit_effects = [effect for effect in self.boss_hit_effects if effect["timer"] > 0]

    def update_core_animation(self, dt):
        if not self.boss_core_frames:
            return

        self.core_frame_timer += dt
        while self.core_frame_timer >= BOSS_CORE_FRAME_DURATION:
            self.core_frame_timer -= BOSS_CORE_FRAME_DURATION
            self.current_core_frame = (self.current_core_frame + 1) % len(self.boss_core_frames)
            if self.current_core_frame != self.last_debug_core_frame:
                print("[CORE FRAME INDEX]", self.current_core_frame)
                self.last_debug_core_frame = self.current_core_frame

    def draw_background(self, screen, camera=None):
        self.draw_boss_room_background(screen, camera)

    def draw_boss_foreground(self, screen, camera=None):
        if self.boss_image is not None:
            draw_pos = self.boss_head_rect.topleft
            if camera:
                draw_pos = camera.apply_pos(draw_pos)
            screen.blit(self.boss_image, draw_pos)
        self.draw_side_hands(screen, camera)
        self.draw_boss_core(screen, camera)

    def draw_boss_room_background(self, screen, camera=None):
        if self.boss_room_background is None:
            return

        draw_rect = self.apply_rect(self.boss_room_background_rect, camera)
        screen.blit(self.boss_room_background, draw_rect)

    def draw_side_hands(self, screen, camera=None):
        self.draw_hand_part(screen, camera, self.left_hand, self.boss_hand_left)
        self.draw_hand_part(screen, camera, self.right_hand, self.boss_hand_right)

    def draw_hand_part(self, screen, camera, hand, image):
        if hand is None or not hand.is_alive or not hand.visible or hand.is_slamming:
            return

        draw_rect = self.apply_rect(hand.rect, camera)
        if image is not None:
            screen.blit(image, draw_rect)
        if self.phase == 2:
            self.draw_hand_hp_bar(screen, draw_rect, hand)

    def draw_hand_hp_bar(self, screen, draw_rect, hand):
        bar = pygame.Rect(0, 0, 92, 9)
        bar.midbottom = (draw_rect.centerx, draw_rect.top - 8)
        ratio = hand.current_hp / hand.max_hp
        pygame.draw.rect(screen, (24, 18, 30), bar)
        fill = bar.inflate(-2, -2)
        fill.width = round(fill.width * ratio)
        pygame.draw.rect(screen, (115, 225, 245), fill)
        pygame.draw.rect(screen, (225, 245, 255), bar, 1)

    def draw_core_idle_glow(self, screen, camera=None):
        pulse = (math.sin(self.float_timer * 3.5) + 1) * 0.5
        center = camera.apply_pos(self.core_center) if camera else self.core_center
        glow_radius = round(32 + pulse * 8)
        inner_radius = round(13 + pulse * 4)

        glow_surface = pygame.Surface((glow_radius * 2 + 8, glow_radius * 2 + 8), pygame.SRCALPHA)
        local_center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)
        pygame.draw.circle(glow_surface, (70, 220, 255, 45), local_center, glow_radius)
        pygame.draw.circle(glow_surface, (100, 245, 255, 90), local_center, round(glow_radius * 0.62))
        pygame.draw.circle(glow_surface, (230, 255, 255, 210), local_center, inner_radius)
        screen.blit(glow_surface, glow_surface.get_rect(center=center))

    def draw_hand_auras(self, screen, camera=None):
        pulse = (math.sin(self.float_timer * 4.0) + 1) * 0.5
        radius = round(21 + pulse * 5)
        for anchor in (self.left_hand_anchor, self.right_hand_anchor):
            center = self.get_floating_pos(anchor)
            center = camera.apply_pos(center) if camera else center
            aura = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
            local_center = (aura.get_width() // 2, aura.get_height() // 2)
            pygame.draw.circle(aura, (80, 230, 255, 38), local_center, radius)
            pygame.draw.circle(aura, (180, 255, 255, 90), local_center, max(4, radius // 3), 2)
            screen.blit(aura, aura.get_rect(center=center))

    def draw_effects(self, screen, camera=None):
        if not self.active and not self.defeated:
            return

        self.draw_boss_foreground(screen, camera)
        for orb in self.moon_orbs:
            draw_pos = orb["rect"].center
            self.blit_boss_effect_frame(screen, "moon_orb_fly", draw_pos, camera, anchor="center")

        for shard in self.shards:
            if shard["warning_timer"] > 0:
                self.blit_boss_effect_frame(
                    screen,
                    "lunar_shard_warning",
                    shard["warning"].midbottom,
                    camera,
                    anchor="midbottom",
                )
            else:
                self.blit_boss_effect_frame(
                    screen,
                    "lunar_shard_fall",
                    shard["rect"].midbottom,
                    camera,
                    anchor="midbottom",
                )

        self.draw_hand_slams(screen, camera)

        self.draw_beam_attack(screen, camera)
        self.draw_boss_hit_effects(screen, camera)

    def draw_weakpoint(self, screen, camera=None):
        if self.defeated:
            return

        return

    def draw_vulnerable_core_effect(self, screen, camera=None):
        if not self.core_vulnerable or self.defeated:
            return

        pulse = (math.sin(self.float_timer * BOSS_VULNERABLE_GLOW_SPEED) + 1) * 0.5
        center = camera.apply_pos(self.core_center) if camera else self.core_center
        radius = round(BOSS_VULNERABLE_GLOW_RADIUS + pulse * 18)
        glow = pygame.Surface((radius * 2 + 40, radius * 2 + 40), pygame.SRCALPHA)
        local_center = (glow.get_width() // 2, glow.get_height() // 2)

        pygame.draw.circle(glow, (45, 180, 255, 58), local_center, radius)
        pygame.draw.circle(glow, (90, 235, 255, 105), local_center, round(radius * 0.68), 5)
        pygame.draw.circle(glow, (225, 255, 255, 170), local_center, round(radius * 0.42), 2)

        for index in range(BOSS_VULNERABLE_SPARK_COUNT):
            angle = self.float_timer * 1.7 + index * (math.tau / BOSS_VULNERABLE_SPARK_COUNT)
            spark_radius = radius * (0.56 + 0.2 * math.sin(self.float_timer * 2.2 + index))
            spark_x = local_center[0] + math.cos(angle) * spark_radius
            spark_y = local_center[1] + math.sin(angle) * spark_radius * 0.72
            spark_size = 2 + (index % 3)
            pygame.draw.circle(glow, (210, 255, 255, 190), (round(spark_x), round(spark_y)), spark_size)

        screen.blit(glow, glow.get_rect(center=center))
        self.draw_weakpoint(screen, camera)

    def draw_boss_core(self, screen, camera=None):
        self.draw_core_idle_glow(screen, camera)
        self.draw_vulnerable_core_effect(screen, camera)
        if self.boss_core_frames:
            frame = self.boss_core_frames[self.current_core_frame % len(self.boss_core_frames)]
        else:
            frame = self.boss_core_image
        if frame is None:
            return

        draw_rect = frame.get_rect(center=self.core_center)
        if camera:
            draw_rect = camera.apply_rect(draw_rect)
        screen.blit(frame, draw_rect)

    def draw_boss_hit_effects(self, screen, camera=None):
        if not self.boss_hit_effect_frames:
            return

        frame_duration = 0.08
        for effect in self.boss_hit_effects:
            frame_index = min(
                len(self.boss_hit_effect_frames) - 1,
                int(effect["elapsed"] / frame_duration),
            )
            frame = self.boss_hit_effect_frames[frame_index]
            draw_pos = camera.apply_pos(effect["center"]) if camera else effect["center"]
            screen.blit(frame, frame.get_rect(center=draw_pos))

    def draw_hand_slams(self, screen, camera=None):
        for hand in self.get_hands():
            if hand is None or not hand.is_slamming:
                continue

            if hand.slam_phase == "warning":
                warning_frame = self.get_looped_frame(
                    self.boss_slam_warning_frames,
                    hand.slam_warning_elapsed,
                    HAND_SLAM_WARNING_ANIM_SPEED,
                )
                self.draw_anchored_frame(
                    screen,
                    warning_frame,
                    hand.slam_warning_pos,
                    camera,
                    anchor="center",
                )
                continue

            image = self.get_hand_slam_image(hand)
            draw_rect = self.apply_rect(hand.slam_rect, camera)
            if image is not None:
                screen.blit(image, draw_rect)

            if hand.slam_landed:
                impact_rect = pygame.Rect(0, 0, 360, 36)
                impact_rect.midbottom = (hand.slam_target_x, hand.slam_target_y + 18)
                pygame.draw.ellipse(screen, (135, 210, 255, 85), self.apply_rect(impact_rect, camera), 3)

    def get_hand_slam_image(self, hand):
        frames = self.boss_slam_hand_frames
        if frames:
            index = min(len(frames) - 1, max(0, self.frame_index % len(frames)))
            image = frames[index]
        elif hand.name == "left":
            image = self.boss_attack_hand_left
        else:
            image = self.boss_attack_hand_right

        if hand.name == "left" and image is not None:
            return pygame.transform.flip(image, True, False)
        return image

    def draw_beam_attack(self, screen, camera=None):
        if self.core_beam_rect is None:
            return

        if self.core_beam_ready_timer > 0:
            elapsed = BOSS_BEAM_READY_DURATION - self.core_beam_ready_timer
            frame = self.get_timed_frame(self.boss_beam_ready_frames, elapsed, BOSS_BEAM_READY_DURATION)
            self.draw_anchored_frame(screen, frame, self.core_beam_origin, camera, anchor=BOSS_BEAM_SOURCE_ANCHOR)
            return

        if self.core_beam_fire_timer <= 0:
            return

        fire_elapsed = BOSS_BEAM_FIRE_DURATION - self.core_beam_fire_timer
        attack_frame = self.get_timed_frame(self.boss_beam_attack_frames, fire_elapsed, BOSS_BEAM_FIRE_DURATION)
        self.draw_boss_beam_column(screen, self.core_beam_draw_rect, camera)
        self.draw_anchored_frame(screen, attack_frame, self.core_beam_origin, camera, anchor=BOSS_BEAM_SOURCE_ANCHOR)

    def get_timed_frame(self, frames, elapsed, duration):
        if not frames:
            return None
        index = min(len(frames) - 1, int((elapsed / max(0.001, duration)) * len(frames)))
        return frames[index]

    def get_looped_frame(self, frames, elapsed, frame_duration):
        if not frames:
            return None
        index = int(elapsed / max(0.001, frame_duration)) % len(frames)
        return frames[index]

    def draw_anchored_frame(self, screen, frame, world_pos, camera=None, anchor="center"):
        if frame is None:
            return None
        screen_pos = camera.apply_pos(world_pos) if camera else world_pos
        rect = frame.get_rect(**{anchor: screen_pos})
        screen.blit(frame, rect)
        return rect

    def blit_surface_at(self, screen, image, target_pos, camera=None, anchor="center"):
        if image is None:
            return False
        draw_pos = camera.apply_pos(target_pos) if camera else target_pos
        draw_rect = image.get_rect()
        if anchor == "midbottom":
            draw_rect.midbottom = draw_pos
        elif anchor == "midtop":
            draw_rect.midtop = draw_pos
        else:
            draw_rect.center = draw_pos
        screen.blit(image, draw_rect)
        return True

    def draw_boss_beam_column(self, screen, beam_rect, camera=None):
        draw_rect = self.apply_rect(beam_rect, camera)
        if draw_rect.height <= 0:
            return

        glow_rect = pygame.Rect(0, 0, BOSS_BEAM_GLOW_WIDTH, draw_rect.height)
        glow_rect.centerx = draw_rect.centerx
        glow_rect.top = draw_rect.top
        beam_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        center_x = glow_rect.width // 2

        pygame.draw.rect(
            beam_surface,
            BOSS_BEAM_COLOR_OUTER,
            pygame.Rect(center_x - BOSS_BEAM_GLOW_WIDTH // 2, 0, BOSS_BEAM_GLOW_WIDTH, glow_rect.height),
            border_radius=18,
        )
        pygame.draw.rect(
            beam_surface,
            BOSS_BEAM_COLOR_MID,
            pygame.Rect(center_x - BOSS_BEAM_WIDTH // 2, 0, BOSS_BEAM_WIDTH, glow_rect.height),
            border_radius=12,
        )
        inner_width = max(12, BOSS_BEAM_WIDTH // 3)
        pygame.draw.rect(
            beam_surface,
            BOSS_BEAM_COLOR_INNER,
            pygame.Rect(center_x - inner_width // 2, 0, inner_width, glow_rect.height),
            border_radius=8,
        )
        for y in range(0, glow_rect.height, 42):
            alpha = 90 if (y // 42) % 2 == 0 else 45
            pygame.draw.line(
                beam_surface,
                (245, 255, 255, alpha),
                (center_x - BOSS_BEAM_WIDTH // 2, y),
                (center_x + BOSS_BEAM_WIDTH // 2, min(glow_rect.height, y + 18)),
                3,
            )
        screen.blit(beam_surface, glow_rect)

    def draw_ui(self, screen):
        if not self.active and not self.defeated:
            return

        panel = pygame.Rect(220, 24, SCREEN_WIDTH - 440, 30)
        hp_ratio = self.current_hp / self.max_hp
        pygame.draw.rect(screen, (28, 22, 38), panel)
        pygame.draw.rect(screen, (155, 210, 255), panel, 2)
        fill = panel.inflate(-6, -6)
        fill.width = int(fill.width * hp_ratio)
        pygame.draw.rect(screen, (105, 225, 245), fill)

        font = pygame.font.Font(None, 26)
        label = font.render(f"PALE CORE - Phase {self.phase}", True, (235, 245, 255))
        screen.blit(label, label.get_rect(center=panel.center))

    def apply_rect(self, rect, camera):
        if camera:
            return camera.apply_rect(rect)
        return rect

    def blit_boss_effect_frame(self, screen, animation_name, target_pos, camera=None, flip_x=False, anchor="center"):
        frame = self.get_current_effect_frame(animation_name)
        if frame is None:
            return False
        image = pygame.transform.flip(frame, True, False) if flip_x else frame
        draw_pos = camera.apply_pos(target_pos) if camera else target_pos
        draw_rect = image.get_rect()
        if anchor == "midbottom":
            draw_rect.midbottom = draw_pos
        elif anchor == "midleft":
            draw_rect.midleft = draw_pos
        elif anchor == "midright":
            draw_rect.midright = draw_pos
        else:
            draw_rect.center = draw_pos
        screen.blit(image, draw_rect)
        return True

    def blit_boss_hand(self, screen, target_pos, side, camera=None):
        if side == "left":
            image = self.boss_attack_hand_left
        else:
            image = self.boss_attack_hand_right
        if image is None:
            return False

        draw_pos = camera.apply_pos(target_pos) if camera else target_pos
        draw_rect = image.get_rect(midbottom=draw_pos)
        screen.blit(image, draw_rect)
        return True

    def blit_boss_effect_to_rect(self, screen, animation_name, target_rect, camera=None):
        frame = self.get_current_effect_frame(animation_name)
        if frame is None:
            return False

        draw_rect = self.apply_rect(target_rect, camera)
        image = pygame.transform.smoothscale(frame, draw_rect.size)
        screen.blit(image, draw_rect)
        return True
