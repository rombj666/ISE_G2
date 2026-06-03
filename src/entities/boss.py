import math
import random
from pathlib import Path

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PALE_CORE_ASSET_DIR = PROJECT_ROOT / "assets" / "bosses" / "pale_core"
PALE_CORE_FALLBACK_ASSET_DIR = PROJECT_ROOT / "assets" / "enemies" / "boss"
DEBUG_OUTPUT_DIR = PROJECT_ROOT / "assets" / "processed" / "debug"
BOSS_PROJECTILE_TARGET_SIZE = (180, 120)
BOSS_GROUND_TARGET_SIZE = (320, 220)
BOSS_BEAM_TARGET_SIZE = (520, 180)

MANUAL_BOSS_PROJECTILE_RECTS = None
MANUAL_BOSS_GROUND_RECTS = None
MANUAL_BOSS_BEAM_RECTS = None

BOSS_EFFECT_CONFIG = {
    "moon_orb_spawn": {
        "category": "projectile",
        "crop_mode": "center_effect",
        "target_size": BOSS_PROJECTILE_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_PROJECTILE_RECTS,
        "debug_name": "boss_projectile_spawn",
    },
    "moon_orb_fly": {
        "category": "projectile",
        "crop_mode": "center_effect",
        "target_size": BOSS_PROJECTILE_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_PROJECTILE_RECTS,
        "debug_name": "boss_projectile",
    },
    "lunar_shard_warning": {
        "category": "ground",
        "crop_mode": "ground_effect",
        "target_size": BOSS_GROUND_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_GROUND_RECTS,
        "debug_name": "boss_ground",
    },
    "lunar_shard_fall": {
        "category": "ground",
        "crop_mode": "ground_effect",
        "target_size": BOSS_GROUND_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_GROUND_RECTS,
        "debug_name": "boss_ground_fall",
    },
    "hand_slam_warning": {
        "category": "ground",
        "crop_mode": "ground_effect",
        "target_size": BOSS_GROUND_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_GROUND_RECTS,
        "debug_name": "boss_ground_slam_warning",
    },
    "hand_slam_down": {
        "category": "ground",
        "crop_mode": "ground_effect",
        "target_size": BOSS_GROUND_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_GROUND_RECTS,
        "debug_name": "boss_ground_slam_down",
    },
    "core_charge_down": {
        "category": "beam",
        "crop_mode": "beam",
        "target_size": BOSS_BEAM_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_BEAM_RECTS,
        "debug_name": "boss_beam_charge",
    },
    "core_beam_down": {
        "category": "beam",
        "crop_mode": "beam",
        "target_size": BOSS_BEAM_TARGET_SIZE,
        "manual_rects": MANUAL_BOSS_BEAM_RECTS,
        "debug_name": "boss_beam",
    },
    "core_open": {
        "category": "ground",
        "crop_mode": "center_effect",
        "target_size": (220, 180),
        "manual_rects": None,
        "debug_name": "boss_core_open",
    },
    "boss_hit_effect": {
        "category": "hit",
        "crop_mode": "center_effect",
        "target_size": (220, 180),
        "manual_rects": None,
        "debug_name": "boss_hit_effect",
    },
}


class PaleCoreBoss:
    """Map 8 background boss with a separate weakpoint damage target."""

    FRAME_COUNTS = {
        "core_charge_down": 4,
        "core_beam_down": 6,
        "moon_orb_spawn": 4,
        "moon_orb_fly": 4,
        "lunar_shard_warning": 4,
        "lunar_shard_fall": 4,
        "hand_slam_warning": 6,
        "hand_slam_down": 6,
        "core_open": 6,
        "boss_hit_effect": 6,
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
        self.float_timer = 0
        self.float_offset_y = 0
        self.has_printed_missing_asset_warning = False
        self.asset_dir = self.resolve_asset_dir()

        self.arena_rect = pygame.Rect(9000, 60, 2000, 790)
        self.body_rect = pygame.Rect(9280, 30, 1150, 690)
        self.base_core_center = (9835, 330)
        self.core_center = self.base_core_center
        self.weakpoint_rect = pygame.Rect(0, 0, 150, 130)
        self.weakpoint_rect.center = self.core_center
        self.left_hand_anchor = (9445, 460)
        self.right_hand_anchor = (10325, 460)
        self.weakpoint_open = False
        self.weakpoint_hit_cooldown = 0
        self.hit_effect_timer = 0

        self.boss_image = None
        self.animations = {}
        self.moon_orbs = []
        self.shards = []
        self.hand_slams = []
        self.core_beam_rect = None
        self.core_beam_draw_rect = None
        self.core_beam_facing = 1
        self.core_beam_active = False
        self.player_hit_cooldown = 0
        self.load_assets()
        self.print_startup_debug()

    def resolve_asset_dir(self):
        if PALE_CORE_ASSET_DIR.exists():
            return PALE_CORE_ASSET_DIR
        if PALE_CORE_FALLBACK_ASSET_DIR.exists():
            print("PaleCoreBoss requested asset folder missing:", PALE_CORE_ASSET_DIR)
            print("PaleCoreBoss using existing asset folder:", PALE_CORE_FALLBACK_ASSET_DIR)
            return PALE_CORE_FALLBACK_ASSET_DIR
        return PALE_CORE_ASSET_DIR

    def load_assets(self):
        boss_path = self.asset_dir / "boss.png"
        self.boss_image = self.load_image(boss_path)
        if self.boss_image is not None:
            self.boss_image = pygame.transform.smoothscale(self.boss_image, self.body_rect.size)

        for name, frame_count in self.FRAME_COUNTS.items():
            config = BOSS_EFFECT_CONFIG.get(name, {})
            self.animations[name] = self.load_boss_effect_sheet(
                self.asset_dir / f"{name}.png",
                frame_count,
                config.get("target_size", BOSS_GROUND_TARGET_SIZE),
                config.get("crop_mode", "center_effect"),
                config.get("manual_rects"),
                config.get("debug_name", name),
            )

    def load_image(self, path):
        if not path.exists():
            print("PaleCoreBoss missing asset:", path)
            return None
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as exc:
            print("PaleCoreBoss failed to load asset:", path, exc)
            return None

    def load_boss_effect_sheet(
        self,
        path,
        frame_count,
        target_size,
        crop_mode,
        manual_rects=None,
        debug_name=None,
    ):
        print("Boss effect file path:", path)
        print("Boss effect frame count:", frame_count)
        print("Boss effect crop mode:", crop_mode)
        print("Boss effect target output size:", target_size)
        sheet = self.load_image(path)
        if sheet is None:
            return []

        source_rects = manual_rects or self.make_equal_source_rects(sheet, frame_count)
        frames = []
        for source_rect in source_rects:
            raw_frame = pygame.Surface(source_rect.size, pygame.SRCALPHA)
            raw_frame.blit(sheet, (0, 0), source_rect)
            raw_frame = self.repair_opaque_white_background(raw_frame)
            cropped = self.crop_visible_pixels(raw_frame)
            frames.append(self.place_on_canvas(cropped, target_size, crop_mode))

        print("Loaded boss effect sheet:", path)
        print("Sheet size:", sheet.get_size())
        print("Frame count:", len(frames))
        print("Frame size:", frames[0].get_size() if frames else None)
        if debug_name:
            self.draw_source_rect_debug(sheet, source_rects, DEBUG_OUTPUT_DIR / f"{debug_name}_source_rects.png")
            self.draw_clean_debug(frames, DEBUG_OUTPUT_DIR / f"{debug_name}_clean_debug.png")
        return frames

    def make_equal_source_rects(self, sheet, frame_count):
        rects = []
        for index in range(frame_count):
            left = round(index * sheet.get_width() / frame_count)
            right = round((index + 1) * sheet.get_width() / frame_count)
            rects.append(pygame.Rect(left, 0, right - left, sheet.get_height()))
        return rects

    def check_effect_alpha(self, path, frame):
        corner = frame.get_at((0, 0))
        center = frame.get_at((frame.get_width() // 2, frame.get_height() // 2))
        print("Boss effect alpha check:", path)
        print("Frame surface alpha:", frame.get_alpha())
        print("Frame corner alpha:", corner.a)
        print("Frame center alpha:", center.a)
        if self.is_opaque_white_background(frame):
            print("Effect PNG background is not transparent. Regenerate/export as transparent PNG.")

    def is_opaque_white_background(self, frame):
        corner = frame.get_at((0, 0))
        return corner.a == 255 and corner.r > 235 and corner.g > 235 and corner.b > 235

    def repair_opaque_white_background(self, frame):
        if not self.is_opaque_white_background(frame):
            return frame

        print("Effect PNG background is not transparent. Regenerate/export as transparent PNG.")
        repaired = frame.copy()
        width, height = repaired.get_size()
        for y in range(height):
            for x in range(width):
                color = repaired.get_at((x, y))
                if color.a == 255 and color.r > 235 and color.g > 235 and color.b > 235:
                    repaired.set_at((x, y), (255, 255, 255, 0))
        return repaired

    def crop_visible_pixels(self, frame):
        bounds = frame.get_bounding_rect(min_alpha=1)
        if bounds.width <= 0 or bounds.height <= 0:
            return frame.copy()

        cropped = pygame.Surface(bounds.size, pygame.SRCALPHA)
        cropped.blit(frame, (0, 0), bounds)
        return cropped

    def scale_to_fit(self, surface, target_size):
        if surface.get_width() <= 0 or surface.get_height() <= 0:
            return pygame.Surface(target_size, pygame.SRCALPHA)

        scale = min(target_size[0] / surface.get_width(), target_size[1] / surface.get_height())
        scaled_size = (
            max(1, round(surface.get_width() * scale)),
            max(1, round(surface.get_height() * scale)),
        )
        return pygame.transform.smoothscale(surface, scaled_size)

    def place_on_canvas(self, surface, target_size, crop_mode):
        canvas = pygame.Surface(target_size, pygame.SRCALPHA)
        scaled = self.scale_to_fit(surface, target_size)
        rect = scaled.get_rect()
        if crop_mode == "ground_effect":
            rect.midbottom = (target_size[0] // 2, target_size[1])
        else:
            rect.center = (target_size[0] // 2, target_size[1] // 2)
        canvas.blit(scaled, rect)
        return canvas

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
        print("PaleCoreBoss requested asset folder:", PALE_CORE_ASSET_DIR)
        print("PaleCoreBoss requested asset folder exists:", PALE_CORE_ASSET_DIR.exists())
        print("PaleCoreBoss current source folder used:", self.asset_dir)
        print("PaleCoreBoss current source folder exists:", self.asset_dir.exists())
        print("PaleCoreBoss boss image loaded:", self.boss_image is not None)
        print("Boss projectile frames loaded:", len(self.animations.get("moon_orb_fly", [])))
        print("Boss ground effect frames loaded:", len(self.animations.get("lunar_shard_warning", [])))
        print("Boss beam frames loaded:", len(self.animations.get("core_beam_down", [])))
        for name in self.FRAME_COUNTS:
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
        self.float_timer = 0
        self.float_offset_y = 0
        self.update_core_anchor()
        self.weakpoint_open = False
        self.weakpoint_hit_cooldown = 0
        self.hit_effect_timer = 0
        self.moon_orbs.clear()
        self.shards.clear()
        self.hand_slams.clear()
        self.core_beam_rect = None
        self.core_beam_draw_rect = None
        self.core_beam_facing = 1
        self.core_beam_active = False
        self.player_hit_cooldown = 0

    def should_exist_on_map(self, map_id):
        return map_id == 8

    def should_draw_background(self, map_id, player):
        return self.should_exist_on_map(map_id) and player.rect.centerx >= self.arena_rect.left - 900

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
            self.phase = 2

        self.float_timer += dt
        self.float_offset_y = math.sin(self.float_timer * 1.4) * 4
        self.update_core_anchor()

        self.frame_timer += dt
        if self.frame_timer >= 0.12:
            self.frame_timer = 0
            self.frame_index += 1

        self.weakpoint_hit_cooldown = max(0, self.weakpoint_hit_cooldown - dt)
        self.hit_effect_timer = max(0, self.hit_effect_timer - dt)
        self.player_hit_cooldown = max(0, self.player_hit_cooldown - dt)
        self.state_timer -= dt

        self.update_moon_orbs(dt, player)
        self.update_shards(dt, player)
        self.update_hand_slams(dt, player)
        self.update_core_beam(player)

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
        self.current_attack_duration = 2.0 if self.phase == 1 else 1.5
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
        self.hand_slams.clear()
        self.core_beam_rect = None
        self.core_beam_draw_rect = None
        self.core_beam_active = False

    def choose_attack_skills(self):
        if self.phase == 1:
            phase1_skills = ["moon_orb", "lunar_shard"]
            chosen_skills = [random.choice(phase1_skills)]
        else:
            phase2_skills = ["core_beam", "moon_orb", "lunar_shard", "hand_slam"]
            skill_count = random.choice([1, 2])
            chosen_skills = random.sample(phase2_skills, skill_count)

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
                phase2_skills = ["core_beam", "moon_orb", "lunar_shard", "hand_slam"]
                skill_count = random.choice([1, 2])
                chosen_skills = random.sample(phase2_skills, skill_count)
            if tuple(sorted(chosen_skills)) != previous_signature:
                return chosen_skills
        return previous_skills

    def start_core_beam(self, player):
        self.core_beam_rect = pygame.Rect(player.rect.centerx - 55, 120, 110, 560)
        self.core_beam_facing = -1 if player.rect.centerx < self.core_center[0] else 1
        self.core_beam_draw_rect = pygame.Rect(0, 0, BOSS_BEAM_TARGET_SIZE[0], BOSS_BEAM_TARGET_SIZE[1])
        self.core_beam_draw_rect.centery = self.core_center[1]
        if self.core_beam_facing == 1:
            self.core_beam_draw_rect.midleft = self.core_center
        else:
            self.core_beam_draw_rect.midright = self.core_center
        self.core_beam_active = False

    def finish_attack(self):
        self.state = "idle"
        self.active_attack_skills = []
        self.core_beam_rect = None
        self.core_beam_draw_rect = None
        self.core_beam_active = False
        self.current_attack_duration = 0
        self.state_timer = 0.5 if self.phase == 2 else 1.0

    def open_weakpoint(self):
        self.state = "weakpoint_open"
        self.weakpoint_open = True
        self.frame_index = 0
        self.state_timer = 3.2
        print("PaleCoreBoss weakpoint open")

    def close_weakpoint(self):
        self.state = "idle"
        self.weakpoint_open = False
        self.state_timer = 0.8
        print("PaleCoreBoss weakpoint closed")

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
                "warning": pygame.Rect(x - 28, 625, 56, 28),
                "rect": pygame.Rect(x - 18, -140, 36, 120),
                "timer": 2.8,
                "warning_timer": 0.65,
                "damage": 16,
                "hit": False,
            })

    def spawn_hand_slam(self, player):
        side = random.choice(["left", "right"])
        offset = -180 if side == "left" else 180
        x = player.rect.centerx + offset
        self.hand_slams.append({
            "warning": pygame.Rect(x - 90, 575, 180, 75),
            "rect": pygame.Rect(x - 95, 495, 190, 155),
            "timer": 1.4,
            "warning_timer": 0.55,
            "damage": 20,
            "hit": False,
            "impact_checked": False,
            "side": side,
        })

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
        for slam in self.hand_slams:
            was_warning = slam["warning_timer"] > 0
            slam["timer"] -= dt
            slam["warning_timer"] -= dt
            impact_started = was_warning and slam["warning_timer"] <= 0
            if impact_started and not slam["impact_checked"]:
                slam["impact_checked"] = True
                if slam["rect"].colliderect(player.rect):
                    self.damage_player(player, slam["damage"])
                    slam["hit"] = True
        self.hand_slams = [slam for slam in self.hand_slams if slam["timer"] > 0]

    def update_core_beam(self, player):
        if "core_beam" not in self.active_attack_skills or self.core_beam_rect is None:
            return
        warning_time = 0.7
        self.core_beam_active = self.state_timer <= max(0.1, self.current_attack_duration - warning_time)
        print("Boss beam active state:", self.core_beam_active)
        if self.core_beam_active and self.core_beam_rect.colliderect(player.rect):
            self.damage_player(player, 18)

    def update_core_anchor(self):
        self.core_center = (
            self.base_core_center[0],
            round(self.base_core_center[1] + self.float_offset_y),
        )
        self.weakpoint_rect.center = self.core_center
        if self.core_beam_draw_rect is not None:
            self.core_beam_draw_rect.centery = self.core_center[1]
            if self.core_beam_facing == 1:
                self.core_beam_draw_rect.midleft = self.core_center
            else:
                self.core_beam_draw_rect.midright = self.core_center

    def get_floating_pos(self, pos):
        return (pos[0], round(pos[1] + self.float_offset_y))

    def damage_player(self, player, amount):
        if self.player_hit_cooldown > 0:
            return
        player.take_damage(amount)
        self.player_hit_cooldown = 0.45

    def take_damage(self, amount):
        if self.defeated or not self.weakpoint_open or self.weakpoint_hit_cooldown > 0:
            return False

        self.current_hp = max(0, self.current_hp - amount)
        self.weakpoint_hit_cooldown = 0.2
        self.hit_effect_timer = 0.42
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

    def draw_background(self, screen, camera=None):
        if self.boss_image is None:
            body_rect = self.body_rect.copy()
            body_rect.y += round(self.float_offset_y)
            draw_rect = self.apply_rect(body_rect, camera)
            pygame.draw.ellipse(screen, (36, 28, 55), draw_rect)
            pygame.draw.ellipse(screen, (110, 82, 150), draw_rect, 4)
            self.draw_core_idle_glow(screen, camera)
            self.draw_hand_auras(screen, camera)
            return

        draw_pos = (self.body_rect.x, self.body_rect.y + round(self.float_offset_y))
        if camera:
            draw_pos = camera.apply_pos(draw_pos)
        screen.blit(self.boss_image, draw_pos)
        self.draw_core_idle_glow(screen, camera)
        self.draw_hand_auras(screen, camera)

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

        self.draw_weakpoint(screen, camera)
        for orb in self.moon_orbs:
            draw_pos = orb["rect"].center
            if not self.blit_boss_effect_frame(screen, "moon_orb_fly", draw_pos, camera, anchor="center"):
                rect = self.apply_rect(orb["rect"], camera)
                pygame.draw.ellipse(screen, (140, 210, 255), rect)
                pygame.draw.ellipse(screen, (235, 250, 255), rect, 2)

        for shard in self.shards:
            if shard["warning_timer"] > 0:
                if not self.blit_boss_effect_frame(
                    screen,
                    "lunar_shard_warning",
                    shard["warning"].midbottom,
                    camera,
                    anchor="midbottom",
                ):
                    rect = self.apply_rect(shard["warning"], camera)
                    pygame.draw.rect(screen, (255, 80, 80), rect, 2)
            else:
                if not self.blit_boss_effect_frame(
                    screen,
                    "lunar_shard_fall",
                    shard["rect"].midbottom,
                    camera,
                    anchor="midbottom",
                ):
                    rect = self.apply_rect(shard["rect"], camera)
                    pygame.draw.rect(screen, (185, 225, 255), rect)

        for slam in self.hand_slams:
            if slam["warning_timer"] > 0:
                if not self.blit_boss_effect_frame(
                    screen,
                    "hand_slam_warning",
                    slam["warning"].midbottom,
                    camera,
                    anchor="midbottom",
                ):
                    rect = self.apply_rect(slam["warning"], camera)
                    pygame.draw.rect(screen, (255, 110, 60), rect, 2)
            else:
                if not self.blit_boss_effect_frame(
                    screen,
                    "hand_slam_down",
                    slam["rect"].midbottom,
                    camera,
                    anchor="midbottom",
                ):
                    rect = self.apply_rect(slam["rect"], camera)
                    pygame.draw.rect(screen, (95, 70, 125), rect)

        print("Current boss attack state:", self.state)
        print("Boss beam active state:", self.core_beam_active)
        if self.core_beam_draw_rect is not None:
            print("Boss beam draw branch entered")
            print("Boss beam file path:", self.asset_dir / "core_beam_down.png")
            print("Boss beam frame count:", len(self.animations.get("core_beam_down", [])))
            if self.core_beam_active:
                anchor = "midleft" if self.core_beam_facing == 1 else "midright"
                target_pos = (
                    self.core_beam_draw_rect.midleft
                    if self.core_beam_facing == 1
                    else self.core_beam_draw_rect.midright
                )
                if not self.blit_boss_effect_frame(
                    screen,
                    "core_beam_down",
                    target_pos,
                    camera,
                    flip_x=self.core_beam_facing < 0,
                    anchor=anchor,
                ):
                    rect = self.apply_rect(self.core_beam_draw_rect, camera)
                    pygame.draw.rect(screen, (80, 230, 255), rect)
                    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            else:
                anchor = "midleft" if self.core_beam_facing == 1 else "midright"
                target_pos = (
                    self.core_beam_draw_rect.midleft
                    if self.core_beam_facing == 1
                    else self.core_beam_draw_rect.midright
                )
                if not self.blit_boss_effect_frame(
                    screen,
                    "core_charge_down",
                    target_pos,
                    camera,
                    flip_x=self.core_beam_facing < 0,
                    anchor=anchor,
                ):
                    rect = self.apply_rect(self.core_beam_draw_rect, camera)
                    pygame.draw.rect(screen, (100, 190, 235), rect, 2)

    def draw_weakpoint(self, screen, camera=None):
        if self.defeated:
            return

        self.draw_core_idle_glow(screen, camera)

        rect = self.apply_rect(self.weakpoint_rect, camera)
        color = (70, 165, 205) if self.weakpoint_open else (45, 90, 130)
        border = (240, 255, 255) if self.weakpoint_open else (100, 145, 180)
        pygame.draw.ellipse(screen, color, rect)
        pygame.draw.ellipse(screen, border, rect, 2)

        if self.weakpoint_open:
            self.blit_boss_effect_frame(
                screen,
                "core_open",
                self.core_center,
                camera,
                anchor="center",
            )

        if self.hit_effect_timer > 0:
            self.blit_boss_effect_frame(
                screen,
                "boss_hit_effect",
                self.core_center,
                camera,
                anchor="center",
            )

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
        frames = self.animations.get(animation_name, [])
        frame_index = self.frame_index % len(frames) if frames else 0
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
        print("Drawing boss effect:", animation_name)
        print("current frame index:", frame_index)
        print("frame size:", image.get_size())
        print("draw rect position:", draw_rect)
        if animation_name == "core_beam_down":
            print("Boss beam draw position:", draw_rect.topleft)
        screen.blit(image, draw_rect)
        return True
