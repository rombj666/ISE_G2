import math

import pygame

from settings import (
    PROJECTILE_LIFETIME,
    SHIELD_RETURN_SPEED,
    SHIELD_THROW_CAN_HIT_ON_RETURN,
    SHIELD_THROW_HIT_COOLDOWN,
    SHIELD_THROW_LIFETIME,
    SHIELD_THROW_MAX_DISTANCE,
    SHIELD_THROW_SIZE,
    SHIELD_THROW_SPEED,
)


class Projectile:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        vel_x,
        vel_y,
        damage,
        is_critical,
        projectile_gravity=0,
        projectile_type="shooter",
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.damage = damage
        self.is_critical = is_critical
        self.projectile_gravity = projectile_gravity
        self.lifetime = PROJECTILE_LIFETIME
        self.alive = True
        self.projectile_type = projectile_type

    def update(self, dt, platforms=None):
        if not self.alive:
            return

        self.rect.x += self.vel_x
        self.vel_y += self.projectile_gravity
        self.rect.y += self.vel_y
        self.lifetime -= dt

        if self.lifetime <= 0:
            self.alive = False

        if platforms is None:
            return

        for platform in platforms:
            if self.rect.colliderect(platform):
                self.alive = False

    def draw(self, screen):
        if not self.alive:
            return

        pygame.draw.rect(screen, (255, 190, 60), self.rect)


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

    def draw(self, screen):
        if not self.alive:
            return

        if self.returning:
            color = (80, 220, 255)
        else:
            color = (80, 160, 255)

        pygame.draw.ellipse(screen, color, self.rect)
        pygame.draw.ellipse(screen, (220, 250, 255), self.rect, 2)
