import math
from pathlib import Path

import pygame

from settings import (
    DEBUG_PROJECTILES,
    SHIELD_RETURN_SPEED,
    SHIELD_THROW_CAN_HIT_ON_RETURN,
    SHIELD_THROW_HIT_COOLDOWN,
    SHIELD_THROW_LIFETIME,
    SHIELD_THROW_MAX_DISTANCE,
    SHIELD_THROW_SIZE,
    SHIELD_THROW_SPEED,
    SHOOTER_BULLET_FRAME_COUNT,
    SHOOTER_BULLET_HIT_PATH,
    SHOOTER_BULLET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SHOOTER_BULLET_FRAMES = None
SHOOTER_BULLET_HIT_FRAMES = None
SHOOTER_BULLET_SCALE = 0.35
SHOOTER_BULLET_HIT_SCALE = 0.45


def resolve_asset_path(path):
    asset_path = Path(path)
    if asset_path.is_absolute():
        return asset_path
    return PROJECT_ROOT / asset_path


def color_distance(color, sample):
    return abs(color.r - sample.r) + abs(color.g - sample.g) + abs(color.b - sample.b)


def repair_projectile_background(surface):
    samples = [
        surface.get_at((0, 0)),
        surface.get_at((surface.get_width() - 1, 0)),
        surface.get_at((0, surface.get_height() - 1)),
        surface.get_at((surface.get_width() - 1, surface.get_height() - 1)),
    ]
    if any(sample.a < 255 for sample in samples):
        return surface

    repaired = surface.copy()
    removed_pixels = 0
    for y in range(repaired.get_height()):
        for x in range(repaired.get_width()):
            color = repaired.get_at((x, y))
            spread = max(color.r, color.g, color.b) - min(color.r, color.g, color.b)
            matches_corner = any(color_distance(color, sample) <= 42 for sample in samples)
            near_white = color.r >= 220 and color.g >= 220 and color.b >= 220 and spread <= 35
            flat_gray = spread <= 16 and 35 <= color.r <= 225 and 35 <= color.g <= 225 and 35 <= color.b <= 225
            if color.a == 255 and (matches_corner or near_white or flat_gray):
                repaired.set_at((x, y), (color.r, color.g, color.b, 0))
                removed_pixels += 1
    if removed_pixels == 0 and samples[0].a == 255:
        print("WARNING: shooter bullet image is not transparent and must be regenerated/exported as transparent PNG")
    return repaired


def crop_visible(surface):
    bounds = surface.get_bounding_rect(min_alpha=1)
    if bounds.width <= 0 or bounds.height <= 0:
        return surface
    cropped = pygame.Surface(bounds.size, pygame.SRCALPHA)
    cropped.blit(surface, (0, 0), bounds)
    return cropped


def scale_projectile_frame(surface, scale):
    if scale == 1:
        return surface
    size = (
        max(1, round(surface.get_width() * scale)),
        max(1, round(surface.get_height() * scale)),
    )
    return pygame.transform.smoothscale(surface, size).convert_alpha()


def load_projectile_sheet(path, frame_count, scale=1.0):
    resolved_path = resolve_asset_path(path)
    print("Projectile sheet path:", resolved_path)
    print("Projectile sheet exists:", resolved_path.exists())

    if not resolved_path.exists():
        print("Missing projectile sheet:", resolved_path)
        return []

    sheet = pygame.image.load(str(resolved_path)).convert_alpha()
    print("Projectile sheet size:", sheet.get_size())
    frame_width = sheet.get_width() // frame_count
    frame_height = sheet.get_height()
    if sheet.get_width() % frame_count != 0:
        print("Projectile sheet width not evenly divisible by frame count:", resolved_path, sheet.get_size())

    frames = []
    for index in range(frame_count):
        source_rect = pygame.Rect(index * frame_width, 0, frame_width, frame_height)
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), source_rect)
        frame = repair_projectile_background(frame)
        frame = crop_visible(frame)
        frame = scale_projectile_frame(frame, scale)
        frames.append(frame)

    print("Projectile loaded frame count:", len(frames))
    print("Projectile first frame size:", frames[0].get_size() if frames else None)
    return frames


def get_shooter_bullet_frames():
    global SHOOTER_BULLET_FRAMES
    if SHOOTER_BULLET_FRAMES is None:
        SHOOTER_BULLET_FRAMES = load_projectile_sheet(
            SHOOTER_BULLET_PATH,
            SHOOTER_BULLET_FRAME_COUNT,
            SHOOTER_BULLET_SCALE,
        )
    return SHOOTER_BULLET_FRAMES


def get_shooter_bullet_hit_frames():
    global SHOOTER_BULLET_HIT_FRAMES
    if SHOOTER_BULLET_HIT_FRAMES is None:
        SHOOTER_BULLET_HIT_FRAMES = load_projectile_sheet(
            SHOOTER_BULLET_HIT_PATH,
            SHOOTER_BULLET_FRAME_COUNT,
            SHOOTER_BULLET_HIT_SCALE,
        )
    return SHOOTER_BULLET_HIT_FRAMES


def print_projectile_asset_debug_summary():
    shooter_bullet_frames = get_shooter_bullet_frames()
    shooter_bullet_hit_frames = get_shooter_bullet_hit_frames()
    print("Shooter bullet path:", SHOOTER_BULLET_PATH)
    print("Shooter bullet frames loaded:", len(shooter_bullet_frames))
    print("Shooter bullet hit path:", SHOOTER_BULLET_HIT_PATH)
    print("Shooter bullet hit frames loaded:", len(shooter_bullet_hit_frames))


class Projectile:
    def __init__(
        self,
        x,
        y,
        direction,
        damage,
        is_critical,
        speed,
        max_distance=350,
        projectile_type="weapon",
    ):
        self.rect = pygame.Rect(0, 0, 16, 10)
        self.rect.center = (round(x), round(y))
        self.start_x = x
        self.start_y = y
        self.direction = direction
        self.velocity_x = direction * speed
        self.max_distance = max_distance
        self.damage = damage
        self.is_critical = is_critical
        self.projectile_type = projectile_type
        self.alive = True
        self.has_hit = False
        self.frames = get_shooter_bullet_frames() if projectile_type == "weapon" else []
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.06

    def update(self, dt, platforms=None):
        if not self.alive:
            return

        self.rect.x += round(self.velocity_x)
        self.animation_timer += dt
        if self.frames and self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        distance = abs(self.rect.centerx - self.start_x)
        if distance >= self.max_distance:
            self.alive = False

        if platforms is None:
            return

        for platform in platforms:
            if self.rect.colliderect(platform):
                self.alive = False

    def draw(self, screen, camera=None):
        if not self.alive:
            return

        if self.frames:
            frame = self.frames[self.frame_index]
            if self.direction < 0:
                frame = pygame.transform.flip(frame, True, False)
            draw_center = self.rect.center
            if camera:
                draw_center = camera.apply_pos(draw_center)
            screen.blit(frame, frame.get_rect(center=draw_center))
            if DEBUG_PROJECTILES:
                print("Drawing shooter bullet frame:", self.frame_index, "at", self.rect.center)
            return

        if DEBUG_PROJECTILES:
            print("Shooter bullet has no loaded frame at", self.rect.center)


class ProjectileHitEffect:
    def __init__(self, center):
        self.center = center
        self.frames = get_shooter_bullet_hit_frames()
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.06
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return

        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.alive = False

    def draw(self, screen, camera=None):
        if not self.alive or not self.frames:
            return

        frame = self.frames[min(self.frame_index, len(self.frames) - 1)]
        draw_center = self.center
        if camera:
            draw_center = camera.apply_pos(draw_center)
        screen.blit(frame, frame.get_rect(center=draw_center))


class ReturningShield:
    def __init__(self, x, y, direction, damage, is_critical, owner_player):
        self.rect = pygame.Rect(
            x - SHIELD_THROW_SIZE // 2,
            y - SHIELD_THROW_SIZE // 2,
            SHIELD_THROW_SIZE,
            SHIELD_THROW_SIZE,
        )
        self.start_x = x
        self.start_y = y
        self.direction = direction
        self.damage = damage
        self.is_critical = is_critical
        self.owner_player = owner_player
        self.speed = SHIELD_THROW_SPEED
        self.return_speed = SHIELD_RETURN_SPEED
        self.max_distance = SHIELD_THROW_MAX_DISTANCE
        self.lifetime = SHIELD_THROW_LIFETIME
        self.alive = True
        self.returning = False
        self.hit_enemy_outgoing = False
        self.hit_enemy_returning = False
        self.hit_cooldown_timer = 0

    def update(self, dt):
        if not self.alive:
            return

        if self.hit_cooldown_timer > 0:
            self.hit_cooldown_timer -= dt

        self.lifetime -= dt

        if self.lifetime <= 0:
            self.alive = False
            return

        if self.returning:
            self.move_toward_player()
        else:
            self.rect.x += self.speed * self.direction

            distance = abs(self.rect.centerx - self.start_x)
            if distance >= self.max_distance:
                self.returning = True

    def move_toward_player(self):
        target_x, target_y = self.owner_player.rect.center
        distance_x = target_x - self.rect.centerx
        distance_y = target_y - self.rect.centery
        distance = math.hypot(distance_x, distance_y)

        if distance <= self.return_speed:
            self.alive = False
            return

        self.rect.x += int((distance_x / distance) * self.return_speed)
        self.rect.y += int((distance_y / distance) * self.return_speed)

    def check_enemy_collision(self, enemy):
        if not self.alive or not enemy.alive:
            return

        if not self.rect.colliderect(enemy.rect):
            return

        if self.hit_cooldown_timer > 0:
            return

        if not self.returning:
            if self.hit_enemy_outgoing:
                return

            enemy.take_damage(self.damage)
            self.hit_enemy_outgoing = True
            self.hit_cooldown_timer = SHIELD_THROW_HIT_COOLDOWN
            print(f"Shield outgoing hit enemy for {self.damage} damage")
            return

        if SHIELD_THROW_CAN_HIT_ON_RETURN and not self.hit_enemy_returning:
            enemy.take_damage(self.damage)
            self.hit_enemy_returning = True
            self.hit_cooldown_timer = SHIELD_THROW_HIT_COOLDOWN
            print(f"Shield returning hit enemy for {self.damage} damage")

    def draw(self, screen, camera=None):
        if not self.alive:
            return

        if self.returning:
            color = (80, 220, 255)
        else:
            color = (80, 160, 255)

        draw_rect = self.rect
        if camera:
            draw_rect = camera.apply_rect(self.rect)

        pygame.draw.ellipse(screen, color, draw_rect)
        pygame.draw.ellipse(screen, (220, 250, 255), draw_rect, 2)
