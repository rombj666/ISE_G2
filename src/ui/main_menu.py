import math

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH, TITLE
from src.entities.player import Player


class MainMenu:
    def __init__(self):
        self.should_start_game = False
        self.should_quit = False
        self.time = 0.0
        self.orb_x = SCREEN_WIDTH * 0.38
        self.orb_y = SCREEN_HEIGHT * 0.38
        self.menu_player = Player(0, 0)
        self.start_rect = pygame.Rect(96, 292, 280, 58)
        self.quit_rect = pygame.Rect(96, 370, 280, 58)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.should_start_game = True
            elif event.key == pygame.K_ESCAPE:
                self.should_quit = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_rect.collidepoint(event.pos):
                self.should_start_game = True
            elif self.quit_rect.collidepoint(event.pos):
                self.should_quit = True

    def update(self, dt):
        self.time += dt
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.orb_x += (mouse_x - self.orb_x) * 0.16
        self.orb_y += (mouse_y - self.orb_y) * 0.16

    def draw(self, screen):
        screen.fill((7, 9, 17))
        self._draw_background(screen)
        self._draw_orb_light(screen)

        title_font = pygame.font.Font(None, 84)
        hint_font = pygame.font.Font(None, 25)
        button_font = pygame.font.Font(None, 38)

        title = title_font.render(TITLE, True, (226, 242, 255))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 104)))

        hint = hint_font.render("Press Enter to begin", True, (145, 183, 218))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 154)))

        self._draw_button(screen, self.start_rect, "Start Game", button_font)
        self._draw_button(screen, self.quit_rect, "Quit", button_font)
        self._draw_platform(screen)
        self._draw_character(screen)
        self._draw_orb(screen)

    def _draw_background(self, screen):
        horizon_y = SCREEN_HEIGHT - 86
        pygame.draw.rect(screen, (13, 16, 28), (0, horizon_y, SCREEN_WIDTH, SCREEN_HEIGHT - horizon_y))
        pygame.draw.line(screen, (47, 82, 114), (0, horizon_y), (SCREEN_WIDTH, horizon_y), 2)

        for i in range(70):
            x = (i * 127 + 31) % SCREEN_WIDTH
            y = 34 + (i * 53) % 390
            alpha = 55 + (i * 29) % 130
            star = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(star, (172, 216, 255, alpha), (2, 2), 1)
            screen.blit(star, (x, y))

        for i in range(18):
            x = (i * 211 + int(self.time * 14)) % SCREEN_WIDTH
            y = 185 + (i * 37) % 330
            radius = 2 + i % 3
            alpha = 30 + (i * 11) % 45
            particle = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle, (130, 205, 255, alpha), (radius, radius), radius)
            screen.blit(particle, (x, y))

    def _draw_platform(self, screen):
        platform = pygame.Rect(742, SCREEN_HEIGHT - 76, 330, 10)
        glow = pygame.Surface((platform.width + 80, 44), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (90, 165, 225, 42), glow.get_rect())
        screen.blit(glow, (platform.x - 40, platform.y - 18))
        pygame.draw.rect(screen, (72, 105, 132), platform)
        pygame.draw.line(screen, (168, 218, 248), platform.topleft, platform.topright, 2)

    def _draw_button(self, screen, rect, text, font):
        mouse_over = rect.collidepoint(pygame.mouse.get_pos())
        fill = (35, 57, 84) if mouse_over else (18, 28, 46)
        border = (168, 225, 255) if mouse_over else (77, 128, 170)
        text_color = (255, 255, 255) if mouse_over else (223, 237, 250)

        pygame.draw.rect(screen, fill, rect, border_radius=6)
        pygame.draw.rect(screen, border, rect, 2, border_radius=6)
        label = font.render(text, True, text_color)
        screen.blit(label, label.get_rect(center=rect.center))

    def _draw_character(self, screen):
        breathe = math.sin(self.time * 2.0) * 2
        character_rect = pygame.Rect(0, 0, 72, 96)
        character_rect.midbottom = (910, SCREEN_HEIGHT - 80 + int(breathe))

        self.menu_player.facing = -1 if self.orb_x < character_rect.centerx else 1
        self.menu_player.draw_kael_template(screen, character_rect, (180, 220, 255))
        self._draw_eye_glow(screen, character_rect)

    def _draw_eye_glow(self, screen, character_rect):
        direction = pygame.Vector2(
            self.orb_x - character_rect.centerx,
            self.orb_y - (character_rect.y + 18),
        )
        if direction.length() > 0:
            direction = direction.normalize()

        eye_shift_x = max(-4, min(4, int(direction.x * 4)))
        eye_shift_y = max(-3, min(3, int(direction.y * 3)))
        eye_y = character_rect.y + 17 + eye_shift_y

        if self.menu_player.facing == 1:
            eye_x = character_rect.x + 34 + eye_shift_x
        else:
            eye_x = character_rect.x + 28 + eye_shift_x

        glow = pygame.Surface((22, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (125, 215, 255, 72), glow.get_rect())
        screen.blit(glow, (eye_x - 11, eye_y - 7))
        pygame.draw.rect(screen, (230, 250, 255), (eye_x - 2, eye_y - 1, 5, 3))

    def _draw_orb_light(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        hover_button = self.start_rect.collidepoint(mouse_pos) or self.quit_rect.collidepoint(mouse_pos)
        radius = 145 if hover_button else 118
        alpha = 54 if hover_button else 34
        light = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(light, (110, 200, 255, alpha), (radius, radius), radius)
        pygame.draw.circle(light, (210, 240, 255, alpha // 2), (radius, radius), radius // 2)
        screen.blit(light, (int(self.orb_x) - radius, int(self.orb_y) - radius))

    def _draw_orb(self, screen):
        sx = int(self.orb_x)
        sy = int(self.orb_y)
        hover_button = self.start_rect.collidepoint(pygame.mouse.get_pos()) or self.quit_rect.collidepoint(pygame.mouse.get_pos())
        pulse = (math.sin(self.time * 3.2) + 1.0) * 0.5

        layers = ((52, 30), (34, 62), (20, 118)) if hover_button else ((44, 22), (28, 48), (17, 92))
        for radius, alpha in layers:
            glow_radius = int(radius + pulse * 5)
            glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (135, 210, 255, alpha), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow, (sx - glow_radius, sy - glow_radius))

        pygame.draw.circle(screen, (226, 248, 255), (sx, sy), 8)
        pygame.draw.circle(screen, (112, 194, 255), (sx, sy), 15, 2)
        pygame.draw.circle(screen, (255, 255, 255), (sx - 3, sy - 3), 3)
