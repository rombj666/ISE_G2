import math
from pathlib import Path

import pygame
from PIL import Image, ImageSequence

from settings import (
    ARCHER_DRAW_OFFSET_Y,
    ARCHER_HP_BAR_OFFSET_Y,
    ARCHER_SPAWN_OFFSET_Y,
    ARCHER_VISUAL_SCALE,
    SHOOTER_BULLET_SPEED,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARCHER_ASSET_DIR = PROJECT_ROOT / "assets" / "enemies" / "archer"

ARCHER_HP = 40
ARCHER_DETECTION_RANGE = 450
ARCHER_SHOOTING_RANGE = ARCHER_DETECTION_RANGE
ARCHER_PATROL_RADIUS = 120
ARCHER_WALK_SPEED = 1.3
ARCHER_ATTACK_COOLDOWN = 1.4
ARCHER_ARROW_SPEED = SHOOTER_BULLET_SPEED
ARCHER_ARROW_DAMAGE = 10
ARCHER_ARROW_MAX_DISTANCE = 900
ARCHER_ANIMATION_SPEED = 0.1
ARCHER_ATTACK_RELEASE_RATIO = 0.5
ARCHER_BODY_SIZE = (42, 72)
ARCHER_DRAW_SIZE = (
    round(96 * ARCHER_VISUAL_SCALE),
    round(96 * ARCHER_VISUAL_SCALE),
)

ARCHER_ANIMATIONS = None


def load_gif_frames(path, target_size=ARCHER_DRAW_SIZE):
    print("Archer animation path:", path)
    print("Archer animation exists:", path.exists())

    if not path.exists():
        return []

    frames = []
    with Image.open(path) as image:
        for frame in ImageSequence.Iterator(image):
            rgba = frame.convert("RGBA")
            surface = pygame.image.fromstring(rgba.tobytes(), rgba.size, "RGBA")
            if target_size is not None and surface.get_size() != target_size:
                surface = pygame.transform.scale(surface, target_size)
            frames.append(surface)

    print("Archer frames loaded:", len(frames))
    print("Archer first frame size:", frames[0].get_size() if frames else None)
    return frames


def get_archer_animations():
    global ARCHER_ANIMATIONS
    if ARCHER_ANIMATIONS is not None:
        return ARCHER_ANIMATIONS

    idle_east_path = ARCHER_ASSET_DIR / "idle_east.gif"
    idle_west_path = ARCHER_ASSET_DIR / "idle_west.gif"
    walk_east_path = ARCHER_ASSET_DIR / "walk_east.gif"
    walk_west_path = ARCHER_ASSET_DIR / "walk_west.gif"
    attack_east_path = ARCHER_ASSET_DIR / "attack_east.gif"
    attack_west_path = ARCHER_ASSET_DIR / "attack_west.gif"

    print("Archer idle east exists:", idle_east_path.exists())
    print("Archer idle west exists:", idle_west_path.exists())
    print("Archer walk east exists:", walk_east_path.exists())
    print("Archer walk west exists:", walk_west_path.exists())
    print("Archer attack east exists:", attack_east_path.exists())
    print("Archer attack west exists:", attack_west_path.exists())

    idle_east_frames = load_gif_frames(idle_east_path)
    idle_west_frames = load_gif_frames(idle_west_path)
    walk_east_frames = load_gif_frames(walk_east_path)
    walk_west_frames = load_gif_frames(walk_west_path)
    attack_east_frames = load_gif_frames(attack_east_path)
    attack_west_frames = load_gif_frames(attack_west_path)

    print("Archer idle frames:", len(idle_east_frames))
    print("Archer walk frames:", len(walk_east_frames))
    print("Archer attack frames:", len(attack_east_frames))

    ARCHER_ANIMATIONS = {
        "idle": {
            "east": idle_east_frames,
            "west": idle_west_frames,
        },
        "walk": {
            "east": walk_east_frames,
            "west": walk_west_frames,
        },
        "attack": {
            "east": attack_east_frames,
            "west": attack_west_frames,
        },
    }
    return ARCHER_ANIMATIONS


class ArcherArrow:
    def __init__(self, x, y, velocity_x, velocity_y):
        self.rect = pygame.Rect(0, 0, 28, 6)
        self.rect.center = (round(x), round(y))
        self.start_x = x
        self.start_y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.facing = 1 if velocity_x >= 0 else -1
        self.angle = math.atan2(velocity_y, velocity_x)
        self.damage = ARCHER_ARROW_DAMAGE
        self.alive = True
        self.max_distance = ARCHER_ARROW_MAX_DISTANCE

    def update(self, dt, player):
        if not self.alive:
            return

        self.rect.x += round(self.velocity_x)
        self.rect.y += round(self.velocity_y)

        distance = ((self.rect.centerx - self.start_x) ** 2 + (self.rect.centery - self.start_y) ** 2) ** 0.5
        if distance >= self.max_distance:
            self.alive = False
            return

        if self.rect.colliderect(player.rect):
            if self._blocked_by_player(player):
                player.block_hit()
                print("Blocked archer arrow")
            else:
                player.take_damage(self.damage)
            self.alive = False

    def _blocked_by_player(self, player):
        shield_ids = ("shield", "shield_weapon")
        return (
            getattr(player, "current_weapon_id", None) in shield_ids
            and getattr(player, "is_blocking", False)
            and getattr(player, "facing", 1) == -self.facing
        )

    def draw(self, screen, camera=None):
        if not self.alive:
            return

        draw_rect = self.rect
        if camera:
            draw_rect = camera.apply_rect(self.rect)

        length = 24
        half_length_x = math.cos(self.angle) * length * 0.5
        half_length_y = math.sin(self.angle) * length * 0.5
        tip = (
            round(draw_rect.centerx + half_length_x),
            round(draw_rect.centery + half_length_y),
        )
        tail = (
            round(draw_rect.centerx - half_length_x),
            round(draw_rect.centery - half_length_y),
        )
        pygame.draw.line(
            screen,
            (75, 170, 230),
            tail,
            tip,
            3,
        )
        pygame.draw.circle(
            screen,
            (185, 235, 255),
            tip,
            2,
        )


class ArcherEnemy:
    def __init__(
        self,
        x,
        y,
        mode="patrol",
        patrol_left=ARCHER_PATROL_RADIUS,
        patrol_right=ARCHER_PATROL_RADIUS,
        index=None,
        debug_ai=False,
    ):
        self.rect = pygame.Rect(0, 0, *ARCHER_BODY_SIZE)
        self.rect.midbottom = (x, y)
        self.rect.y += ARCHER_SPAWN_OFFSET_Y
        self.position_x = float(self.rect.x)
        self.spawn_x = x
        self.spawn_y = y
        self.index = index
        self.debug_ai = debug_ai
        self.mode = mode
        self.patrol_min_x = x - patrol_left
        self.patrol_max_x = x + patrol_right
        self.max_hp = ARCHER_HP
        self.current_hp = self.max_hp
        self.alive = True
        self.active = True
        self.dropped_coins = False
        self.direction = "west"
        self.facing = -1
        self.patrol_direction = -1
        self.velocity_x = 0
        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.attack_cooldown_timer = 0
        self.is_attacking = False
        self.attack_has_fired = False
        self.hurt_timer = 0
        self.stunned_timer = 0
        self.being_pulled = False
        self.pull_target_x = None
        self.animations = get_archer_animations()

    def take_damage(self, amount):
        if not self.active or not self.alive:
            return

        self.current_hp -= amount
        self.hurt_timer = 0.12
        print(f"Archer took {amount} damage, HP: {self.current_hp}")

        if self.current_hp <= 0:
            self.die()

    def die(self):
        self.current_hp = 0
        self.alive = False
        self.is_attacking = False
        self.dropped_coins = False

    def stun(self, duration):
        if self.active and self.alive:
            self.stunned_timer = max(self.stunned_timer, duration)
            self.is_attacking = False
            self.state = "idle"

    def start_pull_to_player(self, player):
        if not self.active or not self.alive:
            return

        self.being_pulled = True
        self.stunned_timer = max(self.stunned_timer, 2.0)
        if player.facing == 1:
            self.pull_target_x = player.rect.right + 20
        else:
            self.pull_target_x = player.rect.left - self.rect.width - 20

    def update(self, dt, player, arrows, platforms=None):
        if not self.active or not self.alive:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        if self.stunned_timer > 0:
            self.stunned_timer -= dt
            self._animate(dt)
            return

        if self.being_pulled:
            self._update_pull()
            self._animate(dt)
            return

        distance_to_player = self._distance_to_player(player)
        player_in_range = distance_to_player <= ARCHER_SHOOTING_RANGE

        if self.is_attacking:
            self.state = "attack"
            self._face_player(player)
            self._animate_attack(dt, player, arrows)
            return

        if player_in_range:
            self._face_player(player)
            if self.attack_cooldown_timer <= 0:
                self._start_attack()
            else:
                self.state = "idle"
                self._animate(dt)
        else:
            self._patrol(dt, platforms or [])

    def _distance_to_player(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        return (dx * dx + dy * dy) ** 0.5

    def _face_player(self, player):
        if player.rect.centerx >= self.rect.centerx:
            self.direction = "east"
            self.facing = 1
        else:
            self.direction = "west"
            self.facing = -1

    def _start_attack(self):
        self.is_attacking = True
        self.attack_has_fired = False
        self.state = "attack"
        self.frame_index = 0
        self.animation_timer = 0
        print("Archer attack started at:", self.rect.midbottom)

    def _animate_attack(self, dt, player, arrows):
        frames = self._current_frames()
        if not frames:
            self._fire_arrow(player, arrows)
            self.is_attacking = False
            self.attack_cooldown_timer = ARCHER_ATTACK_COOLDOWN
            return

        self.animation_timer += dt
        if self.animation_timer >= ARCHER_ANIMATION_SPEED:
            self.animation_timer = 0
            self.frame_index += 1

        release_frame = round((len(frames) - 1) * ARCHER_ATTACK_RELEASE_RATIO)
        release_frame = min(max(1, release_frame), len(frames) - 1)
        if self.frame_index >= release_frame and not self.attack_has_fired:
            self._fire_arrow(player, arrows)

        if self.frame_index >= len(frames):
            self.frame_index = 0
            self.is_attacking = False
            self.attack_cooldown_timer = ARCHER_ATTACK_COOLDOWN
            self.state = "idle"

    def _fire_arrow(self, player, arrows):
        arrow_x = self.rect.centerx + self.facing * 28
        arrow_y = self.rect.centery - 10
        dx = player.rect.centerx - arrow_x
        dy = player.rect.centery - arrow_y
        distance = max(1, (dx * dx + dy * dy) ** 0.5)
        velocity_x = (dx / distance) * ARCHER_ARROW_SPEED
        velocity_y = (dy / distance) * ARCHER_ARROW_SPEED
        arrows.append(ArcherArrow(arrow_x, arrow_y, velocity_x, velocity_y))
        self.attack_has_fired = True
        print("Archer arrow spawned:", (arrow_x, arrow_y), "velocity:", (velocity_x, velocity_y))

    def _patrol(self, dt, platforms):
        if self.mode == "static":
            self.rect.midbottom = (self.spawn_x, self.spawn_y)
            self.rect.y += ARCHER_SPAWN_OFFSET_Y
            self.position_x = float(self.rect.x)
            self.velocity_x = 0
            self.state = "idle"
            self._animate(dt)
            return

        if self.rect.centerx <= self.patrol_min_x:
            self.patrol_direction = 1
        elif self.rect.centerx >= self.patrol_max_x:
            self.patrol_direction = -1

        self.facing = self.patrol_direction
        self.direction = "east" if self.facing > 0 else "west"
        self.state = "walk"
        self.velocity_x = self.patrol_direction * ARCHER_WALK_SPEED

        next_x = self.position_x + self.velocity_x
        next_rect = self.rect.copy()
        next_rect.x = round(next_x)

        if next_rect.centerx < self.patrol_min_x:
            next_rect.centerx = round(self.patrol_min_x)
            self.patrol_direction = 1
        elif next_rect.centerx > self.patrol_max_x:
            next_rect.centerx = round(self.patrol_max_x)
            self.patrol_direction = -1
        elif not self._has_ground_ahead(next_rect, platforms) or self._hits_wall(next_rect, platforms):
            self.patrol_direction *= -1
            self.facing = self.patrol_direction
            self.direction = "east" if self.facing > 0 else "west"
            self.velocity_x = 0
            self._animate(dt)
            return

        self.rect.x = next_rect.x
        self.position_x = float(self.rect.x)
        self.facing = self.patrol_direction
        self.direction = "east" if self.facing > 0 else "west"
        if self.debug_ai:
            print(
                "[ARCHER PATROL]",
                self.index,
                self.rect.x,
                self.patrol_min_x,
                self.patrol_max_x,
                self.patrol_direction,
            )
        self._animate(dt)

    def _has_ground_ahead(self, next_rect, platforms):
        probe_x = next_rect.right + 4 if self.patrol_direction > 0 else next_rect.left - 4
        ground_probe = pygame.Rect(probe_x, next_rect.bottom, 6, 12)
        return any(ground_probe.colliderect(platform) for platform in platforms)

    def _hits_wall(self, next_rect, platforms):
        wall_probe = pygame.Rect(next_rect.x, next_rect.y + 8, next_rect.width, next_rect.height - 16)
        for platform in platforms:
            if wall_probe.colliderect(platform) and platform.top < self.rect.bottom - 8:
                return True
        return False

    def _animate(self, dt):
        frames = self._current_frames()
        if not frames:
            return

        self.animation_timer += dt
        if self.animation_timer >= ARCHER_ANIMATION_SPEED:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)

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

    def draw(self, screen, camera=None):
        if not self.active or not self.alive:
            return

        frames = self._current_frames()
        visual_rect = None
        if frames:
            frame = frames[min(self.frame_index, len(frames) - 1)]
            visual_rect = frame.get_rect(
                midbottom=(self.rect.centerx, self.rect.bottom + ARCHER_DRAW_OFFSET_Y)
            )
            draw_rect = visual_rect
            if camera:
                draw_rect = camera.apply_rect(visual_rect)
            if self.hurt_timer > 0:
                tinted = frame.copy()
                tinted.fill((255, 120, 120, 80), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(tinted, draw_rect)
            else:
                screen.blit(frame, draw_rect)
        else:
            draw_rect = self.rect
            if camera:
                draw_rect = camera.apply_rect(self.rect)
            pygame.draw.rect(screen, (120, 40, 170), draw_rect)

        self._draw_hp_bar(screen, camera, visual_rect)

    def _draw_hp_bar(self, screen, camera=None, visual_rect=None):
        bar_width = self.rect.width
        bar_height = 5
        if visual_rect is not None:
            bar_x = visual_rect.centerx - bar_width // 2
            bar_y = visual_rect.top + ARCHER_HP_BAR_OFFSET_Y
        else:
            bar_x = self.rect.x
            bar_y = self.rect.y + ARCHER_HP_BAR_OFFSET_Y
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        fill_rect = bar_rect.copy()
        fill_rect.width = round(bar_width * max(0, self.current_hp) / self.max_hp)

        if camera:
            bar_rect = camera.apply_rect(bar_rect)
            fill_rect = camera.apply_rect(fill_rect)

        pygame.draw.rect(screen, (45, 18, 55), bar_rect)
        pygame.draw.rect(screen, (95, 220, 135), fill_rect)
