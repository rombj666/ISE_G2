import math
from pathlib import Path

import pygame

from settings import (
    ENERGY_BEAM_ATTACK_OFFSET_X,
    ENERGY_BEAM_ATTACK_OFFSET_Y,
    ENERGY_BEAM_ATTACK_SCALE,
    ENERGY_BEAM_ATTACK_PATH,
    ENERGY_BEAM_DAMAGE,
    ENERGY_BEAM_READY_PATH,
    ORBIT_BLADE_DAMAGE,
    ORBIT_BLADE_FIRE_DELAY,
    ORBIT_BLADE_HIT_PATH,
    ORBIT_BLADE_LIFETIME,
    ORBIT_BLADE_ORBIT_SPEED,
    ORBIT_BLADE_PROJECTILE_PATH,
    ORBIT_BLADE_PROJECTILE_SPEED,
    ORBIT_BLADE_RADIUS,
    ORBIT_BLADE_READY_TIME,
    ORBIT_BLADE_SIZE,
    ORBIT_BLADE_TARGET_RANGE,
    ORBIT_BLADES_READY_PATH,
    SKILL_EFFECT_FRAME_COUNT,
    SOUL_ANCHOR_LOOP_PATH,
    SOUL_ANCHOR_PLACE_PATH,
    SOUL_ANCHOR_READY_PATH,
    SOUL_ANCHOR_RETURN_PATH,
    TIME_FREEZE_ACTION_PATH,
    TIME_FREEZE_LOOP_PATH,
    TIME_FREEZE_RADIUS,
    TIME_FREEZE_READY_PATH,
    TIME_FREEZE_VISUAL_DURATION,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEBUG_OUTPUT_DIR = PROJECT_ROOT / "assets" / "processed" / "debug"
SKILL_WRITE_DEBUG_PREVIEWS = False
SKILL_FRAME_CACHE = {}

PLAYER_SKILL_FRAME_COUNTS = {
    "energy_beam_attack": 6,
}

TIME_FREEZE_ACTION_SIZE = (300, 210)

ORBIT_READY_SIZE = (120, 120)
ORBIT_PROJECTILE_SIZE = (82, 54)
ORBIT_HIT_SIZE = (92, 76)

ENERGY_BEAM_READY_SIZE = (120, 100)
ENERGY_BEAM_ATTACK_SIZE = (360, 90)
ENERGY_BEAM_READY_DURATION = 0.25
ENERGY_BEAM_ATTACK_DURATION = 1.5
ENERGY_BEAM_FRAME_DURATION = 0.12

SOUL_ANCHOR_PLACE_SIZE = (150, 120)
SOUL_ANCHOR_LOOP_SIZE = (118, 96)
SOUL_ANCHOR_RETURN_SIZE = (130, 108)


MANUAL_TIME_FREEZE_RECTS = {
    "ready": None,
    "action": None,
    "loop": None,
}

MANUAL_ORBIT_BLADE_RECTS = {
    "ready": None,
    "projectile": None,
    "hit": None,
}

MANUAL_ENERGY_BEAM_RECTS = {
    "ready": None,
}

MANUAL_SOUL_ANCHOR_RECTS = {
    "ready": None,
    "place": None,
    "loop": None,
    "return": None,
}


SKILLS = {
    "time_freeze": {
        "id": "time_freeze",
        "name": "Time Freeze",
        "skill_type": "time_freeze",
        "mana_cost": 45,
        "cooldown": 10.0,
        "damage": 0,
        "description": "Creates a fixed time domain around the player. Enemy inside cannot move or attack for a short time.",
    },
    "orbit_blades": {
        "id": "orbit_blades",
        "name": "Orbit Blades",
        "skill_type": "orbit_blades",
        "mana_cost": 35,
        "cooldown": 7.0,
        "damage": ORBIT_BLADE_DAMAGE,
        "description": "Creates 3 blades around the player. The blades orbit briefly, auto-aim at enemy, then shoot toward it.",
    },
    "energy_beam": {
        "id": "energy_beam",
        "name": "Energy Beam",
        "skill_type": "energy_beam",
        "mana_cost": 45,
        "cooldown": 9.0,
        "damage": ENERGY_BEAM_DAMAGE,
        "description": "Fires a strong beam forward.",
    },
    "soul_anchor": {
        "id": "soul_anchor",
        "name": "Soul Anchor",
        "skill_type": "soul_anchor",
        "mana_cost": 35,
        "cooldown": 10.0,
        "damage": 0,
        "description": "First use places an anchor. Second use returns the player to that anchor.",
    },
}


SKILL_ASSETS = {
    "time_freeze_ready": {
        "label": "Time Freeze ready frames",
        "path": TIME_FREEZE_READY_PATH,
        "target_size": (220, 150),
        "crop_mode": "ground_effect",
        "manual_rects": MANUAL_TIME_FREEZE_RECTS["ready"],
    },
    "time_freeze_action": {
        "label": "Time Freeze action frames",
        "path": TIME_FREEZE_ACTION_PATH,
        "target_size": TIME_FREEZE_ACTION_SIZE,
        "crop_mode": "ground_effect",
        "manual_rects": MANUAL_TIME_FREEZE_RECTS["action"],
    },
    "time_freeze_loop": {
        "label": "Time Freeze loop frames",
        "path": TIME_FREEZE_LOOP_PATH,
        "target_size": (240, 180),
        "crop_mode": "ground_effect",
        "manual_rects": MANUAL_TIME_FREEZE_RECTS["loop"],
    },
    "orbit_blades_ready": {
        "label": "Orbit Blades ready frames",
        "path": ORBIT_BLADES_READY_PATH,
        "target_size": ORBIT_READY_SIZE,
        "crop_mode": "center_effect",
        "manual_rects": MANUAL_ORBIT_BLADE_RECTS["ready"],
    },
    "orbit_blade_projectile": {
        "label": "Orbit Blade projectile frames",
        "path": ORBIT_BLADE_PROJECTILE_PATH,
        "target_size": ORBIT_PROJECTILE_SIZE,
        "crop_mode": "projectile",
        "manual_rects": MANUAL_ORBIT_BLADE_RECTS["projectile"],
    },
    "orbit_blade_hit": {
        "label": "Orbit Blade hit frames",
        "path": ORBIT_BLADE_HIT_PATH,
        "target_size": ORBIT_HIT_SIZE,
        "crop_mode": "hit",
        "manual_rects": MANUAL_ORBIT_BLADE_RECTS["hit"],
    },
    "energy_beam_ready": {
        "label": "Energy Beam ready frames",
        "path": ENERGY_BEAM_READY_PATH,
        "target_size": ENERGY_BEAM_READY_SIZE,
        "crop_mode": "center_effect",
        "manual_rects": MANUAL_ENERGY_BEAM_RECTS["ready"],
    },
    "energy_beam_attack": {
        "label": "Energy Beam attack frames",
        "path": ENERGY_BEAM_ATTACK_PATH,
        "target_size": None,
        "crop_mode": "beam",
        "manual_rects": None,
        "scale": ENERGY_BEAM_ATTACK_SCALE,
    },
    "soul_anchor_ready": {
        "label": "Soul Anchor ready frames",
        "path": SOUL_ANCHOR_READY_PATH,
        "target_size": (120, 96),
        "crop_mode": "ground_effect",
        "manual_rects": MANUAL_SOUL_ANCHOR_RECTS["ready"],
    },
    "soul_anchor_place": {
        "label": "Soul Anchor place frames",
        "path": SOUL_ANCHOR_PLACE_PATH,
        "target_size": SOUL_ANCHOR_PLACE_SIZE,
        "crop_mode": "ground_effect",
        "manual_rects": MANUAL_SOUL_ANCHOR_RECTS["place"],
    },
    "soul_anchor_loop": {
        "label": "Soul Anchor loop frames",
        "path": SOUL_ANCHOR_LOOP_PATH,
        "target_size": SOUL_ANCHOR_LOOP_SIZE,
        "crop_mode": "ground_effect",
        "manual_rects": MANUAL_SOUL_ANCHOR_RECTS["loop"],
    },
    "soul_anchor_return": {
        "label": "Soul Anchor return frames",
        "path": SOUL_ANCHOR_RETURN_PATH,
        "target_size": SOUL_ANCHOR_RETURN_SIZE,
        "crop_mode": "ground_effect",
        "manual_rects": MANUAL_SOUL_ANCHOR_RECTS["return"],
    },
}


def get_skill(skill_id):
    if skill_id in SKILLS:
        return SKILLS[skill_id]
    return SKILLS["time_freeze"]


def get_all_skills():
    return SKILLS


def resolve_asset_path(path):
    asset_path = Path(path)
    if asset_path.is_absolute():
        return asset_path
    return PROJECT_ROOT / asset_path


def make_equal_source_rects(sheet, frame_count):
    frame_width = sheet.get_width() // frame_count
    if frame_width <= 0 or sheet.get_width() % frame_count != 0:
        print(
            "WARNING: Skill effect sheet width is not evenly divisible by frame count:",
            sheet.get_size(),
            "frames:",
            frame_count,
        )
        frame_width = max(1, sheet.get_width() // frame_count)

    rects = []
    for index in range(frame_count):
        rects.append(pygame.Rect(index * frame_width, 0, frame_width, sheet.get_height()))
    return rects


def color_distance(color, sample):
    return abs(color.r - sample.r) + abs(color.g - sample.g) + abs(color.b - sample.b)


def is_generated_background_color(color, background_samples):
    if color.a < 255:
        return False

    for sample in background_samples:
        if color_distance(color, sample) <= 42:
            return True

    spread = max(color.r, color.g, color.b) - min(color.r, color.g, color.b)
    near_white = color.r >= 220 and color.g >= 220 and color.b >= 220 and spread <= 35
    near_black = color.r <= 35 and color.g <= 35 and color.b <= 35
    flat_gray = spread <= 16 and 36 <= color.r <= 225 and 36 <= color.g <= 225 and 36 <= color.b <= 225
    return near_white or near_black or flat_gray


def get_background_samples(surface):
    width, height = surface.get_size()
    if width <= 0 or height <= 0:
        return []

    points = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
        (width // 2, 0),
        (width // 2, height - 1),
        (0, height // 2),
        (width - 1, height // 2),
    ]
    return [surface.get_at(point) for point in points]


def repair_generated_background(surface):
    alpha_rect = surface.get_bounding_rect(min_alpha=1)
    if alpha_rect.width <= 0 or alpha_rect.height <= 0:
        return surface, 0

    background_samples = get_background_samples(surface)
    if not background_samples or any(sample.a < 255 for sample in background_samples):
        return surface, 0

    repaired = surface.copy()
    width, height = repaired.get_size()
    removed_pixels = 0
    for y in range(height):
        for x in range(width):
            color = repaired.get_at((x, y))
            if is_generated_background_color(color, background_samples):
                repaired.set_at((x, y), (color.r, color.g, color.b, 0))
                removed_pixels += 1
    return repaired, removed_pixels


def get_alpha_bounds(surface):
    return surface.get_bounding_rect(min_alpha=1)


def crop_visible_pixels(frame):
    bounds = get_alpha_bounds(frame)
    if bounds.width <= 0 or bounds.height <= 0:
        return frame.copy()

    cropped = pygame.Surface(bounds.size, pygame.SRCALPHA)
    cropped.blit(frame, (0, 0), bounds)
    return cropped


def scale_to_fit(surface, target_size):
    target_width, target_height = target_size
    if surface.get_width() <= 0 or surface.get_height() <= 0:
        return pygame.Surface(target_size, pygame.SRCALPHA)

    scale = min(target_width / surface.get_width(), target_height / surface.get_height())
    scaled_size = (
        max(1, round(surface.get_width() * scale)),
        max(1, round(surface.get_height() * scale)),
    )
    return pygame.transform.smoothscale(surface, scaled_size)


def place_on_canvas(surface, target_size, crop_mode):
    canvas = pygame.Surface(target_size, pygame.SRCALPHA)
    scaled = scale_to_fit(surface, target_size)
    rect = scaled.get_rect()

    if crop_mode == "ground_effect":
        rect.midbottom = (target_size[0] // 2, target_size[1])
    elif crop_mode == "beam":
        rect.midleft = (0, target_size[1] // 2)
    else:
        rect.center = (target_size[0] // 2, target_size[1] // 2)

    canvas.blit(scaled, rect)
    return canvas


def draw_source_rect_debug(sheet, source_rects, output_path):
    DEBUG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    debug_surface = sheet.copy()
    colors = [
        (255, 80, 80),
        (80, 255, 120),
        (80, 180, 255),
        (255, 230, 80),
        (220, 110, 255),
        (255, 150, 60),
    ]
    for index, rect in enumerate(source_rects):
        pygame.draw.rect(debug_surface, colors[index % len(colors)], rect, 4)
    pygame.image.save(debug_surface, output_path)


def draw_clean_debug(frames, output_path):
    DEBUG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not frames:
        return

    frame_width, frame_height = frames[0].get_size()
    debug_surface = pygame.Surface((frame_width * len(frames), frame_height), pygame.SRCALPHA)
    for index, frame in enumerate(frames):
        debug_surface.blit(frame, (index * frame_width, 0))
        pygame.draw.rect(
            debug_surface,
            (255, 255, 255),
            pygame.Rect(index * frame_width, 0, frame_width, frame_height),
            1,
        )
    pygame.image.save(debug_surface, output_path)


def load_skill_effect_sheet(
    path,
    frame_count=SKILL_EFFECT_FRAME_COUNT,
    target_size=(320, 240),
    crop_mode="center_effect",
    manual_rects=None,
    debug_name=None,
):
    resolved_path = resolve_asset_path(path)
    print("Skill file path:", resolved_path)
    print("Skill frame count:", frame_count)
    print("Skill crop mode:", crop_mode)
    print("Skill target output size:", target_size)

    if not resolved_path.exists():
        print("Missing effect sheet:", resolved_path)
        return []

    sheet = pygame.image.load(str(resolved_path)).convert_alpha()
    source_rects = manual_rects or make_equal_source_rects(sheet, frame_count)
    frames = []
    repaired_pixels_total = 0

    for source_rect in source_rects:
        raw_frame = pygame.Surface(source_rect.size, pygame.SRCALPHA)
        raw_frame.blit(sheet, (0, 0), source_rect)
        raw_frame, repaired_pixels = repair_generated_background(raw_frame)
        repaired_pixels_total += repaired_pixels
        cropped = crop_visible_pixels(raw_frame)
        frames.append(place_on_canvas(cropped, target_size, crop_mode))

    print("Skill loaded frame count:", len(frames))
    if repaired_pixels_total > 0:
        print("Repaired opaque skill PNG background:", resolved_path.name)

    if debug_name and SKILL_WRITE_DEBUG_PREVIEWS:
        draw_source_rect_debug(
            sheet,
            source_rects,
            DEBUG_OUTPUT_DIR / f"{debug_name}_source_rects.png",
        )
        draw_clean_debug(frames, DEBUG_OUTPUT_DIR / f"{debug_name}_clean_debug.png")

    return frames


def load_fixed_frame_sheet(path, frame_count, scale=1.0, target_size=None, debug_name=None):
    resolved_path = resolve_asset_path(path)
    print("Skill fixed sheet file path:", resolved_path)
    print("Skill fixed frame count:", frame_count)

    if not resolved_path.exists():
        print("Missing fixed effect sheet:", resolved_path)
        return []

    sheet = pygame.image.load(str(resolved_path)).convert_alpha()
    frame_width = sheet.get_width() // frame_count
    frame_height = sheet.get_height()
    frames = []

    for index in range(frame_count):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        source_rect = pygame.Rect(index * frame_width, 0, frame_width, frame_height)
        frame.blit(sheet, (0, 0), source_rect)
        if target_size is not None:
            frame = pygame.transform.smoothscale(frame, target_size)
        elif scale != 1.0:
            scaled_size = (
                max(1, round(frame_width * scale)),
                max(1, round(frame_height * scale)),
            )
            frame = pygame.transform.smoothscale(frame, scaled_size)
        frames.append(frame)

    print("Skill fixed loaded frame count:", len(frames))
    print("Skill fixed frame size:", frames[0].get_size() if frames else None)
    print("[LOAD]", resolved_path, "frames:", len(frames), "frame_size:", frames[0].get_size() if frames else None)
    if debug_name == "energy_beam_attack" and frames:
        print("[PLAYER BEAM ATTACK FRAMES]", len(frames), frames[0].get_size())

    if debug_name and SKILL_WRITE_DEBUG_PREVIEWS:
        source_rects = [pygame.Rect(i * frame_width, 0, frame_width, frame_height) for i in range(frame_count)]
        draw_source_rect_debug(sheet, source_rects, DEBUG_OUTPUT_DIR / f"{debug_name}_source_rects.png")
        draw_clean_debug(frames, DEBUG_OUTPUT_DIR / f"{debug_name}_clean_debug.png")

    return frames


def load_manual_rect_sheet(path, rects, scale=1.0, debug_name=None):
    resolved_path = resolve_asset_path(path)
    print("Skill manual rect sheet file path:", resolved_path)
    print("Skill manual rect frame count:", len(rects))

    if not resolved_path.exists():
        print("Missing manual rect effect sheet:", resolved_path)
        return []

    sheet = pygame.image.load(str(resolved_path)).convert_alpha()
    frames = []

    for rect in rects:
        x, y, width, height = rect
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), pygame.Rect(x, y, width, height))
        if scale != 1.0:
            frame = pygame.transform.smoothscale(
                frame,
                (max(1, round(width * scale)), max(1, round(height * scale))),
            )
        frames.append(frame)

    print("[MANUAL RECT LOAD]", resolved_path, "frames:", len(frames), "rects:", rects)
    print("[LOAD]", resolved_path, "frames:", len(frames), "frame_size:", frames[0].get_size() if frames else None)
    return frames


def get_skill_frames(asset_key):
    if asset_key not in SKILL_FRAME_CACHE:
        config = SKILL_ASSETS[asset_key]
        if asset_key in PLAYER_SKILL_FRAME_COUNTS:
            SKILL_FRAME_CACHE[asset_key] = load_fixed_frame_sheet(
                config["path"],
                PLAYER_SKILL_FRAME_COUNTS[asset_key],
                scale=config.get("scale", 1.0),
                target_size=config["target_size"],
                debug_name=asset_key,
            )
        else:
            SKILL_FRAME_CACHE[asset_key] = load_skill_effect_sheet(
                config["path"],
                frame_count=SKILL_EFFECT_FRAME_COUNT,
                target_size=config["target_size"],
                crop_mode=config["crop_mode"],
                manual_rects=config["manual_rects"],
                debug_name=asset_key,
            )
    return SKILL_FRAME_CACHE[asset_key]


def print_skill_asset_debug_summary():
    for asset_key, config in SKILL_ASSETS.items():
        frames = get_skill_frames(asset_key)
        print(f"{config['label']}: {len(frames)}")


def get_animation_frame_info(asset_key, timer, frame_duration=0.08, loop=True):
    frames = get_skill_frames(asset_key)
    if not frames:
        return None, 0

    index = int(timer / frame_duration)
    if loop:
        index %= len(frames)
    else:
        index = min(index, len(frames) - 1)
    return frames[index], index


def blit_effect_frame(
    screen,
    effect_name,
    frame,
    frame_index,
    target_pos,
    camera=None,
    flip_x=False,
    anchor="center",
):
    if frame is None:
        return False

    image = pygame.transform.flip(frame, True, False) if flip_x else frame
    draw_pos = camera.apply_pos(target_pos) if camera else target_pos
    frame_rect = image.get_rect()

    if anchor == "midbottom":
        frame_rect.midbottom = draw_pos
    elif anchor == "midleft":
        frame_rect.midleft = draw_pos
    elif anchor == "midright":
        frame_rect.midright = draw_pos
    else:
        frame_rect.center = draw_pos

    screen.blit(image, frame_rect)
    return True


def draw_anchored_frame(screen, frame, world_pos, camera=None, anchor="center", flip_x=False):
    if frame is None:
        return None

    image = pygame.transform.flip(frame, True, False) if flip_x else frame
    screen_pos = camera.apply_pos(world_pos) if camera else world_pos
    rect = image.get_rect(**{anchor: screen_pos})
    screen.blit(image, rect)
    return rect


class TimeFreezeDomain:
    def __init__(self, center, visual_duration=TIME_FREEZE_VISUAL_DURATION):
        self.center = center
        self.radius = TIME_FREEZE_RADIUS
        self.visual_duration = visual_duration
        self.timer = visual_duration
        self.elapsed = 0
        self.alive = True
        print("Time Freeze freeze center:", self.center)

    def update(self, dt):
        self.timer -= dt
        self.elapsed += dt
        if self.timer <= 0:
            self.alive = False

    def draw(self, screen, camera=None):
        if self.elapsed > self.visual_duration:
            return

        effect_name = "time_freeze_action"
        frame, frame_index = get_animation_frame_info(
            effect_name,
            self.elapsed,
            frame_duration=self.visual_duration / max(1, len(get_skill_frames(effect_name))),
            loop=False,
        )
        if not blit_effect_frame(screen, effect_name, frame, frame_index, self.center, camera, anchor="midbottom"):
            center = camera.apply_pos(self.center) if camera else self.center
            pygame.draw.circle(screen, (80, 180, 255), center, self.radius, 3)
            pygame.draw.circle(screen, (30, 90, 150), center, self.radius // 3, 1)


class OrbitBlade:
    def __init__(self, player, index, total_blades):
        self.rect = pygame.Rect(0, 0, ORBIT_BLADE_SIZE, ORBIT_BLADE_SIZE)
        self.angle = index * (2 * math.pi / total_blades)
        self.index = index
        self.state = "orbit"
        self.fire_delay = ORBIT_BLADE_READY_TIME + index * ORBIT_BLADE_FIRE_DELAY
        self.vel_x = 0
        self.vel_y = 0
        self.damage = ORBIT_BLADE_DAMAGE
        self.lifetime = ORBIT_BLADE_LIFETIME
        self.alive = True
        self.has_hit = False
        self.facing = player.facing
        self.elapsed = 0
        self.hit_effect = None
        self.target = None
        self.update_orbit_position(player)

    def update(self, dt, player, targets):
        if not self.alive:
            return

        self.elapsed += dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            self.state = "dead"
            return

        if self.state == "orbit":
            self.angle += ORBIT_BLADE_ORBIT_SPEED * dt
            self.fire_delay -= dt
            self.update_orbit_position(player)

            if self.fire_delay <= 0:
                target = self.find_target(targets, player.rect.center)
                if target is not None:
                    print("Orbit Blades target chosen:", target.rect.center)
                    self.fire_at(target.rect.center)
                else:
                    print("Orbit Blades target chosen: none, firing forward")
                    self.fire_forward(player.facing)
                print("Orbit Blades projectile spawned:", self.index)

        elif self.state == "fired":
            if self.target is None or not getattr(self.target, "alive", False):
                self.target = self.find_target(targets, self.rect.center)
            if self.target is not None:
                self.fire_at(self.target.rect.center)
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            self.check_enemy_collision(targets)

    def update_orbit_position(self, player):
        x = player.rect.centerx + math.cos(self.angle) * ORBIT_BLADE_RADIUS
        y = player.rect.centery + math.sin(self.angle) * ORBIT_BLADE_RADIUS
        self.rect.center = (round(x), round(y))

    def find_target(self, targets, origin):
        alive_targets = [target for target in targets if getattr(target, "alive", False)]
        if not alive_targets:
            return None

        in_range = [
            target for target in alive_targets
            if math.hypot(target.rect.centerx - origin[0], target.rect.centery - origin[1]) <= ORBIT_BLADE_TARGET_RANGE
        ]
        if not in_range:
            return None

        in_range.sort(
            key=lambda target: math.hypot(
                target.rect.centerx - self.rect.centerx,
                target.rect.centery - self.rect.centery,
            )
        )
        return in_range[self.index % len(in_range)]

    def fire_at(self, target_center):
        dx = target_center[0] - self.rect.centerx
        dy = target_center[1] - self.rect.centery
        distance = max(1, math.hypot(dx, dy))
        self.vel_x = (dx / distance) * ORBIT_BLADE_PROJECTILE_SPEED
        self.vel_y = (dy / distance) * ORBIT_BLADE_PROJECTILE_SPEED
        self.state = "fired"

    def fire_forward(self, facing):
        self.vel_x = ORBIT_BLADE_PROJECTILE_SPEED * facing
        self.vel_y = 0
        self.state = "fired"

    def check_enemy_collision(self, targets):
        if self.has_hit:
            return

        for enemy in targets:
            if not getattr(enemy, "alive", False):
                continue
            if not self.rect.colliderect(enemy.rect):
                continue
            enemy.take_damage(self.damage)
            self.has_hit = True
            self.alive = False
            self.state = "dead"
            self.hit_effect = SkillSpriteEffect("orbit_blade_hit", self.rect.center, duration=0.25)
            print("Orbit blade hit enemy")
            return

    def draw(self, screen, camera=None):
        if not self.alive:
            return

        if self.state == "orbit":
            effect_name = "orbit_blades_ready"
            frame, frame_index = get_animation_frame_info(effect_name, self.elapsed, loop=True)
        else:
            effect_name = "orbit_blade_projectile"
            frame, frame_index = get_animation_frame_info(effect_name, self.elapsed, loop=True)

        if not blit_effect_frame(
            screen,
            effect_name,
            frame,
            frame_index,
            self.rect.center,
            camera,
            flip_x=self.vel_x < 0,
            anchor="center",
        ):
            draw_rect = camera.apply_rect(self.rect) if camera else self.rect
            pygame.draw.ellipse(screen, (255, 240, 90), draw_rect)
            pygame.draw.ellipse(screen, (230, 255, 255), draw_rect, 1)


class EnergyBeamEffect:
    def __init__(
        self,
        player,
        get_rect_func,
        get_origin_func,
        facing=1,
        ready_duration=ENERGY_BEAM_READY_DURATION,
        active_duration=ENERGY_BEAM_ATTACK_DURATION,
    ):
        self.player = player
        self.get_rect_func = get_rect_func
        self.get_origin_func = get_origin_func
        self.rect = get_rect_func(player)
        self.facing = facing
        self.ready_duration = ready_duration
        self.active_duration = active_duration
        self.timer = ready_duration + active_duration
        self.elapsed = 0
        self.alive = True

    def update(self, dt):
        self.timer -= dt
        self.elapsed += dt
        self.rect = self.get_rect_func(self.player)
        if self.timer <= 0:
            self.alive = False

    def draw(self, screen, camera=None):
        if self.elapsed < self.ready_duration:
            effect_name = "energy_beam_ready"
            frame, frame_index = get_animation_frame_info(effect_name, self.elapsed, loop=False)
            origin = self.get_origin_func(self.player)
            blit_effect_frame(screen, effect_name, frame, frame_index, origin, camera, flip_x=self.facing < 0)
            return

        effect_name = "energy_beam_attack"
        active_elapsed = self.elapsed - self.ready_duration
        frame, frame_index = get_animation_frame_info(
            effect_name,
            active_elapsed,
            frame_duration=ENERGY_BEAM_FRAME_DURATION,
            loop=True,
        )
        origin_x, origin_y = self.get_origin_func(self.player)
        target_pos = (
            origin_x + ENERGY_BEAM_ATTACK_OFFSET_X * self.facing,
            origin_y + ENERGY_BEAM_ATTACK_OFFSET_Y,
        )
        anchor = "midleft" if self.facing == 1 else "midright"
        if draw_anchored_frame(
            screen,
            frame,
            target_pos,
            camera,
            anchor=anchor,
            flip_x=self.facing < 0,
        ):
            return

        draw_rect = camera.apply_rect(self.rect) if camera else self.rect
        pygame.draw.rect(screen, (80, 230, 255), draw_rect)
        pygame.draw.rect(screen, (255, 255, 255), draw_rect, 2)


class SkillSpriteEffect:
    def __init__(self, asset_key, center, duration=0.35, flip_x=False, anchor=None):
        self.asset_key = asset_key
        self.center = center
        self.duration = max(duration, SKILL_EFFECT_FRAME_COUNT * 0.08)
        self.timer = self.duration
        self.elapsed = 0
        self.flip_x = flip_x
        self.anchor = anchor or self.get_default_anchor(asset_key)
        self.alive = True

    def get_default_anchor(self, asset_key):
        crop_mode = SKILL_ASSETS.get(asset_key, {}).get("crop_mode")
        if crop_mode == "ground_effect":
            return "midbottom"
        return "center"

    def update(self, dt):
        self.timer -= dt
        self.elapsed += dt
        if self.timer <= 0:
            self.alive = False

    def draw(self, screen, camera=None):
        frame, frame_index = get_animation_frame_info(self.asset_key, self.elapsed, loop=False)
        if blit_effect_frame(
            screen,
            self.asset_key,
            frame,
            frame_index,
            self.center,
            camera,
            flip_x=self.flip_x,
            anchor=self.anchor,
        ):
            return

        center = camera.apply_pos(self.center) if camera else self.center
        pygame.draw.circle(screen, (120, 255, 180), center, 34, 3)


class SoulAnchorLoop:
    def __init__(self, center, duration):
        self.center = center
        self.timer = duration
        self.elapsed = 0
        self.alive = True

    def update(self, dt):
        self.timer -= dt
        self.elapsed += dt
        if self.timer <= 0:
            self.alive = False

    def draw(self, screen, camera=None):
        effect_name = "soul_anchor_loop"
        frame, frame_index = get_animation_frame_info(effect_name, self.elapsed, loop=True)
        if blit_effect_frame(
            screen,
            effect_name,
            frame,
            frame_index,
            self.center,
            camera,
            anchor="midbottom",
        ):
            return

        center = camera.apply_pos(self.center) if camera else self.center
        pygame.draw.circle(screen, (120, 255, 180), center, 28, 3)
