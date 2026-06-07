import json
import math
from pathlib import Path

import pygame

from src.audio.audio import MusicManager
from settings import (
    COIN_PICKUP_RANGE,
    COIN_VALUE,
    DEBUG_DRAW_HITBOXES,
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
    EXECUTE_PARRY_WINDOW,
    BOSS_PLAYER_SPAWN_X,
    BOSS_PLAYER_SPAWN_Y,
    BOSS_ROOM_HEIGHT,
    BOSS_ROOM_MAX_X,
    BOSS_ROOM_MAX_Y,
    BOSS_ROOM_MIN_X,
    BOSS_ROOM_MIN_Y,
    BOSS_ROOM_WIDTH,
    NORMAL_PARRY_STUN_TIME,
    ORBIT_BLADE_COUNT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOOTER_BULLET_MAX_DISTANCE,
    SHOOTER_BULLET_MUZZLE_OFFSET_X,
    SHOOTER_BULLET_MUZZLE_OFFSET_Y,
    SHOOTER_BULLET_SPEED,
    SOUL_ANCHOR_DURATION,
    SOUL_ANCHOR_RETURN_COST,
    TIME_FREEZE_RADIUS,
    TIME_FREEZE_STUN_DURATION,
    TITLE,
    PIXELATE_GAME, 
    PIXEL_WIDTH, 
    PIXEL_HEIGHT
)
from src.core.camera import Camera
from src.entities.archer import ArcherEnemy
from src.entities.boss import (
    BOSS_ARENA_BOTTOM,
    BOSS_ARENA_LEFT,
    BOSS_ARENA_RIGHT,
    BOSS_ARENA_TOP,
    PaleCoreBoss,
)
from src.entities.enemy import Enemy
from src.entities.mage import MageEnemy
from src.entities.moon_shard import MoonShard
from src.entities.player import Player
from src.levels.level_manager import LevelManager
from src.systems.coin import Coin
from src.systems.combat import calculate_damage
from src.systems.dev_teleport import DevTeleport
from src.systems.projectile import (
    Projectile,
    ProjectileHitEffect,
    print_projectile_asset_debug_summary,
)
from src.systems.shop import Shop
from src.systems.skills import (
    EnergyBeamEffect,
    OrbitBlade,
    SkillSpriteEffect,
    SoulAnchorLoop,
    TimeFreezeDomain,
    get_skill,
    get_skill_frames,
    print_skill_asset_debug_summary,
)
from src.systems.weapons import get_weapon
from src.ui.main_menu import MainMenu
from src.ui.origin_story import OriginStory
from src.ui.pause_menu import PauseMenu
from src.ui.dialogue import DialogueSystem
from src.ui.ui import draw_player_ui, draw_skill_boxes, draw_weapon_boxes


PROJECT_ROOT = Path(__file__).resolve().parent
ENEMY_SPAWN_PATH = PROJECT_ROOT / "assets" / "maps" / "enemy_spawns.json"
DEBUG_FORCE_TEST_ENEMY = False
DEBUG_ENEMY_AI = False
ARCHER_SPAWNS = [
    {"x": 863, "y": 260, "mode": "static", "patrol_left": 0, "patrol_right": 0},
    {"x": 1802, "y": 200, "mode": "patrol", "patrol_left": 80, "patrol_right": 80},
    {"x": 2567, "y": 270, "mode": "patrol", "patrol_left": 80, "patrol_right": 40},
    {"x": 2794, "y": 420, "mode": "static", "patrol_left": 0, "patrol_right": 0},
    {"x": 6308, "y": 200, "mode": "patrol", "patrol_left": 100, "patrol_right": 100},
    {"x": 7289, "y": 150, "mode": "patrol", "patrol_left": 80, "patrol_right": 40},
    {"x": 9162, "y": 180, "mode": "static", "patrol_left": 0, "patrol_right": 0},
    {"x": 10747, "y": 290, "mode": "static", "patrol_left": 0, "patrol_right": 0},
]
MELEE_SPAWNS = [
    {"x": 632, "y": 400, "mode": "static", "patrol_left": 0, "patrol_right": 0},
    {"x": 1569, "y": 600, "mode": "patrol", "patrol_left": 80, "patrol_right": 80},
    {"x": 2937, "y": 650, "mode": "patrol", "patrol_left": 80, "patrol_right": 80},
    {"x": 3674, "y": 650, "mode": "patrol", "patrol_left": 80, "patrol_right": 80},
    {"x": 3674, "y": 240, "mode": "patrol", "patrol_left": 70, "patrol_right": 70},
    {"x": 4553, "y": 560, "mode": "static", "patrol_left": 0, "patrol_right": 0},
    {"x": 6000, "y": 650, "mode": "patrol", "patrol_left": 80, "patrol_right": 80},
    {"x": 7233, "y": 650, "mode": "patrol", "patrol_left": 80, "patrol_right": 80},
    {"x": 8187, "y": 380, "mode": "patrol", "patrol_left": 80, "patrol_right": 80},
]
MAGE_SPAWNS = [
    {"x": 2216, "y": 300, "mode": "static"},
    {"x": 5350, "y": 500, "mode": "static"},
    {"x": 8840, "y": 390, "mode": "static"},  # Last mage moved higher for better platform alignment.
]
LEVEL5_BOSS_MAP_ID = 8
BOSS_SECTION_BOUNDS = pygame.Rect(BOSS_ARENA_LEFT, BOSS_ARENA_TOP, BOSS_ARENA_RIGHT - BOSS_ARENA_LEFT, BOSS_ARENA_BOTTOM - BOSS_ARENA_TOP)
BOSS_SECTION_SPAWN = (BOSS_PLAYER_SPAWN_X, BOSS_PLAYER_SPAWN_Y)


def draw_start_tutorial(screen, camera, current_map):
    if current_map.map_id != 0:
        return

    font = pygame.font.Font(None, 28)
    lines = [
        "Controls:",
        "A / D = Walk",
        "W / Space = Jump",
        "Shift = Dash",
        "J = Attack",
        "K = Skill",
        "L = Parry",
    ]
    padding = 12
    line_gap = 4
    rendered_lines = [font.render(line, True, (245, 245, 255)) for line in lines]
    panel_width = max(line.get_width() for line in rendered_lines) + padding * 2
    panel_height = sum(line.get_height() for line in rendered_lines) + line_gap * (len(lines) - 1) + padding * 2
    screen_x, screen_y = camera.apply_pos((330, 70))

    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((12, 16, 28, 175))
    pygame.draw.rect(panel, (180, 195, 225, 190), panel.get_rect(), 1)

    text_y = padding
    for line in rendered_lines:
        panel.blit(line, (padding, text_y))
        text_y += line.get_height() + line_gap

    screen.blit(panel, (screen_x, screen_y))


def main():
    pygame.init()

    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    music_manager = MusicManager()
    print_skill_asset_debug_summary()
    print_projectile_asset_debug_summary()

    level_manager = LevelManager()
    player = Player(100, 500)
    enemy = Enemy(0, 0)
    pale_core_boss = PaleCoreBoss()
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
    projectile_hit_effects = []
    enemies = []
    archers = []
    archer_arrows = []
    time_freeze_domains = []
    active_orbit_blades = []
    active_skill_effects = []
    soul_anchor_loops = []

    enemy_debug_frame = 0
    game_state = "menu"
    opening_dialogue_seen = False
    show_player_debug_overlay = False
    killed_enemy_ids = set()
    boss_section_locked = False
    boss_room_debug_printed = False

    
    dev_teleport = DevTeleport()
    main_menu = MainMenu()
    origin_story = OriginStory()
    dialogue = DialogueSystem()
    pause_menu = PauseMenu()

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

    def current_map_is_shop_safe():
        current = level_manager.get_current_map()
        return current.shop_rect is not None or current.map_type in ("checkpoint_stage", "rest_stage")

    def enemy_was_killed(removed_enemy):
        enemy_id = getattr(removed_enemy, "enemy_id", None)
        if not enemy_id:
            return
        if enemy_id not in killed_enemy_ids:
            killed_enemy_ids.add(enemy_id)
            print("[ENEMY KILLED]", enemy_id)

    def should_skip_dead_spawn(enemy_id):
        if enemy_id in killed_enemy_ids:
            print("[SKIP DEAD ENEMY SPAWN]", enemy_id)
            return True
        return False

    def clamp_player_to_boss_section():
        if not boss_section_locked:
            return

        if player.rect.left < BOSS_SECTION_BOUNDS.left:
            player.rect.left = BOSS_SECTION_BOUNDS.left
            player.vel_x = max(0, player.vel_x)
        if player.rect.right > BOSS_SECTION_BOUNDS.right:
            player.rect.right = BOSS_SECTION_BOUNDS.right
            player.vel_x = min(0, player.vel_x)
        if player.rect.top < BOSS_SECTION_BOUNDS.top:
            player.rect.top = BOSS_SECTION_BOUNDS.top
            player.vel_y = max(0, player.vel_y)
        if player.rect.bottom > BOSS_SECTION_BOUNDS.bottom:
            player.rect.bottom = BOSS_SECTION_BOUNDS.bottom
            player.vel_y = 0
            player.on_ground = True

    def enter_boss_final_section():
        nonlocal boss_section_locked, boss_room_debug_printed
        if not enter_map(LEVEL5_BOSS_MAP_ID):
            return False

        boss_section_locked = True
        player.rect.midbottom = BOSS_SECTION_SPAWN
        player.vel_x = 0
        player.vel_y = 0
        clamp_player_to_boss_section()
        camera.set_bounds(BOSS_SECTION_BOUNDS)
        camera.snap_to(player.rect)
        pale_core_boss.active = False
        if not boss_room_debug_printed:
            print("[BOSS ROOM BOUNDS]", BOSS_ROOM_MIN_X, BOSS_ROOM_MAX_X, BOSS_ROOM_MIN_Y, BOSS_ROOM_MAX_Y)
            print("[BOSS ROOM SIZE]", BOSS_ROOM_WIDTH, BOSS_ROOM_HEIGHT)
            print(
                "[BOSS BG SIZE]",
                pale_core_boss.boss_room_background_source_size,
                "scaled to",
                pale_core_boss.boss_room_background.get_size() if pale_core_boss.boss_room_background else None,
            )
            print("[BOSS CORE RECT]", pale_core_boss.boss_core_rect)
            print("[BOSS HEAD RECT]", pale_core_boss.boss_head_rect)
            print("[WEAK POINT IMAGE REMOVED] using lunar core glow")
            boss_room_debug_printed = True
        print("[BOSS SECTION LOCKED]", BOSS_SECTION_BOUNDS)
        return True

    def debug_remove_enemy(reason, removed_enemy):
        hp = getattr(removed_enemy, "current_hp", getattr(removed_enemy, "hp", None))
        print("[ENEMY REMOVED]", reason, removed_enemy.rect, hp)

    def sync_primary_enemy():
        if enemies:
            return enemies[0]
        enemy.disable()
        return enemy

    def print_room_clear_debug():
        room_cleared = len(enemies) == 0
        boss_stage_active = pale_core_boss.active
        normal_enemy_spawn_enabled = level_manager.get_current_map().map_type != "boss_stage"
        print("room_cleared:", room_cleared)
        print("boss_stage_active:", boss_stage_active)
        print("normal_enemy_spawn_enabled:", normal_enemy_spawn_enabled)

    def create_normal_enemy(
        enemy_type,
        x,
        y,
        mode="patrol",
        patrol_left=80,
        patrol_right=80,
        index=None,
        enemy_id=None,
    ):
        enemy_id = enemy_id or f"{enemy_type}_{index if index is not None else len(enemies) + 1}"
        if should_skip_dead_spawn(enemy_id):
            return None

        normal_enemy = Enemy(
            x,
            y,
            mode=mode,
            patrol_left=patrol_left,
            patrol_right=patrol_right,
            index=index,
            debug_ai=DEBUG_ENEMY_AI,
        )
        normal_enemy.enemy_id = enemy_id
        enemies.append(normal_enemy)
        print("[ENEMY CREATED]")
        print("Enemy type:", enemy_type)
        print("World position:", x, y)
        print("Enemy rect:", normal_enemy.rect)
        print("Total enemies now:", len(enemies))
        return normal_enemy

    def spawn_level_enemies():
        enemies.clear()
        current_level = level_manager.get_current_map()
        if current_map_is_shop_safe():
            print("[SHOP ROOM] enemies disabled")
            return

        level_name = current_level.name
        map_name = f"map{current_level.map_id}"
        enemy_spawns = list(current_level.enemy_spawns or [])
        if current_level.map_id in (0, 1):
            enemy_spawns = []

        print("[LEVEL ENEMY DEBUG]")
        print("Current level name:", level_name)
        print("Current map:", map_name)
        print("Enemy spawn data found:", enemy_spawns)
        print("Enemy spawn count:", len(enemy_spawns))
        print_room_clear_debug()

        for index, spawn in enumerate(enemy_spawns, start=1):
            enemy_type = "normal"
            if isinstance(spawn, dict):
                enemy_type = spawn.get("type", "normal")
                x = spawn.get("x", player.rect.centerx + 300)
                y = spawn.get("y", player.rect.y)
            else:
                x, y = spawn
            create_normal_enemy(enemy_type, int(x), int(y), index=index, enemy_id=f"{enemy_type}_{index}")

        if DEBUG_FORCE_TEST_ENEMY and len(enemies) == 0:
            test_x = player.rect.centerx + 300
            test_y = player.rect.y
            print("[TEMP DEBUG ENEMY SPAWN] No map spawn data; spawning one normal enemy near player.")
            create_normal_enemy("temporary_debug_normal", test_x, test_y)

        sync_primary_enemy()
        print("[LEVEL SETUP COMPLETE]")
        print("Final enemy count:", len(enemies))

    def clear_world_objects(reason="map transition reset"):
        coins.clear()
        projectiles.clear()
        projectile_hit_effects.clear()
        for normal_enemy in enemies:
            debug_remove_enemy(reason, normal_enemy)
        enemies.clear()
        for archer in archers:
            debug_remove_enemy(reason, archer)
        archers.clear()
        archer_arrows.clear()
        time_freeze_domains.clear()
        active_orbit_blades.clear()
        active_skill_effects.clear()
        soul_anchor_loops.clear()

    def spawn_map_archers():
        archers.clear()
        if current_map_is_shop_safe():
            print("[SHOP ROOM] archers disabled")
            return

        spawn_points = []

        if not ENEMY_SPAWN_PATH.exists():
            print("Missing enemy spawn file:", ENEMY_SPAWN_PATH)
        else:
            try:
                spawn_data = json.loads(ENEMY_SPAWN_PATH.read_text())
            except json.JSONDecodeError as error:
                print("Invalid enemy spawn file:", ENEMY_SPAWN_PATH)
                print(error)
                spawn_data = {}

            current_map_key = f"map{level_manager.get_current_map().map_id}"
            for spawn in spawn_data.get(current_map_key, []):
                if spawn.get("type") != "archer":
                    continue
                spawn_points.append(
                    {
                        "x": spawn.get("x", 0),
                        "y": spawn.get("y", 0),
                        "mode": spawn.get("mode", "patrol"),
                        "patrol_left": spawn.get("patrol_left", 120),
                        "patrol_right": spawn.get("patrol_right", 120),
                    }
                )

        current_map = level_manager.get_current_map()
        if current_map.map_id in (0, 1):
            spawn_points = list(ARCHER_SPAWNS)

        print("[ARCHER SPAWN SETUP]")
        print("Archer spawn count:", len(spawn_points))

        for index, spawn in enumerate(spawn_points, start=1):
            x = spawn["x"]
            y = spawn["y"]
            mode = spawn.get("mode", "patrol")
            patrol_left = spawn.get("patrol_left", 120)
            patrol_right = spawn.get("patrol_right", 120)
            enemy_id = f"archer_{index}"
            if should_skip_dead_spawn(enemy_id):
                continue
            archer = ArcherEnemy(
                x,
                y,
                mode=mode,
                patrol_left=patrol_left,
                patrol_right=patrol_right,
                index=index,
                debug_ai=DEBUG_ENEMY_AI,
            )
            archer.enemy_id = enemy_id
            archers.append(archer)
            print("[ARCHER CREATED]", index, x, y, archer.rect)
            print("[ARCHER CONFIG]", index, mode, x, y, archer.patrol_min_x, archer.patrol_max_x)

        print("Total normal enemies:", len(archers))

    def spawn_map_melees():
        current_map = level_manager.get_current_map()
        if current_map_is_shop_safe():
            print("[SHOP ROOM] melees disabled")
            return

        if current_map.map_id not in (0, 1):
            return

        print("[MELEE SPAWN SETUP]")
        print("Melee spawn count:", len(MELEE_SPAWNS))

        for index, spawn in enumerate(MELEE_SPAWNS, start=1):
            x = spawn["x"]
            y = spawn["y"]
            mode = spawn.get("mode", "patrol")
            melee = create_normal_enemy(
                "melee",
                x,
                y,
                mode=mode,
                patrol_left=spawn.get("patrol_left", 80),
                patrol_right=spawn.get("patrol_right", 80),
                index=index,
                enemy_id=f"melee_{index}",
            )
            if melee is None:
                continue
            print("[MELEE CREATED]", index, x, y, mode, melee.rect)

        print("Total enemies after melee spawn:", len(enemies))
        print("Total all enemies after melee spawn:", len(enemies) + len(archers))

    def spawn_map_mages():
        current_map = level_manager.get_current_map()
        if current_map_is_shop_safe():
            print("[SHOP ROOM] mages disabled")
            return

        if current_map.map_id not in (0, 1):
            return

        print("[MAGE SPAWN SETUP]")
        print("Mage spawn count:", len(MAGE_SPAWNS))

        for index, spawn in enumerate(MAGE_SPAWNS, start=1):
            x = spawn["x"]
            y = spawn["y"]
            mode = spawn.get("mode", "static")
            enemy_id = f"mage_{index}"
            if should_skip_dead_spawn(enemy_id):
                continue
            mage = MageEnemy(
                x,
                y,
                mode=mode,
                index=index,
                debug_ai=DEBUG_ENEMY_AI,
            )
            mage.enemy_id = enemy_id
            enemies.append(mage)
            print("[MAGE CREATED]", index, x, y, mode, mage.rect)

        print("Total enemies after mage spawn:", len(enemies))

    def enter_map(target_map_id):
        nonlocal boss_section_locked
        boss_section_locked = False
        camera.clear_bounds()
        changed = level_manager.change_map(target_map_id, player, enemy, camera)
        if not changed:
            return False

        clear_world_objects("map transition reset")
        spawn_level_enemies()
        spawn_map_archers()
        spawn_map_melees()
        spawn_map_mages()
        if current_map_is_shop_safe():
            enemies.clear()
            archers.clear()
            print("[SHOP ROOM] enemies disabled")
        shop.close()
        shop_rect = level_manager.get_shop_rect()
        if shop_rect is not None:
            shop.set_rect(shop_rect)
            shop.refresh_products()
        moon_shard.reset_to(player.rect, player.facing)
        pale_core_boss.active = False
        return True

    def restart_game(show_opening_dialogue=False):
        nonlocal game_state, boss_section_locked, boss_room_debug_printed
        nonlocal opening_dialogue_seen
        killed_enemy_ids.clear()
        boss_section_locked = False
        boss_room_debug_printed = False
        camera.clear_bounds()
        player.current_hp = player.max_hp
        player.hp = player.current_hp
        player.current_mana = player.max_mana
        player.mana = player.current_mana
        level_manager.reset_one_use_items()
        pale_core_boss.reset()
        player.is_dead = False
        player.invincible_timer = 0
        player.vel_x = 0
        player.vel_y = 0
        enter_map(0)
        dialogue.active = False
        if show_opening_dialogue:
            dialogue.reset_for_new_run()
            if not opening_dialogue_seen:
                dialogue.start("opening")
                opening_dialogue_seen = True
        game_state = "playing"

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        e_pressed = False
        e_released = False
        k_pressed = False
        current_map = level_manager.get_current_map()
        shop_active = level_manager.get_shop_rect() is not None
        music_manager.update_for_game(game_state, current_map.map_id, LEVEL5_BOSS_MAP_ID)

        if not shop_active and shop.is_open:
            shop.close()

        nearby_door = level_manager.check_doors(player)

        for event in pygame.event.get():
            if game_state == "menu":
                if event.type == pygame.QUIT:
                    running = False
                else:
                    main_menu.handle_event(event)
                continue

            if game_state == "origin_story":
                if event.type == pygame.QUIT:
                    running = False
                else:
                    origin_story.handle_event(event)
                continue

            if game_state == "paused":
                if event.type == pygame.QUIT:
                    running = False
                else:
                    pause_menu.handle_event(event)
                continue

            if game_state == "playing" and dialogue.active:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state = "paused"
                    pause_menu.reset_flags()
                else:
                    dialogue.handle_event(event)
                continue

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

                if event.key == pygame.K_F3:
                    dev_teleport.toggle()
                    continue

                if event.key == pygame.K_F4 and not dev_teleport.visible:
                    show_player_debug_overlay = not show_player_debug_overlay
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

                if event.key == pygame.K_ESCAPE:
                    game_state = "paused"
                    pause_menu.reset_flags()
                    continue

                if event.key == pygame.K_F1:
                    player.toggle_unlimited_hp()

                if event.key == pygame.K_F2:
                    player.toggle_unlimited_mana()

                if event.key == pygame.K_e:
                    if level_manager.use_moon_altar(player):
                        pass
                    elif shop_active and shop.can_interact(player):
                        if not shop.buy_nearby_product(player):
                            shop.toggle()
                    elif nearby_door is not None:
                        target_map = nearby_door["target_map"]
                        if isinstance(target_map, int):
                            if current_map_is_shop_safe():
                                enter_boss_final_section()
                            else:
                                enter_map(target_map)
                        elif target_map == "victory":
                            game_state = "victory"
                    else:
                        e_pressed = True

                if event.key == pygame.K_k:
                    k_pressed = True

                if shop.is_open:
                    shop.handle_key(event, player)

        if game_state == "menu":
            if main_menu.should_quit:
                running = False
                continue

            if main_menu.should_start_game:
                main_menu.should_start_game = False
                origin_story.open()
                game_state = "origin_story"
                continue

            main_menu.update(dt)
            main_menu.draw(screen)

            if PIXELATE_GAME:
                small_surface = pygame.transform.scale(screen, (PIXEL_WIDTH, PIXEL_HEIGHT))
                pixel_surface = pygame.transform.scale(small_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
                window.blit(pixel_surface, (0, 0))
            else:
                window.blit(screen, (0, 0))

            pygame.display.flip()
            continue

        if game_state == "origin_story":
            origin_story.update(dt)

            if origin_story.should_start_game:
                origin_story.should_start_game = False
                restart_game(show_opening_dialogue=True)
                continue

            origin_story.draw(screen)

            if PIXELATE_GAME:
                small_surface = pygame.transform.scale(screen, (PIXEL_WIDTH, PIXEL_HEIGHT))
                pixel_surface = pygame.transform.scale(small_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
                window.blit(pixel_surface, (0, 0))
            else:
                window.blit(screen, (0, 0))

            pygame.display.flip()
            continue

        if game_state == "paused":
            pause_menu.update(dt)

            if pause_menu.should_quit:
                running = False
                continue

            if pause_menu.should_restart:
                pause_menu.reset_flags()
                restart_game()

            elif pause_menu.should_main_menu:
                pause_menu.reset_flags()
                main_menu.should_start_game = False
                main_menu.should_quit = False
                restart_game()
                game_state = "menu"
                continue

            elif pause_menu.should_resume:
                pause_menu.reset_flags()
                game_state = "playing"

        current_map = level_manager.get_current_map()
        keys = pygame.key.get_pressed()
        platforms = level_manager.get_platforms()
        fulcrums = level_manager.get_fulcrums()

        if game_state == "playing":
            dialogue.check_triggers(player, current_map, enemies, archers, pale_core_boss)
        dialogue.update(dt)

        if game_state == "playing" and not shop.is_open and not dialogue.active:
            enemy_debug_frame += 1
            if enemy_debug_frame % 120 == 0:
                print("[ENEMY RUNTIME COUNT]", len(enemies) + len(archers))
                print("[ENEMY UPDATE COUNT]", len(enemies) + len(archers))
            current_map = level_manager.get_current_map()
            pale_core_boss.update_activation(current_map.map_id, player)
            if current_map.map_id == LEVEL5_BOSS_MAP_ID and pale_core_boss.active and not boss_section_locked:
                boss_section_locked = True
                camera.set_bounds(BOSS_SECTION_BOUNDS)

            for domain in time_freeze_domains:
                domain.update(dt)
            time_freeze_domains = [domain for domain in time_freeze_domains if domain.alive]

            for normal_enemy in enemies:
                normal_enemy.update(dt, player, platforms)
            for archer in archers:
                archer.update(dt, player, archer_arrows, platforms)
            pale_core_boss.update(dt, player)

        if game_state == "playing" and not player.is_dead and not shop.is_open and not dialogue.active:
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
                        if current_map_is_shop_safe():
                            enter_boss_final_section()
                        else:
                            enter_map(target_map)
                    elif target_map == "victory":
                        game_state = "victory"
                    current_map = level_manager.get_current_map()
                    map_changed = True

            if not map_changed and level_manager.is_player_in_deadly_void(player):
                kill_player_instantly(player)

            clamp_player_to_map(player, current_map)
            clamp_player_to_boss_section()

            if k_pressed and not map_changed:
                activate_current_skill(
                    player,
                    enemies,
                    archers,
                    pale_core_boss,
                    time_freeze_domains,
                    active_orbit_blades,
                    active_skill_effects,
                    soul_anchor_loops,
                )

            nearby_fulcrum = get_nearby_fulcrum(player, fulcrums)

            if e_pressed and nearby_fulcrum is not None and not map_changed:
                if current_map.map_id in (2, 8):
                    player.start_swing(nearby_fulcrum["anchor"])
                else:
                    player.start_auto_grapple(nearby_fulcrum["anchor"], nearby_fulcrum["target"])

            if e_released and player.is_swinging:
                player.release_swing()

            if player.should_spawn_projectile and not map_changed:
                spawn_projectile(player, projectiles)
                player.should_spawn_projectile = False

            if not map_changed:
                handle_player_attack_enemies(player, enemies)
                handle_player_attack_archers(player, archers)
                handle_player_attack_boss(player, pale_core_boss)

            update_projectiles(projectiles, dt, platforms, enemies, projectile_hit_effects)
            update_projectile_archer_hits(projectiles, archers, projectile_hit_effects)
            update_projectile_boss_hits(projectiles, pale_core_boss, projectile_hit_effects)
            update_archer_arrows(archer_arrows, dt, player)
            update_orbit_blades(active_orbit_blades, dt, player, enemies, archers, active_skill_effects)
            update_orbit_blade_boss_hits(active_orbit_blades, pale_core_boss)
            active_orbit_blades = [blade for blade in active_orbit_blades if blade.alive]
            for normal_enemy in enemies:
                handle_enemy_attack(player, normal_enemy)
                handle_enemy_coin_drop(normal_enemy, coins)
                if not normal_enemy.alive:
                    enemy_was_killed(normal_enemy)
                    debug_remove_enemy("dead", normal_enemy)
            for archer in archers:
                handle_enemy_coin_drop(archer, coins)
                if not archer.alive:
                    enemy_was_killed(archer)
                    debug_remove_enemy("dead", archer)
            enemies = [normal_enemy for normal_enemy in enemies if normal_enemy.alive]
            archers = [archer for archer in archers if archer.alive]
            update_coins(coins, dt, platforms, player)
            coins = [coin for coin in coins if not coin.collected]
            projectiles = [projectile for projectile in projectiles if projectile.alive]
            archer_arrows = [arrow for arrow in archer_arrows if arrow.alive]
            for hit_effect in projectile_hit_effects:
                hit_effect.update(dt)
            projectile_hit_effects = [effect for effect in projectile_hit_effects if effect.alive]

            if pale_core_boss.defeated:
                game_state = "victory"

        if player.is_dead and game_state == "playing":
            game_state = "game_over"

        if game_state != "paused":
            camera.update(player.rect)

        if game_state == "playing" and not shop.is_open and not dialogue.active:
            for effect in active_skill_effects:
                effect.update(dt)
            active_skill_effects = [effect for effect in active_skill_effects if effect.alive]
            for anchor_loop in soul_anchor_loops:
                anchor_loop.update(dt)
            soul_anchor_loops = [
                anchor_loop for anchor_loop in soul_anchor_loops
                if anchor_loop.alive and player.soul_anchor_active
            ]

        # Trails on the opposite side of the player's facing direction.
        # Held still while paused with the rest of the gameplay scene.
        if game_state != "paused":
            moon_shard.update(dt, player.rect, player.facing)

        
        # Dev teleport hover highlight
        dev_teleport.update_hover(pygame.mouse.get_pos())

        #screen.fill((18, 20, 30))# Background is drawn inside level_manager.draw_current_map()

        current_map = level_manager.get_current_map()
        if pale_core_boss.should_draw_background(current_map.map_id, player):
            level_manager.background_draw_callback = pale_core_boss.draw_background
        else:
            level_manager.background_draw_callback = None
        level_manager.draw_current_map(screen, camera)
        draw_start_tutorial(screen, camera, current_map)

        current_map = level_manager.get_current_map()
        shop_active = level_manager.get_shop_rect() is not None

        if shop_active:
            shop.draw_shop_area(screen, camera)

        # Tiled grapple fulcrums: visible anchor points.
        if current_map.map_id in (2, 8):
            for fulcrum in fulcrums:
                anchor_pos = camera.apply_pos(fulcrum["anchor"])
                pygame.draw.circle(screen, (42, 28, 70), anchor_pos, 30)
                pygame.draw.circle(screen, (110, 65, 170), anchor_pos, 22)
                pygame.draw.circle(screen, (170, 95, 235), anchor_pos, 15)
                pygame.draw.circle(screen, (235, 220, 255), anchor_pos, 6)
                pygame.draw.circle(screen, (205, 160, 255), anchor_pos, 30, 2)

        for domain in time_freeze_domains:
            domain.draw(screen, camera)

        for anchor_loop in soul_anchor_loops:
            anchor_loop.draw(screen, camera)

        for coin in coins:
            coin.draw(screen, camera)

        pale_core_boss.draw_effects(screen, camera)
        if enemy_debug_frame > 0 and enemy_debug_frame % 120 == 0:
            for normal_enemy in enemies:
                screen_x = normal_enemy.rect.x - camera.x
                screen_y = normal_enemy.rect.y - camera.y
                print("[ENEMY DRAW POS]", normal_enemy.rect, "screen:", screen_x, screen_y)
                print("Player world position:", player.rect.center)
                print("Camera offset:", camera.x, camera.y)
                print("Enemy world position:", normal_enemy.rect.center)
            for archer in archers:
                screen_x = archer.rect.x - camera.x
                screen_y = archer.rect.y - camera.y
                print("[ENEMY DRAW POS]", archer.rect, "screen:", screen_x, screen_y)
                print("Player world position:", player.rect.center)
                print("Camera offset:", camera.x, camera.y)
                print("Enemy world position:", archer.rect.center)
        for normal_enemy in enemies:
            normal_enemy.draw(screen, camera)
        for archer in archers:
            archer.draw(screen, camera)
        player.draw(screen, camera)
        # Moon shard renders on top so its glow doesn't get hidden behind the player.
        moon_shard.draw(screen, camera)

        for projectile in projectiles:
            projectile.draw(screen, camera)

        for arrow in archer_arrows:
            arrow.draw(screen, camera)

        for hit_effect in projectile_hit_effects:
            hit_effect.draw(screen, camera)

        for blade in active_orbit_blades:
            blade.draw(screen, camera)

        for effect in active_skill_effects:
            effect.draw(screen, camera)

        weapon = get_weapon(player.current_weapon_id)
        hide_custom_weapon_attack_visuals = (
            player.current_weapon_id in ("light_weapon", "heavy_weapon") and
            player.attack_animation_playing
        )
        if (
            player.is_attacking and
            weapon["weapon_type"] != "projectile" and
            DEBUG_DRAW_HITBOXES and
            not hide_custom_weapon_attack_visuals
        ):
            pygame.draw.rect(screen, (70, 140, 255), camera.apply_rect(player.get_attack_hitbox()), 2)

        nearby_fulcrum = get_nearby_fulcrum(player, fulcrums)
        if nearby_fulcrum is not None and not player.is_auto_grappling:
            draw_interaction_text(screen, player, camera)

        if level_manager.can_use_moon_altar(player) and not shop.is_open:
            draw_moon_altar_interaction_text(screen, level_manager.get_moon_altar_rect(), camera)

        if shop_active and shop.can_interact(player) and not shop.is_open:
            draw_shop_interaction_text(screen, shop, player, camera)

        nearby_door = level_manager.check_doors(player)
        if nearby_door is not None:
            draw_door_interaction_text(screen, nearby_door, camera)

        draw_player_ui(screen, player, level_manager.get_current_map().name)
        pale_core_boss.draw_ui(screen)

        if DEBUG_MODE:
            draw_weapon_boxes(screen, player)
            draw_skill_boxes(screen, player)

        if shop.is_open:
            shop.draw_shop_menu(screen, player)

        if game_state == "game_over":
            draw_popup(screen, "GAME OVER", "You were defeated.")
        elif game_state == "victory":
            draw_popup(screen, "PALE CORE DEFEATED", "The Lunar Core has gone silent.")
        elif game_state == "paused":
            pause_menu.draw(screen)
        if PIXELATE_GAME:
            small_surface = pygame.transform.scale(screen, (PIXEL_WIDTH, PIXEL_HEIGHT))
            pixel_surface = pygame.transform.scale(small_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            window.blit(pixel_surface, (0, 0))
            dialogue.draw(window)
            if DEBUG_MODE or show_player_debug_overlay:
                draw_player_debug_position(window, player)
            # Draw dev tools after pixel scaling so F3 text stays readable.
            dev_teleport.draw(window)
        else:
            dialogue.draw(screen)
            # Dev teleport overlay is drawn last so it sits on top of everything.
            dev_teleport.draw(screen)
            if DEBUG_MODE or show_player_debug_overlay:
                draw_player_debug_position(screen, player)
            window.blit(screen, (0, 0))

        pygame.display.flip()

    pygame.quit()


def spawn_projectile(player, projectiles):
    weapon = get_weapon(player.current_weapon_id)

    if weapon["weapon_type"] != "projectile":
        return

    damage, is_critical = calculate_damage(player, weapon["damage"])
    direction = player.facing
    spawn_x = player.rect.centerx + direction * SHOOTER_BULLET_MUZZLE_OFFSET_X
    spawn_y = player.rect.centery + SHOOTER_BULLET_MUZZLE_OFFSET_Y

    print("[SHOOTER FIRE]")
    print("current weapon:", player.current_weapon_id)
    print("bullet spawn:", spawn_x, spawn_y)
    print("Player center:", player.rect.center)
    print("Facing:", direction)

    projectile = Projectile(
        spawn_x,
        spawn_y,
        direction,
        damage,
        is_critical,
        SHOOTER_BULLET_SPEED,
        SHOOTER_BULLET_MAX_DISTANCE,
        "weapon",
    )
    print("bullet frames:", len(projectile.frames))
    projectiles.append(projectile)


def handle_player_attack(player, enemy):
    weapon = get_weapon(player.current_weapon_id)
    attack_hitbox = None
    melee_hitbox_types = ("melee", "shield", "grapple")

    if player.is_auto_grappling:
        return

    if not player.is_attacking:
        return

    if weapon["weapon_type"] == "projectile":
        return

    if weapon["weapon_type"] in melee_hitbox_types:
        attack_hitbox = player.get_attack_hitbox()
    
    if attack_hitbox is not None:
        print(f"Attack hitbox: {attack_hitbox}")
    print(f"Enemy rect: {enemy.rect}")
    if attack_hitbox is not None:
        print(f"Collision: {attack_hitbox.colliderect(enemy.rect)}")
    print(f"player.attack_has_hit: {player.attack_has_hit}")

    if attack_hitbox is not None and enemy.alive:
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


def handle_player_attack_enemies(player, enemies):
    weapon = get_weapon(player.current_weapon_id)
    melee_hitbox_types = ("melee", "shield", "grapple")

    if player.is_auto_grappling or not player.is_attacking or player.attack_has_hit:
        return

    if weapon["weapon_type"] not in melee_hitbox_types:
        return

    attack_hitbox = player.get_attack_hitbox()
    print(f"Attack hitbox: {attack_hitbox}")

    for normal_enemy in enemies:
        print(f"Enemy rect: {normal_enemy.rect}")
        print(f"Collision: {attack_hitbox.colliderect(normal_enemy.rect)}")
        if not normal_enemy.alive:
            continue
        if not attack_hitbox.colliderect(normal_enemy.rect):
            continue

        damage, is_critical = calculate_damage(player, weapon["damage"])
        normal_enemy.take_damage(damage)
        player.attack_has_hit = True

        if weapon["weapon_type"] == "grapple":
            normal_enemy.stun(weapon["stun_time"])

        if is_critical:
            print(f"Hit enemy for {damage} damage CRITICAL")
        else:
            print(f"Hit enemy for {damage} damage")
        return


def handle_player_attack_archers(player, archers):
    weapon = get_weapon(player.current_weapon_id)
    melee_hitbox_types = ("melee", "shield", "grapple")

    if player.is_auto_grappling or not player.is_attacking or player.attack_has_hit:
        return

    if weapon["weapon_type"] not in melee_hitbox_types:
        return

    attack_hitbox = player.get_attack_hitbox()
    for archer in archers:
        if not archer.alive:
            continue
        if not attack_hitbox.colliderect(archer.rect):
            continue

        damage, is_critical = calculate_damage(player, weapon["damage"])
        archer.take_damage(damage)
        player.attack_has_hit = True

        if weapon["weapon_type"] == "grapple":
            archer.stun(weapon["stun_time"])

        if is_critical:
            print(f"Hit archer for {damage} damage CRITICAL")
        else:
            print(f"Hit archer for {damage} damage")
        return


def handle_player_attack_boss(player, boss):
    if not boss.active or boss.defeated:
        return

    if player.is_auto_grappling or not player.is_attacking or player.attack_has_hit:
        return

    weapon = get_weapon(player.current_weapon_id)
    if weapon["weapon_type"] not in ("melee", "shield", "grapple"):
        return

    attack_hitbox = player.get_attack_hitbox()
    damage, is_critical = calculate_damage(player, weapon["damage"])
    hit_hand = boss.take_hand_damage_at_rect(attack_hitbox, damage)
    if hit_hand is not None:
        player.attack_has_hit = True
        return

    if not attack_hitbox.colliderect(boss.weakpoint_rect):
        return

    if boss.take_damage(damage):
        player.attack_has_hit = True
        if is_critical:
            print(f"Hit Pale Core weakpoint for {damage} damage CRITICAL")
        else:
            print(f"Hit Pale Core weakpoint for {damage} damage")


def update_projectiles(projectiles, dt, platforms, enemies, projectile_hit_effects):
    for projectile in projectiles:
        projectile.update(dt, platforms)

        for normal_enemy in enemies:
            if normal_enemy.alive and projectile.alive and projectile.rect.colliderect(normal_enemy.rect):
                normal_enemy.take_damage(projectile.damage)
                projectile_hit_effects.append(ProjectileHitEffect(projectile.rect.center))
                projectile.alive = False
                break


def update_projectile_archer_hits(projectiles, archers, projectile_hit_effects):
    for projectile in projectiles:
        if not projectile.alive:
            continue

        for archer in archers:
            if not archer.alive:
                continue
            if projectile.rect.colliderect(archer.rect):
                archer.take_damage(projectile.damage)
                projectile_hit_effects.append(ProjectileHitEffect(projectile.rect.center))
                projectile.alive = False
                print(f"Projectile hit archer for {projectile.damage} damage")
                break


def update_projectile_boss_hits(projectiles, boss, projectile_hit_effects):
    if not boss.active or boss.defeated:
        return

    for projectile in projectiles:
        if not projectile.alive:
            continue
        hit_hand = boss.take_hand_damage_at_rect(projectile.rect, projectile.damage)
        if hit_hand is not None:
            projectile_hit_effects.append(ProjectileHitEffect(projectile.rect.center))
            projectile.alive = False
            print(f"Projectile hit Pale Core {hit_hand.name} hand for {projectile.damage} damage")
            continue
        if projectile.rect.colliderect(boss.weakpoint_rect) and boss.take_damage(projectile.damage):
            projectile_hit_effects.append(ProjectileHitEffect(projectile.rect.center))
            projectile.alive = False
            print(f"Projectile hit Pale Core weakpoint for {projectile.damage} damage")


def update_orbit_blades(active_orbit_blades, dt, player, enemies, archers, active_skill_effects):
    targets = [enemy for enemy in enemies + archers if getattr(enemy, "alive", False)]
    for blade in active_orbit_blades:
        blade.update(dt, player, targets)
        if getattr(blade, "hit_effect", None) is not None:
            active_skill_effects.append(blade.hit_effect)
            blade.hit_effect = None


def update_orbit_blade_boss_hits(active_orbit_blades, boss):
    if not boss.active or boss.defeated:
        return

    for blade in active_orbit_blades:
        if not blade.alive or getattr(blade, "has_hit", False):
            continue
        hit_hand = boss.take_hand_damage_at_rect(blade.rect, blade.damage)
        if hit_hand is not None:
            blade.has_hit = True
            blade.alive = False
            blade.state = "dead"
            print(f"Orbit blade hit Pale Core {hit_hand.name} hand for {blade.damage} damage")
            continue
        if blade.rect.colliderect(boss.weakpoint_rect) and boss.take_damage(blade.damage):
            blade.has_hit = True
            blade.alive = False
            blade.state = "dead"
            print(f"Orbit blade hit Pale Core weakpoint for {blade.damage} damage")


def update_archer_arrows(archer_arrows, dt, player):
    for arrow in archer_arrows:
        arrow.update(dt, player)


def get_nearest_alive_enemy(origin, enemies):
    nearest_enemy = None
    nearest_distance = None
    for normal_enemy in enemies:
        if not normal_enemy.alive:
            continue
        distance = math.hypot(
            normal_enemy.rect.centerx - origin[0],
            normal_enemy.rect.centery - origin[1],
        )
        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = normal_enemy
    return nearest_enemy


def activate_current_skill(
    player,
    enemies,
    archers,
    boss,
    time_freeze_domains,
    active_orbit_blades,
    active_skill_effects,
    soul_anchor_loops,
):
    skill = get_skill(player.current_skill_id)
    print("[SKILL USE]")
    print("current_skill_id:", player.current_skill_id)
    print("mana:", player.current_mana)
    print("cooldown:", player.skill_cooldown_timer)
    print("skill frames loaded:", get_skill_loaded_frame_count(skill["skill_type"]))

    if skill["skill_type"] == "soul_anchor" and player.soul_anchor_active:
        activate_soul_anchor(player, skill, active_skill_effects, soul_anchor_loops)
        return

    if not player.can_use_skill(skill):
        print("Cannot use skill")
        return

    if skill["skill_type"] == "time_freeze":
        player.spend_skill_cost(skill)
        time_freeze_domains.append(TimeFreezeDomain(player.rect.midbottom))
        stunned_count = apply_time_freeze_to_enemies(player.rect.center, enemies + archers)
        print("[TIME FREEZE ACTIVATE]")
        print("Freeze radius:", TIME_FREEZE_RADIUS)
        print("Enemies stunned:", stunned_count)

    elif skill["skill_type"] == "orbit_blades":
        player.spend_skill_cost(skill)
        for index in range(ORBIT_BLADE_COUNT):
            active_orbit_blades.append(OrbitBlade(player, index, ORBIT_BLADE_COUNT))
        print("Orbit Blades blade count:", ORBIT_BLADE_COUNT)
        print("Orbit Blades")

    elif skill["skill_type"] == "energy_beam":
        player.spend_skill_cost(skill)
        beam_rect = get_energy_beam_rect(player)
        enemies_hit = 0
        for normal_enemy in enemies:
            if normal_enemy.alive and beam_rect.colliderect(normal_enemy.rect):
                normal_enemy.take_damage(ENERGY_BEAM_DAMAGE)
                enemies_hit += 1
                print("Energy Beam hit enemy")
        for archer in archers:
            if archer.alive and beam_rect.colliderect(archer.rect):
                archer.take_damage(ENERGY_BEAM_DAMAGE)
                enemies_hit += 1
                print("Energy Beam hit archer")
        hit_hand = boss.take_hand_damage_at_rect(beam_rect, ENERGY_BEAM_DAMAGE) if boss.active and not boss.defeated else None
        if hit_hand is not None:
            enemies_hit += 1
            print(f"Energy Beam hit Pale Core {hit_hand.name} hand")
        if boss.active and not boss.defeated and beam_rect.colliderect(boss.weakpoint_rect):
            if boss.take_damage(ENERGY_BEAM_DAMAGE):
                enemies_hit += 1
                print("Energy Beam hit Pale Core weakpoint")
        active_skill_effects.append(EnergyBeamEffect(player, get_energy_beam_rect, get_energy_beam_origin, player.facing))
        print("Energy Beam beam rect:", beam_rect)
        print("Energy Beam enemies hit count:", enemies_hit)

    elif skill["skill_type"] == "soul_anchor":
        activate_soul_anchor(player, skill, active_skill_effects, soul_anchor_loops)


def get_skill_loaded_frame_count(skill_type):
    asset_keys = {
        "time_freeze": ["time_freeze_ready", "time_freeze_action", "time_freeze_loop"],
        "orbit_blades": ["orbit_blades_ready", "orbit_blade_projectile", "orbit_blade_hit"],
        "energy_beam": ["energy_beam_ready", "energy_beam_attack"],
        "soul_anchor": ["soul_anchor_ready", "soul_anchor_place", "soul_anchor_loop", "soul_anchor_return"],
    }
    return {asset_key: len(get_skill_frames(asset_key)) for asset_key in asset_keys.get(skill_type, [])}


def apply_time_freeze_to_enemies(center, targets):
    stunned_count = 0
    for enemy in targets:
        if not getattr(enemy, "alive", False):
            continue
        distance = math.hypot(enemy.rect.centerx - center[0], enemy.rect.centery - center[1])
        if distance > TIME_FREEZE_RADIUS:
            continue

        if hasattr(enemy, "freeze"):
            enemy.freeze(TIME_FREEZE_STUN_DURATION)
        elif hasattr(enemy, "stun"):
            enemy.stun(TIME_FREEZE_STUN_DURATION)
        print("[ENEMY STUNNED]", getattr(enemy, "enemy_id", None), TIME_FREEZE_STUN_DURATION)
        stunned_count += 1
    return stunned_count


def get_energy_beam_rect(player):
    origin_x, origin_y = get_energy_beam_origin(player)
    y = origin_y - ENERGY_BEAM_HEIGHT // 2

    if player.facing == 1:
        x = origin_x
    else:
        x = origin_x - ENERGY_BEAM_RANGE

    return pygame.Rect(x, y, ENERGY_BEAM_RANGE, ENERGY_BEAM_HEIGHT)


def get_energy_beam_origin(player):
    offset_x = 35
    offset_y = -10
    return (
        player.rect.centerx + offset_x * player.facing,
        player.rect.centery + offset_y,
    )


def activate_soul_anchor(player, skill, active_skill_effects, soul_anchor_loops):
    if player.is_dead or player.is_auto_grappling:
        return

    if player.soul_anchor_active:
        if not player.debug_unlimited_mana and player.current_mana < SOUL_ANCHOR_RETURN_COST:
            print("Not enough mana to return")
            return

        if not player.debug_unlimited_mana:
            player.current_mana -= SOUL_ANCHOR_RETURN_COST

        player.rect.midbottom = player.soul_anchor_pos
        player.vel_x = 0
        player.vel_y = 0
        return_position = player.rect.midbottom
        player.soul_anchor_active = False
        player.soul_anchor_pos = None
        player.soul_anchor_timer = 0
        soul_anchor_loops.clear()
        active_skill_effects.append(
            SkillSpriteEffect(
                "soul_anchor_return",
                return_position,
                duration=0.4,
                anchor="midbottom",
            )
        )
        print("Soul Anchor return position:", return_position)
        print("Soul Anchor anchor timer:", player.soul_anchor_timer)
        print("Returned to Soul Anchor")
        return

    player.spend_skill_cost(skill)
    player.soul_anchor_active = True
    player.soul_anchor_pos = player.rect.midbottom
    player.soul_anchor_timer = SOUL_ANCHOR_DURATION
    soul_anchor_loops.clear()
    soul_anchor_loops.append(SoulAnchorLoop(player.soul_anchor_pos, SOUL_ANCHOR_DURATION))
    active_skill_effects.append(
        SkillSpriteEffect(
            "soul_anchor_place",
            player.soul_anchor_pos,
            duration=0.4,
            anchor="midbottom",
        )
    )
    print("Soul Anchor place position:", player.soul_anchor_pos)
    print("Soul Anchor anchor timer:", player.soul_anchor_timer)
    print("Soul Anchor placed")


def handle_enemy_attack(player, enemy):
    if not enemy.is_attacking or not enemy.alive:
        return

    if player.is_auto_grappling:
        return

    if hasattr(enemy, "attack_is_active") and not enemy.attack_is_active:
        return

    enemy_attack_hitbox = enemy.get_attack_hitbox()

    if not enemy_attack_hitbox.colliderect(player.rect) or enemy.attack_has_hit:
        return

    weapon = get_weapon(player.current_weapon_id)

    if weapon["id"] == "shield_weapon" and player.is_blocking:
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
        player.take_damage(getattr(enemy, "damage", ENEMY_DAMAGE))
        enemy.attack_has_hit = True
        if hasattr(enemy, "has_hit_player_this_attack"):
            enemy.has_hit_player_this_attack = True
            print("[MELEE HIT PLAYER]")
            print("damage:", getattr(enemy, "damage", ENEMY_DAMAGE))
            print("hitbox:", enemy_attack_hitbox)


def handle_enemy_coin_drop(enemy, coins):
    if enemy.alive or enemy.dropped_coins:
        return

    coins.append(Coin(enemy.rect.centerx, enemy.rect.centery, COIN_VALUE))
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


def draw_player_debug_position(screen, player):
    font = pygame.font.Font(None, 24)
    lines = [
        f"Player X: {player.rect.centerx}",
        f"Player Y: {player.rect.bottom}",
    ]
    rendered_lines = [font.render(line, True, (255, 245, 150)) for line in lines]
    padding = 10
    line_gap = 4
    width = max(line.get_width() for line in rendered_lines) + padding * 2
    height = sum(line.get_height() for line in rendered_lines) + line_gap + padding * 2
    panel_rect = pygame.Rect(screen.get_width() - width - 18, 18, width, height)

    pygame.draw.rect(screen, (18, 20, 30), panel_rect)
    pygame.draw.rect(screen, (100, 210, 255), panel_rect, 2)

    y = panel_rect.y + padding
    for line in rendered_lines:
        screen.blit(line, (panel_rect.x + padding, y))
        y += line.get_height() + line_gap


def draw_moon_altar_interaction_text(screen, altar_rect, camera=None):
    font = pygame.font.Font(None, 26)
    text = font.render("Press E to restore at Moon Altar", True, (190, 235, 255))
    pos = (altar_rect.centerx, altar_rect.top - 14)
    if camera:
        pos = camera.apply_pos(pos)
    screen.blit(text, text.get_rect(center=pos))


def draw_shop_interaction_text(screen, shop, player, camera=None):
    font = pygame.font.Font(None, 30)
    text = font.render(shop.get_nearby_prompt(player), True, (255, 245, 180))
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
