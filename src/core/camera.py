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
        self.top_margin = 0
        self.bounds = None

    def set_map_size(self, map_width, map_height, top_margin=0):
        self.map_width = map_width
        self.map_height = map_height
        self.top_margin = max(0, int(top_margin))
        self.x = self.clamp_x(self.x)
        self.y = self.clamp_y(self.y)

    def set_bounds(self, bounds):
        self.bounds = bounds.copy()
        self.x = self.clamp_x(self.x)
        self.y = self.clamp_y(self.y)

    def clear_bounds(self):
        self.bounds = None
        self.x = self.clamp_x(self.x)
        self.y = self.clamp_y(self.y)

    def update(self, target_rect):
        target_x = target_rect.centerx - self.screen_width / 2
        target_y = target_rect.centery - self.screen_height / 2
        target_x = self.clamp_x(target_x)
        target_y = self.clamp_y(target_y)
        self.x += (target_x - self.x) * CAMERA_SMOOTHING
        self.y += (target_y - self.y) * CAMERA_SMOOTHING

    def clamp_x(self, value):
        if self.bounds is not None:
            min_x = self.bounds.left
            max_x = max(min_x, self.bounds.right - self.screen_width)
            return max(min_x, min(value, max_x))
        max_x = max(0, self.map_width - self.screen_width)
        return max(0, min(value, max_x))

    def clamp_y(self, value):
        if self.bounds is not None:
            min_y = self.bounds.top
            max_y = max(min_y, self.bounds.bottom - self.screen_height)
            return max(min_y, min(value, max_y))
        max_y = max(0, self.map_height - self.screen_height)
        min_y = -self.top_margin
        return max(min_y, min(value, max_y))

    def snap_to(self, target_rect):
        self.x = self.clamp_x(target_rect.centerx - self.screen_width / 2)
        self.y = self.clamp_y(target_rect.centery - self.screen_height / 2)

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
