import pygame

from settings import (
    HP_BAR_HEIGHT,
    HP_BAR_WIDTH,
    MANA_BAR_HEIGHT,
    MANA_BAR_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WEAPON_BOX_GAP,
    WEAPON_BOX_HEIGHT,
    WEAPON_BOX_WIDTH,
)
from src.weapons import get_all_weapons, get_weapon


def draw_player_ui(screen, player):
    font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 24)

    x = 20
    hp_y = 20
    mana_y = 58
    stamina_y = 88

    draw_bar(
        screen,
        x,
        hp_y,
        HP_BAR_WIDTH,
        HP_BAR_HEIGHT,
        player.current_hp,
        player.max_hp,
        (220, 50, 50),
    )
    hp_text = font.render(f"HP: {player.current_hp} / {player.max_hp}", True, (255, 255, 255))
    screen.blit(hp_text, (x + 8, hp_y + 1))

    draw_bar(
        screen,
        x,
        mana_y,
        MANA_BAR_WIDTH,
        MANA_BAR_HEIGHT,
        player.current_mana,
        player.max_mana,
        (50, 120, 230),
    )
    mana_text = small_font.render(f"Mana: {player.current_mana} / {player.max_mana}", True, (255, 255, 255))
    screen.blit(mana_text, (x + 8, mana_y - 1))

    stamina_color = (80, 220, 110)
    if player.current_stamina < player.max_stamina * 0.35:
        stamina_color = (240, 210, 70)

    draw_bar(
        screen,
        x,
        stamina_y,
        HP_BAR_WIDTH,
        MANA_BAR_HEIGHT,
        player.current_stamina,
        player.max_stamina,
        stamina_color,
    )
    stamina_text = small_font.render(
        f"Stamina: {round(player.current_stamina)} / {player.max_stamina}",
        True,
        (255, 255, 255),
    )
    screen.blit(stamina_text, (x + 8, stamina_y - 1))

    weapon = get_weapon(player.current_weapon_id)
    coins_text = small_font.render(f"Coins: {player.coins}", True, (255, 230, 120))
    weapon_text = small_font.render(f"Weapon: {weapon['name']}", True, (230, 230, 230))

    if weapon["id"] == "shield_weapon":
        if player.guard_broken_timer > 0:
            status = "Block: Guard Broken"
        elif player.is_blocking:
            status = "Block: Active"
        else:
            status = "Block: Ready"

        if player.has_active_shield_throw:
            special_status = "Special: Shield Returning"
        elif player.special_cooldown_timer > 0:
            special_status = "Special: Cooldown"
        else:
            special_status = "Special: Shield Throw Ready"
    else:
        if player.is_parrying:
            status = "Parry: Active"
        elif player.parry_cooldown_timer > 0:
            status = f"Parry: {player.parry_cooldown_timer:.1f}s"
        else:
            status = "Parry: Ready"

        if weapon["id"] == "grapple_weapon" and player.special_cooldown_timer <= 0:
            special_status = "Special: Grapple Ready"
        elif weapon["id"] == "grapple_weapon":
            special_status = "Special: Cooldown"
        else:
            special_status = "Special: None"

    status_text = small_font.render(status, True, (230, 230, 230))
    special_text = small_font.render(special_status, True, (230, 230, 230))

    screen.blit(coins_text, (x, 118))
    screen.blit(weapon_text, (x, 144))
    screen.blit(status_text, (x, 170))
    screen.blit(special_text, (x, 196))


def draw_bar(screen, x, y, width, height, current_value, max_value, fill_color):
    percent = current_value / max_value
    percent = max(0, min(1, percent))
    fill_width = int(width * percent)

    background_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill_width, height)

    pygame.draw.rect(screen, (80, 80, 85), background_rect)
    pygame.draw.rect(screen, fill_color, fill_rect)


def draw_weapon_boxes(screen, player):
    font = pygame.font.Font(None, 24)
    weapons = list(get_all_weapons().values())
    total_width = len(weapons) * WEAPON_BOX_WIDTH + (len(weapons) - 1) * WEAPON_BOX_GAP
    start_x = (SCREEN_WIDTH - total_width) // 2
    y = SCREEN_HEIGHT - WEAPON_BOX_HEIGHT - 18

    for index, weapon in enumerate(weapons):
        x = start_x + index * (WEAPON_BOX_WIDTH + WEAPON_BOX_GAP)
        box = pygame.Rect(x, y, WEAPON_BOX_WIDTH, WEAPON_BOX_HEIGHT)

        if player.current_weapon_id == weapon["id"]:
            fill_color = (70, 120, 180)
            border_color = (255, 255, 255)
        else:
            fill_color = (40, 44, 54)
            border_color = (120, 125, 135)

        pygame.draw.rect(screen, fill_color, box)
        pygame.draw.rect(screen, border_color, box, 2)

        label = font.render(f"{index + 1} {weapon['name']}", True, (255, 255, 255))
        label_rect = label.get_rect(center=box.center)
        screen.blit(label, label_rect)
