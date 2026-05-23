import json
from pathlib import Path

import pygame


class MovingPlatform:
    def __init__(self, rect, name="", move_type="vertical", speed=100, end_y=None, auto_start=True):
        self.rect = rect
        self.name = name
        self.move_type = move_type
        self.speed = float(speed)
        self.start_x = rect.x
        self.start_y = rect.y
        self.current_y = float(rect.y)
        self.end_y = int(round(float(end_y))) if end_y is not None else rect.y
        self.auto_start = bool(auto_start)
        self.active = False
        self.arrived = False

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.current_y = float(self.start_y)
        self.active = False
        self.arrived = False

    def player_is_on_top(self, player):
        horizontal_overlap = (
            player.rect.right > self.rect.left + 4
            and player.rect.left < self.rect.right - 4
        )
        vertical_contact = abs(player.rect.bottom - self.rect.top) <= 8
        return horizontal_overlap and vertical_contact and player.vel_y >= 0

    def update(self, dt, player):
        if self.arrived or self.speed <= 0:
            return

        player_on_platform = self.player_is_on_top(player)

        if self.auto_start and player_on_platform:
            self.active = True
        elif not self.auto_start:
            self.active = True

        if not self.active:
            return

        old_y = self.rect.y
        direction = 1 if self.end_y > self.current_y else -1
        next_y = self.current_y + direction * self.speed * dt

        if direction > 0:
            self.current_y = min(self.end_y, next_y)
        else:
            self.current_y = max(self.end_y, next_y)

        self.rect.y = int(round(self.current_y))
        delta_y = self.rect.y - old_y

        if player_on_platform and delta_y != 0:
            player.rect.y += delta_y
            player.vel_y = 0
            player.on_ground = True

        if self.rect.y == self.end_y:
            self.arrived = True


def load_tiled_map(path):
    path = Path(path)
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    width = int(data.get("width", 0)) * int(data.get("tilewidth", 1))
    height = int(data.get("height", 0)) * int(data.get("tileheight", 1))

    layers = {layer.get("name", "").lower(): layer for layer in data.get("layers", [])}

    platforms = _load_rect_layer(layers, "collision")
    moving_platforms = _load_moving_platforms(layers)
    platforms.extend(platform.rect for platform in moving_platforms)

    spawns = _load_spawns(layers)
    doors = _load_doors(layers)
    fulcrums = _load_fulcrums(layers)
    checkpoints = _load_named_rects(layers, "checkpoints")
    interactables = _load_named_rects(layers, "interactables")
    hazards = _load_named_rects(layers, "hazards")

    shop_rect = None
    for item in interactables:
        item_type = str(item.get("type") or item.get("name") or "").lower()
        if item_type == "merchant":
            shop_rect = item["rect"]
            break

    return {
        "width": width,
        "height": height,
        "platforms": platforms,
        "moving_platforms": moving_platforms,
        "player_spawn": spawns.get("player_spawn"),
        "enemy_spawns": spawns.get("enemy_spawns", []),
        "boss_spawn": spawns.get("boss_spawn"),
        "doors": doors,
        "fulcrums": fulcrums,
        "checkpoints": checkpoints,
        "interactables": interactables,
        "hazards": hazards,
        "shop_rect": shop_rect,
    }


def _layer_objects(layers, layer_name):
    layer = layers.get(layer_name.lower())
    if not layer:
        return []
    return layer.get("objects", []) or []


def _properties(obj):
    props = {}
    for prop in obj.get("properties", []) or []:
        props[prop.get("name")] = prop.get("value")
    return props


def _rect(obj):
    return pygame.Rect(
        int(round(float(obj.get("x", 0)))),
        int(round(float(obj.get("y", 0)))),
        int(round(float(obj.get("width", 0)))),
        int(round(float(obj.get("height", 0)))),
    )


def _spawn_point(obj):
    rect = _rect(obj)
    if rect.width == 0 and rect.height == 0:
        return (rect.x, rect.y)
    return rect.midbottom


def _load_rect_layer(layers, layer_name):
    rects = []
    for obj in _layer_objects(layers, layer_name):
        rect = _rect(obj)
        if rect.width > 0 and rect.height > 0:
            rects.append(rect)
    return rects


def _load_moving_platforms(layers):
    moving_platforms = []
    for obj in _layer_objects(layers, "movingplatforms"):
        rect = _rect(obj)
        if rect.width <= 0 or rect.height <= 0:
            continue

        props = _properties(obj)
        moving_platforms.append(
            MovingPlatform(
                rect,
                name=obj.get("name", ""),
                move_type=str(props.get("move_type", "vertical")),
                speed=_float(props.get("speed"), 100),
                end_y=props.get("end_y", rect.y),
                auto_start=_bool(props.get("auto_start"), True),
            )
        )
    return moving_platforms


def _load_spawns(layers):
    result = {"enemy_spawns": []}
    objects = list(_layer_objects(layers, "spawns"))

    # Temporary friendliness for your current MAP 2 export:
    # the player spawn rectangle is in player_guide and named "Spawns".
    if not objects:
        objects.extend(_layer_objects(layers, "player_guide"))

    for obj in objects:
        props = _properties(obj)
        name = str(obj.get("name") or props.get("name") or "").lower()
        point = _spawn_point(obj)

        if name in ("player_spawn", "spawn", "spawns", "kael_spawn", "start"):
            result["player_spawn"] = point
        elif name == "boss_spawn":
            result["boss_spawn"] = point
        elif name.startswith("enemy"):
            result["enemy_spawns"].append(point)

    return result


def _load_doors(layers):
    doors = []
    for obj in _layer_objects(layers, "doors"):
        rect = _rect(obj)
        if rect.width <= 0 or rect.height <= 0:
            continue

        props = _properties(obj)
        doors.append(
            {
                "rect": rect,
                "target_map": props.get("target_map", props.get("target", 2)),
                "label": str(props.get("label") or obj.get("name") or "Level 2"),
                "visible": _bool(props.get("visible"), True),
                "auto": _bool(props.get("auto"), False),
            }
        )
    return doors


def _load_fulcrums(layers):
    fulcrums = []
    for obj in _layer_objects(layers, "fulcrums"):
        rect = _rect(obj)
        if rect.width <= 0 or rect.height <= 0:
            continue

        props = _properties(obj)
        anchor = (
            int(round(_float(props.get("anchor_x"), rect.centerx))),
            int(round(_float(props.get("anchor_y"), rect.centery))),
        )
        target = (
            int(round(_float(props.get("target_x"), anchor[0]))),
            int(round(_float(props.get("target_y"), anchor[1]))),
        )

        fulcrums.append(
            {
                "rect": rect,
                "anchor": anchor,
                "target": target,
                "used": False,
                "name": obj.get("name", ""),
                "interact_distance": _float(props.get("interact_distance"), 180),
                "requires_grapple_weapon": _bool(props.get("requires_grapple_weapon"), False),
            }
        )
    return fulcrums


def _load_named_rects(layers, layer_name):
    items = []
    for obj in _layer_objects(layers, layer_name):
        rect = _rect(obj)
        if rect.width <= 0 or rect.height <= 0:
            continue

        props = _properties(obj)
        item = {
            "rect": rect,
            "name": obj.get("name", ""),
            "type": obj.get("type", ""),
        }
        item.update(props)
        items.append(item)
    return items


def _float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _bool(value, default):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")
