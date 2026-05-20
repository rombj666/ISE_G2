import math

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
    SCREEN_HEIGHT,
)
from src.levels.game_map import GameMap

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

def draw_level1_structures(screen, camera):
    """
    Big readable structures for Level 1.
    These make platforms look attached to buildings, roads, tram wrecks,
    balconies, bridges, and lab walls.
    Decoration only. No collision.
    """

    def apply_rect(rect):
        shifted_rect = pygame.Rect(rect.x + 4000, rect.y, rect.width, rect.height)
        if camera is not None:
            return camera.apply_rect(shifted_rect)
        return shifted_rect

    def apply_pos(pos):
        shifted_pos = (pos[0] + 4000, pos[1])
        if camera is not None:
            return camera.apply_pos(shifted_pos)
        return shifted_pos

    wall_back = (22, 25, 38)
    wall_mid = (36, 41, 58)
    wall_light = (58, 64, 82)
    metal = (72, 78, 96)
    dark = (10, 12, 20)
    glass = (42, 95, 125)
    glow = (90, 190, 240)
    warning = (210, 150, 70)

    # =====================================================
    # SECTION A: Body Pile & The Long Street (0 - 1500px)
    # Open Sky. Kael wakes up on ruined street ground.
    # Platforms are ROAD SLABS, not floating bars.
    # Every upper platform has a wall mass below it.
    # =====================================================

    # Main long ground — the street itself
    pygame.Rect(0, 650, 1500, 70),

    # Road slab 1: a broken chunk of raised pavement
    # Sits on top of the ground, not floating
    pygame.Rect(280, 612, 200, 38),    # low slab, hugs ground

    # Road slab 2: slightly higher, attached to a ruined wall section
    pygame.Rect(560, 575, 220, 38),    # mid slab

    # Road slab 3: higher broken road chunk
    pygame.Rect(900, 535, 200, 38),    # upper slab

    # Road slab 4: connector step before Section B gap
    pygame.Rect(1220, 570, 180, 38),   # descends back down

    # =====================================================
    # SECTION B: Destroyed Street (1500 - 4000px)
    # Two ground islands with a real gap between them.
    # Upper route uses ruined building FLOORS, not random bars.
    # =====================================================

    # Ground island 1 — right after the first gap
    pygame.Rect(1580, 650, 500, 70),

    # Ruined building floor 1 — low, attached to island wall
    pygame.Rect(1620, 600, 200, 38),

    # Ruined building floor 2 — steps up
    pygame.Rect(1900, 550, 220, 38),

    # Ruined building floor 3 — near top, like a broken 2nd storey
    pygame.Rect(2150, 490, 200, 38),

    # Ground island 2 — after a bigger traversal gap
    pygame.Rect(2450, 650, 1600, 70),

    # Stepping stones leading toward the Ruined Building interior
    # These are ROAD DEBRIS chunks, not abstract platforms
    pygame.Rect(2580, 600, 180, 38),
    pygame.Rect(2860, 545, 200, 38),
    pygame.Rect(3180, 490, 180, 38),
    pygame.Rect(3480, 545, 160, 38),

    # =====================================================
    # SECTION C: Collapsed Transit / Tram Route
    # =====================================================
    pygame.Rect(1580, 650, 650, 70),

    pygame.Rect(1650, 610, 180, 30),
    pygame.Rect(1860, 565, 200, 30),
    pygame.Rect(2080, 520, 180, 30),

    # =====================================================
    # SECTION D: Cracked Observatory Plaza
    # Observatory frame behind the plaza.
    # =====================================================
    pygame.draw.circle(screen, wall_mid, apply_pos((2220, 585)), 130, 14)
    pygame.draw.circle(screen, wall_back, apply_pos((2220, 585)), 92, 8)

    # broken telescope
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(2140, 505, 145, 20)))
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(2205, 525, 18, 80)))
    pygame.draw.circle(screen, glow, apply_pos((2295, 515)), 9)

    # supports for observatory balcony
    pygame.draw.rect(screen, wall_light, apply_rect(pygame.Rect(2110, 570, 24, 80)))
    pygame.draw.rect(screen, wall_light, apply_rect(pygame.Rect(2320, 570, 24, 80)))

    # =====================================================
    # SECTION E: House of Science Exterior
    # Large lab wall behind balconies/walkways.
    # =====================================================
    pygame.draw.rect(screen, wall_mid, apply_rect(pygame.Rect(2640, 370, 700, 280)))
    pygame.draw.rect(screen, wall_back, apply_rect(pygame.Rect(2640, 370, 700, 280)), 5)

    # lab windows/panels
    for wx in [2700, 2820, 2940, 3060, 3180]:
        pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(wx, 420, 54, 60)))
        pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(wx + 8, 430, 28, 4)))
        pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(wx, 525, 54, 60)))

    # pipes
    # for px in [2780, 3040, 3260]:
    #     pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(px, 385, 10, 265)))
    #     pygame.draw.rect(screen, glow, apply_rect(pygame.Rect(px - 4, 505, 18, 4)))

    # balcony support
    pygame.draw.rect(screen, wall_light, apply_rect(pygame.Rect(2880, 585, 260, 65)))
    pygame.draw.rect(screen, wall_back, apply_rect(pygame.Rect(2880, 585, 260, 65)), 3)

    # =====================================================
    # SECTION F: First Combat Courtyard
    # Wide courtyard wall and pillars.
    # =====================================================
    pygame.draw.rect(screen, wall_mid, apply_rect(pygame.Rect(3340, 440, 700, 210)))
    pygame.draw.rect(screen, wall_back, apply_rect(pygame.Rect(3340, 440, 700, 210)), 5)

    # large pillars
    for px in [3420, 3900]:
        pygame.draw.rect(screen, wall_light, apply_rect(pygame.Rect(px, 515, 52, 135)))
        pygame.draw.rect(screen, wall_back, apply_rect(pygame.Rect(px, 515, 52, 135)), 3)

    # balcony wall under upper platform
    pygame.draw.rect(screen, wall_light, apply_rect(pygame.Rect(3520, 575, 300, 75)))
    pygame.draw.rect(screen, wall_back, apply_rect(pygame.Rect(3520, 575, 300, 75)), 3)

    # =====================================================
    # SECTION G: Fallen Research Tower
    # Tower mass supporting vertical platforms.
    # =====================================================
    tower_blocks = [
        pygame.Rect(4100, 560, 220, 90),
        pygame.Rect(4250, 505, 230, 145),
        pygame.Rect(4400, 450, 230, 200),
    ]

    for block in tower_blocks:
        pygame.draw.rect(screen, wall_mid, apply_rect(block))
        pygame.draw.rect(screen, wall_back, apply_rect(block), 4)

    # broken antenna/device
    pygame.draw.line(screen, metal, apply_pos((4550, 445)), apply_pos((4610, 365)), 5)
    pygame.draw.circle(screen, glow, apply_pos((4615, 360)), 8)

    # =====================================================
    # SECTION H: Lab Entrance + SHOP Area
    # Big lab doorway and supply zone.
    # =====================================================
    pygame.draw.rect(screen, wall_mid, apply_rect(pygame.Rect(4620, 440, 520, 210)))
    pygame.draw.rect(screen, wall_back, apply_rect(pygame.Rect(4620, 440, 520, 210)), 5)

    # lab entrance door
    pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(4665, 520, 120, 130)))
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(4665, 520, 120, 130)), 4)
    pygame.draw.rect(screen, glow, apply_rect(pygame.Rect(4685, 540, 80, 5)))

    # SHOP structure/sign
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(4785, 500, 120, 30)))
    pygame.draw.rect(screen, warning, apply_rect(pygame.Rect(4810, 512, 62, 4)))

    # upper lab walkway support
    pygame.draw.rect(screen, wall_light, apply_rect(pygame.Rect(4860, 585, 230, 65)))
    pygame.draw.rect(screen, wall_back, apply_rect(pygame.Rect(4860, 585, 230, 65)), 3)

    # =====================================================
    # SECTION I: Collapsed City Route
    # Bridge supports and final rest gate.
    # =====================================================
    for bx in [5220, 5420]:
        pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(bx + 35, 585, 12, 65)))
        pygame.draw.line(screen, metal, apply_pos((bx + 35, 620)), apply_pos((bx + 130, 650)), 4)
        pygame.draw.line(screen, metal, apply_pos((bx + 130, 620)), apply_pos((bx + 35, 650)), 4)

    # final rest-area entrance
    pygame.draw.rect(screen, wall_mid, apply_rect(pygame.Rect(5400, 470, 190, 180)))
    pygame.draw.rect(screen, wall_back, apply_rect(pygame.Rect(5400, 470, 190, 180)), 5)
    pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(5460, 540, 80, 110)))
    pygame.draw.rect(screen, warning, apply_rect(pygame.Rect(5425, 500, 130, 6)))

def draw_level1_props(screen, camera):
    """
    Draws section-specific props for Level 1.
    These are visual decorations only.
    They help the map feel like a ruined city/science district instead of empty platforms.
    """

    def apply_rect(rect):
        shifted_rect = pygame.Rect(rect.x + 4000, rect.y, rect.width, rect.height)
        if camera is not None:
            return camera.apply_rect(shifted_rect)
        return shifted_rect

    def apply_pos(pos):
        shifted_pos = (pos[0] + 4000, pos[1])
        if camera is not None:
            return camera.apply_pos(shifted_pos)
        return shifted_pos

    dark = (16, 18, 26)
    metal = (75, 82, 100)
    metal_dark = (45, 50, 65)
    stone = (68, 70, 84)
    glow = (90, 200, 245)
    blood = (85, 25, 32)
    warning = (220, 160, 70)
    glass = (70, 150, 190)

    # =====================================================
    # SECTION A: Body pile outside / street damage
    # =====================================================

    # cracked road marks near start
    for x in [90, 180, 320, 430]:
        pygame.draw.line(screen, dark, apply_pos((x, 642)), apply_pos((x + 30, 650)), 3)
        pygame.draw.line(screen, dark, apply_pos((x + 18, 646)), apply_pos((x + 10, 655)), 2)

    # broken science sign on ground
    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(360, 625, 90, 16)))
    pygame.draw.rect(screen, glow, apply_rect(pygame.Rect(370, 630, 38, 3)))

    # small blood trail leading away from body pile
    pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(210, 640, 22, 4)))
    pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(250, 645, 16, 3)))
    pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(285, 638, 26, 4)))

    # =====================================================
    # SECTION B: Destroyed street
    # =====================================================

    # fallen street lamp
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(720, 625, 95, 6)))
    pygame.draw.circle(screen, warning, apply_pos((820, 626)), 7)
    pygame.draw.line(screen, metal, apply_pos((720, 625)), apply_pos((690, 650)), 4)

    # rubble piles
    for x, y in [(610, 635), (980, 635), (1080, 635)]:
        pygame.draw.rect(screen, stone, apply_rect(pygame.Rect(x, y, 22, 10)))
        pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(x + 18, y + 4, 16, 8)))
        pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(x + 5, y + 10, 28, 5)))

    # broken warning board
    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(1030, 575, 70, 34)))
    pygame.draw.rect(screen, warning, apply_rect(pygame.Rect(1040, 586, 42, 5)))
    pygame.draw.line(screen, dark, apply_pos((1095, 575)), apply_pos((1105, 609)), 3)

    # =====================================================
    # SECTION C: Lunar tram wreck
    # =====================================================

    # tram wheels
    for x in [1310, 1430, 1550, 1670]:
        pygame.draw.circle(screen, dark, apply_pos((x, 650)), 14)
        pygame.draw.circle(screen, metal, apply_pos((x, 650)), 6)

    # sparking cable on tram
    pygame.draw.line(screen, metal, apply_pos((1360, 590)), apply_pos((1460, 610)), 3)
    pygame.draw.line(screen, glow, apply_pos((1455, 608)), apply_pos((1480, 595)), 2)

    # broken glass pieces
    for x in [1285, 1340, 1610, 1695]:
        pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(x, 635, 12, 3)))

    # =====================================================
    # SECTION D: Observatory plaza
    # =====================================================

    # cracked moon symbol on ground
    pygame.draw.circle(screen, metal_dark, apply_pos((2050, 640)), 42, 3)
    pygame.draw.line(screen, glow, apply_pos((2015, 640)), apply_pos((2085, 640)), 2)
    pygame.draw.line(screen, glow, apply_pos((2050, 605)), apply_pos((2050, 675)), 2)
    pygame.draw.line(screen, dark, apply_pos((2030, 625)), apply_pos((2065, 655)), 3)

    # fallen telescope parts
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(2180, 626, 90, 12)))
    pygame.draw.circle(screen, glass, apply_pos((2275, 632)), 9)

    # =====================================================
    # SECTION E/F: Science district exterior + combat courtyard
    # =====================================================

    # lab panels and pipes
    for x in [2580, 2740, 2920, 3090]:
        pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(x, 622, 70, 22)))
        pygame.draw.rect(screen, glow, apply_rect(pygame.Rect(x + 10, 630, 35, 4)))

    # warning floor stains / lunar burns
    for x in [3150, 3330, 3520]:
        pygame.draw.rect(screen, blood, apply_rect(pygame.Rect(x, 640, 34, 4)))
        pygame.draw.rect(screen, glow, apply_rect(pygame.Rect(x + 8, 635, 18, 2)))

    # broken pillar chunks
    for x in [3060, 3600]:
        pygame.draw.rect(screen, stone, apply_rect(pygame.Rect(x, 610, 38, 40)))
        pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(x + 6, 620, 24, 6)))

    # =====================================================
    # SECTION G: Fallen research tower
    # =====================================================

    # fallen antenna pieces
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(3860, 630, 120, 5)))
    pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(3975, 610, 80, 5)))
    pygame.draw.circle(screen, glow, apply_pos((4058, 612)), 5)

    # broken experiment containers
    for x in [3780, 4140]:
        pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(x, 615, 26, 32)))
        pygame.draw.rect(screen, glow, apply_rect(pygame.Rect(x + 5, 622, 16, 4)))

    # =====================================================
    # SECTION H: Lab entrance + SHOP area
    # =====================================================

    # supply crates near shop
    for x in [4385, 4620, 4670]:
        pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(x, 620, 42, 30)))
        pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(x + 5, 626, 32, 4)))
        pygame.draw.line(screen, dark, apply_pos((x, 635)), apply_pos((x + 42, 635)), 2)

    # hanging wire near lab entrance
    pygame.draw.line(screen, metal, apply_pos((4300, 480)), apply_pos((4380, 520)), 3)
    pygame.draw.line(screen, metal, apply_pos((4380, 520)), apply_pos((4460, 500)), 3)

    # small shop arrow/light
    pygame.draw.rect(screen, warning, apply_rect(pygame.Rect(4460, 488, 70, 8)))
    pygame.draw.rect(screen, glow, apply_rect(pygame.Rect(4480, 498, 28, 4)))

    # =====================================================
    # SECTION I: Collapsed city route / rest entrance
    # =====================================================

    # bridge debris
    for x in [4860, 5010, 5200, 5370]:
        pygame.draw.rect(screen, stone, apply_rect(pygame.Rect(x, 635, 35, 12)))
        pygame.draw.rect(screen, dark, apply_rect(pygame.Rect(x + 6, 642, 25, 5)))

    # rest entrance marker lights
    pygame.draw.rect(screen, warning, apply_rect(pygame.Rect(5405, 520, 18, 40)))
    pygame.draw.rect(screen, warning, apply_rect(pygame.Rect(5500, 520, 18, 40)))
    pygame.draw.rect(screen, glow, apply_rect(pygame.Rect(5420, 500, 78, 4)))

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

def draw_level1_platform_backings(screen, camera, game_map):
    """
    Draws thick wall/body support under upper platforms.
    This makes ledges look like broken building floors instead of floating bars.
    No thin support lines.
    """

    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    wall = (33, 38, 56)
    wall_dark = (18, 21, 32)
    window = (8, 10, 18)

    ground_y = 650

    for platform in game_map.platforms:
        # Only support upper/mid platforms, not main ground
        if platform.y >= 635:
            continue

        # Ignore very small connector steps
        if platform.width < 120:
            continue

        # Skip ceiling slabs — drawing a column under them would fill the whole room
        if platform.y < 260:
            continue

        # Do not draw backing for safety floor
        if platform.height <= 20 and platform.y > 680:
            continue

        # =========================================================
        # STRUCTURAL FIX: EXCLUSION ZONES (TRUE SCALE)
        # =========================================================
        is_floating_structure = False

        # SECTION 4: Collapsed Transit / Tram Wreck (Pushed way back)
        if 6000 <= platform.x <= 8000:
            is_floating_structure = True

        # SECTION 5 & 6: Lab Balconies & Courtyard Ledges
        if 8000 <= platform.x <= 12000:
            is_floating_structure = True

        # SECTION 9: Broken Bridge Pieces
        if 14000 <= platform.x <= 15500:
            is_floating_structure = True

        # If it's a vehicle or bridge, skip drawing the solid wall backing!
        if is_floating_structure:
            continue

        # =========================================================

        backing_height = ground_y - platform.bottom

        # If platform is too close to ground, no need for backing
        if backing_height < 35:
            continue

        backing = pygame.Rect(
            platform.x,
            platform.bottom,
            platform.width,
            backing_height
        )

        pygame.draw.rect(screen, wall, apply_rect(backing))
        pygame.draw.rect(screen, wall_dark, apply_rect(backing), 3)

        # Add simple dark window/panel holes so it looks like a building chunk
        if backing.height > 70:
            for x in range(backing.x + 30, backing.right - 30, 90):
                pygame.draw.rect(
                    screen,
                    window,
                    apply_rect(pygame.Rect(x, backing.y + 25, 26, 42))
                )

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

def draw_section5_science_buildings(screen, camera):
    """
    Section 5 (x=5100-6400): Science District lab buildings.
    Drawn BEHIND the platforms — each platform reads as a balcony sticking out
    of its building. Buildings have window grids, antennas, and connecting cables.
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
    body_a       = (26, 30, 46)
    body_b       = (34, 40, 58)
    top_trim     = (52, 60, 82)
    edge         = (60, 70, 92)
    window_lit   = (95, 200, 245)
    window_dim   = (35, 80, 130)
    window_dark  = (12, 16, 26)
    window_frame = (50, 60, 82)
    antenna      = (62, 68, 86)
    antenna_dark = (28, 32, 45)
    antenna_red  = (255, 90, 80)
    antenna_glow = (255, 200, 180)
    cable        = (28, 30, 42)
    sign_bg      = (55, 65, 90)
    sign_text    = (200, 230, 250)

    def draw_window(x, y, w=28, h=34, lit=True, has_cross=True):
        pygame.draw.rect(screen, window_frame, apply_rect(pygame.Rect(x, y, w, h)))
        glass = window_lit if lit else window_dim
        pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(x + 3, y + 3, w - 6, h - 6)))
        if has_cross:
            pygame.draw.rect(screen, window_dark,
                             apply_rect(pygame.Rect(x + (w // 2) - 1, y + 3, 2, h - 6)))
            pygame.draw.rect(screen, window_dark,
                             apply_rect(pygame.Rect(x + 3, y + (h // 2) - 1, w - 6, 2)))

    def draw_window_grid(b, cols, rows, win_w=28, win_h=34, h_pad=22, v_pad=22):
        avail_w = b.width - h_pad * 2 - cols * win_w
        avail_h = b.height - v_pad * 2 - rows * win_h
        gap_x = avail_w // max(1, cols - 1) if cols > 1 else 0
        gap_y = avail_h // max(1, rows - 1) if rows > 1 else 0
        for col in range(cols):
            for row in range(rows):
                wx = b.x + h_pad + col * (win_w + gap_x)
                wy = b.y + v_pad + row * (win_h + gap_y)
                lit = ((col + row * 3) % 5) != 0
                draw_window(wx, wy, win_w, win_h, lit=lit)

    def draw_building(b, body_color, top_color):
        pygame.draw.rect(screen, body_color, apply_rect(b))
        pygame.draw.rect(screen, top_color, apply_rect(pygame.Rect(b.x, b.y, b.width, 6)))
        pygame.draw.rect(screen, body_a, apply_rect(pygame.Rect(b.right - 5, b.y, 5, b.height)))
        pygame.draw.rect(screen, edge, apply_rect(pygame.Rect(b.x, b.y + 6, b.width, 2)))

    # ─── Building 1 (Lab A — medium) ───────────────────────────────────
    b1 = pygame.Rect(4970, 320, 240, 330)
    draw_building(b1, body_a, top_trim)
    draw_window_grid(b1, cols=3, rows=4)
    pygame.draw.rect(screen, sign_bg, apply_rect(pygame.Rect(b1.x + 80, b1.y + 12, 80, 14)))
    pygame.draw.rect(screen, sign_text, apply_rect(pygame.Rect(b1.x + 86, b1.y + 17, 6, 4)))
    pygame.draw.rect(screen, sign_text, apply_rect(pygame.Rect(b1.x + 98, b1.y + 17, 16, 4)))
    pygame.draw.rect(screen, sign_text, apply_rect(pygame.Rect(b1.x + 120, b1.y + 17, 4, 4)))
    # Roof vent
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b1.x + 30, b1.y - 18, 16, 18)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b1.x + 28, b1.y - 22, 20, 6)))

    # ─── Building 2 (Lab B — TALL) ─────────────────────────────────────
    b2 = pygame.Rect(5340, 150, 320, 500)
    draw_building(b2, body_b, top_trim)
    draw_window_grid(b2, cols=4, rows=7)
    # Central tall antenna with cross-bars + red beacon
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b2.centerx - 3, b2.y - 70, 6, 70)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b2.centerx - 16, b2.y - 60, 32, 4)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b2.centerx - 14, b2.y - 45, 28, 4)))
    pygame.draw.circle(screen, antenna_red, apply_pos((b2.centerx, b2.y - 70)), 3)
    pygame.draw.circle(screen, antenna_glow, apply_pos((b2.centerx, b2.y - 70)), 1)
    # Side antenna
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b2.right - 50, b2.y - 36, 4, 36)))
    pygame.draw.circle(screen, antenna_red, apply_pos((b2.right - 48, b2.y - 36)), 2)
    # Roof access door
    pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(b2.x + 40, b2.y - 22, 28, 22)))
    pygame.draw.rect(screen, edge, apply_rect(pygame.Rect(b2.x + 40, b2.y - 22, 28, 22)), 1)

    # ─── Building 3 (medium-tall) ──────────────────────────────────────
    b3 = pygame.Rect(5760, 200, 280, 450)
    draw_building(b3, body_a, top_trim)
    draw_window_grid(b3, cols=4, rows=6)
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b3.x + 50, b3.y - 32, 12, 32)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b3.x + 46, b3.y - 36, 20, 6)))
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b3.right - 60, b3.y - 26, 12, 26)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b3.right - 64, b3.y - 30, 20, 6)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b3.x + 100, b3.y, 30, 8)))

    # ─── Building 4 (Lab D — TALLEST) ──────────────────────────────────
    b4 = pygame.Rect(6160, 100, 280, 550)
    draw_building(b4, body_b, top_trim)
    draw_window_grid(b4, cols=4, rows=8)
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b4.x + 40, b4.y - 80, 4, 80)))
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b4.x + 130, b4.y - 60, 6, 60)))
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b4.x + 220, b4.y - 70, 4, 70)))
    pygame.draw.circle(screen, antenna_red, apply_pos((b4.x + 42, b4.y - 80)), 2)
    pygame.draw.circle(screen, antenna_red, apply_pos((b4.x + 133, b4.y - 60)), 3)
    pygame.draw.circle(screen, antenna_glow, apply_pos((b4.x + 133, b4.y - 60)), 1)
    pygame.draw.circle(screen, antenna_red, apply_pos((b4.x + 222, b4.y - 70)), 2)
    pygame.draw.line(screen, cable, apply_pos((b4.x + 42, b4.y - 80)),
                     apply_pos((b4.x + 133, b4.y - 60)), 1)

    # ─── Building 5 (medium) ───────────────────────────────────────────
    b5 = pygame.Rect(6560, 180, 240, 470)
    draw_building(b5, body_a, top_trim)
    draw_window_grid(b5, cols=3, rows=7)
    # Satellite dish
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b5.centerx - 2, b5.y - 38, 4, 38)))
    pygame.draw.arc(screen, antenna,
                    apply_rect(pygame.Rect(b5.centerx - 26, b5.y - 60, 52, 42)),
                    3.14, 6.28, 5)
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b5.centerx - 4, b5.y - 50, 8, 12)))
    # Chimney
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b5.x + 30, b5.y - 20, 18, 20)))
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b5.x + 28, b5.y - 24, 22, 6)))

    # ─── Connecting cables between buildings ───────────────────────────
    pygame.draw.line(screen, cable, apply_pos((b1.right - 30, b1.y + 14)),
                     apply_pos((b2.x + 30, b2.y + 60)), 2)
    pygame.draw.line(screen, cable, apply_pos((b2.right - 30, b2.y + 80)),
                     apply_pos((b3.x + 30, b3.y + 30)), 2)
    pygame.draw.line(screen, cable, apply_pos((b3.right - 30, b3.y + 40)),
                     apply_pos((b4.x + 30, b4.y + 80)), 2)
    pygame.draw.line(screen, cable, apply_pos((b4.right - 30, b4.y + 60)),
                     apply_pos((b5.x + 30, b5.y + 30)), 2)


def draw_section6_courtyard_buildings(screen, camera):
    """
    Section 6 (x=6400-7600): First Combat Courtyard — rooftop-hopping arena.
    Each platform is the rooftop of a building. Buildings extend from rooftop
    DOWN to the street, with window grids + per-building decorations
    (lantern, shed, antennas, exit spire).
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
    body_a       = (26, 30, 46)
    body_b       = (34, 40, 58)
    top_trim     = (52, 60, 82)
    edge         = (60, 70, 92)
    window_lit   = (95, 200, 245)
    window_dim   = (35, 80, 130)
    window_dark  = (12, 16, 26)
    window_frame = (50, 60, 82)
    antenna      = (62, 68, 86)
    antenna_dark = (28, 32, 45)
    antenna_red  = (255, 90, 80)
    antenna_glow = (255, 200, 180)
    cable        = (28, 30, 42)
    lamp_post    = (60, 65, 80)
    lamp_glow    = (255, 200, 80)
    lamp_core    = (255, 240, 160)
    shed_brown   = (90, 60, 38)
    shed_dark    = (55, 35, 22)
    shed_roof    = (62, 42, 28)
    exit_marker  = (90, 230, 130)

    def draw_window(x, y, w=26, h=32, lit=True):
        pygame.draw.rect(screen, window_frame, apply_rect(pygame.Rect(x, y, w, h)))
        glass = window_lit if lit else window_dim
        pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(x + 3, y + 3, w - 6, h - 6)))
        pygame.draw.rect(screen, window_dark,
                         apply_rect(pygame.Rect(x + (w // 2) - 1, y + 3, 2, h - 6)))
        pygame.draw.rect(screen, window_dark,
                         apply_rect(pygame.Rect(x + 3, y + (h // 2) - 1, w - 6, 2)))

    def draw_window_grid(b, cols, rows, win_w=26, win_h=32, h_pad=18, v_pad=22):
        avail_w = b.width - h_pad * 2 - cols * win_w
        avail_h = b.height - v_pad * 2 - rows * win_h
        gap_x = avail_w // max(1, cols - 1) if cols > 1 else 0
        gap_y = avail_h // max(1, rows - 1) if rows > 1 else 0
        for col in range(cols):
            for row in range(rows):
                wx = b.x + h_pad + col * (win_w + gap_x)
                wy = b.y + v_pad + row * (win_h + gap_y)
                lit = ((col + row * 2) % 4) != 0
                draw_window(wx, wy, win_w, win_h, lit=lit)

    def draw_building(b, body_color, top_color):
        pygame.draw.rect(screen, body_color, apply_rect(b))
        pygame.draw.rect(screen, top_color, apply_rect(pygame.Rect(b.x, b.y, b.width, 6)))
        pygame.draw.rect(screen, body_a, apply_rect(pygame.Rect(b.right - 5, b.y, 5, b.height)))
        pygame.draw.rect(screen, edge, apply_rect(pygame.Rect(b.x, b.y + 6, b.width, 2)))

    # ─── Building 1 (Rooftop A — first hop) ────────────────────────────
    b1 = pygame.Rect(6780, 180, 130, 470)
    draw_building(b1, body_a, top_trim)
    draw_window_grid(b1, cols=2, rows=7)
    # Yellow lantern on the rooftop edge
    lamp_x = b1.x + 22
    pygame.draw.rect(screen, lamp_post, apply_rect(pygame.Rect(lamp_x, b1.y - 26, 4, 26)))
    pygame.draw.rect(screen, lamp_post, apply_rect(pygame.Rect(lamp_x - 7, b1.y - 30, 18, 6)))
    pygame.draw.circle(screen, lamp_glow, apply_pos((lamp_x + 2, b1.y - 36)), 6)
    pygame.draw.circle(screen, lamp_core, apply_pos((lamp_x + 2, b1.y - 36)), 3)
    # Small AC unit on roof
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b1.x + 80, b1.y - 14, 26, 14)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b1.x + 80, b1.y - 14, 26, 14)), 1)

    # ─── Building 2 (Tactical block 1) ─────────────────────────────────
    b2 = pygame.Rect(6880, 200, 180, 450)
    draw_building(b2, body_b, top_trim)
    draw_window_grid(b2, cols=3, rows=6)
    # Vent stack on roof
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b2.x + 40, b2.y - 20, 14, 20)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b2.x + 36, b2.y - 24, 22, 6)))

    # ─── Building 3 (Step up / Tallest — main central) ─────────────────
    b3 = pygame.Rect(7030, 150, 330, 500)
    draw_building(b3, body_a, top_trim)
    draw_window_grid(b3, cols=4, rows=7)
    # Brown rooftop SHED — matches the collision rect at (7100, 100, 100, 60)
    shed = pygame.Rect(7100, 100, 100, 60)
    pygame.draw.rect(screen, shed_brown, apply_rect(shed))
    pygame.draw.rect(screen, shed_roof, apply_rect(pygame.Rect(shed.x - 4, shed.y - 6, shed.width + 8, 10)))
    pygame.draw.rect(screen, shed_dark, apply_rect(shed), 2)
    # Shed door + window
    pygame.draw.rect(screen, shed_dark, apply_rect(pygame.Rect(shed.x + 14, shed.y + 20, 18, 38)))
    pygame.draw.rect(screen, (180, 150, 80), apply_rect(pygame.Rect(shed.x + 26, shed.y + 38, 4, 4)))
    pygame.draw.rect(screen, lamp_glow, apply_rect(pygame.Rect(shed.x + 50, shed.y + 20, 22, 18)))
    pygame.draw.rect(screen, shed_dark, apply_rect(pygame.Rect(shed.x + 50, shed.y + 20, 22, 18)), 1)
    # Tall antenna on the right side of building 3
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(b3.right - 50, b3.y - 80, 5, 80)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b3.right - 60, b3.y - 60, 25, 4)))
    pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(b3.right - 60, b3.y - 40, 25, 4)))
    pygame.draw.circle(screen, antenna_red, apply_pos((b3.right - 48, b3.y - 80)), 3)
    pygame.draw.circle(screen, antenna_glow, apply_pos((b3.right - 48, b3.y - 80)), 1)

    # ─── Building 4 (Cover right / EXIT building) ──────────────────────
    b4 = pygame.Rect(7310, 250, 150, 400)
    draw_building(b4, body_b, top_trim)
    draw_window_grid(b4, cols=2, rows=6)
    # Exit marker on rooftop (green glow signals "this way out")
    pygame.draw.rect(screen, exit_marker, apply_rect(pygame.Rect(b4.x + 60, b4.y - 12, 30, 4)))
    pygame.draw.rect(screen, (40, 120, 70), apply_rect(pygame.Rect(b4.x + 60, b4.y - 12, 30, 4)), 1)
    # TALL antenna SPIRE — iconic skyline element on the right side
    spire_x = b4.right - 12
    pygame.draw.rect(screen, antenna, apply_rect(pygame.Rect(spire_x, b4.y - 230, 5, 230)))
    for cy in [b4.y - 200, b4.y - 160, b4.y - 120, b4.y - 80, b4.y - 40]:
        pygame.draw.rect(screen, antenna_dark, apply_rect(pygame.Rect(spire_x - 8, cy, 21, 3)))
    pygame.draw.circle(screen, antenna_red, apply_pos((spire_x + 2, b4.y - 230)), 4)
    pygame.draw.circle(screen, antenna_glow, apply_pos((spire_x + 2, b4.y - 230)), 2)

    # ─── Connecting cables between buildings ───────────────────────────
    pygame.draw.line(screen, cable, apply_pos((b1.right - 20, b1.y + 30)),
                     apply_pos((b2.x + 30, b2.y + 50)), 2)
    pygame.draw.line(screen, cable, apply_pos((b2.right - 30, b2.y + 60)),
                     apply_pos((b3.x + 30, b3.y + 40)), 2)
    pygame.draw.line(screen, cable, apply_pos((b3.right - 50, b3.y + 50)),
                     apply_pos((b4.x + 30, b4.y + 40)), 2)


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


def draw_section7_lab_entrance_details(screen, camera):
    """
    Section 7 (x=7600-9620): Messy Lab Entrance — interior overlay details.
    Drawn AFTER platforms so the windows, chains, signs, pipes, and lamps
    layer on top of the platform stone visuals.
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
    window_lit   = (95, 200, 245)
    window_dim   = (35, 80, 130)
    window_dark  = (12, 16, 26)
    window_frame = (50, 60, 82)
    chain        = (60, 50, 40)
    chain_link   = (88, 80, 64)
    chain_hook   = (110, 100, 80)
    lamp_post    = (60, 65, 80)
    lamp_glow    = (255, 200, 80)
    lamp_core    = (255, 240, 160)
    lamp_dim     = (140, 110, 50)
    danger_red   = (200, 55, 45)
    warning_yel  = (210, 175, 60)
    sign_bg      = (38, 44, 60)
    sign_border  = (90, 100, 120)
    sign_text    = (220, 235, 250)
    pipe         = (78, 82, 96)
    pipe_dark    = (40, 45, 60)
    pipe_joint   = (54, 58, 72)
    steam        = (90, 95, 110)
    steam_light  = (130, 135, 148)
    grate        = (45, 50, 65)
    grate_dark   = (22, 26, 36)
    exit_green   = (90, 230, 130)
    exit_dim     = (40, 120, 70)
    door_dark    = (10, 13, 22)
    rust         = (130, 70, 40)

    # ─── 1. Arch Doorway with hanging chains (x=7600-7700) ─────────────
    # Chains hanging from the ceiling (y=230) down to the floor level (y=380).
    # 6 chains tightly spaced — forms a "grated archway" visual.
    chain_columns = [
        (7610, 380), (7625, 405), (7640, 380), (7655, 412),
        (7670, 380), (7685, 405),
    ]
    for cx, bot_y in chain_columns:
        top_y = 230
        # Hook attaching chain to ceiling
        pygame.draw.rect(screen, chain_hook, apply_rect(pygame.Rect(cx - 4, top_y - 2, 12, 8)))
        # Rope spine
        pygame.draw.rect(screen, chain, apply_rect(pygame.Rect(cx, top_y, 3, bot_y - top_y)))
        # Chain links along the spine
        for ly in range(top_y + 10, bot_y - 4, 14):
            pygame.draw.rect(screen, chain_link, apply_rect(pygame.Rect(cx - 3, ly, 9, 6)))
        # Weight/hook at the bottom
        pygame.draw.rect(screen, chain_hook, apply_rect(pygame.Rect(cx - 5, bot_y - 6, 13, 8)))

    # ─── 2. Main building windows (x=7700-8300, y=380-660) ─────────────
    # The big block at (7700, 380, 600, 280) is the lab building exterior.
    # Draw 2 rows × 5 cols of lit lab windows on its FRONT face.
    main_x, main_y, main_w, main_h = 7700, 380, 600, 280
    # Top trim line
    pygame.draw.rect(screen, sign_border, apply_rect(pygame.Rect(main_x, main_y + 8, main_w, 2)))
    for col in range(5):
        for row in range(2):
            wx = main_x + 40 + col * 110
            wy = main_y + 40 + row * 110
            # Frame
            pygame.draw.rect(screen, window_frame, apply_rect(pygame.Rect(wx, wy, 40, 64)))
            # Glass — alternate lit/dim
            lit = ((col + row * 2) % 3) != 0
            glass = window_lit if lit else window_dim
            pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(wx + 4, wy + 4, 32, 56)))
            # Cross mullion
            pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx + 19, wy + 4, 2, 56)))
            pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx + 4, wy + 31, 32, 2)))
            # Bottom-left scientific equipment silhouette in some lit windows
            if lit and (col + row) % 2 == 0:
                pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx + 8, wy + 40, 6, 16)))
                pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx + 22, wy + 36, 8, 20)))

    # Big "LAB SECTOR 7 — DANGER" sign on the front
    sg_x, sg_y = main_x + 200, main_y + 16
    pygame.draw.rect(screen, sign_bg, apply_rect(pygame.Rect(sg_x, sg_y, 220, 20)))
    pygame.draw.rect(screen, sign_border, apply_rect(pygame.Rect(sg_x, sg_y, 220, 20)), 1)
    pygame.draw.rect(screen, danger_red, apply_rect(pygame.Rect(sg_x, sg_y, 220, 4)))
    # Stylized text bars
    for tb_x, tb_w in [(sg_x + 14, 24), (sg_x + 44, 14), (sg_x + 64, 28), (sg_x + 100, 16),
                       (sg_x + 124, 30), (sg_x + 162, 12), (sg_x + 180, 26)]:
        pygame.draw.rect(screen, sign_text, apply_rect(pygame.Rect(tb_x, sg_y + 9, tb_w, 6)))

    # ─── 3. Upper facade windows (x=7600-8300, y=0-230) ────────────────
    # Windows in the upper wall (ceiling block facade)
    ceiling_x, ceiling_y, ceiling_w = 7600, 0, 700
    for col in range(6):
        wx = ceiling_x + 40 + col * 105
        wy = 130
        pygame.draw.rect(screen, window_frame, apply_rect(pygame.Rect(wx, wy, 34, 50)))
        lit = (col % 2 == 0)
        pygame.draw.rect(screen, window_lit if lit else window_dim,
                         apply_rect(pygame.Rect(wx + 4, wy + 4, 26, 42)))
        pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx + 16, wy + 4, 2, 42)))
    # Big "LAB ENTRANCE" sign on upper facade
    us_x, us_y = ceiling_x + 200, 50
    pygame.draw.rect(screen, sign_bg, apply_rect(pygame.Rect(us_x, us_y, 300, 38)))
    pygame.draw.rect(screen, sign_border, apply_rect(pygame.Rect(us_x, us_y, 300, 38)), 2)
    pygame.draw.rect(screen, warning_yel, apply_rect(pygame.Rect(us_x, us_y, 300, 5)))
    pygame.draw.rect(screen, danger_red, apply_rect(pygame.Rect(us_x, us_y + 33, 300, 5)))
    # Stylized "LAB ENTRANCE" letters
    for ltr_x in [us_x + 20, us_x + 50, us_x + 84, us_x + 120, us_x + 162, us_x + 196, us_x + 230, us_x + 264]:
        pygame.draw.rect(screen, sign_text, apply_rect(pygame.Rect(ltr_x, us_y + 14, 18, 12)))

    # ─── 4. Ceiling pipes running across the corridor ──────────────────
    # Main pipe along the ceiling (just below y=230)
    pygame.draw.rect(screen, pipe, apply_rect(pygame.Rect(7700, 232, 1900, 8)))
    pygame.draw.rect(screen, pipe_dark, apply_rect(pygame.Rect(7700, 240, 1900, 3)))
    # Pipe joints every 200px
    for jx in range(7800, 9620, 200):
        pygame.draw.rect(screen, pipe_joint, apply_rect(pygame.Rect(jx, 228, 12, 16)))
    # Smaller secondary pipe slightly below
    pygame.draw.rect(screen, pipe_dark, apply_rect(pygame.Rect(7700, 258, 1900, 4)))

    # ─── 5. Hanging lamps in the corridor ──────────────────────────────
    for lx in [7780, 8050, 8400, 8650, 8920, 9100, 9320, 9520]:
        # Cable from ceiling pipe
        pygame.draw.rect(screen, chain, apply_rect(pygame.Rect(lx, 262, 2, 22)))
        # Lamp body
        pygame.draw.rect(screen, lamp_post, apply_rect(pygame.Rect(lx - 8, 284, 18, 8)))
        pygame.draw.rect(screen, pipe_dark, apply_rect(pygame.Rect(lx - 8, 284, 18, 8)), 1)
        # Lamp glow
        pygame.draw.circle(screen, lamp_glow, apply_pos((lx, 296)), 5)
        pygame.draw.circle(screen, lamp_core, apply_pos((lx, 296)), 2)
        # Halo
        halo = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 200, 80, 40), (14, 14), 14)
        if camera is not None:
            screen.blit(halo, camera.apply_pos((lx - 14, 282)))
        else:
            screen.blit(halo, (lx - 14, 282))

    # ─── 6. Bridge area: vertical chains between upper and lower segments ──
    # Bridge segments span x=8300-8740. Chains hang between upper (y~200) and lower (y~340).
    bridge_chain_xs = [8310, 8330, 8395, 8420, 8460, 8490, 8540, 8575, 8615, 8650, 8690, 8720]
    for bcx in bridge_chain_xs:
        pygame.draw.rect(screen, chain, apply_rect(pygame.Rect(bcx, 220, 2, 100)))
        for ly in range(228, 320, 14):
            pygame.draw.rect(screen, chain_link, apply_rect(pygame.Rect(bcx - 2, ly, 6, 5)))

    # Light fixtures on the upper bridge segments (small spotlights pointing down)
    for sx in [8330, 8480, 8620]:
        pygame.draw.rect(screen, lamp_post, apply_rect(pygame.Rect(sx, 200, 16, 6)))
        pygame.draw.polygon(screen, lamp_dim, [
            apply_pos((sx + 2, 206)), apply_pos((sx + 14, 206)),
            apply_pos((sx + 18, 240)), apply_pos((sx - 2, 240)),
        ])
        pygame.draw.circle(screen, lamp_glow, apply_pos((sx + 8, 210)), 3)

    # ─── 7. After-bridge wall windows (x=8740-8860) ────────────────────
    # Windows on the upper wall (8740, 0, 120, 230)
    pygame.draw.rect(screen, window_frame, apply_rect(pygame.Rect(8770, 90, 36, 56)))
    pygame.draw.rect(screen, window_lit, apply_rect(pygame.Rect(8774, 94, 28, 48)))
    pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(8788, 94, 2, 48)))
    pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(8774, 117, 28, 2)))
    # Windows on the lower wall (8740, 380, 120, 330)
    for row in range(3):
        wy = 410 + row * 80
        pygame.draw.rect(screen, window_frame, apply_rect(pygame.Rect(8770, wy, 36, 50)))
        pygame.draw.rect(screen, window_lit if row != 1 else window_dim,
                         apply_rect(pygame.Rect(8774, wy + 4, 28, 42)))
        pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(8788, wy + 4, 2, 42)))

    # ─── 8. Central pillar banner (x=9150-9180) ────────────────────────
    # Yellow warning banner near top of pillar
    pillar_x = 9150
    pygame.draw.rect(screen, sign_bg, apply_rect(pygame.Rect(pillar_x - 35, 215, 100, 18)))
    pygame.draw.rect(screen, warning_yel, apply_rect(pygame.Rect(pillar_x - 30, 219, 90, 10)))
    # Diagonal hazard stripes
    for hs in range(5):
        pygame.draw.rect(screen, sign_bg,
                         apply_rect(pygame.Rect(pillar_x - 28 + hs * 18, 219, 8, 10)))
    # Chain hanging from top of pillar to a hook below
    pygame.draw.rect(screen, chain, apply_rect(pygame.Rect(pillar_x + 13, 240, 2, 50)))
    pygame.draw.rect(screen, chain_hook, apply_rect(pygame.Rect(pillar_x + 9, 285, 12, 8)))

    # ─── 9. Final wall windows + EXIT sign (x=9500-9620) ───────────────
    # Upper wall (9500, -20, 120, 200)
    pygame.draw.rect(screen, window_frame, apply_rect(pygame.Rect(9530, 60, 36, 50)))
    pygame.draw.rect(screen, window_lit, apply_rect(pygame.Rect(9534, 64, 28, 42)))
    pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(9548, 64, 2, 42)))
    # Lower wall (9500, 300, 120, 550)
    pygame.draw.rect(screen, window_frame, apply_rect(pygame.Rect(9530, 340, 36, 50)))
    pygame.draw.rect(screen, window_lit, apply_rect(pygame.Rect(9534, 344, 28, 42)))
    # SHOP direction sign — bright green arrow pointing right
    arrow_x, arrow_y = 9560, 470
    pygame.draw.rect(screen, exit_dim, apply_rect(pygame.Rect(arrow_x - 35, arrow_y - 14, 70, 28)))
    pygame.draw.rect(screen, exit_green, apply_rect(pygame.Rect(arrow_x - 32, arrow_y - 11, 64, 22)))
    pygame.draw.polygon(screen, sign_bg, [
        apply_pos((arrow_x - 20, arrow_y - 6)),
        apply_pos((arrow_x + 10, arrow_y - 6)),
        apply_pos((arrow_x + 10, arrow_y - 12)),
        apply_pos((arrow_x + 26, arrow_y)),
        apply_pos((arrow_x + 10, arrow_y + 12)),
        apply_pos((arrow_x + 10, arrow_y + 6)),
        apply_pos((arrow_x - 20, arrow_y + 6)),
    ])
    # "SHOP" letters above the arrow
    for ltr_x in [arrow_x - 24, arrow_x - 10, arrow_x + 4, arrow_x + 18]:
        pygame.draw.rect(screen, sign_text, apply_rect(pygame.Rect(ltr_x, arrow_y - 28, 10, 8)))

    # ─── 10. Floor grates on the lower courtyard (y=520+) ──────────────
    for gx in [8920, 9020, 9230, 9330, 9430]:
        # Grate inset
        pygame.draw.rect(screen, grate, apply_rect(pygame.Rect(gx, 522, 56, 6)))
        # Grate slats
        for sl in range(7):
            pygame.draw.rect(screen, grate_dark,
                             apply_rect(pygame.Rect(gx + 2 + sl * 8, 523, 4, 4)))

    # ─── 11. Steam vents rising from floor grates ──────────────────────
    for vx in [8945, 9255, 9455]:
        pygame.draw.ellipse(screen, steam, apply_rect(pygame.Rect(vx, 500, 26, 14)))
        pygame.draw.ellipse(screen, steam_light, apply_rect(pygame.Rect(vx + 4, 485, 20, 12)))
        pygame.draw.ellipse(screen, steam, apply_rect(pygame.Rect(vx + 8, 468, 16, 10)))

    # ─── 12. Small "FLOOR 1" tag on the small hanging ledge ────────────
    pygame.draw.rect(screen, sign_bg, apply_rect(pygame.Rect(7575, 360, 38, 12)))
    pygame.draw.rect(screen, sign_border, apply_rect(pygame.Rect(7575, 360, 38, 12)), 1)
    pygame.draw.rect(screen, sign_text, apply_rect(pygame.Rect(7580, 364, 8, 4)))
    pygame.draw.rect(screen, warning_yel, apply_rect(pygame.Rect(7592, 364, 16, 4)))

    # ─── 13. Door silhouette on the after-bridge wall ──────────────────
    # Small access door at the bottom of the after-bridge wall (decorative)
    pygame.draw.rect(screen, door_dark, apply_rect(pygame.Rect(8770, 590, 32, 60)))
    pygame.draw.rect(screen, sign_border, apply_rect(pygame.Rect(8770, 590, 32, 60)), 1)
    pygame.draw.circle(screen, warning_yel, apply_pos((8795, 620)), 2)

    # ─── 14. Rust streaks on the main building front ───────────────────
    # Decorative rust runs down from a few windows
    for rx in [7745, 7965, 8185]:
        pygame.draw.rect(screen, rust, apply_rect(pygame.Rect(rx, 400, 4, 60)))
        pygame.draw.rect(screen, (90, 50, 30), apply_rect(pygame.Rect(rx + 1, 400, 2, 60)))


def draw_section8_collapsed_city_background(screen, camera):
    """
    Section 8 backdrop: collapsed city towers, snapped bridge spans, cables,
    and a damaged lift shaft. Visual only.
    """
    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    def apply_pos(pos):
        if camera is not None:
            return camera.apply_pos(pos)
        return pos

    void = (8, 10, 18)
    tower_dark = (18, 22, 34)
    tower_mid = (25, 30, 46)
    tower_light = (42, 50, 70)
    tower_edge = (52, 60, 82)
    window_dark = (7, 9, 16)
    window_blue = (38, 92, 135)
    window_glow = (84, 190, 235)
    metal = (76, 82, 96)
    metal_dark = (35, 38, 50)
    cable = (30, 32, 42)
    warning = (212, 166, 64)
    rust = (104, 56, 38)
    moon_ring = (126, 136, 158)
    moon_ring_dark = (62, 68, 84)

    def draw_window_grid(building, cols, rows):
        gap_x = max(38, building.width // max(1, cols + 1))
        gap_y = max(54, building.height // max(1, rows + 1))

        for col in range(cols):
            for row in range(rows):
                if (col * 3 + row * 5 + building.x // 40) % 4 == 0:
                    continue

                wx = building.x + 22 + col * gap_x
                wy = building.y + 32 + row * gap_y + ((col + building.x // 100) % 3) * 4

                if wx + 28 >= building.right or wy + 34 >= building.bottom:
                    continue

                lit = (col + row * 2 + building.width // 20) % 5 == 0
                glass = window_glow if lit else window_blue
                pygame.draw.rect(screen, tower_edge, apply_rect(pygame.Rect(wx, wy, 28, 34)))
                pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(wx + 4, wy + 4, 20, 26)))
                pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx + 13, wy + 4, 2, 26)))
                pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx + 4, wy + 16, 20, 2)))

                if (row + col) % 3 == 0:
                    pygame.draw.rect(screen, window_dark, apply_rect(pygame.Rect(wx + 4, wy + 18, 20, 12)))

    def draw_ruined_tower(rect, color, cap_offset=0):
        pygame.draw.rect(screen, color, apply_rect(rect))
        pygame.draw.rect(screen, tower_light, apply_rect(pygame.Rect(rect.x, rect.y, rect.width, 7)))
        pygame.draw.rect(screen, tower_dark, apply_rect(pygame.Rect(rect.right - 6, rect.y, 6, rect.height)))
        pygame.draw.rect(screen, tower_edge, apply_rect(pygame.Rect(rect.x, rect.y + 7, rect.width, 2)))

        roof_points = [
            apply_pos((rect.x, rect.y)),
            apply_pos((rect.x + rect.width // 4, rect.y - 22 + cap_offset)),
            apply_pos((rect.x + rect.width // 2, rect.y - 5)),
            apply_pos((rect.x + rect.width - 32, rect.y - 34 - cap_offset)),
            apply_pos((rect.right, rect.y)),
        ]
        pygame.draw.polygon(screen, color, roof_points)
        pygame.draw.line(
            screen,
            tower_edge,
            apply_pos((rect.x, rect.y)),
            apply_pos((rect.x + rect.width // 4, rect.y - 22 + cap_offset)),
            2,
        )
        pygame.draw.line(
            screen,
            tower_edge,
            apply_pos((rect.x + rect.width - 32, rect.y - 34 - cap_offset)),
            apply_pos((rect.right, rect.y)),
            2,
        )
        draw_window_grid(rect, max(2, rect.width // 90), max(2, rect.height // 88))

    # Dark drop under the high route.
    pygame.draw.rect(screen, void, apply_rect(pygame.Rect(9620, 360, 1880, 290)))

    # Buildings that anchor the platforms as broken rooftops and bridge supports.
    draw_ruined_tower(pygame.Rect(9740, 220, 300, 430), tower_mid, cap_offset=8)
    draw_ruined_tower(pygame.Rect(10120, 300, 470, 350), tower_dark, cap_offset=-6)
    draw_ruined_tower(pygame.Rect(10540, 250, 230, 400), tower_mid, cap_offset=4)
    draw_ruined_tower(pygame.Rect(10880, 200, 310, 450), tower_dark, cap_offset=12)
    draw_ruined_tower(pygame.Rect(11245, 160, 255, 490), tower_mid, cap_offset=-4)

    # Broken bridge silhouettes behind the real platform collision.
    bridge_spans = [
        [(9620, 328), (9745, 310), (9820, 220), (9920, 228), (9780, 350)],
        [(9980, 238), (10160, 320), (10560, 320), (10520, 350), (10010, 270)],
        [(10560, 270), (10840, 312), (10780, 345), (10535, 292)],
        [(10940, 218), (11270, 178), (11230, 210), (10980, 245)],
    ]
    for span in bridge_spans:
        pygame.draw.polygon(screen, metal_dark, [apply_pos(point) for point in span])
        pygame.draw.lines(screen, tower_light, False, [apply_pos(point) for point in span[:3]], 3)

    # Snapped suspension cables.
    cable_points = [(9640, 170), (9840, 210), (10160, 125), (10580, 245), (11040, 115), (11380, 170)]
    for start, end in zip(cable_points, cable_points[1:]):
        mid = ((start[0] + end[0]) // 2, max(start[1], end[1]) + 55)
        pygame.draw.line(screen, cable, apply_pos(start), apply_pos(mid), 2)
        pygame.draw.line(screen, cable, apply_pos(mid), apply_pos(end), 2)

    for hx in [9690, 9825, 10190, 10480, 10630, 10800, 11080, 11240]:
        top_y = 150 + (hx // 70) % 70
        bottom_y = 250 + (hx // 50) % 95
        pygame.draw.rect(screen, cable, apply_rect(pygame.Rect(hx, top_y, 3, bottom_y - top_y)))
        for ly in range(top_y + 10, bottom_y - 4, 18):
            pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(hx - 3, ly, 9, 5)))

    # Cracked moon-gate machinery behind the final lift.
    ring_center = (11275, 168)
    pygame.draw.circle(screen, moon_ring_dark, apply_pos(ring_center), 92)
    pygame.draw.circle(screen, moon_ring, apply_pos(ring_center), 76)
    pygame.draw.circle(screen, (24, 28, 42), apply_pos(ring_center), 54)
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        sx = ring_center[0] + int(math.cos(radians) * 62)
        sy = ring_center[1] + int(math.sin(radians) * 62)
        pygame.draw.rect(screen, moon_ring_dark, apply_rect(pygame.Rect(sx - 4, sy - 4, 8, 8)))
    pygame.draw.line(screen, rust, apply_pos((11220, 104)), apply_pos((11308, 230)), 3)
    pygame.draw.line(screen, tower_edge, apply_pos((11238, 95)), apply_pos((11208, 156)), 2)

    # Lift shaft, rails, and landing bracket.
    shaft_x = 11280
    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(shaft_x - 18, 160, 8, 450)))
    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(shaft_x + 228, 160, 8, 450)))
    for y in range(190, 610, 42):
        pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(shaft_x - 20, y, 12, 4)))
        pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(shaft_x + 226, y, 12, 4)))
    pygame.draw.rect(screen, warning, apply_rect(pygame.Rect(11368, 535, 78, 6)))
    pygame.draw.rect(screen, tower_edge, apply_rect(pygame.Rect(11340, 610, 120, 8)))


def draw_section8_collapsed_city_details(screen, camera, lift_rect=None, lift_state="idle"):
    """
    Section 8 foreground dressing: cracks, railings, sparks, debris, and
    lift hardware. Visual only.
    """
    def apply_rect(rect):
        if camera is not None:
            return camera.apply_rect(rect)
        return rect

    def apply_pos(pos):
        if camera is not None:
            return camera.apply_pos(pos)
        return pos

    metal = (92, 98, 114)
    metal_dark = (38, 42, 56)
    cable = (30, 32, 42)
    hazard = (218, 166, 58)
    red = (175, 54, 50)
    spark = (255, 214, 108)
    glow = (92, 202, 245)
    soot = (14, 15, 22)
    dust = (88, 92, 104)
    glass = (80, 165, 210)

    def draw_edge_barricade(x, edge_y):
        post_positions = [x, x + 34, x + 78]
        for post_x in post_positions:
            pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(post_x, edge_y - 54, 5, 52)))
            pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(post_x - 2, edge_y - 6, 9, 6)))

        pygame.draw.line(screen, metal_dark, apply_pos((x - 8, edge_y - 48)), apply_pos((x + 92, edge_y - 38)), 4)
        pygame.draw.line(screen, metal, apply_pos((x - 2, edge_y - 25)), apply_pos((x + 72, edge_y - 31)), 3)

        tape_y = edge_y - 42
        for stripe_x in range(x + 4, x + 76, 18):
            pygame.draw.line(screen, hazard, apply_pos((stripe_x, tape_y - 5)), apply_pos((stripe_x + 12, tape_y + 7)), 4)
            pygame.draw.line(screen, metal_dark, apply_pos((stripe_x + 8, tape_y - 4)), apply_pos((stripe_x + 20, tape_y + 6)), 3)

    def draw_fallen_danger_sign(x, y):
        sign_points = [
            (x, y + 7),
            (x + 44, y),
            (x + 50, y + 25),
            (x + 6, y + 31),
        ]
        pygame.draw.polygon(screen, hazard, [apply_pos(point) for point in sign_points])
        pygame.draw.lines(screen, metal_dark, True, [apply_pos(point) for point in sign_points], 3)
        for stripe_x in [x + 7, x + 21, x + 35]:
            pygame.draw.line(screen, metal_dark, apply_pos((stripe_x, y + 5)), apply_pos((stripe_x + 11, y + 27)), 4)
        pygame.draw.rect(screen, red, apply_rect(pygame.Rect(x + 24, y + 9, 5, 13)))
        pygame.draw.rect(screen, red, apply_rect(pygame.Rect(x + 24, y + 25, 5, 4)))
        pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(x + 6, y + 32, 48, 4)))

    # Cracked road edge and exposed rebar.
    for x in range(8540, 10470, 180):
        pygame.draw.line(screen, metal_dark, apply_pos((x, 648)), apply_pos((x + 52, 620)), 3)
        pygame.draw.line(screen, metal, apply_pos((x + 14, 646)), apply_pos((x + 58, 632)), 2)

    for x in [8700, 9020, 9360, 10080, 10620, 11040]:
        pygame.draw.line(screen, soot, apply_pos((x, 642)), apply_pos((x + 42, 650)), 3)
        pygame.draw.line(screen, soot, apply_pos((x + 20, 646)), apply_pos((x + 10, 660)), 2)
        pygame.draw.ellipse(screen, soot, apply_rect(pygame.Rect(x + 50, 642, 46, 8)))

    # Clear danger cues around the instant-death void, attached to platform edges.
    for stripe_x in [9398, 9418, 9444, 9475]:
        pygame.draw.line(screen, hazard, apply_pos((stripe_x, 642)), apply_pos((stripe_x + 14, 650)), 4)
    for stripe_x in [11262, 11288, 11324, 11356]:
        pygame.draw.line(screen, hazard, apply_pos((stripe_x, 642)), apply_pos((stripe_x + 14, 650)), 4)

    draw_edge_barricade(9385, 650)
    draw_edge_barricade(11278, 650)

    # Uneven glow far below the void, kept sparse so it reads like depth rather than a pattern.
    for glow_x, glow_w in [(9680, 150), (10380, 210), (11080, 130)]:
        pygame.draw.ellipse(screen, (72, 18, 26), apply_rect(pygame.Rect(glow_x, 690, glow_w, 11)))
        pygame.draw.rect(screen, red, apply_rect(pygame.Rect(glow_x + glow_w // 3, 683, glow_w // 3, 3)))
    draw_fallen_danger_sign(10430, 666)

    # Broken railings along the high route.
    railing_groups = [
        (9820, 200, 160),
        (10160, 300, 400),
        (10560, 250, 160),
        (10680, 290, 160),
        (11000, 200, 160),
        (11100, 160, 160),
    ]
    for x, y, w in railing_groups:
        pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(x + 6, y - 14, w - 12, 4)))
        for post_x in range(x + 14, x + w - 10, 44):
            post_h = 18 if post_x % 3 else 10
            pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(post_x, y - post_h, 4, post_h)))
        pygame.draw.line(screen, metal, apply_pos((x + w - 38, y - 12)), apply_pos((x + w + 12, y + 8)), 3)
        pygame.draw.rect(screen, hazard, apply_rect(pygame.Rect(x + 18, y + 6, min(56, w - 36), 3)))

    # Fallen bridge pieces in the void.
    debris = [
        (9665, 470, 44, 12), (9900, 420, 34, 10), (10080, 515, 60, 14),
        (10340, 448, 38, 12), (10690, 500, 52, 12), (10930, 410, 42, 10),
        (11160, 455, 36, 12),
    ]
    for x, y, w, h in debris:
        pygame.draw.rect(screen, dust, apply_rect(pygame.Rect(x, y, w, h)))
        pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(x + 4, y + h - 3, w - 8, 3)))
        pygame.draw.rect(screen, glass, apply_rect(pygame.Rect(x + 8, y + 3, 12, 3)))

    # Warning beacons and live-wire sparks.
    for bx, by in [(10730, 230), (11040, 180), (11234, 142)]:
        pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(bx - 8, by - 8, 16, 8)))
        pygame.draw.circle(screen, red, apply_pos((bx, by - 10)), 5)
        pygame.draw.circle(screen, (255, 150, 120), apply_pos((bx, by - 10)), 2)

    for sx, sy in [(10815, 356), (11184, 126), (11318, 310)]:
        pygame.draw.circle(screen, spark, apply_pos((sx, sy)), 3)
        pygame.draw.rect(screen, spark, apply_rect(pygame.Rect(sx - 9, sy + 5, 3, 3)))
        pygame.draw.rect(screen, spark, apply_rect(pygame.Rect(sx + 8, sy - 7, 2, 2)))

    if lift_rect is None:
        return

    lift_x = lift_rect.x
    lift_y = lift_rect.y
    lift_w = lift_rect.width
    moving = lift_state in ("dropping", "arrived")

    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(lift_x + 8, lift_y - 10, lift_w - 16, 5)))
    for cx in [lift_x + 28, lift_x + lift_w - 34]:
        pygame.draw.rect(screen, cable, apply_rect(pygame.Rect(cx, 160, 3, max(0, lift_y - 160))))
        for ly in range(174, lift_y - 4, 18):
            pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(cx - 3, ly, 9, 5)))
        pygame.draw.rect(screen, metal, apply_rect(pygame.Rect(cx - 9, lift_y - 12, 20, 8)))

    pygame.draw.rect(screen, metal_dark, apply_rect(pygame.Rect(lift_x + 24, lift_y + 20, lift_w - 48, 12)))
    for gear_x in [lift_x + 52, lift_x + lift_w - 58]:
        pygame.draw.circle(screen, metal, apply_pos((gear_x, lift_y + 29)), 10)
        pygame.draw.circle(screen, soot, apply_pos((gear_x, lift_y + 29)), 4)

    if moving:
        for puff_x, puff_y in [(lift_x + 40, lift_y + 44), (lift_x + 114, lift_y + 38), (lift_x + 178, lift_y + 46)]:
            pygame.draw.ellipse(screen, (90, 94, 108), apply_rect(pygame.Rect(puff_x, puff_y, 28, 12)))
        pygame.draw.rect(screen, glow, apply_rect(pygame.Rect(lift_x + 88, lift_y + 8, 42, 3)))


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
            ]
        }

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
                        "label": "Boss Arena",
                    }
                ],
                enemy_spawns=[(7000, 590)],                # Combat Courtyard center
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
            1: GameMap(
                1,
                "The Warden — Boss Arena",
                MAP_1_WIDTH,
                MAP_1_HEIGHT,
                [
                    pygame.Rect(0, 650, MAP_1_WIDTH, 70),                # Arena floor
                    pygame.Rect(0, 200, MAP_1_WIDTH, 40),                # Ceiling
                    pygame.Rect(0, 240, 30, 410),                        # Left wall
                    pygame.Rect(MAP_1_WIDTH - 30, 240, 30, 410),         # Right wall
                    pygame.Rect(150, 540, 200, 110),                     # Tactical block left
                    pygame.Rect(MAP_1_WIDTH - 350, 540, 200, 110),       # Tactical block right
                    pygame.Rect(0, SCREEN_HEIGHT - 20, MAP_1_WIDTH, 20),
                ],
                (100, 650),
                [
                    {
                        "rect": pygame.Rect(MAP_1_WIDTH - 120, 550, DOOR_WIDTH, DOOR_HEIGHT),
                        "target_map": 2,
                        "label": "Resting Area",
                    }
                ],
                boss_spawn=(MAP_1_WIDTH // 2, 590),
                map_type="boss_stage",
            ),

            # =========================================================================
            # MAP 2: Resting Area — Checkpoint + transition to Level 2
            # =========================================================================
            2: GameMap(
                2,
                "Resting Area",
                MAP_2_WIDTH,
                MAP_2_HEIGHT,
                [
                    pygame.Rect(0, 650, MAP_2_WIDTH, 70),                # Floor
                    pygame.Rect(0, 250, MAP_2_WIDTH, 40),                # Ceiling
                    pygame.Rect(0, 290, 30, 360),                        # Left wall
                    pygame.Rect(MAP_2_WIDTH - 30, 290, 30, 360),         # Right wall
                    pygame.Rect(700, 580, 100, 70),                      # Resting altar / bench
                    pygame.Rect(0, SCREEN_HEIGHT - 20, MAP_2_WIDTH, 20),
                ],
                (100, 650),
                [
                    {
                        "rect": pygame.Rect(MAP_2_WIDTH - 120, 550, DOOR_WIDTH, DOOR_HEIGHT),
                        "target_map": "victory",
                        "label": "Level 2",
                    }
                ],
                map_type="rest_stage",
            ),
        }

    def get_current_map(self):
        return self.current_map

    def is_player_in_deadly_void(self, player):
        voids = self.deadly_voids.get(self.current_map_id, [])
        foot_sensor = pygame.Rect(player.rect.x, player.rect.bottom - 4, player.rect.width, 8)

        for void in voids:
            if foot_sensor.colliderect(void):
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

        player.rect.midbottom = self.current_map.player_spawn
        player.vel_x = 0
        player.vel_y = 0
        player.is_dashing = False
        player.is_attacking = False
        player.is_auto_grappling = False
        player.is_blocking = False
        player.is_parrying = False
        player.attack_has_hit = False
        player.should_spawn_projectile = False
        player.has_active_shield_throw = False
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
            camera.set_map_size(self.current_map.width, self.current_map.height)
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
        return self.current_map.platforms

    def get_fulcrums(self):
        return self.current_map.fulcrums

    def get_shop_rect(self):
        return self.current_map.shop_rect

    def get_doors(self):
        return self.current_map.doors

    def draw_current_map(self, screen, camera):
        font = pygame.font.Font(None, 28)

        # 1. Background (moon, stars, distant city silhouette)
        draw_moon_background(screen, camera, self.current_map)

        # 2. Enclosed-room shells: dark void above ceilings + stone interior fill.
        #    Auto-detects ceiling rects in any map's platform list.
        draw_level1_room_shells(screen, camera, self.current_map)

        # 3. Street embankment behind ground islands.
        #    Auto-detects ground rects (y=650, h=70) in any map's platform list.
        draw_level1_wall_masses(screen, camera, self.current_map)

        # 3b. Section 5 + Section 6 background buildings — drawn BEHIND platforms
        #     so the platforms read as balconies / rooftops on the buildings.
        if self.current_map.map_id == 0:
            draw_section5_science_buildings(screen, camera)
            draw_section6_courtyard_buildings(screen, camera)
            draw_section8_collapsed_city_background(screen, camera)

        # 4. Foreground platforms (ground, ledges, rubble, pillars, ceilings).
        #    draw_moon_platform picks the right visual based on rect shape.
        for platform in self.current_map.platforms:
            # Skip the safety floor at very bottom — it's invisible by design.
            if platform.y >= SCREEN_HEIGHT - 30:
                continue
            # Skip very-high invisible collision ceilings (legacy).
            if platform.y <= 50 and platform.height <= 80:
                continue

            draw_rect = platform
            if camera is not None:
                draw_rect = camera.apply_rect(platform)
            draw_moon_platform(screen, draw_rect)

        # 5. Decorative props (no collision) — bones, blood, broken cars, signs, furniture.
        if self.current_map.map_id == 0:
            draw_section_decorations(screen, camera)
            # Section 4 detailed tram-wreck visuals (overlay on top of the platform stones)
            draw_section4_tram_wreck(screen, camera)
            # Section 7 lab-entrance overlay — windows, chains, pipes, lamps, signs
            draw_section7_lab_entrance_details(screen, camera)
            draw_section8_collapsed_city_details(
                screen,
                camera,
                self.collapsing_lift_rect,
                self.collapsing_lift_state,
            )
            draw_body_pile(screen, camera, 135, 650)

        # 6. UI / Interactive Elements Layer
        if self.current_map.map_id == 0:
            return

        for door in self.current_map.doors:
            draw_rect = door["rect"]
            if camera is not None:
                draw_rect = camera.apply_rect(door["rect"])
            pygame.draw.rect(screen, (60, 220, 100), draw_rect)
            pygame.draw.rect(screen, (220, 255, 220), draw_rect, 2)
            text = font.render(door["label"], True, (20, 40, 20))
            screen.blit(text, text.get_rect(center=draw_rect.center))

    def check_doors(self, player):
        if self.current_map_id == 0:
            return None

        for door in self.current_map.doors:
            if player.rect.colliderect(door["rect"]):
                return door

        return None

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
