import random


def calculate_damage(player, weapon_damage):
    base_damage = weapon_damage
    bonus_damage = base_damage * player.bonus_attack_percent
    damage_before_crit = base_damage + bonus_damage

    is_critical = random.random() < player.crit_chance

    if is_critical:
        final_damage = damage_before_crit * player.crit_damage
    else:
        final_damage = damage_before_crit

    return round(final_damage), is_critical
