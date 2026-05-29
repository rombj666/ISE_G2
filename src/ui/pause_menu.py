import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class PauseMenu:
    def __init__(self):
        self.options = ["Resume", "Restart", "Main Menu", "Quit"]
        self.selected_index = 0
        self.should_resume = False
        self.should_restart = False
        self.should_main_menu = False
        self.should_quit = False
        self.panel_rect = pygame.Rect(0, 0, 430, 380)
        self.panel_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.option_rects = []
        self._layout_options()

    def reset_flags(self):
        self.should_resume = False
        self.should_restart = False
        self.should_main_menu = False
        self.should_quit = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.should_resume = True
            elif event.key == pygame.K_RETURN:
                self._confirm_selected()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)

        if event.type == pygame.MOUSEMOTION:
            for index, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self.selected_index = index
                    break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self.selected_index = index
                    self._confirm_selected()
                    break

    def update(self, dt):
        pass

    def draw(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((2, 5, 12, 168))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (12, 18, 31), self.panel_rect, border_radius=8)
        pygame.draw.rect(screen, (145, 215, 255), self.panel_rect, 2, border_radius=8)
        pygame.draw.rect(screen, (38, 72, 104), self.panel_rect.inflate(-18, -18), 1, border_radius=6)

        title_font = pygame.font.Font(None, 64)
        option_font = pygame.font.Font(None, 36)
        title = title_font.render("PAUSED", True, (232, 246, 255))
        screen.blit(title, title.get_rect(center=(self.panel_rect.centerx, self.panel_rect.y + 72)))

        for index, rect in enumerate(self.option_rects):
            selected = index == self.selected_index
            fill = (56, 96, 132) if selected else (20, 32, 52)
            border = (190, 235, 255) if selected else (75, 125, 165)
            text_color = (255, 255, 255) if selected else (214, 232, 246)
            pygame.draw.rect(screen, fill, rect, border_radius=6)
            pygame.draw.rect(screen, border, rect, 2, border_radius=6)
            label = option_font.render(self.options[index], True, text_color)
            screen.blit(label, label.get_rect(center=rect.center))

    def _layout_options(self):
        self.option_rects.clear()
        start_y = self.panel_rect.y + 126
        for index in range(len(self.options)):
            rect = pygame.Rect(0, 0, 270, 46)
            rect.center = (self.panel_rect.centerx, start_y + index * 58)
            self.option_rects.append(rect)

    def _confirm_selected(self):
        option = self.options[self.selected_index]
        if option == "Resume":
            self.should_resume = True
        elif option == "Restart":
            self.should_restart = True
        elif option == "Main Menu":
            self.should_main_menu = True
        elif option == "Quit":
            self.should_quit = True
