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

    for plat in game_map.platforms:
        if plat.y < 320 and plat.height <= 50 and plat.width >= 200:
            ceiling_bottom = plat.y + plat.height
            # Find a wall inside this room (tall, narrow rect at the room's x range)
            wall_bottom = None
            for w in game_map.platforms:
                if (w.height >= 150 and w.width <= 80
                        and plat.x <= w.x and w.right <= plat.right
                        and w.y >= ceiling_bottom):
                    wall_bottom = w.bottom if wall_bottom is None else max(wall_bottom, w.bottom)
            # Fallback when no wall is detected — fill mid-room
            if wall_bottom is None:
                wall_bottom = ceiling_bottom + 200

            # Dark void above ceiling
            void = pygame.Rect(plat.x, plat.y - 400, plat.width, 400 + plat.height)
            pygame.draw.rect(screen, void_color, apply_rect(void))
            pygame.draw.rect(screen, trim, apply_rect(pygame.Rect(plat.x, plat.y - 4, plat.width, 4)))

            # Wallpaper — stone fill only between ceiling and wall.bottom
            interior_h = wall_bottom - ceiling_bottom
            if interior_h > 0:
                interior = pygame.Rect(plat.x, ceiling_bottom, plat.width, interior_h)
                pygame.draw.rect(screen, wallpaper, apply_rect(interior))
                # Subtle horizontal joint lines for stone wall texture
                for jy in range(ceiling_bottom + 35, wall_bottom, 50):
                    pygame.draw.rect(screen, wallpaper_joint, apply_rect(pygame.Rect(plat.x, jy, plat.width, 2)))

class LevelManager:
    def __init__(self):
        self.maps = self.build_maps()
        self.current_map_id = 0
        self.current_map = self.maps[self.current_map_id]

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
                    pygame.Rect(500, 580, 250, 70),       # Lower buckled slab (sits on ground)
                    pygame.Rect(580, 510, 130, 70),       # Upper buckled slab (sits on lower slab)

                    # ─── 2. Destroyed Street (1100-2400) ─────────────────────────────
                    # NO PITS — continuous ground. Two collapsed-wall structures + a tall
                    # rubble heap form natural climbing/jumping challenges along the route.
                    pygame.Rect(1100, 650, 1300, 70),     # Continuous ground (no holes)
                    # Collapsed wall structure 1: two-tier slab
                    pygame.Rect(1200, 580, 300, 70),      # Wall fallen flat (lower slab)
                    pygame.Rect(1280, 510, 200, 70),      # Upper section of fallen wall (sits on lower)
                    # Tall building rubble heap mid-section
                    pygame.Rect(1700, 540, 200, 110),     # Tall rubble pile (climbing block)
                    pygame.Rect(1750, 460, 110, 80),      # Top piece sits on the rubble pile
                    # Collapsed wall structure 2 near end (transition into building)
                    pygame.Rect(2000, 580, 220, 70),      # Lower fallen wall
                    pygame.Rect(2080, 510, 130, 70),      # Upper section (sits on lower)

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
                    pygame.Rect(2400, 60, 30, 520),       # Left wall  (y=60-580)
                    pygame.Rect(3870, 140, 30, 520),       # Right wall (y=60-580)

                    # NO STAIRS — player jumps directly from ground to Floor 2 (140px jump,
                    # well within the 160px max). The peak of a straight-up jump is y=490,
                    # which is ABOVE floor 2 at y=510, so the player cleanly clears floor 2
                    # during ascent and lands on it during descent. No L-shape outside the
                    # building, no head-bumping mid-jump.

                    # Floor 2 — LEFT-side balcony. Direct jump from ground.
                    pygame.Rect(2440, 510, 690, 30),

                    # Floor 3 — RIGHT-side balcony. Reach: jump right + up from floor 2.
                    pygame.Rect(3170, 380, 690, 30),

                    # Floor 4 — LEFT-side balcony. Reach: jump left + up from floor 3.
                    pygame.Rect(2440, 250, 690, 30),

                    # Floor 5 — RIGHT-side TOP balcony. Reach: jump right + up from floor 4.
                    pygame.Rect(3200, 160, 690, 30),

                    # ─── 4. Collapsed Transit / Tram Wreck (3900-5100) ───────────────
                    # Crashed tram cars at varied heights. Walk on top of cars.
                    pygame.Rect(3900, 650, 1200, 70),     # Ground
                    pygame.Rect(4000, 540, 350, 110),     # Tram car 1
                    pygame.Rect(4380, 580, 280, 70),      # Tram car 2 (lower/tilted)
                    pygame.Rect(4690, 510, 220, 140),     # Tram car 3 (taller, upright)
                    pygame.Rect(4940, 570, 130, 80),      # Crashed cab piece

                    # ─── 5. Science District Exterior (5100-6400) ────────────────────
                    # Lab buildings forming a varied skyline. Climb across rooftops.
                    pygame.Rect(5100, 650, 1300, 70),     # Ground
                    pygame.Rect(5180, 550, 200, 100),     # Lab 1
                    pygame.Rect(5400, 470, 220, 180),     # Lab 2 (tall)
                    pygame.Rect(5650, 540, 170, 110),     # Lab 3
                    pygame.Rect(5840, 470, 200, 180),     # Lab 4 (tall)
                    pygame.Rect(6060, 580, 130, 70),      # Lab 5 (small)
                    pygame.Rect(6220, 600, 100, 50),      # Rubble at end

                    # ─── 6. First Combat Courtyard (6400-7600) ───────────────────────
                    # Wide arena. Cover blocks + tactical platforms for fights.
                    # Enemy spawns at center.
                    pygame.Rect(6400, 650, 1200, 70),     # Wide arena floor
                    pygame.Rect(6500, 580, 110, 70),      # Cover left
                    pygame.Rect(6700, 540, 200, 110),     # Tactical block 1
                    pygame.Rect(7050, 540, 200, 110),     # Tactical block 2
                    pygame.Rect(7350, 580, 110, 70),      # Cover right

                    # ─── 7. Messy Lab Entrance (7600-8500) ───────────────────────────
                    # Partial enclosure. Stepped interior leading to the shop.
                    pygame.Rect(7600, 650, 900, 70),      # Ground
                    pygame.Rect(7600, 250, 900, 40),      # Ceiling
                    pygame.Rect(7600, 290, 30, 200),      # Left entry wall
                    pygame.Rect(8470, 290, 30, 200),      # Right entry wall
                    pygame.Rect(7720, 580, 130, 70),      # Step 1
                    pygame.Rect(7860, 510, 130, 140),     # Step 2 (taller)
                    pygame.Rect(8050, 580, 200, 70),      # Long bench
                    pygame.Rect(8270, 540, 100, 110),     # Lab fixture

                    # ─── 8. SHOP Area (8500-9300) ────────────────────────────────────
                    # Enclosed safe room with shop counter + decorative displays.
                    pygame.Rect(8500, 650, 800, 70),      # Floor
                    pygame.Rect(8500, 250, 800, 40),      # Ceiling
                    pygame.Rect(8500, 290, 30, 290),      # Left wall (doorway under)
                    pygame.Rect(9270, 290, 30, 290),      # Right wall (doorway under)
                    pygame.Rect(8650, 580, 130, 70),      # Display 1
                    pygame.Rect(8830, 580, 130, 70),      # Shop counter (interactable)
                    pygame.Rect(9020, 580, 130, 70),      # Display 2

                    # ─── 9. Collapsed City Route (9300-10500) ────────────────────────
                    # 3 islands + 2 wider pits. Bridge debris and rubble piles for navigation.
                    pygame.Rect(9300, 650, 280, 70),      # Island 1
                    # [pit 9580-9750: 170px]
                    pygame.Rect(9750, 650, 250, 70),      # Island 2
                    # [pit 10000-10180: 180px]
                    pygame.Rect(10180, 650, 320, 70),     # Island 3
                    pygame.Rect(9320, 590, 90, 60),       # Bridge piece 1
                    pygame.Rect(9430, 540, 100, 110),     # Tall rubble (island 1)
                    pygame.Rect(9770, 580, 110, 70),      # Bridge piece 2
                    pygame.Rect(9880, 530, 90, 120),      # Tall rubble (island 2)
                    pygame.Rect(10220, 590, 110, 60),     # Bridge piece 3
                    pygame.Rect(10350, 540, 100, 110),    # Tall rubble (island 3)

                    # ─── 10. Boss Arena Entrance (10500-11500) ───────────────────────
                    # Atmospheric corridor leading to the boss. Partial ceiling = ominous feel.
                    pygame.Rect(10500, 650, 1000, 70),    # Long approach
                    pygame.Rect(10500, 280, 1000, 40),    # Corridor ceiling
                    pygame.Rect(10500, 320, 30, 270),     # Left corridor wall (partial)
                    pygame.Rect(11470, 320, 30, 270),     # Right corridor wall (partial)
                    pygame.Rect(10800, 600, 100, 50),     # Step 1
                    pygame.Rect(11050, 580, 130, 70),     # Bigger step
                    pygame.Rect(11280, 600, 100, 50),     # Step 2

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
                shop_rect=pygame.Rect(8830, 530, 130, 90),
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

    def change_map(self, target_map_id, player, enemy, camera=None):
        if target_map_id not in self.maps:
            return False

        self.current_map_id = target_map_id
        self.current_map = self.maps[self.current_map_id]

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

        # 4. Foreground platforms (ground, ledges, rubble, pillars, ceilings).
        #    draw_moon_platform picks the right visual based on rect shape.
        for platform in self.current_map.platforms:
            # Skip the safety floor at very bottom — it's invisible by design.
            if platform.y >= SCREEN_HEIGHT - 30:
                continue
            # Skip very-high invisible collision ceilings (legacy).
            if platform.y <= 50:
                continue

            draw_rect = platform
            if camera is not None:
                draw_rect = camera.apply_rect(platform)
            draw_moon_platform(screen, draw_rect)

        # 5. Decorative props (no collision) — bones, blood, broken cars, signs, furniture.
        if self.current_map.map_id == 0:
            draw_section_decorations(screen, camera)
            draw_body_pile(screen, camera, 135, 650)

        # 6. UI / Interactive Elements Layer
        for door in self.current_map.doors:
            draw_rect = door["rect"]
            if camera is not None:
                draw_rect = camera.apply_rect(door["rect"])
            pygame.draw.rect(screen, (60, 220, 100), draw_rect)
            pygame.draw.rect(screen, (220, 255, 220), draw_rect, 2)
            text = font.render(door["label"], True, (20, 40, 20))
            screen.blit(text, text.get_rect(center=draw_rect.center))

    def check_doors(self, player):
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
