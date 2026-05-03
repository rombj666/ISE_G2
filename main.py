import math

import pygame

from settings import (
    COIN_PICKUP_RANGE,
    COIN_VALUE,
    ENEMY_DAMAGE,
    FPS,
    FULCRUM_INTERACT_DISTANCE,
    FULCRUM_RADIUS,
    NORMAL_PARRY_STUN_TIME,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
    WEAPON_SPECIAL_COOLDOWN,
)
from src.coin import Coin
from src.combat import calculate_damage
from src.enemy import Enemy
from src.player import Player
from src.projectile import Projectile, ReturningShield
from src.ui import draw_player_ui, draw_weapon_boxes
from src.weapons import get_weapon


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    player = Player(100, 500)
    enemy = Enemy(700, 590)
    coins = []
    projectiles = []
    returning_shields = []

    platforms = [
        pygame.Rect(0, 650, 1280, 70),
        pygame.Rect(300, 520, 200, 30),
        pygame.Rect(650, 430, 220, 30),
    ]

    fulcrums = [
        {
            "rect": pygame.Rect(420, 560, FULCRUM_RADIUS * 2, FULCRUM_RADIUS * 2),
            "anchor": (434, 574),
            "target": (780, 398),
            "used": False,
        }
    ]

    u_was_pressed = False
    grapple_special_hitbox = None
    grapple_special_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        e_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                e_pressed = True

        keys = pygame.key.get_pressed()

        if grapple_special_timer > 0:
            grapple_special_timer -= dt
        else:
            grapple_special_hitbox = None

        enemy.update(dt, player)

        if not player.is_dead:
            player.handle_input(keys)
            player.update(dt, platforms, keys)

            nearby_fulcrum = get_nearby_fulcrum(player, fulcrums)

            if e_pressed and nearby_fulcrum is not None:
                player.start_auto_grapple(nearby_fulcrum["anchor"], nearby_fulcrum["target"])

            if player.should_spawn_projectile:
                spawn_projectile(player, projectiles)
                player.should_spawn_projectile = False

            handle_player_attack(player, enemy)
            new_special_hitbox = handle_weapon_special(
                keys,
                player,
                enemy,
                returning_shields,
                u_was_pressed,
            )

            if new_special_hitbox is not None:
                grapple_special_hitbox = new_special_hitbox
                grapple_special_timer = 0.12

            u_was_pressed = keys[pygame.K_u]

            update_projectiles(projectiles, dt, platforms, enemy)
            update_returning_shields(returning_shields, dt, enemy)
            returning_shields = [shield for shield in returning_shields if shield.alive]
            player.has_active_shield_throw = len(returning_shields) > 0
            handle_enemy_attack(player, enemy)
            handle_enemy_coin_drop(enemy, coins)
            update_coins(coins, dt, platforms, player)
            coins = [coin for coin in coins if not coin.collected]
            projectiles = [projectile for projectile in projectiles if projectile.alive]

        screen.fill((18, 20, 30))

        for platform in platforms:
            pygame.draw.rect(screen, (120, 120, 130), platform)

        for fulcrum in fulcrums:
            pygame.draw.circle(screen, (150, 80, 230), fulcrum["anchor"], FULCRUM_RADIUS)
            pygame.draw.rect(screen, (150, 80, 230), fulcrum["rect"], 1)

        for coin in coins:
            coin.draw(screen)

        for projectile in projectiles:
            projectile.draw(screen)

        for shield in returning_shields:
            shield.draw(screen)

        enemy.draw(screen)
        player.draw(screen)

        weapon = get_weapon(player.current_weapon_id)
        if player.is_attacking and weapon["weapon_type"] != "projectile":
            pygame.draw.rect(screen, (70, 140, 255), player.get_attack_hitbox(), 2)

        if enemy.is_attacking and enemy.alive:
            pygame.draw.rect(screen, (255, 150, 50), enemy.get_attack_hitbox(), 2)

        if grapple_special_hitbox is not None:
            pygame.draw.rect(screen, (180, 80, 255), grapple_special_hitbox, 2)

        nearby_fulcrum = get_nearby_fulcrum(player, fulcrums)
        if nearby_fulcrum is not None and not player.is_auto_grappling:
            draw_interaction_text(screen, player)

        draw_player_ui(screen, player)
        draw_weapon_boxes(screen, player)

        if player.is_dead:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("GAME OVER", True, (255, 80, 80))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    pygame.quit()


def spawn_projectile(player, projectiles):
    weapon = get_weapon(player.current_weapon_id)

    if weapon["weapon_type"] != "projectile":
        return

    damage, is_critical = calculate_damage(player, weapon["damage"])

    if player.facing == 1:
        x = player.rect.right
    else:
        x = player.rect.left - weapon["width"]

    y = player.rect.centery - weapon["height"] // 2
    vel_x = weapon["projectile_speed"] * player.facing

    projectile = Projectile(
        x,
        y,
        weapon["width"],
        weapon["height"],
        vel_x,
        0,
        damage,
        is_critical,
        weapon["projectile_gravity"],
    )
    projectiles.append(projectile)


def handle_player_attack(player, enemy):
    weapon = get_weapon(player.current_weapon_id)

    if player.is_auto_grappling:
        return

    if not player.is_attacking or not enemy.alive:
        return

    if weapon["weapon_type"] == "projectile":
        return

    attack_hitbox = player.get_attack_hitbox()

    if attack_hitbox.colliderect(enemy.rect) and not player.attack_has_hit:
        damage, is_critical = calculate_damage(player, weapon["damage"])
        enemy.take_damage(damage)
        player.attack_has_hit = True

        if weapon["weapon_type"] == "grapple":
            enemy.stun(weapon["stun_time"])

        if is_critical:
            print(f"Hit enemy for {damage} damage CRITICAL")
        else:
            print(f"Hit enemy for {damage} damage")


def handle_weapon_special(keys, player, enemy, returning_shields, u_was_pressed):
    if player.is_auto_grappling:
        return None

    if not keys[pygame.K_u] or u_was_pressed:
        return None

    weapon = get_weapon(player.current_weapon_id)

    if player.special_cooldown_timer > 0:
        return None

    if weapon["id"] == "shield_weapon":
        return handle_shield_special(player, returning_shields, weapon)

    if weapon["id"] != "grapple_weapon":
        return None

    special_hitbox = get_grapple_special_hitbox(player)

    if enemy.alive and special_hitbox.colliderect(enemy.rect):
        enemy.start_pull_to_player(player)

    player.special_cooldown_timer = WEAPON_SPECIAL_COOLDOWN
    return special_hitbox


def handle_shield_special(player, returning_shields, weapon):
    if player.is_blocking:
        print("Cannot throw shield while blocking")
        return None

    if player.guard_broken_timer > 0:
        print("Cannot throw shield during guard break")
        return None

    if player.has_active_shield_throw:
        return None

    damage, is_critical = calculate_damage(player, weapon["damage"])
    shield = ReturningShield(
        player.rect.centerx,
        player.rect.centery,
        player.facing,
        damage,
        is_critical,
        player,
    )
    returning_shields.append(shield)
    player.has_active_shield_throw = True
    player.special_cooldown_timer = WEAPON_SPECIAL_COOLDOWN
    print("Shield thrown")
    return None


def get_grapple_special_hitbox(player):
    weapon = get_weapon("grapple_weapon")
    hitbox_y = player.rect.centery - weapon["height"] // 2

    if player.facing == 1:
        hitbox_x = player.rect.right
    else:
        hitbox_x = player.rect.left - weapon["range"]

    return pygame.Rect(hitbox_x, hitbox_y, weapon["width"], weapon["height"])


def update_projectiles(projectiles, dt, platforms, enemy):
    for projectile in projectiles:
        projectile.update(dt, platforms)

        if enemy.alive and projectile.alive and projectile.rect.colliderect(enemy.rect):
            enemy.take_damage(projectile.damage)
            projectile.alive = False


def update_returning_shields(returning_shields, dt, enemy):
    for shield in returning_shields:
        shield.update(dt)
        shield.check_enemy_collision(enemy)


def handle_enemy_attack(player, enemy):
    if not enemy.is_attacking or not enemy.alive:
        return

    if player.is_auto_grappling:
        return

    enemy_attack_hitbox = enemy.get_attack_hitbox()

    if not enemy_attack_hitbox.colliderect(player.rect) or enemy.attack_has_hit:
        return

    weapon = get_weapon(player.current_weapon_id)

    if weapon["id"] == "shield_weapon" and player.is_blocking and player.current_stamina > 0:
        player.block_hit()
        enemy.attack_has_hit = True
        print("Blocked")
    elif player.is_parrying:
        enemy.stun(NORMAL_PARRY_STUN_TIME)
        enemy.attack_has_hit = True
        print("Parried")
    else:
        player.take_damage(ENEMY_DAMAGE)
        enemy.attack_has_hit = True


def handle_enemy_coin_drop(enemy, coins):
    if enemy.alive or enemy.dropped_coins:
        return

    coins.append(Coin(enemy.rect.centerx - 20, enemy.rect.centery, COIN_VALUE))
    coins.append(Coin(enemy.rect.centerx, enemy.rect.centery, COIN_VALUE))
    coins.append(Coin(enemy.rect.centerx + 20, enemy.rect.centery, COIN_VALUE))
    enemy.dropped_coins = True


def update_coins(coins, dt, platforms, player):
    for coin in coins:
        coin.update(dt, platforms)
        pickup_rect = coin.rect.inflate(COIN_PICKUP_RANGE * 2, COIN_PICKUP_RANGE * 2)

        if player.rect.colliderect(pickup_rect):
            player.collect_coin(coin)


def get_nearby_fulcrum(player, fulcrums):
    if get_weapon(player.current_weapon_id)["id"] != "grapple_weapon":
        return None

    if player.is_auto_grappling:
        return None

    player_x, player_y = player.rect.center

    for fulcrum in fulcrums:
        anchor_x, anchor_y = fulcrum["anchor"]
        distance = math.hypot(player_x - anchor_x, player_y - anchor_y)

        if distance <= FULCRUM_INTERACT_DISTANCE:
            return fulcrum

    return None


def draw_interaction_text(screen, player):
    font = pygame.font.Font(None, 30)
    text = font.render("Press E to grapple", True, (235, 225, 255))
    text_rect = text.get_rect(midbottom=(player.rect.centerx, player.rect.top - 12))
    screen.blit(text, text_rect)


if __name__ == "__main__":
    main()
