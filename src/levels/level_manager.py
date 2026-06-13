import csv
import math
from pathlib import Path
import pygame

from settings import (
    DOOR_HEIGHT,
    DOOR_WIDTH,
    FULCRUM_RADIUS,
    MAP_0_HEIGHT,
    MAP_0_WIDTH,
    MAP_1_HEIGHT,
    MAP_1_WIDTH,
    MAP_2_HEIGHT,
    MAP_2_WIDTH,
    MAP_4_HEIGHT,
    MAP_4_WIDTH,
    MAP_5_HEIGHT,
    MAP_5_WIDTH,
    MAP_6_HEIGHT,
    MAP_6_WIDTH,
    MAP_7_HEIGHT,
    MAP_7_WIDTH,
    MAP_8_HEIGHT,
    MAP_8_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    DEBUG_DRAW_HITBOXES,
)
from src.levels.game_map import GameMap
from src.levels.tiled_map_loader import load_tiled_map

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def draw_pixel_stone_face(screen, rect, top_color, face_color, dark_color, glow_color):
    """
    Draw a chunky pixel-stone surface.
    Used by both ground floors and upper ledges.
    """

    BLOCK = 8

    # Main face
    pygame.draw.rect(screen, face_color, rect)

    # Top cap
    pygame.draw.rect(screen, top_color, (rect.x, rect.y, rect.width, 8))
    pygame.draw.rect(screen, (235, 238, 246), (rect.x, rect.y, rect.width, 2))

    # Blocky front-face details (UPDATED: tighter spacing for more texture)
    for x in range(rect.x + 10, rect.right - 10, 16):
        pygame.draw.rect(screen, dark_color, (x, rect.y + 16, 8, 3))

    for x in range(rect.x + 22, rect.right - 14, 40):
        pygame.draw.rect(screen, dark_color, (x, rect.y + 28, 6, 3))

    # Small cracks
    for x in range(rect.x + 30, rect.right - 20, 90):
        pygame.draw.line(screen, (24, 26, 36), (x, rect.y + 18), (x + 6, rect.y + 24), 2)
        pygame.draw.line(screen, (24, 26, 36), (x + 6, rect.y + 24), (x + 3, rect.y + 31), 2)

    # Small lunar glow accents
    for x in range(rect.x + 50, rect.right - 20, 140):
        pygame.draw.rect(screen, glow_color, (x, rect.y + 12, 14, 3))

def draw_ground_platform(screen, rect):
    """
    Thick terrain floor, not a thin floating platform.
    This is for the main street / ground route.
    """

    top_color = (170, 176, 196)
    face_color = (78, 82, 104)
    dark_color = (42, 46, 60)
    glow_color = (80, 195, 245)
    bottom_shadow = (28, 30, 42)

    # Main terrain block
    draw_pixel_stone_face(screen, rect, top_color, face_color, dark_color, glow_color)

    # Bottom heavy shadow strip
    pygame.draw.rect(screen, bottom_shadow, (rect.x, rect.bottom - 8, rect.width, 8))

    # Blocky underside bricks
    for x in range(rect.x + 14, rect.right - 14, 44):
        pygame.draw.rect(screen, dark_color, (x, rect.bottom - 8, 12, 8))

def draw_ledge_platform(screen, rect):
    """
    Chunky ruin ledge, closer to Dead Cells style.
    No thin support legs, no long vertical lines.
    """

    top_color = (182, 186, 204)
    face_color = (90, 94, 112)
    dark_color = (50, 54, 70)
    glow_color = (85, 200, 250)
    underside = (34, 36, 48)

    # Slightly thicker visible mass than a flat bar (UPDATED to 48)
    face_rect = pygame.Rect(rect.x, rect.y, rect.width, max(rect.height, 48))
    draw_pixel_stone_face(screen, face_rect, top_color, face_color, dark_color, glow_color)

    # Dark underside
    pygame.draw.rect(screen, underside, (face_rect.x, face_rect.bottom - 6, face_rect.width, 6))

    # Jagged ruin teeth underneath (short chunky blocks, not thin lines)
    tooth_y = face_rect.bottom - 1
    tooth_pattern = [8, 14, 10, 16, 12]

    i = 0
    for x in range(face_rect.x + 12, face_rect.right - 18, 24):
        h = tooth_pattern[i % len(tooth_pattern)]
        pygame.draw.rect(screen, dark_color, (x, tooth_y, 10, h))
        i += 1

def draw_pillar_platform(screen, rect):
    """Vertical stone pillar / wall — used for tall narrow rects."""
    main = (75, 82, 100)
    edge = (45, 50, 65)
    cap = (170, 176, 196)
    detail = (35, 38, 55)
    glow = (85, 200, 250)
    shadow = (22, 25, 35)

    pygame.draw.rect(screen, main, rect)
    pygame.draw.rect(screen, cap, (rect.x, rect.y, rect.width, 6))
    pygame.draw.rect(screen, shadow, (rect.x, rect.bottom - 6, rect.width, 6))
    pygame.draw.rect(screen, edge, (rect.x, rect.y, 4, rect.height))
    pygame.draw.rect(screen, edge, (rect.right - 4, rect.y, 4, rect.height))
    for y in range(rect.y + 25, rect.bottom - 12, 32):
        pygame.draw.rect(screen, detail, (rect.x + 2, y, rect.width - 4, 2))
    pygame.draw.rect(screen, glow, (rect.x + 4, rect.y + 8, rect.width - 8, 2))


def draw_moon_platform(screen, rect):
    """
    Picks the right visual for a platform based on its shape:
    - Tall narrow rect = stone pillar / wall
    - Bottom near ground = thick ground / rubble / step
    - Otherwise = thin floating ledge (with stalactite teeth = good for ceilings)
    """
    if rect.height >= 150 and rect.width <= 80:
        draw_pillar_platform(screen, rect)
        return
    
    # Thin cap — draw as a slim ledge strip, no forced minimum height
    if rect.height <= 12:
        top_color  = (182, 186, 204)
        face_color = (90, 94, 112)
        dark_color = (50, 54, 70)
        glow_color = (85, 200, 250)
        pygame.draw.rect(screen, face_color, rect)
        pygame.draw.rect(screen, top_color,  (rect.x, rect.y, rect.width, 3))
        pygame.draw.rect(screen, (235, 238, 246), (rect.x, rect.y, rect.width, 1))
        for x in range(rect.x + 50, rect.right - 20, 140):
            pygame.draw.rect(screen, glow_color, (x, rect.y + 4, 14, 2))
        return

    # Anything whose bottom touches the ground line draws as solid stone (rubble / step / building)
    if rect.bottom >= SCREEN_HEIGHT - 70:
        draw_ground_platform(screen, rect)
        return
    # Floating slabs (interior walkways, ceilings) draw with hanging stalactite teeth
    draw_ledge_platform(screen, rect)


def draw_map6_tiled_platform(screen, rect):
    """Draw MAP 6 platforms inside their exact Tiled rectangle."""
    top = (188, 192, 205)
    face = (75, 80, 98)
    side = (45, 51, 67)
    dark = (34, 39, 54)
    cyan = (72, 210, 245)

    pygame.draw.rect(screen, face, rect)

    cap_h = min(7, max(2, rect.height))
    pygame.draw.rect(screen, top, (rect.x, rect.y, rect.width, cap_h))
    pygame.draw.rect(screen, (235, 238, 246), (rect.x, rect.y, rect.width, min(2, cap_h)))

    if rect.height >= 16:
        pygame.draw.rect(screen, dark, (rect.x, rect.bottom - min(6, rect.height), rect.width, min(6, rect.height)))
        for x in range(rect.x + 16, rect.right - 10, 44):
            pygame.draw.rect(screen, dark, (x, rect.y + min(17, rect.height - 5), 12, 3))

    for x in range(rect.x + 50, rect.right - 20, 130):
        pygame.draw.rect(screen, cyan, (x, rect.y + min(9, max(1, rect.height - 3)), 16, 3))

    if rect.width <= 90 and rect.height >= 90:
        pygame.draw.rect(screen, side, (rect.x, rect.y, min(4, rect.width), rect.height))
        pygame.draw.rect(screen, side, (rect.right - min(4, rect.width), rect.y, min(4, rect.width), rect.height))
        for y in range(rect.y + 28, rect.bottom - 8, 34):
            pygame.draw.rect(screen, dark, (rect.x + 4, y, max(0, rect.width - 8), 2))


def draw_collapsing_platform(screen, camera, platform):
    """Draw unstable military platforms with warning lights and rebuild scanlines."""
    base_rect = platform.rect.copy()

    if platform.state == "collapsed":
        progress = platform.rebuild_progress
        if progress < 0.62:
            return

        draw_rect = base_rect.copy()
        if camera is not None:
            draw_rect = camera.apply_rect(draw_rect)

        alpha = int(45 + 155 * progress)
        ghost = pygame.Surface((max(1, draw_rect.width), max(1, draw_rect.height)), pygame.SRCALPHA)
        pygame.draw.rect(ghost, (70, 210, 245, alpha), ghost.get_rect(), 2)
        for x in range(8, draw_rect.width - 4, 28):
            pygame.draw.rect(ghost, (70, 210, 245, max(30, alpha - 60)), (x, 4, 12, 3))
        for y in range(8, draw_rect.height - 4, 12):
            pygame.draw.line(ghost, (50, 120, 155, max(20, alpha - 90)), (4, y), (draw_rect.width - 4, y), 1)
        screen.blit(ghost, draw_rect.topleft)
        return

    shake = 0
    if platform.state == "warning":
        pulse = math.sin(platform.timer * 44.0)
        shake = int(round(pulse * platform.shake_px))

    draw_rect = base_rect.move(shake, 0)
    if camera is not None:
        draw_rect = camera.apply_rect(draw_rect)

    top = (188, 192, 205)
    face = (72, 78, 96)
    under = (30, 34, 47)
    dark = (37, 43, 58)
    cyan = (80, 210, 245)
    amber = (236, 176, 62)
    red = (232, 54, 58)

    pygame.draw.rect(screen, face, draw_rect)
    pygame.draw.rect(screen, top, (draw_rect.x, draw_rect.y, draw_rect.width, 6))
    pygame.draw.rect(screen, under, (draw_rect.x, draw_rect.bottom - 6, draw_rect.width, 6))
    pygame.draw.rect(screen, dark, draw_rect, 2)

    for x in range(draw_rect.x + 12, draw_rect.right - 14, 36):
        pygame.draw.rect(screen, dark, (x, draw_rect.y + 16, 12, 4))
    for x in range(draw_rect.x + 24, draw_rect.right - 10, 56):
        pygame.draw.rect(screen, cyan, (x, draw_rect.y + 9, 18, 3))

    tooth_pattern = [4, 6, 5, 7]
    tooth_y = draw_rect.bottom - min(8, draw_rect.height)
    for i, x in enumerate(range(draw_rect.x + 14, draw_rect.right - 14, 28)):
        pygame.draw.rect(screen, under, (x, tooth_y, 10, min(tooth_pattern[i % len(tooth_pattern)], draw_rect.height)))

    if platform.state == "warning":
        color = red if int(platform.timer * 12) % 2 == 0 else amber
        pygame.draw.rect(screen, color, draw_rect.inflate(4, 4), 2)
        for x in range(draw_rect.x + 10, draw_rect.right - 10, 44):
            pygame.draw.rect(screen, color, (x, draw_rect.y - 8, 18, 5))


def draw_pale_crown_transit_gate(screen, camera, door, font):
    """Draw the MAP 2 checkpoint transit gate without using the green door block."""
    rect = door["rect"]
    draw_rect = camera.apply_rect(rect) if camera is not None else rect.copy()
    cx = draw_rect.centerx
    floor_y = draw_rect.bottom

    glow = pygame.Surface((180, 150), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (52, 240, 160, 34), glow.get_rect())
    pygame.draw.ellipse(glow, (120, 88, 255, 28), glow.get_rect().inflate(-48, -28), 3)
    screen.blit(glow, (cx - glow.get_width() // 2, floor_y - 132))

    pygame.draw.ellipse(screen, (4, 8, 14), (cx - 70, floor_y - 9, 140, 18))

    gate = pygame.Rect(cx - 44, floor_y - 106, 88, 106)
    pygame.draw.rect(screen, (9, 15, 28), gate)
    pygame.draw.rect(screen, (59, 74, 98), gate, 3)
    pygame.draw.rect(screen, (21, 31, 52), (gate.x + 8, gate.y + 12, gate.width - 16, gate.height - 18))

    pygame.draw.rect(screen, (30, 42, 66), (gate.x - 12, gate.y + 22, 12, gate.height - 22))
    pygame.draw.rect(screen, (30, 42, 66), (gate.right, gate.y + 22, 12, gate.height - 22))
    pygame.draw.rect(screen, (96, 111, 138), (gate.x - 16, floor_y - 12, gate.width + 32, 12))

    portal = pygame.Rect(cx - 22, gate.y + 26, 44, 62)
    pygame.draw.rect(screen, (16, 76, 72), portal)
    pygame.draw.rect(screen, (83, 238, 174), portal, 3)
    pygame.draw.rect(screen, (122, 94, 255), (cx - 5, portal.y + 9, 10, portal.height - 18))
    pygame.draw.rect(screen, (197, 255, 232), (cx - 13, portal.y + 7, 26, 3))
    pygame.draw.rect(screen, (197, 255, 232), (cx - 13, portal.bottom - 10, 26, 3))

    crown_y = gate.y - 18
    pygame.draw.rect(screen, (102, 241, 188), (cx - 22, crown_y + 15, 44, 4))
    pygame.draw.polygon(screen, (102, 241, 188), [(cx - 23, crown_y + 15), (cx - 15, crown_y + 2), (cx - 7, crown_y + 15)])
    pygame.draw.polygon(screen, (102, 241, 188), [(cx - 6, crown_y + 15), (cx, crown_y - 6), (cx + 6, crown_y + 15)])
    pygame.draw.polygon(screen, (102, 241, 188), [(cx + 7, crown_y + 15), (cx + 15, crown_y + 2), (cx + 23, crown_y + 15)])

    for x_offset, color in [(-48, (58, 212, 255)), (48, (255, 86, 86)), (0, (146, 98, 255))]:
        pygame.draw.rect(screen, color, (cx + x_offset - 6, gate.y + 34, 12, 4))

    label = font.render(door.get("label", "Checkpoint"), True, (186, 245, 224))
    screen.blit(label, label.get_rect(midbottom=(cx, gate.y - 21)))


def draw_body_pile(screen, camera, x, y):
    """
    Draws a simple pile of bodies / aftermath scene.
    Decoration only. No collision.
    x, y are world coordinates near the ground.
    """

    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    def apply_pos(pos):
        if camera is not None:
            return camera.apply_pos(pos)
        return pos

    # Colors
    body_dark = (36, 34, 42)
    body_mid = (62, 58, 68)
    armor = (95, 102, 120)
    pale = (150, 140, 135)
    blood = (80, 28, 35)
    moon_glow = (110, 185, 225)
    shadow = (12, 12, 18)

    # Ground shadow
    shadow_rect = pygame.Rect(x - 70, y - 18, 155, 24)
    pygame.draw.ellipse(screen, shadow, apply_rect(shadow_rect))

    # Left body
    pygame.draw.rect(screen, body_mid, apply_rect(pygame.Rect(x - 58, y - 34, 48, 14)))
    pygame.draw.rect(screen, armor, apply_rect(pygame.Rect(x - 42, y - 45, 18, 14)))
    pygame.draw.circle(screen, pale, apply_pos((x - 66, y - 28)), 7)

    # Center body
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(x - 12, y - 42, 56, 18)))
    pygame.draw.rect(screen, armor, apply_rect(pygame.Rect(x + 3, y - 56, 20, 16)))
    pygame.draw.circle(screen, pale, apply_pos((x + 42, y - 39)), 7)

    # Right body
    pygame.draw.rect(screen, body_mid, apply_rect(pygame.Rect(x + 36, y - 29, 44, 13)))
    pygame.draw.rect(screen, armor, apply_rect(pygame.Rect(x + 48, y - 42, 18, 14)))
    pygame.draw.circle(screen, pale, apply_pos((x + 84, y - 26)), 6)

    # Broken limbs / extra pile feel
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(x - 24, y - 22, 14, 8)))
    pygame.draw.rect(screen, body_mid, apply_rect(pygame.Rect(x + 18, y - 18, 16, 7)))

    # Broken weapons / debris
    pygame.draw.rect(screen, armor, apply_rect(pygame.Rect(x - 80, y - 48, 34, 4)))
    pygame.draw.rect(screen, armor, apply_rect(pygame.Rect(x + 56, y - 54, 28, 4)))

    # Blood stains
    pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(x - 30, y - 14, 20, 4)))
    pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(x + 10, y - 12, 26, 4)))
    pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(x + 54, y - 10, 16, 3)))

    # Residual lunar energy from Kael's outburst
    pygame.draw.rect(screen, moon_glow, apply_rect(pygame.Rect(x - 6, y - 62, 16, 3)))
    pygame.draw.rect(screen, moon_glow, apply_rect(pygame.Rect(x + 18, y - 66, 8, 3)))
    pygame.draw.circle(screen, moon_glow, apply_pos((x + 7, y - 70)), 3)

def draw_moon_background(screen, camera, game_map):
    """
    Draws a simple moon-themed background.
    This is visual only. It does not affect collision or gameplay.
    """

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Base night sky
    screen.fill((10, 12, 22))

    # Camera offset for parallax movement
    camera_x = 0
    if camera is not None:
       if hasattr(camera, "offset"):
        camera_x = camera.offset.x
       elif hasattr(camera, "x"):
        camera_x = camera.x
       elif hasattr(camera, "camera"):
        camera_x = camera.camera.x

    # Big moon - moves slower than camera for depth effect
    moon_x = int(930 - camera_x * 0.15)
    moon_y = 120
    pygame.draw.circle(screen, (190, 200, 220), (moon_x, moon_y), 72)
    pygame.draw.circle(screen, (145, 155, 180), (moon_x - 24, moon_y - 18), 14)
    pygame.draw.circle(screen, (155, 165, 190), (moon_x + 26, moon_y + 16), 10)
    pygame.draw.circle(screen, (130, 140, 165), (moon_x + 8, moon_y - 35), 7)

    # Distant stars / lunar dust
    star_color = (120, 150, 190)
    for i in range(28):
        x = (i * 173 - int(camera_x * 0.08)) % (screen_width + 200) - 100
        y = 45 + (i * 47) % 260
        pygame.draw.rect(screen, star_color, (x, y, 2, 2))

    # Far ruined city silhouette
    far_color = (20, 24, 38)
    base_y = 555

    for i in range(18):
        tower_x = i * 170 - int(camera_x * 0.25) % 170
        tower_h = 80 + (i * 37) % 150
        tower_w = 55 + (i * 13) % 35

        rect = pygame.Rect(tower_x, base_y - tower_h, tower_w, tower_h)
        pygame.draw.rect(screen, far_color, rect)

        # Broken roof shape
        pygame.draw.polygon(
            screen,
            far_color,
            [
                (rect.left, rect.top),
                (rect.left + rect.width // 2, rect.top - 25),
                (rect.right, rect.top + 10),
            ],
        )

    # Closer broken ruins
    near_color = (28, 32, 48)

    for i in range(10):
        ruin_x = i * 260 - int(camera_x * 0.45) % 260
        ruin_h = 90 + (i * 53) % 120
        ruin_w = 70 + (i * 19) % 50

        rect = pygame.Rect(ruin_x, 610 - ruin_h, ruin_w, ruin_h)
        pygame.draw.rect(screen, near_color, rect)

        # Window holes
        for wy in range(rect.y + 20, rect.bottom - 20, 32):
            pygame.draw.rect(screen, (12, 14, 24), (rect.x + 16, wy, 10, 16))
            pygame.draw.rect(screen, (12, 14, 24), (rect.x + 42, wy, 10, 16))

    # Light fog near ground
    fog = pygame.Surface((screen_width, 120), pygame.SRCALPHA)
    fog.fill((80, 95, 130, 32))
    screen.blit(fog, (0, screen_height - 170))

def draw_level1_room_shells(screen, camera, game_map):
    """
    For each ceiling: draws the dark void above + the wallpaper (stone interior fill)
    DOWN ONLY as far as the side walls extend. The strip below the wall bottom is left
    clear so the doorway shows the moon background through it = visually obvious entry.
    """
    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    void_color = (14, 17, 26)
    trim = (72, 82, 112)
    wallpaper = (26, 30, 46)
    wallpaper_joint = (16, 19, 30)

    tower_fill = (28, 32, 46)
    tower_dark = (18, 21, 32)
    tower_window = (8, 10, 18)

    # === First pass: enclosed rooms (ceiling + walls) get void + wallpaper ===
    handled_rects = set()
    for plat in game_map.platforms:
        if plat.y < 320 and plat.height <= 50 and plat.width >= 200:
            ceiling_bottom = plat.y + plat.height
            wall_bottom = None
            for w in game_map.platforms:
                if (w.height >= 150 and w.width <= 80
                        and plat.x <= w.x and w.right <= plat.right
                        and w.y >= ceiling_bottom):
                    wall_bottom = w.bottom if wall_bottom is None else max(wall_bottom, w.bottom)
            if wall_bottom is None:
                continue   # not an enclosed room — handled in second pass

            handled_rects.add(id(plat))

            # Dark void above ceiling
            void = pygame.Rect(plat.x, plat.y - 400, plat.width, 400 + plat.height)
            pygame.draw.rect(screen, void_color, apply_rect(void))
            pygame.draw.rect(screen, trim, apply_rect(pygame.Rect(plat.x, plat.y - 4, plat.width, 4)))

            # Wallpaper — stone fill only between ceiling and wall.bottom
            interior_h = wall_bottom - ceiling_bottom
            if interior_h > 0:
                interior = pygame.Rect(plat.x, ceiling_bottom, plat.width, interior_h)
                pygame.draw.rect(screen, wallpaper, apply_rect(interior))
                for jy in range(ceiling_bottom + 35, wall_bottom, 50):
                    pygame.draw.rect(screen, wallpaper_joint, apply_rect(pygame.Rect(plat.x, jy, plat.width, 2)))

    # === Second pass: stacked outdoor slabs (rubble towers) get a tower fill ===
    # Group platforms by horizontal overlap. If 2+ platforms share x range and are
    # stacked vertically, draw a stone-tower background spanning their combined extent.
    candidates = [p for p in game_map.platforms
                  if p.width >= 100 and p.height <= 50 and p.bottom < 650 and id(p) not in handled_rects]
    used = set()
    for p in candidates:
        if id(p) in used:
            continue
        group = [p]
        for q in candidates:
            if id(q) in used or q is p:
                continue
            # Same x range (within 20px tolerance on each side)
            if abs(q.x - p.x) <= 20 and abs(q.right - p.right) <= 20:
                group.append(q)
        if len(group) < 2:
            continue
        for g in group:
            used.add(id(g))
        gx = min(g.x for g in group)
        gright = max(g.right for g in group)
        gtop = min(g.y for g in group)
        gbottom = max(g.bottom for g in group)
        # Extend the fill down to ground level so the tower meets the street
        tower = pygame.Rect(gx, gtop, gright - gx, 650 - gtop)
        pygame.draw.rect(screen, tower_fill, apply_rect(tower))
        pygame.draw.rect(screen, tower_dark, apply_rect(tower), 3)
        # Window holes — 3 columns, evenly spaced rows down the tower
        col_count = max(1, (tower.width - 40) // 80)
        col_step = (tower.width - 40) // max(1, col_count)
        for row_y in range(gtop + 30, 650 - 40, 70):
            for c in range(col_count):
                wx = gx + 20 + c * col_step
                pygame.draw.rect(screen, tower_window, apply_rect(pygame.Rect(wx, row_y, 30, 26)))

def draw_level1_wall_masses(screen, camera, game_map=None):
    """
    Auto-detects ground islands (rects at y=650 with full street height) and draws
    a thick dark embankment wall behind each one — makes the street feel raised
    instead of a thin floating bar.
    """
    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    wall      = (34, 39, 58)
    wall_dark = (18, 21, 32)
    road_dark = (28, 32, 45)
    window    = (9, 11, 18)

    GROUND_Y = 650
    EMBANKMENT_Y = 558

    if game_map is None:
        return

    for plat in game_map.platforms:
        # Ground islands sit at y=650 with a 70px tall body
        if plat.y == GROUND_Y and plat.height == 70 and plat.width >= 80:
            block = pygame.Rect(plat.x, EMBANKMENT_Y, plat.width, GROUND_Y - EMBANKMENT_Y)
            pygame.draw.rect(screen, wall, apply_rect(block))
            pygame.draw.rect(screen, wall_dark, apply_rect(block), 4)
            pygame.draw.rect(screen, road_dark, apply_rect(pygame.Rect(block.x, block.y + 16, block.width, 6)))
            for x in range(block.x + 60, block.right - 50, 160):
                hole_h = block.height - 30
                if hole_h > 10:
                    pygame.draw.rect(screen, window, apply_rect(pygame.Rect(x, block.y + 24, 36, hole_h)))

def draw_section4_tram_wreck(screen, camera):
    """
    Section 4 (x=3900-5100): A real crashed-tram scene.
    - Train rails along the ground
    - Hanging power-line poles + sagging cables (one broken, sparking)
    - 3 tram cars + a cab debris piece, each with body/windows/doors/wheels
    - Tram car 3 is overturned on its side with smoke billowing out
    - Scattered glass + twisted metal on the ground
    """
    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    def apply_pos(pos):
        if camera is not None:
            return camera.apply_pos(pos)
        return pos

    # ─── Colors ────────────────────────────────────────────────────────
    body_main   = (62, 75, 98)
    body_dark   = (32, 42, 60)
    body_light  = (90, 108, 130)
    glass       = (30, 50, 80)
    glass_glow  = (95, 135, 175)
    metal       = (95, 100, 110)
    metal_dark  = (45, 50, 60)
    rust        = (130, 65, 35)
    rust_dark   = (80, 35, 15)
    wheel       = (28, 30, 38)
    wheel_hub   = (75, 80, 90)
    rail        = (115, 115, 125)
    rail_dark   = (60, 60, 70)
    tie         = (60, 45, 30)
    spark       = (255, 220, 100)
    spark_hot   = (255, 255, 220)
    cable       = (32, 32, 42)
    pole        = (62, 68, 78)
    pole_dark   = (35, 38, 48)
    smoke       = (75, 75, 82)
    smoke_light = (110, 110, 118)
    ember       = (255, 130, 60)

    # ─── Train tracks along the street ─────────────────────────────────
    # Crossties (sleepers) every 24px
    for tx in range(3900, 5100, 24):
        pygame.draw.rect(screen, tie, apply_rect(pygame.Rect(tx, 656, 18, 5)))
    # Two parallel rails (front + back)
    pygame.draw.rect(screen, rail, apply_rect(pygame.Rect(3900, 653, 1200, 3)))
    pygame.draw.rect(screen, rail_dark, apply_rect(pygame.Rect(3900, 656, 1200, 1)))
    pygame.draw.rect(screen, rail, apply_rect(pygame.Rect(3900, 664, 1200, 3)))
    pygame.draw.rect(screen, rail_dark, apply_rect(pygame.Rect(3900, 667, 1200, 1)))
    # Bent rail near the crash — kinked upward
    pygame.draw.line(screen, rail, apply_pos((4670, 654)), apply_pos((4720, 638)), 3)
    pygame.draw.line(screen, rail, apply_pos((4720, 638)), apply_pos((4760, 654)), 3)
    pygame.draw.line(screen, rail, apply_pos((4670, 665)), apply_pos((4720, 648)), 3)
    pygame.draw.line(screen, rail, apply_pos((4720, 648)), apply_pos((4760, 665)), 3)

    # ─── Power-line poles ──────────────────────────────────────────────
    for px in [3950, 4400, 4850]:
        pygame.draw.rect(screen, pole, apply_rect(pygame.Rect(px, 350, 6, 200)))
        pygame.draw.rect(screen, pole_dark, apply_rect(pygame.Rect(px, 350, 6, 200)), 1)
        # Crossbar
        pygame.draw.rect(screen, pole, apply_rect(pygame.Rect(px - 18, 350, 42, 6)))
        pygame.draw.rect(screen, pole_dark, apply_rect(pygame.Rect(px - 18, 350, 42, 6)), 1)
        # Insulators (small)
        pygame.draw.rect(screen, (180, 170, 150), apply_rect(pygame.Rect(px - 14, 346, 4, 6)))
        pygame.draw.rect(screen, (180, 170, 150), apply_rect(pygame.Rect(px + 16, 346, 4, 6)))

    # ─── Sagging cables between poles ──────────────────────────────────
    # Between pole 1 and pole 2 — slight sag
    pygame.draw.line(screen, cable, apply_pos((3956, 354)), apply_pos((4180, 405)), 2)
    pygame.draw.line(screen, cable, apply_pos((4180, 405)), apply_pos((4400, 354)), 2)
    # Between pole 2 and pole 3 — broken, drooping down toward overturned car, sparking
    pygame.draw.line(screen, cable, apply_pos((4406, 354)), apply_pos((4620, 420)), 2)
    pygame.draw.line(screen, cable, apply_pos((4620, 420)), apply_pos((4770, 470)), 2)
    # Sparks at the broken end
    pygame.draw.circle(screen, spark, apply_pos((4770, 470)), 3)
    pygame.draw.circle(screen, spark_hot, apply_pos((4770, 470)), 1)
    for sx, sy in [(4762, 478), (4780, 463), (4774, 482), (4768, 462)]:
        pygame.draw.rect(screen, spark, apply_rect(pygame.Rect(sx, sy, 2, 2)))
    # Continuing cable past the broken section
    pygame.draw.line(screen, cable, apply_pos((4856, 354)), apply_pos((5080, 405)), 2)

    # ─── Tram Car 1: Mostly intact, on wheels (4030, 520, 360, 130) ────
    c1x, c1y, c1w, c1h = 4030, 520, 360, 130
    # Main body
    pygame.draw.rect(screen, body_main, apply_rect(pygame.Rect(c1x, c1y + 10, c1w, c1h - 10)))
    # Roof (slightly indented = lighter)
    pygame.draw.rect(screen, body_light, apply_rect(pygame.Rect(c1x + 8, c1y, c1w - 16, 14)))
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(c1x + 8, c1y, c1w - 16, 14)), 1)
    # Belt line stripe
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(c1x + 4, c1y + 56, c1w - 8, 3)))
    # Bottom shadow strip
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(c1x, c1y + c1h - 14, c1w, 6)))
    # Windows — 4 across the upper body
    for wi in range(4):
        wx = c1x + 22 + wi * 78
        pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(wx, c1y + 22, 56, 28)))
        pygame.draw.rect(screen, glass_glow, apply_rect(pygame.Rect(wx + 4, c1y + 26, 14, 4)))
        pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(wx, c1y + 22, 56, 28)), 1)
    # Door on the right
    dx, dy = c1x + c1w - 50, c1y + 68
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(dx, dy, 36, 58)))
    pygame.draw.rect(screen, body_light, apply_rect(pygame.Rect(dx, dy, 36, 58)), 2)
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(dx + 28, dy + 26, 4, 8)))   # handle
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(dx + 16, dy, 2, 58)))   # door split line
    # Tram route number plate
    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(c1x + 14, c1y + 18, 20, 12)))
    pygame.draw.rect(screen, spark, apply_rect(pygame.Rect(c1x + 17, c1y + 21, 14, 6)))
    # Rust patches
    pygame.draw.rect(screen, rust, apply_rect(pygame.Rect(c1x + 90, c1y + 80, 22, 18)))
    pygame.draw.rect(screen, rust_dark, apply_rect(pygame.Rect(c1x + 92, c1y + 82, 14, 6)))
    pygame.draw.rect(screen, rust, apply_rect(pygame.Rect(c1x + 240, c1y + 96, 18, 14)))
    pygame.draw.rect(screen, rust_dark, apply_rect(pygame.Rect(c1x + 244, c1y + 100, 10, 4)))
    # Wheels — 4 along the bottom
    for wx_off in [45, 115, 245, 315]:
        wx = c1x + wx_off
        pygame.draw.circle(screen, wheel, apply_pos((wx, c1y + c1h + 4)), 13)
        pygame.draw.circle(screen, wheel_hub, apply_pos((wx, c1y + c1h + 4)), 6)
        pygame.draw.circle(screen, metal_dark, apply_pos((wx, c1y + c1h + 4)), 13, 2)
        # Spokes
        for sa in range(0, 4):
            ang = sa * 0.78
            sx = int(wx + math.cos(ang) * 8)
            sy = int(c1y + c1h + 4 + math.sin(ang) * 8)
            pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(sx - 1, sy - 1, 2, 2)))
    # Coupler at the right end (connects to next car)
    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(c1x + c1w, c1y + c1h - 28, 30, 10)))
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(c1x + c1w + 4, c1y + c1h - 26, 22, 6)))

    # ─── Tram Car 2: Derailed and smashed (4420, 560, 260, 90) ─────────
    c2x, c2y, c2w, c2h = 4420, 560, 260, 90
    pygame.draw.rect(screen, body_main, apply_rect(pygame.Rect(c2x, c2y + 8, c2w, c2h - 8)))
    pygame.draw.rect(screen, body_light, apply_rect(pygame.Rect(c2x + 6, c2y, c2w - 12, 11)))
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(c2x + 6, c2y, c2w - 12, 11)), 1)
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(c2x, c2y + c2h - 10, c2w, 5)))
    # Broken windows (3 — dark inside, jagged glass edges)
    for wi in range(3):
        wx = c2x + 18 + wi * 78
        pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(wx, c2y + 18, 52, 26)))
        # Glass shards remaining at edges
        pygame.draw.polygon(screen, glass, [
            apply_pos((wx, c2y + 18)), apply_pos((wx + 12, c2y + 18)),
            apply_pos((wx + 8, c2y + 32)), apply_pos((wx + 2, c2y + 28)),
        ])
        pygame.draw.polygon(screen, glass, [
            apply_pos((wx + 52, c2y + 18)), apply_pos((wx + 40, c2y + 18)),
            apply_pos((wx + 44, c2y + 26)),
        ])
    # Big crack / dent zig-zagging across the body
    pygame.draw.lines(screen, body_dark, False, [
        apply_pos((c2x + 30, c2y + 50)),
        apply_pos((c2x + 70, c2y + 65)),
        apply_pos((c2x + 110, c2y + 55)),
        apply_pos((c2x + 150, c2y + 72)),
        apply_pos((c2x + 200, c2y + 60)),
    ], 4)
    # Rust over the dent
    pygame.draw.rect(screen, rust, apply_rect(pygame.Rect(c2x + 60, c2y + 58, 30, 18)))
    pygame.draw.rect(screen, rust_dark, apply_rect(pygame.Rect(c2x + 66, c2y + 62, 18, 8)))
    pygame.draw.rect(screen, rust, apply_rect(pygame.Rect(c2x + 200, c2y + 52, 25, 20)))
    # Wheels — front one intact, middle missing (off the rail), rear intact
    pygame.draw.circle(screen, wheel, apply_pos((c2x + 32, c2y + c2h + 4)), 12)
    pygame.draw.circle(screen, wheel_hub, apply_pos((c2x + 32, c2y + c2h + 4)), 6)
    pygame.draw.circle(screen, wheel, apply_pos((c2x + 220, c2y + c2h + 4)), 12)
    pygame.draw.circle(screen, wheel_hub, apply_pos((c2x + 220, c2y + c2h + 4)), 6)
    # Detached wheel rolled away
    pygame.draw.circle(screen, wheel, apply_pos((c2x + 130, c2y + c2h + 12)), 10)
    pygame.draw.circle(screen, wheel_hub, apply_pos((c2x + 130, c2y + c2h + 12)), 5)
    # Coupler dangling
    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(c2x - 22, c2y + c2h - 16, 24, 8)))

    # ─── Tram Car 3: Overturned on its side (4730, 480, 240, 170) ──────
    c3x, c3y, c3w, c3h = 4730, 480, 240, 170
    # Body (now vertical since car is on its side)
    pygame.draw.rect(screen, body_main, apply_rect(pygame.Rect(c3x + 10, c3y, c3w - 20, c3h)))
    # "Roof" is now on the LEFT face (the curved side was on top before)
    pygame.draw.rect(screen, body_light, apply_rect(pygame.Rect(c3x, c3y + 8, 14, c3h - 16)))
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(c3x, c3y + 8, 14, c3h - 16)), 1)
    # "Bottom" is now on the RIGHT face (where wheels stick out)
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(c3x + c3w - 14, c3y + 8, 8, c3h - 16)))
    # Windows now stacked vertically along the visible side
    for wi in range(3):
        wy = c3y + 22 + wi * 50
        pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(c3x + 70, wy, 36, 36)))   # broken interior
        pygame.draw.polygon(screen, glass, [
            apply_pos((c3x + 70, wy)), apply_pos((c3x + 82, wy)),
            apply_pos((c3x + 78, wy + 14)),
        ])
        pygame.draw.polygon(screen, glass, [
            apply_pos((c3x + 106, wy + 36)), apply_pos((c3x + 96, wy + 36)),
            apply_pos((c3x + 102, wy + 22)),
        ])
    # Door now appears near the bottom of the visible side
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(c3x + 28, c3y + 130, 32, 32)))
    pygame.draw.rect(screen, body_light, apply_rect(pygame.Rect(c3x + 28, c3y + 130, 32, 32)), 1)
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(c3x + 50, c3y + 144, 4, 5)))
    # Wheels visible on the right side (sticking out — car is sideways)
    for wy_off in [30, 90, 140]:
        wx = c3x + c3w + 4
        pygame.draw.circle(screen, wheel, apply_pos((wx, c3y + wy_off)), 13)
        pygame.draw.circle(screen, wheel_hub, apply_pos((wx, c3y + wy_off)), 6)
        pygame.draw.circle(screen, metal_dark, apply_pos((wx, c3y + wy_off)), 13, 2)
    # Heavy rust patches all over this car
    pygame.draw.rect(screen, rust, apply_rect(pygame.Rect(c3x + 30, c3y + 60, 30, 32)))
    pygame.draw.rect(screen, rust_dark, apply_rect(pygame.Rect(c3x + 36, c3y + 66, 18, 18)))
    pygame.draw.rect(screen, rust, apply_rect(pygame.Rect(c3x + 150, c3y + 100, 24, 28)))
    pygame.draw.rect(screen, rust_dark, apply_rect(pygame.Rect(c3x + 156, c3y + 106, 14, 16)))
    # Smoke billowing up from the wreck
    pygame.draw.ellipse(screen, smoke, apply_rect(pygame.Rect(c3x + 70, c3y - 30, 50, 32)))
    pygame.draw.ellipse(screen, smoke_light, apply_rect(pygame.Rect(c3x + 90, c3y - 55, 38, 30)))
    pygame.draw.ellipse(screen, smoke, apply_rect(pygame.Rect(c3x + 110, c3y - 90, 60, 42)))
    pygame.draw.ellipse(screen, smoke_light, apply_rect(pygame.Rect(c3x + 130, c3y - 130, 48, 38)))
    pygame.draw.ellipse(screen, smoke, apply_rect(pygame.Rect(c3x + 80, c3y - 160, 80, 52)))
    # Embers/sparks near the wreck
    for ex, ey in [(c3x + 95, c3y + 15), (c3x + 130, c3y - 5), (c3x + 80, c3y - 8)]:
        pygame.draw.circle(screen, ember, apply_pos((ex, ey)), 2)
        pygame.draw.circle(screen, spark_hot, apply_pos((ex, ey)), 1)

    # ─── Cab debris piece (4990, 580, 110, 70) ─────────────────────────
    cx, cy, cw, ch = 4990, 580, 110, 70
    pygame.draw.rect(screen, body_main, apply_rect(pygame.Rect(cx, cy + 6, cw, ch - 6)))
    pygame.draw.rect(screen, body_light, apply_rect(pygame.Rect(cx + 2, cy, cw - 4, 10)))
    pygame.draw.rect(screen, body_dark, apply_rect(pygame.Rect(cx, cy + ch - 6, cw, 4)))
    # Driver's windshield (slanted broken)
    pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(cx + 14, cy + 14, 42, 28)))
    pygame.draw.rect(screen, glass_glow, apply_rect(pygame.Rect(cx + 18, cy + 18, 10, 5)))
    # Crack across windshield
    pygame.draw.line(screen, body_dark, apply_pos((cx + 14, cy + 18)), apply_pos((cx + 56, cy + 40)), 2)
    pygame.draw.line(screen, body_dark, apply_pos((cx + 32, cy + 14)), apply_pos((cx + 40, cy + 42)), 1)
    # Twisted metal sticking out the right side
    pygame.draw.line(screen, metal, apply_pos((cx + cw, cy + 20)), apply_pos((cx + cw + 22, cy + 4)), 3)
    pygame.draw.line(screen, metal, apply_pos((cx + cw + 22, cy + 4)), apply_pos((cx + cw + 35, cy + 30)), 3)
    pygame.draw.line(screen, metal_dark, apply_pos((cx + cw + 8, cy + 35)), apply_pos((cx + cw + 28, cy + 50)), 2)
    # Wheel
    pygame.draw.circle(screen, wheel, apply_pos((cx + 25, cy + ch + 4)), 10)
    pygame.draw.circle(screen, wheel_hub, apply_pos((cx + 25, cy + ch + 4)), 5)
    # Headlight (broken, dim glow)
    pygame.draw.circle(screen, (180, 180, 100), apply_pos((cx + 88, cy + 36)), 4)
    pygame.draw.circle(screen, spark_hot, apply_pos((cx + 88, cy + 36)), 1)

    # ─── Ground debris between/around the cars ─────────────────────────
    # Broken glass shards
    for gx in [4180, 4360, 4520, 4700, 4880, 5060]:
        pygame.draw.polygon(screen, glass, [
            apply_pos((gx, 646)), apply_pos((gx + 8, 644)), apply_pos((gx + 5, 650)),
        ])
        pygame.draw.rect(screen, glass_glow, apply_rect(pygame.Rect(gx + 1, 645, 2, 1)))
    # Twisted metal scraps
    for mx in [4200, 4380, 4640, 4940]:
        pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(mx, 643, 28, 7)))
        pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(mx + 6, 641, 14, 4)))
    # Spilled oil / dark stain under tram 2
    pygame.draw.ellipse(screen, (15, 15, 22), apply_rect(pygame.Rect(c2x + 80, 644, 110, 8)))

def draw_section_decorations(screen, camera):
    """
    Visual props (no collision) that make Map 0 sections feel ruined.
    Section 1: aftermath of body pile — skeletons, blood, broken weapons, dropped sign
    Section 2: destroyed street — overturned car, skeletons, broken signs, road cracks
    Section 3: ruined building interior — broken furniture, hanging chains, lights, stains
    """
    def apply_pos(pos):
        if camera is not None:
            return camera.apply_pos(pos)
        return pos

    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    blood = (88, 26, 36)
    bone = (190, 184, 168)
    bone_dark = (104, 99, 88)
    metal = (95, 100, 115)
    metal_dark = (45, 50, 65)
    dark = (16, 18, 26)
    glow = (90, 200, 245)

    # ─── Section 1: Body Pile aftermath (x=0-1100) ───────────────────────
    # Standing broken streetlights (atmospheric — moon-glow lamps)
    for sx in [80, 950]:
        pygame.draw.rect(screen, (50, 55, 70), apply_rect(pygame.Rect(sx, 540, 5, 110)))    # post
        pygame.draw.rect(screen, (50, 55, 70), apply_rect(pygame.Rect(sx - 8, 540, 22, 5))) # cross arm
        pygame.draw.circle(screen, (210, 195, 100), apply_pos((sx + 3, 548)), 6)             # bulb
        pygame.draw.circle(screen, (255, 235, 140), apply_pos((sx + 3, 548)), 3)             # bulb core
    # Standing rusted barrel
    pygame.draw.rect(screen, (90, 55, 35), apply_rect(pygame.Rect(660, 612, 26, 38)))
    pygame.draw.rect(screen, (60, 35, 22), apply_rect(pygame.Rect(660, 612, 26, 4)))
    pygame.draw.rect(screen, (60, 35, 22), apply_rect(pygame.Rect(660, 638, 26, 4)))
    # Fallen sword stuck in the ground (vertical)
    pygame.draw.rect(screen, (170, 175, 190), apply_rect(pygame.Rect(395, 612, 4, 38)))   # blade
    pygame.draw.rect(screen, (90, 70, 50), apply_rect(pygame.Rect(391, 608, 12, 6)))      # crossguard
    pygame.draw.rect(screen, (60, 45, 35), apply_rect(pygame.Rect(394, 600, 6, 10)))      # grip
    # Dropped helmet
    pygame.draw.ellipse(screen, (75, 80, 95), apply_rect(pygame.Rect(820, 630, 22, 18)))
    pygame.draw.ellipse(screen, (50, 55, 70), apply_rect(pygame.Rect(823, 638, 16, 8)))
    # Blood smears across the road
    for x in [60, 230, 310, 400, 760, 870, 990]:
        pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(x, 642, 32, 5)))
        pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(x + 6, 646, 14, 3)))
    # Scattered bones / skulls
    for x, y in [(300, 644), (390, 644), (760, 643), (920, 644), (1010, 644)]:
        pygame.draw.circle(screen, bone, apply_pos((x, y)), 5)
        pygame.draw.rect(screen, bone_dark, apply_rect(pygame.Rect(x - 2, y - 1, 4, 2)))
        pygame.draw.rect(screen, bone, apply_rect(pygame.Rect(x + 7, y + 2, 14, 3)))  # rib bone
    # Broken weapons on the ground
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(360, 644, 32, 3)))
    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(355, 642, 8, 7)))   # hilt
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(820, 643, 28, 4)))
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(190, 645, 22, 3)))
    # Fallen lamp post lying on ground
    pygame.draw.rect(screen, (60, 65, 80), apply_rect(pygame.Rect(140, 638, 80, 5)))
    pygame.draw.circle(screen, (200, 180, 90), apply_pos((226, 640)), 6)
    pygame.draw.circle(screen, glow, apply_pos((226, 640)), 3)
    # Knocked-over warning sign (at the cracked road)
    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(440, 562, 4, 18)))     # broken post
    pygame.draw.rect(screen, (200, 165, 75), apply_rect(pygame.Rect(420, 552, 32, 14)))
    pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(424, 556, 24, 3)))            # text bar
    # Torn banner hanging from somewhere
    pygame.draw.rect(screen, (95, 35, 45), apply_rect(pygame.Rect(720, 540, 4, 60)))
    pygame.draw.polygon(screen, (95, 35, 45), [
        apply_pos((720, 600)), apply_pos((758, 605)), apply_pos((735, 624)),
    ])

    # ─── Section 2: Destroyed Street (x=1100-2400) ───────────────────────
    # Cracked road segments
    for x in [1130, 1430, 1900, 2150, 2330]:
        pygame.draw.line(screen, dark, apply_pos((x, 642)), apply_pos((x + 30, 650)), 3)
        pygame.draw.line(screen, dark, apply_pos((x + 18, 646)), apply_pos((x + 10, 656)), 2)
    # Burnt wreckage piles
    burn = (38, 28, 22)
    for x in [1140, 1620, 1980, 2280]:
        pygame.draw.rect(screen, burn, apply_rect(pygame.Rect(x, 640, 50, 8)))
        pygame.draw.rect(screen, (60, 40, 28), apply_rect(pygame.Rect(x + 8, 638, 26, 5)))
    # Overturned wrecked car
    car_dark = (35, 38, 50)
    car_mid = (62, 68, 84)
    car_glass = (50, 105, 135)
    car_x = 2240
    pygame.draw.rect(screen, car_dark, apply_rect(pygame.Rect(car_x, 622, 130, 28)))    # body
    pygame.draw.rect(screen, car_mid, apply_rect(pygame.Rect(car_x + 12, 612, 106, 12)))  # cab
    pygame.draw.rect(screen, car_glass, apply_rect(pygame.Rect(car_x + 32, 615, 60, 7)))  # window
    pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(car_x + 30, 622, 4, 6)))        # broken
    pygame.draw.circle(screen, (15, 15, 20), apply_pos((car_x + 28, 650)), 9)             # wheel
    pygame.draw.circle(screen, (15, 15, 20), apply_pos((car_x + 102, 650)), 9)
    pygame.draw.circle(screen, (45, 45, 55), apply_pos((car_x + 28, 650)), 4)             # hubcap
    pygame.draw.circle(screen, (45, 45, 55), apply_pos((car_x + 102, 650)), 4)
    # Knocked-down street signs (post at angle)
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(1480, 600, 4, 50)))
    pygame.draw.rect(screen, (200, 170, 80), apply_rect(pygame.Rect(1462, 590, 38, 14)))
    pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(1467, 595, 28, 4)))
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(1900, 605, 4, 45)))
    pygame.draw.rect(screen, (90, 130, 180), apply_rect(pygame.Rect(1882, 596, 38, 12)))
    # Blood and bones in section 2
    for x in [1240, 1660, 2030, 2370]:
        pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(x, 642, 28, 4)))
    for x, y in [(1450, 644), (1900, 644), (2210, 644)]:
        pygame.draw.circle(screen, bone, apply_pos((x, y)), 5)
        pygame.draw.rect(screen, bone, apply_rect(pygame.Rect(x + 8, y + 1, 14, 3)))
    # Smoldering ember spots
    for x in [1180, 1660, 2050]:
        pygame.draw.circle(screen, (180, 60, 30), apply_pos((x + 25, 645)), 3)
        pygame.draw.circle(screen, (240, 130, 40), apply_pos((x + 25, 645)), 1)

    # Standing broken streetlights in section 2
    for sx in [1150, 2050]:
        pygame.draw.rect(screen, (50, 55, 70), apply_rect(pygame.Rect(sx, 540, 5, 110)))
        pygame.draw.rect(screen, (50, 55, 70), apply_rect(pygame.Rect(sx - 8, 540, 22, 5)))
        pygame.draw.circle(screen, (210, 195, 100), apply_pos((sx + 3, 548)), 6)
        pygame.draw.circle(screen, (255, 235, 140), apply_pos((sx + 3, 548)), 3)

    # Trash piles / rubbish scattered
    junk_a = (60, 50, 40)
    junk_b = (95, 80, 60)
    for x in [1330, 1830, 2160]:
        pygame.draw.rect(screen, junk_a, apply_rect(pygame.Rect(x, 638, 35, 12)))
        pygame.draw.rect(screen, junk_b, apply_rect(pygame.Rect(x + 5, 634, 20, 8)))
        pygame.draw.rect(screen, junk_a, apply_rect(pygame.Rect(x + 22, 636, 10, 6)))

    # Hanging wires / power cables sagging across the street
    cable = (30, 30, 38)
    pygame.draw.line(screen, cable, apply_pos((1180, 540)), apply_pos((1500, 580)), 2)
    pygame.draw.line(screen, cable, apply_pos((1500, 580)), apply_pos((1820, 545)), 2)
    pygame.draw.line(screen, cable, apply_pos((1820, 545)), apply_pos((2080, 580)), 2)

    # ─── Building entry signboard (just before Section 3 at x≈2360) ──────
    # Tall warning sign on a metal post — clear "BUILDING AHEAD" hint
    sign_post = (60, 65, 75)
    sign_panel = (90, 75, 50)
    sign_metal = (140, 115, 65)
    sign_x = 2360
    pygame.draw.rect(screen, sign_post, apply_rect(pygame.Rect(sign_x + 3, 540, 6, 110)))                 # post
    pygame.draw.rect(screen, sign_panel, apply_rect(pygame.Rect(sign_x - 38, 514, 90, 44)))                # board
    pygame.draw.rect(screen, sign_metal, apply_rect(pygame.Rect(sign_x - 38, 514, 90, 44)), 2)             # frame
    # Warning chevrons / hazard stripe
    pygame.draw.rect(screen, (200, 60, 40), apply_rect(pygame.Rect(sign_x - 33, 522, 80, 5)))
    # Building icon (house shape with door)
    pygame.draw.rect(screen, (40, 30, 24), apply_rect(pygame.Rect(sign_x - 18, 535, 36, 18)))             # building body
    pygame.draw.polygon(screen, (40, 30, 24), [
        apply_pos((sign_x - 22, 535)), apply_pos((sign_x + 22, 535)), apply_pos((sign_x, 525)),
    ])  # roof
    pygame.draw.rect(screen, sign_panel, apply_rect(pygame.Rect(sign_x - 4, 543, 8, 10)))                  # door on icon
    # Small lamp at the top of the post
    pygame.draw.circle(screen, (255, 200, 90), apply_pos((sign_x + 6, 510)), 4)
    pygame.draw.circle(screen, (255, 240, 150), apply_pos((sign_x + 6, 510)), 2)

    # Stone bollards/markers flanking the building entrance
    for bx in [2390, 2392 - 2]:
        pass
    bollard = (95, 100, 115)
    bollard_dark = (45, 50, 65)
    for bx in [2384]:
        pygame.draw.rect(screen, bollard, apply_rect(pygame.Rect(bx, 622, 14, 28)))
        pygame.draw.rect(screen, bollard_dark, apply_rect(pygame.Rect(bx, 622, 14, 4)))
        pygame.draw.circle(screen, (90, 200, 240), apply_pos((bx + 7, 628)), 2)  # moon-glow rune

    # Faint moon-rune glyphs on the road approaching the building
    rune = (100, 200, 240)
    for rx in [2280, 2330]:
        pygame.draw.rect(screen, rune, apply_rect(pygame.Rect(rx, 644, 12, 2)))
        pygame.draw.rect(screen, rune, apply_rect(pygame.Rect(rx + 4, 640, 4, 8)))

    # ─── Section 2: Chains hanging from floating block to the 3 pillars ──
    # The big block top: pygame.Rect(1990, -30, 410, 140) -> bottom at y=110
    # Pillar 1: Rect(1990, 280, 40, 300) -> top y=280, center x=2010
    # Pillar 2: Rect(2100, 220, 40, 360) -> top y=220, center x=2120
    # Pillar 3: Rect(2200, 300, 40, 360) -> top y=300, center x=2220
    chain_rope = (60, 50, 40)
    chain_link = (74, 70, 62)
    chain_hook = (95, 85, 70)
    chain_data = [
        (2010, 110, 280),   # pillar 1: chain length 170
        (2120, 110, 220),   # pillar 2: chain length 110
        (2220, 110, 300),   # pillar 3: chain length 190
    ]
    for cx, top_y, bot_y in chain_data:
        chain_h = bot_y - top_y
        # Rope spine running from the block down to the pillar top
        pygame.draw.rect(screen, chain_rope, apply_rect(pygame.Rect(cx, top_y, 4, chain_h)))
        # Chain links every 18px along the rope
        for ly in range(top_y + 8, bot_y - 8, 18):
            pygame.draw.rect(screen, chain_link, apply_rect(pygame.Rect(cx - 3, ly, 10, 6)))
        # Top hook attached to the block, bottom hook attached to the pillar
        pygame.draw.rect(screen, chain_hook, apply_rect(pygame.Rect(cx - 5, top_y - 4, 14, 8)))
        pygame.draw.rect(screen, chain_hook, apply_rect(pygame.Rect(cx - 5, bot_y - 6, 14, 10)))

    # ─── Section 3: Ruined Building Interior (x=2400-3900) ───────────────
    rope = (60, 50, 40)
    chain = (74, 70, 62)
    # Chains hanging from ceiling. Lengths chosen so they NEVER cross any floor:
    # left zone (x<3130) chains can be longer (reach down to floor 4 at y=250);
    # right zone (x>3170) chains stop above floor 5 at y=160.
    for x, length in [(2520, 100), (2700, 170), (2880, 130), (3060, 180),
                      (3240, 80),  (3420, 90),  (3600, 75),  (3780, 85)]:
        pygame.draw.rect(screen, rope, apply_rect(pygame.Rect(x, 60, 3, length)))
        # Chain links along the rope
        for ly in range(78, 60 + length, 22):
            pygame.draw.rect(screen, chain, apply_rect(pygame.Rect(x - 2, ly, 7, 4)))
        # Hook/weight at the bottom
        pygame.draw.rect(screen, (90, 80, 65), apply_rect(pygame.Rect(x - 5, 60 + length - 4, 13, 7)))

    # Hanging broken moon-glow light fixtures — placed in OPEN gaps between floors
    # Floor 5 at y=160-190; Floor 4 at y=250-280; Floor 3 at y=380-410; Floor 2 at y=510-540.
    # Lights placed in gaps (200-250), (290-380), (420-510).
    for x, y in [(2620, 320), (2980, 460), (3340, 320), (3700, 220)]:
        pygame.draw.rect(screen, (62, 67, 82), apply_rect(pygame.Rect(x - 8, y - 18, 16, 18)))
        pygame.draw.rect(screen, (40, 45, 58), apply_rect(pygame.Rect(x - 5, y - 6, 10, 4)))
        pygame.draw.circle(screen, (110, 135, 165), apply_pos((x, y + 6)), 8)
        pygame.draw.circle(screen, (200, 230, 250), apply_pos((x, y + 6)), 3)

    # Floating moon-glow particles in non-floor zones
    glow_dot = (140, 200, 240)
    for px, py in [(2580, 350), (2820, 460), (3050, 430), (3280, 220),
                   (3500, 320), (3680, 100), (3820, 220)]:
        pygame.draw.rect(screen, glow_dot, apply_rect(pygame.Rect(px, py, 3, 3)))

    # Hanging banners — placed in left zone (long, reach down to floor 4 zone)
    banner_a = (95, 35, 45)
    banner_b = (50, 60, 95)
    for x, color in [(2750, banner_a), (2950, banner_b)]:
        pygame.draw.rect(screen, color, apply_rect(pygame.Rect(x, 60, 4, 130)))
        pygame.draw.polygon(screen, color, [
            apply_pos((x - 18, 180)), apply_pos((x + 22, 180)),
            apply_pos((x + 22, 230)), apply_pos((x + 5, 245)),
            apply_pos((x - 12, 235)), apply_pos((x - 18, 225)),
        ])

    wood = (62, 46, 32)
    wood_dark = (36, 26, 18)
    # Broken chair on ground floor
    pygame.draw.rect(screen, wood, apply_rect(pygame.Rect(2900, 632, 26, 18)))
    pygame.draw.rect(screen, wood, apply_rect(pygame.Rect(2900, 626, 26, 5)))
    pygame.draw.rect(screen, wood_dark, apply_rect(pygame.Rect(2922, 632, 4, 18)))
    # Smashed table with broken legs
    pygame.draw.rect(screen, wood, apply_rect(pygame.Rect(3200, 638, 84, 6)))
    pygame.draw.rect(screen, wood_dark, apply_rect(pygame.Rect(3200, 644, 6, 6)))
    pygame.draw.rect(screen, wood_dark, apply_rect(pygame.Rect(3278, 644, 6, 6)))
    pygame.draw.rect(screen, wood_dark, apply_rect(pygame.Rect(3220, 632, 4, 12)))    # broken leg sticking up
    # Bookshelf rubble with books
    book_a = (90, 50, 40)
    book_b = (50, 80, 90)
    pygame.draw.rect(screen, wood, apply_rect(pygame.Rect(3500, 615, 60, 35)))
    pygame.draw.rect(screen, book_a, apply_rect(pygame.Rect(3505, 620, 8, 16)))
    pygame.draw.rect(screen, book_b, apply_rect(pygame.Rect(3515, 622, 8, 14)))
    pygame.draw.rect(screen, book_a, apply_rect(pygame.Rect(3525, 619, 8, 17)))
    pygame.draw.rect(screen, book_b, apply_rect(pygame.Rect(3536, 621, 8, 15)))
    # Standing braziers (decorative torches on the floors and ground)
    for fx, fy in [(2550, 580), (3850, 580), (2700, 480), (3700, 350)]:
        pygame.draw.rect(screen, (50, 45, 35), apply_rect(pygame.Rect(fx, fy + 10, 14, 60)))   # stand
        pygame.draw.rect(screen, (60, 55, 40), apply_rect(pygame.Rect(fx - 4, fy, 22, 14)))    # bowl
        pygame.draw.circle(screen, (255, 160, 60), apply_pos((fx + 7, fy - 4)), 6)              # flame
        pygame.draw.circle(screen, (255, 220, 100), apply_pos((fx + 7, fy - 6)), 3)              # flame core
    # Floor stains (old blood)
    stain = (38, 26, 30)
    for x in [2700, 3050, 3450, 3780]:
        pygame.draw.ellipse(screen, stain, apply_rect(pygame.Rect(x, 643, 32, 6)))

def draw_map1_underground_background(screen, camera, game_map):
    """
    Underground/cavern background for Map 1 (boss arena or checkpoint).
    Dark stone walls, distant glowing crystals, no moon/sky.
    """
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Base dark cavern
    screen.fill((8, 10, 18))

    # Camera offset for parallax
    camera_x = 0
    if camera is not None:
        if hasattr(camera, "offset"):
            camera_x = camera.offset.x
        elif hasattr(camera, "x"):
            camera_x = camera.x
        elif hasattr(camera, "camera"):
            camera_x = camera.camera.x

    # Distant cave walls (parallax layers)
    far_wall = (18, 22, 38)
    mid_wall = (28, 32, 48)
    near_wall = (38, 42, 58)

    # Far layer — distant stalactites
    for i in range(12):
        x = (i * 220 - int(camera_x * 0.1)) % (screen_width + 400) - 200
        y = 20 + (i * 47) % 180
        h = 60 + (i * 23) % 100
        pygame.draw.polygon(screen, far_wall, [
            (x, y), (x + 30, y + h), (x - 30, y + h)
        ])

    # Mid layer — cave pillars
    for i in range(8):
        x = (i * 350 - int(camera_x * 0.25)) % (screen_width + 500) - 250
        w = 40 + (i * 11) % 50
        h = 200 + (i * 37) % 150
        rect = pygame.Rect(x, screen_height - h - 50, w, h)
        pygame.draw.rect(screen, mid_wall, rect)
        # Horizontal cracks
        for cy in range(rect.y + 40, rect.bottom - 40, 50):
            pygame.draw.rect(screen, (12, 15, 25), (rect.x + 5, cy, rect.width - 10, 3))

    # Near layer — rocky floor edge
    floor_rect = pygame.Rect(0, screen_height - 80, screen_width, 80)
    pygame.draw.rect(screen, near_wall, floor_rect)
    for fx in range(0, screen_width + 100, 40):
        fx_scroll = (fx - int(camera_x * 0.5)) % (screen_width + 100) - 50
        pygame.draw.rect(screen, (20, 24, 38), (fx_scroll, screen_height - 85, 20, 10))

    # Glowing crystals in background
    crystal_glow = (80, 180, 220)
    crystal_dark = (40, 90, 110)
    for i in range(15):
        x = (i * 280 - int(camera_x * 0.15)) % (screen_width + 600) - 300
        y = screen_height - 120 - (i * 17) % 80
        pygame.draw.polygon(screen, crystal_dark, [
            (x, y), (x + 12, y - 28), (x + 24, y)
        ])
        pygame.draw.polygon(screen, crystal_glow, [
            (x + 4, y - 6), (x + 12, y - 24), (x + 20, y - 6)
        ])
        # Glow aura
        glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (80, 180, 220, 40), (15, 15), 15)
        screen.blit(glow_surf, (x - 3, y - 20))

    # Light fog at bottom
    fog = pygame.Surface((screen_width, 100), pygame.SRCALPHA)
    fog.fill((20, 30, 50, 50))
    screen.blit(fog, (0, screen_height - 100))

def draw_section5_science_buildings(screen, camera):
    """
    Section 5 background buildings (x=5100-6400).
    Tall lab structures behind the platforms so they read as balconies/rooftops.
    """
    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect
    
    def apply_pos(pos):
        if camera is not None:
            return camera.apply_pos(pos)
        return pos

    building_main = (34, 42, 62)
    building_dark = (22, 28, 44)
    building_light = (52, 62, 82)
    window_light = (70, 160, 210)
    window_dark = (15, 25, 45)

    # Building 1 (x~5180-5380)
    b1_rect = pygame.Rect(5100, 350, 280, 300)
    pygame.draw.rect(screen, building_main, apply_rect(b1_rect))
    pygame.draw.rect(screen, building_dark, apply_rect(b1_rect), 3)
    # Windows
    for wx in range(b1_rect.x + 30, b1_rect.right - 40, 60):
        for wy in range(b1_rect.y + 40, b1_rect.bottom - 50, 50):
            pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx, wy, 35, 30)))
            pygame.draw.rect(screen, window_light, apply_rect(pygame.Rect(wx + 5, wy + 5, 10, 6)))

    # Building 2 (x~5400-5620) taller
    b2_rect = pygame.Rect(5380, 250, 240, 400)
    pygame.draw.rect(screen, building_light, apply_rect(b2_rect))
    pygame.draw.rect(screen, building_dark, apply_rect(b2_rect), 3)
    for wx in range(b2_rect.x + 25, b2_rect.right - 35, 55):
        for wy in range(b2_rect.y + 35, b2_rect.bottom - 60, 60):
            pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx, wy, 30, 28)))

    # Building 3 (x~5650-5820)
    b3_rect = pygame.Rect(5650, 380, 170, 270)
    pygame.draw.rect(screen, building_main, apply_rect(b3_rect))
    pygame.draw.rect(screen, building_dark, apply_rect(b3_rect), 2)

    # Building 4 (x~5840-6040) tall
    b4_rect = pygame.Rect(5840, 300, 200, 350)
    pygame.draw.rect(screen, building_dark, apply_rect(b4_rect))
    for wx in range(b4_rect.x + 20, b4_rect.right - 30, 50):
        pygame.draw.rect(screen, window_light, apply_rect(pygame.Rect(wx, b4_rect.y + 50, 20, 40)))

    # Building 5 (x~6060-6190)
    b5_rect = pygame.Rect(6060, 420, 130, 230)
    pygame.draw.rect(screen, building_main, apply_rect(b5_rect))

    # Chimney / antenna on top of building 4
    pygame.draw.rect(screen, building_light, apply_rect(pygame.Rect(5920, 260, 15, 50)))
    pygame.draw.circle(screen, window_light, apply_pos((5927, 255)), 5)

def draw_section6_courtyard_buildings(screen, camera):
    """
    Section 6 background (x=6400-7600) — combat courtyard.
    Arena walls and distant stands.
    """
    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    def apply_pos(pos):
        if camera is not None:
            return camera.apply_pos(pos)
        return pos

    arena_wall = (32, 38, 58)
    arena_wall_light = (52, 60, 80)
    arena_dark = (18, 22, 38)

    # Back wall of courtyard
    back_wall = pygame.Rect(6400, 400, 1200, 250)
    pygame.draw.rect(screen, arena_wall, apply_rect(back_wall))
    pygame.draw.rect(screen, arena_dark, apply_rect(back_wall), 4)

    # Upper decorative arches
    for ax in range(6450, 7550, 180):
        arch_rect = pygame.Rect(ax, 420, 80, 60)
        pygame.draw.rect(screen, arena_wall_light, apply_rect(arch_rect))
        pygame.draw.arc(screen, arena_dark, apply_rect(pygame.Rect(ax + 10, 420, 60, 50)), 0, 3.14, 3)

    # Distant spectator stands (top)
    stand_base = pygame.Rect(6500, 340, 1000, 80)
    pygame.draw.rect(screen, arena_wall_light, apply_rect(stand_base))
    for step in range(4):
        step_y = 340 + step * 15
        pygame.draw.rect(screen, arena_dark, apply_rect(pygame.Rect(6500, step_y, 1000, 3)))

    # Pillars flanking arena
    for px in [6450, 7550]:
        pillar = pygame.Rect(px, 420, 40, 230)
        pygame.draw.rect(screen, arena_wall_light, apply_rect(pillar))
        pygame.draw.rect(screen, arena_dark, apply_rect(pillar), 2)
        for py in range(450, 620, 40):
            pygame.draw.rect(screen, arena_dark, apply_rect(pygame.Rect(px + 5, py, 30, 8)))

def draw_section8_collapsed_city_background(screen, camera):
    """
    Section 8 background (x=8400-9500) — collapsed city / bridge area.
    Distant ruined skyscrapers and bridge supports.
    """
    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    def apply_pos(pos):
        if camera is not None:
            return camera.apply_pos(pos)
        return pos

    skyline_far = (22, 28, 48)
    skyline_mid = (32, 38, 58)
    skyline_near = (42, 48, 68)

    # Far distant skyscrapers
    for i, x in enumerate(range(8500, 9600, 180)):
        h = 180 + (i * 37) % 150
        w = 50 + (i * 13) % 40
        rect = pygame.Rect(x, 650 - h, w, h)
        pygame.draw.rect(screen, skyline_far, apply_rect(rect))
        # Windows
        for wy in range(rect.y + 20, rect.bottom - 20, 35):
            pygame.draw.rect(screen, (50, 70, 100), apply_rect(pygame.Rect(rect.x + 10, wy, 12, 20)))

    # Mid-distance ruined towers
    for i, x in enumerate(range(8700, 9400, 220)):
        h = 250 + (i * 43) % 180
        w = 70 + (i * 17) % 50
        rect = pygame.Rect(x, 650 - h, w, h)
        pygame.draw.rect(screen, skyline_mid, apply_rect(rect))
        pygame.draw.rect(screen, (15, 20, 35), apply_rect(rect), 2)
        # Broken top
        pygame.draw.polygon(screen, skyline_mid, [
            apply_pos((rect.x, rect.y)),
            apply_pos((rect.x + rect.width // 2, rect.y - 20)),
            apply_pos((rect.right, rect.y)),
        ])

    # Bridge support columns (massive)
    for bx in [8800, 9200]:
        column = pygame.Rect(bx, 480, 40, 170)
        pygame.draw.rect(screen, skyline_near, apply_rect(column))
        pygame.draw.rect(screen, (25, 30, 45), apply_rect(column), 3)
        # Cross beams
        pygame.draw.rect(screen, (50, 60, 80), apply_rect(pygame.Rect(bx - 10, 540, 60, 8)))
        pygame.draw.rect(screen, (50, 60, 80), apply_rect(pygame.Rect(bx - 10, 580, 60, 8)))

    # Hanging cables from bridge (broken)
    cable = (25, 30, 40)
    pygame.draw.line(screen, cable, apply_pos((8840, 480)), apply_pos((9000, 520)), 3)
    pygame.draw.line(screen, cable, apply_pos((9000, 520)), apply_pos((9160, 480)), 3)
    pygame.draw.line(screen, cable, apply_pos((9240, 480)), apply_pos((9400, 510)), 3)

    # Glowing emergency lights on bridge
    for lx in [8900, 9100, 9300]:
        pygame.draw.circle(screen, (200, 80, 40), apply_pos((lx, 475)), 4)
        pygame.draw.circle(screen, (255, 150, 80), apply_pos((lx, 475)), 2)


def draw_map3_train_station_background(screen, camera, game_map):
    """Indoor train-station checkpoint after MAP 2."""
    def apply_rect(rect):
        return camera.apply_rect(rect) if camera is not None else rect

    def apply_pos(pos):
        return camera.apply_pos(pos) if camera is not None else pos

    def rect(x, y, w, h, color):
        pygame.draw.rect(screen, color, apply_rect(pygame.Rect(x, y, w, h)))

    def line(start, end, color, width=2):
        pygame.draw.line(screen, color, apply_pos(start), apply_pos(end), width)

    bg = (3, 7, 13)
    wall_panel = (13, 19, 31)
    panel_dark = (7, 11, 20)
    beam = (43, 52, 70)
    cyan = (88, 214, 250)
    pale = (194, 235, 255)
    amber = (230, 176, 72)
    green = (96, 232, 155)
    violet = (123, 94, 255)

    screen.fill(bg)

    # Far station wall panels with deeper structural rhythm.
    for x in range(0, game_map.width, 170):
        rect(x + 8, 70, 142, 472, wall_panel)
        rect(x + 15, 82, 128, 13, panel_dark)
        rect(x + 16, 509, 126, 10, panel_dark)
        line((x + 30, 108), (x + 30, 498), (31, 39, 57), 3)
        line((x + 132, 108), (x + 132, 498), (31, 39, 57), 3)
        for y in range(146, 486, 78):
            line((x + 24, y), (x + 142, y), (24, 31, 47), 2)
        if (x // 170) % 2 == 0:
            line((x + 50, 120), (x + 118, 210), (19, 28, 44), 2)
            line((x + 118, 210), (x + 60, 302), (19, 28, 44), 2)

    # Ceiling ribs, rails, hanging clamps, and service cables.
    rect(0, 0, game_map.width, 82, (16, 15, 18))
    rect(0, 76, game_map.width, 10, beam)
    rect(0, 88, game_map.width, 6, (7, 10, 16))
    rect(0, 126, game_map.width, 8, (23, 31, 46))
    for x in range(52, game_map.width, 96):
        rect(x, 78, 6, 62, (52, 61, 79))
        rect(x - 5, 136, 16, 5, (29, 36, 50))
    for x in range(96, game_map.width, 200):
        line((x, 96), (x + 52, 164), (19, 28, 44), 2)
        line((x + 52, 164), (x + 104, 96), (19, 28, 44), 2)
    for x in range(180, game_map.width, 260):
        line((x, 136), (x + 80, 210), (12, 19, 32), 2)
        line((x + 80, 210), (x + 170, 132), (12, 19, 32), 2)

    # Arrival gate from the MAP 2 checkpoint.
    gate_x, gate_y = 92, 438
    glow = pygame.Surface((230, 210), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (56, 240, 165, 42), glow.get_rect())
    pygame.draw.ellipse(glow, (126, 92, 255, 34), glow.get_rect().inflate(-50, -24), 4)
    screen.blit(glow, apply_pos((gate_x - 46, gate_y - 86)))

    rect(gate_x, gate_y, 142, 174, (8, 14, 27))
    pygame.draw.rect(screen, (68, 84, 108), apply_rect(pygame.Rect(gate_x, gate_y, 142, 174)), 4)
    rect(gate_x + 15, gate_y + 25, 112, 129, (14, 30, 46))
    rect(gate_x + 34, gate_y + 43, 74, 92, (18, 90, 79))
    if DEBUG_DRAW_HITBOXES:
        pygame.draw.rect(screen, green, apply_rect(pygame.Rect(gate_x + 34, gate_y + 43, 74, 92)), 3)
    rect(gate_x + 64, gate_y + 54, 14, 70, violet)
    rect(gate_x + 48, gate_y + 38, 46, 4, pale)
    rect(gate_x + 48, gate_y + 132, 46, 4, pale)
    pygame.draw.rect(screen, (100, 242, 188), apply_rect(pygame.Rect(gate_x + 41, gate_y - 14, 60, 5)))
    pygame.draw.polygon(
        screen,
        (100, 242, 188),
        [apply_pos((gate_x + 42, gate_y - 10)), apply_pos((gate_x + 58, gate_y - 30)), apply_pos((gate_x + 74, gate_y - 10))],
    )
    pygame.draw.polygon(
        screen,
        (100, 242, 188),
        [apply_pos((gate_x + 68, gate_y - 10)), apply_pos((gate_x + 72, gate_y - 38)), apply_pos((gate_x + 94, gate_y - 10))],
    )
    rect(gate_x + 34, gate_y + 162, 74, 8, (94, 112, 138))

    # Distant train body with lit windows.
    rect(250, 350, 900, 184, (13, 20, 31))
    rect(250, 350, 900, 16, (54, 66, 88))
    rect(250, 518, 900, 15, (8, 13, 22))
    rect(250, 335, 900, 10, (7, 10, 17))
    for x in range(292, 1110, 92):
        rect(x, 392, 54, 54, (10, 29, 45))
        rect(x + 6, 398, 42, 42, (31, 86, 120))
        rect(x + 8, 400, 38, 8, cyan)

    # Lowered shop alcove. The real interactive shop is drawn by Shop.draw_shop_area on top.
    rect(502, 512, 262, 118, (21, 18, 22))
    pygame.draw.rect(screen, (100, 73, 52), apply_rect(pygame.Rect(502, 512, 262, 118)), 3)
    rect(520, 528, 226, 20, (55, 38, 25))
    sign_font = pygame.font.Font(None, 32)
    shop_text = sign_font.render("SHOP", True, (245, 226, 145))
    screen.blit(shop_text, shop_text.get_rect(center=apply_pos((633, 538))))
    for x in [528, 560, 704, 736]:
        rect(x, 596, 8, 40, (97, 70, 48))

    # Small stocked shelf silhouettes so the shop reads as usable.
    for x, color in [(536, cyan), (558, amber), (584, (178, 118, 190)), (713, green), (735, cyan)]:
        rect(x, 565, 12, 26, color)
    rect(530, 593, 220, 6, (78, 54, 36))

    # Moon altar alcove.
    rect(292, 505, 130, 112, (10, 16, 27))
    pygame.draw.rect(screen, (56, 72, 96), apply_rect(pygame.Rect(292, 505, 130, 112)), 2)
    rect(310, 598, 95, 10, (42, 50, 66))
    pygame.draw.circle(screen, (40, 118, 150), apply_pos((356, 538)), 32, 2)
    pygame.draw.circle(screen, (170, 225, 255), apply_pos((356, 538)), 11)


    # Subtle maintenance panels instead of giant train/route signage.
    rect(900, 110, 330, 48, (9, 17, 27))
    pygame.draw.rect(screen, (44, 64, 88), apply_rect(pygame.Rect(900, 110, 330, 48)), 2)
    for x in range(930, 1200, 70):
        rect(x, 130, 42, 5, cyan)
        rect(x + 5, 142, 24, 4, (74, 89, 118))

    rect(760, 205, 270, 74, (8, 15, 24))
    pygame.draw.rect(screen, (46, 62, 88), apply_rect(pygame.Rect(760, 205, 270, 74)), 2)
    for y in [228, 248, 268]:
        rect(786, y, 58, 4, cyan)
        rect(862, y, 125, 4, (74, 89, 118))

    # Benches, crates, lamps, and station clutter.
    rect(820, 548, 190, 30, (35, 28, 23))
    rect(836, 534, 158, 16, (94, 70, 48))
    rect(864, 578, 16, 44, (30, 24, 21))
    rect(950, 578, 16, 44, (30, 24, 21))
    rect(1048, 595, 48, 32, (62, 46, 34))
    rect(1102, 582, 66, 45, (78, 58, 39))
    rect(1114, 592, 42, 5, amber)
    rect(1214, 602, 36, 26, (35, 44, 62))
    rect(1256, 592, 52, 36, (46, 54, 72))
    for x in [278, 785, 1240, 1458]:
        rect(x, 510, 10, 112, (38, 46, 63))
        rect(x - 10, 500, 30, 10, amber)
        pygame.draw.circle(screen, (245, 205, 102), apply_pos((x + 5, 493)), 5)


    # Hidden emergency ladder hatch on the right side.
    rect(1366, 150, 82, 470, (4, 8, 14))
    pygame.draw.rect(screen, (39, 54, 76), apply_rect(pygame.Rect(1366, 150, 82, 470)), 3)
    rect(1376, 166, 62, 32, (13, 24, 36))
    pygame.draw.rect(screen, (78, 94, 126), apply_rect(pygame.Rect(1376, 166, 62, 32)), 2)
    rect(1388, 178, 28, 4, cyan)
    rect(1376, 603, 62, 12, (92, 102, 126))
    for rail_x in [1390, 1420]:
        line((rail_x, 205), (rail_x, 608), (86, 104, 134), 4)
    for y in range(225, 590, 28):
        line((1390, y), (1420, y), (126, 148, 178), 3)
    for x in range(1369, 1432, 20):
        rect(x, 626, 12, 5, amber)
    rect(1340, 524, 28, 68, (21, 31, 48))
    rect(1348, 538, 12, 4, cyan)
    rect(1348, 564, 12, 4, (245, 82, 120))

    # Rail bed and foreground depth under the checkpoint platform.
    rect(0, 660, game_map.width, 60, (4, 6, 10))
    for x in range(-20, game_map.width, 55):
        rect(x, 665, 34, 9, (48, 55, 70))
    line((0, 682), (game_map.width, 682), (84, 91, 108), 3)
    line((0, 704), (game_map.width, 704), (42, 48, 64), 3)


def draw_map3_emergency_ladder_exit(screen, camera, door, font):
    """MAP 3 exit: hidden emergency ladder into House of Intelligence."""
    rect = door["rect"]
    draw_rect = camera.apply_rect(rect) if camera is not None else rect.copy()
    cx = draw_rect.centerx
    top_y = draw_rect.top
    floor_y = draw_rect.bottom

    glow = pygame.Surface((150, 260), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (72, 224, 255, 28), glow.get_rect())
    screen.blit(glow, (cx - glow.get_width() // 2, top_y - 26))

    # Dark wall recess around the hidden route.
    recess = pygame.Rect(cx - 46, top_y - 10, 92, draw_rect.height + 18)
    pygame.draw.rect(screen, (4, 8, 14), recess)
    pygame.draw.rect(screen, (44, 58, 78), recess, 3)

    # Ladder rails and rungs.
    left_rail = cx - 20
    right_rail = cx + 20
    pygame.draw.line(screen, (92, 110, 138), (left_rail, top_y + 10), (left_rail, floor_y - 12), 4)
    pygame.draw.line(screen, (92, 110, 138), (right_rail, top_y + 10), (right_rail, floor_y - 12), 4)
    for y in range(top_y + 24, floor_y - 18, 24):
        pygame.draw.line(screen, (130, 150, 178), (left_rail, y), (right_rail, y), 3)

    # Half-open maintenance hatch at the top.
    hatch = pygame.Rect(cx - 54, top_y - 42, 108, 32)
    pygame.draw.rect(screen, (12, 18, 29), hatch)
    pygame.draw.rect(screen, (82, 96, 124), hatch, 2)
    pygame.draw.rect(screen, (72, 224, 255), (hatch.x + 12, hatch.y + 10, 34, 4))
    pygame.draw.rect(screen, (238, 178, 65), (hatch.right - 34, hatch.y + 8, 18, 16))

    # Warning stripes and small access sensor.
    for x in range(cx - 48, cx + 42, 20):
        pygame.draw.rect(screen, (238, 178, 65), (x, floor_y - 16, 12, 5))
    pygame.draw.rect(screen, (24, 34, 52), (cx - 66, floor_y - 88, 22, 52))
    pygame.draw.rect(screen, (72, 224, 255), (cx - 61, floor_y - 78, 12, 4))
    pygame.draw.rect(screen, (245, 82, 120), (cx - 61, floor_y - 58, 12, 4))

    label = font.render(door.get("label", "Emergency Route"), True, (190, 238, 255))
    screen.blit(label, label.get_rect(midbottom=(cx, top_y - 48)))


def draw_map4_intelligence_city_background(screen, camera, game_map):
    """Cyberpunk moon-city background for Level 3 / MAP 4. Collision still comes from Tiled."""
    def apply_rect(rect):
        return camera.apply_rect(rect) if camera is not None else rect

    def apply_pos(pos):
        return camera.apply_pos(pos) if camera is not None else pos

    def visible(x, y, w, h, pad=260):
        if camera is None:
            return True
        viewport = pygame.Rect(camera.x - pad, camera.y - pad, screen.get_width() + pad * 2, screen.get_height() + pad * 2)
        return viewport.colliderect(pygame.Rect(x, y, w, h))

    def rect(x, y, w, h, color):
        if visible(x, y, w, h):
            pygame.draw.rect(screen, color, apply_rect(pygame.Rect(x, y, w, h)))

    def line(start, end, color, width=2):
        x1, y1 = start
        x2, y2 = end
        if visible(min(x1, x2), min(y1, y2), abs(x2 - x1) + 1, abs(y2 - y1) + 1):
            pygame.draw.line(screen, color, apply_pos(start), apply_pos(end), width)

    def circle(pos, radius, color, width=0):
        x, y = pos
        if visible(x - radius, y - radius, radius * 2, radius * 2):
            pygame.draw.circle(screen, color, apply_pos(pos), radius, width)

    def glow(cx, cy, w, h, color):
        if not visible(cx - w // 2, cy - h // 2, w, h):
            return
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, color, surface.get_rect())
        screen.blit(surface, apply_pos((cx - w // 2, cy - h // 2)))

    screen.fill((3, 7, 14))

    # Storm sky and huge moon.
    for y in range(0, game_map.height, 90):
        rect(0, y, game_map.width, 45, (4 + y // 180, 9 + y // 220, 18 + y // 180))
    glow(13280, 190, 820, 520, (86, 162, 255, 38))
    circle((13280, 190), 170, (190, 210, 235), 0)
    circle((13280, 190), 174, (88, 150, 225), 5)
    for crater in [(13225, 150, 34), (13370, 230, 26), (13325, 100, 18), (13170, 230, 22)]:
        circle((crater[0], crater[1]), crater[2], (158, 176, 204), 0)

    # Rain streaks.
    for x in range(-80, game_map.width + 80, 72):
        offset = (x * 37) % 190
        for y in range(-60 + offset, game_map.height, 230):
            line((x, y), (x - 22, y + 62), (42, 86, 130), 2)

    # Distant layered skyline.
    for x in range(-120, game_map.width + 200, 260):
        h = 280 + ((x // 260) % 5) * 55
        base_y = game_map.height - 155
        rect(x, base_y - h, 180, h, (7, 14, 27))
        rect(x + 18, base_y - h - 36, 144, 36, (9, 17, 31))
        for wy in range(base_y - h + 35, base_y - 30, 58):
            rect(x + 28, wy, 18, 28, (13, 47, 75))
            rect(x + 82, wy + 10, 18, 28, (14, 35, 58))
            if (wy + x) % 3 == 0:
                rect(x + 132, wy, 16, 28, (98, 54, 160))

    # Section-flavored silhouettes. No section words on-screen.
    for sx in [250, 640]:
        rect(sx, 520, 95, 260, (13, 21, 34))
        rect(sx + 28, 465, 40, 55, (24, 38, 58))
        line((sx + 47, 430), (sx + 47, 465), (72, 224, 255), 4)
        circle((sx + 47, 426), 9, (72, 224, 255))

    for sx in range(1380, 2520, 210):
        rect(sx, 475, 72, 280, (9, 18, 32))
        for y in range(510, 720, 44):
            rect(sx + 18, y, 36, 8, (72, 224, 255))
        line((sx + 72, 500), (sx + 145, 450), (34, 54, 82), 3)

    for sx in [2860, 3260, 3740]:
        rect(sx, 430, 140, 330, (10, 18, 31))
        line((sx + 70, 330), (sx + 70, 430), (52, 70, 98), 5)
        circle((sx + 70, 318), 24, (72, 224, 255), 3)
        for dx in [-46, 46]:
            line((sx + 70, 360), (sx + 70 + dx, 392), (52, 70, 98), 3)

    for sx in [4480, 4940, 5320]:
        rect(sx, 350, 185, 420, (10, 18, 30))
        for y in range(390, 720, 44):
            rect(sx + 25, y, 135, 9, (38, 70, 100))
        glow(sx + 92, 545, 210, 420, (58, 220, 255, 20))
        line((sx - 40, 320), (sx + 230, 320), (45, 58, 82), 5)

    glow(6220, 500, 620, 420, (132, 90, 255, 26))
    for sx in range(5770, 6760, 180):
        rect(sx, 430, 110, 310, (9, 16, 30))
        rect(sx + 15, 460, 80, 12, (92, 230, 255))
        rect(sx + 15, 500, 80, 12, (110, 90, 210))

    for y in [435, 585, 735]:
        line((7000, y), (8550, y - 60), (74, 84, 108), 5)
        line((7000, y + 28), (8550, y - 32), (42, 50, 70), 5)
    for sx in [7100, 7600, 8150]:
        rect(sx, 470, 240, 72, (14, 22, 34))
        rect(sx + 24, 490, 48, 22, (70, 220, 255))
        rect(sx + 94, 490, 48, 22, (120, 80, 255))
        circle((sx + 35, 550), 12, (8, 12, 20))
        circle((sx + 200, 550), 12, (8, 12, 20))

    for sx in [8750, 9100, 9500]:
        rect(sx, 430, 230, 350, (9, 14, 25))
        for y in range(475, 720, 55):
            rect(sx + 35, y, 42, 32, (20, 34, 52))
            rect(sx + 140, y + 10, 42, 32, (20, 34, 52))
        circle((sx + 188, 405), 18, (110, 122, 160), 2)

    glow(10620, 485, 620, 700, (82, 150, 255, 24))
    rect(10120, 210, 680, 610, (8, 14, 27))
    rect(10320, 120, 280, 700, (12, 20, 38))
    for y in range(180, 760, 82):
        rect(10345, y, 230, 12, (64, 98, 138))
        circle((10620, y + 34), 16, (72, 224, 255), 2)
    line((10460, 80), (10460, 120), (120, 90, 255), 5)
    circle((10460, 72), 20, (120, 90, 255), 3)

    rect(11720, 250, 900, 520, (8, 13, 25))
    for x in range(11760, 12580, 88):
        for y in range(290, 710, 70):
            rect(x, y, 56, 38, (17, 34, 58))
            rect(x + 8, y + 8, 40, 8, (72, 224, 255))
    glow(12160, 515, 420, 280, (132, 84, 255, 34))
    circle((12160, 515), 82, (132, 84, 255), 3)
    circle((12160, 515), 18, (222, 235, 255))

    for sx in [13050, 13520, 14020]:
        rect(sx, 430, 160, 380, (8, 13, 24))
        line((sx + 80, 210), (sx + 80, 430), (70, 82, 112), 6)
        circle((sx + 80, 190), 44, (72, 224, 255), 3)
        line((sx + 80, 245), (sx + 15, 300), (70, 82, 112), 4)
        line((sx + 80, 245), (sx + 145, 300), (70, 82, 112), 4)
    for x in range(12900, game_map.width, 360):
        glow(x, 120, 140, 80, (255, 255, 255, 26))
        line((x, 95), (x - 90, 178), (164, 210, 255), 3)


_map2_background_cache = None


def draw_map2_pale_crown_background(screen, camera, game_map):
    """Draw the high-resolution Pale Crown Underfacility background for MAP 2."""
    global _map2_background_cache

    if _map2_background_cache is None:
        bg_path = Path(__file__).resolve().parents[2] / "assets" / "backgrounds" / "map2_pale_crown_underfacility.png"
        if bg_path.exists():
            _map2_background_cache = pygame.image.load(str(bg_path)).convert()
        else:
            _map2_background_cache = False

    if _map2_background_cache:
        src_x = 0
        src_y = 0
        if camera is not None:
            src_x = max(0, min(round(camera.x), _map2_background_cache.get_width() - screen.get_width()))
            src_y = max(0, min(round(camera.y), _map2_background_cache.get_height() - screen.get_height()))
        source = pygame.Rect(src_x, src_y, screen.get_width(), screen.get_height())
        screen.blit(_map2_background_cache, (0, 0), source)
        return

    screen.fill((4, 7, 14))



def draw_map2_section_story_details(screen, camera, game_map):
    """Decorative Pale Crown story dressing for MAP 2. No collision."""
    def apply_rect(rect):
        return camera.apply_rect(rect) if camera is not None else rect

    def apply_pos(pos):
        return camera.apply_pos(pos) if camera is not None else pos

    def visible(x, y, w, h, pad=220):
        if camera is None:
            return True
        viewport = pygame.Rect(camera.x - pad, camera.y - pad, screen.get_width() + pad * 2, screen.get_height() + pad * 2)
        return viewport.colliderect(pygame.Rect(x, y, w, h))

    def rect(x, y, w, h, color):
        if visible(x, y, w, h):
            pygame.draw.rect(screen, color, apply_rect(pygame.Rect(x, y, w, h)))

    def border(x, y, w, h, color, width=2):
        if visible(x, y, w, h):
            pygame.draw.rect(screen, color, apply_rect(pygame.Rect(x, y, w, h)), width)

    def line(start, end, color, width=2):
        x1, y1 = start
        x2, y2 = end
        if visible(min(x1, x2), min(y1, y2), abs(x2 - x1) + 1, abs(y2 - y1) + 1):
            pygame.draw.line(screen, color, apply_pos(start), apply_pos(end), width)

    def circle(pos, radius, color, width=0):
        x, y = pos
        if visible(x - radius, y - radius, radius * 2, radius * 2):
            pygame.draw.circle(screen, color, apply_pos(pos), radius, width)

    def glow(cx, cy, w, h, color):
        if not visible(cx - w // 2, cy - h // 2, w, h):
            return
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, color, surface.get_rect())
        screen.blit(surface, apply_pos((cx - w // 2, cy - h // 2)))

    def hanging_cable(x, y, length, color=(24, 34, 54)):
        line((x, y), (x, y + length), color, 3)
        for i in range(18, length, 26):
            rect(x - 6, y + i, 12, 4, (50, 60, 82))

    def warning_panel(x, y, color=(238, 178, 65)):
        rect(x, y, 34, 28, (18, 20, 28))
        border(x, y, 34, 28, color, 2)
        rect(x + 15, y + 6, 4, 12, color)
        rect(x + 15, y + 21, 4, 4, color)
        rect(x - 4, y + 31, 42, 4, (64, 72, 88))
        rect(x + 14, y + 35, 6, 34, (38, 46, 62))

    def barricade(x, y, color=(238, 178, 65)):
        rect(x, y, 118, 18, (34, 37, 48))
        border(x, y, 118, 18, color, 2)
        for sx in range(x + 10, x + 100, 28):
            rect(sx, y + 3, 12, 12, color)
            rect(sx + 10, y + 3, 10, 12, (54, 45, 38))
        rect(x + 12, y + 18, 8, 38, (42, 48, 62))
        rect(x + 96, y + 18, 8, 38, (42, 48, 62))

    def console(x, y, color=(75, 220, 255)):
        rect(x, y, 74, 52, (12, 18, 30))
        border(x, y, 74, 52, (62, 78, 104), 2)
        rect(x + 10, y + 10, 48, 12, color)
        rect(x + 10, y + 31, 18, 6, color)
        rect(x + 35, y + 31, 25, 6, (74, 92, 120))

    def glass_tank(x, y, w, h, liquid=(45, 190, 215), broken=False, body=True):
        rect(x, y, w, h, (7, 14, 25))
        border(x, y, w, h, (78, 104, 132), 3)
        rect(x + 8, y + 10, w - 16, h - 20, (13, 36, 52))
        rect(x + 12, y + h - 38, w - 24, 26, liquid)
        rect(x + 15, y + 18, w - 30, 5, (128, 236, 255))
        if body:
            circle((x + w // 2, y + h // 2 - 6), 16, (40, 70, 86))
            rect(x + w // 2 - 8, y + h // 2 + 10, 16, 32, (42, 60, 76))
        if broken:
            line((x + w - 28, y + 18), (x + w - 12, y + 42), (210, 232, 245), 2)
            line((x + w - 12, y + 42), (x + w - 35, y + 72), (210, 232, 245), 2)
            rect(x + w - 18, y + h + 4, 44, 5, liquid)

    def security_door(x, y, w=150, h=150, open_gap=False):
        rect(x, y, w, h, (18, 24, 36))
        border(x, y, w, h, (76, 88, 112), 3)
        gap_x = x + w // 2 - 18
        if open_gap:
            rect(gap_x, y + 10, 36, h - 20, (2, 6, 12))
        else:
            rect(x + w // 2 - 5, y + 10, 10, h - 20, (7, 10, 17))
        for yy in range(y + 22, y + h - 12, 28):
            rect(x + 16, yy, w - 32, 4, (54, 64, 84))
        rect(x + 12, y + 14, 22, 8, (238, 70, 70))
        rect(x + w - 34, y + 14, 22, 8, (238, 70, 70))

    def rail_track(x, y, w):
        line((x, y), (x + w, y), (84, 96, 116), 4)
        line((x, y + 30), (x + w, y + 30), (54, 64, 82), 4)
        for sx in range(x, x + w, 64):
            rect(sx, y - 7, 18, 46, (42, 48, 64))

    def sinkhole(x, y, w):
        rect(x, y, w, 118, (1, 3, 7))
        glow(x + w // 2, y + 58, w, 130, (76, 54, 120, 28))
        border(x + 16, y + 10, w - 32, 34, (28, 38, 58), 2)
        for sx in range(x + 30, x + w - 20, 74):
            rect(sx, y + 10, 34, 9, (72, 80, 98))
            rect(sx + 10, y + 23, 10, 28, (38, 45, 62))
        for sx in range(x + 45, x + w - 30, 132):
            line((sx, y + 24), (sx + 54, y + 72), (34, 42, 66), 2)
            line((sx + 54, y + 72), (sx + 95, y + 48), (34, 42, 66), 2)
        for sx in range(x + 70, x + w - 20, 190):
            rect(sx, y + 82, 40, 5, (86, 58, 120))
            rect(sx + 18, y + 68, 5, 20, (116, 84, 170))

    def experiment_altar(cx, floor_y):
        def poly(points, color, width=0):
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            if visible(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)):
                pygame.draw.polygon(screen, color, [apply_pos(p) for p in points], width)

        # One clear altar-chair silhouette: no tall side pillars or tank stacks.
        glow(cx, floor_y - 165, 560, 390, (132, 84, 255, 42))
        glow(cx - 18, floor_y - 218, 300, 250, (72, 196, 255, 26))

        # Circular lunar machine behind the restraint chair.
        circle((cx, floor_y - 230), 138, (18, 19, 34), 0)
        circle((cx, floor_y - 230), 138, (116, 96, 172), 4)
        circle((cx, floor_y - 230), 92, (44, 38, 72), 3)
        circle((cx, floor_y - 230), 38, (104, 214, 255), 2)
        circle((cx, floor_y - 230), 13, (225, 235, 255), 0)
        rect(cx - 7, floor_y - 379, 14, 34, (80, 88, 120))
        rect(cx - 30, floor_y - 350, 60, 8, (126, 116, 172))

        # Reclined experiment chair.
        poly(
            [
                (cx - 88, floor_y - 278),
                (cx + 50, floor_y - 250),
                (cx + 30, floor_y - 118),
                (cx - 118, floor_y - 145),
            ],
            (28, 27, 44),
        )
        poly(
            [
                (cx - 88, floor_y - 278),
                (cx + 50, floor_y - 250),
                (cx + 30, floor_y - 118),
                (cx - 118, floor_y - 145),
            ],
            (174, 152, 224),
            3,
        )
        poly(
            [
                (cx - 57, floor_y - 238),
                (cx + 12, floor_y - 224),
                (cx - 2, floor_y - 145),
                (cx - 75, floor_y - 160),
            ],
            (74, 64, 104),
        )
        rect(cx - 136, floor_y - 116, 272, 48, (31, 28, 44))
        border(cx - 136, floor_y - 116, 272, 48, (160, 132, 220), 3)
        rect(cx - 170, floor_y - 70, 340, 28, (42, 34, 58))
        border(cx - 170, floor_y - 70, 340, 28, (126, 96, 188), 2)
        rect(cx - 116, floor_y - 42, 232, 24, (22, 20, 32))
        rect(cx - 78, floor_y - 33, 156, 6, (88, 230, 255))

        # Head ring and body restraints.
        circle((cx - 50, floor_y - 260), 28, (23, 25, 38), 0)
        circle((cx - 50, floor_y - 260), 28, (188, 172, 236), 3)
        rect(cx - 87, floor_y - 264, 74, 8, (134, 124, 174))
        rect(cx - 136, floor_y - 136, 58, 12, (104, 114, 142))
        rect(cx + 78, floor_y - 136, 58, 12, (104, 114, 142))
        rect(cx - 128, floor_y - 88, 52, 10, (104, 114, 142))
        rect(cx + 76, floor_y - 88, 52, 10, (104, 114, 142))
        rect(cx - 145, floor_y - 130, 8, 56, (74, 86, 112))
        rect(cx + 137, floor_y - 130, 8, 56, (74, 86, 112))

        # Tubes and monitor arms feeding the chair, drawn diagonally so they do not read as pillars.
        tube_paths = [
            ((cx - 315, floor_y - 276), (cx - 106, floor_y - 194), (76, 58, 122), 5),
            ((cx - 286, floor_y - 88), (cx - 83, floor_y - 108), (52, 220, 235), 3),
            ((cx + 318, floor_y - 270), (cx + 94, floor_y - 190), (76, 58, 122), 5),
            ((cx + 280, floor_y - 74), (cx + 86, floor_y - 105), (52, 220, 235), 3),
            ((cx - 10, floor_y - 388), (cx - 45, floor_y - 285), (112, 92, 180), 4),
        ]
        for start, end, color, width in tube_paths:
            line(start, end, color, width)
            circle(start, 6, color, 0)
            circle(end, 5, color, 0)

        # Low machinery beside the chair. These stay below the altar line, not as pillars.
        rect(cx - 332, floor_y - 106, 92, 54, (10, 16, 28))
        border(cx - 332, floor_y - 106, 92, 54, (76, 88, 124), 2)
        rect(cx - 318, floor_y - 92, 50, 8, (92, 230, 255))
        rect(cx - 318, floor_y - 72, 30, 7, (146, 104, 255))
        rect(cx + 238, floor_y - 108, 102, 58, (10, 16, 28))
        border(cx + 238, floor_y - 108, 102, 58, (76, 88, 124), 2)
        rect(cx + 256, floor_y - 92, 54, 8, (92, 230, 255))
        rect(cx + 256, floor_y - 72, 36, 7, (146, 104, 255))
        for sx in [cx - 114, cx + 114]:
            line((sx, floor_y - 68), (sx, floor_y - 22), (58, 66, 90), 4)
            rect(sx - 18, floor_y - 22, 36, 8, (82, 94, 120))

    # Section dividers only: visual architecture, no text.
    for x in [1050, 2100, 3300, 4600, 5600, 6700, 7900, 9100, 10300]:
        line((x, 40), (x, game_map.height - 80), (28, 38, 58), 2)
        for y in range(80, game_map.height - 90, 90):
            rect(x - 3, y, 6, 28, (44, 58, 84))

    # Bottom abyss treatment. Falling past the map bottom is death.
    for x, w in [(260, 760), (1320, 820), (3180, 780), (4580, 920), (6460, 920), (8780, 980), (10420, 800)]:
        sinkhole(x, game_map.height - 128, w)

    # Upper facility entrance.
    rect(80, 230, 350, 240, (9, 16, 28))
    border(80, 230, 350, 240, (50, 72, 98), 3)
    rect(120, 270, 88, 126, (14, 34, 52))
    rect(140, 296, 48, 72, (42, 144, 176))
    rect(238, 274, 120, 22, (64, 224, 255))
    rect(238, 315, 156, 8, (70, 88, 116))
    rect(238, 344, 120, 8, (70, 88, 116))
    console(520, 392)
    for x in [690, 820, 940]:
        hanging_cable(x, 110, 145)
    glow(190, 334, 180, 170, (70, 225, 255, 28))

    # Broken maintenance route.
    for x, y in [(1230, 420), (1440, 500), (1680, 365), (1880, 620)]:
        rect(x, y, 210, 20, (55, 64, 82))
        rect(x, y - 6, 210, 5, (140, 156, 184))
        barricade(x + 28, y - 40)
        for tx in range(x + 12, x + 200, 48):
            rect(tx, y + 18, 12, 45, (35, 43, 62))
    for x in [1140, 1320, 1550, 1840, 2010]:
        hanging_cable(x, 105, 230, (35, 43, 63))
    for sx, sy in [(1540, 330), (1798, 520), (1970, 255)]:
        rect(sx, sy, 9, 9, (255, 216, 98))
        rect(sx + 18, sy + 14, 6, 6, (255, 92, 60))
    line((1210, 260), (2050, 560), (31, 43, 65), 2)

    # Specimen storage.
    for i, x in enumerate([2220, 2440, 2660, 2900]):
        glass_tank(x, 270 + (i % 2) * 60, 118, 220, liquid=(44, 196, 222), broken=(i == 2), body=True)
        console(x + 10, 530 + (i % 2) * 55, (104, 98, 255))
    rect(2140, 220, 980, 36, (15, 25, 40))
    border(2140, 220, 980, 36, (78, 104, 132), 2)
    for x in range(2180, 3100, 105):
        rect(x, 231, 44, 6, (75, 230, 255))
    glow(2700, 410, 780, 520, (68, 212, 255, 18))
    rect(3060, 560, 74, 24, (45, 17, 25))
    rect(3080, 550, 28, 9, (205, 70, 78))

    # Reactor shaft.
    glow(3920, 530, 520, 900, (74, 202, 255, 25))
    for radius, color in [(180, (48, 78, 108)), (135, (42, 120, 156)), (86, (110, 232, 255)), (42, (220, 250, 255))]:
        if visible(3700, 300, 470, 470):
            pygame.draw.circle(screen, color, apply_pos((3920, 550)), radius, 5 if radius > 50 else 0)
    for y in range(180, 1180, 105):
        rect(3670, y, 38, 60, (38, 48, 70))
        rect(4125, y + 35, 38, 60, (38, 48, 70))
        line((3708, y + 28), (3920, y + 72), (36, 73, 98), 3)
        line((4125, y + 62), (3920, y + 20), (36, 73, 98), 3)
    for x in [3410, 4320]:
        for y in range(210, 1240, 62):
            rect(x, y, 28, 44, (40, 48, 66))
    rect(3810, 930, 220, 96, (9, 18, 29))
    border(3810, 930, 220, 96, (80, 200, 245), 2)
    rect(3840, 956, 160, 10, (86, 235, 255))
    rect(3840, 985, 118, 10, (255, 210, 88))

    # Security lockdown.
    security_door(4700, 338, 170, 230, open_gap=True)
    security_door(5320, 300, 170, 260, open_gap=False)
    for x in [4860, 5010, 5180, 5480]:
        rect(x, 610, 70, 58, (42, 36, 36))
        warning_panel(x + 18, 570, (255, 92, 72))
    for x, y in [(4850, 210), (5235, 180), (5500, 430)]:
        glow(x, y, 86, 86, (255, 50, 50, 40))
        circle((x, y), 12, (255, 74, 74))
        line((x - 28, y), (x - 12, y), (255, 74, 74), 3)
        line((x + 12, y), (x + 28, y), (255, 74, 74), 3)
    rect(4960, 730, 360, 46, (11, 15, 24))
    border(4960, 730, 360, 46, (255, 70, 70), 2)
    for sx in range(5000, 5300, 72):
        rect(sx, 746, 38, 8, (255, 70, 70))

    # Flooded sector.
    for x in range(5660, 6650, 190):
        rect(x, 825, 150, 12, (58, 230, 190))
        glow(x + 75, 842, 210, 60, (48, 220, 180, 32))
    for x in [5740, 5950, 6310, 6560]:
        line((x, 180), (x, 690), (42, 62, 82), 9)
        rect(x - 26, 265, 52, 14, (64, 82, 104))
        for y in range(360, 650, 90):
            circle((x + 20, y), 5, (76, 226, 208))
            line((x + 14, y + 8), (x - 24, y + 48), (76, 226, 208), 2)
    rect(5860, 1010, 540, 96, (5, 24, 29))
    border(5860, 1010, 540, 96, (64, 214, 188), 2)
    for x in range(5900, 6380, 90):
        circle((x, 1058), 14, (33, 114, 120), 2)
    glass_tank(6410, 890, 150, 230, liquid=(72, 230, 190), broken=True, body=False)

    # Memory archive.
    for x in [6820, 7020, 7220, 7420, 7620]:
        rect(x, 290, 118, 320, (8, 15, 28))
        border(x, 290, 118, 320, (58, 84, 120), 2)
        for y in range(315, 570, 38):
            rect(x + 18, y, 82, 8, (52, 128, 200))
            rect(x + 18, y + 14, 42, 5, (98, 235, 255))
    for x, y in [(6950, 735), (7260, 820), (7600, 700)]:
        rect(x, y, 210, 94, (10, 20, 35))
        border(x, y, 210, 94, (98, 148, 255), 2)
        rect(x + 22, y + 24, 160, 8, (102, 235, 255))
        rect(x + 22, y + 48, 114, 8, (86, 112, 154))
    glow(7350, 520, 820, 580, (78, 128, 255, 18))

    # Transit rails.
    for y in [520, 815, 1090]:
        rail_track(8000, y, 1020)
    for x in [8130, 8420, 8730, 9010]:
        rect(x, 470, 98, 56, (35, 38, 48))
        rect(x + 12, 456, 74, 16, (78, 88, 112))
        circle((x + 22, 530), 10, (18, 22, 32))
        circle((x + 76, 530), 10, (18, 22, 32))
    for x in range(8050, 9100, 150):
        rect(x, 260, 54, 110, (12, 20, 32))
        rect(x + 10, 278, 34, 18, (255, 205, 76))
        rect(x + 10, 314, 34, 18, (70, 220, 255))
    line((7980, 402), (9100, 290), (46, 60, 86), 4)
    line((7980, 1180), (9100, 970), (46, 60, 86), 4)

    # Quiet descent.
    for x, y in [(9240, 392), (9460, 760), (9820, 536), (10120, 930)]:
        glow(x, y, 180, 180, (166, 168, 255, 28))
        circle((x, y), 26, (74, 82, 118), 2)
        circle((x + 5, y - 4), 9, (208, 220, 255))
        rect(x - 2, y + 32, 4, 78, (70, 78, 112))
    for x in range(9250, 10220, 145):
        circle((x, 210 + (x // 9) % 320), 3, (160, 190, 255))
    line((9280, 250), (10180, 740), (30, 40, 65), 2)
    line((9280, 1030), (10180, 610), (30, 40, 65), 2)
    rect(9480, 1160, 530, 42, (8, 13, 22))
    border(9480, 1160, 530, 42, (116, 122, 190), 2)

    # Experiment core.
    glow(10940, 610, 620, 650, (132, 84, 255, 34))
    rect(10430, 300, 630, 440, (9, 13, 25))
    border(10430, 300, 630, 440, (102, 82, 150), 3)

    # Broken containment remains, kept low so they do not look like pillars.
    rect(10488, 458, 210, 74, (10, 18, 30))
    border(10488, 458, 210, 74, (80, 88, 120), 2)
    rect(10512, 474, 146, 12, (72, 220, 245))
    rect(10526, 506, 102, 8, (118, 90, 245))
    line((10644, 458), (10682, 424), (160, 190, 220), 2)
    line((10682, 424), (10706, 452), (160, 190, 220), 2)

    experiment_altar(10845, 560)

    # Wall conduits and signal beams feeding the altar.
    for start, end, color, width in [
        ((10482, 368), (10708, 430), (54, 44, 86), 4),
        ((10496, 642), (10732, 506), (42, 70, 98), 3),
        ((11194, 366), (10962, 430), (54, 44, 86), 4),
        ((11238, 636), (10964, 504), (42, 70, 98), 3),
        ((10844, 304), (10844, 380), (108, 92, 174), 3),
    ]:
        line(start, end, color, width)
        circle(start, 5, color, 0)

    # Small consoles, warning beacons, and observation glass.
    for x, y in [(10688, 604), (11078, 610)]:
        console(x, y, (146, 104, 255))
    rect(10935, 690, 160, 34, (42, 18, 34))
    rect(10980, 676, 62, 8, (218, 74, 115))
    for x, y, color in [(10578, 384, (92, 230, 255)), (11186, 390, (255, 80, 95)), (11092, 502, (138, 104, 255))]:
        glow(x, y, 86, 70, color + (32,))
        rect(x - 20, y - 6, 40, 12, color)
        rect(x - 5, y + 10, 10, 18, (52, 60, 82))
    rect(11264, 332, 112, 258, (8, 14, 26))
    border(11264, 332, 112, 258, (114, 96, 172), 3)
    rect(11286, 356, 68, 178, (34, 26, 70))
    rect(11298, 378, 44, 120, (118, 90, 245))
    glow(11320, 448, 170, 330, (132, 84, 255, 28))


def draw_map5_fighter_trash_checkpoint_background(screen, camera, game_map):
    """The Scrap Trenches: Kael falls from Intelligence into Fighter-house waste."""
    screen.fill((3, 6, 10))

    def rect(x, y, w, h, color, width=0):
        r = pygame.Rect(x, y, w, h)
        if camera is not None:
            r = camera.apply_rect(r)
        pygame.draw.rect(screen, color, r, width)
        return r

    def line(a, b, color, width=2):
        if camera is not None:
            a = camera.apply_pos(a)
            b = camera.apply_pos(b)
        pygame.draw.line(screen, color, a, b, width)

    def circle(x, y, radius, color, width=0):
        pos = (x, y)
        if camera is not None:
            pos = camera.apply_pos(pos)
        pygame.draw.circle(screen, color, pos, radius, width)

    def polygon(points, color, width=0):
        draw_points = [camera.apply_pos(point) for point in points] if camera is not None else points
        pygame.draw.polygon(screen, color, draw_points, width)

    wall = (9, 13, 21)
    deep = (1, 3, 7)
    rib = (24, 32, 46)
    metal = (54, 63, 79)
    glow = (74, 211, 245)
    violet = (118, 87, 255)
    warning = (232, 174, 58)
    rust = (119, 72, 39)

    rect(0, 0, game_map.width, game_map.height, deep)
    rect(0, 64, game_map.width, 596, wall)

    # Broken overhead conveyor with the open fall hole.
    rect(0, 42, 132, 44, (34, 41, 57))
    rect(372, 42, game_map.width - 372, 44, (34, 41, 57))
    rect(132, 38, 48, 12, metal)
    rect(324, 38, 48, 12, metal)
    rect(142, 49, 24, 22, (18, 22, 32))
    rect(338, 49, 24, 22, (18, 22, 32))
    for x in list(range(20, 120, 70)) + list(range(390, game_map.width, 70)):
        rect(x, 82, 24, 14, (15, 20, 31))
    for x in list(range(55, 126, 170)) + list(range(430, game_map.width, 170)):
        rect(x, 54, 34, 5, glow)

    # Gigantic vertical abyss shaft in the middle.
    rect(490, 86, 520, 568, (2, 5, 11))
    rect(500, 94, 500, 554, (9, 13, 22), 4)
    for x in [530, 640, 755, 872, 970]:
        rect(x, 106, 8, 520, (18, 26, 39))
        for y in range(144, 620, 82):
            rect(x - 20, y, 48, 5, (44, 55, 75))
    # Depth bands inside the shaft.
    for y in [134, 228, 322, 416, 510, 604]:
        rect(512, y, 476, 4, (12, 20, 32))
    # Falling cables.
    for a, b in [
        ((560, 90), (505, 295)), ((612, 86), (692, 310)),
        ((760, 86), (705, 455)), ((840, 88), (938, 520)),
        ((970, 90), (892, 370)), ((520, 310), (622, 650)),
    ]:
        line(a, b, (36, 63, 91), 3)
        line((a[0] + 4, a[1] + 12), (b[0] + 4, b[1] - 12), (13, 21, 34), 2)

    # Broken hologram screens falling through the abyss.
    for x, y, w, h, color in [
        (552, 160, 92, 46, glow), (722, 238, 120, 56, violet),
        (862, 148, 96, 40, glow), (580, 396, 104, 48, violet),
        (828, 462, 118, 54, glow),
    ]:
        rect(x, y, w, h, (7, 13, 23))
        rect(x + 6, y + 7, w - 12, h - 14, (18, 34, 52))
        rect(x + 16, y + h // 2 - 2, w - 32, 4, color)
        rect(x, y, w, h, color, 2)

    # Falling scraps and dust.
    for x, y in [
        (182, 92), (214, 136), (280, 116), (324, 168), (248, 206),
        (548, 260), (642, 342), (778, 184), (908, 382), (966, 246),
    ]:
        rect(x, y, 8, 8, (91, 83, 70))
    for x, y, c in [(604, 210, glow), (936, 318, glow), (706, 502, warning), (864, 564, violet)]:
        rect(x, y, 12, 5, c)

    # Left landing trash pile: broken fighter equipment.
    rect(56, 622, 460, 28, (48, 35, 28))
    rect(78, 593, 382, 42, (78, 55, 37))
    rect(122, 565, 286, 38, (100, 69, 42))
    rect(184, 544, 172, 30, (129, 88, 48))
    for x, y, w, h in [
        (105, 576, 86, 14), (228, 536, 48, 18), (324, 566, 96, 12),
        (154, 610, 36, 12), (365, 602, 76, 14), (78, 607, 46, 16),
    ]:
        rect(x, y, w, h, rust)
    for x, y in [(150, 550), (326, 548), (407, 592), (242, 604)]:
        circle(x, y, 15, (74, 83, 102), 3)
        line((x - 9, y), (x + 9, y), (98, 110, 132), 2)
    for x in [120, 206, 288, 378]:
        line((x, 535), (x + 54, 606), (102, 78, 58), 4)
        rect(x + 49, 600, 16, 10, (146, 106, 58))

    # Scrap trench floor, pipes, and low haze.
    rect(0, 650, game_map.width, 70, (41, 47, 62))
    rect(0, 650, game_map.width, 7, (185, 190, 207))
    for x in range(22, game_map.width, 145):
        rect(x, 667, 46, 4, (24, 28, 38))
        line((x + 70, 652), (x + 94, 681), (16, 19, 29), 3)
    for x in range(0, game_map.width, 58):
        rect(x + 15, 706, 14, 14, (24, 28, 39))

    # Right-side walk-out breach toward MAP 6: no E-door, just move right.
    rect(1104, 486, 360, 154, (30, 43, 39))
    rect(1124, 506, 284, 112, (13, 21, 21))
    rect(1138, 526, 82, 70, (26, 42, 35))
    rect(1236, 520, 76, 76, (22, 34, 32))
    rect(1422, 478, 78, 172, (2, 5, 8))
    rect(1410, 478, 12, 172, (70, 78, 92))
    rect(1396, 632, 82, 18, (96, 70, 48))
    for x in [1136, 1218, 1300, 1380]:
        rect(x, 474, 38, 12, warning)
    line((1104, 486), (1064, 444), (79, 87, 101), 4)
    line((1416, 486), (1462, 444), (79, 87, 101), 4)
    line((1436, 510), (1478, 545), (40, 48, 62), 4)
    line((1430, 610), (1474, 584), (40, 48, 62), 4)

    sign_font = pygame.font.SysFont("consolas", 18, bold=True)
    sign_box = pygame.Rect(1134, 452, 292, 36)
    draw_sign_box = camera.apply_rect(sign_box) if camera is not None else sign_box
    pygame.draw.rect(screen, (8, 14, 22), draw_sign_box)
    pygame.draw.rect(screen, (93, 222, 246), draw_sign_box, 2)
    sign_text = sign_font.render("MOVE RIGHT  ->  LEAVE DUMPSTER", True, (200, 244, 255))
    screen.blit(sign_text, sign_text.get_rect(center=draw_sign_box.center))

    # Icon lamps / hazard markers.
    for x in [70, 472, 1020, 1430]:
        rect(x, 530, 10, 92, (38, 45, 58))
        rect(x - 16, 520, 42, 12, warning)
        circle(x + 5, 518, 6, warning)

    fog = pygame.Surface((game_map.width, 124), pygame.SRCALPHA)
    fog.fill((33, 45, 58, 54))
    if camera is not None:
        screen.blit(fog, camera.apply_pos((0, 536)))
    else:
        screen.blit(fog, (0, 536))


def draw_map5_fighter_trash_foreground(screen, camera):
    """Foreground scraps in front of the landing pile and dumpster exit."""
    def rect(x, y, w, h, color, width=0):
        r = pygame.Rect(x, y, w, h)
        if camera is not None:
            r = camera.apply_rect(r)
        pygame.draw.rect(screen, color, r, width)

    def line(a, b, color, width=2):
        if camera is not None:
            a = camera.apply_pos(a)
            b = camera.apply_pos(b)
        pygame.draw.line(screen, color, a, b, width)

    for x in [108, 172, 246, 318, 426, 720, 892, 1128, 1194, 1365]:
        rect(x, 635, 46, 10, (34, 24, 20))
    line((96, 586), (190, 642), (132, 91, 49), 5)
    line((392, 560), (286, 642), (132, 91, 49), 5)
    line((1178, 596), (1264, 646), (91, 73, 55), 5)
    line((1344, 588), (1276, 646), (91, 73, 55), 5)
    rect(210, 622, 92, 10, (157, 117, 63))
    rect(218, 612, 22, 10, (96, 103, 119))
    rect(272, 612, 22, 10, (96, 103, 119))
    rect(1232, 614, 128, 12, (91, 68, 49))
    rect(1264, 595, 28, 22, (103, 111, 128))


def draw_map5_broken_dumpster_exit(screen, camera, door, font):
    """Small interactive shimmer on the broken dumpster passage."""
    rect = camera.apply_rect(door["rect"]) if camera is not None else door["rect"].copy()
    glow = pygame.Surface((rect.width + 70, rect.height + 60), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (60, 235, 165, 32), glow.get_rect())
    screen.blit(glow, (rect.centerx - glow.get_width() // 2, rect.centery - glow.get_height() // 2))
    pygame.draw.rect(screen, (5, 10, 12), rect)
    pygame.draw.rect(screen, (71, 225, 158), rect, 3)
    pygame.draw.rect(screen, (104, 83, 245), (rect.centerx - 9, rect.y + 18, 18, rect.height - 36))


def draw_map6_military_background(screen, camera, game_map):
    """Level 4: House of Military fallback background until map6 is drawn in Tiled."""
    screen.fill((5, 7, 11))

    def rect(x, y, w, h, color, width=0):
        r = pygame.Rect(x, y, w, h)
        if camera is not None:
            r = camera.apply_rect(r)
        pygame.draw.rect(screen, color, r, width)

    def line(a, b, color, width=2):
        if camera is not None:
            a = camera.apply_pos(a)
            b = camera.apply_pos(b)
        pygame.draw.line(screen, color, a, b, width)

    def circle(x, y, radius, color, width=0):
        pos = (x, y)
        if camera is not None:
            pos = camera.apply_pos(pos)
        pygame.draw.circle(screen, color, pos, radius, width)

    sky = (5, 8, 13)
    wall = (11, 15, 23)
    steel = (42, 49, 65)
    dark_steel = (22, 27, 39)
    red = (235, 58, 58)
    amber = (236, 169, 64)
    cyan = (76, 213, 244)

    rect(0, 0, game_map.width, game_map.height, sky)
    rect(0, 72, game_map.width, game_map.height - 72, wall)

    for x in range(0, game_map.width, 360):
        rect(x + 40, 108, 160, 760, (9, 13, 22))
        rect(x + 70, 180, 100, 8, steel)
        rect(x + 70, 360, 100, 8, steel)
        rect(x + 70, 540, 100, 8, steel)
        rect(x + 70, 720, 100, 8, steel)
        if x % 720 == 0:
            rect(x + 132, 126, 10, 630, (30, 39, 58))

    # Section divider ribs from the design plan.
    for x in [1400, 2800, 4200, 5700, 7000, 8300, 9300, 10600, 11400]:
        line((x, 70), (x, game_map.height - 70), (38, 45, 63), 3)
        for y in range(110, game_map.height - 100, 86):
            rect(x - 6, y, 12, 34, (65, 75, 98))

    # Scrap graveyard start.
    for x, y, w, h in [
        (120, 790, 360, 54), (280, 746, 220, 48), (620, 800, 280, 42),
        (760, 744, 170, 50), (1030, 804, 240, 40),
    ]:
        rect(x, y, w, h, (63, 45, 35))
        rect(x + 18, y + 10, w - 36, 8, (112, 77, 43))
    for x, y in [(420, 750), (730, 790), (1180, 820)]:
        circle(x, y, 34, (64, 72, 89), 5)
        circle(x, y, 16, (24, 30, 42))

    # War-street barricades and sniper towers.
    for x in [1550, 2020, 2460, 9560, 10100]:
        rect(x, 790, 120, 54, dark_steel)
        rect(x - 18, 782, 156, 12, amber)
        for i in range(4):
            line((x - 12 + i * 38, 794), (x + 12 + i * 38, 840), (20, 24, 32), 4)
    for x in [3200, 3900, 10880]:
        rect(x, 610, 46, 250, dark_steel)
        rect(x - 38, 600, 122, 24, steel)
        circle(x + 23, 590, 7, red)

    # Wall sector, artillery bridge, and bunker silhouettes.
    rect(4300, 150, 520, 730, (18, 24, 36))
    rect(4520, 210, 80, 610, (50, 58, 78))
    for y in range(240, 790, 70):
        rect(4340, y, 440, 8, (74, 84, 106))
    for x in range(5700, 7000, 170):
        rect(x, 470, 120, 20, steel)
        rect(x + 18, 490, 14, 82, dark_steel)
        circle(x + 60, 438, 9, red)
    rect(8460, 520, 620, 360, (17, 20, 29))
    rect(8620, 610, 300, 140, (8, 12, 18))
    rect(8570, 590, 410, 28, (74, 83, 101))
    for x in [8640, 8740, 8840]:
        circle(x, 576, 8, red)

    # Mech disposal silhouettes.
    rect(7180, 680, 420, 120, (16, 22, 31))
    circle(7240, 656, 42, (36, 44, 58), 5)
    circle(7570, 654, 50, (36, 44, 58), 5)
    line((7320, 690), (7440, 585), (51, 61, 78), 8)
    line((7480, 702), (7690, 606), (51, 61, 78), 8)
    for x in [7060, 7780, 8120]:
        line((x, 130), (x - 80, 610), (35, 46, 66), 3)

    # Exodus rail station at the far end.
    rect(11480, 590, 410, 170, (16, 22, 32))
    rect(11520, 620, 320, 50, (24, 32, 47))
    rect(11540, 636, 54, 22, cyan)
    rect(11630, 636, 54, 22, cyan)
    rect(11720, 636, 54, 22, cyan)
    rect(11420, 828, 520, 16, (76, 84, 101))

    # Rain, ash, and warning lamps.
    for x in range(100, game_map.width, 260):
        line((x, 96), (x - 26, 178), (34, 79, 116), 2)
    for x in range(180, game_map.width, 640):
        circle(x, 116, 5, red)
        rect(x - 2, 122, 4, 34, (82, 38, 44))
    for x in range(260, game_map.width, 520):
        rect(x, 844, 36, 5, cyan)


def draw_map7_architecture_checkpoint_background(screen, camera, game_map):
    """Checkpoint after MAP 6: an underground service tunnel opening into House of Architecture."""
    def apply_rect(rect):
        return camera.apply_rect(rect) if camera is not None else rect

    def apply_pos(pos):
        return camera.apply_pos(pos) if camera is not None else pos

    def rect(x, y, w, h, color, width=0):
        pygame.draw.rect(screen, color, apply_rect(pygame.Rect(x, y, w, h)), width)

    def line(a, b, color, width=2):
        pygame.draw.line(screen, color, apply_pos(a), apply_pos(b), width)

    def circle(x, y, radius, color, width=0):
        pygame.draw.circle(screen, color, apply_pos((x, y)), radius, width)

    bg = (4, 7, 12)
    tunnel = (12, 17, 25)
    tunnel_dark = (5, 9, 15)
    steel = (52, 62, 82)
    stone = (68, 74, 92)
    stone_light = (178, 184, 205)
    cyan = (75, 216, 250)
    gold = (226, 184, 82)
    teal = (94, 236, 190)
    violet = (128, 96, 255)

    screen.fill(bg)

    # Left side: low military drainage tunnel from Level 4.
    rect(0, 392, 610, 258, tunnel_dark)
    rect(0, 392, 610, 18, (34, 43, 60))
    rect(0, 626, 610, 24, (42, 49, 66))
    for x in range(20, 600, 86):
        rect(x, 410, 14, 216, (22, 30, 44))
        for y in range(438, 610, 52):
            rect(x - 8, y, 30, 5, steel)
    for x in range(46, 570, 96):
        line((x, 420), (x + 56, 472), (20, 31, 48), 2)
        rect(x + 12, 616, 34, 5, cyan)
    for x in range(115, 545, 130):
        rect(x, 474, 82, 10, steel)
        rect(x + 12, 486, 52, 5, (20, 26, 38))

    # The tunnel mouth where the military concrete gives way to architecture stone.
    rect(560, 360, 150, 290, (9, 13, 20))
    pygame.draw.arc(screen, stone_light, apply_rect(pygame.Rect(548, 335, 174, 190)), 3.14, 6.28, 6)
    pygame.draw.arc(screen, stone, apply_rect(pygame.Rect(566, 355, 138, 156)), 3.14, 6.28, 5)
    rect(584, 474, 98, 152, (5, 9, 14))
    for y in range(388, 617, 46):
        rect(552, y, 18, 7, gold)
        rect(700, y, 18, 7, gold)

    # Open architecture-city safe area.
    rect(690, 110, game_map.width - 690, 540, (8, 13, 22))
    rect(690, 96, game_map.width - 690, 18, (31, 40, 58))
    rect(690, 620, game_map.width - 690, 30, (34, 42, 58))

    # Tall geometric ribs and arches.
    for x in range(760, game_map.width, 210):
        rect(x, 124, 10, 500, (34, 44, 64))
        rect(x + 132, 124, 10, 500, (24, 32, 49))
        for y in range(170, 585, 78):
            line((x, y), (x + 132, y - 34), (21, 31, 50), 2)
            line((x + 132, y - 34), (x + 132, y + 34), (21, 31, 50), 2)
        pygame.draw.arc(screen, (42, 58, 84), apply_rect(pygame.Rect(x - 14, 132, 166, 185)), 3.14, 6.28, 3)

    # Distant architecture city: impossible columns, suspended halls, moonlit plans.
    for x, h, c in [
        (760, 210, (13, 22, 36)), (930, 285, (10, 19, 32)), (1120, 240, (15, 24, 38)),
        (1320, 325, (11, 18, 31)), (1540, 230, (15, 25, 39)),
    ]:
        rect(x, 640 - h, 110, h, c)
        rect(x + 20, 640 - h - 30, 70, 30, c)
        for y in range(640 - h + 34, 610, 62):
            rect(x + 28, y, 20, 32, (18, 51, 78))
            rect(x + 66, y + 12, 20, 26, (44, 34, 82))

    # Blueprint panels and construction glyphs.
    rect(940, 180, 250, 92, (7, 15, 25))
    pygame.draw.rect(screen, (64, 204, 236), apply_rect(pygame.Rect(940, 180, 250, 92)), 2)
    line((970, 222), (1162, 222), cyan, 3)
    line((970, 246), (1115, 246), (94, 236, 190), 3)
    circle(1118, 222, 8, cyan, 2)
    circle(1076, 246, 6, teal, 2)

    rect(1255, 284, 285, 118, (6, 13, 23))
    pygame.draw.rect(screen, (88, 106, 142), apply_rect(pygame.Rect(1255, 284, 285, 118)), 2)
    for i in range(5):
        x = 1288 + i * 48
        line((x, 370), (x + 22, 326), cyan if i % 2 == 0 else gold, 3)
        circle(x + 22, 326, 5, cyan if i % 2 == 0 else gold)
    line((1288, 370), (1505, 370), (82, 236, 184), 3)

    # Safe-area props: shop alcove and moon altar alcove are drawn behind the real interactables.
    rect(900, 520, 250, 110, (30, 22, 20))
    pygame.draw.rect(screen, (111, 78, 48), apply_rect(pygame.Rect(900, 520, 250, 110)), 3)
    rect(920, 540, 210, 18, (70, 48, 31))
    rect(934, 574, 15, 30, cyan)
    rect(958, 570, 13, 34, teal)
    rect(1028, 571, 14, 33, violet)
    rect(1060, 578, 13, 26, gold)
    rect(925, 608, 202, 6, (82, 56, 34))

    rect(1220, 520, 132, 110, (7, 13, 24))
    pygame.draw.rect(screen, (58, 74, 100), apply_rect(pygame.Rect(1220, 520, 132, 110)), 2)
    pygame.draw.circle(screen, (48, 126, 155), apply_pos((1286, 552)), 34, 2)
    pygame.draw.circle(screen, (185, 232, 255), apply_pos((1286, 552)), 12)
    pygame.draw.circle(screen, (92, 216, 255), apply_pos((1292, 550)), 8)
    rect(1246, 604, 80, 10, (48, 58, 78))

    # Right side: unfinished path into House of Architecture.
    rect(1580, 250, 210, 400, (5, 9, 15))
    pygame.draw.arc(screen, (184, 190, 214), apply_rect(pygame.Rect(1558, 206, 254, 260)), 3.14, 6.28, 6)
    pygame.draw.arc(screen, (76, 86, 110), apply_rect(pygame.Rect(1584, 234, 202, 206)), 3.14, 6.28, 4)
    rect(1625, 430, 120, 190, (3, 7, 12))
    rect(1636, 442, 98, 8, cyan)
    rect(1666, 472, 38, 78, violet)
    for y in [300, 352, 404]:
        rect(1550, y, 34, 6, gold)
        rect(1786, y, 34, 6, gold)

    # Foreground depth.
    rect(0, 666, game_map.width, 54, (3, 5, 9))
    for x in range(-10, game_map.width, 48):
        rect(x, 670, 30, 8, (42, 50, 66))
    line((0, 688), (game_map.width, 688), (88, 95, 112), 3)
    line((0, 710), (game_map.width, 710), (39, 47, 64), 3)


def draw_map8_architecture_final_background(screen, camera, game_map):
    """Clean moon-architecture background for Level 5 Tiled gameplay."""
    def apply_rect(rect):
        return camera.apply_rect(rect) if camera is not None else rect

    def apply_pos(pos):
        return camera.apply_pos(pos) if camera is not None else pos

    def rect(x, y, w, h, color, width=0):
        pygame.draw.rect(screen, color, apply_rect(pygame.Rect(int(x), int(y), int(w), int(h))), width)

    def line(a, b, color, width=2):
        pygame.draw.line(screen, color, apply_pos(a), apply_pos(b), width)

    def circle(x, y, radius, color, width=0):
        pygame.draw.circle(screen, color, apply_pos((int(x), int(y))), int(radius), width)

    def arc(x, y, w, h, start, end, color, width=2):
        pygame.draw.arc(screen, color, apply_rect(pygame.Rect(int(x), int(y), int(w), int(h))), start, end, width)

    def glow(cx, cy, w, h, color):
        draw_rect = apply_rect(pygame.Rect(int(cx - w / 2), int(cy - h / 2), int(w), int(h)))
        if draw_rect.width <= 0 or draw_rect.height <= 0:
            return
        surface = pygame.Surface((max(1, draw_rect.width), max(1, draw_rect.height)), pygame.SRCALPHA)
        for i, alpha in enumerate((38, 24, 15, 8)):
            inset = i * 34
            pygame.draw.ellipse(
                surface,
                (*color, alpha),
                pygame.Rect(inset, inset, max(1, draw_rect.width - inset * 2), max(1, draw_rect.height - inset * 2)),
            )
        screen.blit(surface, draw_rect.topleft)

    width = game_map.width
    height = game_map.height
    screen.fill((2, 5, 12))
    rect(0, 0, width, height, (2, 5, 12))

    # Quiet cosmic depth.
    for y in range(0, height, 90):
        shade = 8 + (y // 90) * 2
        rect(0, y, width, 90, (3, shade, 18 + (y // 180) * 2))

    for i in range(180):
        x = (i * 557 + 83) % max(1, width)
        y = 36 + ((i * 149) % 560)
        color = (68, 126, 164) if i % 4 else (125, 215, 246)
        size = 1 if i % 5 else 2
        rect(x, y, size, size, color)

    # The final moon and distant Lunar Core glow are large and clean, not noisy.
    glow(9800, 165, 980, 620, (105, 185, 255))
    circle(9800, 165, 175, (183, 202, 231))
    circle(9868, 106, 32, (147, 164, 194))
    circle(9720, 206, 42, (151, 169, 199))
    circle(9895, 226, 22, (142, 160, 191))

    glow(10420, 520, 1050, 520, (100, 90, 255))
    for r, color in ((240, (54, 72, 120)), (176, (72, 220, 248)), (112, (152, 118, 255))):
        circle(10420, 520, r, color, 3)
    line((10420, 278), (10420, 766), (86, 222, 250), 2)
    line((10170, 520), (10670, 520), (126, 96, 255), 2)

    # Massive architecture supports. These give the scene structure without clutter.
    for index, x in enumerate(range(180, width, 620)):
        top = 84 + (index % 4) * 32
        pillar_w = 54 + (index % 3) * 10
        rect(x, top, pillar_w, height - top, (10, 18, 32))
        rect(x + 8, top, 4, height - top, (36, 58, 84))
        rect(x + pillar_w - 10, top, 3, height - top, (4, 8, 16))
        for y in range(top + 60, height - 30, 92):
            rect(x - 22, y, pillar_w + 44, 8, (36, 45, 66))
            rect(x + pillar_w // 2 - 3, y - 26, 6, 20, (74, 210, 238))

    # Long celestial rails and bridge systems behind the playable platforms.
    for y, color in ((210, (31, 49, 78)), (360, (25, 42, 70)), (548, (21, 37, 62))):
        line((0, y), (width, y), color, 2)
        for x in range(0, width, 720):
            line((x + 60, y), (x + 220, y - 70), (18, 31, 55), 1)
            line((x + 300, y - 74), (x + 480, y), (18, 31, 55), 1)

    # Connected moon-transit rings.
    ring_data = [
        (1300, 430, 360, 300, (65, 207, 238)),
        (3050, 385, 440, 360, (100, 235, 190)),
        (5350, 440, 520, 420, (130, 104, 255)),
        (7600, 420, 470, 380, (78, 220, 250)),
        (9100, 500, 420, 340, (144, 115, 255)),
    ]
    for cx, cy, rw, rh, accent in ring_data:
        arc(cx - rw // 2, cy - rh // 2, rw, rh, math.radians(196), math.radians(344), (39, 54, 84), 5)
        arc(cx - rw // 2 + 36, cy - rh // 2 + 28, rw - 72, rh - 56, math.radians(202), math.radians(338), accent, 2)
        line((cx - rw // 2, cy), (cx + rw // 2, cy), (21, 36, 62), 2)
        circle(cx, cy, 8, accent)

    # Hanging gardens and moon-waterfalls.
    for x in range(1500, 3000, 360):
        rect(x, 500, 230, 18, (42, 58, 74))
        rect(x + 24, 487, 180, 13, (42, 92, 76))
        for vx in range(x + 36, x + 205, 42):
            line((vx, 500), (vx - 18, 620), (28, 84, 70), 2)
        for drop_x in (x + 56, x + 156):
            line((drop_x, 518), (drop_x, 700), (60, 194, 222), 1)
            line((drop_x + 8, 540), (drop_x + 8, 720), (25, 78, 102), 1)

    # Broken city section: cracked but readable.
    for x in range(3300, 4700, 300):
        rect(x, 150 + (x // 300 % 4) * 52, 150, 460, (8, 14, 26))
        rect(x + 18, 180 + (x // 300 % 4) * 52, 112, 6, (69, 205, 230))
        line((x + 16, 225), (x + 118, 326), (37, 48, 74), 2)
        line((x + 132, 244), (x + 54, 410), (37, 48, 74), 2)

    # Cathedral silhouettes around the finale.
    for x in range(8500, 10900, 360):
        base = 790
        spire_h = 310 + (x // 360 % 3) * 70
        rect(x, base - spire_h, 120, spire_h, (5, 10, 22))
        rect(x + 44, base - spire_h - 90, 32, 90, (6, 12, 25))
        line((x + 60, base - spire_h - 124), (x + 60, base - spire_h - 10), (65, 200, 230), 2)
        for y in range(base - spire_h + 54, base - 40, 96):
            circle(x + 60, y, 10, (91, 80, 166), 2)

    # Abyss band below: calm darkness, so bottom areas read as dangerous depth.
    rect(0, height - 88, width, 88, (0, 2, 8))
    line((0, height - 88), (width, height - 88), (18, 29, 48), 3)
    for x in range(40, width, 260):
        line((x, height - 82), (x + 110, height - 44), (9, 17, 30), 1)



def draw_map1_moon_altar(screen, camera, altar_rect, used):
    """Small one-use healing altar for the checkpoint map."""
    if altar_rect is None:
        return

    def apply_rect(rect):
        return camera.apply_rect(rect) if camera is not None else rect

    def apply_pos(pos):
        return camera.apply_pos(pos) if camera is not None else pos

    x = altar_rect.x
    y = altar_rect.y
    w = altar_rect.width
    h = altar_rect.height

    stone_dark = (29, 32, 44)
    stone = (58, 63, 82)
    stone_light = (122, 132, 154)
    gold = (208, 170, 78)
    gold_dark = (104, 77, 38)
    glow = (90, 204, 238) if not used else (70, 78, 92)
    glow_soft = (35, 82, 116) if not used else (28, 32, 42)
    core = (225, 246, 255) if not used else (118, 126, 140)
    dim = (16, 18, 26)

    pygame.draw.rect(screen, stone_dark, apply_rect(pygame.Rect(x + 6, y + h - 16, w - 12, 16)))
    pygame.draw.rect(screen, stone, apply_rect(pygame.Rect(x + 14, y + h - 28, w - 28, 14)))
    pygame.draw.rect(screen, stone_light, apply_rect(pygame.Rect(x + 14, y + h - 28, w - 28, 3)))
    pygame.draw.rect(screen, gold_dark, apply_rect(pygame.Rect(x + 22, y + h - 34, w - 44, 8)))
    pygame.draw.rect(screen, gold, apply_rect(pygame.Rect(x + 27, y + h - 36, w - 54, 3)))

    pygame.draw.rect(screen, stone, apply_rect(pygame.Rect(x + 12, y + 26, 8, 34)))
    pygame.draw.rect(screen, stone, apply_rect(pygame.Rect(x + w - 20, y + 26, 8, 34)))
    pygame.draw.rect(screen, stone_light, apply_rect(pygame.Rect(x + 10, y + 24, 12, 5)))
    pygame.draw.rect(screen, stone_light, apply_rect(pygame.Rect(x + w - 22, y + 24, 12, 5)))

    center = (x + w // 2, y + 24)
    if not used:
        pygame.draw.circle(screen, glow_soft, apply_pos(center), 31)
        pygame.draw.circle(screen, glow, apply_pos(center), 20)
    else:
        pygame.draw.circle(screen, dim, apply_pos(center), 22)
        pygame.draw.circle(screen, stone, apply_pos(center), 16)

    pygame.draw.circle(screen, core, apply_pos(center), 10)
    pygame.draw.circle(screen, glow, apply_pos((center[0] + 5, center[1] - 1)), 8)
    pygame.draw.circle(screen, dim, apply_pos((center[0] + 9, center[1] - 2)), 8)


class LevelManager:
    def __init__(self):
        self.maps = self.build_maps()
        self.current_map_id = 0
        self.current_map = self.maps[self.current_map_id]
        self.collapsing_lift_rect = self.find_platform_rect(0, 11280, 160, 220, 20)
        self.collapsing_lift_start_y = 160
        self.collapsing_lift_target_y = 670
        self.collapsing_lift_speed = 105
        self.collapsing_lift_y = float(self.collapsing_lift_start_y)
        self.collapsing_lift_state = "idle"
        self.collapsing_lift_has_transitioned = False
        self.deadly_voids = {
            0: [
                pygame.Rect(9500, SCREEN_HEIGHT - 40, 1755, 60),
            ],
            2: [
                pygame.Rect(0, MAP_2_HEIGHT + 2, MAP_2_WIDTH, 120),
            ],
        }
        self.map1_moon_altar_rect = pygame.Rect(1218, 536, 82, 68)
        self.map1_moon_altar_used = False
        self.map3_moon_altar_rect = pygame.Rect(315, 536, 82, 68)
        self.map3_moon_altar_used = False
        self.map5_moon_altar_rect = pygame.Rect(535, 556, 82, 68)
        self.map5_moon_altar_used = False
        self.map7_moon_altar_rect = pygame.Rect(1245, 536, 82, 68)
        self.map7_moon_altar_used = False
        self.background_draw_callback = None

        # CSV/PNG Tiled map loading for Map 0 (your part)
        self.csv_tile_surfaces = []
        self.csv_map = []
        self.tiled_layers = []  # List of (surface, x, y) for each layer
        self.last_vel_x = 0  # Track last horizontal velocity to detect direction change
        self.jump_state = "rising"  # rising, falling, landing
        self.dash_distance = 0  # Track dash distance
        self.dash_start_x = 0  # Dash start position
        self.tiled_image = None

        try:
            self.tiled_image = pygame.image.load(PROJECT_ROOT / "assets" / "Map0.png").convert_alpha()
            # tileset_image = pygame.image.load("assets/Map0.png").convert_alpha()

            # self.csv_tile_surfaces = self._slice_tileset(self.tiled_image, 32, 32)
            # print(f"Tileset loaded: {len(self.csv_tile_surfaces)} tiles")
            print("Map0.png loaded successfully")

            # Load all layer CSVs and render them
            # layer_files = [
            #     ("maps/Map0_Tile Layer 1 Floor.csv", "Floor"),      # layer 0 (bottom)
            #     ("maps/Map0_Tile Layer 2 Wall.csv", "Wall"),       # layer 1
            #     ("maps/Map0_Tile Layer 3 Platform (Rect).csv", "Platform"),  # layer 2
            #     ("maps/Map0_Tile Layer 4 Object.csv", "Object"),     # layer 3 (top)
            # ]

        except Exception as e:
            print(f"Failed to load Tiled map: {e}")

    # def _slice_tileset(self, image, tile_w, tile_h):
    #     surfaces = []
    #     for y in range(0, image.get_height(), tile_h):
    #         for x in range(0, image.get_width(), tile_w):
    #             surfaces.append(image.subsurface((x, y, tile_w, tile_h)))
    #     return surfaces

    # def _load_csv_raw(self, filepath):
    #     map_data = []
    #     with open(filepath, 'r') as f:
    #         for line in f:
    #             line = line.strip()
    #             if not line:
    #                 continue
    #             cells = line.split(',')
    #             int_row = []
    #             for cell in cells:
    #                 val = cell.strip()
    #                 if val == '' or val == '-1':
    #                     int_row.append(-1)
    #                 else:
    #                     try:
    #                         int_row.append(int(val))
    #                     except ValueError:
    #                         int_row.append(-1)
    #             if int_row:
    #                 map_data.append(int_row)
    #     print(f"Loaded {len(map_data)} rows, {len(map_data[0]) if map_data else 0} columns")
    #     return map_data

    # def _render_layer(self, layer_data, tile_w, tile_h, layer_name="unknown"):
    #     """Render a single CSV layer to a pygame Surface"""
    #     if not layer_data or not layer_data[0]:
    #         return None

    #     rows = len(layer_data)
    #     cols = len(layer_data[0])

    #     # Calculate surface size
    #     width = cols * tile_w
    #     height = rows * tile_h

    #     # Create transparent surface for this layer
    #     surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
    #     tiles_drawn = 0
    #     # Draw each tile
    #     for row in range(rows):
    #         for col in range(cols):
    #             tile_id = layer_data[row][col]
    #             if tile_id >= 0:
    #                 x = col * tile_w
    #                 y = row * tile_h
    #                 pygame.draw.rect(surface, (255, 0, 0), (x, y, tile_w, tile_h))
    #                 # surface.blit(self.csv_tile_surfaces[tile_id], (x, y))
    #                 tiles_drawn += 1
        
    #     print(f"Layer: {layer_name}, tiles drawn: {tiles_drawn} / {rows*cols}")
    #     return surface

    def find_platform_rect(self, map_id, x, y, width, height):
        """Find a platform in the given map by its rect position/size."""
        game_map = self.maps.get(map_id)
        if game_map is None:
            return None
        target = pygame.Rect(x, y, width, height)
        for plat in game_map.platforms:
            if plat == target:
                return plat
        return None

    def build_default_map2(self):
        return GameMap(
            2,
            "Pale Crown Underfacility - Vertical Test",
            MAP_2_WIDTH,
            MAP_2_HEIGHT,
            [
                pygame.Rect(0, MAP_2_HEIGHT - 80, MAP_2_WIDTH, 80),
                pygame.Rect(0, 0, MAP_2_WIDTH, 40),
                pygame.Rect(0, 40, 30, MAP_2_HEIGHT - 40),
                pygame.Rect(MAP_2_WIDTH - 30, 40, 30, MAP_2_HEIGHT - 40),
                pygame.Rect(220, MAP_2_HEIGHT - 220, 240, 30),
                pygame.Rect(560, MAP_2_HEIGHT - 360, 220, 30),
                pygame.Rect(900, MAP_2_HEIGHT - 500, 240, 30),
                pygame.Rect(560, MAP_2_HEIGHT - 640, 220, 30),
                pygame.Rect(220, MAP_2_HEIGHT - 780, 240, 30),
                pygame.Rect(560, MAP_2_HEIGHT - 920, 220, 30),
                pygame.Rect(900, MAP_2_HEIGHT - 1060, 240, 30),
                pygame.Rect(1180, 220, 220, 30),
                pygame.Rect(0, MAP_2_HEIGHT - 20, MAP_2_WIDTH, 20),
            ],
            (140, MAP_2_HEIGHT - 80),
            [
                {
                    "rect": pygame.Rect(1260, 120, DOOR_WIDTH, DOOR_HEIGHT),
                    "target_map": "victory",
                    "label": "Level 3",
                }
            ],
            map_type="rest_stage",
        )

    def build_tiled_map2(self):
        map_path = Path(__file__).resolve().parents[2] / "assets" / "maps" / "map2.json"
        tiled = load_tiled_map(map_path)

        if tiled is None or not tiled["platforms"]:
            return self.build_default_map2()

        player_spawn = tiled["player_spawn"] or (140, tiled["height"] - 80)
        doors = [
            {
                # Top-right MAP 2 platform checkpoint gate. Change target_map to 3 later when Level 3 exists.
                "rect": pygame.Rect(10860, 214, 140, 100),
                "target_map": 3,
                "label": "Checkpoint",
                "visible": True,
                "auto": False,
                "style": "pale_crown_transit",
                "prompt": "Press E to enter checkpoint",
            }
        ]

        return GameMap(
            2,
            "Pale Crown Underfacility",
            tiled["width"] or MAP_2_WIDTH,
            tiled["height"] or MAP_2_HEIGHT,
            tiled["platforms"],
            player_spawn,
            doors,
            enemy_spawns=tiled["enemy_spawns"],
            boss_spawn=tiled["boss_spawn"],
            fulcrums=tiled["fulcrums"],
            shop_rect=tiled["shop_rect"],
            moving_platforms=tiled["moving_platforms"],
            checkpoints=tiled["checkpoints"],
            interactables=tiled["interactables"],
            hazards=tiled["hazards"],
            map_type="level2_stage",
        )


    def build_checkpoint_map3(self):
        return GameMap(
            3,
            "Checkpoint - Pale Crown Rail Station",
            MAP_1_WIDTH,
            MAP_1_HEIGHT,
            [
                pygame.Rect(0, 650, MAP_1_WIDTH, 70),
                pygame.Rect(0, 0, MAP_1_WIDTH, 40),
                pygame.Rect(0, 40, 40, 610),
                pygame.Rect(MAP_1_WIDTH - 40, 40, 40, 610),
                pygame.Rect(100, 620, 1300, 30),
            ],
            (222, 650),
            [
                {
                    "rect": pygame.Rect(MAP_1_WIDTH - 104, 430, 72, 220),
                    "target_map": 5,
                    "label": "Scrap Trenches",
                    "visible": True,
                    "auto": False,
                    "style": "map3_emergency_ladder",
                    "prompt": "Press E to enter scrap trenches",
                }
            ],
            shop_rect=pygame.Rect(540, 528, 180, 92),
            map_type="checkpoint_stage",
        )


    def build_tiled_map4(self):
        map_path = Path(__file__).resolve().parents[2] / "assets" / "maps" / "map4.json"
        tiled = load_tiled_map(map_path)

        if tiled is None or not tiled["platforms"]:
            return GameMap(
                4,
                "House of Intelligence",
                MAP_4_WIDTH,
                MAP_4_HEIGHT,
                [
                    pygame.Rect(0, MAP_4_HEIGHT - 70, MAP_4_WIDTH, 70),
                    pygame.Rect(0, 0, MAP_4_WIDTH, 40),
                    pygame.Rect(0, 40, 40, MAP_4_HEIGHT - 40),
                    pygame.Rect(MAP_4_WIDTH - 40, 40, 40, MAP_4_HEIGHT - 40),
                    pygame.Rect(180, MAP_4_HEIGHT - 210, 220, 28),
                    pygame.Rect(520, MAP_4_HEIGHT - 330, 240, 28),
                    pygame.Rect(920, MAP_4_HEIGHT - 450, 260, 28),
                ],
                (160, MAP_4_HEIGHT - 70),
                [],
                map_type="level3_stage",
            )

        player_spawn = tiled["player_spawn"] or (140, tiled["height"] - 80)
        doors = list(tiled["doors"])
        doors.append(
            {
                # Invisible fall exit near the MAP 4 apex route.
                # Jump down through this shaft to reach the Level 3 checkpoint.
                "rect": pygame.Rect(13510, 870, 250, 360),
                "target_map": 5,
                "label": "House of Intelligence waste drop",
                "visible": False,
                "auto": True,
            }
        )

        return GameMap(
            4,
            "House of Intelligence",
            tiled["width"] or MAP_4_WIDTH,
            tiled["height"] or MAP_4_HEIGHT,
            tiled["platforms"],
            player_spawn,
            doors,
            enemy_spawns=tiled["enemy_spawns"],
            boss_spawn=tiled["boss_spawn"],
            fulcrums=tiled["fulcrums"],
            shop_rect=tiled["shop_rect"],
            moving_platforms=tiled["moving_platforms"],
            checkpoints=tiled["checkpoints"],
            interactables=tiled["interactables"],
            hazards=tiled["hazards"],
            map_type="level3_stage",
        )


    def build_checkpoint_map5(self):
        return GameMap(
            5,
            "Checkpoint - The Scrap Trenches",
            MAP_5_WIDTH,
            MAP_5_HEIGHT,
            [
                pygame.Rect(0, 650, MAP_5_WIDTH, 70),
                pygame.Rect(0, 0, 132, 40),
                pygame.Rect(372, 0, MAP_5_WIDTH - 372, 40),
                pygame.Rect(0, 40, 40, 610),
                pygame.Rect(MAP_5_WIDTH - 40, 40, 40, 430),
                pygame.Rect(110, 620, 390, 30),
                pygame.Rect(530, 590, 160, 26),
                pygame.Rect(710, 620, 260, 30),
                pygame.Rect(1030, 610, 260, 30),
                pygame.Rect(1285, 630, 165, 20),
            ],
            (255, 118),
            [
                {
                    "rect": pygame.Rect(MAP_5_WIDTH - 96, 540, 122, 110),
                    "target_map": 7,
                    "label": "Architecture Subgate",
                    "visible": False,
                    "auto": True,
                }
            ],
            shop_rect=pygame.Rect(730, 548, 180, 92),
            map_type="checkpoint_stage",
        )


    def build_tiled_map6(self):
        map_path = Path(__file__).resolve().parents[2] / "assets" / "maps" / "map6.json"
        tiled = load_tiled_map(map_path)

        if tiled is None or not tiled["platforms"]:
            return self.build_level4_military_map6()

        map_width = tiled["width"] or MAP_6_WIDTH
        map_height = tiled["height"] or MAP_6_HEIGHT
        player_spawn = tiled["player_spawn"] or (160, map_height - 80)
        doors = list(tiled["doors"])
        doors.append(
            {
                "rect": pygame.Rect(map_width - 72, max(0, map_height - 118), 82, 108),
                "target_map": 7,
                "label": "Architecture underpass",
                "visible": False,
                "auto": True,
            }
        )
        return GameMap(
            6,
            "House of Military",
            map_width,
            map_height,
            tiled["platforms"],
            player_spawn,
            doors,
            enemy_spawns=tiled["enemy_spawns"],
            boss_spawn=tiled["boss_spawn"],
            fulcrums=tiled["fulcrums"],
            shop_rect=tiled["shop_rect"],
            moving_platforms=tiled["moving_platforms"],
            collapsing_platforms=tiled["collapsing_platforms"],
            checkpoints=tiled["checkpoints"],
            interactables=tiled["interactables"],
            hazards=tiled["hazards"],
            map_type="level4_stage",
        )


    def build_level4_military_map6(self):
        return GameMap(
            6,
            "House of Military - Scrap Graveyard Escape",
            MAP_6_WIDTH,
            MAP_6_HEIGHT,
            [
                pygame.Rect(0, 880, MAP_6_WIDTH, 70),
                pygame.Rect(0, 0, MAP_6_WIDTH, 40),
                pygame.Rect(0, 40, 40, 840),
                pygame.Rect(MAP_6_WIDTH - 40, 40, 40, 840),
                pygame.Rect(140, 820, 360, 40),
                pygame.Rect(620, 770, 260, 32),
                pygame.Rect(1010, 720, 300, 30),
                pygame.Rect(1520, 820, 420, 32),
                pygame.Rect(2260, 760, 300, 30),
                pygame.Rect(3020, 705, 260, 30),
                pygame.Rect(3620, 640, 320, 30),
                pygame.Rect(4380, 760, 260, 30),
                pygame.Rect(4620, 600, 250, 30),
                pygame.Rect(4920, 445, 220, 28),
                pygame.Rect(5780, 690, 360, 28),
                pygame.Rect(6280, 640, 330, 28),
                pygame.Rect(6780, 710, 280, 28),
                pygame.Rect(7240, 760, 340, 32),
                pygame.Rect(7800, 700, 300, 30),
                pygame.Rect(8460, 820, 520, 32),
                pygame.Rect(9360, 820, 780, 32),
                pygame.Rect(10640, 800, 520, 32),
                pygame.Rect(11440, 820, 520, 32),
            ],
            (220, 820),
            [
                {
                    "rect": pygame.Rect(MAP_6_WIDTH - 72, MAP_6_HEIGHT - 118, 82, 108),
                    "target_map": 7,
                    "label": "Architecture underpass",
                    "visible": False,
                    "auto": True,
                }
            ],
            map_type="level4_stage",
        )


    def build_checkpoint_map7(self):
        return GameMap(
            7,
            "Checkpoint - Architecture Subgate",
            MAP_7_WIDTH,
            MAP_7_HEIGHT,
            [
                pygame.Rect(0, 650, MAP_7_WIDTH, 70),
                pygame.Rect(0, 0, MAP_7_WIDTH, 40),
                pygame.Rect(0, 40, 54, 610),
                pygame.Rect(0, 392, 610, 40),
                pygame.Rect(0, 620, 720, 30),
                pygame.Rect(690, 620, 1110, 30),
                pygame.Rect(820, 565, 150, 24),
                pygame.Rect(1140, 540, 140, 24),
                pygame.Rect(1390, 505, 160, 24),
                pygame.Rect(1540, 620, 260, 30),
            ],
            (126, 620),
            [
                {
                    "rect": pygame.Rect(MAP_7_WIDTH - 70, 520, 90, 130),
                    "target_map": 8,
                    "label": "House of Architecture",
                    "visible": False,
                    "auto": True,
                }
            ],
            shop_rect=pygame.Rect(930, 548, 180, 92),
            map_type="checkpoint_stage",
        )



    def build_tiled_map8(self):
        map_path = Path(__file__).resolve().parents[2] / "assets" / "maps" / "map8.json"
        tiled = load_tiled_map(map_path)

        if tiled is None or not tiled["platforms"]:
            return self.build_level5_architecture_map8()

        player_spawn = tiled["player_spawn"] or (160, (tiled["height"] or MAP_8_HEIGHT) - 80)
        return GameMap(
            8,
            "Lunar Chamber",
            tiled["width"] or MAP_8_WIDTH,
            tiled["height"] or MAP_8_HEIGHT,
            tiled["platforms"],
            player_spawn,
            tiled["doors"],
            enemy_spawns=tiled["enemy_spawns"],
            boss_spawn=tiled["boss_spawn"],
            fulcrums=tiled["fulcrums"],
            shop_rect=tiled["shop_rect"],
            moving_platforms=tiled["moving_platforms"],
            collapsing_platforms=tiled["collapsing_platforms"],
            checkpoints=tiled["checkpoints"],
            interactables=tiled["interactables"],
            hazards=tiled["hazards"],
            map_type="level5_stage",
        )


    def build_level5_architecture_map8(self):
        return GameMap(
            8,
            "Level 5 - House of Architecture",
            MAP_8_WIDTH,
            MAP_8_HEIGHT,
            [
                pygame.Rect(0, 650, MAP_8_WIDTH, 70),
                pygame.Rect(0, 0, MAP_8_WIDTH, 40),
                pygame.Rect(0, 40, 44, 610),
                pygame.Rect(MAP_8_WIDTH - 44, 40, 44, 610),
                pygame.Rect(470, 535, 210, 30),
                pygame.Rect(840, 470, 190, 30),
                pygame.Rect(1220, 405, 230, 30),
                pygame.Rect(1650, 520, 260, 30),
                pygame.Rect(2140, 430, 260, 30),
            ],
            (170, 650),
            [],
            map_type="level5_stage",
        )


    def build_maps(self):
        return {
            # =========================================================================
            # MAP 0: LEVEL 1 — Fractured Velaris (Body Pile -> Boss Arena Entrance)
            # Sections 1-10. Boss + Resting Area continue in Map 1 / Map 2.
            # All platforms are connected/grounded — no random floaters.
            # =========================================================================
            0: GameMap(
                0,
                "Fractured Velaris — House of Science District",
                MAP_0_WIDTH,
                MAP_0_HEIGHT,
                [
                    # ─── 1. Body Pile Outside (0-1100) ───────────────────────────────
                    # Ruined street start. Long flat ground with ONE cracked-road structure
                    # mid-section: the pavement has buckled upward into a 2-tier slab.
                    # Looks intentional (an earthquake fault line), not random scattered pieces.
                    pygame.Rect(0, 650, 1100, 70),        # Long continuous street
                    pygame.Rect(400, 580, 50, 70),       # Lower buckled slab (sits on ground)
                    pygame.Rect(350, 530, 150, 40),       # Upper buckled slab (sits on lower slab)

                    pygame.Rect(650, 440, 250, 40), 
                    pygame.Rect(600, 400, 150, 40),  #second slab

                    pygame.Rect(850, 260, 50, 40),

                    pygame.Rect(900, 200, 30, 450), #wall
                    pygame.Rect(900, -20, 30, 140),  

                    # ─── 2. Destroyed Street (1100-2400) ─────────────────────────────
                    # NO PITS — continuous ground. Two collapsed-wall structures + a tall
                    # rubble heap form natural climbing/jumping challenges along the route.
                    pygame.Rect(1100, 650, 1300, 70),     # Continuous ground (no holes)
                    # Collapsed wall structure 1: two-tier slab
                    pygame.Rect(930, 200, 70, 10),

                    pygame.Rect(1040, 360, 300, 40),      # Wall fallen flat (lower slab)
                         

                    pygame.Rect(1040, 400, 60, 140), # tall wall sticking on "wall fallen flat"
                    pygame.Rect(930, 580, 20, 40), #lowest small slab
                    pygame.Rect(1000, 492, 60, 40),
                    pygame.Rect(930, 380, 20, 40), 

                    # Tall building rubble heap mid-section
                    pygame.Rect(1500, 200, 300, 40),
                    pygame.Rect(1500, 600, 300, 40),           # Tall rubble pile (climbing block)
                    pygame.Rect(1450, 200, 50, 40),
                    pygame.Rect(1800, 200, 50, 40),
                    # second wall and building
                    pygame.Rect(1990, 280, 40, 300),      # Lower fallen wall
                    pygame.Rect(2100, 220, 40, 360),      # Upper section (sits on lower)
                    pygame.Rect(2200, 300, 40, 360),
                    pygame.Rect(1990, -30, 410, 140),
                    pygame.Rect(2350, 400, 60, 20),
                    pygame.Rect(2240, 500, 60, 20),

                    # ─── 3. Ruined Building Route (2400-3900) ────────────────────────
                    # TALL multi-story building with 5 floors of vertical exploration.
                    # Walls extend almost to the ground so the stairs are visually INSIDE
                    # the building (no "L-shape" sticking out below). The doorway is a 70px
                    # gap at the bottom of the wall — player (64px tall) walks under at
                    # ground level. Floors alternate left/right so the player must jump
                    # back and forth to climb upward.
                    pygame.Rect(2400, 650, 1500, 70),     # Ground floor
                    pygame.Rect(2400, 20, 1500, 40),      # Stone ceiling (HIGH — y=20-60)

                    # Tall side walls — extend almost all the way to ground (y=60-580).
                    # The 70px gap below each wall is the doorway (player fits, 6px clearance).
                    pygame.Rect(2400, 50, 30, 520),       # Left wall  (y=60-580)
                    pygame.Rect(3870, 140, 30, 520),       # Right wall (y=60-580)

                    # NO STAIRS — player jumps directly from ground to Floor 2 (140px jump,
                    # well within the 160px max). The peak of a straight-up jump is y=490,
                    # which is ABOVE floor 2 at y=510, so the player cleanly clears floor 2
                    # during ascent and lands on it during descent. No L-shape outside the
                    # building, no head-bumping mid-jump.

                    # Floor 2 — LEFT-side fat wall
                    pygame.Rect(2440, 270, 160, 300),
                    pygame.Rect(2770, 200, 160, 30),
                    pygame.Rect(2690, 400, 160, 30),

                    # Floor 3 — RIGHT-side balcony. Reach: jump right + up from floor 2.
                    pygame.Rect(3080, 570, 50, 90),

                    # Floor 4 — LEFT-side balcony. Reach: jump left + up from floor 3.
                    pygame.Rect(2970, 520, 160, 30),

                    # Floor 5 — RIGHT-side TOP balcony. Reach: jump right + up from floor 4.
                    pygame.Rect(3790, 160, 90, 30),
                    pygame.Rect(3000, 160, 220, 30),

                    #new part
                    pygame.Rect(3200, 600, 140, 40), #first
                    pygame.Rect(3440, 480, 170, 40), #second
                    pygame.Rect(3480, 240, 190, 40), #above second
                    pygame.Rect(3200, 360, 170, 40), #third  
                    pygame.Rect(3200, 200, 80, 160), #third tall wall
                    pygame.Rect(3830, 200, 40, 220), # wall on right side small platform
                    pygame.Rect(3750, 420, 120, 40), #right side small platform
                    pygame.Rect(3750, 460, 30, 40),

                    # ─── 4. Collapsed Transit / Tram Wreck (3900-5100) ───────────────
                    # 3 crashed tram cars + a cab debris piece. Detailed visuals are drawn
                    # by draw_section4_tram_wreck (windows, doors, wheels, smoke, sparks).
                    pygame.Rect(3900, 650, 1200, 70),     # Street ground (with rails on top)
                    pygame.Rect(4030, 520, 360, 130),     # Tram car 1 — mostly intact, on wheels
                    pygame.Rect(4420, 560, 260, 90),      # Tram car 2 — derailed lower, smashed
                    pygame.Rect(4730, 480, 240, 170),     # Tram car 3 — overturned on its side
                    pygame.Rect(4990, 580, 110, 70),      # Cab / control room debris piece

                    # ─── 5. Science District Exterior (5100-6400) ────────────────────
                    # Lab buildings forming a varied skyline. Climb across rooftops.
                    pygame.Rect(5100, 650, 1300, 70),     # Ground
                    pygame.Rect(5000, 400, 200, 40),      # The platform of first building (nearby train)
                    pygame.Rect(5230, 500, 100, 20),      # The small platform lower near to the platform of first building
                    pygame.Rect(5380, 320, 240, 20),     # The platform of second building
                    pygame.Rect(5800, 260, 200, 20),     # The platform of third building
                    pygame.Rect(6200, 200, 200, 20),     # The platform of fourth building
                    pygame.Rect(6600, 240, 180, 20),      # The platform of fifth building

                    # ─── 6. Combat Roof (6400-7600) ───────────────────────
                    # Wide arena. Cover blocks + tactical platforms for fights.
                    # Enemy spawns at center.
                    pygame.Rect(6400, 650, 1200, 70),     # Ground
                    pygame.Rect(6800, 180, 100, 10),     # super thin platform on building
                    pygame.Rect(6900, 200, 150, 20),     # platform next to super thin building 
                    pygame.Rect(7050, 150, 300, 20),     # long platform at building  
                    pygame.Rect(7100, 100, 100, 60),     # small platform above long platform 
                    pygame.Rect(7330, 250, 110, 20),      # small platform below long platform

                    # ─── 7. Messy Lab Entrance (7600-8500) ───────────────────────────
                    # Partial enclosure. Stepped interior leading to the shop.
                    pygame.Rect(7600, 650, 900, 70),      # Ground
                    pygame.Rect(7600, 0, 700, 230),       # Ceiling
                    pygame.Rect(7700, 380, 600, 280),     # Huge part on ground       
                    pygame.Rect(7560, 380, 140, 20),      # small hang on cliff platform
                    pygame.Rect(7650, 420, 50, 40),       # small square below hang on cliff platform
                    pygame.Rect(8300, 380, 70, 20),       # first part of bridge (below)
                    pygame.Rect(8300, 183, 70, 20),       # first part of bridge (above)
                    pygame.Rect(8370, 350, 70, 20),       # second part of bridge (below)
                    pygame.Rect(8370, 150, 70, 20),       # second part of bridge (above)
                    pygame.Rect(8440, 320, 160, 20),      # third part of bridge (below)
                    pygame.Rect(8440, 120, 160, 20),      # third part of bridge (above)
                    pygame.Rect(8600, 350, 70, 20),       # fourth part of bridge (below)
                    pygame.Rect(8600, 150, 70, 20),       # fourth part of bridge (above)
                    pygame.Rect(8670, 380, 70, 20),       # fifth part of bridge (below)
                    pygame.Rect(8670, 183, 70, 20),       # fifth part of bridge (above)
                    pygame.Rect(8740, 0, 120, 230),       # after bridge tall wall (above)
                    pygame.Rect(8740, 380, 120, 330),     # after bridge tall wall (below)
                    pygame.Rect(8860, 380, 80, 10),     # small out cliff attached at below wall
                    pygame.Rect(9150, 180, 30, 520),      # next pillar witth 2 platform
                    pygame.Rect(9070, 300, 80, 10),     # first platform on pillar
                    pygame.Rect(9180, 200, 100, 10),     # second platform on pillar
                    pygame.Rect(8860, 520, 295, 140),   # first piece between cliff and pillar
                    pygame.Rect(9180, 520, 350, 140),    # second piece between cliff and pillar
                    pygame.Rect(9500, -20, 120, 200),       # after bridge tall wall (above)
                    pygame.Rect(9500, 300, 120, 550),       # after bridge tall wall (below)
                    pygame.Rect(9420, 360, 80, 10),      #small out cliff attached to after bridge tall wall below


                    # ─── 8. Collapse city, fallen bridge ───────────────────────────
                    pygame.Rect(8400, 650, 1100, 70),     # Floor
                    # pygame.Rect(11255, 650, 240, 70),    # Long approach
                    pygame.Rect(9620, 300, 80, 10),       # small cliff attach to tall wall (below) on right side
                    pygame.Rect(9820, 200, 160, 20),      #first short platform
                    pygame.Rect(10160, 300, 400, 20),     #long platform after small platform
                    pygame.Rect(10560, 250, 160, 20),
                    pygame.Rect(10680, 290, 160, 20),
                    pygame.Rect(11000, 200, 160, 20),
                    pygame.Rect(11100, 160, 160, 20),
                    pygame.Rect(11250, 160, 30, 560),
                    pygame.Rect(11280, 160, 220, 20),  
                 

                    # ─── Safety floor (catches falls into pits) ──────────────────────
                    pygame.Rect(0, SCREEN_HEIGHT - 20, MAP_0_WIDTH, 20),
                ],
                (155, 650),                                # Player spawn (Body Pile)
                [
                    {
                        "rect": pygame.Rect(11380, 550, DOOR_WIDTH, DOOR_HEIGHT),
                        "target_map": 1,
                        "label": "Lower Sanctuary",
                    }
                ],
                enemy_spawns=[],
                fulcrums=[
                    {
                        "rect": pygame.Rect(9620, 540, FULCRUM_RADIUS * 2, FULCRUM_RADIUS * 2),
                        "anchor": (9634, 554),
                        "target": (9770, 600),
                        "used": False,
                    }
                ],
                # shop_rect=pygame.Rect(8830, 530, 130, 90),
                map_type="science_city_stage",
            ),
            # =========================================================================
            # MAP 1: LEVEL 1 BOSS — The Warden Arena
            # =========================================================================
            1: self.build_tiled_map1(),
            # =========================================================================
            # MAP 2: LEVEL 2 - Pale Crown Underfacility / Tiled map
            # =========================================================================
            2: self.build_tiled_map2(),

            # =========================================================================
            # MAP 3: LEVEL 2 Checkpoint - Pale Crown Rail Station
            # =========================================================================
            3: self.build_checkpoint_map3(),

            # map4 and map6 are temporarily hidden from level progression but kept in assets.

            # =========================================================================
            # MAP 5: LEVEL 3 Checkpoint - The Scrap Trenches
            # =========================================================================
            5: self.build_checkpoint_map5(),

            # =========================================================================
            # MAP 7: LEVEL 4 Checkpoint - Architecture Subgate
            # =========================================================================
            7: self.build_checkpoint_map7(),

            # =========================================================================
            # MAP 8: LEVEL 5 - House of Architecture
            # =========================================================================
            8: self.build_tiled_map8(),
        }

    def build_default_map1(self):
        return GameMap(
            1,
            "The Warden - Boss Arena",
            MAP_1_WIDTH,
            MAP_1_HEIGHT,
            [
                pygame.Rect(0, 650, MAP_1_WIDTH, 70),
                pygame.Rect(0, 200, MAP_1_WIDTH, 40),
                pygame.Rect(0, 240, 30, 410),
                pygame.Rect(MAP_1_WIDTH - 30, 240, 30, 410),
                pygame.Rect(150, 540, 200, 110),
                pygame.Rect(MAP_1_WIDTH - 350, 540, 200, 110),
                pygame.Rect(0, SCREEN_HEIGHT - 20, MAP_1_WIDTH, 20),
            ],
            (100, 650),
            [
                {
                    "rect": pygame.Rect(MAP_1_WIDTH - 120, 550, DOOR_WIDTH, DOOR_HEIGHT),
                    "target_map": 8,
                    "label": "Lunar Core",
                }
            ],
            boss_spawn=(MAP_1_WIDTH // 2, 590),
            map_type="boss_stage",
        )

    def build_tiled_map1(self):
        map_path = Path(__file__).resolve().parents[2] / "assets" / "maps" / "map1.json"
        tiled = load_tiled_map(map_path)
        if tiled is None or not tiled["platforms"]:
            return self.build_default_map1()
        player_spawn = tiled["player_spawn"]
        if player_spawn is None and tiled["moving_platforms"]:
            first_lift = tiled["moving_platforms"][0].rect
            player_spawn = (first_lift.centerx, first_lift.top)
        if player_spawn is None:
            player_spawn = (100, 650)
        doors = tiled["doors"] or [
            {
                "rect": pygame.Rect(MAP_1_WIDTH - 70, 120, 70, 180),
                "target_map": 8,
                "label": "Lunar Core",
                "visible": False,
                "auto": True,
            }
        ]
        doors = [door.copy() for door in doors]
        for door in doors:
            if door.get("target_map") == 2:
                door["target_map"] = 8
                door["label"] = "Lunar Core"
                if door.get("auto", False) or door.get("visible", True) is False:
                    door["prompt"] = "Press E to enter Lunar Core"
        map1_shop_rect = tiled["shop_rect"] or pygame.Rect(520, 506, 150, 90)
        return GameMap(
            1,
            "Checkpoint - Lower Sanctuary",
            tiled["width"] or MAP_1_WIDTH,
            tiled["height"] or MAP_1_HEIGHT,
            tiled["platforms"],
            player_spawn,
            doors,
            enemy_spawns=tiled["enemy_spawns"],
            boss_spawn=tiled["boss_spawn"],
            shop_rect=map1_shop_rect,
            moving_platforms=tiled["moving_platforms"],
            checkpoints=tiled["checkpoints"],
            interactables=tiled["interactables"],
            hazards=tiled["hazards"],
            map_type="checkpoint_stage",
        )

    def reset_one_use_items(self):
        self.map1_moon_altar_used = False
        self.map3_moon_altar_used = False
        self.map5_moon_altar_used = False
        self.map7_moon_altar_used = False

    def get_moon_altar_rect(self):
        if self.current_map_id == 1:
            return self.map1_moon_altar_rect
        if self.current_map_id == 3:
            return self.map3_moon_altar_rect
        if self.current_map_id == 5:
            return self.map5_moon_altar_rect
        if self.current_map_id == 7:
            return self.map7_moon_altar_rect
        return None

    def _is_current_moon_altar_used(self):
        if self.current_map_id == 1:
            return self.map1_moon_altar_used
        if self.current_map_id == 3:
            return self.map3_moon_altar_used
        if self.current_map_id == 5:
            return self.map5_moon_altar_used
        if self.current_map_id == 7:
            return self.map7_moon_altar_used
        return True

    def _set_current_moon_altar_used(self):
        if self.current_map_id == 1:
            self.map1_moon_altar_used = True
        elif self.current_map_id == 3:
            self.map3_moon_altar_used = True
        elif self.current_map_id == 5:
            self.map5_moon_altar_used = True
        elif self.current_map_id == 7:
            self.map7_moon_altar_used = True

    def can_use_moon_altar(self, player):
        altar_rect = self.get_moon_altar_rect()
        if altar_rect is None or self._is_current_moon_altar_used():
            return False

        interaction_rect = altar_rect.inflate(64, 44)
        return player.rect.colliderect(interaction_rect)

    def use_moon_altar(self, player):
        """Use the moon altar (heal and restore mana)."""
        if not self.can_use_moon_altar(player):
            return False

        player.current_hp = player.max_hp
        player.hp = player.current_hp
        player.current_mana = player.max_mana
        player.mana = player.current_mana
        player.invincible_timer = 0
        self._set_current_moon_altar_used()
        return True
    
    def draw_tiled_map(self, screen, camera):
        """Draw all Tiled CSV layers (multi-layer support)"""
        if not self.tiled_layers:
            return

        # Get camera offset
        camera_x = 0
        camera_y = 0
        if camera is not None:
            if hasattr(camera, "offset"):
                camera_x = camera.offset.x
                camera_y = camera.offset.y
            print(f"DEBUG: Camera offset: ({camera_x}, {camera_y})")

        # Draw each layer (they are already in correct order from loading)
        for layer_surface, layer_name in self.tiled_layers:
            if layer_surface:
                print(f"DEBUG: Layer: {layer_name}, size={layer_surface.get_size()}")
                screen.blit(layer_surface, (0, 0))
                # print(f"Blitting {layer_name} at -{camera_x}, -{camera_y}")
                # screen.blit(layer_surface, (-camera_x, -camera_y))

    def draw_tiled_image(self, screen, camera):
        if self.tiled_image is None:
            return

        if camera is None:
            screen.blit(self.tiled_image, (0, 0))
            return

        camera_x = camera.offset.x if hasattr(camera, "offset") else getattr(camera, "x", 0)
        camera_y = camera.offset.y if hasattr(camera, "offset") else getattr(camera, "y", 0)
        screen.blit(self.tiled_image, (-camera_x, -camera_y))

    def get_current_map(self):
        return self.current_map

    def reset_current_moving_platforms(self):
        for moving_platform in self.current_map.moving_platforms:
            moving_platform.reset()

    def reset_current_collapsing_platforms(self):
        for platform in getattr(self.current_map, "collapsing_platforms", []):
            platform.reset()

    def update_collapsing_platforms(self, dt, player):
        for platform in getattr(self.current_map, "collapsing_platforms", []):
            platform.update(dt, player)

    def update_moving_platforms(self, dt, player):
        self.update_collapsing_platforms(dt, player)
        moving_platforms = self.current_map.moving_platforms
        moving_rects = [moving_platform.rect for moving_platform in moving_platforms]
        static_colliders = [
            platform
            for platform in self.current_map.platforms
            if all(platform is not moving_rect for moving_rect in moving_rects)
        ]

        for moving_platform in moving_platforms:
            moving_platform.update(dt, player, static_colliders)

    def is_player_in_deadly_void(self, player):
        voids = self.deadly_voids.get(self.current_map_id, [])
        foot_sensor = pygame.Rect(player.rect.x, player.rect.bottom - 4, player.rect.width, 8)

        for void in voids:
            if foot_sensor.colliderect(void):
                return True

        for hazard in self.current_map.hazards:
            if hazard["rect"].colliderect(foot_sensor):
                damage = str(hazard.get("damage", "instant")).lower()
                if damage in ("instant", "death", "kill"):
                    return True

        return False

    def find_platform_rect(self, map_id, x, y, width, height):
        if map_id not in self.maps:
            return None

        for platform in self.maps[map_id].platforms:
            if (
                platform.x == x
                and platform.y == y
                and platform.width == width
                and platform.height == height
            ):
                return platform

        return None

    def reset_collapsing_lift(self):
        if self.collapsing_lift_rect is None:
            return

        self.collapsing_lift_y = float(self.collapsing_lift_start_y)
        self.collapsing_lift_rect.y = self.collapsing_lift_start_y
        self.collapsing_lift_state = "idle"
        self.collapsing_lift_has_transitioned = False

    def is_player_on_collapsing_lift(self, player):
        if self.current_map_id != 0 or self.collapsing_lift_rect is None:
            return False

        lift = self.collapsing_lift_rect
        horizontal_overlap = (
            player.rect.right > lift.left + 8
            and player.rect.left < lift.right - 8
        )
        vertical_contact = abs(player.rect.bottom - lift.top) <= 6

        return horizontal_overlap and vertical_contact and player.vel_y >= 0

    def update_collapsing_lift(self, dt, player):
        if self.current_map_id != 0 or self.collapsing_lift_rect is None:
            return

        player_on_lift = self.is_player_on_collapsing_lift(player)

        if player_on_lift and self.collapsing_lift_state == "idle":
            self.collapsing_lift_state = "dropping"

        if self.collapsing_lift_state != "dropping":
            return

        old_y = self.collapsing_lift_rect.y
        self.collapsing_lift_y = min(
            self.collapsing_lift_target_y,
            self.collapsing_lift_y + self.collapsing_lift_speed * dt,
        )
        self.collapsing_lift_rect.y = round(self.collapsing_lift_y)
        lift_delta_y = self.collapsing_lift_rect.y - old_y

        if player_on_lift and lift_delta_y != 0:
            player.rect.y += lift_delta_y
            player.vel_y = 0
            player.on_ground = True

        if self.collapsing_lift_rect.y >= self.collapsing_lift_target_y:
            self.collapsing_lift_state = "arrived"

    def get_collapsing_lift_transition_target(self, player):
        if self.current_map_id != 0:
            return None

        if self.collapsing_lift_rect is None:
            return None

        if self.collapsing_lift_state != "arrived":
            return None

        if self.collapsing_lift_has_transitioned:
            return None

        if not self.is_player_on_collapsing_lift(player):
            return None

        if not self.current_map.doors:
            return None

        self.collapsing_lift_has_transitioned = True
        return self.current_map.doors[0]["target_map"]

    def change_map(self, target_map_id, player, enemy, camera=None):
        if target_map_id not in self.maps:
            return False

        self.current_map_id = target_map_id
        self.current_map = self.maps[self.current_map_id]

        if target_map_id == 0:
            self.reset_collapsing_lift()

        self.reset_current_moving_platforms()
        self.reset_current_collapsing_platforms()

        player.rect.midbottom = self.current_map.player_spawn
        player.vel_x = 0
        player.vel_y = 0
        if target_map_id == 5:
            player.vel_y = 7
            player.on_ground = False
        player.is_dashing = False
        player.is_attacking = False
        if hasattr(player, "clear_attack_animation"):
            player.clear_attack_animation()
        player.is_auto_grappling = False
        if hasattr(player, "cancel_swing"):
            player.cancel_swing()
        player.is_blocking = False
        player.is_parrying = False
        player.attack_has_hit = False
        player.should_spawn_projectile = False
        player.auto_grapple_start = None
        player.auto_grapple_end = None
        player.auto_grapple_control = None
        player.auto_grapple_anchor = None
        player.soul_anchor_active = False
        player.soul_anchor_pos = None
        player.soul_anchor_timer = 0

        enemy_spawn = self.get_active_enemy_spawn()
        if enemy_spawn is None:
            enemy.disable()
        else:
            enemy.respawn_at(enemy_spawn[0], enemy_spawn[1])

        if camera is not None:
            top_margin = camera.screen_height if target_map_id == 4 else 0
            camera.set_map_size(self.current_map.width, self.current_map.height, top_margin=top_margin)
            camera.snap_to(player.rect)

        print(f"Entered {self.current_map.name}")
        return True

    def get_active_enemy_spawn(self):
        if self.current_map.enemy_spawns:
            return self.current_map.enemy_spawns[0]

        if self.current_map.boss_spawn is not None:
            return self.current_map.boss_spawn

        return None

    def get_platforms(self):
        active_collapsing = [
            platform.rect
            for platform in getattr(self.current_map, "collapsing_platforms", [])
            if platform.is_solid
        ]
        return list(self.current_map.platforms) + active_collapsing

    def get_fulcrums(self):
        return self.current_map.fulcrums

    def get_shop_rect(self):
        return self.current_map.shop_rect

    def get_doors(self):
        return self.current_map.doors

    def check_deadly_void(self, player_rect):
        """Check if player falls into a deadly void (instant respawn)."""
        voids = self.deadly_voids.get(self.current_map_id, [])
        for void_rect in voids:
            if player_rect.colliderect(void_rect):
                return True
        return False

    def check_moon_altar(self, player_rect):
        """Check if player touches the moon altar in map 1."""
        if self.current_map_id != 1:
            return False
        if self.map1_moon_altar_used:
            return False
        if player_rect.colliderect(self.map1_moon_altar_rect):
            self.map1_moon_altar_used = True
            return True
        return False

    def draw_current_map(self, screen, camera):
        font = pygame.font.Font(None, 28)

        if self.current_map.map_id == 1:
            draw_map1_underground_background(screen, camera, self.current_map)
        elif self.current_map.map_id == 2:
            draw_map2_pale_crown_background(screen, camera, self.current_map)
            draw_map2_section_story_details(screen, camera, self.current_map)
        elif self.current_map.map_id == 3:
            draw_map3_train_station_background(screen, camera, self.current_map)
        elif self.current_map.map_id == 4:
            draw_map4_intelligence_city_background(screen, camera, self.current_map)
        elif self.current_map.map_id == 5:
            draw_map5_fighter_trash_checkpoint_background(screen, camera, self.current_map)
        elif self.current_map.map_id == 6:
            draw_map6_military_background(screen, camera, self.current_map)
        elif self.current_map.map_id == 7:
            draw_map7_architecture_checkpoint_background(screen, camera, self.current_map)
        elif self.current_map.map_id == 8:
            draw_map8_architecture_final_background(screen, camera, self.current_map)
        else:
            # 1. Background (moon, stars, distant city silhouette)
            draw_moon_background(screen, camera, self.current_map)

            # 2. Enclosed-room shells: dark void above ceilings + stone interior fill.
            draw_level1_room_shells(screen, camera, self.current_map)

            # 3. Street embankment behind ground islands.
            draw_level1_wall_masses(screen, camera, self.current_map)

            # 3b. Section 5 + Section 6 background buildings - drawn BEHIND platforms
            if self.current_map.map_id == 0:
                draw_section5_science_buildings(screen, camera)
                draw_section6_courtyard_buildings(screen, camera)
                draw_section8_collapsed_city_background(screen, camera)

        if self.background_draw_callback is not None:
            self.background_draw_callback(screen, camera)

        # 4. Draw Tiled CSV/PNG map (YOUR TILED MAP - placed behind platforms)
        self.draw_tiled_map(screen, camera)

        # 5. Foreground platforms (ground, ledges, rubble, pillars, ceilings)
        for platform in self.current_map.platforms:
            # Skip the safety floor at very bottom — it's invisible by design.
            if platform.y >= self.current_map.height - 30 and platform.height <= 30:
                continue
            # MAP 0 has old invisible ceiling blockers. Tiled MAP 2 collision should be visible.
            if self.current_map.map_id == 0 and platform.y <= 50 and platform.height <= 80:
                continue

            draw_rect = platform
            if camera is not None:
                draw_rect = camera.apply_rect(platform)
            if self.current_map.map_id in (6, 8):
                draw_map6_tiled_platform(screen, draw_rect)
            else:
                draw_moon_platform(screen, draw_rect)
                pass

        for collapsing_platform in getattr(self.current_map, "collapsing_platforms", []):
            draw_collapsing_platform(screen, camera, collapsing_platform)

        if self.current_map.map_id in (1, 3, 5, 7):
            draw_map1_moon_altar(
                screen,
                camera,
                self.get_moon_altar_rect(),
                self._is_current_moon_altar_used(),
            )

        # 5. Decorative props (no collision) — bones, blood, broken cars, signs, furniture.
        if self.current_map.map_id == 0:
            draw_section_decorations(screen, camera)
            draw_section4_tram_wreck(screen, camera)
            draw_body_pile(screen, camera, 135, 650)

        # 7. UI / Interactive Elements Layer
        for door in self.current_map.doors:
            if door.get("visible", True) is False:
                continue


            if door.get("style") == "map3_emergency_ladder":
                draw_map3_emergency_ladder_exit(screen, camera, door, font)
                continue

            if door.get("style") == "pale_crown_transit":
                draw_pale_crown_transit_gate(screen, camera, door, font)
                continue

            if door.get("style") == "broken_dumpster_exit":
                draw_map5_broken_dumpster_exit(screen, camera, door, font)
                continue

            draw_rect = door["rect"]
            if camera is not None:
                draw_rect = camera.apply_rect(door["rect"])
            if DEBUG_DRAW_HITBOXES:
                pygame.draw.rect(screen, (60, 220, 100), draw_rect)
                pygame.draw.rect(screen, (220, 255, 220), draw_rect, 2)
            text = font.render(door["label"], True, (20, 40, 20))
            screen.blit(text, text.get_rect(center=draw_rect.center))

        # 8. Draw collapsing lift if active
        if self.current_map_id == 0 and self.collapsing_lift_rect:
            draw_rect = self.collapsing_lift_rect
            if camera is not None:
                draw_rect = camera.apply_rect(draw_rect)
            draw_moon_platform(screen, draw_rect)

        # 9. Draw the Tiled art over MAP 0's procedural base.
        if self.current_map_id == 0:
            self.draw_tiled_image(screen, camera)

    def check_doors(self, player):
        for door in self.current_map.doors:
            if door.get("auto", False) or door.get("visible", True) is False:
                continue
            if player.rect.colliderect(door["rect"]):
                return door

        return None


    def check_auto_doors(self, player):
        if self.current_map_id == 0:
            return None

        for door in self.current_map.doors:
            if door.get("auto", False) and player.rect.colliderect(door["rect"]):
                return door

        return None

    def update(self, dt, player):
        """Update any level-specific animations (collapsing lift, etc.)."""
        self.update_moving_platforms(dt, player)
        self.update_collapsing_lift(dt, player)

    # Backward-friendly names for older code and beginner readability.
    def get_current_room(self):
        return self.get_current_map()

    def change_room(self, room_id, player, enemy):
        return self.change_map(room_id, player, enemy)

    def draw_current_room(self, screen):
        self.draw_current_map(screen, None)

    def get_current_platforms(self):
        return self.get_platforms()

    def get_current_fulcrums(self):
        return self.get_fulcrums()

    def reset_one_use_items(self):
        """Reset any one-time items (like fulcrums, altars, etc.) when restarting game."""
        for game_map in self.maps.values():
            for fulcrum in game_map.fulcrums:
                fulcrum["used"] = False

        self.map1_moon_altar_used = False
        self.map3_moon_altar_used = False
        self.map5_moon_altar_used = False
        self.map7_moon_altar_used = False

        self.reset_collapsing_lift()
        self.reset_current_moving_platforms()
        self.reset_current_collapsing_platforms()
