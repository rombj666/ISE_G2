import pygame


class DevTeleport:
    """
    Developer-only teleport panel.
    - Press F3 to toggle the overlay
    - While open, press the shown key or click a button
    - ESC closes the panel
    """

    TARGETS = [
        {"id": 1, "key": "1", "key_code": pygame.K_1, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Body Pile", "pos": (100, 650)},
        {"id": 2, "key": "2", "key_code": pygame.K_2, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Destroyed Street", "pos": (1150, 650)},
        {"id": 3, "key": "3", "key_code": pygame.K_3, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Ruined Building", "pos": (2450, 650)},
        {"id": 4, "key": "4", "key_code": pygame.K_4, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Tram Wreck", "pos": (3950, 650)},
        {"id": 5, "key": "5", "key_code": pygame.K_5, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Science District", "pos": (5150, 650)},
        {"id": 6, "key": "6", "key_code": pygame.K_6, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Combat Yard", "pos": (6450, 650)},
        {"id": 7, "key": "7", "key_code": pygame.K_7, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Lab Entrance", "pos": (7650, 650)},
        {"id": 8, "key": "8", "key_code": pygame.K_8, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Shop Area", "pos": (8550, 650)},
        {"id": 9, "key": "9", "key_code": pygame.K_9, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Collapsed City", "pos": (9350, 650)},
        {"id": 10, "key": "0", "key_code": pygame.K_0, "map_id": 0, "group": "LEVEL 1 / MAP 0", "name": "Boss Entrance", "pos": (10550, 650)},

        {"id": 11, "key": "Q", "key_code": pygame.K_q, "map_id": 1, "group": "CHECKPOINTS", "name": "Lower Sanctuary", "pos": (600, 604)},
        {"id": 12, "key": "C", "key_code": pygame.K_c, "map_id": 3, "group": "CHECKPOINTS", "name": "Pale Crown Rail", "pos": (165, 650)},
        {"id": 34, "key": "L", "key_code": pygame.K_l, "map_id": 5, "group": "CHECKPOINTS", "name": "Scrap Trenches", "pos": (255, 650)},
        {"id": 45, "key": "F2", "key_code": pygame.K_F2, "map_id": 7, "group": "CHECKPOINTS", "name": "Architecture Subgate", "pos": (126, 620)},

        {"id": 13, "key": "W", "key_code": pygame.K_w, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Upper Entrance", "pos": (220, 337)},
        {"id": 14, "key": "E", "key_code": pygame.K_e, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Broken Catwalk", "pos": (760, 420)},
        {"id": 15, "key": "R", "key_code": pygame.K_r, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Glass Labs", "pos": (1490, 643)},
        {"id": 16, "key": "T", "key_code": pygame.K_t, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Reactor Shaft", "pos": (2400, 474)},
        {"id": 17, "key": "Y", "key_code": pygame.K_y, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Security Lockdown", "pos": (3420, 310)},
        {"id": 18, "key": "\\", "key_code": pygame.K_BACKSLASH, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Flooded Sector", "pos": (4550, 338)},
        {"id": 19, "key": "I", "key_code": pygame.K_i, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Memory Archive", "pos": (6150, 339)},
        {"id": 20, "key": "O", "key_code": pygame.K_o, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Transit Rails", "pos": (7400, 394)},
        {"id": 21, "key": "P", "key_code": pygame.K_p, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Quiet Descent", "pos": (8500, 482)},
        {"id": 22, "key": "A", "key_code": pygame.K_a, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Experiment Chamber", "pos": (9750, 336)},
        {"id": 23, "key": "S", "key_code": pygame.K_s, "map_id": 2, "group": "LEVEL 2 / MAP 2", "name": "Checkpoint Gate", "pos": (10930, 314)},

        {"id": 24, "key": "Z", "key_code": pygame.K_z, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Border Station", "pos": (180, 1030)},
        {"id": 25, "key": "X", "key_code": pygame.K_x, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Rain Alley", "pos": (1400, 1030)},
        {"id": 26, "key": "V", "key_code": pygame.K_v, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Surveillance Roofs", "pos": (2850, 1030)},
        {"id": 27, "key": "B", "key_code": pygame.K_b, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Data Center", "pos": (4350, 1030)},
        {"id": 28, "key": "N", "key_code": pygame.K_n, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Archives", "pos": (5750, 1030)},
        {"id": 29, "key": "M", "key_code": pygame.K_m, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Transit Rail", "pos": (7000, 1030)},
        {"id": 30, "key": "F", "key_code": pygame.K_f, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Residential", "pos": (8700, 1030)},
        {"id": 31, "key": "G", "key_code": pygame.K_g, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Core Tower", "pos": (9900, 1030)},
        {"id": 32, "key": "H", "key_code": pygame.K_h, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Observer Chamber", "pos": (11680, 1030)},
        {"id": 33, "key": "J", "key_code": pygame.K_j, "map_id": 4, "group": "LEVEL 3 / MAP 4", "name": "Apex Rooftops", "pos": (13000, 1030)},

        {"id": 35, "key": "K", "key_code": pygame.K_k, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "Scrap Escape", "pos": (220, 597)},
        {"id": 36, "key": "F4", "key_code": pygame.K_F4, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "War Streets", "pos": (1500, 597)},
        {"id": 37, "key": "F5", "key_code": pygame.K_F5, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "Housing Blocks", "pos": (2900, 597)},
        {"id": 38, "key": "F6", "key_code": pygame.K_F6, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "Wall Sector", "pos": (4300, 597)},
        {"id": 39, "key": "F7", "key_code": pygame.K_F7, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "Artillery Bridge", "pos": (5800, 597)},
        {"id": 40, "key": "F8", "key_code": pygame.K_F8, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "Mech Grounds", "pos": (7100, 597)},
        {"id": 41, "key": "F9", "key_code": pygame.K_F9, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "Bunker", "pos": (8400, 597)},
        {"id": 42, "key": "F10", "key_code": pygame.K_F10, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "Arena", "pos": (9400, 597)},
        {"id": 43, "key": "F11", "key_code": pygame.K_F11, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "Command", "pos": (10700, 597)},
        {"id": 44, "key": "F12", "key_code": pygame.K_F12, "map_id": 6, "group": "LEVEL 4 / MAP 6", "name": "Exodus Station", "pos": (11500, 597)},

        {"id": 46, "key": "F1", "key_code": pygame.K_F1, "map_id": 8, "group": "LEVEL 5 / MAP 8", "name": "Arrival", "pos": (50, 796)},
        {"id": 47, "key": "D", "key_code": pygame.K_d, "map_id": 8, "group": "LEVEL 5 / MAP 8", "name": "Hanging Gardens", "pos": (1709, 169)},
        {"id": 48, "key": "-", "key_code": pygame.K_MINUS, "map_id": 8, "group": "LEVEL 5 / MAP 8", "name": "Fractured City", "pos": (2956, 597)},
        {"id": 49, "key": "=", "key_code": pygame.K_EQUALS, "map_id": 8, "group": "LEVEL 5 / MAP 8", "name": "Transit Ring", "pos": (5049, 316)},
        {"id": 50, "key": "[", "key_code": pygame.K_LEFTBRACKET, "map_id": 8, "group": "LEVEL 5 / MAP 8", "name": "Core Descent", "pos": (6479, 713)},
        {"id": 51, "key": "]", "key_code": pygame.K_RIGHTBRACKET, "map_id": 8, "group": "LEVEL 5 / MAP 8", "name": "Lunar Core", "pos": (9851, 649)},
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
        if not self.visible:
            return None

        for target in self.TARGETS:
            if key == target["key_code"]:
                return target["id"]
        return None

    def handle_click(self, mouse_pos):
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
        overlay.fill((0, 0, 0, 178))
        screen.blit(overlay, (0, 0))

        panel_w = min(screen_w - 24, 1248)
        panel_h = min(screen_h - 24, 684)
        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (screen_w // 2, screen_h // 2)

        pygame.draw.rect(screen, (8, 13, 23), panel)
        pygame.draw.rect(screen, (112, 216, 255), panel, 3)
        pygame.draw.rect(screen, (28, 42, 63), panel.inflate(-14, -14), 1)

        title_font = pygame.font.SysFont("consolas", 28, bold=True)
        sub_font = pygame.font.SysFont("consolas", 15)
        header_font = pygame.font.SysFont("consolas", 15, bold=True)
        group_font = pygame.font.SysFont("consolas", 13, bold=True)
        btn_font = pygame.font.SysFont("consolas", 12, bold=True)

        title = title_font.render("DEV TELEPORT", True, (210, 239, 255))
        screen.blit(title, title.get_rect(midtop=(panel.centerx, panel.y + 14)))

        sub = sub_font.render("F3 close/open | ESC close | click or press shown key", True, (160, 178, 207))
        screen.blit(sub, sub.get_rect(midtop=(panel.centerx, panel.y + 48)))

        self.button_rects.clear()

        col_gap = 10
        col_count = 5
        usable_w = panel_w - 48 - col_gap * (col_count - 1)
        col_w = usable_w // col_count
        start_x = panel.x + 24
        start_y = panel.y + 86

        level1 = [target for target in self.TARGETS if target["map_id"] == 0]
        checkpoints = [target for target in self.TARGETS if target["map_id"] in (1, 3, 5, 7)]
        level2 = [target for target in self.TARGETS if target["map_id"] == 2]
        level3 = [target for target in self.TARGETS if target["map_id"] == 4]
        level4 = [target for target in self.TARGETS if target["map_id"] == 6]
        level5 = [target for target in self.TARGETS if target["map_id"] == 8]

        columns = [
            ("LEVEL 1", [("MAP 0", level1), ("CHECKPOINTS", checkpoints)]),
            ("LEVEL 2", [("MAP 2", level2)]),
            ("LEVEL 3", [("MAP 4", level3)]),
            ("LEVEL 4", [("MAP 6", level4)]),
            ("LEVEL 5", [("MAP 8", level5)]),
        ]

        for index, (title_text, sections) in enumerate(columns):
            self._draw_grouped_column(
                screen,
                sections,
                start_x + index * (col_w + col_gap),
                start_y,
                col_w,
                title_text,
                header_font,
                group_font,
                btn_font,
            )

    def _draw_grouped_column(self, screen, sections, x, y, width, title, header_font, group_font, btn_font):
        title_rect = pygame.Rect(x, y, width, 24)
        pygame.draw.rect(screen, (18, 31, 48), title_rect)
        pygame.draw.rect(screen, (80, 184, 225), title_rect, 1)
        title_text = header_font.render(title, True, (137, 229, 255))
        screen.blit(title_text, title_text.get_rect(center=title_rect.center))
        y += 32

        btn_h = 24
        gap = 5

        for section_title, targets in sections:
            if not targets:
                continue

            label = group_font.render(section_title, True, (245, 215, 118))
            screen.blit(label, (x + 4, y))
            y += 18

            for target in targets:
                btn = pygame.Rect(x, y, width, btn_h)
                is_hover = self.hover_index == target["id"]
                bg_color = (58, 90, 128) if is_hover else (25, 40, 61)
                border_color = (211, 242, 255) if is_hover else (76, 130, 174)

                pygame.draw.rect(screen, bg_color, btn)
                pygame.draw.rect(screen, border_color, btn, 1)

                label = f"[{target['key']}] {target['name']}"
                text = btn_font.render(label, True, (240, 247, 255))
                text_rect = text.get_rect(midleft=(btn.x + 8, btn.centery))
                clip = screen.get_clip()
                screen.set_clip(btn.inflate(-8, 0))
                screen.blit(text, text_rect)
                screen.set_clip(clip)

                self.button_rects.append((target["id"], btn))
                y += btn_h + gap

            y += 8
