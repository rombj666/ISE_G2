WEAPONS = {
    "light_weapon": {
        "id": "light_weapon",
        "name": "Light",
        "weapon_type": "melee",
        "damage": 20,
        "cooldown": 0.25,
        "range": 45,
        "width": 45,
        "height": 35,
        "effect": "fast_slash",
    },
    "heavy_weapon": {
        "id": "heavy_weapon",
        "name": "Heavy",
        "weapon_type": "melee",
        "damage": 40,
        "cooldown": 0.75,
        "range": 80,
        "width": 80,
        "height": 45,
        "effect": "heavy_slash",
    },
    "shooter_weapon": {
        "id": "shooter_weapon",
        "name": "Shooter",
        "weapon_type": "projectile",
        "damage": 12,
        "cooldown": 0.40,
        "range": 45,
        "width": 16,
        "height": 10,
        "effect": "projectile",
        "projectile_speed": 9,
        "projectile_gravity": 0.15,
    },
    "shield_weapon": {
        "id": "shield_weapon",
        "name": "Shield",
        "weapon_type": "shield",
        "damage": 8,
        "cooldown": 0.40,
        "range": 40,
        "width": 40,
        "height": 40,
        "effect": "shield_bash",
        "can_block": True,
    },
    "grapple_weapon": {
        "id": "grapple_weapon",
        "name": "Grapple",
        "weapon_type": "grapple",
        "damage": 28,
        "cooldown": 0.50,
        "range": 120,
        "width": 120,
        "height": 25,
        "effect": "grapple_hook",
        "stun_time": 0.5,
        "pull_strength": 10,
    },
}


def get_weapon(weapon_id):
    if weapon_id in WEAPONS:
        return WEAPONS[weapon_id]
    return WEAPONS["light_weapon"]


def get_all_weapons():
    return WEAPONS
