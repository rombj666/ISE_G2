import math
from pathlib import Path

import pygame
from src.utils.animation import load_libresprite_animation, Animation

from src.systems.animation import load_fixed_frame_sheet
from settings import (
    AUTO_GRAPPLE_ARC_HEIGHT,
    AUTO_GRAPPLE_DURATION,
    DEBUG_UNLIMITED_HP,
    DEBUG_UNLIMITED_MANA,
    GRAVITY,
    GRAPPLE_ANIM_OFFSET_X,
    GRAPPLE_ANIM_OFFSET_Y,
    GRAPPLE_ATTACK_ANIMATION_SPEED,
    GRAPPLE_ATTACK_FRAME_COUNT,
    GRAPPLE_ATTACK_OFFSET_X,
    GRAPPLE_ATTACK_OFFSET_Y,
    GRAPPLE_ATTACK_TARGET_HEIGHT,
    GRAPPLE_ATTACK_TARGET_WIDTH,
    GRAPPLE_DASH_ANIMATION_SPEED,
    GRAPPLE_DASH_FRAME_COUNT,
    GRAPPLE_IDLE_ANIMATION_SPEED,
    GRAPPLE_IDLE_FRAME_COUNT,
    GRAPPLE_JUMP_ANIMATION_SPEED,
    GRAPPLE_JUMP_FRAME_COUNT,
    GRAPPLE_PLAYER_TARGET_HEIGHT,
    GRAPPLE_PLAYER_TARGET_WIDTH,
    GRAPPLE_WALK_ANIMATION_SPEED,
    GRAPPLE_WALK_FRAME_COUNT,
    HEAVY_ATTACK_ANIMATION_SPEED,
    HEAVY_ATTACK_FRAME_COUNT,
    HEAVY_ATTACK_OFFSET_X,
    HEAVY_ATTACK_OFFSET_Y,
    HEAVY_ATTACK_TARGET_HEIGHT,
    HEAVY_ATTACK_TARGET_WIDTH,
    HEAVY_ANIM_OFFSET_X,
    HEAVY_ANIM_OFFSET_Y,
    HEAVY_DASH_ANIMATION_SPEED,
    HEAVY_DASH_FRAME_COUNT,
    HEAVY_IDLE_ANIMATION_SPEED,
    HEAVY_IDLE_FRAME_COUNT,
    HEAVY_JUMP_ANIMATION_SPEED,
    HEAVY_JUMP_FRAME_COUNT,
    HEAVY_PLAYER_TARGET_HEIGHT,
    HEAVY_PLAYER_TARGET_WIDTH,
    HEAVY_WALK_ANIMATION_SPEED,
    HEAVY_WALK_FRAME_COUNT,
    LIGHT_ATTACK_ANIMATION_SPEED,
    LIGHT_ATTACK_FRAME_COUNT,
    LIGHT_ATTACK_OFFSET_X,
    LIGHT_ATTACK_OFFSET_Y,
    LIGHT_ATTACK_TARGET_HEIGHT,
    LIGHT_ATTACK_TARGET_WIDTH,
    LIGHT_ANIM_OFFSET_X,
    LIGHT_ANIM_OFFSET_Y,
    LIGHT_DASH_ANIMATION_SPEED,
    LIGHT_DASH_FRAME_COUNT,
    LIGHT_IDLE_ANIMATION_SPEED,
    LIGHT_IDLE_FRAME_COUNT,
    LIGHT_JUMP_ANIMATION_SPEED,
    LIGHT_JUMP_FRAME_COUNT,
    LIGHT_PLAYER_TARGET_HEIGHT,
    LIGHT_PLAYER_TARGET_WIDTH,
    LIGHT_WALK_ANIMATION_SPEED,
    LIGHT_WALK_FRAME_COUNT,
    NORMAL_PARRY_ACTIVE_TIME,
    NORMAL_PARRY_COOLDOWN,
    PLAYER_BONUS_ATTACK_PERCENT,
    PLAYER_CRIT_CHANCE,
    PLAYER_CRIT_DAMAGE,
    PLAYER_DASH_COOLDOWN,
    PLAYER_DASH_SPEED,
    PLAYER_DASH_TIME,
    PLAYER_INVINCIBLE_TIME,
    PLAYER_JUMP_SPEED,
    PLAYER_MAX_HP,
    PLAYER_MAX_MANA,
    PLAYER_SPEED,
    SHIELD_ANIM_OFFSET_X,
    SHIELD_ANIM_OFFSET_Y,
    SHIELD_ATTACK_ANIMATION_SPEED,
    SHIELD_ATTACK_FRAME_COUNT,
    SHIELD_ATTACK_OFFSET_X,
    SHIELD_ATTACK_OFFSET_Y,
    SHIELD_ATTACK_TARGET_HEIGHT,
    SHIELD_ATTACK_TARGET_WIDTH,
    SHIELD_DASH_ANIMATION_SPEED,
    SHIELD_DASH_FRAME_COUNT,
    SHIELD_IDLE_ANIMATION_SPEED,
    SHIELD_IDLE_FRAME_COUNT,
    SHIELD_JUMP_ANIMATION_SPEED,
    SHIELD_JUMP_FRAME_COUNT,
    SHIELD_PLAYER_TARGET_HEIGHT,
    SHIELD_PLAYER_TARGET_WIDTH,
    SHIELD_WALK_ANIMATION_SPEED,
    SHIELD_WALK_FRAME_COUNT,
    SHOOTER_ANIM_OFFSET_X,
    SHOOTER_ANIM_OFFSET_Y,
    SHOOTER_ATTACK_ANIMATION_SPEED,
    SHOOTER_ATTACK_FRAME_COUNT,
    SHOOTER_ATTACK_OFFSET_X,
    SHOOTER_ATTACK_OFFSET_Y,
    SHOOTER_ATTACK_TARGET_HEIGHT,
    SHOOTER_ATTACK_TARGET_WIDTH,
    SHOOTER_DASH_ANIMATION_SPEED,
    SHOOTER_DASH_FRAME_COUNT,
    SHOOTER_IDLE_ANIMATION_SPEED,
    SHOOTER_IDLE_FRAME_COUNT,
    SHOOTER_JUMP_ANIMATION_SPEED,
    SHOOTER_JUMP_FRAME_COUNT,
    SHOOTER_PLAYER_TARGET_HEIGHT,
    SHOOTER_PLAYER_TARGET_WIDTH,
    SHOOTER_WALK_ANIMATION_SPEED,
    SHOOTER_WALK_FRAME_COUNT,
)
from src.systems.skills import get_skill
from src.systems.weapons import get_weapon


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LIGHT_WEAPON_IMAGE_PATH = PROJECT_ROOT / "assets" / "weapons" / "light_weapon.png"
PROCESSED_ANIMATION_ROOT = PROJECT_ROOT / "assets" / "processed" / "animations"
PROCESSED_WEAPON_ROOT = PROJECT_ROOT / "assets" / "processed" / "weapons"
DEBUG_ATTACK_ANIMATION = True
DEBUG_JUMP_ANIMATION = True
LIGHT_WEAPON_IDLE_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "light_weapon_idle_clean.png"
LIGHT_WEAPON_WALK_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "light_weapon_walk_clean.png"
LIGHT_WEAPON_JUMP_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "light_weapon_jump_clean.png"
LIGHT_WEAPON_DASH_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "light_weapon_dash_clean.png"
LIGHT_ATTACK_SHEET_PATH = PROCESSED_WEAPON_ROOT / "light_attack_clean.png"
HEAVY_WEAPON_IDLE_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "heavy_weapon_idle_clean.png"
HEAVY_WEAPON_WALK_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "heavy_weapon_walk_clean.png"
HEAVY_WEAPON_JUMP_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "heavy_weapon_jump_clean.png"
HEAVY_WEAPON_DASH_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "heavy_weapon_dash_clean.png"
HEAVY_ATTACK_SHEET_PATH = PROCESSED_WEAPON_ROOT / "heavy_attack_clean.png"
SHOOTER_WEAPON_IDLE_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "shooter_weapon_idle_clean.png"
SHOOTER_WEAPON_WALK_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "shooter_weapon_walk_clean.png"
SHOOTER_WEAPON_JUMP_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "shooter_weapon_jump_clean.png"
SHOOTER_WEAPON_DASH_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "shooter_weapon_dash_clean.png"
SHOOTER_ATTACK_SHEET_PATH = PROCESSED_WEAPON_ROOT / "shooter_attack_clean.png"
SHIELD_WEAPON_IDLE_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "shield_weapon_idle_clean.png"
SHIELD_WEAPON_WALK_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "shield_weapon_walk_clean.png"
SHIELD_WEAPON_JUMP_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "shield_weapon_jump_clean.png"
SHIELD_WEAPON_DASH_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "shield_weapon_dash_clean.png"
SHIELD_ATTACK_SHEET_PATH = PROCESSED_WEAPON_ROOT / "shield_attack_clean.png"
GRAPPLE_WEAPON_IDLE_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "grapple_weapon_idle_clean.png"
GRAPPLE_WEAPON_WALK_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "grapple_weapon_walk_clean.png"
GRAPPLE_WEAPON_JUMP_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "grapple_weapon_jump_clean.png"
GRAPPLE_WEAPON_DASH_SHEET_PATH = PROCESSED_ANIMATION_ROOT / "grapple_weapon_dash_clean.png"
GRAPPLE_ATTACK_SHEET_PATH = PROCESSED_WEAPON_ROOT / "grapple_attack_clean.png"
LIGHT_WEAPON_ATTACK_DURATION = 0.12
ATTACK_FRAME_CANVAS_SIZES = {
    "light": (320, 220),
    "heavy": (360, 240),
    "shooter": (300, 220),
    "shield": (320, 220),
    "grapple": (420, 240),
}
MOVEMENT_FRAME_CANVAS_SIZES = {
    ("light", "idle"): (LIGHT_PLAYER_TARGET_WIDTH, LIGHT_PLAYER_TARGET_HEIGHT),
    ("light", "walk"): (LIGHT_PLAYER_TARGET_WIDTH, LIGHT_PLAYER_TARGET_HEIGHT),
    ("light", "jump"): (LIGHT_PLAYER_TARGET_WIDTH, LIGHT_PLAYER_TARGET_HEIGHT),
    ("light", "dash"): (LIGHT_PLAYER_TARGET_WIDTH, LIGHT_PLAYER_TARGET_HEIGHT),
    ("heavy", "idle"): (HEAVY_PLAYER_TARGET_WIDTH, HEAVY_PLAYER_TARGET_HEIGHT),
    ("heavy", "walk"): (HEAVY_PLAYER_TARGET_WIDTH, HEAVY_PLAYER_TARGET_HEIGHT),
    ("heavy", "jump"): (HEAVY_PLAYER_TARGET_WIDTH, HEAVY_PLAYER_TARGET_HEIGHT),
    ("heavy", "dash"): (HEAVY_PLAYER_TARGET_WIDTH, HEAVY_PLAYER_TARGET_HEIGHT),
    ("shooter", "idle"): (SHOOTER_PLAYER_TARGET_WIDTH, SHOOTER_PLAYER_TARGET_HEIGHT),
    ("shooter", "walk"): (SHOOTER_PLAYER_TARGET_WIDTH, SHOOTER_PLAYER_TARGET_HEIGHT),
    ("shooter", "jump"): (300, 260),
    ("shooter", "dash"): (SHOOTER_PLAYER_TARGET_WIDTH, SHOOTER_PLAYER_TARGET_HEIGHT),
    ("shield", "idle"): (SHIELD_PLAYER_TARGET_WIDTH, SHIELD_PLAYER_TARGET_HEIGHT),
    ("shield", "walk"): (SHIELD_PLAYER_TARGET_WIDTH, SHIELD_PLAYER_TARGET_HEIGHT),
    ("shield", "jump"): (300, 260),
    ("shield", "dash"): (SHIELD_PLAYER_TARGET_WIDTH, SHIELD_PLAYER_TARGET_HEIGHT),
    ("grapple", "idle"): (GRAPPLE_PLAYER_TARGET_WIDTH, GRAPPLE_PLAYER_TARGET_HEIGHT),
    ("grapple", "walk"): (GRAPPLE_PLAYER_TARGET_WIDTH, GRAPPLE_PLAYER_TARGET_HEIGHT),
    ("grapple", "jump"): (GRAPPLE_PLAYER_TARGET_WIDTH, GRAPPLE_PLAYER_TARGET_HEIGHT),
    ("grapple", "dash"): (GRAPPLE_PLAYER_TARGET_WIDTH, GRAPPLE_PLAYER_TARGET_HEIGHT),
}
MANUAL_JUMP_RECTS_ACTIVE = {
    "shooter": True,
    "shield": True,
}


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48,64)

        self.vel_x = 0
        self.vel_y = 0
        self.facing = 1

        self.jump_count = 0
        self.max_jumps = 2
        self.jump_pressed = False
        self.acceleration = 0.6
        self.friction = 0.85
        self.max_speed = PLAYER_SPEED
        self.on_ground = True
        self.drop_through_timer = 0
        self.previous_bottom = self.rect.bottom

        self.hp = PLAYER_MAX_HP
        self.current_hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.mana = PLAYER_MAX_MANA
        self.current_mana = PLAYER_MAX_MANA
        self.max_mana = PLAYER_MAX_MANA

        self.crit_chance = PLAYER_CRIT_CHANCE
        self.crit_damage = PLAYER_CRIT_DAMAGE
        self.bonus_attack_percent = PLAYER_BONUS_ATTACK_PERCENT
        self.coins = 0

        self.current_weapon_id = "light_weapon"
        self.current_skill_id = "time_freeze"
        self.skill_cooldown_timer = 0
        self.debug_unlimited_hp = DEBUG_UNLIMITED_HP
        self.debug_unlimited_mana = DEBUG_UNLIMITED_MANA

        self.soul_anchor_active = False
        self.soul_anchor_pos = None
        self.soul_anchor_timer = 0

        self.is_blocking = False

        self.is_parrying = False
        self.parry_timer = 0
        self.parry_cooldown_timer = 0

        self.is_auto_grappling = False
        self.auto_grapple_timer = 0
        self.auto_grapple_duration = 0
        self.auto_grapple_start = None
        self.auto_grapple_end = None
        self.auto_grapple_control = None
        self.auto_grapple_anchor = None

        self.is_swinging = False
        self.swing_anchor = None
        self.swing_radius = 0
        self.swing_angle = 0
        self.swing_angular_velocity = 0

        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0

        self.is_attacking = False
        self.attack_timer = 0
        self.attack_visual_duration = LIGHT_WEAPON_ATTACK_DURATION
        self.attack_cooldown_timer = 0
        self.attack_hitbox = pygame.Rect(0, 0, 1, 1)
        self.attack_has_hit = False
        self.should_spawn_projectile = False
        self.light_weapon_image = self.load_light_weapon_image()
        def load_weapon_sheet(
            path,
            frame_count,
            target_size,
            debug_name=None,
            **_unused_preprocess_options,
        ):
            return load_fixed_frame_sheet(
                path,
                frame_count,
                target_size[0],
                target_size[1],
                debug_name=debug_name,
            )

        self.light_weapon_idle_frames = load_weapon_sheet(
            LIGHT_WEAPON_IDLE_SHEET_PATH,
            LIGHT_IDLE_FRAME_COUNT,
            (LIGHT_PLAYER_TARGET_WIDTH, LIGHT_PLAYER_TARGET_HEIGHT),
            padding=6,
        )
        self.light_weapon_walk_frames = load_weapon_sheet(
            LIGHT_WEAPON_WALK_SHEET_PATH,
            LIGHT_WALK_FRAME_COUNT,
            (LIGHT_PLAYER_TARGET_WIDTH, LIGHT_PLAYER_TARGET_HEIGHT),
            padding=6,
        )
        self.light_weapon_jump_frames = load_weapon_sheet(
            LIGHT_WEAPON_JUMP_SHEET_PATH,
            LIGHT_JUMP_FRAME_COUNT,
            (LIGHT_PLAYER_TARGET_WIDTH, LIGHT_PLAYER_TARGET_HEIGHT),
        )
        self.light_weapon_dash_frames = load_weapon_sheet(
            LIGHT_WEAPON_DASH_SHEET_PATH,
            LIGHT_DASH_FRAME_COUNT,
            (LIGHT_PLAYER_TARGET_WIDTH, LIGHT_PLAYER_TARGET_HEIGHT),
        )
        self.light_weapon_attack_frames = load_weapon_sheet(
            LIGHT_ATTACK_SHEET_PATH,
            LIGHT_ATTACK_FRAME_COUNT,
            ATTACK_FRAME_CANVAS_SIZES["light"],
            debug_name="light attack",
        )
        if self.light_weapon_attack_frames:
            print("Light attack final canvas size:", self.light_weapon_attack_frames[0].get_size())
        self.heavy_weapon_idle_frames = load_weapon_sheet(
            HEAVY_WEAPON_IDLE_SHEET_PATH,
            HEAVY_IDLE_FRAME_COUNT,
            (HEAVY_PLAYER_TARGET_WIDTH, HEAVY_PLAYER_TARGET_HEIGHT),
        )
        self.heavy_weapon_walk_frames = load_weapon_sheet(
            HEAVY_WEAPON_WALK_SHEET_PATH,
            HEAVY_WALK_FRAME_COUNT,
            (HEAVY_PLAYER_TARGET_WIDTH, HEAVY_PLAYER_TARGET_HEIGHT),
            padding=6,
        )
        self.heavy_weapon_jump_frames = load_weapon_sheet(
            HEAVY_WEAPON_JUMP_SHEET_PATH,
            HEAVY_JUMP_FRAME_COUNT,
            (HEAVY_PLAYER_TARGET_WIDTH, HEAVY_PLAYER_TARGET_HEIGHT),
        )
        self.heavy_weapon_dash_frames = load_weapon_sheet(
            HEAVY_WEAPON_DASH_SHEET_PATH,
            HEAVY_DASH_FRAME_COUNT,
            (HEAVY_PLAYER_TARGET_WIDTH, HEAVY_PLAYER_TARGET_HEIGHT),
        )
        self.heavy_weapon_attack_frames = load_weapon_sheet(
            HEAVY_ATTACK_SHEET_PATH,
            HEAVY_ATTACK_FRAME_COUNT,
            ATTACK_FRAME_CANVAS_SIZES["heavy"],
            debug_name="heavy attack",
        )
        self.shooter_weapon_idle_frames = load_weapon_sheet(
            SHOOTER_WEAPON_IDLE_SHEET_PATH,
            SHOOTER_IDLE_FRAME_COUNT,
            (SHOOTER_PLAYER_TARGET_WIDTH, SHOOTER_PLAYER_TARGET_HEIGHT),
        )
        self.shooter_weapon_walk_frames = load_weapon_sheet(
            SHOOTER_WEAPON_WALK_SHEET_PATH,
            SHOOTER_WALK_FRAME_COUNT,
            (SHOOTER_PLAYER_TARGET_WIDTH, SHOOTER_PLAYER_TARGET_HEIGHT),
        )
        self.shooter_weapon_jump_frames = load_weapon_sheet(
            SHOOTER_WEAPON_JUMP_SHEET_PATH,
            SHOOTER_JUMP_FRAME_COUNT,
            MOVEMENT_FRAME_CANVAS_SIZES[("shooter", "jump")],
            debug_name="shooter jump",
        )
        self.shooter_weapon_dash_frames = load_weapon_sheet(
            SHOOTER_WEAPON_DASH_SHEET_PATH,
            SHOOTER_DASH_FRAME_COUNT,
            (SHOOTER_PLAYER_TARGET_WIDTH, SHOOTER_PLAYER_TARGET_HEIGHT),
        )
        self.shooter_weapon_attack_frames = load_weapon_sheet(
            SHOOTER_ATTACK_SHEET_PATH,
            SHOOTER_ATTACK_FRAME_COUNT,
            ATTACK_FRAME_CANVAS_SIZES["shooter"],
            debug_name="shooter attack",
        )
        if self.shooter_weapon_attack_frames:
            print("Shooter attack final canvas size:", self.shooter_weapon_attack_frames[0].get_size())

        self.shield_weapon_idle_frames = load_weapon_sheet(
            SHIELD_WEAPON_IDLE_SHEET_PATH,
            SHIELD_IDLE_FRAME_COUNT,
            (SHIELD_PLAYER_TARGET_WIDTH, SHIELD_PLAYER_TARGET_HEIGHT),
        )
        self.shield_weapon_walk_frames = load_weapon_sheet(
            SHIELD_WEAPON_WALK_SHEET_PATH,
            SHIELD_WALK_FRAME_COUNT,
            (SHIELD_PLAYER_TARGET_WIDTH, SHIELD_PLAYER_TARGET_HEIGHT),
        )
        self.shield_weapon_jump_frames = load_weapon_sheet(
            SHIELD_WEAPON_JUMP_SHEET_PATH,
            SHIELD_JUMP_FRAME_COUNT,
            MOVEMENT_FRAME_CANVAS_SIZES[("shield", "jump")],
            debug_name="shield jump",
        )
        self.shield_weapon_dash_frames = load_weapon_sheet(
            SHIELD_WEAPON_DASH_SHEET_PATH,
            SHIELD_DASH_FRAME_COUNT,
            (SHIELD_PLAYER_TARGET_WIDTH, SHIELD_PLAYER_TARGET_HEIGHT),
        )
        self.shield_weapon_attack_frames = load_weapon_sheet(
            SHIELD_ATTACK_SHEET_PATH,
            SHIELD_ATTACK_FRAME_COUNT,
            ATTACK_FRAME_CANVAS_SIZES["shield"],
            debug_name="shield attack",
        )
        if self.shield_weapon_attack_frames:
            print("Shield attack final canvas size:", self.shield_weapon_attack_frames[0].get_size())

        self.grapple_weapon_idle_frames = load_weapon_sheet(
            GRAPPLE_WEAPON_IDLE_SHEET_PATH,
            GRAPPLE_IDLE_FRAME_COUNT,
            (GRAPPLE_PLAYER_TARGET_WIDTH, GRAPPLE_PLAYER_TARGET_HEIGHT),
        )
        self.grapple_weapon_walk_frames = load_weapon_sheet(
            GRAPPLE_WEAPON_WALK_SHEET_PATH,
            GRAPPLE_WALK_FRAME_COUNT,
            (GRAPPLE_PLAYER_TARGET_WIDTH, GRAPPLE_PLAYER_TARGET_HEIGHT),
        )
        self.grapple_weapon_jump_frames = load_weapon_sheet(
            GRAPPLE_WEAPON_JUMP_SHEET_PATH,
            GRAPPLE_JUMP_FRAME_COUNT,
            (GRAPPLE_PLAYER_TARGET_WIDTH, GRAPPLE_PLAYER_TARGET_HEIGHT),
        )
        self.grapple_weapon_dash_frames = load_weapon_sheet(
            GRAPPLE_WEAPON_DASH_SHEET_PATH,
            GRAPPLE_DASH_FRAME_COUNT,
            (GRAPPLE_PLAYER_TARGET_WIDTH, GRAPPLE_PLAYER_TARGET_HEIGHT),
        )
        self.grapple_weapon_attack_frames = load_weapon_sheet(
            GRAPPLE_ATTACK_SHEET_PATH,
            GRAPPLE_ATTACK_FRAME_COUNT,
            ATTACK_FRAME_CANVAS_SIZES["grapple"],
            debug_name="grapple attack",
        )
        if self.grapple_weapon_attack_frames:
            print("Grapple attack final canvas size:", self.grapple_weapon_attack_frames[0].get_size())

        self.print_jump_animation_debug_summary()

        self.light_idle_index = 0
        self.light_idle_timer = 0
        self.light_walk_index = 0
        self.light_walk_timer = 0
        self.light_jump_index = 0
        self.light_jump_timer = 0
        self.light_dash_index = 0
        self.light_dash_timer = 0
        self.heavy_idle_index = 0
        self.heavy_idle_timer = 0
        self.heavy_walk_index = 0
        self.heavy_walk_timer = 0
        self.heavy_jump_index = 0
        self.heavy_jump_timer = 0
        self.heavy_dash_index = 0
        self.heavy_dash_timer = 0
        self.shooter_idle_index = 0
        self.shooter_idle_timer = 0
        self.shooter_walk_index = 0
        self.shooter_walk_timer = 0
        self.shooter_jump_index = 0
        self.shooter_jump_timer = 0
        self.shooter_dash_index = 0
        self.shooter_dash_timer = 0
        self.shield_idle_index = 0
        self.shield_idle_timer = 0
        self.shield_walk_index = 0
        self.shield_walk_timer = 0
        self.shield_jump_index = 0
        self.shield_jump_timer = 0
        self.shield_dash_index = 0
        self.shield_dash_timer = 0
        self.grapple_idle_index = 0
        self.grapple_idle_timer = 0
        self.grapple_walk_index = 0
        self.grapple_walk_timer = 0
        self.grapple_jump_index = 0
        self.grapple_jump_timer = 0
        self.grapple_dash_index = 0
        self.grapple_dash_timer = 0
        self.attack_animation_frames = []
        self.attack_animation_index = 0
        self.attack_animation_timer = 0
        self.attack_animation_playing = False
        self.attack_animation_flip = False
        self.attack_animation_speed = LIGHT_ATTACK_ANIMATION_SPEED
        self.attack_animation_weapon_id = None
        self.last_jump_animation_debug_state = None
        self.light_anim_offset_x = LIGHT_ANIM_OFFSET_X
        self.light_anim_offset_y = LIGHT_ANIM_OFFSET_Y
        self.light_attack_offset_x = LIGHT_ATTACK_OFFSET_X
        self.light_attack_offset_y = LIGHT_ATTACK_OFFSET_Y
        self.heavy_anim_offset_x = HEAVY_ANIM_OFFSET_X
        self.heavy_anim_offset_y = HEAVY_ANIM_OFFSET_Y
        self.heavy_attack_offset_x = HEAVY_ATTACK_OFFSET_X
        self.heavy_attack_offset_y = HEAVY_ATTACK_OFFSET_Y
        self.shooter_anim_offset_x = SHOOTER_ANIM_OFFSET_X
        self.shooter_anim_offset_y = SHOOTER_ANIM_OFFSET_Y
        self.shooter_attack_offset_x = SHOOTER_ATTACK_OFFSET_X
        self.shooter_attack_offset_y = SHOOTER_ATTACK_OFFSET_Y
        self.shield_anim_offset_x = SHIELD_ANIM_OFFSET_X
        self.shield_anim_offset_y = SHIELD_ANIM_OFFSET_Y
        self.shield_attack_offset_x = SHIELD_ATTACK_OFFSET_X
        self.shield_attack_offset_y = SHIELD_ATTACK_OFFSET_Y
        self.grapple_anim_offset_x = GRAPPLE_ANIM_OFFSET_X
        self.grapple_anim_offset_y = GRAPPLE_ANIM_OFFSET_Y
        self.grapple_attack_offset_x = GRAPPLE_ATTACK_OFFSET_X
        self.grapple_attack_offset_y = GRAPPLE_ATTACK_OFFSET_Y

        self.invincible_timer = 0
        self.is_dead = False

        self.l_was_pressed = False

        # Animation system
        self.animations = {}
        self.current_animation = None           # Currently playing animation
        self.current_action = "idle"            # Current action status
        self.attack_hit_frame = 0               # Trigger damage at frame 0
        self.attack_has_dealt_damage = False    # Whether damage has been caused
        self.jump_state = "rising"
        self.dash_start_x = 0
        self.last_vel_x = 0

        self.play_idle_animation()

    def load_light_weapon_image(self):
        if not LIGHT_WEAPON_IMAGE_PATH.exists():
            return None

        try:
            image = pygame.image.load(str(LIGHT_WEAPON_IMAGE_PATH)).convert_alpha()
        except (pygame.error, OSError):
            return None

        target_height = 28
        scale = target_height / image.get_height()
        target_size = (max(1, int(image.get_width() * scale)), target_height)
        return pygame.transform.smoothscale(image, target_size)

    def print_jump_animation_debug_summary(self):
        print("Shooter jump path:", SHOOTER_WEAPON_JUMP_SHEET_PATH)
        print("Shooter jump exists:", SHOOTER_WEAPON_JUMP_SHEET_PATH.exists())
        print("Shooter jump frames loaded:", len(self.shooter_weapon_jump_frames))
        if self.shooter_weapon_jump_frames:
            print("Shooter jump first frame size:", self.shooter_weapon_jump_frames[0].get_size())
        print("Shield jump path:", SHIELD_WEAPON_JUMP_SHEET_PATH)
        print("Shield jump exists:", SHIELD_WEAPON_JUMP_SHEET_PATH.exists())
        print("Shield jump frames loaded:", len(self.shield_weapon_jump_frames))
        if self.shield_weapon_jump_frames:
            print("Shield jump first frame size:", self.shield_weapon_jump_frames[0].get_size())
        print("Current source folder used:", PROCESSED_ANIMATION_ROOT)
        print("Manual jump rects active for shooter:", MANUAL_JUMP_RECTS_ACTIVE["shooter"])
        print("Manual jump rects active for shield:", MANUAL_JUMP_RECTS_ACTIVE["shield"])

    def handle_input(self, keys):
        if self.is_dead:
            self.vel_x = 0
            return

        if self.is_auto_grappling or self.is_swinging:
            self.vel_x = 0
            return

        if keys[pygame.K_1]:
            self.switch_weapon("light_weapon")
        if keys[pygame.K_2]:
            self.switch_weapon("heavy_weapon")
        if keys[pygame.K_3]:
            self.switch_weapon("shooter_weapon")
        if keys[pygame.K_4]:
            self.switch_weapon("shield_weapon")
        if keys[pygame.K_5]:
            self.switch_weapon("grapple_weapon")

        if keys[pygame.K_6]:
            self.switch_skill("time_freeze")
        if keys[pygame.K_7]:
            self.switch_skill("orbit_blades")
        if keys[pygame.K_8]:
            self.switch_skill("energy_beam")
        if keys[pygame.K_9]:
            self.switch_skill("soul_anchor")

        moving_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        moving_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        jump_key_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w]
        drop_pressed = keys[pygame.K_s] or keys[pygame.K_DOWN]

        if self.on_ground:
            self.jump_count = 0

        if not self.is_dashing:
            if moving_left:
                self.vel_x -= self.acceleration
                self.facing = -1

            if moving_right:
                self.vel_x += self.acceleration
                self.facing = 1

            if not moving_left and not moving_right:
                self.vel_x *= self.friction

            self.vel_x = max(-self.max_speed, min(self.max_speed, self.vel_x))

            if abs(self.vel_x) < 0.1:
                self.vel_x = 0

        if self.vel_x != 0:
            self.last_vel_x = self.vel_x

        if jump_key_pressed and drop_pressed and self.on_ground and not self.jump_pressed:
            self.drop_through_timer = 0.25
            self.rect.y += 4
            self.on_ground = False
            self.jump_pressed = True
        elif jump_key_pressed and not self.jump_pressed:
            if self.jump_count < self.max_jumps:
                self.vel_y = PLAYER_JUMP_SPEED
                self.jump_count += 1
                self.on_ground = False
                self.current_action = None
                self.jump_state = "rising"
            self.jump_pressed = True
        elif not jump_key_pressed:
            self.jump_pressed = False

        if keys[pygame.K_LSHIFT] and self.dash_cooldown_timer <= 0:
            self.start_dash()

        if keys[pygame.K_j] and self.attack_cooldown_timer <= 0:
            self.start_attack()

        l_pressed = keys[pygame.K_l]
        current_weapon = get_weapon(self.current_weapon_id)

        if current_weapon["id"] != "shield_weapon" and l_pressed and not self.l_was_pressed:
            self.start_normal_parry()

        self.l_was_pressed = l_pressed

    def switch_weapon(self, weapon_id):
        if self.current_weapon_id == weapon_id:
            return

        weapon = get_weapon(weapon_id)
        self.current_weapon_id = weapon["id"]
        self.is_attacking = False
        self.attack_has_hit = False
        self.should_spawn_projectile = False
        self.is_blocking = False
        print(f"Equipped {weapon['name']}")

    def switch_skill(self, skill_id):
        skill = get_skill(skill_id)

        if self.current_skill_id == skill["id"]:
            return

        self.current_skill_id = skill["id"]
        print(f"Equipped skill: {skill['name']}")

    def can_use_skill(self, skill):
        has_enough_mana = self.debug_unlimited_mana or self.current_mana >= skill["mana_cost"]

        return (
            has_enough_mana
            and self.skill_cooldown_timer <= 0
            and not self.is_dead
            and not self.is_auto_grappling
            and not self.is_swinging
        )

    def spend_skill_cost(self, skill):
        if not self.debug_unlimited_mana:
            self.current_mana -= skill["mana_cost"]
            self.current_mana = max(self.current_mana, 0)

        self.skill_cooldown_timer = skill["cooldown"]

    def toggle_unlimited_hp(self):
        self.debug_unlimited_hp = not self.debug_unlimited_hp

        if self.debug_unlimited_hp:
            print("Unlimited HP: ON")
        else:
            print("Unlimited HP: OFF")

    def toggle_unlimited_mana(self):
        self.debug_unlimited_mana = not self.debug_unlimited_mana

        if self.debug_unlimited_mana:
            print("Unlimited Mana: ON")
        else:
            print("Unlimited Mana: OFF")

    def update_skill_timers(self, dt):
        if self.skill_cooldown_timer > 0:
            self.skill_cooldown_timer -= dt

        if self.soul_anchor_active:
            self.soul_anchor_timer -= dt

            if self.soul_anchor_timer <= 0:
                self.soul_anchor_active = False
                self.soul_anchor_pos = None
                self.soul_anchor_timer = 0

    def start_dash(self):
        self.is_attacking = False
        self.current_action = "idle"

        self.is_dashing = True
        self.dash_timer = PLAYER_DASH_TIME
        self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN
        self.vel_y = 0

    def start_attack(self):
        if self.current_action == "attack_na1":
            return

        weapon = get_weapon(self.current_weapon_id)
        self.is_dashing = False
        print("Current weapon id:", self.current_weapon_id)
        print("Starting attack animation:", self.current_weapon_id)
        print("is_blocking:", self.is_blocking)
        weapon_visual_started = self.start_weapon_attack_animation(self.current_weapon_id)

        anim = None if weapon_visual_started else self.animations.get("attack_na1")
        if anim:
            anim.reset()
            anim.loop = False
            self.current_animation = anim
            self.current_action = "attack_na1"
            self.attack_has_hit = False
            self.attack_timer = LIGHT_WEAPON_ATTACK_DURATION
            self.attack_visual_duration = LIGHT_WEAPON_ATTACK_DURATION
            self.attack_cooldown_timer = weapon["cooldown"]
            self.is_attacking = True

            if weapon["weapon_type"] == "projectile":
                self.should_spawn_projectile = True
            else:
                self.attack_hitbox = self.get_attack_hitbox()
        else:
            if weapon_visual_started:
                self.current_animation = None
                self.current_action = "weapon_attack"

            self.is_attacking = True
            self.attack_timer = LIGHT_WEAPON_ATTACK_DURATION
            self.attack_visual_duration = LIGHT_WEAPON_ATTACK_DURATION
            self.attack_cooldown_timer = weapon["cooldown"]
            self.attack_has_hit = False

            if weapon["weapon_type"] == "projectile":
                self.should_spawn_projectile = True
            else:
                self.attack_hitbox = self.get_attack_hitbox()

    def normalize_weapon_id(self, weapon_id):
        mapping = {
            "light": "light",
            "light_weapon": "light",
            "heavy": "heavy",
            "heavy_weapon": "heavy",
            "shooter": "shooter",
            "shooter_weapon": "shooter",
            "shoot_weapon": "shooter",
            "shield": "shield",
            "shield_weapon": "shield",
            "grapple": "grapple",
            "grapple_weapon": "grapple",
        }
        return mapping.get(weapon_id, weapon_id)

    def start_weapon_attack_animation(self, weapon_id):
        weapon_key = self.normalize_weapon_id(weapon_id)

        if weapon_key == "light":
            frames = self.light_weapon_attack_frames
            speed = LIGHT_ATTACK_ANIMATION_SPEED
        elif weapon_key == "heavy":
            frames = self.heavy_weapon_attack_frames
            speed = HEAVY_ATTACK_ANIMATION_SPEED
        elif weapon_key == "shooter":
            frames = self.shooter_weapon_attack_frames
            speed = SHOOTER_ATTACK_ANIMATION_SPEED
        elif weapon_key == "shield":
            frames = self.shield_weapon_attack_frames
            speed = SHIELD_ATTACK_ANIMATION_SPEED
        elif weapon_key == "grapple":
            frames = self.grapple_weapon_attack_frames
            speed = GRAPPLE_ATTACK_ANIMATION_SPEED
        else:
            print("Unknown attack weapon id:", self.current_weapon_id)
            print("[ATTACK RESET] unknown weapon id")
            self.attack_animation_playing = False
            return False

        if not frames:
            print("No attack frames found for weapon:", self.current_weapon_id)
            print("[ATTACK RESET] missing frames")
            self.attack_animation_playing = False
            return False

        self.attack_animation_playing = True
        self.attack_animation_weapon_id = weapon_key
        self.attack_animation_frames = frames
        self.attack_animation_index = 0
        self.attack_animation_timer = 0
        self.attack_animation_speed = speed
        self.attack_animation_flip = self.facing == -1
        if DEBUG_ATTACK_ANIMATION:
            print("[ATTACK START]")
            print("weapon:", self.current_weapon_id)
            print("normalized:", weapon_key)
            print("frames:", len(frames))
            print("playing:", self.attack_animation_playing)
            print("index:", self.attack_animation_index)
            print("speed:", self.attack_animation_speed)
            print("first frame size:", frames[0].get_size() if frames else None)
        return True

    def get_attack_hitbox(self):
        weapon = get_weapon(self.current_weapon_id)
        hitbox_y = self.rect.centery - weapon["height"] // 2

        if self.facing == 1:
            hitbox_x = self.rect.right
        else:
            hitbox_x = self.rect.left - weapon["range"]

        return pygame.Rect(hitbox_x, hitbox_y, weapon["width"], weapon["height"])

    def start_normal_parry(self):
        if self.parry_cooldown_timer > 0:
            return

        if get_weapon(self.current_weapon_id)["id"] == "shield_weapon":
            return

        self.is_parrying = True
        self.parry_timer = NORMAL_PARRY_ACTIVE_TIME
        self.parry_cooldown_timer = NORMAL_PARRY_COOLDOWN

    def update_blocking(self, keys, dt):
        weapon = get_weapon(self.current_weapon_id)

        if weapon["id"] == "shield_weapon" and keys[pygame.K_l]:
            self.is_blocking = True
            return

        self.is_blocking = False

    def block_hit(self):
        self.is_blocking = True

    def take_damage(self, amount):
        if self.invincible_timer > 0 or self.is_dead:
            return

        if self.debug_unlimited_hp:
            self.invincible_timer = PLAYER_INVINCIBLE_TIME
            return

        self.current_hp -= amount
        self.current_hp = max(self.current_hp, 0)
        self.hp = self.current_hp
        self.invincible_timer = PLAYER_INVINCIBLE_TIME

        if self.current_hp <= 0:
            self.is_dead = True
            self.is_attacking = False
            self.is_dashing = False
            self.is_blocking = False
            self.vel_x = 0

    def collect_coin(self, coin):
        self.coins += coin.value
        coin.collected = True

    def start_auto_grapple(self, anchor_pos, end_pos):
        self.is_auto_grappling = True
        self.auto_grapple_timer = 0
        self.auto_grapple_duration = AUTO_GRAPPLE_DURATION
        self.auto_grapple_start = self.rect.center
        self.auto_grapple_end = end_pos
        self.auto_grapple_anchor = anchor_pos

        start_x, start_y = self.auto_grapple_start
        end_x, end_y = self.auto_grapple_end
        control_x = (start_x + end_x) / 2
        control_y = min(start_y, end_y) - AUTO_GRAPPLE_ARC_HEIGHT
        self.auto_grapple_control = (control_x, control_y)

        self.cancel_swing()
        self.is_dashing = False
        self.is_attacking = False
        self.is_blocking = False
        self.is_parrying = False
        self.vel_x = 0
        self.vel_y = 0

    def update_auto_grapple(self, dt):
        self.auto_grapple_timer += dt
        t = self.auto_grapple_timer / self.auto_grapple_duration
        t = max(0, min(1, t))

        p0_x, p0_y = self.auto_grapple_start
        p1_x, p1_y = self.auto_grapple_control
        p2_x, p2_y = self.auto_grapple_end

        x = (1 - t) ** 2 * p0_x + 2 * (1 - t) * t * p1_x + t ** 2 * p2_x
        y = (1 - t) ** 2 * p0_y + 2 * (1 - t) * t * p1_y + t ** 2 * p2_y

        self.rect.center = (round(x), round(y))

        if t >= 1:
            self.is_auto_grappling = False
            self.rect.center = self.auto_grapple_end
            self.vel_x = 0
            self.vel_y = 0
            self.auto_grapple_start = None
            self.auto_grapple_end = None
            self.auto_grapple_control = None
            self.auto_grapple_anchor = None

    def start_swing(self, anchor_pos):
        anchor_x, anchor_y = anchor_pos
        player_x, player_y = self.rect.center
        dx = player_x - anchor_x
        dy = player_y - anchor_y

        # Fulcrums are ceiling hooks. Kael always hangs below the hook,
        # but keeps enough side offset to start a real swinging arc.
        if dy < 90:
            dy = 135

        if abs(dx) < 30:
            dx = 90 * self.facing

        dx = max(-280, min(280, dx))
        radius = max(135, min(340, math.hypot(dx, dy)))

        min_swing_angle = math.radians(15)
        max_swing_angle = math.radians(165)

        self.is_swinging = True
        self.swing_anchor = anchor_pos
        self.swing_radius = radius
        self.swing_angle = math.atan2(dy, dx)
        self.swing_angle = max(min_swing_angle, min(max_swing_angle, self.swing_angle))

        self.swing_angular_velocity = self.vel_x / max(radius, 1)
        if abs(self.swing_angular_velocity) < 0.03:
            if self.swing_angle < math.pi / 2:
                self.swing_angular_velocity = 0.045
            elif self.swing_angle > math.pi / 2:
                self.swing_angular_velocity = -0.045
            else:
                self.swing_angular_velocity = 0.045 * self.facing

        center_x = anchor_x + math.cos(self.swing_angle) * self.swing_radius
        center_y = anchor_y + math.sin(self.swing_angle) * self.swing_radius
        self.rect.center = (round(center_x), round(center_y))

        self.is_auto_grappling = False
        self.is_dashing = False
        self.is_attacking = False
        self.is_blocking = False
        self.is_parrying = False
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def update_swing(self, dt, keys):
        if self.swing_anchor is None:
            self.cancel_swing()
            return

        frame_scale = max(0.5, min(2.0, dt * 60))
        min_swing_angle = math.radians(15)
        max_swing_angle = math.radians(165)

        # True below-hook pendulum motion. Straight down is pi / 2.
        angle_from_bottom = self.swing_angle - math.pi / 2
        self.swing_angular_velocity += -math.sin(angle_from_bottom) * 0.0062 * frame_scale

        # Optional player pumping. A pushes toward the left side of the arc,
        # D pushes toward the right side.
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.swing_angular_velocity += 0.0024 * frame_scale
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.swing_angular_velocity -= 0.0024 * frame_scale
            self.facing = 1

        self.swing_angular_velocity *= 0.997
        self.swing_angular_velocity = max(-0.115, min(0.115, self.swing_angular_velocity))
        self.swing_angle += self.swing_angular_velocity * frame_scale

        # Reflect at the top ends of the arc so the swing comes back naturally.
        # This prevents full-circle loops without creating a frozen hard stop.
        if self.swing_angle < min_swing_angle:
            overshoot = min_swing_angle - self.swing_angle
            self.swing_angle = min_swing_angle + overshoot
            self.swing_angular_velocity = abs(self.swing_angular_velocity) * 0.88
        elif self.swing_angle > max_swing_angle:
            overshoot = self.swing_angle - max_swing_angle
            self.swing_angle = max_swing_angle - overshoot
            self.swing_angular_velocity = -abs(self.swing_angular_velocity) * 0.88

        self.swing_angle = max(min_swing_angle, min(max_swing_angle, self.swing_angle))

        anchor_x, anchor_y = self.swing_anchor
        center_x = anchor_x + math.cos(self.swing_angle) * self.swing_radius
        center_y = anchor_y + math.sin(self.swing_angle) * self.swing_radius
        self.rect.center = (round(center_x), round(center_y))
        self.vel_x = 0
        self.vel_y = 0

    def release_swing(self):
        if not self.is_swinging or self.swing_anchor is None:
            return

        tangent_x = -math.sin(self.swing_angle)
        tangent_y = math.cos(self.swing_angle)
        launch_speed = self.swing_angular_velocity * self.swing_radius
        launch_speed = max(-18, min(18, launch_speed))

        self.vel_x = tangent_x * launch_speed
        self.vel_y = tangent_y * launch_speed - 5

        if abs(self.vel_x) < PLAYER_SPEED * 1.2:
            self.vel_x = PLAYER_SPEED * 1.8 * self.facing
        if self.vel_y > -4:
            self.vel_y = -8

        self.cancel_swing(keep_velocity=True)

    def cancel_swing(self, keep_velocity=False):
        self.is_swinging = False
        self.swing_anchor = None
        self.swing_radius = 0
        self.swing_angle = 0
        self.swing_angular_velocity = 0
        if not keep_velocity:
            self.vel_x = 0
            self.vel_y = 0

    def update(self, dt, platforms, keys):
        self.previous_bottom = self.rect.bottom
        if self.drop_through_timer > 0:
            self.drop_through_timer -= dt

        self.update_timers(dt)
        self.update_attack_animation(dt)

        if self.debug_unlimited_mana:
            self.current_mana = self.max_mana

        if self.is_dead:
            self.vel_x = 0
            return

        if self.is_swinging:
            self.update_swing(dt, keys)
            return

        if self.is_auto_grappling:
            self.update_auto_grapple(dt)
            return

        self.update_blocking(keys, dt)

        if self.is_attacking:
            self.attack_hitbox = self.get_attack_hitbox()

        if self.is_dashing:
            self.dash_timer -= dt
            self.vel_x = PLAYER_DASH_SPEED * self.facing
            self.vel_y = 0

            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            self.vel_y += GRAVITY

        self.move_x(platforms)
        self.move_y(platforms)
        self.update_weapon_movement_animation(dt)

        self.update_animation(dt)

    def update_timers(self, dt):
        self.update_skill_timers(dt)

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        if self.parry_cooldown_timer > 0:
            self.parry_cooldown_timer -= dt

        if self.is_parrying:
            self.parry_timer -= dt

            if self.parry_timer <= 0:
                self.is_parrying = False

        if self.is_attacking:
            self.attack_timer -= dt

            if self.attack_timer <= 0:
                self.is_attacking = False

    def update_animation(self, dt):
        """Update the currently playing animation with state-based logic"""

        # if hasattr(self, '_debug_counter'):
        #     self._debug_counter += 1
        # else:
        #     self._debug_counter = 0
        # if self._debug_counter % 30 == 0:
        #     print(f"on_ground: {self.on_ground}, vel_y: {self.vel_y}")

        if self.is_attacking:
            self.update_player_sprite_attack_animation(dt)
        elif self.is_dashing:
            self.update_dash_animation(dt)
        elif not self.on_ground:
            self.update_jump_animation(dt)
        elif abs(self.vel_x) > 0.5:
            self.update_walk_animation(dt)
        else:
            self.update_idle_animation(dt)

        # print(f"Frame end - current_action: {self.current_action}")

    def update_idle_animation(self, dt):
        """Play idle animation (looping)"""
        if self.current_action != "idle":
            anim = self.animations.get("idle")
            if anim:
                anim.reset()
                anim.loop = True
                self.current_animation = anim
                self.current_action = "idle"

        if self.current_animation:
            self.current_animation.update(dt)


    def update_walk_animation(self, dt):
        """Play walking animation (looping) - facing handled in draw()"""
        if self.is_attacking:
            return

        if self.current_action != "walk":
            anim = self.animations.get("walk")
            if anim:
                anim.reset()
                anim.loop = True
                self.current_animation = anim
                self.current_action = "walk"

        if self.current_animation:
            self.current_animation.update(dt)

    def update_jump_animation(self, dt):
        """
        Jump animation frame control:
        Frame 0: Crouch/prepare (rising start)
        Frame 1: Rising (vel_y < 0)
        Frame 2: Falling (vel_y > 0)
        Frame 3: Landing (only when on_ground becomes True)
        """

        self._idle_playing = False
        anim = self.animations.get("jump")
        if not anim:
            return

        if not hasattr(self, 'jump_state'):
            self.jump_state = "rising"

        # Start jump animation if not already playing
        if self.current_action != "jump":
            anim.reset()
            anim.loop = False
            self.current_animation = anim
            self.current_action = "jump"
            self.jump_state = "rising"

        # Control frame based on jump state
        if self.current_animation:
            if self.vel_y < 0:
                self.jump_state = "rising"
            elif self.vel_y > 0 and self.jump_state != "falling":
                # Switch to falling state
                self.jump_state = "falling"
                self.current_animation.current_frame = 2
            elif self.jump_state == "falling" and self.on_ground:
                # Landing - go to frame 3 then idle
                self.jump_state = "landing"
                self.current_animation.current_frame = 3
            elif self.jump_state == "rising":
                # Rising - stay at frame 1
                if self.current_animation.current_frame < 1:
                    self.current_animation.current_frame = 1
                self.current_animation.current_frame = min(self.current_animation.current_frame, 1)
            elif self.jump_state == "falling":
                # Falling - stay at frame 2
                if self.current_animation.current_frame < 2:
                    self.current_animation.current_frame = 2
                self.current_animation.current_frame = min(self.current_animation.current_frame, 2)
            elif self.jump_state == "landing":
                # Landing - wait for animation to finish then go to idle
                self.current_animation.update(dt)
                if self.current_animation.finished or self.current_animation.current_frame >= 3:
                    self.play_idle_animation()
                    self.jump_state = "rising"
                return

            # Update animation timer
            self.current_animation.timer += dt
            if self.current_animation.timer >= self.current_animation.duration_per_frame:
                self.current_animation.timer = 0
                # Only auto-advance frames for rising/falling if not manually controlled
                if self.jump_state == "rising" and self.current_animation.current_frame < 1:
                    self.current_animation.current_frame = min(self.current_animation.current_frame + 1, 1)
                elif self.jump_state == "falling" and self.current_animation.current_frame < 2:
                    self.current_animation.current_frame = min(self.current_animation.current_frame + 1, 2)


    def update_dash_animation(self, dt):
        """
        Dash animation: play frames 0,1,2 during dash movement,
        frame 3 at the end of dash, then back to idle/walk.
        """
        anim = self.animations.get("dash")
        if not anim:
            return

        # Start dash animation if not already playing
        if self.current_action != "dash":
            anim.reset()
            anim.loop = False
            self.current_animation = anim
            self.current_action = "dash"
            self.dash_start_x = self.rect.x

        if self.current_animation:
            # During dash, play frames 0,1,2
            if self.is_dashing:
                # Force frame to advance based on dash progress
                dash_progress = 1.0 - (self.dash_timer / PLAYER_DASH_TIME)
                frame_index = min(int(dash_progress * 3), 2)  # 0, 1, or 2
                self.current_animation.current_frame = frame_index
                self.current_animation.update(dt)  # Still update timer but frame is forced
            else:
                # Dash finished - go to frame 3 then switch to idle/walk
                if self.current_animation.current_frame < 3:
                    self.current_animation.current_frame = 3
                self.current_animation.update(dt)
                if self.current_animation.finished or self.current_animation.current_frame >= 3:
                    # Dash animation complete, return to idle or walk
                    if abs(self.vel_x) > 0.5 and self.on_ground:
                        # Start walking animation
                        self.update_walk_animation(dt)
                    else:
                        self.play_idle_animation()

    def update_player_sprite_attack_animation(self, dt):
        """Update attack animation (non-looping)"""
        anim = self.current_animation
        if anim:
            anim.update(dt)

            # Trigger damage on hit frame
            if (not self.attack_has_hit and
                anim.current_frame >= self.attack_hit_frame):
                self.attack_has_hit = True

            # When animation finishes, go back to idle/walk
            if anim.finished:
                self.is_attacking = False
                if abs(self.vel_x) > 0.5 and self.on_ground:
                    self.update_walk_animation(dt)
                else:
                    self.play_idle_animation()

    def update_attack_animation(self, dt):
        if not self.attack_animation_playing:
            return

        if not self.attack_animation_frames:
            print("[ATTACK RESET] no attack animation frames during update")
            self.attack_animation_playing = False
            return

        if DEBUG_ATTACK_ANIMATION:
            print(
                "[ATTACK UPDATE]",
                "index:", self.attack_animation_index,
                "timer:", self.attack_animation_timer,
            )

        self.attack_animation_timer += dt
        while self.attack_animation_timer >= self.attack_animation_speed:
            self.attack_animation_timer -= self.attack_animation_speed
            self.attack_animation_index += 1

            if self.attack_animation_index >= len(self.attack_animation_frames):
                self.attack_animation_playing = False
                self.attack_animation_index = 0
                self.attack_animation_timer = 0
                self.attack_animation_frames = []
                self.attack_animation_weapon_id = None
                self.attack_animation_flip = False
                print("[ATTACK FINISHED]")
                return


    def update_weapon_movement_animation(self, dt):
        if self.attack_animation_playing:
            return

        visual_state = self.get_visual_state()
        weapon_key = self.normalize_weapon_id(self.current_weapon_id)

        if weapon_key in ("light", "heavy", "shooter", "shield", "grapple"):
            if DEBUG_JUMP_ANIMATION and visual_state == "jump" and weapon_key in ("shooter", "shield"):
                frames, _ = self.get_weapon_state_frames_and_speed(weapon_key, visual_state)
                debug_state = (
                    self.current_weapon_id,
                    weapon_key,
                    visual_state,
                    len(frames),
                    self.on_ground,
                )
                if debug_state != self.last_jump_animation_debug_state:
                    print("[JUMP ANIMATION SELECT]")
                    print("current weapon id:", self.current_weapon_id)
                    print("normalized weapon key:", weapon_key)
                    print("current movement state:", visual_state)
                    print("jump animation selected:", True)
                    print("jump frames available:", len(frames))
                    self.last_jump_animation_debug_state = debug_state

            self.update_weapon_state_animation(weapon_key, visual_state, dt)
            return

    def get_visual_state(self):
        if self.attack_animation_playing:
            return "attack"
        if not self.on_ground:
            return "jump"
        if self.is_dashing:
            return "dash"
        if abs(self.vel_x) > 0.1:
            return "walk"
        return "idle"

    def update_weapon_state_animation(self, weapon_prefix, visual_state, dt):
        frames, speed = self.get_weapon_state_frames_and_speed(weapon_prefix, visual_state)
        self.update_looping_animation(
            dt,
            frames,
            f"{weapon_prefix}_{visual_state}_index",
            f"{weapon_prefix}_{visual_state}_timer",
            speed,
        )

    def update_looping_animation(self, dt, frames, index_attr, timer_attr, speed):
        if not frames:
            return

        setattr(self, timer_attr, getattr(self, timer_attr) + dt)
        if getattr(self, timer_attr) >= speed:
            setattr(self, timer_attr, 0)
            setattr(self, index_attr, (getattr(self, index_attr) + 1) % len(frames))

    def get_weapon_state_frames_and_speed(self, weapon_prefix, visual_state):
        animation_map = {
            "light": {
                "idle": (self.light_weapon_idle_frames, LIGHT_IDLE_ANIMATION_SPEED),
                "walk": (self.light_weapon_walk_frames, LIGHT_WALK_ANIMATION_SPEED),
                "jump": (self.light_weapon_jump_frames, LIGHT_JUMP_ANIMATION_SPEED),
                "dash": (self.light_weapon_dash_frames, LIGHT_DASH_ANIMATION_SPEED),
            },
            "heavy": {
                "idle": (self.heavy_weapon_idle_frames, HEAVY_IDLE_ANIMATION_SPEED),
                "walk": (self.heavy_weapon_walk_frames, HEAVY_WALK_ANIMATION_SPEED),
                "jump": (self.heavy_weapon_jump_frames, HEAVY_JUMP_ANIMATION_SPEED),
                "dash": (self.heavy_weapon_dash_frames, HEAVY_DASH_ANIMATION_SPEED),
            },
            "shooter": {
                "idle": (self.shooter_weapon_idle_frames, SHOOTER_IDLE_ANIMATION_SPEED),
                "walk": (self.shooter_weapon_walk_frames, SHOOTER_WALK_ANIMATION_SPEED),
                "jump": (self.shooter_weapon_jump_frames, SHOOTER_JUMP_ANIMATION_SPEED),
                "dash": (self.shooter_weapon_dash_frames, SHOOTER_DASH_ANIMATION_SPEED),
            },
            "shield": {
                "idle": (self.shield_weapon_idle_frames, SHIELD_IDLE_ANIMATION_SPEED),
                "walk": (self.shield_weapon_walk_frames, SHIELD_WALK_ANIMATION_SPEED),
                "jump": (self.shield_weapon_jump_frames, SHIELD_JUMP_ANIMATION_SPEED),
                "dash": (self.shield_weapon_dash_frames, SHIELD_DASH_ANIMATION_SPEED),
            },
            "grapple": {
                "idle": (self.grapple_weapon_idle_frames, GRAPPLE_IDLE_ANIMATION_SPEED),
                "walk": (self.grapple_weapon_walk_frames, GRAPPLE_WALK_ANIMATION_SPEED),
                "jump": (self.grapple_weapon_jump_frames, GRAPPLE_JUMP_ANIMATION_SPEED),
                "dash": (self.grapple_weapon_dash_frames, GRAPPLE_DASH_ANIMATION_SPEED),
            },
        }
        return animation_map[weapon_prefix].get(visual_state, ([], 0.1))

    def play_idle_animation(self):

        if self.current_action == "idle" and self.current_animation and not self.current_animation.finished:
            return

        anim = self.animations.get("idle")
        if anim:
            anim.reset()
            anim.loop = True
            anim.playing = True
            anim.finished = False
            self.current_animation = anim
            self.current_action = "idle"
            self.is_attacking = False
            self.attack_has_hit = False
        else:
            self.current_animation = None
            self.current_action = "idle"

    def move_x(self, platforms):
        move_amount = int(round(self.vel_x))
        self.rect.x += move_amount

        for platform in platforms:
            if self._is_one_way_platform(platform):
                continue
            if self.rect.colliderect(platform):
                if move_amount > 0:
                    self.rect.right = platform.left
                    self.vel_x = 0
                elif move_amount < 0:
                    self.rect.left = platform.right
                    self.vel_x = 0

    def move_y(self, platforms):
        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if self._is_one_way_platform(platform):
                if self.drop_through_timer > 0:
                    continue
                if not self._should_land_on_one_way_platform(platform):
                    continue

                self.rect.bottom = platform.top
                self.vel_y = 0
                self.on_ground = True
                self.jump_count = 0
                break

            if self.rect.colliderect(platform):
                if self.vel_y >= 0:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                    break
                elif self.vel_y < 0:
                    self.rect.top = platform.bottom
                    self.vel_y = 0
                    break

    def _is_one_way_platform(self, platform):
        return platform.height <= 24

    def _should_land_on_one_way_platform(self, platform):
        return (
            self.vel_y >= 0
            and self.previous_bottom <= platform.top + 3
            and self.rect.bottom >= platform.top
            and self.rect.right > platform.left + 5
            and self.rect.left < platform.right - 5
        )

    def draw(self, screen, camera=None):
        if self.draw_attack_animation(screen, camera):
            return

        if not self.on_ground and self.draw_weapon_specific_state_animation("jump", screen, camera):
            return

        if self.is_dashing and self.draw_weapon_specific_state_animation("dash", screen, camera):
            return

        if self.draw_custom_weapon_movement_animation(screen, camera):
            return

        if self.current_animation:
            frame = self.current_animation.get_frame()
            if frame:
                draw_rect = self.rect
                if camera:
                    draw_rect = camera.apply_rect(self.rect)

                if self.facing == -1:
                    frame = pygame.transform.flip(frame, True, False)

                screen.blit(frame, (draw_rect.x, draw_rect.y))
                self.draw_light_weapon(screen, camera)

                if self.is_blocking:
                    self.draw_block_effect(screen, camera)
                if self.is_parrying:
                    self.draw_parry_effect(screen, camera)
                return

        if self.invincible_timer > 0:
            color = (255, 255, 255)
        else:
            color = (180, 220, 255)

        draw_rect = self.rect
        if camera:
            draw_rect = camera.apply_rect(self.rect)

        self.draw_kael_template(screen, draw_rect, color)
        self.draw_light_weapon(screen, camera)

        if self.is_blocking:
            self.draw_block_effect(screen, camera)

        if self.is_parrying:
            self.draw_parry_effect(screen, camera)

        if self.is_auto_grappling and self.auto_grapple_anchor is not None:
            start_pos = self.auto_grapple_anchor
            end_pos = self.rect.center
            if camera:
                start_pos = camera.apply_pos(start_pos)
                end_pos = camera.apply_pos(end_pos)
            pygame.draw.line(screen, (180, 90, 255), start_pos, end_pos, 3)

        if self.is_swinging and self.swing_anchor is not None:
            start_pos = self.swing_anchor
            end_pos = self.rect.center
            if camera:
                start_pos = camera.apply_pos(start_pos)
                end_pos = camera.apply_pos(end_pos)
            pygame.draw.line(screen, (130, 210, 255), start_pos, end_pos, 2)

    def draw_attack_animation(self, screen, camera=None):
        if not self.attack_animation_playing:
            return False

        if not self.attack_animation_frames:
            return False

        if DEBUG_ATTACK_ANIMATION:
            print(
                "[ATTACK DRAW CALL]",
                "index:", self.attack_animation_index,
                "frames:", len(self.attack_animation_frames),
            )

        frame_index = min(self.attack_animation_index, len(self.attack_animation_frames) - 1)
        frame = self.attack_animation_frames[frame_index]
        if self.attack_animation_flip:
            frame = pygame.transform.flip(frame, True, False)

        frame_rect = frame.get_rect()
        frame_rect.midbottom = self.rect.midbottom
        offset_x, offset_y = self.get_attack_animation_offset()
        if self.facing == -1:
            offset_x = -offset_x
        frame_rect.x += offset_x
        frame_rect.y += offset_y

        if camera:
            frame_rect = camera.apply_rect(frame_rect)

        if DEBUG_ATTACK_ANIMATION:
            print("[ATTACK DRAW FRAME]", "size:", frame.get_size(), "rect:", frame_rect)

        screen.blit(frame, frame_rect)
        return True

    def get_attack_animation_offset(self):
        if self.attack_animation_weapon_id == "light":
            return self.light_attack_offset_x, self.light_attack_offset_y
        if self.attack_animation_weapon_id == "heavy":
            return self.heavy_attack_offset_x, self.heavy_attack_offset_y
        if self.attack_animation_weapon_id == "shooter":
            return self.shooter_attack_offset_x, self.shooter_attack_offset_y
        if self.attack_animation_weapon_id == "shield":
            return self.shield_attack_offset_x, self.shield_attack_offset_y
        if self.attack_animation_weapon_id == "grapple":
            return self.grapple_attack_offset_x, self.grapple_attack_offset_y
        return self.light_attack_offset_x, self.light_attack_offset_y

    def draw_custom_weapon_frame(self, screen, frame, offset_x=0, offset_y=0, camera=None):
        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)

        frame_rect = frame.get_rect()
        frame_rect.midbottom = self.rect.midbottom
        frame_rect.x += offset_x
        frame_rect.y += offset_y

        if camera:
            frame_rect = camera.apply_rect(frame_rect)

        screen.blit(frame, frame_rect)

    def draw_custom_weapon_movement_animation(self, screen, camera=None):
        visual_state = self.get_visual_state()
        return self.draw_weapon_specific_state_animation(visual_state, screen, camera)

    def draw_weapon_specific_state_animation(self, visual_state, screen, camera=None):
        weapon_key = self.normalize_weapon_id(self.current_weapon_id)
        if weapon_key not in ("light", "heavy", "shooter", "shield", "grapple"):
            return False

        frames, frame_index, selected_name = self.get_custom_weapon_frames_for_state(weapon_key, visual_state)
        if DEBUG_JUMP_ANIMATION and visual_state == "jump" and weapon_key in ("shooter", "shield"):
            print("[JUMP ANIM]")
            print("current_weapon_id:", self.current_weapon_id)
            print("weapon_key:", weapon_key)
            print("selected jump frames:", selected_name)
            print("frame count:", len(frames) if frames else 0)

        if frames:
            frame = frames[min(frame_index, len(frames) - 1)]
            offset_x, offset_y = self.get_custom_weapon_movement_offset(weapon_key)
            if DEBUG_JUMP_ANIMATION and visual_state == "jump" and weapon_key in ("shooter", "shield"):
                print("[JUMP DRAW]")
                print("current weapon id:", self.current_weapon_id)
                print("normalized weapon key:", weapon_key)
                print("current movement state:", visual_state)
                print("frame size:", frame.get_size())
            self.draw_custom_weapon_frame(
                screen,
                frame,
                offset_x,
                offset_y,
                camera,
            )
            return True

        return False

    def get_custom_weapon_movement_offset(self, weapon_key):
        if weapon_key == "light":
            return self.light_anim_offset_x, self.light_anim_offset_y
        if weapon_key == "heavy":
            return self.heavy_anim_offset_x, self.heavy_anim_offset_y
        if weapon_key == "shooter":
            return self.shooter_anim_offset_x, self.shooter_anim_offset_y
        if weapon_key == "shield":
            return self.shield_anim_offset_x, self.shield_anim_offset_y
        if weapon_key == "grapple":
            return self.grapple_anim_offset_x, self.grapple_anim_offset_y
        return 0, 0

    def get_custom_weapon_frame(self, weapon_prefix, visual_state):
        frames, index, _ = self.get_custom_weapon_frames_for_state(weapon_prefix, visual_state)
        if frames:
            return frames[min(index, len(frames) - 1)]

        return None

    def get_custom_weapon_frames_for_state(self, weapon_prefix, visual_state):
        frame_map = {
            "light": {
                "dash": (self.light_weapon_dash_frames, self.light_dash_index, "light jump" if visual_state == "jump" else "light dash"),
                "jump": (self.light_weapon_jump_frames, self.light_jump_index, "light jump"),
                "walk": (self.light_weapon_walk_frames, self.light_walk_index, "light walk"),
                "idle": (self.light_weapon_idle_frames, self.light_idle_index, "light idle"),
            },
            "heavy": {
                "dash": (self.heavy_weapon_dash_frames, self.heavy_dash_index, "heavy dash"),
                "jump": (self.heavy_weapon_jump_frames, self.heavy_jump_index, "heavy jump"),
                "walk": (self.heavy_weapon_walk_frames, self.heavy_walk_index, "heavy walk"),
                "idle": (self.heavy_weapon_idle_frames, self.heavy_idle_index, "heavy idle"),
            },
            "shooter": {
                "dash": (self.shooter_weapon_dash_frames, self.shooter_dash_index, "shooter dash"),
                "jump": (self.shooter_weapon_jump_frames, self.shooter_jump_index, "shooter jump"),
                "walk": (self.shooter_weapon_walk_frames, self.shooter_walk_index, "shooter walk"),
                "idle": (self.shooter_weapon_idle_frames, self.shooter_idle_index, "shooter idle"),
            },
            "shield": {
                "dash": (self.shield_weapon_dash_frames, self.shield_dash_index, "shield dash"),
                "jump": (self.shield_weapon_jump_frames, self.shield_jump_index, "shield jump"),
                "walk": (self.shield_weapon_walk_frames, self.shield_walk_index, "shield walk"),
                "idle": (self.shield_weapon_idle_frames, self.shield_idle_index, "shield idle"),
            },
            "grapple": {
                "dash": (self.grapple_weapon_dash_frames, self.grapple_dash_index, "grapple dash"),
                "jump": (self.grapple_weapon_jump_frames, self.grapple_jump_index, "grapple jump"),
                "walk": (self.grapple_weapon_walk_frames, self.grapple_walk_index, "grapple walk"),
                "idle": (self.grapple_weapon_idle_frames, self.grapple_idle_index, "grapple idle"),
            },
        }
        return frame_map[weapon_prefix].get(visual_state, ([], 0, f"{weapon_prefix} {visual_state} missing"))

    def draw_light_weapon(self, screen, camera=None):
        if self.current_weapon_id != "light_weapon":
            return

        world_x = self.rect.centerx + 10 if self.facing == 1 else self.rect.centerx - 40
        world_y = self.rect.centery - 5
        draw_pos = (world_x, world_y)
        if camera:
            draw_pos = camera.apply_pos(draw_pos)

        if self.light_weapon_image is None:
            self.draw_light_weapon_fallback(screen, draw_pos)
            return

        weapon_image = self.light_weapon_image
        if self.facing == -1:
            weapon_image = pygame.transform.flip(weapon_image, True, False)

        angle = 0
        if self.is_attacking and self.attack_timer > 0 and self.attack_visual_duration > 0:
            progress = 1 - (self.attack_timer / self.attack_visual_duration)
            progress = max(0, min(1, progress))
            if self.facing == 1:
                angle = -35 + (70 * progress)
            else:
                angle = 35 - (70 * progress)

        base_rect = weapon_image.get_rect(topleft=draw_pos)
        weapon_image = pygame.transform.rotate(weapon_image, angle)
        weapon_rect = weapon_image.get_rect(center=base_rect.center)
        screen.blit(weapon_image, weapon_rect)

    def draw_light_weapon_fallback(self, screen, draw_pos):
        x, y = draw_pos
        moon_core = (150, 220, 255)
        moon_glow = (90, 170, 230)
        blade_rect = pygame.Rect(x, y + 2, 30, 5)

        if self.facing == -1:
            blade_rect.right = x + 30

        if self.is_attacking and self.attack_timer > 0 and self.attack_visual_duration > 0:
            progress = 1 - (self.attack_timer / self.attack_visual_duration)
            progress = max(0, min(1, progress))
            swing_offset = int(10 * progress)
            blade_rect.y += swing_offset if self.facing == 1 else -swing_offset

        pygame.draw.rect(screen, moon_core, blade_rect)
        pygame.draw.rect(screen, moon_glow, blade_rect, 2)

    def draw_kael_template(self, screen, draw_rect, state_color):
        """
        Draws Kael as a simple pixel-style character template.
        This is only visual. It does not affect collision or gameplay.
        """

        x = draw_rect.x
        y = draw_rect.y
        w = draw_rect.width
        h = draw_rect.height

        # Main palette
        armor_dark = (30, 34, 48)
        armor_mid = (58, 64, 86)
        armor_light = (105, 116, 145)
        moon_core = (150, 220, 255)
        moon_glow = (90, 170, 230)
        shadow = (12, 14, 22)

        # Special state colors
        if self.invincible_timer > 0:
            moon_core = (255, 255, 255)
            moon_glow = (220, 240, 255)
        elif self.is_dashing:
            moon_core = (170, 240, 255)
            moon_glow = (80, 210, 255)

        # Small dash afterimage / glow
        if self.is_dashing:
            glow_rect = pygame.Rect(x - self.facing * 10, y + 12, w, h - 12)
            pygame.draw.rect(screen, (60, 120, 180), glow_rect, 1)

        # Crown reactor glow above head
        crown_x = x + w // 2
        pygame.draw.rect(screen, moon_glow, (crown_x - 7, y - 8, 14, 3))
        pygame.draw.rect(screen, moon_core, (crown_x - 3, y - 13, 6, 6))

        # Head
        head_rect = pygame.Rect(x + 13, y + 4, 22, 18)
        pygame.draw.rect(screen, armor_mid, head_rect)
        pygame.draw.rect(screen, armor_light, (head_rect.x + 3, head_rect.y + 3, 16, 3))

        # Face shadow / visor
        visor_rect = pygame.Rect(head_rect.x + 4, head_rect.y + 9, 14, 4)
        pygame.draw.rect(screen, shadow, visor_rect)

        # Body armor
        body_rect = pygame.Rect(x + 10, y + 24, 28, 25)
        pygame.draw.rect(screen, armor_dark, body_rect)
        pygame.draw.rect(screen, armor_mid, (body_rect.x + 3, body_rect.y + 3, 22, 18))

        # Chest moon core
        core_rect = pygame.Rect(x + 20, y + 31, 8, 8)
        pygame.draw.rect(screen, moon_glow, (core_rect.x - 2, core_rect.y - 2, 12, 12), 1)
        pygame.draw.rect(screen, moon_core, core_rect)

        # Shoulders
        pygame.draw.rect(screen, armor_light, (x + 5, y + 25, 8, 10))
        pygame.draw.rect(screen, armor_light, (x + 35, y + 25, 8, 10))

        # Arms
        if self.facing == 1:
            front_arm = pygame.Rect(x + 37, y + 35, 7, 18)
            back_arm = pygame.Rect(x + 4, y + 35, 6, 15)
        else:
            front_arm = pygame.Rect(x + 4, y + 35, 7, 18)
            back_arm = pygame.Rect(x + 38, y + 35, 6, 15)

        pygame.draw.rect(screen, armor_mid, back_arm)
        pygame.draw.rect(screen, armor_light, front_arm)

        # Legs
        left_leg = pygame.Rect(x + 12, y + 49, 9, 15)
        right_leg = pygame.Rect(x + 27, y + 49, 9, 15)
        pygame.draw.rect(screen, armor_dark, left_leg)
        pygame.draw.rect(screen, armor_dark, right_leg)
        pygame.draw.rect(screen, armor_light, (left_leg.x, left_leg.bottom - 4, 10, 4))
        pygame.draw.rect(screen, armor_light, (right_leg.x, right_leg.bottom - 4, 10, 4))

        # Weapon hint / small blade glow when attacking
        if self.is_attacking and not (
            self.current_weapon_id == "light_weapon" and self.light_weapon_image is not None
        ):
            if self.facing == 1:
                blade_rect = pygame.Rect(x + w - 2, y + 28, 28, 5)
            else:
                blade_rect = pygame.Rect(x - 26, y + 28, 28, 5)

            pygame.draw.rect(screen, moon_core, blade_rect)
            pygame.draw.rect(screen, moon_glow, blade_rect, 2)

        # Thin outline
        pygame.draw.rect(screen, shadow, draw_rect, 1)

    def draw_block_effect(self, screen, camera=None):
        if self.facing == 1:
            shield_rect = pygame.Rect(self.rect.right, self.rect.y + 8, 10, self.rect.height - 16)
        else:
            shield_rect = pygame.Rect(self.rect.left - 10, self.rect.y + 8, 10, self.rect.height - 16)

        if camera:
            shield_rect = camera.apply_rect(shield_rect)

        pygame.draw.rect(screen, (80, 170, 255), shield_rect, 2)

    def draw_parry_effect(self, screen, camera=None):
        if self.facing == 1:
            parry_rect = pygame.Rect(self.rect.right, self.rect.y, 20, self.rect.height)
        else:
            parry_rect = pygame.Rect(self.rect.left - 20, self.rect.y, 20, self.rect.height)

        if camera:
            parry_rect = camera.apply_rect(parry_rect)

        pygame.draw.rect(screen, (255, 255, 120), parry_rect, 2)

    def load_animation(self, animation_name, json_path, png_path, scale=1):
        """Load an animation"""
        json_path = PROJECT_ROOT / json_path
        png_path = PROJECT_ROOT / png_path
        if not json_path.exists() or not png_path.exists():
            return None

        anim = load_libresprite_animation(json_path, png_path, scale)
        if anim:
            self.animations[animation_name] = anim
            print(f"Loaded animation: {animation_name}")
        return anim

    def load_all_animations(self):
        """Load all animations"""
        # Idle animation (looping)
        self.load_animation(
            "idle",
            "assets/animations/idle_withoutweapon.json",
            "assets/animations/idle_withoutweapon.png",
            scale=0.75
        )

        # Walk animation (looping)
        self.load_animation(
            "walk",
            "assets/animations/walk_withoutweapon.json",
            "assets/animations/walk_withoutweapon.png",
            scale=0.75
        )

        # # Walk right animation (looping)
        # self.load_animation(
        #     "walk_right",
        #     "assets/animations/rightwalk_withoutweapon.json",
        #     "assets/animations/rightwalk_withoutweapon.png",
        #     scale=0.75
        # )

        # # Walk left animation (looping)
        # self.load_animation(
        #     "walk_left",
        #     "assets/animations/leftwalk_withoutweapon.json",
        #     "assets/animations/leftwalk_withoutweapon.png",
        #     scale=0.75
        # )

        # Jump animation (4 frames, non-looping, frame-controlled)
        self.load_animation(
            "jump",
            "assets/animations/jump_withoutweapon.json",
            "assets/animations/jump_withoutweapon.png",
            scale=0.75
        )

        # Dash animation (4 frames, non-looping)
        self.load_animation(
            "dash",
            "assets/animations/dash_withoutweapon.json",
            "assets/animations/dash_withoutweapon.png",
            scale=0.75
        )

        # Normal attack animation
        self.load_animation(
            "attack_na1",
            "assets/animations/NA1.json",
            "assets/animations/NA1.png",
            scale=0.75
        )
