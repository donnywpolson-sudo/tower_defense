from .config import (
    BASE_ENEMIES_PER_WAVE,
    ENEMIES_PER_WAVE_GROWTH,
    MAX_WAVE,
    MIN_SPAWN_INTERVAL,
)


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


def get_wave_affix(wave_number):
    if wave_number < 8 or wave_number % 5 == 0:
        return None
    affixes = [None, "haste", "regen", "armored", "split"]
    return affixes[wave_number % len(affixes)]


def get_wave_label(wave_number):
    label = get_wave_enemy_kind(wave_number).title()
    affix = get_wave_affix(wave_number)
    if affix:
        label += f" + {affix.title()}"
    return label


def get_boss_count_for_wave(wave_number):
    if wave_number % 5 != 0:
        return 0
    if wave_number <= MAX_WAVE:
        return 1 + wave_number // 10
    return 1 + wave_number // 10


def get_regular_enemy_count(wave_number):
    return BASE_ENEMIES_PER_WAVE + wave_number * ENEMIES_PER_WAVE_GROWTH


def get_spawn_interval(wave_number):
    return max(MIN_SPAWN_INTERVAL, 0.62 - wave_number * 0.012)
