import pygame

from settings import (
    GRAVITY,
    PLAYER_BONUS_ATTACK_PERCENT,
    PLAYER_CRIT_CHANCE,
    PLAYER_CRIT_DAMAGE,
    PLAYER_DASH_COOLDOWN,
    PLAYER_DASH_SPEED,
    PLAYER_DASH_TIME,
    PLAYER_JUMP_SPEED,
    PLAYER_MAX_HP,
    PLAYER_MAX_MANA,
    PLAYER_SPEED,
)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 64)

        self.vel_x = 0
        self.vel_y = 0
        self.facing = 1
        self.on_ground = False

        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.mana = PLAYER_MAX_MANA
        self.max_mana = PLAYER_MAX_MANA

        self.crit_chance = PLAYER_CRIT_CHANCE
        self.crit_damage = PLAYER_CRIT_DAMAGE
        self.bonus_attack_percent = PLAYER_BONUS_ATTACK_PERCENT
        self.coins = 0

        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0

    def handle_input(self, keys):
        self.vel_x = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
            self.facing = -1

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            self.facing = 1

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = PLAYER_JUMP_SPEED
            self.on_ground = False

        if keys[pygame.K_LSHIFT] and self.dash_cooldown_timer <= 0:
            self.start_dash()

    def start_dash(self):
        self.is_dashing = True
        self.dash_timer = PLAYER_DASH_TIME
        self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN
        self.vel_y = 0

    def update(self, dt, platforms):
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

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

    def move_x(self, platforms):
        self.rect.x += self.vel_x

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_x > 0:
                    self.rect.right = platform.left
                elif self.vel_x < 0:
                    self.rect.left = platform.right

    def move_y(self, platforms):
        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.bottom
                    self.vel_y = 0
