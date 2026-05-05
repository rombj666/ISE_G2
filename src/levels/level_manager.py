import pygame

from settings import (
    DOOR_HEIGHT,
    DOOR_WIDTH,
    FULCRUM_RADIUS,
    MAP_0_HEIGHT,
    MAP_0_WIDTH,
    MAP_1_HEIGHT,
    MAP_1_WIDTH,
    MAP_2_HEIGHT,
    MAP_2_WIDTH,
    SCREEN_HEIGHT,
)
from src.levels.game_map import GameMap


class LevelManager:
    def __init__(self):
        self.maps = self.build_maps()
        self.current_map_id = 0
        self.current_map = self.maps[self.current_map_id]

    def build_maps(self):
        return {
            0: GameMap(
                0,
                "Settings / Shrine Room",
                MAP_0_WIDTH,
                MAP_0_HEIGHT,
                [
                    pygame.Rect(0, 650, MAP_0_WIDTH, 70),
                    pygame.Rect(520, 540, 180, 28),
                    pygame.Rect(880, 485, 180, 28),
                ],
                (120, 650),
                [
                    {
                        "rect": pygame.Rect(1480, 560, DOOR_WIDTH, DOOR_HEIGHT),
                        "target_map": 1,
                        "label": "Start",
                    }
                ],
                shop_rect=pygame.Rect(220, 560, 120, 90),
                map_type="safe_room",
            ),
            1: GameMap(
                1,
                "Normal Map",
                MAP_1_WIDTH,
                MAP_1_HEIGHT,
                [
                    pygame.Rect(0, 650, MAP_1_WIDTH, 70),
                    pygame.Rect(360, 540, 220, 30),
                    pygame.Rect(760, 470, 240, 30),
                    pygame.Rect(1180, 550, 260, 30),
                    pygame.Rect(1600, 460, 240, 30),
                    pygame.Rect(2020, 535, 220, 30),
                    pygame.Rect(2360, 475, 220, 30),
                    pygame.Rect(0, SCREEN_HEIGHT - 20, MAP_1_WIDTH, 20),
                ],
                (100, 650),
                [
                    {
                        "rect": pygame.Rect(2700, 560, DOOR_WIDTH, DOOR_HEIGHT),
                        "target_map": 2,
                        "label": "Boss",
                    }
                ],
                enemy_spawns=[(900, 590)],
                fulcrums=[
                    {
                        "rect": pygame.Rect(1510, 500, FULCRUM_RADIUS * 2, FULCRUM_RADIUS * 2),
                        "anchor": (1524, 514),
                        "target": (1715, 428),
                        "used": False,
                    }
                ],
                map_type="normal_stage",
            ),
            2: GameMap(
                2,
                "Boss Map",
                MAP_2_WIDTH,
                MAP_2_HEIGHT,
                [
                    pygame.Rect(0, 650, MAP_2_WIDTH, 70),
                    pygame.Rect(560, 520, 260, 30),
                    pygame.Rect(1220, 500, 260, 30),
                    pygame.Rect(0, SCREEN_HEIGHT - 20, MAP_2_WIDTH, 20),
                ],
                (100, 650),
                [
                    {
                        "rect": pygame.Rect(2100, 560, DOOR_WIDTH, DOOR_HEIGHT),
                        "target_map": "victory",
                        "label": "Exit",
                    }
                ],
                boss_spawn=(1500, 590),
                map_type="boss_stage",
            ),
        }

    def get_current_map(self):
        return self.current_map

    def change_map(self, target_map_id, player, enemy, camera=None):
        if target_map_id not in self.maps:
            return False

        self.current_map_id = target_map_id
        self.current_map = self.maps[self.current_map_id]

        player.rect.midbottom = self.current_map.player_spawn
        player.vel_x = 0
        player.vel_y = 0
        player.is_dashing = False
        player.is_attacking = False
        player.is_auto_grappling = False
        player.is_blocking = False
        player.is_parrying = False
        player.attack_has_hit = False
        player.should_spawn_projectile = False
        player.has_active_shield_throw = False
        player.auto_grapple_start = None
        player.auto_grapple_end = None
        player.auto_grapple_control = None
        player.auto_grapple_anchor = None
        player.soul_anchor_active = False
        player.soul_anchor_pos = None
        player.soul_anchor_timer = 0

        enemy_spawn = self.get_active_enemy_spawn()
        if enemy_spawn is None:
            enemy.disable()
        else:
            enemy.respawn_at(enemy_spawn[0], enemy_spawn[1])

        if camera is not None:
            camera.set_map_size(self.current_map.width, self.current_map.height)
            camera.snap_to(player.rect)

        print(f"Entered {self.current_map.name}")
        return True

    def get_active_enemy_spawn(self):
        if self.current_map.enemy_spawns:
            return self.current_map.enemy_spawns[0]

        if self.current_map.boss_spawn is not None:
            return self.current_map.boss_spawn

        return None

    def get_platforms(self):
        return self.current_map.platforms

    def get_fulcrums(self):
        return self.current_map.fulcrums

    def get_shop_rect(self):
        return self.current_map.shop_rect

    def get_doors(self):
        return self.current_map.doors

    def draw_current_map(self, screen, camera):
        font = pygame.font.Font(None, 28)

        for platform in self.current_map.platforms:
            draw_rect = platform
            if camera is not None:
                draw_rect = camera.apply_rect(platform)
            pygame.draw.rect(screen, (120, 120, 130), draw_rect)

        for door in self.current_map.doors:
            draw_rect = door["rect"]
            if camera is not None:
                draw_rect = camera.apply_rect(door["rect"])
            pygame.draw.rect(screen, (60, 220, 100), draw_rect)
            pygame.draw.rect(screen, (220, 255, 220), draw_rect, 2)
            text = font.render(door["label"], True, (20, 40, 20))
            screen.blit(text, text.get_rect(center=draw_rect.center))

    def check_doors(self, player):
        for door in self.current_map.doors:
            if player.rect.colliderect(door["rect"]):
                return door

        return None

    # Backward-friendly names for older code and beginner readability.
    def get_current_room(self):
        return self.get_current_map()

    def change_room(self, room_id, player, enemy):
        return self.change_map(room_id, player, enemy)

    def draw_current_room(self, screen):
        self.draw_current_map(screen, None)

    def get_current_platforms(self):
        return self.get_platforms()

    def get_current_fulcrums(self):
        return self.get_fulcrums()
