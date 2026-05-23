import math

import pygame

from settings import (
    COIN_PICKUP_RANGE,
    COIN_VALUE,
    DEBUG_MODE,
    ENEMY_DAMAGE,
    FPS,
    FULCRUM_INTERACT_DISTANCE,
    FULCRUM_RADIUS,
    GAME_OVER_POPUP_HEIGHT,
    GAME_OVER_POPUP_WIDTH,
    ENERGY_BEAM_DAMAGE,
    ENERGY_BEAM_HEIGHT,
    ENERGY_BEAM_RANGE,
    EXECUTE_HP_THRESHOLD,
    EXECUTE_PARRY_WINDOW,
    EXECUTE_RANGE,
    NORMAL_PARRY_STUN_TIME,
    ORBIT_BLADE_COUNT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SOUL_ANCHOR_DURATION,
    SOUL_ANCHOR_RETURN_COST,
    TIME_FREEZE_DURATION,
    TITLE,
    WEAPON_SPECIAL_COOLDOWN,
    PIXELATE_GAME, 
    PIXEL_WIDTH, 
    PIXEL_HEIGHT
)
from src.core.camera import Camera
from src.entities.enemy import Enemy
from src.entities.moon_shard import MoonShard
from src.entities.player import Player
from src.levels.level_manager import LevelManager
from src.systems.coin import Coin
from src.systems.combat import calculate_damage
from src.systems.dev_teleport import DevTeleport
from src.systems.projectile import Projectile, ReturningShield
from src.systems.shop import Shop
from src.systems.skills import (
    EnergyBeamEffect,
    OrbitBlade,
    SkillCircleEffect,
    TimeFreezeDomain,
    get_skill,
)
from src.systems.weapons import get_weapon
from src.ui.ui import draw_player_ui, draw_skill_boxes, draw_weapon_boxes


def main():
    pygame.init()

    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    level_manager = LevelManager()
    player = Player(100, 500)
    enemy = Enemy(0, 0)
    moon_shard = MoonShard()
    current_map = level_manager.get_current_map()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, current_map.width, current_map.height)
    level_manager.change_map(0, player, enemy, camera)
    moon_shard.reset_to(player.rect, player.facing)
    initial_shop_rect = level_manager.get_shop_rect()

    if initial_shop_rect is None:
        initial_shop_rect = pygame.Rect(0, 0, 1, 1)

    shop = Shop(
        initial_shop_rect.x,
        initial_shop_rect.y,
        initial_shop_rect.width,
        initial_shop_rect.height,
    )

    coins = []
    projectiles = []
    returning_shields = []
    time_freeze_domains = []
    active_orbit_blades = []
    active_skill_effects = []

    u_was_pressed = False
    grapple_special_hitbox = None
    grapple_special_timer = 0
    game_state = "playing"

    
    dev_teleport = DevTeleport()

    def teleport_player_to(target):
        """Snap the player to a dev teleport target on any map."""
        if isinstance(target, dict):
            target_map_id = target.get("map_id", 0)
            pos = target.get("pos")
        else:
            target_map_id = 0
            pos = target

        if level_manager.get_current_map().map_id != target_map_id:
            if not enter_map(target_map_id):
                return

        if pos is not None:
            player.rect.midbottom = pos

        player.vel_x = 0
        player.vel_y = 0
        player.is_dashing = False
        player.is_attacking = False
        player.is_auto_grappling = False
        player.is_blocking = False
        player.is_parrying = False
        camera.snap_to(player.rect)
        moon_shard.reset_to(player.rect, player.facing)

    def clear_world_objects():
        nonlocal u_was_pressed, grapple_special_hitbox, grapple_special_timer
        coins.clear()
        projectiles.clear()
        returning_shields.clear()
        time_freeze_domains.clear()
        active_orbit_blades.clear()
        active_skill_effects.clear()
        player.has_active_shield_throw = False
        grapple_special_hitbox = None
        grapple_special_timer = 0
        u_was_pressed = False

    def enter_map(target_map_id):
        changed = level_manager.change_map(target_map_id, player, enemy, camera)
        if not changed:
            return False

        clear_world_objects()
        shop.close()
        shop_rect = level_manager.get_shop_rect()
        if shop_rect is not None:
            shop.set_rect(shop_rect)
            shop.refresh_products()
        moon_shard.reset_to(player.rect, player.facing)
        return True

    def restart_game():
        nonlocal game_state
        player.current_hp = player.max_hp
        player.hp = player.current_hp
        player.current_mana = player.max_mana
        player.mana = player.current_mana
        player.current_stamina = player.max_stamina
        level_manager.reset_one_use_items()
        player.is_dead = False
        player.invincible_timer = 0
        player.vel_x = 0
        player.vel_y = 0
        enter_map(0)
        game_state = "playing"

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        e_pressed = False
        e_released = False
        k_pressed = False
        current_map = level_manager.get_current_map()
        shop_active = level_manager.get_shop_rect() is not None

        if not shop_active and shop.is_open:
            shop.close()

        nearby_door = level_manager.check_doors(player)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Dev teleport — click on a button in the overlay
                if dev_teleport.visible:
                    section_idx = dev_teleport.handle_click(event.pos)
                    if section_idx is not None:
                        target = dev_teleport.get_target(section_idx)
                        if target is not None:
                            teleport_player_to(target)
                            dev_teleport.close()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    e_released = True
            elif event.type == pygame.KEYDOWN:

                                # ----- Dev teleport (F3) takes priority over everything else -----
                if event.key == pygame.K_F3:
                    dev_teleport.toggle()
                    continue

                if dev_teleport.visible:
                    if event.key == pygame.K_ESCAPE:
                        dev_teleport.close()
                        continue
                    section_idx = dev_teleport.handle_key(event.key)
                    if section_idx is not None:
                        target = dev_teleport.get_target(section_idx)
                        if target is not None:
                            teleport_player_to(target)
                            dev_teleport.close()
                    continue   # while overlay is open, swallow other keys
                # ----------------------------------------------------------------

                if game_state in ("game_over", "victory"):
                    if event.key == pygame.K_r:
                        restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    continue

                if event.key == pygame.K_F1:
                    player.toggle_unlimited_hp()

                if event.key == pygame.K_F2:
                    player.toggle_unlimited_mana()

                if event.key == pygame.K_e:
                    if level_manager.use_moon_altar(player):
                        pass
                    elif shop_active and shop.can_interact(player):
                        shop.toggle()
                    elif nearby_door is not None:
                        target_map = nearby_door["target_map"]
                        if isinstance(target_map, int):
                            enter_map(target_map)
                        elif target_map == "victory":
                            game_state = "victory"
                    else:
                        e_pressed = True

                if event.key == pygame.K_k:
                    k_pressed = True

                if shop.is_open:
                    shop.handle_key(event, player)

        current_map = level_manager.get_current_map()
        keys = pygame.key.get_pressed()
        platforms = level_manager.get_platforms()
        fulcrums = level_manager.get_fulcrums()

        if game_state == "playing" and not shop.is_open:
            if grapple_special_timer > 0:
                grapple_special_timer -= dt
            else:
                grapple_special_hitbox = None

            for domain in time_freeze_domains:
                domain.update(dt, enemy)
            time_freeze_domains = [domain for domain in time_freeze_domains if domain.alive]

            enemy.update(dt, player)

        if game_state == "playing" and not player.is_dead and not shop.is_open:
            player.handle_input(keys)
            previous_map_id = current_map.map_id
            player.update(dt, platforms, keys)
            level_manager.update_collapsing_lift(dt, player)
            level_manager.update_moving_platforms(dt, player)

            transition_target = level_manager.get_collapsing_lift_transition_target(player)
            if transition_target is not None:
                if isinstance(transition_target, int):
                    enter_map(transition_target)
                elif transition_target == "victory":
                    game_state = "victory"

            current_map = level_manager.get_current_map()
            map_changed = previous_map_id != current_map.map_id

            if not map_changed:
                auto_door = level_manager.check_auto_doors(player)
                if auto_door is not None:
                    target_map = auto_door["target_map"]
                    if isinstance(target_map, int):
                        enter_map(target_map)
                    elif target_map == "victory":
                        game_state = "victory"
                    current_map = level_manager.get_current_map()
                    map_changed = True

            if not map_changed and level_manager.is_player_in_deadly_void(player):
                kill_player_instantly(player)

            clamp_player_to_map(player, current_map)

            if k_pressed and not map_changed:
                activate_current_skill(
                    player,
                    enemy,
                    time_freeze_domains,
                    active_orbit_blades,
                    active_skill_effects,
                )

            nearby_fulcrum = get_nearby_fulcrum(player, fulcrums)

            if e_pressed and nearby_fulcrum is not None and not map_changed:
                if current_map.map_id == 2:
                    player.start_swing(nearby_fulcrum["anchor"])
                else:
                    player.start_auto_grapple(nearby_fulcrum["anchor"], nearby_fulcrum["target"])

            if e_released and player.is_swinging:
                player.release_swing()

            if player.should_spawn_projectile and not map_changed:
                spawn_projectile(player, projectiles)
                player.should_spawn_projectile = False

            if not map_changed:
                handle_player_attack(player, enemy)
                new_special_hitbox = handle_weapon_special(
                    keys,
                    player,
                    enemy,
                    returning_shields,
                    u_was_pressed,
                )
            else:
                new_special_hitbox = None

            if new_special_hitbox is not None:
                grapple_special_hitbox = new_special_hitbox
                grapple_special_timer = 0.12

            if not map_changed:
                u_was_pressed = keys[pygame.K_u]

            update_projectiles(projectiles, dt, platforms, enemy)
            update_returning_shields(returning_shields, dt, enemy)
            update_orbit_blades(active_orbit_blades, dt, player, enemy)
            returning_shields = [shield for shield in returning_shields if shield.alive]
            active_orbit_blades = [blade for blade in active_orbit_blades if blade.alive]
            player.has_active_shield_throw = len(returning_shields) > 0
            handle_enemy_attack(player, enemy)
            handle_enemy_coin_drop(enemy, coins)
            update_coins(coins, dt, platforms, player)
            coins = [coin for coin in coins if not coin.collected]
            projectiles = [projectile for projectile in projectiles if projectile.alive]

        if player.is_dead and game_state == "playing":
            game_state = "game_over"

        camera.update(player.rect)

        if game_state == "playing" and not shop.is_open:
            for effect in active_skill_effects:
                effect.update(dt)
            active_skill_effects = [effect for effect in active_skill_effects if effect.alive]

        # Moon shard floats with the player even while paused (gives life to the scene).
        # Trails on the opposite side of the player's facing direction.
        moon_shard.update(dt, player.rect, player.facing)

        
        # Dev teleport hover highlight
        dev_teleport.update_hover(pygame.mouse.get_pos())

        #screen.fill((18, 20, 30))# Background is drawn inside level_manager.draw_current_map()

        level_manager.draw_current_map(screen, camera)

        current_map = level_manager.get_current_map()
        shop_active = level_manager.get_shop_rect() is not None

        if shop_active:
            shop.draw_shop_area(screen, camera)

        # MAP 2 grapple fulcrums: visible anchor points from Tiled.
        if current_map.map_id == 2:
            for fulcrum in fulcrums:
                anchor_pos = camera.apply_pos(fulcrum["anchor"])
                pygame.draw.circle(screen, (42, 28, 70), anchor_pos, 30)
                pygame.draw.circle(screen, (110, 65, 170), anchor_pos, 22)
                pygame.draw.circle(screen, (170, 95, 235), anchor_pos, 15)
                pygame.draw.circle(screen, (235, 220, 255), anchor_pos, 6)
                pygame.draw.circle(screen, (205, 160, 255), anchor_pos, 30, 2)

        for coin in coins:
            coin.draw(screen, camera)

        for projectile in projectiles:
            projectile.draw(screen, camera)

        for shield in returning_shields:
            shield.draw(screen, camera)

        for domain in time_freeze_domains:
            domain.draw(screen, camera)

        for blade in active_orbit_blades:
            blade.draw(screen, camera)

        for effect in active_skill_effects:
            effect.draw(screen, camera)

        enemy.draw(screen, camera)
        player.draw(screen, camera)
        # Moon shard renders on top so its glow doesn't get hidden behind the player.
        moon_shard.draw(screen, camera)

        weapon = get_weapon(player.current_weapon_id)
        if player.is_attacking and weapon["weapon_type"] != "projectile":
            pygame.draw.rect(screen, (70, 140, 255), camera.apply_rect(player.get_attack_hitbox()), 2)

        if enemy.is_attacking and enemy.alive:
            pygame.draw.rect(screen, (255, 150, 50), camera.apply_rect(enemy.get_attack_hitbox()), 2)

        if grapple_special_hitbox is not None:
            pygame.draw.rect(screen, (180, 80, 255), camera.apply_rect(grapple_special_hitbox), 2)

        nearby_fulcrum = get_nearby_fulcrum(player, fulcrums)
        if nearby_fulcrum is not None and not player.is_auto_grappling:
            draw_interaction_text(screen, player, camera)

        if level_manager.can_use_moon_altar(player) and not shop.is_open:
            draw_moon_altar_interaction_text(screen, level_manager.get_moon_altar_rect(), camera)

        if shop_active and shop.can_interact(player) and not shop.is_open:
            draw_shop_interaction_text(screen, shop, camera)

        nearby_door = level_manager.check_doors(player)
        if nearby_door is not None:
            draw_door_interaction_text(screen, nearby_door, camera)

        draw_player_ui(screen, player, level_manager.get_current_map().name)

        if DEBUG_MODE:
            draw_weapon_boxes(screen, player)
            draw_skill_boxes(screen, player)

        if shop.is_open:
            shop.draw_shop_menu(screen, player)

        if game_state == "game_over":
            draw_popup(screen, "GAME OVER", "You were defeated.")
        elif game_state == "victory":
            draw_popup(screen, "PROTOTYPE COMPLETE", "You reached the final door.")
        if PIXELATE_GAME:
            small_surface = pygame.transform.scale(screen, (PIXEL_WIDTH, PIXEL_HEIGHT))
            pixel_surface = pygame.transform.scale(small_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            window.blit(pixel_surface, (0, 0))
            # Draw dev tools after pixel scaling so F3 text stays readable.
            dev_teleport.draw(window)
        else:
            # Dev teleport overlay is drawn last so it sits on top of everything.
            dev_teleport.draw(screen)
            window.blit(screen, (0, 0))

        pygame.display.flip()

    pygame.quit()


def spawn_projectile(player, projectiles):
    weapon = get_weapon(player.current_weapon_id)

    if weapon["weapon_type"] != "projectile":
        return

    damage, is_critical = calculate_damage(player, weapon["damage"])

    projectile = Projectile(
        player.rect.centerx,
        player.rect.centery,
        player.facing,
        damage,
        is_critical,
        weapon.get("projectile_speed", 12),
        weapon.get("projectile_max_distance", 350),
        "weapon",
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


def update_orbit_blades(active_orbit_blades, dt, player, enemy):
    for blade in active_orbit_blades:
        blade.update(dt, player, enemy)


def activate_current_skill(
    player,
    enemy,
    time_freeze_domains,
    active_orbit_blades,
    active_skill_effects,
):
    skill = get_skill(player.current_skill_id)

    if skill["skill_type"] == "soul_anchor" and player.soul_anchor_active:
        activate_soul_anchor(player, skill, active_skill_effects)
        return

    if not player.can_use_skill(skill):
        print("Cannot use skill")
        return

    if skill["skill_type"] == "time_freeze":
        player.spend_skill_cost(skill)
        time_freeze_domains.append(TimeFreezeDomain(player.rect.center, TIME_FREEZE_DURATION))
        print("Time Freeze")

    elif skill["skill_type"] == "orbit_blades":
        player.spend_skill_cost(skill)
        for index in range(ORBIT_BLADE_COUNT):
            active_orbit_blades.append(OrbitBlade(player, index, ORBIT_BLADE_COUNT))
        print("Orbit Blades")

    elif skill["skill_type"] == "energy_beam":
        player.spend_skill_cost(skill)
        beam_rect = get_energy_beam_rect(player)
        if enemy.alive and beam_rect.colliderect(enemy.rect):
            enemy.take_damage(ENERGY_BEAM_DAMAGE)
            print("Energy Beam hit enemy")
        active_skill_effects.append(EnergyBeamEffect(beam_rect))

    elif skill["skill_type"] == "execute":
        activate_execute_strike(player, enemy, skill, active_skill_effects)

    elif skill["skill_type"] == "soul_anchor":
        activate_soul_anchor(player, skill, active_skill_effects)


def get_energy_beam_rect(player):
    y = player.rect.centery - ENERGY_BEAM_HEIGHT // 2

    if player.facing == 1:
        x = player.rect.right
    else:
        x = player.rect.left - ENERGY_BEAM_RANGE

    return pygame.Rect(x, y, ENERGY_BEAM_RANGE, ENERGY_BEAM_HEIGHT)


def activate_execute_strike(player, enemy, skill, active_skill_effects):
    target = get_enemy_in_front(player, enemy, EXECUTE_RANGE)

    if target is None:
        print("Enemy is not executable")
        return

    hp_is_low = target.current_hp <= target.max_hp * EXECUTE_HP_THRESHOLD
    if not hp_is_low and not target.is_executable:
        print("Enemy is not executable")
        return

    player.spend_skill_cost(skill)
    target.execute()
    active_skill_effects.append(SkillCircleEffect(target.rect.center, 42, (255, 80, 40)))
    print("Executed enemy")


def get_enemy_in_front(player, enemy, skill_range):
    if not enemy.alive:
        return None

    if player.facing == 1 and enemy.rect.centerx < player.rect.centerx:
        return None

    if player.facing == -1 and enemy.rect.centerx > player.rect.centerx:
        return None

    distance = math.hypot(
        enemy.rect.centerx - player.rect.centerx,
        enemy.rect.centery - player.rect.centery,
    )
    if distance <= skill_range:
        return enemy

    return None


def activate_soul_anchor(player, skill, active_skill_effects):
    if player.is_dead or player.is_auto_grappling:
        return

    if player.soul_anchor_active:
        if not player.debug_unlimited_mana and player.current_mana < SOUL_ANCHOR_RETURN_COST:
            print("Not enough mana to return")
            return

        if not player.debug_unlimited_mana:
            player.current_mana -= SOUL_ANCHOR_RETURN_COST

        player.rect.center = player.soul_anchor_pos
        player.vel_x = 0
        player.vel_y = 0
        player.soul_anchor_active = False
        player.soul_anchor_pos = None
        player.soul_anchor_timer = 0
        active_skill_effects.append(SkillCircleEffect(player.rect.center, 34, (120, 255, 180)))
        print("Returned to Soul Anchor")
        return

    player.spend_skill_cost(skill)
    player.soul_anchor_active = True
    player.soul_anchor_pos = player.rect.center
    player.soul_anchor_timer = SOUL_ANCHOR_DURATION
    active_skill_effects.append(SkillCircleEffect(player.soul_anchor_pos, 28, (120, 255, 180)))
    print("Soul Anchor placed")


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
        enemy.mark_executable(EXECUTE_PARRY_WINDOW)
        enemy.attack_has_hit = True
        print("Parried")
        print("Perfect parry: enemy executable")
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


def clamp_player_to_map(player, game_map):
    if player.rect.left < 0:
        player.rect.left = 0

    if player.rect.right > game_map.width:
        player.rect.right = game_map.width

    if player.rect.bottom > game_map.height:
        player.rect.bottom = game_map.height
        player.vel_y = 0
        player.on_ground = True


def kill_player_instantly(player):
    player.current_hp = 0
    player.hp = 0
    player.is_dead = True
    player.invincible_timer = 0
    player.vel_x = 0
    player.vel_y = 0
    player.is_dashing = False
    player.is_attacking = False
    player.is_auto_grappling = False
    player.is_blocking = False
    player.is_parrying = False


def get_nearby_fulcrum(player, fulcrums):
    if player.is_auto_grappling or getattr(player, "is_swinging", False):
        return None

    player_x, player_y = player.rect.center

    for fulcrum in fulcrums:
        requires_grapple_weapon = fulcrum.get("requires_grapple_weapon", True)
        if requires_grapple_weapon and get_weapon(player.current_weapon_id)["id"] != "grapple_weapon":
            continue

        anchor_x, anchor_y = fulcrum["anchor"]
        distance = math.hypot(player_x - anchor_x, player_y - anchor_y)

        interact_distance = fulcrum.get("interact_distance", FULCRUM_INTERACT_DISTANCE)
        if distance <= interact_distance:
            return fulcrum

    return None

def draw_interaction_text(screen, player, camera=None):
    font = pygame.font.Font(None, 30)
    text = font.render("Press E to grapple", True, (235, 225, 255))
    pos = (player.rect.centerx, player.rect.top - 12)
    if camera:
        pos = camera.apply_pos(pos)
    text_rect = text.get_rect(midbottom=pos)
    screen.blit(text, text_rect)


def draw_moon_altar_interaction_text(screen, altar_rect, camera=None):
    font = pygame.font.Font(None, 26)
    text = font.render("Press E to restore at Moon Altar", True, (190, 235, 255))
    pos = (altar_rect.centerx, altar_rect.top - 14)
    if camera:
        pos = camera.apply_pos(pos)
    screen.blit(text, text.get_rect(center=pos))


def draw_shop_interaction_text(screen, shop, camera=None):
    font = pygame.font.Font(None, 30)
    text = font.render("Press E to open shop", True, (255, 245, 180))
    pos = (shop.rect.centerx, shop.rect.top - 12)
    if camera:
        pos = camera.apply_pos(pos)
    text_rect = text.get_rect(midbottom=pos)
    screen.blit(text, text_rect)


def draw_door_interaction_text(screen, door, camera=None):
    font = pygame.font.Font(None, 30)
    prompt = door.get("prompt", "Press E to enter")
    text = font.render(prompt, True, (220, 255, 220))
    rect = door["rect"]
    pos = (rect.centerx, rect.top - 12)
    if camera:
        pos = camera.apply_pos(pos)
    text_rect = text.get_rect(midbottom=pos)
    screen.blit(text, text_rect)


def draw_level_complete_text(screen):
    font = pygame.font.Font(None, 44)
    text = font.render("Level Complete", True, (120, 255, 160))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 120))
    screen.blit(text, text_rect)


def draw_popup(screen, title, message):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(0, 0, GAME_OVER_POPUP_WIDTH, GAME_OVER_POPUP_HEIGHT)
    panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.rect(screen, (24, 24, 34), panel)
    pygame.draw.rect(screen, (235, 220, 140), panel, 3)

    title_font = pygame.font.Font(None, 56)
    text_font = pygame.font.Font(None, 30)

    title_text = title_font.render(title, True, (255, 245, 180))
    message_text = text_font.render(message, True, (235, 235, 235))
    restart_text = text_font.render("Press R to Restart", True, (235, 235, 235))
    quit_text = text_font.render("Press ESC to Quit", True, (235, 235, 235))

    screen.blit(title_text, title_text.get_rect(center=(panel.centerx, panel.y + 58)))
    screen.blit(message_text, message_text.get_rect(center=(panel.centerx, panel.y + 112)))
    screen.blit(restart_text, restart_text.get_rect(center=(panel.centerx, panel.y + 170)))
    screen.blit(quit_text, quit_text.get_rect(center=(panel.centerx, panel.y + 208)))


if __name__ == "__main__":
    main()
