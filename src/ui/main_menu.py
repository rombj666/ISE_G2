import math
from pathlib import Path

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UNARMED_IDLE_PATH = PROJECT_ROOT / "assets" / "animations" / "idle_withoutweapon.png"
UNARMED_IDLE_FRAME_COUNT = 4
UNARMED_IDLE_TARGET_HEIGHT = 132


def load_unarmed_idle_frames():
    print("Main menu unarmed idle path:", UNARMED_IDLE_PATH)
    if not UNARMED_IDLE_PATH.exists():
        print("WARNING: Main menu unarmed idle sheet missing:", UNARMED_IDLE_PATH)
        return []

    try:
        sheet = pygame.image.load(str(UNARMED_IDLE_PATH)).convert_alpha()
    except pygame.error as exc:
        print("WARNING: Failed to load main menu unarmed idle sheet:", UNARMED_IDLE_PATH, exc)
        return []

    frame_width = sheet.get_width() // UNARMED_IDLE_FRAME_COUNT
    frame_height = sheet.get_height()
    if frame_width <= 0 or sheet.get_width() % UNARMED_IDLE_FRAME_COUNT != 0:
        print("WARNING: Main menu unarmed idle sheet has unexpected size:", UNARMED_IDLE_PATH, sheet.get_size())
        return []

    frames = []
    for index in range(UNARMED_IDLE_FRAME_COUNT):
        source_rect = pygame.Rect(index * frame_width, 0, frame_width, frame_height)
        frame = pygame.Surface(source_rect.size, pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), source_rect)
        scale = UNARMED_IDLE_TARGET_HEIGHT / frame_height
        scaled_size = (max(1, round(frame_width * scale)), UNARMED_IDLE_TARGET_HEIGHT)
        frames.append(pygame.transform.smoothscale(frame, scaled_size))

    print("Main menu unarmed idle frame count:", len(frames))
    print("Main menu unarmed idle frame size:", frames[0].get_size() if frames else None)
    return frames


class MainMenu:
    def __init__(self):
        self.should_start_game = False
        self.should_quit = False
        self.time = 0.0
        self.orb_x = SCREEN_WIDTH * 0.38
        self.orb_y = SCREEN_HEIGHT * 0.38
        self.menu_facing = 1
        self.start_rect = pygame.Rect(96, 292, 280, 58)
        self.quit_rect = pygame.Rect(96, 370, 280, 58)
        self.unarmed_idle_frames = load_unarmed_idle_frames()
        self.unarmed_idle_index = 0
        self.unarmed_idle_timer = 0.0
        self.unarmed_idle_frame_time = 0.24

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
        if self.unarmed_idle_frames:
            self.unarmed_idle_timer += dt
            if self.unarmed_idle_timer >= self.unarmed_idle_frame_time:
                self.unarmed_idle_timer = 0.0
                self.unarmed_idle_index = (self.unarmed_idle_index + 1) % len(self.unarmed_idle_frames)

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
        character_rect = pygame.Rect(0, 0, 88, UNARMED_IDLE_TARGET_HEIGHT)
        character_rect.midbottom = (910, SCREEN_HEIGHT - 80 + int(breathe))

        self.menu_facing = -1 if self.orb_x < character_rect.centerx else 1
        if self.unarmed_idle_frames:
            frame = self.unarmed_idle_frames[self.unarmed_idle_index]
            image = pygame.transform.flip(frame, True, False) if self.menu_facing < 0 else frame
            draw_rect = image.get_rect(midbottom=character_rect.midbottom)
            screen.blit(image, draw_rect)
            return

        self._draw_kael_preview(screen, character_rect)
        self._draw_eye_glow(screen, character_rect)

    def _draw_kael_preview(self, screen, rect):
        x = rect.x
        y = rect.y
        scale_x = rect.width / 48
        scale_y = rect.height / 64

        def scaled_rect(px, py, pw, ph):
            return pygame.Rect(
                x + int(px * scale_x),
                y + int(py * scale_y),
                max(1, int(pw * scale_x)),
                max(1, int(ph * scale_y)),
            )

        armor_dark = (30, 34, 48)
        armor_mid = (58, 64, 86)
        armor_light = (105, 116, 145)
        moon_core = (150, 220, 255)
        moon_glow = (90, 170, 230)
        shadow = (12, 14, 22)

        pygame.draw.rect(screen, moon_glow, scaled_rect(17, -8, 14, 3))
        pygame.draw.rect(screen, moon_core, scaled_rect(21, -13, 6, 6))
        pygame.draw.rect(screen, armor_mid, scaled_rect(13, 4, 22, 18))
        pygame.draw.rect(screen, armor_light, scaled_rect(16, 7, 16, 3))
        pygame.draw.rect(screen, shadow, scaled_rect(17, 13, 14, 4))
        pygame.draw.rect(screen, armor_dark, scaled_rect(10, 24, 28, 25))
        pygame.draw.rect(screen, armor_mid, scaled_rect(13, 27, 22, 18))
        pygame.draw.rect(screen, moon_glow, scaled_rect(18, 29, 12, 12), 1)
        pygame.draw.rect(screen, moon_core, scaled_rect(20, 31, 8, 8))
        pygame.draw.rect(screen, armor_light, scaled_rect(5, 25, 8, 10))
        pygame.draw.rect(screen, armor_light, scaled_rect(35, 25, 8, 10))

        if self.menu_facing == 1:
            front_arm = scaled_rect(37, 35, 7, 18)
            back_arm = scaled_rect(4, 35, 6, 15)
        else:
            front_arm = scaled_rect(4, 35, 7, 18)
            back_arm = scaled_rect(38, 35, 6, 15)

        pygame.draw.rect(screen, armor_mid, back_arm)
        pygame.draw.rect(screen, armor_light, front_arm)
        pygame.draw.rect(screen, armor_dark, scaled_rect(12, 49, 9, 15))
        pygame.draw.rect(screen, armor_dark, scaled_rect(27, 49, 9, 15))
        pygame.draw.rect(screen, armor_light, scaled_rect(12, 60, 10, 4))
        pygame.draw.rect(screen, armor_light, scaled_rect(27, 60, 10, 4))
        pygame.draw.rect(screen, shadow, rect, 1)

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

        if self.menu_facing == 1:
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
