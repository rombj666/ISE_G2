import math
from pathlib import Path

import pygame
from PIL import Image, ImageSequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAGE_ASSET_DIR = PROJECT_ROOT / "assets" / "enemies" / "mage"

DEBUG_MAGE_AI = False
MAGE_HP = 50
MAGE_SPEED = 1.0
MAGE_DETECT_RANGE = 360
MAGE_ATTACK_RANGE = 240
MAGE_FIRE_DAMAGE = 12
MAGE_ATTACK_COOLDOWN = 2.0
MAGE_SHIELD_RADIUS = 34
MAGE_VISUAL_SCALE = 1.35
MAGE_DRAW_OFFSET_Y = 20
MAGE_ANIMATION_SPEED = 0.1
MAGE_PATROL_RADIUS = 100
MAGE_ATTACK_ACTIVE_FRAME = 3
MAGE_BODY_SIZE = (48, 64)
MAGE_DRAW_SIZE = (
    round(96 * MAGE_VISUAL_SCALE),
    round(96 * MAGE_VISUAL_SCALE),
)
MAGE_EFFECT_FRAME_COUNT = 6
MAGE_FIRE_ARC_DRAW_SIZE = (230, 170)
MAGE_FIRE_HIT_DRAW_SIZE = (140, 140)

MAGE_ANIMATIONS = None
MAGE_EFFECTS = None


def _surface_from_rgba_image(image):
    surface = pygame.image.fromstring(image.tobytes(), image.size, "RGBA")
    return surface.convert_alpha()


def _transparentize_generated_background(image):
    image = image.convert("RGBA")
    alpha = image.getchannel("A")
    if alpha.getextrema() != (255, 255):
        return image

    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            red, green, blue, current_alpha = pixels[x, y]
            color_spread = max(red, green, blue) - min(red, green, blue)
            is_near_white_background = red >= 220 and green >= 220 and blue >= 220 and color_spread <= 24
            if is_near_white_background:
                pixels[x, y] = (red, green, blue, 0)
            else:
                pixels[x, y] = (red, green, blue, current_alpha)
    return image


def _visible_bounds(surface):
    rect = surface.get_bounding_rect()
    if rect.width <= 0 or rect.height <= 0:
        return surface.get_rect()
    return rect


def _trim_and_scale_frame(frame, target_size):
    visible_rect = _visible_bounds(frame)
    trimmed = pygame.Surface(visible_rect.size, pygame.SRCALPHA)
    trimmed.blit(frame, (0, 0), visible_rect)
    if target_size is not None and trimmed.get_size() != target_size:
        trimmed = pygame.transform.smoothscale(trimmed, target_size)
    return trimmed.convert_alpha()


def _first_existing_path(label, paths):
    for path in paths:
        if path.exists():
            return path

    print(f"[MAGE ASSET WARNING] {label} failed to load. Tried paths:")
    for path in paths:
        print("  ", path)
    return paths[0]


def load_mage_gif_frames(path, target_size=MAGE_DRAW_SIZE):
    if not path.exists():
        print("[MAGE ASSET WARNING] Missing GIF:", path)
        return []

    frames = []
    try:
        with Image.open(path) as image:
            for frame in ImageSequence.Iterator(image):
                rgba = frame.convert("RGBA")
                surface = _surface_from_rgba_image(rgba)
                if target_size is not None and surface.get_size() != target_size:
                    surface = pygame.transform.smoothscale(surface, target_size).convert_alpha()
                frames.append(surface)
    except Exception as error:
        print("[MAGE ASSET WARNING] GIF failed to load:", path, error)
        return []

    return frames


def load_effect_sheet(path, frame_count=MAGE_EFFECT_FRAME_COUNT, target_size=None):
    if not path.exists():
        print("[MAGE EFFECT WARNING] Missing effect sheet:", path)
        return []

    try:
        with Image.open(path) as image:
            sheet_image = _transparentize_generated_background(image)
    except Exception as error:
        print("[MAGE EFFECT WARNING] Effect sheet failed to load:", path, error)
        return []

    sheet_width, sheet_height = sheet_image.size
    frame_width = sheet_width // frame_count
    if frame_width <= 0:
        print("[MAGE EFFECT WARNING] Effect sheet is too narrow for frames:", path, sheet_image.size)
        return []

    if sheet_width % frame_count != 0:
        print(
            "[MAGE EFFECT WARNING] Sheet width is not evenly divisible by frame count:",
            path,
            "width:",
            sheet_width,
            "frame count:",
            frame_count,
        )

    frames = []
    for index in range(frame_count):
        left = index * frame_width
        right = left + frame_width
        frame_image = sheet_image.crop((left, 0, right, sheet_height))
        frame = _surface_from_rgba_image(frame_image)
        frames.append(_trim_and_scale_frame(frame, target_size))

    return frames


def get_mage_animations():
    global MAGE_ANIMATIONS
    if MAGE_ANIMATIONS is not None:
        return MAGE_ANIMATIONS

    idle_east_path = _first_existing_path(
        "mage idle east gif",
        [
            MAGE_ASSET_DIR / "idle_east.gif",
            MAGE_ASSET_DIR / "remain_same_breathing-idle_east.gif",
        ],
    )
    idle_west_path = _first_existing_path(
        "mage idle west gif",
        [
            MAGE_ASSET_DIR / "idle_west.gif",
            MAGE_ASSET_DIR / "remain_same_breathing-idle_west.gif",
        ],
    )
    walk_east_path = _first_existing_path(
        "mage walk east gif",
        [
            MAGE_ASSET_DIR / "walk_east.gif",
            MAGE_ASSET_DIR / "remain_same_walking-6-frames_east.gif",
        ],
    )
    walk_west_path = _first_existing_path(
        "mage walk west gif",
        [
            MAGE_ASSET_DIR / "walk_west.gif",
            MAGE_ASSET_DIR / "remain_same_walking-6-frames_west.gif",
        ],
    )
    attack_east_path = _first_existing_path(
        "mage attack east gif",
        [
            MAGE_ASSET_DIR / "attack_east.gif",
            MAGE_ASSET_DIR / "remain_same_custom-Create_a_clear_and_dramatic_ma_east.gif",
        ],
    )
    attack_west_path = _first_existing_path(
        "mage attack west gif",
        [
            MAGE_ASSET_DIR / "attack_west.gif",
            MAGE_ASSET_DIR / "remain_same_custom-Create_a_clear_and_dramatic_ma_west.gif",
        ],
    )

    idle_frames_east = load_mage_gif_frames(idle_east_path)
    idle_frames_west = load_mage_gif_frames(idle_west_path)
    walk_frames_east = load_mage_gif_frames(walk_east_path)
    walk_frames_west = load_mage_gif_frames(walk_west_path)
    attack_frames_east = load_mage_gif_frames(attack_east_path)
    attack_frames_west = load_mage_gif_frames(attack_west_path)

    print("[MAGE ASSET DEBUG]")
    print("Mage folder:", MAGE_ASSET_DIR)
    print("Mage idle east path:", idle_east_path)
    print("Mage idle west path:", idle_west_path)
    print("Mage walk east path:", walk_east_path)
    print("Mage walk west path:", walk_west_path)
    print("Mage attack east path:", attack_east_path)
    print("Mage attack west path:", attack_west_path)
    print("mage idle frame count:", len(idle_frames_east))
    print("mage walk frame count:", len(walk_frames_east))
    print("mage attack frame count:", len(attack_frames_east))

    MAGE_ANIMATIONS = {
        "idle": {"east": idle_frames_east, "west": idle_frames_west},
        "walk": {"east": walk_frames_east, "west": walk_frames_west},
        "attack": {"east": attack_frames_east, "west": attack_frames_west},
    }
    return MAGE_ANIMATIONS


def get_mage_effects():
    global MAGE_EFFECTS
    if MAGE_EFFECTS is not None:
        return MAGE_EFFECTS

    fire_arc_path = MAGE_ASSET_DIR / "mage_fire_arc_attack.png"
    fire_hit_path = MAGE_ASSET_DIR / "mage_fire_hit.png"
    fire_arc_frames = load_effect_sheet(fire_arc_path, MAGE_EFFECT_FRAME_COUNT, MAGE_FIRE_ARC_DRAW_SIZE)
    fire_hit_frames = load_effect_sheet(fire_hit_path, MAGE_EFFECT_FRAME_COUNT, MAGE_FIRE_HIT_DRAW_SIZE)

    print("[MAGE EFFECT DEBUG]")
    print("Mage shield effect path: coded pygame circle, no PNG loaded")
    print("mage shield frame count: 0")
    print("Mage fire attack effect path:", fire_arc_path)
    print("mage fire attack frame count:", len(fire_arc_frames))
    print("Mage fire hit effect path:", fire_hit_path)
    print("mage fire hit frame count:", len(fire_hit_frames))

    MAGE_EFFECTS = {
        "fire_arc": fire_arc_frames,
        "fire_hit": fire_hit_frames,
    }
    return MAGE_EFFECTS


class MageTimedEffect:
    def __init__(self, frames, center, frame_time=0.08, facing=1, flip_with_facing=False):
        self.frames = frames
        self.center = center
        self.frame_time = frame_time
        self.facing = facing
        self.flip_with_facing = flip_with_facing
        self.timer = 0
        self.frame_index = 0
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return

        if not self.frames:
            self.alive = False
            return

        self.timer += dt
        if self.timer >= self.frame_time:
            self.timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.alive = False

    def draw(self, screen, camera=None):
        if not self.alive or not self.frames:
            return

        frame = self.frames[min(self.frame_index, len(self.frames) - 1)]
        if self.flip_with_facing and self.facing < 0:
            frame = pygame.transform.flip(frame, True, False)
        rect = frame.get_rect(center=self.center)
        draw_rect = camera.apply_rect(rect) if camera else rect
        screen.blit(frame, draw_rect)


class MageEnemy:
    def __init__(
        self,
        x,
        y,
        mode="static",
        patrol_left=MAGE_PATROL_RADIUS,
        patrol_right=MAGE_PATROL_RADIUS,
        index=None,
        debug_ai=False,
    ):
        self.rect = pygame.Rect(0, 0, *MAGE_BODY_SIZE)
        self.rect.midbottom = (x, y)
        self.position_x = float(self.rect.x)
        self.spawn_x = x
        self.spawn_y = y
        self.mode = mode
        self.index = index
        self.debug_ai = debug_ai
        self.patrol_min_x = x - patrol_left
        self.patrol_max_x = x + patrol_right

        self.max_hp = MAGE_HP
        self.current_hp = self.max_hp
        self.damage = MAGE_FIRE_DAMAGE
        self.alive = True
        self.active = True
        self.dropped_coins = False
        self.hurt_timer = 0
        self.stunned_timer = 0
        self.frozen_timer = 0
        self.frozen = False
        self.freeze_timer = 0
        self.being_pulled = False
        self.pull_target_x = None

        self.state = "idle"
        self.facing = -1
        self.direction = "west"
        self.patrol_direction = -1
        self.velocity_x = 0
        self.vel_x = 0
        self.frame_index = 0
        self.animation_timer = 0

        self.is_attacking = False
        self.attack_cooldown_timer = 0
        self.attack_has_hit = False
        self.has_hit_player_this_attack = False
        self.attack_frame_index = 0
        self.attack_is_active = False
        self.attack_has_spawned_fire = False

        self.shield_active = True
        self.shield_hits_remaining = 1
        self.static_debug_frame = 0

        self.fire_arc_effects = []
        self.fire_hit_effects = []
        self.animations = get_mage_animations()
        self.effects = get_mage_effects()

    def take_damage(self, amount):
        if not self.active or not self.alive:
            return

        damage = amount
        if self.shield_active and self.shield_hits_remaining > 0:
            self.shield_hits_remaining -= 1
            self.shield_active = False
            print("[MAGE SHIELD BLOCKED HIT]", getattr(self, "enemy_id", None))
            return

        self.current_hp -= damage
        self.hurt_timer = 0.12
        print(f"Mage took {damage} damage, HP: {self.current_hp}")

        if self.current_hp <= 0:
            self.die()

    def die(self):
        self.current_hp = 0
        self.alive = False
        self.is_attacking = False

    def stun(self, duration):
        if self.active and self.alive:
            self.stunned_timer = max(self.stunned_timer, duration)
            self.is_attacking = False
            self.state = "idle"

    def freeze(self, duration):
        if self.active and self.alive:
            self.frozen_timer = max(self.frozen_timer, duration)
            self.freeze_timer = self.frozen_timer
            self.frozen = True
            self.is_attacking = False
            self.state = "idle"

    def mark_executable(self, duration):
        return

    def start_pull_to_player(self, player):
        if not self.active or not self.alive:
            return
        if self.mode == "static":
            return

        self.being_pulled = True
        self.stunned_timer = max(self.stunned_timer, 2.0)
        if player.facing == 1:
            self.pull_target_x = player.rect.right + 20
        else:
            self.pull_target_x = player.rect.left - self.rect.width - 20

    def update(self, dt, player=None, platforms=None):
        if not self.active or not self.alive:
            return

        platforms = platforms or []
        self._update_timers(dt)
        self._update_effects(dt)
        self._print_static_check()

        if self.frozen_timer > 0:
            self.frozen_timer -= dt
            self.freeze_timer = self.frozen_timer
            self.frozen = True
            self._animate(dt)
            return
        self.frozen = False
        self.freeze_timer = 0

        if self.stunned_timer > 0:
            self.stunned_timer -= dt
            self._animate(dt)
            return

        if self.being_pulled:
            self._update_pull()
            self._animate(dt)
            return

        if self.is_attacking:
            self._update_attack(dt, player)
            return

        if player is None or player.is_dead:
            self._idle_or_patrol(dt, platforms)
            return

        distance = self._distance_to_player(player)
        self._print_ai_debug(player, distance)
        if self.mode == "static":
            self._update_static_behavior(dt, player, distance)
            return

        if distance <= MAGE_DETECT_RANGE:
            self._face_player(player)

            if distance <= MAGE_ATTACK_RANGE and self.attack_cooldown_timer <= 0:
                self._start_attack(player)
            else:
                self._keep_mid_range(player, platforms, dt, distance)
            return

        self._idle_or_patrol(dt, platforms)

    def _update_timers(self, dt):
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

    def _update_effects(self, dt):
        for effect in self.fire_arc_effects:
            effect.update(dt)
        for effect in self.fire_hit_effects:
            effect.update(dt)
        self.fire_arc_effects = [effect for effect in self.fire_arc_effects if effect.alive]
        self.fire_hit_effects = [effect for effect in self.fire_hit_effects if effect.alive]

    def _distance_to_player(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        return math.hypot(dx, dy)

    def _face_player(self, player):
        self.facing = 1 if player.rect.centerx >= self.rect.centerx else -1
        self.direction = "east" if self.facing > 0 else "west"

    def _start_attack(self, player):
        self.is_attacking = True
        self.state = "attack"
        self.velocity_x = 0
        self.vel_x = 0
        self.frame_index = 0
        self.animation_timer = 0
        self.attack_frame_index = 0
        self.attack_is_active = False
        self.attack_has_hit = False
        self.has_hit_player_this_attack = False
        self.attack_has_spawned_fire = False
        self._face_player(player)
        self._spawn_fire_arc()
        print("[MAGE ATTACK START]")
        print("Mage:", self.rect.center)
        print("Player:", player.rect.center)
        print("Facing:", self.facing)

    def _update_attack(self, dt, player):
        self.state = "attack"
        self.velocity_x = 0
        self.vel_x = 0
        frames = self._current_frames()
        if not frames:
            self._apply_fire_hit(player)
            self._finish_attack()
            return

        self.animation_timer += dt
        if self.animation_timer >= MAGE_ANIMATION_SPEED:
            self.animation_timer = 0
            self.frame_index += 1

        self.attack_frame_index = self.frame_index
        self.attack_is_active = self.attack_frame_index >= MAGE_ATTACK_ACTIVE_FRAME
        if self.attack_is_active and not self.has_hit_player_this_attack:
            self._apply_fire_hit(player)

        if self.frame_index >= len(frames):
            self._finish_attack()

    def _finish_attack(self):
        self.is_attacking = False
        self.attack_cooldown_timer = MAGE_ATTACK_COOLDOWN
        self.attack_is_active = False
        self.state = "idle"
        self.frame_index = 0

    def _spawn_fire_arc(self):
        frames = self.effects.get("fire_arc", [])
        if not frames:
            return

        center_x = self.rect.right + 70 if self.facing > 0 else self.rect.left - 70
        center = (center_x, self.rect.centery - 10)
        self.fire_arc_effects.append(
            MageTimedEffect(frames, center, frame_time=0.08, facing=self.facing, flip_with_facing=True)
        )

    def _get_fire_hitbox(self):
        if self.facing > 0:
            fire_rect = pygame.Rect(self.rect.right - 10, self.rect.centery - 70, 160, 120)
        else:
            fire_rect = pygame.Rect(self.rect.left - 150, self.rect.centery - 70, 160, 120)
        print("[MAGE FIRE HITBOX]", fire_rect)
        return fire_rect

    def get_attack_hitbox(self):
        return self._get_fire_hitbox()

    def _apply_fire_hit(self, player):
        if player is None or self.has_hit_player_this_attack:
            return

        fire_rect = self._get_fire_hitbox()
        if not fire_rect.colliderect(player.rect):
            return

        player.take_damage(MAGE_FIRE_DAMAGE)
        self.has_hit_player_this_attack = True
        self.attack_has_hit = True
        self._spawn_fire_hit(player.rect.center)
        print("[MAGE HIT PLAYER]", MAGE_FIRE_DAMAGE)

    def _spawn_fire_hit(self, center):
        frames = self.effects.get("fire_hit", [])
        if frames:
            self.fire_hit_effects.append(MageTimedEffect(frames, center, frame_time=0.08))

    def _keep_mid_range(self, player, platforms, dt, distance):
        if self.mode == "static":
            self.velocity_x = 0
            self.vel_x = 0
            self.state = "idle"
            self._animate(dt)
            return

        if distance < MAGE_ATTACK_RANGE * 0.55:
            direction = -1 if player.rect.centerx > self.rect.centerx else 1
            self._move_horizontal(direction, platforms, dt)
            return

        self.velocity_x = 0
        self.vel_x = 0
        self.state = "idle"
        self._animate(dt)

    def _update_static_behavior(self, dt, player, distance):
        self.rect.midbottom = (self.spawn_x, self.spawn_y)
        self.position_x = float(self.rect.x)
        self.velocity_x = 0
        self.vel_x = 0

        if distance <= MAGE_DETECT_RANGE:
            self._face_player(player)

            if distance <= MAGE_ATTACK_RANGE and self.attack_cooldown_timer <= 0:
                self._start_attack(player)
                return

        self.state = "idle"
        self._animate(dt)

    def _idle_or_patrol(self, dt, platforms):
        if self.mode == "static":
            self.rect.midbottom = (self.spawn_x, self.spawn_y)
            self.position_x = float(self.rect.x)
            self.velocity_x = 0
            self.vel_x = 0
            self.state = "idle"
            self._animate(dt)
            return

        self._patrol(dt, platforms)

    def _patrol(self, dt, platforms):
        if self.rect.centerx <= self.patrol_min_x:
            self.patrol_direction = 1
        elif self.rect.centerx >= self.patrol_max_x:
            self.patrol_direction = -1

        moved = self._move_horizontal(self.patrol_direction, platforms, dt)
        if not moved:
            self.patrol_direction *= -1

    def _move_horizontal(self, direction, platforms, dt):
        self.facing = direction
        self.direction = "east" if self.facing > 0 else "west"
        self.velocity_x = direction * MAGE_SPEED
        self.vel_x = self.velocity_x
        self.state = "walk"

        next_rect = self.rect.copy()
        next_rect.x = round(self.position_x + self.velocity_x)

        if next_rect.centerx < self.patrol_min_x:
            next_rect.centerx = round(self.patrol_min_x)
            self.patrol_direction = 1
        elif next_rect.centerx > self.patrol_max_x:
            next_rect.centerx = round(self.patrol_max_x)
            self.patrol_direction = -1
        elif not self._has_ground_ahead(next_rect, platforms) or self._hits_wall(next_rect, platforms):
            self.velocity_x = 0
            self.vel_x = 0
            self._animate(dt)
            return False

        self.rect.x = next_rect.x
        self.position_x = float(self.rect.x)
        self._animate(dt)
        return True

    def _has_ground_ahead(self, next_rect, platforms):
        if not platforms:
            return True
        probe_x = next_rect.right + 4 if self.facing > 0 else next_rect.left - 4
        ground_probe = pygame.Rect(probe_x, next_rect.bottom, 6, 12)
        return any(ground_probe.colliderect(platform) for platform in platforms)

    def _hits_wall(self, next_rect, platforms):
        wall_probe = pygame.Rect(next_rect.x, next_rect.y + 8, next_rect.width, next_rect.height - 16)
        for platform in platforms:
            if wall_probe.colliderect(platform) and platform.top < self.rect.bottom - 8:
                return True
        return False

    def _update_pull(self):
        if self.pull_target_x is None:
            self.being_pulled = False
            return

        distance_x = self.pull_target_x - self.rect.x
        if abs(distance_x) <= 12:
            self.rect.x = self.pull_target_x
            self.position_x = float(self.rect.x)
            self.being_pulled = False
            self.stunned_timer = max(self.stunned_timer, 0.5)
            return

        self.rect.x += 12 if distance_x > 0 else -12
        self.position_x = float(self.rect.x)

    def _current_frames(self):
        frames = self.animations.get(self.state, {}).get(self.direction, [])
        if not frames and self.state != "idle":
            frames = self.animations.get("idle", {}).get(self.direction, [])
        return frames

    def _animate(self, dt):
        frames = self._current_frames()
        if not frames:
            return

        self.animation_timer += dt
        if self.animation_timer >= MAGE_ANIMATION_SPEED:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)

    def _print_ai_debug(self, player, distance):
        if not (DEBUG_MAGE_AI or self.debug_ai):
            return

        print("[MAGE AI]")
        print("state:", self.state)
        print("mage:", self.rect.center)
        print("player:", player.rect.center)
        print("distance:", distance)
        print("attack cooldown:", self.attack_cooldown_timer)
        print("shield active:", self.shield_active)

    def _print_static_check(self):
        if self.mode != "static":
            return

        self.static_debug_frame += 1
        if self.static_debug_frame % 120 == 0:
            print("[MAGE STATIC CHECK]", self.rect.center, "velocity_x:", self.velocity_x, "state:", self.state)

    def draw(self, screen, camera=None):
        if not self.active or not self.alive:
            return

        self._draw_shield(screen, camera)
        self._draw_body(screen, camera)
        self._draw_effects(screen, camera)
        self._draw_hp_bar(screen, camera)

    def _draw_shield(self, screen, camera):
        if not self.shield_active:
            return

        shield_radius = MAGE_SHIELD_RADIUS
        shield_center_rect = pygame.Rect(0, 0, 1, 1)
        shield_center_rect.center = self.rect.center
        if camera:
            shield_center_rect = camera.apply_rect(shield_center_rect)
        shield_center = shield_center_rect.center

        padding = 4
        shield_surface = pygame.Surface(
            (shield_radius * 2 + padding * 2, shield_radius * 2 + padding * 2),
            pygame.SRCALPHA,
        )
        local_center = (shield_radius + padding, shield_radius + padding)
        pygame.draw.circle(shield_surface, (40, 160, 255, 60), local_center, shield_radius)
        pygame.draw.circle(shield_surface, (80, 210, 255, 180), local_center, shield_radius, 2)
        screen.blit(
            shield_surface,
            (shield_center[0] - shield_radius - padding, shield_center[1] - shield_radius - padding),
        )

    def _draw_body(self, screen, camera):
        frames = self._current_frames()
        if frames:
            frame = frames[min(self.frame_index, len(frames) - 1)]
            visual_rect = frame.get_rect(
                midbottom=(self.rect.centerx, self.rect.bottom + MAGE_DRAW_OFFSET_Y)
            )
            draw_rect = camera.apply_rect(visual_rect) if camera else visual_rect
            if self.hurt_timer > 0:
                tinted = frame.copy()
                tinted.fill((255, 120, 120, 80), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(tinted, draw_rect)
            else:
                screen.blit(frame, draw_rect)
            return

        draw_rect = camera.apply_rect(self.rect) if camera else self.rect
        pygame.draw.rect(screen, (120, 60, 190), draw_rect)

    def _draw_effects(self, screen, camera):
        for effect in self.fire_arc_effects:
            effect.draw(screen, camera)
        for effect in self.fire_hit_effects:
            effect.draw(screen, camera)

    def _draw_hp_bar(self, screen, camera):
        bar_width = self.rect.width
        bar_height = 5
        bar_rect = pygame.Rect(self.rect.x, self.rect.y - 12, bar_width, bar_height)
        fill_rect = bar_rect.copy()
        fill_rect.width = round(bar_width * max(0, self.current_hp) / self.max_hp)

        if camera:
            bar_rect = camera.apply_rect(bar_rect)
            fill_rect = camera.apply_rect(fill_rect)

        pygame.draw.rect(screen, (35, 18, 55), bar_rect)
        pygame.draw.rect(screen, (180, 90, 255), fill_rect)
