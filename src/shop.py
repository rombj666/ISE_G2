import math

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
    SHOP_SKILL_COST,
    SHOP_WEAPON_COST,
)


class Shop:
    def __init__(self, x, y, width=70, height=80):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_open = False
        self.mode = "main"

    def can_interact(self, player):
        distance = math.hypot(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery,
        )
        return distance <= SHOP_INTERACT_DISTANCE

    def open(self):
        self.is_open = True
        self.mode = "main"

    def close(self):
        self.is_open = False
        self.mode = "main"

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
            if self.mode == "main":
                self.close()
            else:
                self.mode = "main"
            return

        if self.mode == "main":
            self.handle_main_key(event, player)
        elif self.mode == "weapon":
            self.handle_weapon_key(event, player)
        elif self.mode == "skill":
            self.handle_skill_key(event, player)

    def handle_main_key(self, event, player):
        if event.key == pygame.K_1:
            if player.current_hp >= player.max_hp:
                print("HP already full")
                return

            if self.try_spend(player, SHOP_HEAL_COST):
                player.current_hp = player.max_hp
                player.hp = player.current_hp
                print("HP restored")

        elif event.key == pygame.K_2:
            if player.current_mana >= player.max_mana:
                print("Mana already full")
                return

            if self.try_spend(player, SHOP_MANA_COST):
                player.current_mana = player.max_mana
                player.mana = player.current_mana
                print("Mana restored")

        elif event.key == pygame.K_3:
            if self.try_spend(player, SHOP_MAX_HP_COST):
                player.max_hp += SHOP_MAX_HP_INCREASE
                player.current_hp = player.max_hp
                player.hp = player.current_hp
                print("Max HP upgraded")

        elif event.key == pygame.K_4:
            if self.try_spend(player, SHOP_MAX_MANA_COST):
                player.max_mana += SHOP_MAX_MANA_INCREASE
                player.current_mana = player.max_mana
                player.mana = player.current_mana
                print("Max mana upgraded")

        elif event.key == pygame.K_5:
            if player.crit_chance >= SHOP_CRIT_CHANCE_MAX:
                print("Crit chance already maxed")
                return

            if self.try_spend(player, SHOP_CRIT_CHANCE_COST):
                player.crit_chance += SHOP_CRIT_CHANCE_INCREASE
                player.crit_chance = min(player.crit_chance, SHOP_CRIT_CHANCE_MAX)
                print("Crit chance upgraded")

        elif event.key == pygame.K_6:
            if player.crit_damage >= SHOP_CRIT_DAMAGE_MAX:
                print("Crit damage already maxed")
                return

            if self.try_spend(player, SHOP_CRIT_DAMAGE_COST):
                player.crit_damage += SHOP_CRIT_DAMAGE_INCREASE
                player.crit_damage = min(player.crit_damage, SHOP_CRIT_DAMAGE_MAX)
                print("Crit damage upgraded")

        elif event.key == pygame.K_7:
            if player.bonus_attack_percent >= SHOP_ATTACK_POTION_MAX:
                print("Attack potion already maxed")
                return

            if self.try_spend(player, SHOP_ATTACK_POTION_COST):
                player.bonus_attack_percent += SHOP_ATTACK_POTION_INCREASE
                player.bonus_attack_percent = min(player.bonus_attack_percent, SHOP_ATTACK_POTION_MAX)
                print("Attack potion purchased")

        elif event.key == pygame.K_8:
            self.mode = "weapon"

        elif event.key == pygame.K_9:
            self.mode = "skill"

    def handle_weapon_key(self, event, player):
        weapon_ids = {
            pygame.K_1: "light_weapon",
            pygame.K_2: "heavy_weapon",
            pygame.K_3: "shooter_weapon",
            pygame.K_4: "shield_weapon",
            pygame.K_5: "grapple_weapon",
        }

        if event.key in weapon_ids and self.try_spend(player, SHOP_WEAPON_COST):
            player.switch_weapon(weapon_ids[event.key])
            self.mode = "main"

    def handle_skill_key(self, event, player):
        skill_ids = {
            pygame.K_1: "time_freeze",
            pygame.K_2: "orbit_blades",
            pygame.K_3: "energy_beam",
            pygame.K_4: "execute_strike",
            pygame.K_5: "soul_anchor",
        }

        if event.key in skill_ids and self.try_spend(player, SHOP_SKILL_COST):
            player.switch_skill(skill_ids[event.key])
            self.mode = "main"

    def draw_shop_area(self, screen):
        pygame.draw.rect(screen, (150, 90, 220), self.rect)
        pygame.draw.rect(screen, (250, 230, 130), self.rect, 3)

        font = pygame.font.Font(None, 26)
        text = font.render("SHOP", True, (255, 245, 180))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def draw_shop_menu(self, screen, player):
        panel = pygame.Rect(260, 90, SCREEN_WIDTH - 520, SCREEN_HEIGHT - 180)
        pygame.draw.rect(screen, (24, 24, 34), panel)
        pygame.draw.rect(screen, (230, 210, 120), panel, 3)

        font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 25)

        if self.mode == "main":
            lines = [
                "SHOP / SHRINE",
                f"Coins: {player.coins}",
                "",
                f"1. Heal HP - {SHOP_HEAL_COST} coins",
                f"2. Restore Mana - {SHOP_MANA_COST} coins",
                f"3. Upgrade Max HP +20 - {SHOP_MAX_HP_COST} coins",
                f"4. Upgrade Max Mana +20 - {SHOP_MAX_MANA_COST} coins",
                f"5. Upgrade Crit Chance +5% - {SHOP_CRIT_CHANCE_COST} coins",
                f"6. Upgrade Crit Damage +25% - {SHOP_CRIT_DAMAGE_COST} coins",
                f"7. Buy Attack Potion +10% damage - {SHOP_ATTACK_POTION_COST} coins",
                f"8. Change Weapon - {SHOP_WEAPON_COST} coins",
                f"9. Change Skill - {SHOP_SKILL_COST} coins",
                "",
                "ESC. Close Shop",
            ]
        elif self.mode == "weapon":
            lines = [
                f"CHOOSE WEAPON - {SHOP_WEAPON_COST} coins",
                f"Coins: {player.coins}",
                "",
                "1. Light",
                "2. Heavy",
                "3. Shooter",
                "4. Shield",
                "5. Grapple",
                "",
                "ESC. Back",
            ]
        else:
            lines = [
                f"CHOOSE SKILL - {SHOP_SKILL_COST} coins",
                f"Coins: {player.coins}",
                "",
                "1. Time Freeze",
                "2. Orbit Blades",
                "3. Energy Beam",
                "4. Execute Strike",
                "5. Soul Anchor",
                "",
                "ESC. Back",
            ]

        y = panel.y + 28
        for index, line in enumerate(lines):
            if index == 0:
                text = font.render(line, True, (255, 245, 180))
            else:
                text = small_font.render(line, True, (235, 235, 235))

            screen.blit(text, (panel.x + 34, y))
            y += 30
