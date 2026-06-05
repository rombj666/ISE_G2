from pathlib import Path

import pygame
from PIL import Image, ImageSequence

from settings import (
    DEBUG_ENEMY_HITBOX,
    ENEMY_ATTACK_TIME,
    ENEMY_MAX_HP,
    ENEMY_RESPAWN_TIME,
    GRAVITY,
    GRAPPLE_ENEMY_FINAL_STUN_TIME,
    GRAPPLE_PULL_SPEED,
    MELEE_DRAW_OFFSET_Y,
    MELEE_HP_BAR_OFFSET_Y,
    MELEE_SPAWN_OFFSET_Y,
    MELEE_VISUAL_SCALE,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MELEE_ASSET_DIR = PROJECT_ROOT / "assets" / "enemies" / "melee"
DEBUG_MELEE_AI = False
MELEE_DETECT_RANGE = 260
MELEE_ATTACK_RANGE = 65
MELEE_CHASE_MAX_DISTANCE = 9999
MELEE_RETURN_TOLERANCE = 20
MELEE_DAMAGE = 10
MELEE_SPEED = 1.5
MELEE_RETURN_SPEED = MELEE_SPEED
MELEE_JUMP_VELOCITY = -8
MELEE_STUCK_TIME_TO_JUMP = 0.35
MELEE_OBSTACLE_JUMP_COOLDOWN = 1.0
MELEE_ATTACK_COOLDOWN = 1.0
MELEE_ATTACK_ACTIVE_FRAME = 3
MELEE_DRAW_SIZE = (
    round(96 * MELEE_VISUAL_SCALE),
    round(96 * MELEE_VISUAL_SCALE),
)
MELEE_ANIMATION_SPEED = 0.1
MELEE_ANIMATIONS = None
MELEE_PLACEHOLDER_WARNING_PRINTED = False


def load_melee_gif_frames(path, target_size=MELEE_DRAW_SIZE):
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
    return frames


def get_melee_animations():
    global MELEE_ANIMATIONS, MELEE_PLACEHOLDER_WARNING_PRINTED
    if MELEE_ANIMATIONS is not None:
        return MELEE_ANIMATIONS

    exact_idle_east_path = MELEE_ASSET_DIR / "idle_east.gif"
    exact_idle_west_path = MELEE_ASSET_DIR / "idle_west.gif"
    exact_walk_east_path = MELEE_ASSET_DIR / "walk_east.gif"
    exact_walk_west_path = MELEE_ASSET_DIR / "walk_west.gif"
    exact_attack_east_path = MELEE_ASSET_DIR / "attack_east.gif"
    exact_attack_west_path = MELEE_ASSET_DIR / "attack_west.gif"
    idle_east_path = exact_idle_east_path if exact_idle_east_path.exists() else MELEE_ASSET_DIR / "melee_breathing-idle_east.gif"
    idle_west_path = exact_idle_west_path if exact_idle_west_path.exists() else MELEE_ASSET_DIR / "melee_breathing-idle_west.gif"
    walk_east_path = exact_walk_east_path if exact_walk_east_path.exists() else MELEE_ASSET_DIR / "melee_custom-Create_a_clear_walking_animati_east.gif"
    walk_west_path = exact_walk_west_path if exact_walk_west_path.exists() else MELEE_ASSET_DIR / "melee_custom-Create_a_clear_walking_animati_west.gif"
    attack_east_path = exact_attack_east_path if exact_attack_east_path.exists() else MELEE_ASSET_DIR / "melee_custom-Create_a_clear_and_dramatic_sw_east.gif"
    attack_west_path = exact_attack_west_path if exact_attack_west_path.exists() else MELEE_ASSET_DIR / "melee_custom-Create_a_clear_and_dramatic_sw_west.gif"

    MELEE_ANIMATIONS = {
        "idle": {
            "east": load_melee_gif_frames(idle_east_path),
            "west": load_melee_gif_frames(idle_west_path),
        },
        "walk": {
            "east": load_melee_gif_frames(walk_east_path),
            "west": load_melee_gif_frames(walk_west_path),
        },
        "attack": {
            "east": load_melee_gif_frames(attack_east_path),
            "west": load_melee_gif_frames(attack_west_path),
        },
    }

    print("[MELEE ASSET DEBUG]")
    print("Melee folder:", MELEE_ASSET_DIR)
    print("idle_east exists:", exact_idle_east_path.exists())
    print("walk_east exists:", exact_walk_east_path.exists())
    print("attack_east exists:", exact_attack_east_path.exists())
    print("idle frames:", len(MELEE_ANIMATIONS["idle"]["east"]))
    print("walk frames:", len(MELEE_ANIMATIONS["walk"]["east"]))
    print("attack frames:", len(MELEE_ANIMATIONS["attack"]["east"]))

    if not any(frames for states in MELEE_ANIMATIONS.values() for frames in states.values()):
        if not MELEE_PLACEHOLDER_WARNING_PRINTED:
            print("Melee enemy asset missing, using placeholder")
            MELEE_PLACEHOLDER_WARNING_PRINTED = True

    return MELEE_ANIMATIONS


class Enemy:
    def __init__(
        self,
        x,
        y,
        mode="patrol",
        patrol_left=80,
        patrol_right=80,
        index=None,
        debug_ai=False,
    ):
        self.rect = pygame.Rect(0, 0, 44, 60)
        self.rect.midbottom = (x, y)
        self.rect.y += MELEE_SPAWN_OFFSET_Y
        self.spawn_x = x
        self.spawn_y = y
        self.spawn_rect_x = self.rect.x
        self.spawn_rect_y = self.rect.y
        self.locked_static_x = self.rect.x
        self.locked_static_bottom = self.rect.bottom
        self.index = index
        self.debug_ai = debug_ai
        self.mode = mode
        self.stay_still = mode == "static"
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.patrol_min_x = x - patrol_left
        self.patrol_max_x = x + patrol_right
        self.max_hp = ENEMY_MAX_HP
        self.current_hp = self.max_hp
        self.damage = MELEE_DAMAGE
        self.active = True
        self.alive = True
        self.hurt_timer = 0
        self.respawn_timer = 0
        self.dropped_coins = False

        self.attack_cooldown_timer = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_hitbox = pygame.Rect(0, 0, MELEE_ATTACK_RANGE, self.rect.height)
        self.attack_has_hit = False
        self.has_hit_player_this_attack = False
        self.attack_frame_index = 0
        self.attack_is_active = False
        self.facing = -1
        self.patrol_direction = -1
        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.animations = get_melee_animations()

        self.stunned_timer = 0
        self.vel_x = 0
        self.vel_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration_x = 0
        self.on_ground = True
        self.last_x = self.rect.x
        self.stuck_timer = 0
        self.jump_cooldown = 0
        self.being_pulled = False
        self.pull_target_x = None
        self.frozen_timer = 0
        self.frozen = False
        self.freeze_timer = 0
        self.is_executable = False
        self.execute_timer = 0

    def take_damage(self, amount):
        if not self.active or not self.alive:
            return

        print(f"Enemy took {amount} damage, HP: {self.current_hp - amount} -> {self.current_hp}")  
        
        self.current_hp -= amount
        self.hurt_timer = 0.12

        if self.current_hp <= 0:
            self.die()

    def die(self):
        self.current_hp = 0
        self.alive = False
        self.respawn_timer = 0
        self.is_attacking = False
        self.being_pulled = False

    def respawn(self):
        self.rect.x = self.spawn_rect_x
        self.rect.y = self.spawn_rect_y
        self.active = True
        self.current_hp = self.max_hp
        self.alive = True
        self.dropped_coins = False
        self.hurt_timer = 0
        self.respawn_timer = 0

        self.stunned_timer = 0
        self.vel_x = 0
        self.vel_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration_x = 0
        self.on_ground = True
        self.last_x = self.rect.x
        self.stuck_timer = 0
        self.jump_cooldown = 0
        self.being_pulled = False
        self.pull_target_x = None
        self.frozen_timer = 0
        self.frozen = False
        self.freeze_timer = 0
        self.is_executable = False
        self.execute_timer = 0

        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown_timer = 0
        self.attack_has_hit = False
        self.has_hit_player_this_attack = False
        self.attack_frame_index = 0
        self.attack_is_active = False
        self.attack_hitbox = self.get_attack_hitbox()

    def respawn_at(self, x, y):
        self.spawn_x = x
        self.spawn_y = y
        self.rect.midbottom = (x, y)
        self.rect.y += MELEE_SPAWN_OFFSET_Y
        self.spawn_rect_x = self.rect.x
        self.spawn_rect_y = self.rect.y
        self.locked_static_x = self.rect.x
        self.locked_static_bottom = self.rect.bottom
        self.patrol_min_x = x - self.patrol_left
        self.patrol_max_x = x + self.patrol_right
        self.respawn()

    def disable(self):
        self.active = False
        self.alive = False
        self.current_hp = 0
        self.respawn_timer = 0
        self.dropped_coins = True
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown_timer = 0
        self.attack_has_hit = False
        self.has_hit_player_this_attack = False
        self.attack_frame_index = 0
        self.attack_is_active = False
        self.stunned_timer = 0
        self.frozen_timer = 0
        self.frozen = False
        self.freeze_timer = 0
        self.is_executable = False
        self.execute_timer = 0
        self.being_pulled = False
        self.pull_target_x = None
        self.vel_x = 0
        self.vel_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration_x = 0
        self.on_ground = True
        self.last_x = self.rect.x
        self.stuck_timer = 0
        self.jump_cooldown = 0

    def stun(self, duration):
        if not self.active:
            return

        self.stunned_timer = max(self.stunned_timer, duration)
        self.is_attacking = False
        self.stop_horizontal_motion()

    def freeze(self, duration):
        if not self.active:
            return

        self.frozen_timer = max(self.frozen_timer, duration)
        self.freeze_timer = self.frozen_timer
        self.frozen = True
        self.is_attacking = False
        self.stop_horizontal_motion()

    def mark_executable(self, duration):
        if not self.active:
            return

        self.is_executable = True
        self.execute_timer = duration

    def execute(self):
        if not self.active or not self.alive:
            return

        self.die()

    def start_pull_to_player(self, player):
        if self.mode == "static":
            return

        self.being_pulled = True
        self.stunned_timer = max(self.stunned_timer, 2.0)
        self.is_attacking = False

        if player.facing == 1:
            self.pull_target_x = player.rect.right + 20
        else:
            self.pull_target_x = player.rect.left - self.rect.width - 20

    def start_attack(self, player):
        self.is_attacking = True
        self.attack_cooldown_timer = MELEE_ATTACK_COOLDOWN
        self.attack_has_hit = False
        self.has_hit_player_this_attack = False
        self.attack_frame_index = 0
        self.attack_is_active = False
        self.vel_x = 0
        self.velocity_x = 0
        self.velocity_y = self.vel_y
        self.acceleration_x = 0
        self.state = "attack"
        self.frame_index = 0
        self.animation_timer = 0

        if player.rect.centerx < self.rect.centerx:
            self.facing = -1
        else:
            self.facing = 1

        self.attack_hitbox = self.get_attack_hitbox()
        attack_frames = self._current_frames()
        self.attack_timer = max(ENEMY_ATTACK_TIME, len(attack_frames) * MELEE_ANIMATION_SPEED)
        print("[MELEE ATTACK START]")
        print("enemy:", self.rect.center)
        print("player:", player.rect.center)
        print("facing:", self.facing)

    def get_attack_hitbox(self):
        if self.facing == 1:
            hitbox_x = self.rect.right - 5
        else:
            hitbox_x = self.rect.left - 50

        attack_rect = pygame.Rect(hitbox_x, self.rect.centery - 10, 55, 45)
        if self.is_attacking:
            print("[MELEE ATTACK BOX]", attack_rect)
        return attack_rect

    def update(self, dt, player=None, platforms=None):
        if not self.active:
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt

        if self.execute_timer > 0:
            self.execute_timer -= dt

            if self.execute_timer <= 0:
                self.is_executable = False

        if not self.alive:
            return

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt

        if self.stunned_timer > 0:
            self.stunned_timer -= dt

        if self.frozen_timer > 0:
            self.frozen_timer -= dt
            self.freeze_timer = self.frozen_timer
            self.is_attacking = False
            self.attack_has_hit = False
            if self.mode == "static":
                self.lock_static_position()
            return
        self.frozen = False
        self.freeze_timer = 0

        if self.being_pulled:
            self.update_pull()
            return

        if self.stunned_timer > 0:
            if self.mode == "static":
                self.lock_static_position()
            return

        platforms = platforms or []
        self.update_vertical_motion(platforms)
        self.update_jump_cooldown(dt)

        if self.is_attacking:
            self.attack_timer -= dt
            self.attack_hitbox = self.get_attack_hitbox()
            self._animate(dt)
            self.attack_frame_index = self.frame_index
            self.attack_is_active = self.attack_frame_index >= MELEE_ATTACK_ACTIVE_FRAME
            if self.attack_timer <= 0:
                self.is_attacking = False
                self.state = "idle"
                self.attack_is_active = False

        if player is None or player.is_dead or self.is_attacking:
            return

        horizontal_distance = abs(player.rect.centerx - self.rect.centerx)
        vertical_distance = abs(player.rect.centery - self.rect.centery)
        distance_to_player = horizontal_distance
        distance_to_spawn = abs(self.rect.centerx - self.spawn_x)
        player_in_detect_range = (
            distance_to_player <= MELEE_DETECT_RANGE
            and vertical_distance <= self.rect.height * 2
            and distance_to_spawn <= MELEE_CHASE_MAX_DISTANCE
        )
        player_in_attack_range = (
            distance_to_player <= MELEE_ATTACK_RANGE
            and vertical_distance <= self.rect.height
        )

        self.print_ai_debug(player, distance_to_player, distance_to_spawn)

        if player_in_detect_range:
            self.face_player(player)

        if player_in_attack_range:
            self.stop_horizontal_motion()
            if self.attack_cooldown_timer <= 0:
                self.start_attack(player)
            else:
                self.state = "idle"
                self._animate(dt)
            return

        if player_in_detect_range:
            self.chase_player(player, platforms, dt)
            return

        if distance_to_spawn > MELEE_RETURN_TOLERANCE:
            self.return_to_spawn(platforms, dt)
            return

        if self.stay_still:
            self.lock_static_position()
            self.stop_horizontal_motion()
            self.state = "idle"
            self._animate(dt)
            return

        self.patrol(platforms, dt)

    def face_player(self, player):
        if player.rect.centerx < self.rect.centerx:
            self.facing = -1
        else:
            self.facing = 1

    def lock_static_position(self):
        self.rect.x = self.locked_static_x

    def stop_horizontal_motion(self):
        self.vel_x = 0
        self.velocity_x = 0
        self.acceleration_x = 0

    def chase_player(self, player, platforms, dt):
        direction = 1 if player.rect.centerx > self.rect.centerx else -1
        self.patrol_direction = direction
        self.try_move_horizontal(direction, platforms, "chase", dt, clamp_to_patrol=False)

    def return_to_spawn(self, platforms, dt):
        if abs(self.rect.centerx - self.spawn_x) <= MELEE_RETURN_TOLERANCE:
            self.stop_horizontal_motion()
            self.rect.centerx = self.spawn_x
            self.state = "idle" if self.stay_still else "patrol"
            self._animate(dt)
            return

        direction = 1 if self.spawn_x > self.rect.centerx else -1
        self.patrol_direction = direction
        self.try_move_horizontal(
            direction,
            platforms,
            "return",
            dt,
            clamp_to_patrol=False,
            speed=MELEE_RETURN_SPEED,
        )

    def patrol(self, platforms, dt):
        if self.rect.centerx <= self.patrol_min_x:
            self.patrol_direction = 1
        elif self.rect.centerx >= self.patrol_max_x:
            self.patrol_direction = -1

        moved = self.try_move_horizontal(self.patrol_direction, platforms, "patrol", dt)
        if not moved:
            self.patrol_direction *= -1
        if self.debug_ai:
            print(
                "[MELEE PATROL]",
                self.index,
                self.rect.x,
                self.patrol_min_x,
                self.patrol_max_x,
                self.patrol_direction,
            )

    def try_move_horizontal(
        self,
        direction,
        platforms,
        state,
        dt,
        clamp_to_patrol=True,
        speed=MELEE_SPEED,
    ):
        self.facing = direction
        self.vel_x = direction * speed
        self.velocity_x = self.vel_x
        next_rect = self.rect.copy()
        next_rect.x = round(self.rect.x + self.vel_x)

        if clamp_to_patrol:
            if next_rect.centerx < self.patrol_min_x:
                next_rect.centerx = round(self.patrol_min_x)
                self.patrol_direction = 1
            elif next_rect.centerx > self.patrol_max_x:
                next_rect.centerx = round(self.patrol_max_x)
                self.patrol_direction = -1

        wall_ahead = self.hits_wall(next_rect, platforms)
        ground_ahead = self.has_ground_ahead(next_rect, platforms)
        if wall_ahead:
            self.try_obstacle_jump()

        if not ground_ahead or wall_ahead:
            self.vel_x = 0
            self.velocity_x = 0
            self.state = state
            self._animate(dt)
            return False

        self.rect.x = next_rect.x
        self.state = state
        self._animate(dt)
        self.update_stuck_detection(dt)
        return True

    def has_ground_ahead(self, next_rect, platforms):
        probe_x = next_rect.right + 4 if self.facing > 0 else next_rect.left - 4
        ground_probe = pygame.Rect(probe_x, next_rect.bottom, 6, 14)
        return any(ground_probe.colliderect(platform) for platform in platforms)

    def hits_wall(self, next_rect, platforms):
        wall_probe = pygame.Rect(next_rect.x, next_rect.y + 8, next_rect.width, next_rect.height - 16)
        for platform in platforms:
            if wall_probe.colliderect(platform) and platform.top < self.rect.bottom - 8:
                return True
        return False

    def update_vertical_motion(self, platforms):
        if not platforms:
            self.on_ground = True
            self.vel_y = 0
            self.velocity_y = 0
            return

        if not self.on_ground or self.vel_y != 0:
            self.vel_y += GRAVITY

        self.rect.y += round(self.vel_y)
        self.on_ground = False

        for platform in platforms:
            if not self.rect.colliderect(platform):
                continue

            if self.vel_y >= 0:
                self.rect.bottom = platform.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = platform.bottom
                self.vel_y = 0

        if not self.on_ground:
            ground_probe = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, 4)
            self.on_ground = any(ground_probe.colliderect(platform) for platform in platforms)

        self.velocity_y = self.vel_y

    def update_jump_cooldown(self, dt):
        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt

    def update_stuck_detection(self, dt):
        if abs(self.rect.x - self.last_x) < 1 and abs(self.velocity_x) > 0:
            self.stuck_timer += dt
        else:
            self.stuck_timer = 0

        self.last_x = self.rect.x

        if self.stuck_timer >= MELEE_STUCK_TIME_TO_JUMP:
            self.try_obstacle_jump()

    def try_obstacle_jump(self):
        if not self.on_ground or self.jump_cooldown > 0:
            return False

        self.vel_y = MELEE_JUMP_VELOCITY
        self.velocity_y = self.vel_y
        self.on_ground = False
        self.stuck_timer = 0
        self.jump_cooldown = MELEE_OBSTACLE_JUMP_COOLDOWN
        print("[MELEE JUMP UNSTUCK]", self.rect, "state:", self.state)
        return True

    def print_ai_debug(self, player, distance_to_player, distance_to_spawn):
        if not (DEBUG_MELEE_AI or self.debug_ai):
            return

        print("[MELEE AI]")
        print("state:", self.state)
        print("mode:", self.mode)
        print("enemy x:", self.rect.centerx)
        print("spawn x:", self.spawn_x)
        print("player x:", player.rect.centerx)
        print("distance_to_player:", distance_to_player)
        print("distance_to_spawn:", distance_to_spawn)
        print("velocity_x:", self.velocity_x)

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

    def _current_frames(self):
        direction = "east" if self.facing > 0 else "west"
        animation_state = self.state
        if animation_state in ("patrol", "chase", "return"):
            animation_state = "walk"

        frames = self.animations.get(animation_state, {}).get(direction, [])
        if not frames and self.state != "idle":
            frames = self.animations.get("idle", {}).get(direction, [])
        return frames

    def _animate(self, dt):
        frames = self._current_frames()
        if not frames:
            return

        self.animation_timer += dt
        if self.animation_timer >= MELEE_ANIMATION_SPEED:
            self.animation_timer = 0
            if self.state == "attack":
                self.frame_index = min(self.frame_index + 1, len(frames) - 1)
            else:
                self.frame_index = (self.frame_index + 1) % len(frames)

    def draw(self, screen, camera=None):
        if not self.active or not self.alive:
            return

        if self.frozen_timer > 0:
            color = (120, 220, 255)
        elif self.being_pulled:
            color = (180, 80, 255)
        elif self.stunned_timer > 0:
            color = (255, 220, 80)
        elif self.hurt_timer > 0:
            color = (255, 220, 220)
        else:
            color = (220, 50, 50)

        frames = self._current_frames()
        draw_rect = self.rect
        visual_rect = None
        if frames:
            frame = frames[min(self.frame_index, len(frames) - 1)]
            visual_rect = frame.get_rect(midbottom=(self.rect.centerx, self.rect.bottom + MELEE_DRAW_OFFSET_Y))
            draw_rect = visual_rect
            if camera:
                draw_rect = camera.apply_rect(visual_rect)
            screen.blit(frame, draw_rect)
        else:
            if camera:
                draw_rect = camera.apply_rect(self.rect)
            pygame.draw.rect(screen, color, draw_rect)

        if self.is_executable:
            pygame.draw.rect(screen, (255, 240, 80), draw_rect.inflate(8, 8), 3)

        if self.being_pulled:
            pygame.draw.rect(screen, (240, 220, 255), draw_rect, 2)

        if DEBUG_ENEMY_HITBOX:
            collision_rect = self.rect
            attack_rect = self.get_attack_hitbox()
            if camera:
                collision_rect = camera.apply_rect(collision_rect)
                attack_rect = camera.apply_rect(attack_rect)
            pygame.draw.rect(screen, (80, 255, 120), collision_rect, 2)
            if self.is_attacking:
                pygame.draw.rect(screen, (255, 60, 60), attack_rect, 2)

        self.draw_hp_bar(screen, camera, visual_rect)

    def draw_hp_bar(self, screen, camera=None, visual_rect=None):
        bar_width = self.rect.width
        bar_height = 6
        if visual_rect is not None:
            bar_x = visual_rect.centerx - bar_width // 2
            bar_y = visual_rect.top + MELEE_HP_BAR_OFFSET_Y
        else:
            bar_x = self.rect.x
            bar_y = self.rect.y + MELEE_HP_BAR_OFFSET_Y

        hp_percent = self.current_hp / self.max_hp
        fill_width = int(bar_width * hp_percent)

        background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)

        if camera:
            background_rect = camera.apply_rect(background_rect)
            fill_rect = camera.apply_rect(fill_rect)

        pygame.draw.rect(screen, (60, 20, 20), background_rect)
        pygame.draw.rect(screen, (50, 220, 80), fill_rect)
