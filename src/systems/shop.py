import math

import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH, SHOP_INTERACT_DISTANCE


SHOP_PRODUCTS = [
    {
        "id": "max_hp",
        "name": "Max HP",
        "cost": 10,
        "description": "+50 Max HP",
    },
    {
        "id": "max_mana",
        "name": "Max Mana",
        "cost": 10,
        "description": "+50 Max Mana",
    },
]


class Shop:
    def __init__(self, x, y, width=120, height=90):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_open = False
        self.current_products = []
        self.refresh_products()

    def set_rect(self, rect):
        if rect is None:
            return

        self.rect = rect.copy()

    def refresh_products(self):
        self.current_products = [product.copy() for product in SHOP_PRODUCTS]

    def can_interact(self, player):
        return self.nearby_product_index(player) is not None or math.hypot(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery,
        ) <= SHOP_INTERACT_DISTANCE

    def nearby_product_index(self, player):
        for index, product_rect in enumerate(self.get_product_interaction_rects()):
            if player.rect.colliderect(product_rect.inflate(48, 64)):
                return index
        return None

    def get_product_positions(self):
        center_y = self.rect.bottom - 18
        return [
            (self.rect.centerx - 120, center_y),
            (self.rect.centerx + 120, center_y),
        ]

    def get_product_interaction_rects(self):
        rects = []
        for center_x, platform_y in self.get_product_positions():
            rect = pygame.Rect(0, 0, 120, 110)
            rect.midbottom = (center_x, platform_y + 8)
            rects.append(rect)
        return rects

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()

    def try_spend(self, player, cost):
        if player.coins >= cost:
            player.coins -= cost
            return True

        print("Not enough coins")
        return False

    def handle_key(self, event, player):
        if event.key == pygame.K_ESCAPE:
            self.close()
            return
        if event.key == pygame.K_1:
            self.buy_product(0, player)
        elif event.key == pygame.K_2:
            self.buy_product(1, player)

    def buy_nearby_product(self, player):
        product_index = self.nearby_product_index(player)
        if product_index is None:
            return False

        self.buy_product(product_index, player)
        return True

    def buy_product(self, product_index, player):
        if product_index >= len(self.current_products):
            return

        product = self.current_products[product_index]
        if not self.try_spend(player, product["cost"]):
            return

        if product["id"] == "max_hp":
            player.max_hp += 50
            player.current_hp = player.max_hp
            player.hp = player.current_hp
        elif product["id"] == "max_mana":
            player.max_mana += 50
            player.current_mana = player.max_mana
            player.mana = player.current_mana

        print(f"Bought {product['name']}")

    def draw_shop_area(self, screen, camera=None):
        font = pygame.font.Font(None, 24)
        price_font = pygame.font.Font(None, 22)

        for index, product in enumerate(self.current_products):
            center_x, platform_y = self.get_product_positions()[index]
            platform_rect = pygame.Rect(0, 0, 130, 18)
            platform_rect.midtop = (center_x, platform_y)
            potion_center = (center_x, platform_y - 34)

            draw_platform = camera.apply_rect(platform_rect) if camera else platform_rect
            draw_potion_center = camera.apply_pos(potion_center) if camera else potion_center
            draw_name_pos = camera.apply_pos((center_x, platform_y - 76)) if camera else (center_x, platform_y - 76)
            draw_price_pos = camera.apply_pos((center_x, platform_y + 36)) if camera else (center_x, platform_y + 36)

            pygame.draw.rect(screen, (78, 62, 78), draw_platform)
            pygame.draw.rect(screen, (220, 205, 130), draw_platform, 2)

            potion_color = (225, 70, 92) if product["id"] == "max_hp" else (70, 145, 245)
            pygame.draw.circle(screen, potion_color, draw_potion_center, 14)
            pygame.draw.circle(screen, (245, 245, 255), draw_potion_center, 14, 2)
            cap_rect = pygame.Rect(0, 0, 14, 8)
            cap_rect.midbottom = (draw_potion_center[0], draw_potion_center[1] - 11)
            pygame.draw.rect(screen, (210, 220, 235), cap_rect)

            name_text = font.render(product["name"], True, (255, 245, 210))
            screen.blit(name_text, name_text.get_rect(center=draw_name_pos))

            price_text = price_font.render("10 coins", True, (255, 225, 90))
            screen.blit(price_text, price_text.get_rect(center=draw_price_pos))

    def get_nearby_prompt(self, player):
        index = self.nearby_product_index(player)
        if index is None:
            return "Press E to buy"

        product = self.current_products[index]
        if product["id"] == "max_hp":
            return "Press E to buy Max HP (+50) - 10 coins"
        return "Press E to buy Max Mana (+50) - 10 coins"

    def draw_shop_menu(self, screen, player):
        panel = pygame.Rect(300, 170, SCREEN_WIDTH - 600, SCREEN_HEIGHT - 340)
        pygame.draw.rect(screen, (24, 24, 34), panel)
        pygame.draw.rect(screen, (230, 210, 120), panel, 3)

        font = pygame.font.Font(None, 34)
        small_font = pygame.font.Font(None, 26)

        lines = [
            "SHOP",
            f"Coins: {player.coins}",
            "1. Max HP (+50) - 10 coins",
            "2. Max Mana (+50) - 10 coins",
            "ESC. Close Shop",
        ]

        y = panel.y + 30
        for index, line in enumerate(lines):
            text = font.render(line, True, (255, 245, 180)) if index == 0 else small_font.render(line, True, (235, 235, 235))
            screen.blit(text, (panel.x + 34, y))
            y += 34
