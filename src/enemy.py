import pygame

from settings import (
    ENEMY_ATTACK_COOLDOWN,
    ENEMY_ATTACK_RANGE,
    ENEMY_ATTACK_TIME,
    ENEMY_MAX_HP,
    ENEMY_RESPAWN_TIME,
    GRAPPLE_ENEMY_FINAL_STUN_TIME,
    GRAPPLE_PULL_SPEED,
)


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 60)
        self.spawn_x = x
        self.spawn_y = y
        self.max_hp = ENEMY_MAX_HP
        self.current_hp = self.max_hp
        self.alive = True
        self.hurt_timer = 0
        self.respawn_timer = 0
        self.dropped_coins = False

        self.attack_cooldown_timer = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_hitbox = pygame.Rect(0, 0, ENEMY_ATTACK_RANGE, self.rect.height)
        self.attack_has_hit = False
        self.facing = -1

        self.stunned_timer = 0
        self.vel_x = 0
        self.being_pulled = False
        self.pull_target_x = None

    def take_damage(self, amount):
        if not self.alive:
            return

        self.current_hp -= amount
        self.hurt_timer = 0.12

        if self.current_hp <= 0:
            self.current_hp = 0
            self.alive = False
            self.respawn_timer = ENEMY_RESPAWN_TIME
            self.is_attacking = False
            self.being_pulled = False

    def respawn(self):
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.current_hp = self.max_hp
        self.alive = True
        self.dropped_coins = False
        self.hurt_timer = 0
        self.respawn_timer = 0

        self.stunned_timer = 0
        self.vel_x = 0
        self.being_pulled = False
        self.pull_target_x = None

        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown_timer = 0
        self.attack_has_hit = False
        self.attack_hitbox = self.get_attack_hitbox()

    def stun(self, duration):
        self.stunned_timer = max(self.stunned_timer, duration)
        self.is_attacking = False

    def start_pull_to_player(self, player):
        self.being_pulled = True
        self.stunned_timer = max(self.stunned_timer, 2.0)
        self.is_attacking = False

        if player.facing == 1:
            self.pull_target_x = player.rect.right + 20
        else:
            self.pull_target_x = player.rect.left - self.rect.width - 20

    def start_attack(self, player):
        self.is_attacking = True
        self.attack_timer = ENEMY_ATTACK_TIME
        self.attack_cooldown_timer = ENEMY_ATTACK_COOLDOWN
        self.attack_has_hit = False

        if player.rect.centerx < self.rect.centerx:
            self.facing = -1
        else:
            self.facing = 1

        self.attack_hitbox = self.get_attack_hitbox()

    def get_attack_hitbox(self):
        if self.facing == 1:
            hitbox_x = self.rect.right
        else:
            hitbox_x = self.rect.left - ENEMY_ATTACK_RANGE

        return pygame.Rect(hitbox_x, self.rect.y, ENEMY_ATTACK_RANGE, self.rect.height)

    def update(self, dt, player=None):
        if self.hurt_timer > 0:
            self.hurt_timer -= dt

        if not self.alive:
            self.respawn_timer -= dt

            if self.respawn_timer <= 0:
                self.respawn()

            return

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        if self.stunned_timer > 0:
            self.stunned_timer -= dt

        if self.being_pulled:
            self.update_pull()
            return

        if self.stunned_timer > 0:
            return

        if self.is_attacking:
            self.attack_timer -= dt
            self.attack_hitbox = self.get_attack_hitbox()

            if self.attack_timer <= 0:
                self.is_attacking = False

        if player is None or player.is_dead or self.is_attacking:
            return

        horizontal_distance = abs(player.rect.centerx - self.rect.centerx)
        vertical_distance = abs(player.rect.centery - self.rect.centery)

        if horizontal_distance <= ENEMY_ATTACK_RANGE + self.rect.width and vertical_distance <= self.rect.height:
            if player.rect.centerx < self.rect.centerx:
                self.facing = -1
            else:
                self.facing = 1

            if self.attack_cooldown_timer <= 0:
                self.start_attack(player)

    def update_pull(self):
        if self.pull_target_x is None:
            self.being_pulled = False
            return

        distance_x = self.pull_target_x - self.rect.x

        if abs(distance_x) <= GRAPPLE_PULL_SPEED:
            self.rect.x = self.pull_target_x
            self.being_pulled = False
            self.stunned_timer = GRAPPLE_ENEMY_FINAL_STUN_TIME
            return

        if distance_x > 0:
            self.rect.x += GRAPPLE_PULL_SPEED
        else:
            self.rect.x -= GRAPPLE_PULL_SPEED

    def draw(self, screen):
        if not self.alive:
            return

        if self.being_pulled:
            color = (180, 80, 255)
        elif self.stunned_timer > 0:
            color = (255, 220, 80)
        elif self.hurt_timer > 0:
            color = (255, 220, 220)
        else:
            color = (220, 50, 50)

        pygame.draw.rect(screen, color, self.rect)

        if self.being_pulled:
            pygame.draw.rect(screen, (240, 220, 255), self.rect, 2)

        self.draw_hp_bar(screen)

    def draw_hp_bar(self, screen):
        bar_width = self.rect.width
        bar_height = 6
        bar_x = self.rect.x
        bar_y = self.rect.y - 12

        hp_percent = self.current_hp / self.max_hp
        fill_width = int(bar_width * hp_percent)

        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)

        pygame.draw.rect(screen, (60, 20, 20), background_rect)
        pygame.draw.rect(screen, (50, 220, 80), fill_rect)
