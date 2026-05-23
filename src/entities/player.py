import math

import pygame

from settings import (
    AUTO_GRAPPLE_ARC_HEIGHT,
    AUTO_GRAPPLE_DURATION,
    DEBUG_UNLIMITED_HP,
    DEBUG_UNLIMITED_MANA,
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
from src.systems.skills import get_skill
from src.systems.weapons import get_weapon


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
        self.current_skill_id = "time_freeze"
        self.skill_cooldown_timer = 0
        self.debug_unlimited_hp = DEBUG_UNLIMITED_HP
        self.debug_unlimited_mana = DEBUG_UNLIMITED_MANA

        self.soul_anchor_active = False
        self.soul_anchor_pos = None
        self.soul_anchor_timer = 0

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
            self.switch_skill("execute_strike")
        if keys[pygame.K_0]:
            self.switch_skill("soul_anchor")

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
        self.update_timers(dt)

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
        self.update_skill_timers(dt)

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

    def draw(self, screen, camera=None):
        if self.guard_broken_timer > 0:
            color = (255, 180, 80)
        elif self.invincible_timer > 0:
            color = (255, 255, 255)
        else:
            color = (180, 220, 255)

        draw_rect = self.rect
        if camera:
            draw_rect = camera.apply_rect(self.rect)

        self.draw_kael_template(screen, draw_rect, color)

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

        if self.soul_anchor_active and self.soul_anchor_pos is not None:
            anchor_pos = self.soul_anchor_pos
            if camera:
                anchor_pos = camera.apply_pos(anchor_pos)
            pygame.draw.circle(screen, (120, 255, 180), anchor_pos, 14, 3)
            pygame.draw.circle(screen, (120, 255, 180), anchor_pos, 4)

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
        if self.guard_broken_timer > 0:
            moon_core = (255, 180, 80)
            moon_glow = (255, 120, 50)
        elif self.invincible_timer > 0:
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
        if self.is_attacking:
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
