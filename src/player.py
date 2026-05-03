import pygame

from settings import (
    AUTO_GRAPPLE_ARC_HEIGHT,
    AUTO_GRAPPLE_DURATION,
    GRAVITY,
    GUARD_BREAK_TIME,
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
    STAMINA_BLOCK_DRAIN_PER_SECOND,
    STAMINA_BLOCK_HIT_COST,
    STAMINA_MAX,
    STAMINA_RECOVER_DELAY,
    STAMINA_RECOVER_DELAY_AFTER_HIT,
    STAMINA_RECOVER_PER_SECOND,
)
from src.weapons import get_weapon


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 64)

        self.vel_x = 0
        self.vel_y = 0
        self.facing = 1
        self.on_ground = False

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

        self.max_stamina = STAMINA_MAX
        self.current_stamina = STAMINA_MAX
        self.is_blocking = False
        self.guard_broken_timer = 0
        self.stamina_recover_delay_timer = 0

        self.is_parrying = False
        self.parry_timer = 0
        self.parry_cooldown_timer = 0

        self.special_cooldown_timer = 0

        self.is_auto_grappling = False
        self.auto_grapple_timer = 0
        self.auto_grapple_duration = 0
        self.auto_grapple_start = None
        self.auto_grapple_end = None
        self.auto_grapple_control = None
        self.auto_grapple_anchor = None

        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0

        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown_timer = 0
        self.attack_hitbox = pygame.Rect(0, 0, 1, 1)
        self.attack_has_hit = False
        self.should_spawn_projectile = False
        self.has_active_shield_throw = False

        self.invincible_timer = 0
        self.is_dead = False

        self.l_was_pressed = False

    def handle_input(self, keys):
        if self.is_dead:
            self.vel_x = 0
            return

        if self.is_auto_grappling:
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

    def start_dash(self):
        if self.guard_broken_timer > 0:
            return

        self.is_dashing = True
        self.dash_timer = PLAYER_DASH_TIME
        self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN
        self.vel_y = 0

    def start_attack(self):
        if self.guard_broken_timer > 0:
            return

        weapon = get_weapon(self.current_weapon_id)
        self.is_attacking = True
        self.attack_timer = 0.12
        self.attack_cooldown_timer = weapon["cooldown"]
        self.attack_has_hit = False

        if weapon["weapon_type"] == "projectile":
            self.should_spawn_projectile = True
        else:
            self.attack_hitbox = self.get_attack_hitbox()

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
            can_block = self.current_stamina > 0 and self.guard_broken_timer <= 0

            if can_block:
                self.is_blocking = True
                self.current_stamina -= STAMINA_BLOCK_DRAIN_PER_SECOND * dt
                self.stamina_recover_delay_timer = STAMINA_RECOVER_DELAY

                if self.current_stamina <= 0:
                    self.current_stamina = 0
                    self.is_blocking = False
                    self.guard_broken_timer = GUARD_BREAK_TIME
                return

        self.is_blocking = False

    def block_hit(self):
        self.current_stamina -= STAMINA_BLOCK_HIT_COST
        self.stamina_recover_delay_timer = STAMINA_RECOVER_DELAY_AFTER_HIT

        if self.current_stamina <= 0:
            self.current_stamina = 0
            self.is_blocking = False
            self.guard_broken_timer = GUARD_BREAK_TIME

    def take_damage(self, amount):
        if self.invincible_timer > 0 or self.is_dead:
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

    def update(self, dt, platforms, keys):
        self.update_timers(dt)

        if self.is_dead:
            self.vel_x = 0
            return

        if self.is_auto_grappling:
            self.update_auto_grapple(dt)
            return

        self.update_blocking(keys, dt)
        self.recover_stamina(dt)

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

    def update_timers(self, dt):
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        if self.special_cooldown_timer > 0:
            self.special_cooldown_timer -= dt

        if self.guard_broken_timer > 0:
            self.guard_broken_timer -= dt

        if self.stamina_recover_delay_timer > 0:
            self.stamina_recover_delay_timer -= dt

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

    def recover_stamina(self, dt):
        if self.is_blocking:
            return

        if self.stamina_recover_delay_timer > 0:
            return

        if self.current_stamina < self.max_stamina:
            self.current_stamina += STAMINA_RECOVER_PER_SECOND * dt
            self.current_stamina = min(self.current_stamina, self.max_stamina)

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

    def draw(self, screen):
        if self.guard_broken_timer > 0:
            color = (255, 180, 80)
        elif self.invincible_timer > 0:
            color = (255, 255, 255)
        else:
            color = (180, 220, 255)

        pygame.draw.rect(screen, color, self.rect)

        if self.is_blocking:
            self.draw_block_effect(screen)

        if self.is_parrying:
            self.draw_parry_effect(screen)

        if self.is_auto_grappling and self.auto_grapple_anchor is not None:
            pygame.draw.line(screen, (180, 90, 255), self.auto_grapple_anchor, self.rect.center, 3)

    def draw_block_effect(self, screen):
        if self.facing == 1:
            shield_rect = pygame.Rect(self.rect.right, self.rect.y + 8, 10, self.rect.height - 16)
        else:
            shield_rect = pygame.Rect(self.rect.left - 10, self.rect.y + 8, 10, self.rect.height - 16)

        pygame.draw.rect(screen, (80, 170, 255), shield_rect, 2)

    def draw_parry_effect(self, screen):
        if self.facing == 1:
            parry_rect = pygame.Rect(self.rect.right, self.rect.y, 20, self.rect.height)
        else:
            parry_rect = pygame.Rect(self.rect.left - 20, self.rect.y, 20, self.rect.height)

        pygame.draw.rect(screen, (255, 255, 120), parry_rect, 2)
