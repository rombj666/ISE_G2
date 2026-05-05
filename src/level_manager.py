import pygame

from settings import FULCRUM_RADIUS, SCREEN_HEIGHT, SCREEN_WIDTH
from src.room import Room


class LevelManager:
    def __init__(self):
        self.rooms = self.create_test_rooms()
        self.current_room_id = 0

    def create_test_rooms(self):
        ground = pygame.Rect(0, 650, SCREEN_WIDTH, 70)

        return {
            0: Room(
                0,
                "Start / Shrine Room",
                [
                    ground.copy(),
                    pygame.Rect(260, 540, 180, 30),
                ],
                (110, 650),
                None,
                [],
                pygame.Rect(SCREEN_WIDTH - 60, 560, 50, 90),
                1,
                pygame.Rect(180, 570, 70, 80),
            ),
            1: Room(
                1,
                "Combat Room",
                [
                    ground.copy(),
                    pygame.Rect(260, 530, 190, 30),
                    pygame.Rect(650, 445, 220, 30),
                ],
                (90, 650),
                (700, 590),
                [],
                pygame.Rect(SCREEN_WIDTH - 60, 560, 50, 90),
                2,
            ),
            2: Room(
                2,
                "Grapple Room",
                [
                    pygame.Rect(0, 650, 360, 70),
                    pygame.Rect(520, 650, SCREEN_WIDTH - 520, 70),
                    pygame.Rect(760, 430, 230, 30),
                    pygame.Rect(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20),
                ],
                (100, 650),
                None,
                [
                    {
                        "rect": pygame.Rect(430, 520, FULCRUM_RADIUS * 2, FULCRUM_RADIUS * 2),
                        "anchor": (444, 534),
                        "target": (835, 398),
                        "used": False,
                    }
                ],
                pygame.Rect(SCREEN_WIDTH - 60, 560, 50, 90),
                3,
            ),
            3: Room(
                3,
                "Exit Room",
                [
                    ground.copy(),
                ],
                (110, 650),
                None,
                [],
                None,
                None,
            ),
        }

    def get_current_room(self):
        return self.rooms[self.current_room_id]

    def change_room(self, room_id, player, enemy):
        if room_id not in self.rooms:
            return False

        self.current_room_id = room_id
        room = self.get_current_room()

        player.rect.midbottom = room.get_player_spawn()
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

        enemy_spawn = room.get_enemy_spawn()
        if enemy_spawn is None:
            enemy.disable()
        else:
            enemy.respawn_at(enemy_spawn[0], enemy_spawn[1])

        print(f"Entered {room.name}")
        return True

    def draw_current_room(self, screen):
        self.get_current_room().draw(screen)

    def get_current_platforms(self):
        return self.get_current_room().get_platforms()

    def get_current_fulcrums(self):
        return self.get_current_room().get_fulcrums()

    def check_room_exit(self, player):
        room = self.get_current_room()
        exit_rect = room.get_exit_rect()

        if exit_rect is None:
            return None

        if player.rect.colliderect(exit_rect):
            return room.exit_target_room

        return None
