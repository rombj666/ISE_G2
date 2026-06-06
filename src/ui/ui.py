import pygame

from settings import (
    DEBUG_MODE,
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
from src.systems.skills import get_skill
from src.systems.weapons import get_all_weapons, get_weapon


def draw_player_ui(screen, player, room_name=None):
    font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 24)

    x = 20
    hp_y = 20
    mana_y = 58

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

    weapon = get_weapon(player.current_weapon_id)
    skill = get_skill(player.current_skill_id)
    coins_text = small_font.render(f"Coins: {player.coins}", True, (255, 230, 120))
    weapon_text = small_font.render(f"Weapon: {weapon['name']}", True, (230, 230, 230))
    skill_text = small_font.render(f"Skill: {skill['name']}", True, (230, 230, 230))

    if player.skill_cooldown_timer <= 0:
        skill_status = "Skill Ready"
    else:
        skill_status = f"Skill CD: {player.skill_cooldown_timer:.1f}s"

    skill_status_text = small_font.render(skill_status, True, (230, 230, 230))

    if weapon["id"] == "shield_weapon":
        if player.is_blocking:
            status = "Block: Active"
        else:
            status = "Block: Ready"

    else:
        if player.is_parrying:
            status = "Parry: Active"
        elif player.parry_cooldown_timer > 0:
            status = f"Parry: {player.parry_cooldown_timer:.1f}s"
        else:
            status = "Parry: Ready"

    status_text = small_font.render(status, True, (230, 230, 230))

    screen.blit(coins_text, (x, 92))
    screen.blit(weapon_text, (x, 118))
    screen.blit(skill_text, (x, 144))
    screen.blit(skill_status_text, (x, 170))
    screen.blit(status_text, (x, 196))

    if player.soul_anchor_active:
        anchor_text = small_font.render(f"Anchor: {player.soul_anchor_timer:.1f}s", True, (120, 255, 180))
        screen.blit(anchor_text, (x, 222))

    if room_name is not None:
        room_text = small_font.render(f"Room: {room_name}", True, (230, 230, 230))
        screen.blit(room_text, (x, 252))

    if DEBUG_MODE:
        hp_status = "ON" if player.debug_unlimited_hp else "OFF"
        mana_status = "ON" if player.debug_unlimited_mana else "OFF"
        debug_text = small_font.render(
            f"DEBUG | F1 HP: {hp_status} | F2 Mana: {mana_status}",
            True,
            (255, 235, 120),
        )
        screen.blit(debug_text, (SCREEN_WIDTH - debug_text.get_width() - 20, 20))


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


def draw_skill_boxes(screen, player):
    font = pygame.font.Font(None, 22)
    skill_ids = ["time_freeze", "orbit_blades", "energy_beam", "soul_anchor"]
    labels = ["6 Freeze", "7 Orbit", "8 Beam", "9 Anchor"]
    box_width = 104
    box_height = 32
    gap = 8
    total_width = len(skill_ids) * box_width + (len(skill_ids) - 1) * gap
    start_x = (SCREEN_WIDTH - total_width) // 2
    y = SCREEN_HEIGHT - WEAPON_BOX_HEIGHT - box_height - 28

    for index, skill_id in enumerate(skill_ids):
        x = start_x + index * (box_width + gap)
        box = pygame.Rect(x, y, box_width, box_height)

        if player.current_skill_id == skill_id:
            fill_color = (60, 130, 150)
            border_color = (255, 255, 255)
        else:
            fill_color = (36, 42, 52)
            border_color = (115, 125, 135)

        pygame.draw.rect(screen, fill_color, box)
        pygame.draw.rect(screen, border_color, box, 2)

        label = font.render(labels[index], True, (255, 255, 255))
        label_rect = label.get_rect(center=box.center)
        screen.blit(label, label_rect)
