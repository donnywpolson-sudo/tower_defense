from .config import (
    BASE_ENEMIES_PER_WAVE,
    ENEMIES_PER_WAVE_GROWTH,
    MAX_WAVE,
    MIN_SPAWN_INTERVAL,
)


WAVE_MODIFIERS = {
    "haste": {
        "label": "Surge",
        "description": "Malware packets move faster.",
        "recommendation": "Surge: add Frost, Barracks, or Quarantine control.",
        "color": (235, 95, 190),
        "effects": {"speed_multiplier": 1.22},
    },
    "regen": {
        "label": "Self-Healing",
        "description": "Packets regenerate health until cleansed.",
        "recommendation": "Self-Healing: use Poison, sustained fire, or burst.",
        "color": (110, 220, 95),
        "effects": {"regen_scale": 0.012},
    },
    "armored": {
        "label": "Encrypted",
        "description": "Packets gain extra shield layers and resist damage.",
        "recommendation": "Encrypted: Sniper pierce, Cannon breach, or EMP.",
        "color": (185, 185, 205),
        "effects": {"shield_hits": 1, "damage_multiplier": 0.8},
    },
    "split": {
        "label": "Fragmenting",
        "description": "Packets split into smaller fragments when deleted.",
        "recommendation": "Fragmenting: add splash, chain, or Machine Gun cleanup.",
        "color": (230, 135, 80),
        "effects": {"death_spawns": 1},
    },
}


def get_wave_enemy_kind(wave_number):
    if wave_number < 5:
        wave_types = ["normal", "swarm", "fast", "tank"]
    elif wave_number < 10:
        wave_types = ["swarm", "fast", "tank", "normal"]
    elif wave_number < 14:
        wave_types = ["shield", "tank", "fast", "swarm"]
    elif wave_number < 18:
        wave_types = ["flying", "shield", "tank", "fast"]
    else:
        wave_types = ["shield", "flying", "armored", "tank", "fast", "swarm"]

    return wave_types[(wave_number - 1) % len(wave_types)]


def get_wave_modifier(wave_number):
    if wave_number < 8 or wave_number % 5 == 0:
        return None
    affixes = [None, "haste", "regen", "armored", "split"]
    return affixes[wave_number % len(affixes)]


def get_wave_affix(wave_number):
    return get_wave_modifier(wave_number)


def get_wave_modifier_data(wave_number):
    modifier = get_wave_modifier(wave_number)
    if modifier is None:
        return None
    return WAVE_MODIFIERS[modifier]


def get_wave_label(wave_number):
    label = get_wave_enemy_kind(wave_number).title()
    modifier = get_wave_modifier_data(wave_number)
    if modifier:
        label += f" + {modifier['label']}"
    return label


def get_boss_count_for_wave(wave_number):
    if wave_number % 5 != 0:
        return 0
    if wave_number <= MAX_WAVE:
        return 1 + wave_number // 10
    return 1 + wave_number // 10


def get_commander_count_for_wave(wave_number):
    if get_boss_count_for_wave(wave_number) > 0:
        return 0
    if get_wave_modifier(wave_number) is None:
        return 0
    return 1 if wave_number >= 8 and wave_number % 4 == 0 else 0


def get_regular_enemy_count(wave_number):
    return BASE_ENEMIES_PER_WAVE + wave_number * ENEMIES_PER_WAVE_GROWTH


def get_spawn_interval(wave_number):
    return max(MIN_SPAWN_INTERVAL, 0.62 - wave_number * 0.012)
