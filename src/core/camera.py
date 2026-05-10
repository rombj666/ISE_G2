import pygame

from settings import CAMERA_SMOOTHING


class Camera:
    def __init__(self, screen_width, screen_height, map_width, map_height):
        self.x = 0
        self.y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height

    def set_map_size(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.x = self.clamp_x(self.x)
        self.y = 0

    def update(self, target_rect):
        target_x = target_rect.centerx - self.screen_width / 2
        target_x = self.clamp_x(target_x)
        self.x += (target_x - self.x) * CAMERA_SMOOTHING
        self.y = 0

    def clamp_x(self, value):
        max_x = max(0, self.map_width - self.screen_width)
        return max(0, min(value, max_x))

    def snap_to(self, target_rect):
        self.x = self.clamp_x(target_rect.centerx - self.screen_width / 2)
        self.y = 0

    def apply_rect(self, rect):
        return pygame.Rect(
            round(rect.x - self.x),
            round(rect.y - self.y),
            rect.width,
            rect.height
        )

    def apply_pos(self, pos):
        return (
            round(pos[0] - self.x),
            round(pos[1] - self.y)
        )
