import pygame
from settings import DEBUG_DRAW_HITBOXES


class Room:
    def __init__(
        self,
        room_id,
        name,
        platforms,
        player_spawn,
        enemy_spawn,
        fulcrums,
        exit_rect,
        exit_target_room,
        shop_rect=None,
    ):
        self.room_id = room_id
        self.name = name
        self.platforms = platforms
        self.player_spawn = player_spawn
        self.enemy_spawn = enemy_spawn
        self.fulcrums = fulcrums
        self.exit_rect = exit_rect
        self.exit_target_room = exit_target_room
        self.shop_rect = shop_rect

    def draw(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, (120, 120, 130), platform)

        if self.exit_rect is not None:
            if DEBUG_DRAW_HITBOXES:
                pygame.draw.rect(screen, (60, 220, 100), self.exit_rect)
                pygame.draw.rect(screen, (220, 255, 220), self.exit_rect, 2)

            font = pygame.font.Font(None, 28)
            text = font.render("Exit", True, (20, 40, 20))
            text_rect = text.get_rect(center=self.exit_rect.center)
            screen.blit(text, text_rect)

    def get_platforms(self):
        return self.platforms

    def get_player_spawn(self):
        return self.player_spawn

    def get_enemy_spawn(self):
        return self.enemy_spawn

    def get_fulcrums(self):
        return self.fulcrums

    def get_exit_rect(self):
        return self.exit_rect

    def get_shop_rect(self):
        return self.shop_rect
