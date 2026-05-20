import pygame


class DevTeleport:
    """
    Developer-only teleport panel.
    - Press F3 to toggle the overlay
    - While open: press 1-9 or 0 (for section 10) to jump
    - OR click a button in the panel
    - ESC also closes the panel
    """

    SECTIONS = [
        (1,  "Body Pile",        (100,   650)),
        (2,  "Destroyed Street", (1150,  650)),
        (3,  "Ruined Building",  (2450,  650)),
        (4,  "Tram Wreck",       (3950,  650)),
        (5,  "Science District", (5150,  650)),
        (6,  "Combat Courtyard", (6450,  650)),
        (7,  "Lab Entrance",     (7650,  650)),
        (8,  "SHOP Area",        (8550,  650)),
        (9,  "Collapsed City",   (9350,  650)),
        (10, "Boss Entrance",    (10550, 650)),
    ]

    def __init__(self):
        self.visible = False
        self.hover_index = None
        self.button_rects = []   # list of (section_idx, pygame.Rect)

    def toggle(self):
        self.visible = not self.visible
        self.hover_index = None

    def close(self):
        self.visible = False
        self.hover_index = None

    def handle_key(self, key):
        """Returns section index (1..10) if a number key was pressed, else None."""
        if not self.visible:
            return None
        if pygame.K_1 <= key <= pygame.K_9:
            return key - pygame.K_0   # K_1 -> 1, K_9 -> 9
        if key == pygame.K_0:
            return 10
        return None

    def handle_click(self, mouse_pos):
        """Returns section index if a button was clicked, else None."""
        if not self.visible:
            return None
        for idx, rect in self.button_rects:
            if rect.collidepoint(mouse_pos):
                return idx
        return None

    def update_hover(self, mouse_pos):
        if not self.visible:
            self.hover_index = None
            return
        self.hover_index = None
        for idx, rect in self.button_rects:
            if rect.collidepoint(mouse_pos):
                self.hover_index = idx
                break

    def get_position(self, section_index):
        for idx, _, pos in self.SECTIONS:
            if idx == section_index:
                return pos
        return None

    def draw(self, screen):
        if not self.visible:
            return

        screen_w, screen_h = screen.get_size()

        # Dim the world behind the panel
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Panel background
        panel_w, panel_h = 480, 500
        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (screen_w // 2, screen_h // 2)
        pygame.draw.rect(screen, (22, 28, 42), panel)
        pygame.draw.rect(screen, (140, 200, 250), panel, 3)

        # Title
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("DEV TELEPORT", True, (180, 220, 255))
        screen.blit(title, title.get_rect(midtop=(panel.centerx, panel.y + 16)))

        # Subtitle
        sub_font = pygame.font.Font(None, 20)
        sub = sub_font.render(
            "Press 1-9 / 0 (for #10), click, or ESC to close", True, (160, 170, 200)
        )
        screen.blit(sub, sub.get_rect(midtop=(panel.centerx, panel.y + 50)))

        # Section buttons
        self.button_rects.clear()
        btn_font = pygame.font.Font(None, 24)
        btn_w, btn_h = 430, 34
        gap = 6
        y = panel.y + 84

        for idx, name, _ in self.SECTIONS:
            btn = pygame.Rect(0, 0, btn_w, btn_h)
            btn.midtop = (panel.centerx, y)

            is_hover = (self.hover_index == idx)
            bg_color = (60, 100, 140) if is_hover else (40, 55, 80)
            border_color = (180, 230, 255) if is_hover else (110, 160, 210)

            pygame.draw.rect(screen, bg_color, btn)
            pygame.draw.rect(screen, border_color, btn, 1)

            key_label = idx if idx < 10 else 0
            label = btn_font.render(
                f"[{key_label}]   Section {idx}:   {name}", True, (235, 245, 255)
            )
            screen.blit(label, label.get_rect(midleft=(btn.x + 18, btn.centery)))

            self.button_rects.append((idx, btn))
            y += btn_h + gap
