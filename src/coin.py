import pygame

from settings import COIN_BOUNCE_SPEED, COIN_GRAVITY, COIN_RADIUS


class Coin:
    def __init__(self, x, y, value):
        self.rect = pygame.Rect(x - COIN_RADIUS, y - COIN_RADIUS, COIN_RADIUS * 2, COIN_RADIUS * 2)
        self.value = value
        self.vel_y = COIN_BOUNCE_SPEED
        self.collected = False

    def update(self, dt, platforms):
        if self.collected:
            return

        self.vel_y += COIN_GRAVITY
        self.rect.y += self.vel_y

        for platform in platforms:
            if self.rect.colliderect(platform) and self.vel_y > 0:
                self.rect.bottom = platform.top
                self.vel_y = 0

    def draw(self, screen):
        if self.collected:
            return

        pygame.draw.circle(screen, (255, 220, 60), self.rect.center, COIN_RADIUS)
