import pygame


class DevTeleport:
    """
    Developer-only teleport panel.
    - Press F3 to toggle the overlay
    - While open: press 1-9 / 0 for MAP 0 sections
    - Press Q for MAP 1 checkpoint, W for MAP 2
    - Or click any button in the panel
    - ESC closes the panel
    """

    TARGETS = [
        {"id": 1, "key": "1", "key_code": pygame.K_1, "map_id": 0, "name": "Body Pile", "pos": (100, 650)},
        {"id": 2, "key": "2", "key_code": pygame.K_2, "map_id": 0, "name": "Destroyed Street", "pos": (1150, 650)},
        {"id": 3, "key": "3", "key_code": pygame.K_3, "map_id": 0, "name": "Ruined Building", "pos": (2450, 650)},
        {"id": 4, "key": "4", "key_code": pygame.K_4, "map_id": 0, "name": "Tram Wreck", "pos": (3950, 650)},
        {"id": 5, "key": "5", "key_code": pygame.K_5, "map_id": 0, "name": "Science District", "pos": (5150, 650)},
        {"id": 6, "key": "6", "key_code": pygame.K_6, "map_id": 0, "name": "Combat Courtyard", "pos": (6450, 650)},
        {"id": 7, "key": "7", "key_code": pygame.K_7, "map_id": 0, "name": "Lab Entrance", "pos": (7650, 650)},
        {"id": 8, "key": "8", "key_code": pygame.K_8, "map_id": 0, "name": "SHOP Area", "pos": (8550, 650)},
        {"id": 9, "key": "9", "key_code": pygame.K_9, "map_id": 0, "name": "Collapsed City", "pos": (9350, 650)},
        {"id": 10, "key": "0", "key_code": pygame.K_0, "map_id": 0, "name": "Boss Entrance", "pos": (10550, 650)},
        {"id": 11, "key": "Q", "key_code": pygame.K_q, "map_id": 1, "name": "Checkpoint Map", "pos": (600, 604)},
        {"id": 12, "key": "W", "key_code": pygame.K_w, "map_id": 2, "name": "Level 2 / Map 2", "pos": (100, 650)},
    ]

    def __init__(self):
        self.visible = False
        self.hover_index = None
        self.button_rects = []

    def toggle(self):
        self.visible = not self.visible
        self.hover_index = None

    def close(self):
        self.visible = False
        self.hover_index = None

    def handle_key(self, key):
        """Returns target id if a teleport key was pressed, else None."""
        if not self.visible:
            return None

        for target in self.TARGETS:
            if key == target["key_code"]:
                return target["id"]
        return None

    def handle_click(self, mouse_pos):
        """Returns target id if a button was clicked, else None."""
        if not self.visible:
            return None

        for target_id, rect in self.button_rects:
            if rect.collidepoint(mouse_pos):
                return target_id
        return None

    def update_hover(self, mouse_pos):
        if not self.visible:
            self.hover_index = None
            return

        self.hover_index = None
        for target_id, rect in self.button_rects:
            if rect.collidepoint(mouse_pos):
                self.hover_index = target_id
                break

    def get_target(self, target_id):
        for target in self.TARGETS:
            if target["id"] == target_id:
                return target.copy()
        return None

    # Backward-compatible helper for older code paths.
    def get_position(self, target_id):
        target = self.get_target(target_id)
        if target is None:
            return None
        return target["pos"]

    def draw(self, screen):
        if not self.visible:
            return

        screen_w, screen_h = screen.get_size()

        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        panel_w, panel_h = 520, min(screen_h - 40, 600)
        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (screen_w // 2, screen_h // 2)
        pygame.draw.rect(screen, (22, 28, 42), panel)
        pygame.draw.rect(screen, (140, 200, 250), panel, 3)

        title_font = pygame.font.Font(None, 36)
        title = title_font.render("DEV TELEPORT", True, (180, 220, 255))
        screen.blit(title, title.get_rect(midtop=(panel.centerx, panel.y + 16)))

        sub_font = pygame.font.Font(None, 20)
        sub = sub_font.render("1-9/0 = MAP 0, Q = MAP 1, W = MAP 2, ESC = close", True, (160, 170, 200))
        screen.blit(sub, sub.get_rect(midtop=(panel.centerx, panel.y + 50)))

        self.button_rects.clear()
        btn_font = pygame.font.Font(None, 23)
        btn_w, btn_h = 460, 32
        gap = 5
        y = panel.y + 84

        for target in self.TARGETS:
            btn = pygame.Rect(0, 0, btn_w, btn_h)
            btn.midtop = (panel.centerx, y)

            is_hover = self.hover_index == target["id"]
            bg_color = (60, 100, 140) if is_hover else (40, 55, 80)
            border_color = (180, 230, 255) if is_hover else (110, 160, 210)

            pygame.draw.rect(screen, bg_color, btn)
            pygame.draw.rect(screen, border_color, btn, 1)

            label = btn_font.render(
                f"[{target['key']}]  MAP {target['map_id']}  -  {target['name']}",
                True,
                (235, 245, 255),
            )
            screen.blit(label, label.get_rect(midleft=(btn.x + 18, btn.centery)))

            self.button_rects.append((target["id"], btn))
            y += btn_h + gap
