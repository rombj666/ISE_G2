import math

import pygame

from settings import (
    ENERGY_BEAM_DAMAGE,
    ORBIT_BLADE_DAMAGE,
    ORBIT_BLADE_FIRE_DELAY,
    ORBIT_BLADE_LIFETIME,
    ORBIT_BLADE_ORBIT_SPEED,
    ORBIT_BLADE_PROJECTILE_SPEED,
    ORBIT_BLADE_RADIUS,
    ORBIT_BLADE_READY_TIME,
    ORBIT_BLADE_SIZE,
    ORBIT_BLADE_TARGET_RANGE,
    SKILL_EFFECT_LIFETIME,
    TIME_FREEZE_RADIUS,
)


SKILLS = {
    "time_freeze": {
        "id": "time_freeze",
        "name": "Time Freeze",
        "skill_type": "time_freeze",
        "mana_cost": 45,
        "cooldown": 10.0,
        "damage": 0,
        "description": "Creates a fixed time domain around the player. Enemy inside cannot move or attack for a short time.",
    },
    "orbit_blades": {
        "id": "orbit_blades",
        "name": "Orbit Blades",
        "skill_type": "orbit_blades",
        "mana_cost": 35,
        "cooldown": 7.0,
        "damage": ORBIT_BLADE_DAMAGE,
        "description": "Creates 3 blades around the player. The blades orbit briefly, auto-aim at enemy, then shoot toward it.",
    },
    "energy_beam": {
        "id": "energy_beam",
        "name": "Energy Beam",
        "skill_type": "energy_beam",
        "mana_cost": 45,
        "cooldown": 9.0,
        "damage": ENERGY_BEAM_DAMAGE,
        "description": "Fires a strong beam forward.",
    },
    "execute_strike": {
        "id": "execute_strike",
        "name": "Execute Strike",
        "skill_type": "execute",
        "mana_cost": 30,
        "cooldown": 6.0,
        "damage": 9999,
        "description": "Instantly kills enemy if enemy HP is 50% or lower, or if enemy was marked executable by a perfect parry.",
    },
    "soul_anchor": {
        "id": "soul_anchor",
        "name": "Soul Anchor",
        "skill_type": "soul_anchor",
        "mana_cost": 35,
        "cooldown": 10.0,
        "damage": 0,
        "description": "First use places an anchor. Second use returns the player to that anchor.",
    },
}


def get_skill(skill_id):
    if skill_id in SKILLS:
        return SKILLS[skill_id]
    return SKILLS["time_freeze"]


def get_all_skills():
    return SKILLS


class TimeFreezeDomain:
    def __init__(self, center, duration):
        self.center = center
        self.radius = TIME_FREEZE_RADIUS
        self.timer = duration
        self.alive = True

    def update(self, dt, enemy):
        self.timer -= dt
        if self.timer <= 0:
            self.alive = False
            return

        if enemy.alive:
            distance = math.hypot(
                enemy.rect.centerx - self.center[0],
                enemy.rect.centery - self.center[1],
            )
            if distance <= self.radius:
                enemy.freeze(0.1)

    def draw(self, screen, camera=None):
        center = self.center
        if camera:
            center = camera.apply_pos(center)

        pygame.draw.circle(screen, (80, 180, 255), center, self.radius, 3)
        pygame.draw.circle(screen, (30, 90, 150), center, self.radius // 3, 1)


class OrbitBlade:
    def __init__(self, player, index, total_blades):
        self.rect = pygame.Rect(0, 0, ORBIT_BLADE_SIZE, ORBIT_BLADE_SIZE)
        self.angle = index * (2 * math.pi / total_blades)
        self.index = index
        self.state = "orbit"
        self.fire_delay = ORBIT_BLADE_READY_TIME + index * ORBIT_BLADE_FIRE_DELAY
        self.vel_x = 0
        self.vel_y = 0
        self.damage = ORBIT_BLADE_DAMAGE
        self.lifetime = ORBIT_BLADE_LIFETIME
        self.alive = True
        self.has_hit = False
        self.update_orbit_position(player)

    def update(self, dt, player, enemy):
        if not self.alive:
            return

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            self.state = "dead"
            return

        if self.state == "orbit":
            self.angle += ORBIT_BLADE_ORBIT_SPEED * dt
            self.fire_delay -= dt
            self.update_orbit_position(player)

            if self.fire_delay <= 0:
                target = self.find_target(enemy)
                if target is not None:
                    self.fire_at(target)

        elif self.state == "fired":
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            self.check_enemy_collision(enemy)

    def update_orbit_position(self, player):
        x = player.rect.centerx + math.cos(self.angle) * ORBIT_BLADE_RADIUS
        y = player.rect.centery + math.sin(self.angle) * ORBIT_BLADE_RADIUS
        self.rect.center = (round(x), round(y))

    def find_target(self, enemy):
        if not enemy.alive:
            return None

        distance = math.hypot(
            enemy.rect.centerx - self.rect.centerx,
            enemy.rect.centery - self.rect.centery,
        )
        if distance <= ORBIT_BLADE_TARGET_RANGE:
            return enemy
        return None

    def fire_at(self, enemy):
        dx = enemy.rect.centerx - self.rect.centerx
        dy = enemy.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1

        self.vel_x = (dx / distance) * ORBIT_BLADE_PROJECTILE_SPEED
        self.vel_y = (dy / distance) * ORBIT_BLADE_PROJECTILE_SPEED
        self.state = "fired"

    def check_enemy_collision(self, enemy):
        if not enemy.alive or self.has_hit:
            return

        if self.rect.colliderect(enemy.rect):
            enemy.take_damage(self.damage)
            self.has_hit = True
            self.alive = False
            self.state = "dead"
            print("Orbit blade hit enemy")

    def draw(self, screen, camera=None):
        if not self.alive:
            return

        if self.state == "orbit":
            color = (80, 230, 255)
        else:
            color = (255, 240, 90)

        draw_rect = self.rect
        if camera:
            draw_rect = camera.apply_rect(self.rect)

        pygame.draw.ellipse(screen, color, draw_rect)
        pygame.draw.ellipse(screen, (230, 255, 255), draw_rect, 1)


class EnergyBeamEffect:
    def __init__(self, rect):
        self.rect = rect
        self.timer = SKILL_EFFECT_LIFETIME
        self.alive = True

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.alive = False

    def draw(self, screen, camera=None):
        draw_rect = self.rect
        if camera:
            draw_rect = camera.apply_rect(self.rect)

        pygame.draw.rect(screen, (80, 230, 255), draw_rect)
        pygame.draw.rect(screen, (255, 255, 255), draw_rect, 2)


class SkillCircleEffect:
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color = color
        self.timer = SKILL_EFFECT_LIFETIME
        self.alive = True

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.alive = False

    def draw(self, screen, camera=None):
        center = self.center
        if camera:
            center = camera.apply_pos(center)

        pygame.draw.circle(screen, self.color, center, self.radius, 3)
