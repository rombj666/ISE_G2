import math
import random

import pygame

from settings import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOP_ATTACK_POTION_COST,
    SHOP_ATTACK_POTION_INCREASE,
    SHOP_ATTACK_POTION_MAX,
    SHOP_CRIT_CHANCE_COST,
    SHOP_CRIT_CHANCE_INCREASE,
    SHOP_CRIT_CHANCE_MAX,
    SHOP_CRIT_DAMAGE_COST,
    SHOP_CRIT_DAMAGE_INCREASE,
    SHOP_CRIT_DAMAGE_MAX,
    SHOP_HEAL_COST,
    SHOP_INTERACT_DISTANCE,
    SHOP_MANA_COST,
    SHOP_MAX_HP_COST,
    SHOP_MAX_HP_INCREASE,
    SHOP_MAX_MANA_COST,
    SHOP_MAX_MANA_INCREASE,
    SHOP_PRODUCT_SLOT_COUNT,
    SHOP_RANDOM_SEED_ENABLED,
    SHOP_SKILL_COST,
    SHOP_WEAPON_COST,
)


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
        product_pool = self.build_product_pool()
        if SHOP_RANDOM_SEED_ENABLED:
            random.seed(1)
        self.current_products = random.sample(product_pool, SHOP_PRODUCT_SLOT_COUNT)

    def build_product_pool(self):
        return [
            self.make_weapon("light_weapon", "Light Weapon"),
            self.make_weapon("heavy_weapon", "Heavy Weapon"),
            self.make_weapon("shooter_weapon", "Shooter Weapon"),
            self.make_weapon("shield_weapon", "Shield Weapon"),
            self.make_weapon("grapple_weapon", "Grapple Weapon"),
            self.make_skill("time_freeze", "Time Freeze"),
            self.make_skill("orbit_blades", "Orbit Blades"),
            self.make_skill("energy_beam", "Energy Beam"),
            self.make_skill("execute_strike", "Execute Strike"),
            self.make_skill("soul_anchor", "Soul Anchor"),
            {
                "id": "heal_hp",
                "name": "Heal HP",
                "product_type": "recovery",
                "cost": SHOP_HEAL_COST,
                "recovery_type": "hp",
            },
            {
                "id": "restore_mana",
                "name": "Restore Mana",
                "product_type": "recovery",
                "cost": SHOP_MANA_COST,
                "recovery_type": "mana",
            },
            self.make_upgrade("max_hp", "Max HP +20", SHOP_MAX_HP_COST),
            self.make_upgrade("max_mana", "Max Mana +20", SHOP_MAX_MANA_COST),
            self.make_upgrade("crit_chance", "Crit Chance +5%", SHOP_CRIT_CHANCE_COST),
            self.make_upgrade("crit_damage", "Crit Damage +25%", SHOP_CRIT_DAMAGE_COST),
            self.make_upgrade("attack_potion", "Attack Potion +10%", SHOP_ATTACK_POTION_COST),
        ]

    def make_weapon(self, weapon_id, name):
        return {
            "id": f"buy_{weapon_id}",
            "name": name,
            "product_type": "weapon",
            "cost": SHOP_WEAPON_COST,
            "weapon_id": weapon_id,
        }

    def make_skill(self, skill_id, name):
        return {
            "id": f"buy_{skill_id}",
            "name": name,
            "product_type": "skill",
            "cost": SHOP_SKILL_COST,
            "skill_id": skill_id,
        }

    def make_upgrade(self, upgrade_type, name, cost):
        return {
            "id": f"upgrade_{upgrade_type}",
            "name": name,
            "product_type": "upgrade",
            "cost": cost,
            "upgrade_type": upgrade_type,
        }

    def can_interact(self, player):
        distance = math.hypot(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery,
        )
        return distance <= SHOP_INTERACT_DISTANCE

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

        key_to_index = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_5: 4,
        }

        if event.key in key_to_index:
            self.buy_product(key_to_index[event.key], player)

    def buy_product(self, product_index, player):
        if product_index >= len(self.current_products):
            return

        product = self.current_products[product_index]
        if not self.try_spend(player, product["cost"]):
            return

        product_type = product["product_type"]

        if product_type == "weapon":
            player.switch_weapon(product["weapon_id"])
        elif product_type == "skill":
            player.switch_skill(product["skill_id"])
        elif product_type == "recovery":
            self.apply_recovery(player, product["recovery_type"])
        elif product_type == "upgrade":
            self.apply_upgrade(player, product["upgrade_type"])

        print(f"Bought {product['name']}")

    def apply_recovery(self, player, recovery_type):
        if recovery_type == "hp":
            player.current_hp = player.max_hp
            player.hp = player.current_hp
        elif recovery_type == "mana":
            player.current_mana = player.max_mana
            player.mana = player.current_mana

    def apply_upgrade(self, player, upgrade_type):
        if upgrade_type == "max_hp":
            player.max_hp += SHOP_MAX_HP_INCREASE
            player.current_hp = player.max_hp
            player.hp = player.current_hp
        elif upgrade_type == "max_mana":
            player.max_mana += SHOP_MAX_MANA_INCREASE
            player.current_mana = player.max_mana
            player.mana = player.current_mana
        elif upgrade_type == "crit_chance":
            player.crit_chance += SHOP_CRIT_CHANCE_INCREASE
            player.crit_chance = min(player.crit_chance, SHOP_CRIT_CHANCE_MAX)
        elif upgrade_type == "crit_damage":
            player.crit_damage += SHOP_CRIT_DAMAGE_INCREASE
            player.crit_damage = min(player.crit_damage, SHOP_CRIT_DAMAGE_MAX)
        elif upgrade_type == "attack_potion":
            player.bonus_attack_percent += SHOP_ATTACK_POTION_INCREASE
            player.bonus_attack_percent = min(player.bonus_attack_percent, SHOP_ATTACK_POTION_MAX)

    def draw_shop_area(self, screen, camera=None):
        draw_rect = self.rect
        if camera:
            draw_rect = camera.apply_rect(self.rect)

        cabinet = draw_rect
        counter = pygame.Rect(draw_rect.x - 12, draw_rect.y + draw_rect.height - 24, draw_rect.width + 24, 24)

        pygame.draw.rect(screen, (105, 70, 50), cabinet)
        pygame.draw.rect(screen, (170, 120, 70), counter)
        pygame.draw.rect(screen, (245, 220, 140), cabinet, 3)

        font = pygame.font.Font(None, 22)
        title = font.render("SHOP", True, (255, 245, 180))
        screen.blit(title, title.get_rect(center=cabinet.center))

        slot_width = 92
        slot_height = 28
        gap = 8
        total_width = len(self.current_products) * slot_width + (len(self.current_products) - 1) * gap
        start_x = self.rect.centerx - total_width // 2
        slot_y = self.rect.y - slot_height - 12

        for index, product in enumerate(self.current_products):
            slot_rect = pygame.Rect(start_x + index * (slot_width + gap), slot_y, slot_width, slot_height)
            if camera:
                slot_rect = camera.apply_rect(slot_rect)

            pygame.draw.rect(screen, (38, 44, 54), slot_rect)
            pygame.draw.rect(screen, (220, 210, 120), slot_rect, 2)
            label = self.get_short_product_name(product)
            text = font.render(label, True, (245, 245, 245))
            screen.blit(text, text.get_rect(center=slot_rect.center))

    def get_short_product_name(self, product):
        short_names = {
            "Light Weapon": "Light",
            "Heavy Weapon": "Heavy",
            "Shooter Weapon": "Shoot",
            "Shield Weapon": "Shield",
            "Grapple Weapon": "Grapple",
            "Time Freeze": "Freeze",
            "Orbit Blades": "Orbit",
            "Energy Beam": "Beam",
            "Execute Strike": "Execute",
            "Soul Anchor": "Anchor",
            "Restore Mana": "Mana",
            "Attack Potion +10%": "Potion",
        }
        return short_names.get(product["name"], product["name"])

    def draw_shop_menu(self, screen, player):
        panel = pygame.Rect(300, 130, SCREEN_WIDTH - 600, SCREEN_HEIGHT - 260)
        pygame.draw.rect(screen, (24, 24, 34), panel)
        pygame.draw.rect(screen, (230, 210, 120), panel, 3)

        font = pygame.font.Font(None, 34)
        small_font = pygame.font.Font(None, 26)

        lines = [
            "SHOP / SHRINE",
            f"Coins: {player.coins}",
            "",
        ]

        for index, product in enumerate(self.current_products):
            lines.append(f"{index + 1}. {product['name']} - {product['cost']} coins")

        lines.extend(["", "ESC. Close Shop"])

        y = panel.y + 30
        for index, line in enumerate(lines):
            if index == 0:
                text = font.render(line, True, (255, 245, 180))
            else:
                text = small_font.render(line, True, (235, 235, 235))

            screen.blit(text, (panel.x + 34, y))
            y += 32
