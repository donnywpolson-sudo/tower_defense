import sys
import math
import argparse
import asyncio
import copy
import random
import pygame

from .assets import draw_sprite_centered, load_image, load_sound, load_sound_any
from .audio import make_tone
from .config import *
from .crash_logging import write_crash_log
from .data import *
from .geometry import dist, distance_segment_to_rect, distance_to_segment
from .mapgen import generate_random_map
from .particles import ParticleManager
from .rendering import RenderOptions, make_renderer
from .waves import (
    WAVE_MODIFIERS,
    get_boss_count_for_wave as get_boss_count_for_wave_data,
    get_commander_count_for_wave as get_commander_count_for_wave_data,
    get_regular_enemy_count as get_regular_enemy_count_data,
    get_spawn_interval as get_spawn_interval_data,
    get_wave_affix as get_wave_affix_data,
    get_wave_enemy_kind as get_wave_enemy_kind_data,
    get_wave_label as get_wave_label_data,
    get_wave_modifier_data as get_wave_modifier_data_for_wave,
)

pygame.init()

screen = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 22)
tiny_font = pygame.font.SysFont(None, 18)
window_width, window_height = WIDTH, HEIGHT
scale = 1
offset_x = 0
offset_y = 0
current_map_index = 0
active_map = generate_random_map()
spawn_path_index = 0
money = STARTING_MONEY
lives = STARTING_LIVES
score = 0
research_points = 0
wave = 1
game_over = False
victory = False
paused = False
game_speed = 1.0
screen_shake_timer = 0
screen_shake_strength = 0
boss_warning_timer = 0
pending_card_choices = []
run_damage_bonus = 0.0
run_range_bonus = 0.0
next_wave_bounty_bonus = 0
next_wave_bounty_wave = None

enemies = []
towers = []
projectiles = []
effects = []

spawn_timer = 0
spawned_this_wave = 0
wave_active = False
selected_tower = None
selected_build_type = None
endless_mode = False
stars = 0
starting_money_bonus_level = 0
tower_damage_bonus_level = 0
run_stars_awarded = False
sound_enabled = False
sfx_enabled = True
music_enabled = True
sounds = {}
images = {}
last_sound_times = {}
music_loaded = False
current_music_track = None
renderer_backend = None
render_options = RenderOptions(
    renderer=RENDERER,
    enable_glow=ENABLE_GLOW,
    enable_particles=ENABLE_PARTICLES,
    enable_screen_shake=ENABLE_SCREEN_SHAKE,
    max_particles=MAX_PARTICLES,
)
particle_manager = ParticleManager(MAX_PARTICLES)
glow_cache = {}
scaled_sprite_cache = {}

COMMANDER_AURA_RADIUS = 118
PACKET_TRAIL_LIMIT = 8
PACKET_TRAIL_LIFETIME = 0.34
CORE_WARNING_RATIO = 0.35
RANSOMWARE_LOCK_RADIUS = 150
RANSOMWARE_LOCK_DURATION = 2.4
RANSOMWARE_LOCK_INTERVAL = 5.8

ROLE_ICON_COLORS = {
    "fast": (255, 230, 100),
    "single": (210, 235, 245),
    "aoe": (235, 145, 85),
    "slow": (150, 225, 255),
    "dot": (125, 235, 95),
    "support": (245, 225, 145),
    "air": (185, 205, 255),
    "hold": (220, 170, 95),
    "armor": (210, 210, 225),
}

TOWER_ROLE_ICONS = {
    "machine_gun": ("fast", "single"),
    "cannon": ("aoe", "armor"),
    "frost": ("slow", "aoe"),
    "poison": ("dot", "slow"),
    "support": ("support", "single"),
    "sniper": ("single", "armor", "air"),
    "tesla": ("air", "aoe", "fast"),
    "barracks": ("hold", "slow"),
}

TOWER_TOOLTIP_SUMMARY = {
    "machine_gun": ("Fast single-target", "Best: swarms", "Weak: armor"),
    "cannon": ("Slow massive AoE", "Best: groups", "Weak: flying"),
    "frost": ("Slow and freeze", "Best: fast", "Weak: damage"),
    "poison": ("Poison and burn", "Best: tanks", "Weak: leaks"),
    "support": ("Mana support casts", "Best: clusters", "Weak: solo"),
    "sniper": ("Long-range execute", "Best: armor", "Weak: swarms"),
    "tesla": ("Chain anti-air", "Best: flying", "Weak: cost"),
    "barracks": ("Ground hold zone", "Best: lanes", "Weak: flying"),
}

CARD_POOL = {
    "cpu_cache": {
        "label": "CPU Cache",
        "description": "Gain emergency CPU for new defenses.",
        "color": (245, 220, 120),
    },
    "research_grant": {
        "label": "Tech Cache",
        "description": "Gain tech for mastery upgrades.",
        "color": (150, 220, 255),
    },
    "core_patch": {
        "label": "HP Patch",
        "description": "Repair base health.",
        "color": (130, 225, 145),
    },
    "range_patch": {
        "label": "Range Boost",
        "description": "All towers gain permanent range.",
        "color": (180, 215, 245),
    },
    "damage_patch": {
        "label": "Damage Boost",
        "description": "All towers gain permanent damage.",
        "color": (245, 155, 110),
    },
    "bounty_trace": {
        "label": "Bounty Trace",
        "description": "Next wave pays bonus CPU per packet.",
        "color": (245, 225, 95),
    },
}


def is_web_runtime():
    return sys.platform == "emscripten"


def parse_runtime_options(argv=None):
    parser = argparse.ArgumentParser(description="Signal Defense")
    parser.add_argument("--renderer", choices=("pygame", "opengl"), default=RENDERER)
    parser.add_argument("--enable-glow", dest="enable_glow", action="store_true", default=ENABLE_GLOW)
    parser.add_argument("--disable-glow", dest="enable_glow", action="store_false")
    parser.add_argument("--enable-particles", dest="enable_particles", action="store_true", default=ENABLE_PARTICLES)
    parser.add_argument("--disable-particles", dest="enable_particles", action="store_false")
    parser.add_argument("--enable-screen-shake", dest="enable_screen_shake", action="store_true", default=ENABLE_SCREEN_SHAKE)
    parser.add_argument("--disable-screen-shake", dest="enable_screen_shake", action="store_false")
    parser.add_argument("--max-particles", type=int, default=MAX_PARTICLES)
    args = parser.parse_args(argv)
    return RenderOptions(
        renderer=args.renderer,
        enable_glow=args.enable_glow,
        enable_particles=args.enable_particles,
        enable_screen_shake=args.enable_screen_shake,
        max_particles=max(0, args.max_particles),
    )

def draw_text(text, x, y, color=(240, 240, 240)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_small_text(text, x, y, color=(230, 230, 230)):
    img = small_font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_small_text_right(text, right_x, y, color=(230, 230, 230)):
    img = small_font.render(text, True, color)
    screen.blit(img, (right_x - img.get_width(), y))


def draw_tiny_text(text, x, y, color=(220, 220, 210)):
    img = tiny_font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_tiny_text_right(text, right_x, y, color=(220, 220, 210)):
    img = tiny_font.render(text, True, color)
    screen.blit(img, (right_x - img.get_width(), y))


def wrap_text(text, max_chars):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def truncate_text(text, max_chars):
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "."

def current_paths():
    return active_map.get("paths") or MAPS[current_map_index]["paths"]


def current_theme():
    return active_map.get("theme", MAPS[current_map_index].get("theme", "forest"))


def primary_path():
    return current_paths()[0]


def all_path_segments():
    for path in current_paths():
        for i in range(len(path) - 1):
            yield path[i], path[i + 1]


def can_change_map():
    return wave == 1 and not wave_active and not enemies and not towers and not game_over and not victory


def generate_new_active_map(seed=None):
    global active_map, spawn_path_index

    active_map = generate_random_map(seed)
    spawn_path_index = 0
    return active_map


def get_research_reward(completed_wave):
    return 1 + completed_wave // 5


def get_min_towers_for_upgrade(current_level):
    return HIGH_TIER_MIN_TOWERS.get(current_level, 1)


def get_animation_frame(options, speed=220):
    if not options:
        return None
    index = (pygame.time.get_ticks() // speed) % len(options)
    return options[index]


def clamp(value, low, high):
    return max(low, min(high, value))


def blend_color(color, target, amount):
    amount = clamp(amount, 0, 1)
    return tuple(int(channel + (target_channel - channel) * amount) for channel, target_channel in zip(color, target))


def packet_status_color(enemy):
    if enemy.commander:
        return (245, 220, 90)
    if enemy.boss:
        return (255, 90, 80)
    if enemy.freeze_timer > 0:
        return (190, 245, 255)
    if enemy.slow_timer > 0:
        return (105, 190, 255)
    if enemy.poison_timer > 0:
        return (130, 245, 110)
    if enemy.burn_timer > 0:
        return (255, 130, 70)
    if enemy.shield_hits > 0 or enemy.affix == "armored":
        return (220, 230, 255)
    if enemy.affix and enemy.affix in WAVE_MODIFIERS:
        return WAVE_MODIFIERS[enemy.affix]["color"]
    if enemy.kind == "fast":
        return (235, 95, 190)
    if enemy.flying:
        return (185, 120, 245)
    return (95, 235, 160)


def active_bosses():
    return [enemy for enemy in enemies if enemy.boss]


def get_boss_protocol_for_wave(wave_number):
    if wave_number in (10, MAX_WAVE):
        return "ransomware"
    return None


def get_wave_recommendation(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    kind = get_wave_enemy_kind(preview_wave)
    affix = get_wave_affix(preview_wave)
    modifier = get_wave_modifier_data(preview_wave)
    bosses = get_boss_count_for_wave(preview_wave)
    boss_protocol = get_boss_protocol_for_wave(preview_wave)
    commanders = get_commander_count_for_wave(preview_wave)
    recommendations = []
    tower_types = []

    if bosses:
        recommendations.append("Boss incoming. Add Sniper or Artillery.")
        tower_types.extend(["sniper", "cannon"])
    if boss_protocol == "ransomware":
        recommendations.append("Ransomware: locks towers. Spread defenses.")
        tower_types.extend(["support", "sniper"])
    if commanders:
        recommendations.append("Commander packet: focus-fire the aura source.")
        tower_types.extend(["sniper", "tesla"])
    if modifier:
        recommendations.append(modifier["recommendation"])
    if kind == "shield":
        recommendations.append("Shield: Sniper or Artillery.")
        tower_types.extend(["sniper", "cannon"])
    if kind == "armored" or affix == "armored":
        recommendations.append("Armored: Sniper pierce or Artillery.")
        tower_types.extend(["sniper", "cannon"])
    if kind == "flying":
        recommendations.append("Flying: Tesla or Sniper.")
        tower_types.extend(["tesla", "sniper"])
    if kind in ("fast",) or affix == "haste":
        recommendations.append("Fast/Haste: Frost and Garrison control.")
        tower_types.extend(["frost", "barracks"])
    if kind == "swarm" or affix == "split":
        recommendations.append("Split/Swarm: Artillery splash or Gunner cleanup.")
        tower_types.extend(["cannon", "machine_gun"])

    if not recommendations:
        recommendations.append("Balanced wave. Upgrade key towers.")
        tower_types.extend(["machine_gun", "support"])

    unique_towers = []
    for tower_type in tower_types:
        if tower_type not in unique_towers:
            unique_towers.append(tower_type)
    return recommendations[:2], unique_towers[:3]


def has_tower_type(tower_type):
    return any(tower.tower_type == tower_type for tower in towers)


def has_tower_mechanic(mechanic):
    return any(tower.branch_has(mechanic) for tower in towers)


def towers_with_mechanic(mechanic):
    return [tower for tower in towers if tower.branch_has(mechanic)]


def apply_synergy_damage(tower_type, enemy, amount, damage_type):
    multiplier = 1.0
    labels = []

    if tower_type == "cannon":
        if enemy.freeze_timer > 0 and has_tower_type("frost"):
            multiplier *= 1.35
            labels.append("SHATTER")
        if enemy.barracks_hold_timer > 0 and has_tower_type("barracks"):
            multiplier *= 1.20
            labels.append("BREACH")
        if enemy.barracks_hold_timer > 0 and has_tower_mechanic("mine"):
            multiplier *= 1.12
            labels.append("KILL ZONE")
    elif tower_type == "machine_gun" and enemy.slow_timer > 0 and has_tower_type("frost"):
        multiplier *= 1.15
        labels.append("FOCUS")

    if enemy.marked_timer > 0 and tower_type in ("archer", "machine_gun", "sniper", "tesla"):
        multiplier *= 1.12
        labels.append("SCAN")

    return amount * multiplier, labels


def branch_rank(tower, level=None):
    if tower is None or tower.selected_branch is None:
        return 0
    check_level = tower.level if level is None else level
    if check_level < BRANCH_UNLOCK_LEVEL:
        return 0
    return max(1, min(8, check_level - BRANCH_UNLOCK_LEVEL + 1))


def mastery_rank(tower, level=None):
    if tower is None or tower.selected_branch is None:
        return 0
    check_level = tower.level if level is None else level
    if check_level < PARAGON_LEVEL:
        return 0
    return max(1, min(5, check_level - PARAGON_LEVEL + 1))


def branch_upgrade_effect(tower, next_level):
    branch = tower.branch_data() if tower else None
    if branch is None:
        return None
    return branch.get("upgrade_effects", {}).get(next_level)


def preview_upgraded_tower(tower):
    if tower is None or tower.upgrade_cost is None:
        return None

    preview = copy.copy(tower)
    preview.mutations = list(tower.mutations)
    preview.available_mutations = list(tower.available_mutations)
    preview.notified_mutations = set(tower.notified_mutations)
    preview.level += 1
    if preview.level == PARAGON_LEVEL:
        preview.is_paragon = True
        preview.apply_paragon_stats()
    elif preview.level > PARAGON_LEVEL:
        preview.apply_mastery_stats()
    else:
        preview.apply_weapon_level_stats()
    return preview


def format_stat_delta(label, delta, decimals=0, suffix=""):
    if abs(delta) < 0.0001:
        return None
    if decimals:
        amount = f"{delta:+.{decimals}f}"
    else:
        amount = f"{delta:+.0f}"
    return f"{label} {amount}{suffix}"


def branch_upgrade_description(tower, next_level):
    preview = preview_upgraded_tower(tower)
    if preview is None:
        return tower_tier_description(tower.tower_type, next_level, tower.selected_branch)

    parts = []
    if tower.tower_type == "support":
        mana_delta = preview.support_mana_rate() - tower.support_mana_rate()
        parts.append(format_stat_delta("Range", preview.range - tower.range))
        parts.append(format_stat_delta("Mana", mana_delta, 1, "/s"))
    else:
        parts.append(format_stat_delta("DMG", preview.damage - tower.damage))
        parts.append(format_stat_delta("Range", preview.range - tower.range))

    fire_delta = preview.fire_rate - tower.fire_rate
    if abs(fire_delta) >= 0.001:
        parts.append(f"Fire {fire_delta:+.3f}s")

    effect = branch_upgrade_effect(tower, next_level)
    if effect:
        parts.append(effect)

    compact = [part for part in parts if part]
    if compact:
        return " | ".join(compact)
    return tower_tier_description(tower.tower_type, next_level, tower.selected_branch)


def get_scaled_sprite(sprite, size):
    if sprite is None:
        return None
    key = (id(sprite), size)
    scaled = scaled_sprite_cache.get(key)
    if scaled is None:
        scaled = pygame.transform.smoothscale(sprite, size)
        scaled_sprite_cache[key] = scaled
    return scaled


def draw_glow(x, y, color, radius=18, alpha=50):
    if not render_options.enable_glow:
        return
    key = (tuple(color), int(radius), int(alpha))
    glow = glow_cache.get(key)
    if glow is None:
        size = int(radius * 2)
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        for step in range(4, 0, -1):
            step_radius = int(radius * step / 4)
            step_alpha = int(alpha * (step / 4) ** 2)
            pygame.draw.circle(glow, (*color[:3], step_alpha), (size // 2, size // 2), step_radius)
        glow_cache[key] = glow
    screen.blit(glow, (int(x - radius), int(y - radius)), special_flags=pygame.BLEND_ADD)


def emit_particles(x, y, color, count=6, speed=70, size=4, lifetime=0.45, alpha=1.0):
    if render_options.enable_particles and particle_manager is not None:
        particle_manager.emit(x, y, color, count, speed, size, lifetime, alpha=alpha)


def emit_shot_particles(x, y, color, count=1, speed=28, size=2, lifetime=0.14, chance=0.65):
    if not render_options.enable_particles or particle_manager is None:
        return
    if len(enemies) >= BUSY_ENEMY_COUNT:
        chance *= 0.55
    if random.random() > chance:
        return
    particle_manager.emit(x, y, color, max(1, count), speed, size, lifetime, alpha=0.58)


def _round_state_number(value):
    if isinstance(value, (int, float)):
        return round(float(value), 3)
    return value


def _position_state(obj):
    return [_round_state_number(getattr(obj, "x", 0)), _round_state_number(getattr(obj, "y", 0))]


def _compact_tower_state(tower):
    if tower is None:
        return None
    return {
        "type": getattr(tower, "tower_type", None),
        "branch": getattr(tower, "selected_branch", None),
        "level": getattr(tower, "level", None),
        "pos": _position_state(tower),
        "range": _round_state_number(getattr(tower, "range", 0)),
        "fire_rate": _round_state_number(getattr(tower, "fire_rate", 0)),
        "cooldown": _round_state_number(getattr(tower, "cooldown", 0)),
        "kills": getattr(tower, "kills", None),
        "shots_fired": getattr(tower, "shots_fired", None),
        "locked_timer": _round_state_number(getattr(tower, "locked_timer", 0)),
        "mutations": list(getattr(tower, "mutations", [])),
    }


def _compact_enemy_state(enemy):
    return {
        "kind": getattr(enemy, "kind", None),
        "affix": getattr(enemy, "affix", None),
        "boss": getattr(enemy, "boss", False),
        "commander": getattr(enemy, "commander", False),
        "flying": getattr(enemy, "flying", False),
        "split_child": getattr(enemy, "is_split_child", False),
        "pos": _position_state(enemy),
        "hp": _round_state_number(getattr(enemy, "hp", 0)),
        "max_hp": _round_state_number(getattr(enemy, "max_hp", 0)),
        "path_index": getattr(enemy, "path_index", None),
        "target_index": getattr(enemy, "target_index", None),
        "shield_hits": getattr(enemy, "shield_hits", None),
        "reached_end": getattr(enemy, "reached_end", False),
        "death_spawns": getattr(enemy, "death_spawns", 0),
    }


def _compact_projectile_state(projectile):
    return {
        "tower_type": getattr(projectile, "tower_type", None),
        "tower_level": getattr(projectile, "tower_level", None),
        "pos": _position_state(projectile),
        "target_kind": getattr(getattr(projectile, "target", None), "kind", None),
        "dead": getattr(projectile, "dead", False),
    }


def collect_crash_state():
    enemy_kinds = {}
    for enemy in enemies:
        kind = getattr(enemy, "kind", "unknown")
        enemy_kinds[kind] = enemy_kinds.get(kind, 0) + 1

    try:
        enemies_per_wave = get_enemies_per_wave()
    except Exception:
        enemies_per_wave = None

    try:
        spawn_interval = get_spawn_interval()
    except Exception:
        spawn_interval = None

    try:
        paths = current_paths()
        path_count = len(paths)
    except Exception:
        path_count = None

    particles = getattr(particle_manager, "particles", [])
    return {
        "wave": wave,
        "wave_active": wave_active,
        "spawned_this_wave": spawned_this_wave,
        "enemies_per_wave": enemies_per_wave,
        "spawn_timer": _round_state_number(spawn_timer),
        "spawn_interval": _round_state_number(spawn_interval),
        "money": money,
        "lives": lives,
        "score": score,
        "research_points": research_points,
        "game_over": game_over,
        "victory": victory,
        "paused": paused,
        "game_speed": game_speed,
        "pending_card_choices": list(pending_card_choices),
        "selected_build_type": selected_build_type,
        "selected_tower": _compact_tower_state(selected_tower),
        "counts": {
            "enemies": len(enemies),
            "towers": len(towers),
            "projectiles": len(projectiles),
            "effects": len(effects),
            "particles": len(particles),
        },
        "enemy_kinds": enemy_kinds,
        "map": {
            "name": active_map.get("name"),
            "seed": active_map.get("seed"),
            "theme": current_theme(),
            "path_count": path_count,
            "spawn_path_index": spawn_path_index,
        },
        "render_options": {
            "renderer": getattr(render_options, "renderer", None),
            "enable_glow": getattr(render_options, "enable_glow", None),
            "enable_particles": getattr(render_options, "enable_particles", None),
            "enable_screen_shake": getattr(render_options, "enable_screen_shake", None),
            "max_particles": getattr(render_options, "max_particles", None),
        },
        "window": {
            "window_width": window_width,
            "window_height": window_height,
            "scale": _round_state_number(scale),
            "offset_x": offset_x,
            "offset_y": offset_y,
        },
        "towers": [_compact_tower_state(tower) for tower in towers[:16]],
        "enemies": [_compact_enemy_state(enemy) for enemy in enemies[:24]],
        "projectiles": [_compact_projectile_state(projectile) for projectile in projectiles[:16]],
    }


def write_current_crash_log(exc):
    try:
        state = collect_crash_state()
    except Exception as state_exc:
        state = {"crash_state_error": repr(state_exc)}
    return write_crash_log(exc, state)


def init_images():
    global images

    tower_images = {}
    for tower_type in TOWER_TYPES:
        tower_images[tower_type] = {
            "idle": load_image(f"sprites/towers/{tower_type}_idle.png"),
            "fire": load_image(f"sprites/towers/{tower_type}_fire.png"),
            "idle_1": load_image(f"sprites/towers/{tower_type}_idle_1.png"),
            "idle_2": load_image(f"sprites/towers/{tower_type}_idle_2.png"),
            "fire_1": load_image(f"sprites/towers/{tower_type}_fire_1.png"),
            "fire_2": load_image(f"sprites/towers/{tower_type}_fire_2.png"),
        }

    enemy_images = {}
    for enemy_type in ("normal", "fast", "tank", "swarm", "shield", "armored", "flying", "boss", "split_child", "shield_cracked"):
        enemy_images[enemy_type] = {
            "base": load_image(f"sprites/enemies/{enemy_type}.png"),
            "walk_1": load_image(f"sprites/enemies/{enemy_type}_walk_1.png"),
            "walk_2": load_image(f"sprites/enemies/{enemy_type}_walk_2.png"),
            "hit": load_image(f"sprites/enemies/{enemy_type}_hit.png"),
            "rage": load_image(f"sprites/enemies/{enemy_type}_rage.png"),
        }

    terrain_images = {
        "grass": load_image("sprites/terrain/grass.png"),
        "grass_dark": load_image("sprites/terrain/grass_dark.png"),
        "road": load_image("sprites/terrain/road.png"),
        "road_edge": load_image("sprites/terrain/road_edge.png"),
        "spawn": load_image("sprites/terrain/spawn_gate.png"),
        "base": load_image("sprites/terrain/base_gate.png"),
    }
    for theme in ("forest", "swamp", "snow", "lava"):
        for name in ("grass", "grass_dark", "road", "road_edge"):
            terrain_images[f"{theme}_{name}"] = load_image(f"sprites/terrain/{theme}_{name}.png")

    images = {
        "towers": tower_images,
        "enemies": enemy_images,
        "terrain": terrain_images,
        "projectiles": {
            "archer": load_image("sprites/projectiles/archer.png"),
            "sniper": load_image("sprites/projectiles/sniper.png"),
            "machine_gun": load_image("sprites/projectiles/machine_gun.png"),
            "cannon": load_image("sprites/projectiles/cannon.png"),
            "frost": load_image("sprites/projectiles/frost.png"),
            "tesla": load_image("sprites/projectiles/tesla.png"),
            "poison": load_image("sprites/projectiles/poison.png"),
            "flame": load_image("sprites/projectiles/flame.png"),
            "mortar": load_image("sprites/projectiles/mortar.png"),
            "gold": load_image("sprites/projectiles/gold.png"),
        },
        "effects": {
            "explosion": load_image("sprites/effects/explosion.png"),
            "frost_burst": load_image("sprites/effects/frost_burst.png"),
            "spark": load_image("sprites/effects/spark.png"),
            "shield_break": load_image("sprites/effects/shield_break.png"),
            "smoke": load_image("sprites/effects/smoke.png"),
            "explosion_ring": load_image("sprites/effects/explosion_ring.png"),
            "frost_mist": load_image("sprites/effects/frost_mist.png"),
            "lightning_spark": load_image("sprites/effects/lightning_spark.png"),
            "poison_cloud": load_image("sprites/effects/poison_cloud.png"),
            "flame_burst": load_image("sprites/effects/flame_burst.png"),
            "coin_sparkle": load_image("sprites/effects/coin_sparkle.png"),
        },
    }


def init_sounds():
    global sound_enabled, sounds, music_loaded

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=256)
        sounds = {
            "build": load_game_sound("sounds/ui/build.wav") or make_tone(360, 0.08, 0.22),
            "upgrade": load_game_sound("sounds/ui/upgrade.wav") or make_tone(620, 0.10, 0.22),
            "sell": load_game_sound("sounds/ui/sell.wav") or make_tone(260, 0.10, 0.18),
            "wave": load_game_sound("sounds/ui/wave.wav") or make_tone(480, 0.13, 0.20),
            "wave_fast": load_game_sound("sounds/ui/wave_fast.wav") or make_tone(920, 0.10, 0.18),
            "wave_tank": load_game_sound("sounds/ui/wave_tank.wav") or make_tone(110, 0.14, 0.18),
            "wave_shield": load_game_sound("sounds/ui/wave_shield.wav") or make_tone(360, 0.12, 0.18),
            "wave_flying": load_game_sound("sounds/ui/wave_flying.wav") or make_tone(1040, 0.14, 0.16),
            "wave_boss": load_game_sound("sounds/ui/wave_boss.wav") or make_tone(90, 0.18, 0.20),
            "wave_complete": load_game_sound("sounds/ui/wave_complete.wav") or make_tone(680, 0.10, 0.18),
            "death": load_game_sound("sounds/enemies/death.wav") or make_tone(150, 0.08, 0.16),
            "leak": load_game_sound("sounds/enemies/leak.wav") or make_tone(130, 0.12, 0.16),
            "boss_spawn": load_game_sound("sounds/enemies/boss_spawn.wav") or make_tone(95, 0.16, 0.18),
            "boss_death": load_game_sound("sounds/enemies/boss_death.wav") or make_tone(110, 0.16, 0.18),
            "archer": load_game_sound("sounds/towers/archer.wav") or make_tone(520, 0.035, 0.10),
            "sniper": load_game_sound("sounds/towers/sniper.wav") or make_tone(880, 0.055, 0.16),
            "machine_gun": load_game_sound("sounds/towers/machine_gun.wav") or make_tone(700, 0.025, 0.07),
            "cannon": load_game_sound("sounds/towers/cannon.wav") or make_tone(120, 0.12, 0.20),
            "frost": load_game_sound("sounds/towers/frost.wav") or make_tone(760, 0.07, 0.12),
            "tesla": load_game_sound("sounds/towers/tesla.wav") or make_tone(1050, 0.04, 0.11),
            "poison": load_game_sound("sounds/towers/poison.wav") or make_tone(540, 0.055, 0.10),
            "flame": load_game_sound("sounds/towers/flame.wav") or make_tone(210, 0.07, 0.13),
            "mortar": load_game_sound("sounds/towers/mortar.wav") or make_tone(85, 0.12, 0.18),
            "gold": load_game_sound("sounds/towers/gold.wav") or make_tone(760, 0.06, 0.12),
            "freeze": load_game_sound("sounds/towers/freeze.wav") or make_tone(900, 0.08, 0.12),
            "chain": load_game_sound("sounds/towers/chain.wav") or make_tone(1100, 0.04, 0.10),
            "shield_break": load_game_sound("sounds/enemies/shield_break.wav") or make_tone(420, 0.07, 0.14),
        }
        music_path = ASSET_DIR / "sounds/music/loop.wav"
        if music_path.exists():
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
            music_loaded = True
        sound_enabled = True
    except pygame.error:
        sounds = {}
        sound_enabled = False
        music_loaded = False


def play_sound(name, cooldown=0.04):
    if not sound_enabled or not sfx_enabled or name not in sounds:
        return

    now = pygame.time.get_ticks()
    last = last_sound_times.get(name, -100000)
    if now - last < cooldown * 1000:
        return

    last_sound_times[name] = now
    try:
        sounds[name].play()
    except pygame.error:
        pass


def load_game_sound(relative_path):
    if is_web_runtime() and relative_path.endswith(".wav"):
        return load_sound_any(relative_path[:-4] + ".ogg", relative_path)
    return load_sound(relative_path)


def get_wave_stinger_key(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    if get_boss_count_for_wave(preview_wave):
        return "wave_boss"

    kind = get_wave_enemy_kind(preview_wave)
    affix = get_wave_affix(preview_wave)
    if kind == "fast" or affix == "haste":
        return "wave_fast"
    if kind == "tank":
        return "wave_tank"
    if kind in ("shield", "armored") or affix in ("shield", "armored"):
        return "wave_shield"
    if kind == "flying":
        return "wave_flying"
    return "wave"


def play_wave_start_sound():
    play_sound(get_wave_stinger_key(), 0.35)


def tower_sound_cooldown(tower_type):
    return {
        "machine_gun": 0.045,
        "tesla": 0.055,
        "poison": 0.10,
        "flame": 0.10,
        "gold": 0.10,
        "cannon": 0.12,
        "mortar": 0.14,
        "sniper": 0.10,
    }.get(tower_type, 0.08)


def update_music_state():
    global current_music_track

    if not sound_enabled or not music_loaded:
        return
    desired_track = "boss" if active_bosses() else "normal"
    music_path = ASSET_DIR / ("sounds/music/boss_loop.wav" if desired_track == "boss" else "sounds/music/loop.wav")
    if music_enabled:
        if current_music_track != desired_track and music_path.exists():
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.play(-1)
            current_music_track = desired_track
        elif not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.25)
    else:
        pygame.mixer.music.pause()


def trigger_screen_shake(duration=0.12, strength=4):
    global screen_shake_timer, screen_shake_strength

    if not render_options.enable_screen_shake:
        return

    screen_shake_timer = max(screen_shake_timer, duration)
    screen_shake_strength = max(screen_shake_strength, strength)


def get_game_mouse_pos():
    mx, my = pygame.mouse.get_pos()
    gx = (mx - offset_x) / scale
    gy = (my - offset_y) / scale
    return (int(gx), int(gy))


def mouse_in_game_area(pos=None):
    if pos is None:
        pos = pygame.mouse.get_pos()

    mx, my = pos
    return offset_x <= mx <= offset_x + WIDTH * scale and offset_y <= my <= offset_y + HEIGHT * scale


def update_window_transform():
    global scale, offset_x, offset_y

    scale = min(window_width / WIDTH, window_height / HEIGHT)
    offset_x = int((window_width - WIDTH * scale) // 2)
    offset_y = int((window_height - HEIGHT * scale) // 2)


def near_path(pos, clearance=45):
    for start, end in all_path_segments():
        if distance_to_segment(pos, start, end) < clearance:
            return True
    return False

def build_rect_for_site(site):
    half = BUILD_TILE_SIZE // 2
    return pygame.Rect(site[0] - half, site[1] - half, BUILD_TILE_SIZE, BUILD_TILE_SIZE)


def build_rect_overlaps_path(site):
    rect = build_rect_for_site(site)
    blocked_distance = PATH_WIDTH / 2 + BUILD_PATH_PADDING

    for start, end in all_path_segments():
        if distance_segment_to_rect(start, end, rect) < blocked_distance:
            return True

    return False


def get_build_site_at(pos):
    px, py = pos
    half = BUILD_TILE_SIZE // 2

    if py < BUILD_GRID_TOP:
        return None

    col = round((px - half) / BUILD_GRID_STEP)
    row = round((py - BUILD_GRID_TOP - half) / BUILD_GRID_STEP)
    sx = int(col * BUILD_GRID_STEP + half)
    sy = int(BUILD_GRID_TOP + row * BUILD_GRID_STEP + half)

    if sx - half < 0 or sx + half > MAP_WIDTH:
        return None
    if sy - half < BUILD_GRID_TOP or sy + half > HEIGHT:
        return None

    return (sx, sy)


def is_site_occupied(site):
    rect = build_rect_for_site(site)

    for tower in towers:
        tower_rect = build_rect_for_site((tower.x, tower.y))
        if rect.colliderect(tower_rect):
            return True
    return False


def get_tower_at(pos):
    for tower in towers:
        if dist(pos, (tower.x, tower.y)) < 24:
            return tower
    return None


def has_behavior_tag(enemy, tag):
    return tag in enemy.behavior_tags()


def apply_modifier_effects(enemy, modifier_key):
    if modifier_key is None:
        return enemy

    modifier = WAVE_MODIFIERS.get(modifier_key)
    if modifier is None:
        return enemy

    effects_data = modifier["effects"]
    if "regen_scale" in effects_data:
        enemy.regen_rate = max(3, enemy.max_hp * effects_data["regen_scale"])
    if "shield_hits" in effects_data:
        enemy.shield_hits += effects_data["shield_hits"]
    if "speed_multiplier" in effects_data:
        enemy.speed *= effects_data["speed_multiplier"]
    if "death_spawns" in effects_data:
        enemy.death_spawns += effects_data["death_spawns"]
    return enemy


class Enemy:
    def __init__(
        self,
        hp,
        speed,
        reward,
        kind="normal",
        shield_hits=0,
        flying=False,
        boss=False,
        commander=False,
        death_spawns=0,
        affix=None,
        path_index=0,
        is_split_child=False,
        boss_protocol=None,
    ):
        self.path_index = path_index % len(current_paths())
        self.path = current_paths()[self.path_index]
        self.x, self.y = self.path[0]
        self.target_index = 1
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.reward = reward
        self.kind = kind
        self.shield_hits = shield_hits
        self.flying = flying
        self.boss = boss
        self.commander = commander
        self.death_spawns = death_spawns
        self.affix = affix
        self.is_split_child = is_split_child
        self.boss_protocol = boss_protocol
        self.leak_damage = 5 if boss else 1
        self.radius = 10 if is_split_child else 26 if boss else 18 if commander else 15
        self.reached_end = False
        self.burn_timer = 0
        self.burn_dps = 0
        self.burn_source_tower = None
        self.poison_timer = 0
        self.poison_dps = 0
        self.poison_source_tower = None
        self.slow_timer = 0
        self.slow_multiplier = 1
        self.freeze_timer = 0
        self.vulnerable_timer = 0
        self.damage_multiplier = 1
        self.regen_rate = 0
        self.hit_flash_timer = 0
        self.shield_break_timer = 0
        self.marked_timer = 0
        self.barracks_hold_timer = 0
        self.commander_aura_timer = 0
        self.last_damaging_tower = None
        self.trail_points = []
        self.trail_sample_timer = 0
        self.ransomware_lock_timer = 1.2 if boss_protocol == "ransomware" else 0
        apply_modifier_effects(self, affix)

    def behavior_tags(self):
        tags = set()
        if self.kind == "fast" or self.affix == "haste":
            tags.add("fast")
        if self.kind in ("shield", "armored") or self.affix == "armored" or self.shield_hits > 0:
            tags.add("armored")
        if self.kind == "swarm" or self.is_split_child or self.affix == "split":
            tags.add("swarm")
        if self.flying:
            tags.add("flying")
        if self.boss:
            tags.add("boss")
        if self.commander:
            tags.add("commander")
        return tags

    def take_damage(self, amount, damage_type=None, source_tower=None):
        self.hit_flash_timer = 0.12
        tags = self.behavior_tags()
        effective_damage_type = damage_type

        if self.commander_aura_timer > 0 and not self.commander:
            amount *= 0.86

        if source_tower is not None:
            self.last_damaging_tower = source_tower
            if source_tower.has_mutation("fast_hunter") and "fast" in tags:
                amount *= 1.25
                self.slow_timer = max(self.slow_timer, 0.45)
                self.slow_multiplier = min(self.slow_multiplier, 0.74)
            if source_tower.has_mutation("armor_piercer") and "armored" in tags:
                amount *= 1.25
                effective_damage_type = "pierce"
            if source_tower.has_mutation("swarm_reaper") and "swarm" in tags:
                amount *= 1.22
            if source_tower.has_mutation("sky_watcher") and "flying" in tags:
                amount *= 1.30
            if source_tower.has_mutation("corrupted") and self.hp <= self.max_hp * 0.40:
                amount *= 1.32

        if effective_damage_type == "electric":
            if self.boss:
                amount *= 0.55
            elif self.kind in ("armored", "shield") or self.shield_hits > 0:
                amount *= 0.65

        shield_before = self.shield_hits
        if self.shield_hits > 0:
            amount *= 0.75 if effective_damage_type == "pierce" else 0.35
            self.shield_hits -= 1
            self.shield_break_timer = 0.22
            add_effect(SparkEffect(self.x, self.y, (220, 230, 255), self.radius + 8, 0.18))
            emit_particles(self.x, self.y, (220, 230, 255), 5, 55, 3, 0.28)
            add_floating_text(self.x - 12, self.y - 42, "SHIELD", (220, 230, 255))
            play_sound("shield_break", 0.08)

        if self.affix == "armored":
            amount *= 0.95 if effective_damage_type == "pierce" else 0.8

        dealt = amount * self.damage_multiplier
        self.hp -= dealt
        if source_tower is not None:
            source_tower.record_hit(self, dealt, shield_before > self.shield_hits)
        return dealt

    def progress(self):
        if self.flying:
            return dist(self.path[0], (self.x, self.y))

        total = 0
        for i in range(1, min(self.target_index, len(self.path))):
            total += dist(self.path[i - 1], self.path[i])

        if 0 < self.target_index < len(self.path):
            total += dist(self.path[self.target_index - 1], (self.x, self.y))

        return total

    def update(self, dt):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        if self.shield_break_timer > 0:
            self.shield_break_timer -= dt
        if self.marked_timer > 0:
            self.marked_timer -= dt
        if self.barracks_hold_timer > 0:
            self.barracks_hold_timer -= dt
        if self.commander_aura_timer > 0:
            self.commander_aura_timer -= dt
        self.update_packet_trail(dt)
        self.update_boss_protocol(dt)

        if self.vulnerable_timer > 0:
            self.vulnerable_timer -= dt
        else:
            self.damage_multiplier = 1

        if self.regen_rate > 0 and self.hp > 0:
            self.hp = min(self.max_hp, self.hp + self.regen_rate * dt)

        if self.burn_timer > 0:
            dealt = self.take_damage(self.burn_dps * dt, "fire", self.burn_source_tower)
            if self.burn_source_tower in towers:
                self.burn_source_tower.total_damage += dealt
                self.burn_source_tower.mastery_xp += dealt * 0.01
            self.burn_timer -= dt

        if self.poison_timer > 0:
            dealt = self.take_damage(self.poison_dps * dt, "poison", self.poison_source_tower)
            if self.poison_source_tower in towers:
                self.poison_source_tower.total_damage += dealt
                self.poison_source_tower.mastery_xp += dealt * 0.01
            self.poison_timer -= dt

        if self.target_index >= len(self.path):
            self.reached_end = True
            return

        if self.flying:
            tx, ty = self.path[-1]
        else:
            tx, ty = self.path[self.target_index]

        dx = tx - self.x
        dy = ty - self.y
        distance = math.hypot(dx, dy)

        if distance < 2:
            if self.flying:
                self.reached_end = True
            else:
                self.target_index += 1
            return

        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            return

        current_speed = self.speed
        if self.commander_aura_timer > 0 and not self.commander:
            current_speed *= 1.14
        if self.slow_timer > 0:
            current_speed *= self.slow_multiplier
            self.slow_timer -= dt
        else:
            self.slow_multiplier = 1

        self.x += (dx / distance) * current_speed * dt
        self.y += (dy / distance) * current_speed * dt

    def update_boss_protocol(self, dt):
        if self.boss_protocol != "ransomware" or self.hp <= 0:
            return

        self.ransomware_lock_timer -= dt
        if self.ransomware_lock_timer > 0:
            return

        locked = self.trigger_ransomware_lock()
        self.ransomware_lock_timer = RANSOMWARE_LOCK_INTERVAL if locked else 1.2

    def trigger_ransomware_lock(self):
        candidates = [
            tower for tower in towers
            if tower.locked_timer <= 0
            and dist((self.x, self.y), (tower.x, tower.y)) <= RANSOMWARE_LOCK_RADIUS
        ]
        if not candidates:
            return False

        target = max(candidates, key=lambda tower: (tower.level, -dist((self.x, self.y), (tower.x, tower.y))))
        target.locked_timer = RANSOMWARE_LOCK_DURATION
        target.cooldown = max(target.cooldown, min(RANSOMWARE_LOCK_DURATION, 0.8))
        add_effect(LightningEffect((self.x, self.y), (target.x, target.y), (255, 90, 120), 0.16))
        add_effect(SparkEffect(target.x, target.y, (255, 90, 120), 26, 0.28, "shield_break"))
        emit_particles(target.x, target.y, (255, 90, 120), 10, 75, 4, 0.35)
        add_floating_text(target.x - 24, target.y - 48, "LOCKED", (255, 120, 145))
        return True

    def update_packet_trail(self, dt):
        self.trail_points = [
            (x, y, age + dt)
            for x, y, age in self.trail_points
            if age + dt < PACKET_TRAIL_LIFETIME
        ]

        if len(enemies) >= VERY_BUSY_ENEMY_COUNT:
            return

        self.trail_sample_timer -= dt
        if self.trail_sample_timer > 0:
            return

        self.trail_sample_timer = 0.045 if self.kind == "fast" or self.affix == "haste" else 0.065
        self.trail_points.append((self.x, self.y, 0))
        if len(self.trail_points) > PACKET_TRAIL_LIMIT:
            self.trail_points = self.trail_points[-PACKET_TRAIL_LIMIT:]

    def draw_packet_trail(self, color):
        if not self.trail_points or len(enemies) >= VERY_BUSY_ENEMY_COUNT:
            return

        for index, (x, y, age) in enumerate(self.trail_points):
            fade = max(0, 1 - age / PACKET_TRAIL_LIFETIME)
            fade *= (index + 1) / max(1, len(self.trail_points))
            if fade <= 0:
                continue
            radius = max(2, int(self.radius * (0.22 + 0.26 * fade)))
            trail_color = blend_color(color, (8, 13, 12), 0.38)
            draw_glow(x, y, color, radius + 5, int(26 * fade))
            pygame.draw.circle(screen, trail_color, (int(x), int(y)), radius)

    def draw_scan_brackets(self):
        pulse = (math.sin(pygame.time.get_ticks() * 0.012) + 1) * 0.5
        radius = self.radius + 10 + int(pulse * 3)
        color = (120, 235, 255)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius, 1)
        for sx in (-1, 1):
            x = int(self.x + sx * radius)
            pygame.draw.line(screen, color, (x, int(self.y - 7)), (x, int(self.y + 7)), 2)
        for sy in (-1, 1):
            y = int(self.y + sy * radius)
            pygame.draw.line(screen, color, (int(self.x - 7), y), (int(self.x + 7), y), 2)

    def draw(self):
        color = (210, 60, 60)
        if self.kind == "fast":
            color = (235, 95, 190)
        elif self.kind == "tank":
            color = (160, 80, 55)
        elif self.kind == "swarm":
            color = (230, 120, 70)
        elif self.kind == "shield":
            color = (170, 170, 190)
        elif self.kind == "armored":
            color = (130, 130, 145)
        elif self.commander:
            color = (245, 210, 90)
        elif self.flying:
            color = (185, 120, 245)
        elif self.boss:
            color = (170, 55, 55)

        if self.vulnerable_timer > 0:
            color = (165, 120, 70)
        if self.slow_timer > 0:
            color = (80, 150, 240)
        if self.freeze_timer > 0:
            color = (180, 235, 255)
        if self.burn_timer > 0:
            color = (240, 95, 45)
        if self.poison_timer > 0:
            color = (110, 220, 80)

        signal_color = packet_status_color(self)
        self.draw_packet_trail(signal_color)
        pygame.draw.ellipse(screen, (0, 0, 0, 85), (int(self.x - self.radius), int(self.y + self.radius * 0.58), self.radius * 2, max(4, self.radius // 2)))
        sprite_key = "boss" if self.boss else "shield" if self.commander else "split_child" if self.is_split_child else "flying" if self.flying else "shield_cracked" if self.kind == "shield" and self.shield_hits <= 0 else self.kind
        frames = images.get("enemies", {}).get(sprite_key, {})
        if self.hit_flash_timer > 0:
            sprite = frames.get("hit") or frames.get("base")
        elif self.boss and self.hp < self.max_hp * 0.35:
            sprite = frames.get("rage") or frames.get("base")
        else:
            sprite = get_animation_frame([frames.get("walk_1"), frames.get("walk_2")]) or frames.get("base")
        if sprite is None:
            sprite = images.get("enemies", {}).get("normal", {}).get("base")
        drew_sprite = draw_sprite_centered(screen, sprite, self.x, self.y)
        if self.hit_flash_timer > 0:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius + 2, 2)
        if self.shield_break_timer > 0:
            effect_sprite = images.get("effects", {}).get("shield_break")
            if effect_sprite:
                draw_sprite_centered(screen, effect_sprite, self.x, self.y)
            else:
                pygame.draw.circle(screen, (220, 230, 255), (int(self.x), int(self.y)), self.radius + 8, 2)
        if not drew_sprite:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        crowded = len(enemies) >= VERY_BUSY_ENEMY_COUNT
        if self.shield_hits > 0 and not crowded:
            pygame.draw.circle(screen, (225, 225, 245), (int(self.x), int(self.y)), self.radius + 5, 2)
        if self.flying and not crowded:
            pygame.draw.circle(screen, (235, 225, 255), (int(self.x), int(self.y)), self.radius + 4, 1)
        if self.affix and not crowded:
            affix_color = WAVE_MODIFIERS.get(self.affix, {}).get("color", (255, 255, 140))
            pygame.draw.circle(screen, affix_color, (int(self.x), int(self.y)), self.radius + 8, 1)
        if self.marked_timer > 0 and not crowded:
            self.draw_scan_brackets()
        if self.commander and not crowded:
            pygame.draw.circle(screen, (120, 105, 45), (int(self.x), int(self.y)), COMMANDER_AURA_RADIUS, 1)
            pygame.draw.circle(screen, (245, 220, 90), (int(self.x), int(self.y)), self.radius + 10, 3)
            draw_tiny_text("CMD", int(self.x - 15), int(self.y - self.radius - 30), (255, 235, 130))
        elif self.commander_aura_timer > 0 and not crowded:
            pygame.draw.circle(screen, (245, 220, 90), (int(self.x), int(self.y)), self.radius + 7, 1)

        show_health_bar = (
            self.boss
            or self.commander
            or len(enemies) < CROWD_HEALTH_BAR_LIMIT
            or self.hit_flash_timer > 0
            or self.hp < self.max_hp * 0.55
        )
        if show_health_bar:
            bar_w = 48 if self.boss else 34
            hp_ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(screen, (40, 40, 40), (self.x - bar_w / 2, self.y - self.radius - 13, bar_w, 5))
            pygame.draw.rect(screen, (60, 220, 80), (self.x - bar_w / 2, self.y - self.radius - 13, bar_w * hp_ratio, 5))


class Tower:
    def __init__(self, x, y, tower_type=None, money_spent=TOWER_COST):
        self.x = x
        self.y = y
        self.level = 1
        self.tower_type = None
        self.selected_branch = None
        self.range = BASE_TOWER_RANGE
        self.fire_rate = 0.55
        self.cooldown = 0
        self.damage = 25
        self.is_paragon = False
        self.money_spent = TOWER_COST
        self.target_mode = "first"
        self.kills = 0
        self.total_damage = 0
        self.mastery_xp = 0
        self.fire_anim_timer = 0
        self.locked_timer = 0
        self.mutations = []
        self.available_mutations = []
        self.notified_mutations = set()
        self.shots_fired = 0
        self.waves_present = 0
        self.behavior_hits = {"fast": 0, "armored": 0, "swarm": 0, "flying": 0}
        self.behavior_damage = {"fast": 0, "armored": 0, "swarm": 0, "flying": 0}
        self.behavior_kills = {"fast": 0, "armored": 0, "swarm": 0, "flying": 0}
        self.shield_breaks = 0
        self.nearby_deaths = 0
        self.flying_seen_timer = 0
        self.corruption_burst_cooldown = 0
        self.gold_income_timer = 0
        self.gold_income_wave = wave
        self.gold_income_earned = 0
        self.support_mana = 0.0
        self.support_max_mana = 100.0
        self.support_cast_cooldown = 0.0
        self.support_buff_timer = 0.0
        self.support_damage_bonus = 0.0
        self.support_rate_bonus = 0.0
        self.support_range_bonus = 0.0
        self.support_casts = 0
        self.spin_heat = 0.0
        self.overclock_pulse_timer = 0.0
        if tower_type:
            self.tower_type, self.selected_branch = normalize_tower_type(tower_type)
            self.level = 2
            self.money_spent = money_spent
            self.apply_weapon_level_stats()

    def cycle_target_mode(self):
        index = TARGET_MODES.index(self.target_mode)
        self.target_mode = TARGET_MODES[(index + 1) % len(TARGET_MODES)]

    def has_mutation(self, mutation_key):
        return mutation_key in self.mutations

    def can_add_mutation(self):
        return len(self.mutations) < MUTATION_SLOT_LIMIT

    def apply_mutation(self, mutation_key):
        if mutation_key not in self.available_mutations or not self.can_add_mutation():
            return False

        self.available_mutations.remove(mutation_key)
        self.mutations.append(mutation_key)
        data = MUTATION_TRAITS[mutation_key]
        add_floating_text(self.x - 34, self.y - 48, data["label"], data["color"])
        return True

    def record_hit(self, enemy, dealt, broke_shield=False):
        for tag in enemy.behavior_tags():
            if tag in self.behavior_hits:
                self.behavior_hits[tag] += 1
                self.behavior_damage[tag] += dealt
        if broke_shield:
            self.shield_breaks += 1

    def record_kill(self, enemy):
        self.kills += 1
        self.mastery_xp += 1
        for tag in enemy.behavior_tags():
            if tag in self.behavior_kills:
                self.behavior_kills[tag] += 1

    def update_mutation_timers(self, dt):
        if self.corruption_burst_cooldown > 0:
            self.corruption_burst_cooldown = max(0, self.corruption_burst_cooldown - dt)

        if self.tower_type in ("support", "barracks"):
            return

        for enemy in enemies:
            if enemy.flying and dist((self.x, self.y), (enemy.x, enemy.y)) <= self.effective_range():
                self.flying_seen_timer += dt
                break

    @property
    def upgrade_cost(self):
        if self.level < BASE_MAX_TOWER_LEVEL:
            return TOWER_UPGRADE_COSTS.get(self.level)
        if self.level < MAX_TOWER_LEVEL:
            return MASTERY_UPGRADE_COSTS.get(self.level)
        return None

    def can_upgrade(self):
        if self.level >= MAX_TOWER_LEVEL:
            return False
        if self.needs_branch_choice():
            return False
        if self.level < BASE_MAX_TOWER_LEVEL:
            return True
        return (
            research_points >= RESEARCH_UPGRADE_COSTS[self.level]
            and len(towers) >= get_min_towers_for_upgrade(self.level)
        )

    def needs_branch_choice(self):
        return (
            self.tower_type in ROOT_TOWER_IDS
            and self.level == BRANCH_UNLOCK_LEVEL - 1
            and self.selected_branch is None
        )

    def branch_data(self):
        return branch_data(self.tower_type, self.selected_branch)

    def branch_has(self, mechanic):
        branch = self.branch_data()
        return branch is not None and mechanic in branch["mechanics"]

    def choose_branch(self, branch_key):
        if not self.needs_branch_choice():
            return False
        if branch_key not in BRANCH_DEFINITIONS.get(self.tower_type, {}):
            return False

        cost = self.upgrade_cost
        self.selected_branch = branch_key
        self.level = BRANCH_UNLOCK_LEVEL
        self.money_spent += cost
        self.apply_weapon_level_stats()
        branch = self.branch_data()
        if branch:
            add_floating_text(self.x - 38, self.y - 50, branch["name"], branch["color"])
        return True

    def apply_weapon_level_stats(self):
        if self.tower_type == "archer":
            self.damage += 14 + (self.level - 2) * 5
            self.range += 18
            self.fire_rate = max(0.25, self.fire_rate - 0.05)
        elif self.tower_type == "sniper":
            if self.level == 2:
                self.damage = 95
                self.range = 330
                self.fire_rate = 1.25
            else:
                self.damage += 55 + (self.level - 3) * 22
                self.range += 35
                self.fire_rate = max(0.85, self.fire_rate - 0.08)
        elif self.tower_type == "machine_gun":
            if self.level == 2:
                self.damage = 9
                self.range = 135
                self.fire_rate = 0.12
            else:
                self.damage += 4 + (self.level - 3) * 2
                self.range += 10
                self.fire_rate = max(0.04, self.fire_rate - 0.025)
        elif self.tower_type == "cannon":
            if self.level == 2:
                self.damage = 58
                self.range = 165
                self.fire_rate = 1.05
            else:
                self.damage += 32 + (self.level - 3) * 14
                self.range += 18
                self.fire_rate = max(0.78, self.fire_rate - 0.06)
        elif self.tower_type == "frost":
            self.damage += 7 + (self.level - 2) * 3
            self.range += 22
            self.fire_rate = max(0.28, self.fire_rate - 0.05)
        elif self.tower_type == "tesla":
            self.damage += 7 + (self.level - 2) * 2
            self.range += 12
            self.fire_rate = max(0.07, self.fire_rate - 0.13)
        elif self.tower_type == "poison":
            if self.level == 2:
                self.damage = 16
                self.range = 165
                self.fire_rate = 0.68
            else:
                self.damage += 6 + (self.level - 3) * 3
                self.range += 16
                self.fire_rate = max(0.34, self.fire_rate - 0.07)
        elif self.tower_type == "barracks":
            self.damage += 8 + (self.level - 2) * 4
            self.range += 16
            self.fire_rate = 0.25
        elif self.tower_type == "flame":
            if self.level == 2:
                self.damage = 28
                self.range = 118
                self.fire_rate = 0.55
            else:
                self.damage += 12 + (self.level - 3) * 6
                self.range += 8
                self.fire_rate = max(0.28, self.fire_rate - 0.055)
        elif self.tower_type == "mortar":
            if self.level == 2:
                self.damage = 72
                self.range = 360
                self.fire_rate = 1.45
            else:
                self.damage += 45 + (self.level - 3) * 18
                self.range += 25
                self.fire_rate = max(1.05, self.fire_rate - 0.08)
        elif self.tower_type == "support":
            self.damage = 0
            self.range += 35
            self.fire_rate = 0.5
        elif self.tower_type == "gold":
            if self.level == 2:
                self.damage = 10
                self.range = 145
                self.fire_rate = 0.78
            else:
                self.damage += 4 + (self.level - 3) * 2
                self.range += 12
                self.fire_rate = max(0.42, self.fire_rate - 0.055)
        self.apply_branch_level_stats()

    def apply_branch_level_stats(self):
        if self.selected_branch is None or self.level < BRANCH_UNLOCK_LEVEL:
            return

        branch = self.branch_data()
        focus = branch.get("focus") if branch else None
        tags = set(branch.get("tags", ())) if branch else set()

        if self.branch_has("mortar"):
            self.range += 45
            self.fire_rate += 0.12
        if self.branch_has("splash") or self.branch_has("cluster"):
            self.damage *= 1.08
        if self.branch_has("armor_break") or self.branch_has("pierce"):
            self.damage *= 1.10
        if self.branch_has("slow") or self.branch_has("freeze"):
            self.range += 10
        if self.branch_has("chain"):
            self.range += 12
        if self.branch_has("overclock") or self.branch_has("aura"):
            self.range += 18
        if self.branch_has("research") or self.branch_has("bounty"):
            self.range += 12
        if self.branch_has("spin_up"):
            self.fire_rate = max(0.035, self.fire_rate - 0.015)
        if self.branch_has("hazard") or self.branch_has("trap"):
            self.range += 10
        if focus == "damage":
            self.damage *= 1.04
        elif focus == "control":
            self.range += 7
            self.fire_rate = max(0.035, self.fire_rate - 0.006)
        elif focus == "utility":
            self.range += 6
        elif focus == "weird":
            self.damage *= 1.025
            self.range += 3
        if "boss" in tags and self.level >= 4:
            self.damage *= 1.035
        if "swarm" in tags or "splash" in tags:
            self.fire_rate = max(0.035, self.fire_rate - 0.004)

    def upgrade(self, tower_type):
        if not self.can_upgrade():
            return False

        cost = self.upgrade_cost

        if self.tower_type is None:
            self.tower_type, self.selected_branch = normalize_tower_type(tower_type)

        self.level += 1
        self.money_spent += cost
        if self.level == PARAGON_LEVEL:
            self.is_paragon = True

        if self.level == PARAGON_LEVEL:
            self.apply_paragon_stats()
            return True

        if self.level > PARAGON_LEVEL:
            self.apply_mastery_stats()
            return True

        self.apply_weapon_level_stats()

        return True

    def apply_paragon_stats(self):
        self.range += 90

        if self.tower_type == "archer":
            self.damage *= 2.0
            self.fire_rate = 0.16
        elif self.tower_type == "sniper":
            self.damage *= 2.7
            self.fire_rate = 0.65
        elif self.tower_type == "machine_gun":
            self.damage *= 1.8
            self.fire_rate = 0.025
        elif self.tower_type == "cannon":
            self.damage *= 2.5
            self.fire_rate = 0.6
        elif self.tower_type == "frost":
            self.damage *= 1.7
            self.fire_rate = 0.13
        elif self.tower_type == "tesla":
            self.damage *= 1.18
            self.fire_rate = 0.09
        elif self.tower_type == "poison":
            self.damage *= 1.75
            self.fire_rate = 0.18
        elif self.tower_type == "barracks":
            self.damage *= 2.2
            self.fire_rate = 0.12
        elif self.tower_type == "flame":
            self.damage *= 2.0
            self.fire_rate = 0.18
        elif self.tower_type == "mortar":
            self.damage *= 2.35
            self.fire_rate = 0.85
        elif self.tower_type == "support":
            self.damage = 0
            self.range = max(self.range, 420)
            self.fire_rate = 0.5
        elif self.tower_type == "gold":
            self.damage *= 1.7
            self.fire_rate = 0.35

    def apply_mastery_stats(self):
        self.range += 18

        if self.tower_type == "support":
            self.range += 35
            return

        if self.tower_type == "sniper":
            self.damage *= 1.35
            self.fire_rate = max(0.45, self.fire_rate - 0.04)
        elif self.tower_type == "machine_gun":
            self.damage *= 1.22
            self.fire_rate = max(0.018, self.fire_rate - 0.004)
        elif self.tower_type == "cannon":
            self.damage *= 1.32
            self.fire_rate = max(0.42, self.fire_rate - 0.04)
        elif self.tower_type == "frost":
            self.damage *= 1.20
            self.fire_rate = max(0.08, self.fire_rate - 0.015)
        elif self.tower_type == "tesla":
            self.damage *= 1.06
            self.fire_rate = max(0.075, self.fire_rate - 0.002)
        elif self.tower_type == "poison":
            self.damage *= 1.15
            self.fire_rate = max(0.14, self.fire_rate - 0.018)
        elif self.tower_type == "barracks":
            self.damage *= 1.28
            self.fire_rate = max(0.06, self.fire_rate - 0.01)
        elif self.tower_type == "flame":
            self.damage *= 1.18
            self.fire_rate = max(0.12, self.fire_rate - 0.018)
        elif self.tower_type == "mortar":
            self.damage *= 1.25
            self.fire_rate = max(0.65, self.fire_rate - 0.045)
        elif self.tower_type == "gold":
            self.damage *= 1.12
            self.fire_rate = max(0.22, self.fire_rate - 0.025)
        else:
            self.damage *= 1.25
            self.fire_rate = max(0.09, self.fire_rate - 0.025)

    def can_attack(self, enemy):
        if self.tower_type in ("support", "barracks"):
            return False
        if not enemy.flying:
            return True
        if self.has_mutation("sky_watcher"):
            return True
        return self.is_paragon or self.tower_type == "tesla" and self.level >= 4 or self.tower_type == "sniper" and self.level >= 3

    def minimum_range(self):
        if self.tower_type != "mortar":
            return 0
        return 115 if self.level < PARAGON_LEVEL else 95

    def update(self, dt):
        if self.locked_timer > 0:
            self.locked_timer = max(0, self.locked_timer - dt)

        if self.support_buff_timer > 0:
            self.support_buff_timer = max(0.0, self.support_buff_timer - dt)
            if self.support_buff_timer == 0:
                self.support_damage_bonus = 0.0
                self.support_rate_bonus = 0.0
                self.support_range_bonus = 0.0

        if self.support_cast_cooldown > 0:
            self.support_cast_cooldown = max(0.0, self.support_cast_cooldown - dt)

        self.update_mutation_timers(dt)
        self.spin_heat = max(0.0, self.spin_heat - dt * (0.10 if self.level >= 9 else 0.16))
        if self.branch_has("overclock"):
            self.update_battery_grid(dt)

        if self.fire_anim_timer > 0:
            self.fire_anim_timer -= dt

        if self.locked_timer > 0:
            return

        if self.tower_type == "gold":
            self.update_gold_income(dt)

        if self.tower_type == "support":
            self.update_support(dt)
            return

        if self.tower_type == "barracks":
            self.update_barracks(dt)
            return

        self.cooldown -= dt
        if self.cooldown > 0:
            return

        target = self.find_target()
        if target:
            if len(projectiles) < MAX_ACTIVE_PROJECTILES:
                projectiles.append(Projectile(self.x, self.y, target, self))
                self.shots_fired += 1
                if self.selected_branch == "vulcan":
                    self.spin_heat = min(1.0 + mastery_rank(self) * 0.08, self.spin_heat + 0.10 + branch_rank(self) * 0.018)
                data = TOWER_TYPES.get(self.tower_type, {})
                emit_shot_particles(self.x, self.y, data.get("projectile_color", (245, 220, 80)), 1, 26, 2, 0.11, 0.75)
                play_sound(self.tower_type, tower_sound_cooldown(self.tower_type))
            self.fire_anim_timer = 0.12
            self.cooldown = self.effective_fire_rate()

    def update_gold_income(self, dt):
        global money

        if self.gold_income_wave != wave:
            self.gold_income_wave = wave
            self.gold_income_earned = 0
            self.gold_income_timer = 0

        if not wave_active or not enemies:
            return

        cap = 8 + self.level * 3
        if self.is_paragon:
            cap += 12
        if self.gold_income_earned >= cap:
            return

        self.gold_income_timer -= dt
        if self.gold_income_timer > 0:
            return

        bonus = min(1 + self.level // 3, cap - self.gold_income_earned)
        money += bonus
        self.gold_income_earned += bonus
        self.mastery_xp += 0.2
        self.gold_income_timer = max(1.8, 4.2 - self.level * 0.28)
        add_floating_text(self.x - 12, self.y - 42, f"+${bonus}", TOWER_TYPES["gold"]["projectile_color"])

    def update_battery_grid(self, dt):
        if not wave_active:
            return

        allies = [
            tower for tower in towers
            if tower is not self
            and tower.tower_type not in (None, "support")
            and dist((self.x, self.y), (tower.x, tower.y)) <= self.effective_range()
        ]
        if not allies:
            return

        rank = branch_rank(self)
        mastery = mastery_rank(self)
        self.overclock_pulse_timer -= dt
        if self.overclock_pulse_timer > 0:
            return

        interval = max(1.4, 3.1 - rank * 0.16 - mastery * 0.10)
        duration = 2.4 + rank * 0.24 + mastery * 0.24
        rate_bonus = 0.06 + rank * 0.007 + mastery * 0.01
        damage_bonus = 0.0 if self.level < 9 else 0.04 + mastery * 0.006
        target_count = 1 + (1 if self.level >= 5 else 0) + (1 if self.level >= 8 else 0)

        allies.sort(key=lambda tower: (tower.support_buff_timer, dist((self.x, self.y), (tower.x, tower.y))))
        for ally in allies[:target_count]:
            ally.support_buff_timer = max(ally.support_buff_timer, duration)
            ally.support_rate_bonus = max(ally.support_rate_bonus, min(0.22, rate_bonus))
            ally.support_damage_bonus = max(ally.support_damage_bonus, min(0.14, damage_bonus))
            add_effect(SparkEffect(ally.x, ally.y, TOWER_TYPES["tesla"]["projectile_color"], 14, 0.20, "lightning_spark"))
            add_floating_text(ally.x - 22, ally.y - 44, "OVERCLOCK", TOWER_TYPES["tesla"]["projectile_color"])

        self.overclock_pulse_timer = interval
        self.mastery_xp += 0.4

    def update_barracks(self, dt):
        for enemy in enemies:
            if enemy.flying:
                continue
            if dist((self.x, self.y), (enemy.x, enemy.y)) <= self.effective_range():
                self.mastery_xp += dt * 0.35
                enemy.slow_timer = max(enemy.slow_timer, 0.3)
                enemy.barracks_hold_timer = max(enemy.barracks_hold_timer, 0.5)
                hold_multiplier = 0.58 if self.level < 5 else 0.42
                if self.branch_has("hold"):
                    hold_multiplier -= 0.08
                if self.branch_has("trap"):
                    hold_multiplier -= 0.05
                enemy.slow_multiplier = min(enemy.slow_multiplier, max(0.30, hold_multiplier))
                if self.level >= 4:
                    enemy.vulnerable_timer = max(enemy.vulnerable_timer, 0.5)
                    enemy.damage_multiplier = max(enemy.damage_multiplier, 1.12 if self.level < PARAGON_LEVEL else 1.25)
                if self.branch_has("mine") and self.level >= BRANCH_UNLOCK_LEVEL:
                    dealt = enemy.take_damage(self.effective_damage() * dt * 0.85, "explosive", self)
                    self.total_damage += dealt
                    self.mastery_xp += dealt * 0.02
                if self.level >= 5:
                    dealt = enemy.take_damage(self.effective_damage() * dt * 1.5, "melee", self)
                    self.total_damage += dealt
                    self.mastery_xp += dealt * 0.02

    def update_support(self, dt):
        if not wave_active or not enemies:
            return

        allies = self.support_allies()
        enemy_target = self.support_enemy_target()
        if not allies and enemy_target is None:
            return

        self.support_mana = min(self.support_max_mana, self.support_mana + self.support_mana_rate() * dt)
        if allies:
            self.mastery_xp += dt * min(1.2, len(allies) * 0.12)
        if self.support_cast_cooldown > 0 or self.support_mana < self.support_cast_cost():
            return

        buff_target = self.support_buff_target(allies)
        if buff_target is not None:
            self.cast_support_buff(buff_target)
        elif enemy_target is not None:
            self.cast_support_debuff(enemy_target)

    def support_cast_range(self):
        return self.range * (1 + run_range_bonus)

    def support_cast_cost(self):
        return 30.0 if self.branch_has("paint") or self.branch_has("threat_scan") else 35.0

    def support_mana_rate(self):
        rate = 10.0 + self.level * 2.0
        if self.branch_has("research"):
            rate += 3.0
        if self.is_paragon:
            rate += 5.0
        return rate

    def support_allies(self):
        support_range = self.support_cast_range()
        return [
            tower for tower in towers
            if tower is not self
            and tower.tower_type not in (None, "support")
            and (self.is_paragon or dist((self.x, self.y), (tower.x, tower.y)) <= support_range)
        ]

    def support_enemy_target(self):
        support_range = self.support_cast_range()
        valid = [
            enemy for enemy in enemies
            if self.is_paragon or dist((self.x, self.y), (enemy.x, enemy.y)) <= support_range
        ]
        if not valid:
            return None
        return max(valid, key=lambda enemy: (enemy.progress(), enemy.max_hp))

    def support_buff_target(self, allies):
        ready = [tower for tower in allies if tower.support_buff_timer <= 1.0]
        if not ready:
            return None
        return min(ready, key=lambda tower: (tower.support_buff_timer, dist((self.x, self.y), (tower.x, tower.y))))

    def cast_support_buff(self, target):
        cost = self.support_cast_cost()
        if self.support_mana < cost:
            return False

        duration = 4.2 + self.level * 0.28
        damage_bonus = 0.08 + self.level * 0.018
        rate_bonus = 0.06 + self.level * 0.014
        if self.branch_has("damage_buff"):
            damage_bonus += 0.04
        if self.branch_has("rate_buff"):
            rate_bonus += 0.04
        if self.branch_has("range_buff"):
            duration += 0.8
        if self.is_paragon:
            duration += 1.4
            damage_bonus += 0.06
            rate_bonus += 0.04

        target.support_buff_timer = max(target.support_buff_timer, duration)
        target.support_damage_bonus = max(target.support_damage_bonus, min(0.30, damage_bonus))
        target.support_rate_bonus = max(target.support_rate_bonus, min(0.24, rate_bonus))
        self.finish_support_cast(cost, 1.35)
        add_effect(SparkEffect(target.x, target.y, TOWER_TYPES["support"]["projectile_color"], 18, 0.28, "coin_sparkle"))
        add_floating_text(target.x - 16, target.y - 44, "BUFF", TOWER_TYPES["support"]["projectile_color"])
        play_sound("upgrade", 0.05)
        return True

    def cast_support_debuff(self, enemy):
        cost = self.support_cast_cost()
        if self.support_mana < cost:
            return False

        duration = 2.8 + self.level * 0.22
        enemy.marked_timer = max(enemy.marked_timer, duration)
        enemy.vulnerable_timer = max(enemy.vulnerable_timer, duration * 0.85)
        enemy.damage_multiplier = max(enemy.damage_multiplier, 1.08 + min(0.12, self.level * 0.012))
        if self.branch_has("paint") or self.branch_has("threat_scan") or self.level >= 4:
            enemy.slow_timer = max(enemy.slow_timer, duration * 0.6)
            enemy.slow_multiplier = min(enemy.slow_multiplier, 0.78 if self.level < PARAGON_LEVEL else 0.68)

        self.finish_support_cast(cost, 1.15)
        add_effect(SparkEffect(enemy.x, enemy.y, (180, 215, 245), enemy.radius + 10, 0.24, "lightning_spark"))
        add_floating_text(enemy.x - 18, enemy.y - 44, "HEX", (180, 215, 245))
        play_sound("chain", 0.04)
        return True

    def finish_support_cast(self, cost, cooldown):
        global research_points

        self.support_mana = max(0.0, self.support_mana - cost)
        self.support_cast_cooldown = cooldown
        self.support_casts += 1
        self.mastery_xp += 0.6
        if self.branch_has("research") and self.support_casts % 3 == 0:
            research_points += 1
            add_floating_text(self.x - 20, self.y - 44, "+1 Tech", (150, 220, 255))

    def find_target(self):
        valid = []
        for enemy in enemies:
            enemy_distance = dist((self.x, self.y), (enemy.x, enemy.y))
            if enemy_distance < self.minimum_range():
                continue
            if self.can_attack(enemy) and enemy_distance <= self.effective_range():
                valid.append(enemy)

        if not valid:
            return None

        marked = [enemy for enemy in valid if enemy.marked_timer > 0]
        if marked and (self.tower_type in ("archer", "sniper") or has_tower_mechanic("shared_targeting")):
            return min(marked, key=lambda e: e.hp)

        if self.target_mode == "first":
            return max(valid, key=lambda e: e.progress())
        if self.target_mode == "last":
            return min(valid, key=lambda e: e.progress())
        if self.target_mode == "strongest":
            return max(valid, key=lambda e: e.hp)
        if self.target_mode == "weakest":
            return min(valid, key=lambda e: e.hp)
        if self.target_mode == "flying":
            flying = [enemy for enemy in valid if enemy.flying]
            if flying:
                return min(flying, key=lambda e: dist((self.x, self.y), (e.x, e.y)))

        return min(valid, key=lambda e: dist((self.x, self.y), (e.x, e.y)))

    def support_bonus(self, bonus_type):
        bonus = 0
        if self.support_buff_timer > 0:
            if bonus_type == "damage":
                bonus = max(bonus, self.support_damage_bonus)
            elif bonus_type == "rate":
                bonus = max(bonus, self.support_rate_bonus)
        for tower in towers:
            if tower == self or not tower.has_mutation("field_medic"):
                continue
            if dist((self.x, self.y), (tower.x, tower.y)) <= tower.range * 0.85:
                if bonus_type == "damage":
                    bonus = max(bonus, 0.07)
                elif bonus_type == "rate":
                    bonus = max(bonus, 0.06)
        for tower in towers:
            if tower == self or not tower.branch_has("overclock"):
                continue
            if tower.is_paragon or dist((self.x, self.y), (tower.x, tower.y)) <= tower.effective_range():
                if bonus_type == "rate":
                    bonus = max(bonus, 0.10 if self.tower_type == "machine_gun" else 0.06)
                elif bonus_type == "damage" and tower.level >= 4:
                    bonus = max(bonus, 0.06)
        return bonus

    def effective_damage(self):
        return self.damage * (1 + tower_damage_bonus_level * 0.05 + run_damage_bonus + self.support_bonus("damage"))

    def effective_fire_rate(self):
        return max(0.025, self.fire_rate * (1 - self.support_bonus("rate")))

    def effective_range(self):
        return self.range * (1 + run_range_bonus + self.support_bonus("range"))

    def draw(self):
        data = TOWER_TYPES.get(self.tower_type)
        color = data["color"] if data else (70, 110, 240)
        label = data["short"] if data else str(self.level)

        pygame.draw.ellipse(screen, (0, 0, 0, 85), (self.x - 20, self.y + 18, 40, 12))
        draw_glow(self.x, self.y, color, 28 if self.is_paragon else 22, 36 if self.is_paragon else 24)
        if self.fire_anim_timer > 0 and self.tower_type:
            flash = clamp(self.fire_anim_timer / 0.12, 0, 1)
            ring_radius = int(20 + (1 - flash) * 13)
            pygame.draw.circle(screen, blend_color(color, (255, 255, 255), 0.35), (self.x, self.y), ring_radius, 2)
            draw_glow(self.x, self.y, color, ring_radius + 6, int(42 * flash))
        sprite = None
        if self.tower_type:
            frames = images.get("towers", {}).get(self.tower_type, {})
            if self.fire_anim_timer > 0:
                sprite = get_animation_frame([frames.get("fire_1"), frames.get("fire_2")], 80) or frames.get("fire")
            else:
                sprite = get_animation_frame([frames.get("idle_1"), frames.get("idle_2")], 420) or frames.get("idle")
        if not draw_sprite_centered(screen, sprite, self.x, self.y):
            self.draw_figurine(color)
        if self.locked_timer > 0:
            lock_color = (255, 90, 120)
            pulse = (math.sin(pygame.time.get_ticks() * 0.018) + 1) * 0.5
            radius = 27 + int(pulse * 4)
            draw_glow(self.x, self.y, lock_color, radius + 6, 38)
            pygame.draw.circle(screen, lock_color, (self.x, self.y), radius, 2)
            pygame.draw.line(screen, lock_color, (self.x - 13, self.y - 13), (self.x + 13, self.y + 13), 3)
            pygame.draw.line(screen, lock_color, (self.x + 13, self.y - 13), (self.x - 13, self.y + 13), 3)
            draw_tiny_text("LOCK", self.x - 16, self.y - 38, (255, 150, 170))
        if selected_tower == self and (self.tower_type == "support" or self.has_mutation("field_medic")):
            aura_color = (245, 225, 145) if self.tower_type == "support" else MUTATION_TRAITS["field_medic"]["color"]
            pygame.draw.circle(screen, aura_color, (self.x, self.y), int(self.effective_range()), 1)
        if self.support_buff_timer > 0:
            buff_color = TOWER_TYPES["support"]["projectile_color"]
            pygame.draw.circle(screen, buff_color, (self.x, self.y), 25, 2)
            draw_tiny_text("BUFF", self.x - 17, self.y - 42, buff_color)
        if self.is_paragon:
            pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 23, 2)
        for index, mutation_key in enumerate(self.mutations[:MUTATION_SLOT_LIMIT]):
            mutation = MUTATION_TRAITS[mutation_key]
            pygame.draw.circle(screen, mutation["color"], (self.x - 14 + index * 12, self.y + 27), 4)
        draw_text(str(self.level), self.x - 6, self.y - 10, (255, 255, 255))
        draw_small_text("M" if self.is_paragon else label, self.x - 13, self.y + 8, (255, 255, 255))
        if self.level >= MAX_TOWER_LEVEL:
            draw_small_text("MAX", self.x - 16, self.y - 32, (255, 255, 255))
        elif self.level >= BASE_MAX_TOWER_LEVEL and not self.can_upgrade():
            draw_small_text("XP", self.x - 10, self.y - 32, (255, 235, 130))

    def draw_figurine(self, color):
        x, y = self.x, self.y
        pygame.draw.circle(screen, color, (x, y - 8), 7)
        pygame.draw.rect(screen, color, (x - 8, y - 2, 16, 18))
        pygame.draw.line(screen, (35, 35, 35), (x - 5, y + 16), (x - 10, y + 23), 3)
        pygame.draw.line(screen, (35, 35, 35), (x + 5, y + 16), (x + 10, y + 23), 3)

        if self.tower_type == "archer":
            pygame.draw.arc(screen, (95, 55, 25), (x - 22, y - 13, 18, 30), -1.2, 1.2, 2)
            pygame.draw.line(screen, (230, 210, 150), (x - 17, y + 2), (x + 15, y - 4), 2)
        elif self.tower_type == "sniper":
            pygame.draw.line(screen, (35, 35, 35), (x - 6, y - 1), (x + 28, y - 7), 4)
            pygame.draw.circle(screen, (210, 210, 220), (x + 13, y - 4), 3)
        elif self.tower_type == "machine_gun":
            pygame.draw.rect(screen, (45, 45, 45), (x + 4, y - 7, 26, 8))
            pygame.draw.circle(screen, (30, 30, 30), (x + 30, y - 3), 4)
        elif self.tower_type == "cannon":
            pygame.draw.rect(screen, (55, 45, 40), (x - 3, y - 10, 28, 12))
            pygame.draw.circle(screen, (80, 70, 65), (x + 24, y - 4), 6)
        elif self.tower_type == "frost":
            pygame.draw.line(screen, (200, 245, 255), (x - 17, y - 18), (x + 17, y + 10), 3)
            pygame.draw.circle(screen, (220, 250, 255), (x + 18, y + 11), 5)
        elif self.tower_type == "tesla":
            pygame.draw.line(screen, (255, 245, 90), (x, y - 20), (x - 8, y - 2), 3)
            pygame.draw.line(screen, (255, 245, 90), (x - 8, y - 2), (x + 9, y - 2), 3)
            pygame.draw.line(screen, (255, 245, 90), (x + 9, y - 2), (x, y + 18), 3)
        elif self.tower_type == "poison":
            pygame.draw.circle(screen, (125, 235, 95), (x + 16, y - 5), 7)
            pygame.draw.rect(screen, (45, 95, 45), (x + 11, y - 3, 10, 17))
            pygame.draw.circle(screen, (185, 255, 140), (x + 17, y - 8), 3)
        elif self.tower_type == "barracks":
            pygame.draw.rect(screen, (135, 100, 55), (x - 21, y + 5, 12, 18))
            pygame.draw.rect(screen, (135, 100, 55), (x + 9, y + 5, 12, 18))
            pygame.draw.line(screen, (220, 220, 230), (x - 15, y + 3), (x - 15, y - 12), 2)
            pygame.draw.line(screen, (220, 220, 230), (x + 15, y + 3), (x + 15, y - 12), 2)
        elif self.tower_type == "flame":
            pygame.draw.polygon(screen, (255, 115, 45), [(x + 8, y - 14), (x + 25, y - 2), (x + 8, y + 10)])
            pygame.draw.circle(screen, (255, 190, 70), (x + 12, y - 2), 5)
        elif self.tower_type == "mortar":
            pygame.draw.rect(screen, (65, 60, 55), (x - 5, y - 18, 15, 32))
            pygame.draw.line(screen, (90, 85, 75), (x + 2, y - 16), (x + 24, y - 28), 7)
            pygame.draw.circle(screen, (45, 42, 38), (x + 25, y - 29), 5)
        elif self.tower_type == "support":
            pygame.draw.line(screen, (80, 60, 30), (x - 16, y + 18), (x - 16, y - 20), 3)
            pygame.draw.polygon(screen, (235, 215, 90), [(x - 15, y - 20), (x + 18, y - 12), (x - 15, y - 4)])
        elif self.tower_type == "gold":
            pygame.draw.circle(screen, (255, 220, 90), (x + 15, y - 4), 8)
            pygame.draw.circle(screen, (160, 120, 35), (x + 15, y - 4), 8, 2)
            draw_tiny_text("$", x + 11, y - 9, (70, 55, 20))


class BurstEffect:
    def __init__(self, x, y, color, max_radius, duration, sprite_name=None):
        self.x = x
        self.y = y
        self.color = color
        self.max_radius = max_radius
        self.duration = duration
        self.timer = duration
        self.sprite_name = sprite_name
        self.dead = False

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.dead = True

    def draw(self):
        progress = 1 - self.timer / self.duration
        radius = max(2, int(self.max_radius * progress))
        sprite_name = self.sprite_name or ("explosion" if self.color[0] >= 160 and self.color[1] < 180 else "frost_burst")
        sprite = images.get("effects", {}).get(sprite_name)
        if sprite:
            size = max(12, radius * 2)
            scaled = get_scaled_sprite(sprite, (size, size))
            draw_sprite_centered(screen, scaled, self.x, self.y)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius, 2)


class SparkEffect:
    def __init__(self, x, y, color, radius, duration, sprite_name="spark"):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.duration = duration
        self.timer = duration
        self.sprite_name = sprite_name
        self.dead = False

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.dead = True

    def draw(self):
        progress = self.timer / self.duration
        radius = max(1, int(self.radius * progress))
        sprite = images.get("effects", {}).get(self.sprite_name)
        if sprite:
            size = max(8, radius * 2)
            scaled = get_scaled_sprite(sprite, (size, size))
            draw_sprite_centered(screen, scaled, self.x, self.y)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)


class LightningEffect:
    def __init__(self, start, end, color=(255, 245, 120), duration=0.09):
        self.start = start
        self.end = end
        self.color = color
        self.duration = duration
        self.timer = duration
        self.dead = False

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.dead = True

    def draw(self):
        sx, sy = self.start
        ex, ey = self.end
        points = [(sx, sy)]

        for i in range(1, 4):
            t = i / 4
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t
            jitter = math.sin((self.timer * 120) + i * 2.3) * 12
            points.append((x + jitter, y - jitter * 0.5))

        points.append((ex, ey))
        pygame.draw.lines(screen, self.color, False, points, 3)
        pygame.draw.lines(screen, (255, 255, 255), False, points, 1)


class FloatingTextEffect:
    def __init__(self, x, y, text, color, duration=0.6):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.timer = duration
        self.dead = False

    def update(self, dt):
        self.timer -= dt
        self.y -= 28 * dt
        if self.timer <= 0:
            self.dead = True

    def draw(self):
        alpha_ratio = max(0.25, self.timer / self.duration)
        color = tuple(int(channel * alpha_ratio) for channel in self.color)
        draw_tiny_text(self.text, int(self.x), int(self.y), color)


def damage_text_color(tower_type):
    colors = {
        "archer": (205, 245, 185),
        "sniper": (255, 245, 245),
        "machine_gun": (255, 230, 100),
        "cannon": (255, 160, 90),
        "frost": (180, 240, 255),
        "tesla": (160, 210, 255),
        "barracks": (235, 205, 150),
        "poison": (150, 245, 110),
        "flame": (255, 150, 80),
        "mortar": (230, 185, 125),
        "gold": (255, 225, 95),
    }
    return colors.get(tower_type, (245, 245, 220))


def add_floating_text(x, y, text, color):
    if not should_show_floating_text(text):
        return
    floating_count = sum(1 for effect in effects if isinstance(effect, FloatingTextEffect))
    if floating_count >= current_floating_text_limit():
        return
    add_effect(FloatingTextEffect(x, y, text, color))


def add_effect(effect):
    if not should_show_effect(effect):
        return
    max_effects = current_effect_limit()
    if len(effects) >= max_effects:
        for index, existing in enumerate(effects):
            if not isinstance(existing, FloatingTextEffect):
                effects.pop(index)
                break
        else:
            return
    effects.append(effect)


def current_effect_limit():
    if len(enemies) >= VERY_BUSY_ENEMY_COUNT:
        return 70
    if len(enemies) >= BUSY_ENEMY_COUNT:
        return 105
    return MAX_ACTIVE_EFFECTS


def current_floating_text_limit():
    if len(enemies) >= VERY_BUSY_ENEMY_COUNT:
        return 8
    if len(enemies) >= BUSY_ENEMY_COUNT:
        return 16
    return MAX_FLOATING_TEXTS


def should_show_floating_text(text):
    if len(enemies) < BUSY_ENEMY_COUNT:
        return True

    numeric_text = text.isdigit() or text.startswith(("+$", "$", "CRIT "))
    noisy_status = text in {"BLOCK", "CHAIN", "SHIELD", "SLOW", "BURN", "POISON", "TOXIN"}
    if numeric_text or noisy_status:
        return False

    if len(enemies) >= VERY_BUSY_ENEMY_COUNT and text not in {"FREEZE", "SHATTER", "OVERCHARGE"}:
        return False

    return True


def should_show_effect(effect):
    enemy_count = len(enemies)
    if enemy_count < BUSY_ENEMY_COUNT:
        return True

    if isinstance(effect, SparkEffect):
        return len(effects) < current_effect_limit() * 0.35
    if isinstance(effect, LightningEffect):
        return enemy_count < VERY_BUSY_ENEMY_COUNT and len(effects) < current_effect_limit() * 0.55
    if isinstance(effect, BurstEffect):
        return len(effects) < current_effect_limit() * 0.75

    return True


def mutation_requirement_met(tower, mutation_key):
    if tower.tower_type is None:
        return False
    if mutation_key in tower.mutations or mutation_key in tower.available_mutations:
        return False
    if not tower.can_add_mutation():
        return False

    if mutation_key == "fast_hunter":
        return tower.behavior_hits["fast"] >= 20 or tower.behavior_kills["fast"] >= 5
    if mutation_key == "armor_piercer":
        return tower.behavior_hits["armored"] >= 22 or tower.shield_breaks >= 8
    if mutation_key == "field_medic":
        return (
            tower.tower_type != "support"
            and tower.waves_present >= 2
            and tower.kills <= 2
            and (tower.shots_fired >= 22 or tower.total_damage >= 250 or tower.mastery_xp >= 6)
        )
    if mutation_key == "corrupted":
        return tower.nearby_deaths >= 28
    if mutation_key == "swarm_reaper":
        return tower.behavior_hits["swarm"] >= 30 or tower.behavior_kills["swarm"] >= 8
    if mutation_key == "sky_watcher":
        return (
            tower.tower_type not in ("support", "barracks")
            and (tower.behavior_hits["flying"] >= 10 or tower.behavior_kills["flying"] >= 3 or tower.flying_seen_timer >= 10)
        )
    return False


def evaluate_mutations_for_tower(tower):
    available_slots = MUTATION_SLOT_LIMIT - len(tower.mutations) - len(tower.available_mutations)
    if available_slots <= 0:
        return

    for mutation_key in MUTATION_TRAITS:
        if mutation_requirement_met(tower, mutation_key):
            tower.available_mutations.append(mutation_key)
            if mutation_key not in tower.notified_mutations:
                tower.notified_mutations.add(mutation_key)
                add_floating_text(tower.x - 38, tower.y - 48, "MUTATION READY", MUTATION_TRAITS[mutation_key]["color"])
            available_slots -= 1
            if available_slots <= 0:
                break


def evaluate_all_mutations():
    for tower in towers:
        evaluate_mutations_for_tower(tower)


def award_enemy_death_credit(enemy):
    global money, research_points

    killer = enemy.last_damaging_tower
    if killer in towers:
        killer.record_kill(enemy)
        if killer.has_mutation("corrupted") and killer.corruption_burst_cooldown <= 0:
            add_effect(BurstEffect(enemy.x, enemy.y, MUTATION_TRAITS["corrupted"]["color"], 34, 0.24))
            emit_particles(enemy.x, enemy.y, MUTATION_TRAITS["corrupted"]["color"], 9, 90, 5, 0.42)
            killer.corruption_burst_cooldown = 0.45

    death_color = (255, 150, 90) if enemy.boss else (220, 90, 70)
    emit_particles(enemy.x, enemy.y, death_color, 14 if enemy.boss else 6, 95 if enemy.boss else 55, 5 if enemy.boss else 3, 0.45)

    for tower in towers:
        if dist((tower.x, tower.y), (enemy.x, enemy.y)) <= CORRUPTION_DEATH_RADIUS:
            tower.nearby_deaths += 1
        if tower.branch_has("bounty") and dist((tower.x, tower.y), (enemy.x, enemy.y)) <= tower.effective_range():
            bonus = 2 if enemy.boss else 1
            money += bonus
            tower.mastery_xp += 0.25
            add_floating_text(tower.x - 12, tower.y - 44, f"+${bonus}", (245, 220, 110))
        if tower.branch_has("research") and dist((tower.x, tower.y), (enemy.x, enemy.y)) <= tower.effective_range():
            tower.mastery_xp += 0.18
            if enemy.boss or (tower.nearby_deaths > 0 and tower.nearby_deaths % 14 == 0):
                research_points += 1
                add_floating_text(tower.x - 18, tower.y - 44, "+1 Tech", (150, 220, 255))

    if enemy.marked_timer > 0 and (has_tower_mechanic("marked_reward") or has_tower_mechanic("research")):
        money += 1
        add_floating_text(enemy.x - 12, enemy.y - 46, "+$1 MARK", (245, 230, 140))


class Projectile:
    def __init__(self, x, y, target, tower):
        self.x = x
        self.y = y
        self.target = target
        self.source_tower = tower
        self.damage = tower.effective_damage()
        self.tower_type = tower.tower_type
        self.tower_level = tower.level
        if self.tower_type == "mortar":
            self.speed = 300
        else:
            self.speed = 760 if self.tower_type in ("sniper", "machine_gun", "tesla") else 420
        self.dead = False
        self.trail_timer = 0

    def update(self, dt):
        if self.target not in enemies:
            self.dead = True
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)

        if distance < 8:
            self.hit_target()
            self.dead = True
            return

        self.x += (dx / distance) * self.speed * dt
        self.y += (dy / distance) * self.speed * dt
        self.update_trail(dt)

    def update_trail(self, dt):
        if len(enemies) >= BUSY_ENEMY_COUNT:
            return

        self.trail_timer -= dt
        if self.trail_timer > 0:
            return

        self.trail_timer = 0.07

        if self.tower_type == "archer":
            add_effect(SparkEffect(self.x, self.y, (210, 160, 90), 3, 0.10))
            emit_shot_particles(self.x, self.y, (210, 160, 90), 1, 14, 1.6, 0.08, 0.45)
        elif self.tower_type == "machine_gun":
            add_effect(SparkEffect(self.x, self.y, (255, 230, 120), 3, 0.08))
            emit_shot_particles(self.x, self.y, (255, 230, 120), 1, 16, 1.6, 0.08, 0.35)
        elif self.tower_type == "cannon":
            add_effect(SparkEffect(self.x, self.y, (90, 80, 70), 6, 0.18, "smoke"))
            emit_shot_particles(self.x, self.y, (90, 80, 70), 1, 18, 2.2, 0.14, 0.55)
        elif self.tower_type == "frost":
            add_effect(SparkEffect(self.x, self.y, (185, 240, 255), 5, 0.18, "frost_mist"))
            emit_shot_particles(self.x, self.y, (185, 240, 255), 1, 18, 2.2, 0.14, 0.55)
        elif self.tower_type == "poison":
            add_effect(SparkEffect(self.x, self.y, (125, 235, 95), 5, 0.16, "poison_cloud"))
            emit_shot_particles(self.x, self.y, (125, 235, 95), 1, 16, 2, 0.12, 0.55)
        elif self.tower_type == "flame":
            add_effect(SparkEffect(self.x, self.y, (255, 115, 45), 5, 0.12, "flame_burst"))
            emit_shot_particles(self.x, self.y, (255, 115, 45), 1, 22, 2, 0.10, 0.55)
        elif self.tower_type == "mortar":
            add_effect(SparkEffect(self.x, self.y, (95, 85, 70), 8, 0.22, "smoke"))
            emit_shot_particles(self.x, self.y, (95, 85, 70), 1, 16, 2.8, 0.16, 0.55)
        elif self.tower_type == "gold":
            add_effect(SparkEffect(self.x, self.y, (255, 220, 90), 5, 0.12, "coin_sparkle"))
            emit_shot_particles(self.x, self.y, (255, 220, 90), 1, 16, 2, 0.10, 0.45)
        elif self.tower_type == "tesla":
            jittered = (
                self.x + math.sin(self.trail_timer + self.x) * 8,
                self.y + math.cos(self.trail_timer + self.y) * 8,
            )
            add_effect(LightningEffect((self.x, self.y), jittered, duration=0.04))
            emit_shot_particles(self.x, self.y, (255, 245, 90), 1, 20, 1.6, 0.08, 0.40)

    def hit_target(self):
        global money

        self.spawn_hit_effect()
        data = TOWER_TYPES.get(self.tower_type, {})
        emit_shot_particles(self.target.x, self.target.y, data.get("projectile_color", (245, 220, 80)), 2, 36, 2, 0.14, 0.85)
        damage_type = self.get_damage_type()
        shield_before = self.target.shield_hits
        damage, synergy_labels = apply_synergy_damage(self.tower_type, self.target, self.damage, damage_type)
        dealt = self.target.take_damage(damage, damage_type, self.source_tower)
        if shield_before > 0:
            add_floating_text(self.target.x - 10, self.target.y - 34, "BLOCK", (210, 210, 235))
        for index, label in enumerate(synergy_labels):
            add_floating_text(self.target.x - 16, self.target.y - 42 - index * 12, label, (255, 245, 150))
        add_floating_text(self.target.x - 8, self.target.y - 24, str(int(dealt)), damage_text_color(self.tower_type))
        self.source_tower.total_damage += dealt
        self.source_tower.mastery_xp += dealt * 0.02
        self.apply_branch_effects()
        self.apply_swarm_reaper_cleave()

        if self.tower_type == "sniper":
            self.target.marked_timer = max(self.target.marked_timer, 2.0)
            add_floating_text(self.target.x - 16, self.target.y - 50, "SCANNED", (150, 235, 255))
            if self.tower_level >= 3:
                self.target.shield_hits = max(0, self.target.shield_hits - 1)
            if self.tower_level >= 4:
                dealt = self.target.take_damage(self.damage * 0.35, "pierce", self.source_tower)
                add_floating_text(self.target.x + 8, self.target.y - 38, f"CRIT {int(dealt)}", (255, 245, 245))
                self.source_tower.total_damage += dealt
                self.source_tower.mastery_xp += dealt * 0.02
        elif self.tower_type == "cannon":
            splash_radius = 48 + self.tower_level * 9
            splash_damage = self.damage * (0.45 if self.tower_level < 5 else 0.75)
            trigger_screen_shake(0.08, 3)
            if self.tower_level >= 4:
                self.target.vulnerable_timer = max(self.target.vulnerable_timer, 2.0)
                self.target.damage_multiplier = max(self.target.damage_multiplier, 1.18)
            for enemy in enemies:
                if enemy != self.target and dist((self.target.x, self.target.y), (enemy.x, enemy.y)) <= splash_radius:
                    adjusted_damage, labels = apply_synergy_damage(self.tower_type, enemy, splash_damage, "explosive")
                    dealt = enemy.take_damage(adjusted_damage, "explosive", self.source_tower)
                    for label_index, label in enumerate(labels):
                        add_floating_text(enemy.x - 16, enemy.y - 38 - label_index * 12, label, (255, 245, 150))
                    add_floating_text(enemy.x - 8, enemy.y - 24, str(int(dealt)), damage_text_color(self.tower_type))
                    self.source_tower.total_damage += dealt
                    self.source_tower.mastery_xp += dealt * 0.02
                    if self.tower_level >= 4:
                        enemy.vulnerable_timer = max(enemy.vulnerable_timer, 1.5)
                        enemy.damage_multiplier = max(enemy.damage_multiplier, 1.12)
        elif self.tower_type == "frost":
            slow_multiplier = 0.68 if self.tower_level < 3 else 0.52
            slow_timer = 1.8 if self.tower_level < 4 else 2.6
            self.apply_slow(self.target, slow_multiplier, slow_timer)
            add_floating_text(self.target.x - 10, self.target.y - 38, "SLOW", (180, 240, 255))
            if self.tower_level >= 4:
                for enemy in self.nearby_enemies(self.target, 60):
                    self.apply_slow(enemy, slow_multiplier, slow_timer * 0.75)
            if self.tower_level >= 5:
                self.target.freeze_timer = max(self.target.freeze_timer, 0.45 if self.tower_level < PARAGON_LEVEL else 0.8)
                add_floating_text(self.target.x - 12, self.target.y - 52, "FREEZE", (220, 250, 255))
                play_sound("freeze", 0.25)
        elif self.tower_type == "poison":
            poison_dps = self.damage * (0.20 + self.tower_level * 0.035)
            poison_timer = 2.6 + self.tower_level * 0.35
            self.apply_poison(self.target, poison_dps, poison_timer)
            add_floating_text(self.target.x - 18, self.target.y - 38, "POISON", (150, 245, 110))
            if self.tower_level >= 4:
                spread_limit = 4 if self.tower_level >= PARAGON_LEVEL else 2
                for enemy in self.nearby_enemies(self.target, 58 + self.tower_level * 4, spread_limit):
                    self.apply_poison(enemy, poison_dps * 0.45, poison_timer * 0.75)
                    add_floating_text(enemy.x - 18, enemy.y - 38, "TOXIN", (150, 245, 110))
        elif self.tower_type == "flame":
            burn_dps = self.damage * (0.24 + self.tower_level * 0.035)
            burn_timer = 1.7 + self.tower_level * 0.25
            self.apply_burn(self.target, burn_dps, burn_timer)
            add_floating_text(self.target.x - 12, self.target.y - 38, "BURN", (255, 145, 70))
            splash_radius = 34 + self.tower_level * 5
            splash_damage = self.damage * (0.25 if self.tower_level < 5 else 0.38)
            for enemy in self.nearby_enemies(self.target, splash_radius, 4):
                if enemy.flying:
                    continue
                dealt = enemy.take_damage(splash_damage, "fire", self.source_tower)
                self.apply_burn(enemy, burn_dps * 0.55, burn_timer * 0.7)
                add_floating_text(enemy.x - 8, enemy.y - 24, str(int(dealt)), damage_text_color(self.tower_type))
                self.source_tower.total_damage += dealt
                self.source_tower.mastery_xp += dealt * 0.02
        elif self.tower_type == "mortar":
            splash_radius = 68 + self.tower_level * 11
            splash_damage = self.damage * (0.55 if self.tower_level < 5 else 0.82)
            trigger_screen_shake(0.10, 4)
            for enemy in self.nearby_enemies(self.target, splash_radius, 8):
                adjusted_damage, labels = apply_synergy_damage(self.tower_type, enemy, splash_damage, "explosive")
                dealt = enemy.take_damage(adjusted_damage, "explosive", self.source_tower)
                for label_index, label in enumerate(labels):
                    add_floating_text(enemy.x - 16, enemy.y - 38 - label_index * 12, label, (255, 245, 150))
                add_floating_text(enemy.x - 8, enemy.y - 24, str(int(dealt)), damage_text_color(self.tower_type))
                self.source_tower.total_damage += dealt
                self.source_tower.mastery_xp += dealt * 0.02
        elif self.tower_type == "gold":
            if self.target.hp <= self.target.max_hp * 0.5:
                bonus = 1 if self.tower_level < PARAGON_LEVEL else 2
                money += bonus
                self.source_tower.gold_income_earned += bonus
                add_floating_text(self.target.x + 4, self.target.y - 40, f"+${bonus}", TOWER_TYPES["gold"]["projectile_color"])
        elif self.tower_type == "tesla":
            if self.tower_level < 3:
                return

            chain_count = 1
            chain_damage = self.damage * 0.5
            chain_range = 90

            if self.tower_level >= 4:
                chain_count = 3
                chain_range = 105
            if self.tower_level >= 5:
                chain_damage = self.damage * 0.75
                chain_range = 120
            if self.tower_level >= PARAGON_LEVEL:
                chain_count = 3
                chain_damage = self.damage * 0.45
                chain_range = 125
            if (self.target.slow_timer > 0 or self.target.freeze_timer > 0) and has_tower_type("frost"):
                chain_count = min(4, chain_count + 1)
                add_floating_text(self.target.x - 20, self.target.y - 50, "OVERCHARGE", (180, 220, 255))

            chain_targets = [
                enemy for enemy in enemies
                if enemy != self.target and dist((self.target.x, self.target.y), (enemy.x, enemy.y)) <= chain_range
            ]
            chain_targets.sort(key=lambda e: dist((self.target.x, self.target.y), (e.x, e.y)))
            for enemy in chain_targets[:chain_count]:
                dealt = enemy.take_damage(chain_damage, "electric", self.source_tower)
                add_floating_text(enemy.x - 8, enemy.y - 24, str(int(dealt)), damage_text_color(self.tower_type))
                add_floating_text(enemy.x - 10, enemy.y - 38, "CHAIN", (180, 220, 255))
                self.source_tower.total_damage += dealt
                self.source_tower.mastery_xp += dealt * 0.02
                add_effect(LightningEffect((self.target.x, self.target.y), (enemy.x, enemy.y)))
                play_sound("chain", 0.05)

    def apply_branch_effects(self):
        branch = self.source_tower.branch_data()
        if branch is None:
            return

        mechanics = set(branch["mechanics"])
        tower_level = self.source_tower.level

        if mechanics.intersection({"mark", "paint", "shared_targeting"}):
            mark_time = 2.0 + max(0, tower_level - BRANCH_UNLOCK_LEVEL) * 0.35
            self.target.marked_timer = max(self.target.marked_timer, mark_time)
            self.target.vulnerable_timer = max(self.target.vulnerable_timer, 0.8)
            self.target.damage_multiplier = max(self.target.damage_multiplier, 1.08)
            add_floating_text(self.target.x - 18, self.target.y - 50, "SCAN", branch["color"])

        if "poison" in mechanics:
            poison_dps = self.damage * (0.12 + tower_level * 0.025)
            self.apply_poison(self.target, poison_dps, 2.2 + tower_level * 0.25)
            if self.target.affix == "regen":
                self.target.regen_rate *= 0.75
            add_floating_text(self.target.x - 18, self.target.y - 40, "VENOM", (150, 245, 110))

        if "burn" in mechanics:
            burn_dps = self.damage * (0.10 + tower_level * 0.025)
            self.apply_burn(self.target, burn_dps, 1.4 + tower_level * 0.22)
            add_floating_text(self.target.x - 14, self.target.y - 40, "BURN", (255, 145, 70))

        if mechanics.intersection({"slow", "pin", "trap", "crater", "hazard"}):
            slow = 0.72 if tower_level < 5 else 0.62
            self.apply_slow(self.target, slow, 0.9 + tower_level * 0.14)
            add_floating_text(self.target.x - 12, self.target.y - 38, "SNARE", branch["color"])

        if mechanics.intersection({"stasis", "cryo_prison"}):
            if self.target.slow_timer > 0 or self.target.freeze_timer > 0:
                self.target.freeze_timer = max(self.target.freeze_timer, 0.22 if tower_level < 5 else 0.38)
                add_floating_text(self.target.x - 12, self.target.y - 52, "STASIS", branch["color"])

        if mechanics.intersection({"armor_break", "shield_break", "pierce", "emp"}):
            if self.target.shield_hits > 0:
                self.target.shield_hits = max(0, self.target.shield_hits - 1)
                self.source_tower.shield_breaks += 1
            self.target.vulnerable_timer = max(self.target.vulnerable_timer, 1.8)
            self.target.damage_multiplier = max(self.target.damage_multiplier, 1.15)
            add_floating_text(self.target.x - 16, self.target.y - 48, "EXPOSED", branch["color"])

        if mechanics.intersection({"pet_hit", "echo", "delayed_damage"}):
            bonus = self.damage * (0.16 if tower_level < 5 else 0.25)
            dealt = self.target.take_damage(bonus, self.get_damage_type(), self.source_tower)
            self.source_tower.total_damage += dealt
            self.source_tower.mastery_xp += dealt * 0.02
            add_floating_text(self.target.x + 8, self.target.y - 34, f"+{int(dealt)}", branch["color"])

        if "adaptive_ammo" in mechanics:
            if has_behavior_tag(self.target, "armored"):
                self.target.shield_hits = max(0, self.target.shield_hits - 1)
            if has_behavior_tag(self.target, "swarm"):
                self.apply_swarm_reaper_cleave()

        if "pull" in mechanics:
            for enemy in self.nearby_enemies(self.target, 70, 3):
                enemy.x += (self.target.x - enemy.x) * 0.08
                enemy.y += (self.target.y - enemy.y) * 0.08
                enemy.slow_timer = max(enemy.slow_timer, 0.45)
                enemy.slow_multiplier = min(enemy.slow_multiplier, 0.72)
            add_floating_text(self.target.x - 12, self.target.y - 52, "PULL", branch["color"])

    def apply_swarm_reaper_cleave(self):
        if not self.source_tower.has_mutation("swarm_reaper") or not has_behavior_tag(self.target, "swarm"):
            return

        cleave_targets = [
            enemy for enemy in enemies
            if enemy != self.target
            and has_behavior_tag(enemy, "swarm")
            and dist((self.target.x, self.target.y), (enemy.x, enemy.y)) <= 55
        ]
        cleave_targets.sort(key=lambda enemy: dist((self.target.x, self.target.y), (enemy.x, enemy.y)))
        for enemy in cleave_targets[:3]:
            dealt = enemy.take_damage(self.damage * 0.22, "physical", self.source_tower)
            self.source_tower.total_damage += dealt
            self.source_tower.mastery_xp += dealt * 0.02
            add_floating_text(enemy.x - 12, enemy.y - 34, "REAP", MUTATION_TRAITS["swarm_reaper"]["color"])

    def get_damage_type(self):
        if self.tower_type == "sniper":
            return "pierce"
        if self.tower_type in ("cannon", "mortar"):
            return "explosive"
        if self.tower_type == "tesla":
            return "electric"
        if self.tower_type == "poison":
            return "poison"
        if self.tower_type == "flame":
            return "fire"
        return "physical"

    def spawn_hit_effect(self):
        if self.tower_type == "sniper":
            add_effect(LightningEffect((self.x, self.y), (self.target.x, self.target.y), (245, 245, 235), 0.06))
        elif self.tower_type == "machine_gun":
            add_effect(SparkEffect(self.target.x, self.target.y, (255, 225, 100), 7, 0.08))
        elif self.tower_type == "cannon":
            add_effect(SparkEffect(self.target.x, self.target.y, (100, 92, 82), 18, 0.26, "smoke"))
            add_effect(BurstEffect(self.target.x, self.target.y, (185, 120, 70), 34 + self.tower_level * 7, 0.28, "explosion_ring"))
        elif self.tower_type == "frost":
            add_effect(BurstEffect(self.target.x, self.target.y, (120, 220, 255), 24 + self.tower_level * 4, 0.26, "frost_mist"))
        elif self.tower_type == "tesla":
            add_effect(LightningEffect((self.x, self.y), (self.target.x, self.target.y)))
            add_effect(SparkEffect(self.target.x, self.target.y, (255, 255, 150), 12, 0.16, "lightning_spark"))
        elif self.tower_type == "poison":
            add_effect(BurstEffect(self.target.x, self.target.y, (110, 220, 85), 24 + self.tower_level * 4, 0.25, "poison_cloud"))
        elif self.tower_type == "flame":
            add_effect(BurstEffect(self.target.x, self.target.y, (255, 105, 45), 28 + self.tower_level * 5, 0.22, "flame_burst"))
        elif self.tower_type == "mortar":
            add_effect(SparkEffect(self.target.x, self.target.y, (100, 92, 82), 24, 0.32, "smoke"))
            add_effect(BurstEffect(self.target.x, self.target.y, (170, 130, 85), 52 + self.tower_level * 10, 0.32, "explosion_ring"))
        elif self.tower_type == "gold":
            add_effect(SparkEffect(self.target.x, self.target.y, (255, 225, 90), 10, 0.16, "coin_sparkle"))
        else:
            add_effect(BurstEffect(self.target.x, self.target.y, (245, 220, 80), 18, 0.18))

    def nearby_enemies(self, target, radius, limit=None):
        nearby = [
            enemy for enemy in enemies
            if enemy != target and dist((target.x, target.y), (enemy.x, enemy.y)) <= radius
        ]
        nearby.sort(key=lambda e: dist((target.x, target.y), (e.x, e.y)))
        if limit is not None:
            return nearby[:limit]
        return nearby

    def apply_burn(self, enemy, dps, timer):
        enemy.burn_timer = max(enemy.burn_timer, timer)
        enemy.burn_dps = max(enemy.burn_dps, dps)
        enemy.burn_source_tower = self.source_tower

    def apply_poison(self, enemy, dps, timer):
        enemy.poison_timer = max(enemy.poison_timer, timer)
        enemy.poison_dps = max(enemy.poison_dps, dps)
        enemy.poison_source_tower = self.source_tower

    def apply_slow(self, enemy, multiplier, timer):
        enemy.slow_timer = max(enemy.slow_timer, timer)
        enemy.slow_multiplier = min(enemy.slow_multiplier, multiplier)

    def draw(self):
        data = TOWER_TYPES.get(self.tower_type)
        color = data["projectile_color"] if data else (245, 220, 80)
        sprite = images.get("projectiles", {}).get(self.tower_type)
        draw_glow(self.x, self.y, color, 12, 44)

        if draw_sprite_centered(screen, sprite, self.x, self.y):
            return

        if self.tower_type == "archer":
            pygame.draw.line(screen, color, (int(self.x - 8), int(self.y + 3)), (int(self.x + 8), int(self.y - 3)), 3)
        elif self.tower_type == "sniper":
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)
        elif self.tower_type == "machine_gun":
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)
        elif self.tower_type == "cannon":
            points = [
                (int(self.x), int(self.y - 7)),
                (int(self.x + 7), int(self.y)),
                (int(self.x), int(self.y + 7)),
                (int(self.x - 7), int(self.y)),
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (85, 60, 35), points, 1)
        elif self.tower_type == "frost":
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 6, 2)
            pygame.draw.circle(screen, (225, 250, 255), (int(self.x), int(self.y)), 3)
        elif self.tower_type == "tesla":
            pygame.draw.line(screen, color, (int(self.x - 7), int(self.y)), (int(self.x + 7), int(self.y)), 3)
            pygame.draw.line(screen, (255, 255, 255), (int(self.x), int(self.y - 7)), (int(self.x), int(self.y + 7)), 2)
        else:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 5)


def terrain_palette():
    palettes = {
        "forest": {
            "grass": (23, 36, 28),
            "grass_patch": (36, 57, 35),
            "grass_patch_dark": (18, 29, 23),
            "road_shadow": (36, 31, 25),
            "road_edge": (74, 57, 38),
            "road": (132, 102, 66),
            "road_highlight": (166, 130, 82),
        },
        "swamp": {
            "grass": (22, 39, 35),
            "grass_patch": (42, 66, 45),
            "grass_patch_dark": (16, 29, 29),
            "road_shadow": (31, 42, 31),
            "road_edge": (58, 72, 43),
            "road": (102, 118, 64),
            "road_highlight": (132, 148, 82),
        },
        "snow": {
            "grass": (174, 198, 202),
            "grass_patch": (214, 232, 232),
            "grass_patch_dark": (130, 158, 166),
            "road_shadow": (46, 56, 66),
            "road_edge": (62, 73, 86),
            "road": (101, 114, 128),
            "road_highlight": (146, 160, 172),
        },
        "lava": {
            "grass": (35, 27, 27),
            "grass_patch": (70, 38, 31),
            "grass_patch_dark": (24, 20, 21),
            "road_shadow": (24, 20, 20),
            "road_edge": (73, 38, 32),
            "road": (112, 63, 42),
            "road_highlight": (168, 86, 44),
        },
    }
    return palettes.get(current_theme(), palettes["forest"])


def draw_terrain():
    palette = terrain_palette()
    pygame.draw.rect(screen, palette["grass"], (0, 0, MAP_WIDTH, HEIGHT))

    for col in range(0, MAP_WIDTH, 72):
        for row in range(BUILD_GRID_TOP, HEIGHT, 72):
            patch_w = 30 + (col // 72) % 16
            patch_h = 13 + (row // 72) % 9
            patch = pygame.Rect(col + 12, row + 9, patch_w, patch_h)
            color = palette["grass_patch_dark"] if (col // 72 + row // 72) % 3 == 0 else palette["grass_patch"]
            pygame.draw.rect(screen, color, patch, border_radius=6)


def draw_portal_sparks(marker, color, radius, ticks, count=4):
    for index in range(count):
        angle = ticks * 0.006 + index * math.tau / count
        spark_x = int(marker[0] + math.cos(angle) * radius)
        spark_y = int(marker[1] + math.sin(angle) * radius * 0.64)
        pygame.draw.circle(screen, color, (spark_x, spark_y), 2 + index % 2)


def draw_signal_spawn_marker(marker):
    ticks = pygame.time.get_ticks()
    pulse = (math.sin(ticks * 0.009) + 1) * 0.5
    color = (78, 238, 198)
    accent = (105, 190, 255)
    radius = 24 + int(pulse * 3)
    arc_rect = pygame.Rect(marker[0] - radius + 3, marker[1] - radius + 3, (radius - 3) * 2, (radius - 3) * 2)

    draw_glow(marker[0], marker[1], color, radius + 10, 50)
    pygame.draw.circle(screen, (12, 40, 38), marker, radius)
    pygame.draw.circle(screen, color, marker, radius, 3)
    pygame.draw.circle(screen, accent, marker, radius - 8, 2)
    pygame.draw.arc(screen, color, arc_rect, ticks * 0.006, ticks * 0.006 + math.pi * 0.92, 3)
    pygame.draw.arc(screen, accent, arc_rect.inflate(-10, -10), ticks * 0.006 + math.pi, ticks * 0.006 + math.pi * 1.72, 2)

    portal_rect = pygame.Rect(marker[0] - 9, marker[1] - 16, 18, 32)
    pygame.draw.ellipse(screen, (5, 24, 28), portal_rect)
    pygame.draw.ellipse(screen, (218, 255, 236), portal_rect, 2)
    pygame.draw.line(screen, color, (marker[0], marker[1] - 10), (marker[0], marker[1] + 10), 2)
    draw_portal_sparks(marker, (196, 255, 230), radius + 4, ticks)


def draw_signal_core_marker(marker):
    integrity = clamp(lives / STARTING_LIVES, 0, 1)
    ticks = pygame.time.get_ticks()
    pulse = (math.sin(ticks * 0.008) + 1) * 0.5
    warning = integrity <= CORE_WARNING_RATIO
    color = (255, 90, 80) if warning else blend_color((255, 205, 82), (255, 115, 86), 1 - integrity)
    accent = (255, 242, 164) if not warning else (255, 178, 150)
    ring_radius = 25 + int(pulse * (8 if warning else 4))

    draw_glow(marker[0], marker[1], color, ring_radius + 8, 54 if warning else 40)
    pygame.draw.circle(screen, (55, 38, 24), marker, ring_radius)
    pygame.draw.circle(screen, color, marker, ring_radius, 2)
    pygame.draw.arc(
        screen,
        accent,
        pygame.Rect(marker[0] - ring_radius + 5, marker[1] - ring_radius + 5, (ring_radius - 5) * 2, (ring_radius - 5) * 2),
        ticks * -0.005,
        ticks * -0.005 + math.pi * 1.05,
        3,
    )
    pygame.draw.polygon(
        screen,
        accent,
        [
            (marker[0], marker[1] - 16),
            (marker[0] + 16, marker[1]),
            (marker[0], marker[1] + 16),
            (marker[0] - 16, marker[1]),
        ],
        2,
    )
    core_rect = pygame.Rect(marker[0] - 9, marker[1] - 9, 18, 18)
    pygame.draw.rect(screen, (28, 24, 20), core_rect, border_radius=3)
    pygame.draw.rect(screen, color, core_rect, 2, border_radius=3)
    pygame.draw.line(screen, accent, (marker[0] - 5, marker[1]), (marker[0] + 5, marker[1]), 2)
    pygame.draw.line(screen, accent, (marker[0], marker[1] - 5), (marker[0], marker[1] + 5), 2)
    draw_portal_sparks(marker, accent, ring_radius + 3, ticks, 3)
    if warning:
        draw_tiny_text("CORE", marker[0] - 18, marker[1] - 36, (255, 155, 130))


def draw_spawn_exit_markers():
    for path in current_paths():
        start = path[0]
        end = path[-1]
        start_marker = (max(32, min(MAP_WIDTH - 32, start[0])), start[1])
        end_marker = (max(32, min(MAP_WIDTH - 32, end[0])), end[1])
        draw_signal_spawn_marker(start_marker)
        draw_signal_core_marker(end_marker)


def draw_path():
    palette = terrain_palette()
    edge_color = palette["road_edge"]
    road_color = palette["road"]
    highlight_color = palette["road_highlight"]
    shadow_color = palette["road_shadow"]
    for path in current_paths():
        for i in range(len(path) - 1):
            pygame.draw.line(screen, shadow_color, path[i], path[i + 1], PATH_WIDTH + 22)
        for point in path:
            pygame.draw.circle(screen, shadow_color, point, PATH_WIDTH // 2 + 11)

        for i in range(len(path) - 1):
            pygame.draw.line(screen, edge_color, path[i], path[i + 1], PATH_WIDTH + 14)
        for point in path:
            pygame.draw.circle(screen, edge_color, point, PATH_WIDTH // 2 + 7)

        for i in range(len(path) - 1):
            pygame.draw.line(screen, road_color, path[i], path[i + 1], PATH_WIDTH)
        for point in path:
            pygame.draw.circle(screen, road_color, point, PATH_WIDTH // 2)

        for i in range(len(path) - 1):
            pygame.draw.line(screen, highlight_color, path[i], path[i + 1], 5)

    draw_spawn_exit_markers()


def draw_build_preview():
    mouse_pos = get_game_mouse_pos()
    site = get_build_site_at(mouse_pos)

    for tower in towers:
        rect = build_rect_for_site((tower.x, tower.y))
        pygame.draw.rect(screen, (45, 45, 38), rect)
        pygame.draw.rect(screen, (85, 85, 75), rect, 2)

    if site is None or game_over or victory or selected_build_type is None:
        return

    rect = build_rect_for_site(site)
    valid = can_place_tower(mouse_pos)
    preview_tower = Tower(site[0], site[1], selected_build_type, 0)

    if valid:
        fill = (35, 70, 52)
        outline = (80, 190, 120)
        range_color = TOWER_TYPES[selected_build_type]["range_color"]
    else:
        fill = (75, 36, 36)
        outline = (220, 70, 70)
        range_color = (220, 70, 70)

    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, outline, rect, 2)
    preview_tower.draw_figurine(TOWER_TYPES[selected_build_type]["color"])
    pygame.draw.circle(screen, range_color, site, int(preview_tower.range), 1)


def can_place_tower(pos):
    global money

    if selected_build_type is None:
        return False

    if money < SHOP_COSTS[selected_build_type]:
        return False

    site = get_build_site_at(pos)
    if site is None:
        return False

    if build_rect_overlaps_path(site):
        return False

    if is_site_occupied(site):
        return False

    return True


def spawn_enemy():
    global spawn_path_index, boss_warning_timer

    if len(enemies) >= MAX_ACTIVE_ENEMIES:
        return False

    kind = get_next_enemy_kind()
    path_index = spawn_path_index % len(current_paths())
    spawn_path_index += 1
    enemies.append(create_enemy(kind, path_index=path_index))
    if kind == "boss":
        play_sound("boss_spawn", 0.5)
        trigger_screen_shake(0.2, 5)
        boss_warning_timer = 2.0
    return True


def update_commander_auras():
    commanders = [enemy for enemy in enemies if enemy.commander and enemy.hp > 0]
    if not commanders:
        return

    for commander in commanders:
        for enemy in enemies:
            if enemy == commander or enemy.hp <= 0:
                continue
            if dist((commander.x, commander.y), (enemy.x, enemy.y)) <= COMMANDER_AURA_RADIUS:
                enemy.commander_aura_timer = max(enemy.commander_aura_timer, 0.22)


def get_next_enemy_kind():
    boss_count = get_boss_count_for_wave()
    if spawned_this_wave < boss_count:
        return "boss"
    if spawned_this_wave < boss_count + get_commander_count_for_wave():
        return "commander"
    return get_wave_enemy_kind()


def apply_bounty_bonus(enemy):
    if next_wave_bounty_wave == wave and next_wave_bounty_bonus > 0:
        enemy.reward += next_wave_bounty_bonus
    return enemy


def get_boss_count_for_wave(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    return get_boss_count_for_wave_data(preview_wave)


def get_commander_count_for_wave(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    return get_commander_count_for_wave_data(preview_wave)


def get_enemies_per_wave(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    return (
        get_regular_enemy_count_data(preview_wave)
        + get_boss_count_for_wave(preview_wave)
        + get_commander_count_for_wave(preview_wave)
    )


def get_spawn_interval(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    return get_spawn_interval_data(preview_wave)


def get_wave_enemy_kind(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    return get_wave_enemy_kind_data(preview_wave)


def get_wave_label(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    return get_wave_label_data(preview_wave)


def get_wave_affix(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    return get_wave_affix_data(preview_wave)


def get_wave_modifier_data(wave_number=None):
    preview_wave = wave if wave_number is None else wave_number
    return get_wave_modifier_data_for_wave(preview_wave)


def apply_wave_affix(enemy):
    affix = get_wave_affix()
    if enemy.boss or affix is None:
        return enemy

    enemy.affix = affix
    return apply_modifier_effects(enemy, affix)


def create_enemy(kind, x=None, y=None, target_index=1, path_index=0, allow_affix=True):
    hp = 65 + wave * 18 + max(0, wave - 10) * 8 + max(0, wave - 20) * 18
    speed = 62 + wave * 2
    reward = 4 + wave // 8

    if kind == "fast":
        hp *= 0.65
        speed *= 1.65
        reward += 1
    elif kind == "tank":
        hp *= 2.2
        speed *= 0.62
        reward += 4
    elif kind == "swarm":
        hp *= 0.45
        speed *= 1.15
        reward += 0
    elif kind == "shield":
        hp *= 1.2
        speed *= 0.9
        reward += 3
        enemy = Enemy(hp, speed, reward, kind=kind, shield_hits=2, path_index=path_index)
        if allow_affix:
            enemy = apply_wave_affix(enemy)
        return place_spawned_enemy(apply_bounty_bonus(enemy), x, y, target_index)
    elif kind == "flying":
        hp *= 0.9
        speed *= 1.35
        reward += 4
        enemy = Enemy(hp, speed, reward, kind=kind, flying=True, path_index=path_index)
        if allow_affix:
            enemy = apply_wave_affix(enemy)
        return place_spawned_enemy(apply_bounty_bonus(enemy), x, y, target_index)
    elif kind == "armored":
        hp *= 1.35
        speed *= 0.85
        reward += 4
        enemy = Enemy(hp, speed, reward, kind=kind, shield_hits=3, path_index=path_index)
        if allow_affix:
            enemy = apply_wave_affix(enemy)
        return place_spawned_enemy(apply_bounty_bonus(enemy), x, y, target_index)
    elif kind == "boss":
        return create_boss_enemy(path_index)
    elif kind == "commander":
        hp *= 2.6
        speed *= 0.86
        reward += 18
        enemy = Enemy(hp, speed, reward, kind=kind, shield_hits=1, commander=True, path_index=path_index)
        if allow_affix:
            enemy = apply_wave_affix(enemy)
        return place_spawned_enemy(apply_bounty_bonus(enemy), x, y, target_index)

    enemy = Enemy(hp, speed, reward, kind=kind, path_index=path_index)
    if allow_affix:
        enemy = apply_wave_affix(enemy)
    return place_spawned_enemy(apply_bounty_bonus(enemy), x, y, target_index)


def create_boss_enemy(path_index=0):
    boss_tier = wave // 5
    hp = 950 + wave * 190 + boss_tier * 420
    speed = max(35, 58 - boss_tier * 3)
    reward = 75 + boss_tier * 25
    boss_protocol = get_boss_protocol_for_wave(wave)

    if wave == 5:
        return apply_bounty_bonus(Enemy(hp, speed, reward, kind="ogre boss", boss=True, path_index=path_index))
    if wave == 10:
        return apply_bounty_bonus(
            Enemy(
                hp * 1.25,
                speed * 0.9,
                reward + 20,
                kind="ransomware boss",
                shield_hits=6,
                boss=True,
                path_index=path_index,
                boss_protocol=boss_protocol,
            )
        )
    if wave == 15:
        return apply_bounty_bonus(Enemy(hp * 1.1, speed, reward + 25, kind="iron boss", shield_hits=8, boss=True, path_index=path_index))
    if wave == 20:
        return apply_bounty_bonus(Enemy(hp, speed * 0.95, reward + 35, kind="summoner boss", boss=True, death_spawns=12, path_index=path_index))
    if wave == 25:
        return apply_bounty_bonus(Enemy(hp * 1.2, speed * 1.15, reward + 45, kind="sky boss", flying=True, boss=True, path_index=path_index))
    return apply_bounty_bonus(
        Enemy(
            hp * 1.55,
            speed,
            reward + 75,
            kind="final boss",
            shield_hits=8,
            boss=True,
            death_spawns=18,
            path_index=path_index,
            boss_protocol=boss_protocol,
        )
    )


def place_spawned_enemy(enemy, x=None, y=None, target_index=1):
    if x is not None and y is not None:
        enemy.x = x
        enemy.y = y
        enemy.target_index = target_index
    return enemy


def spawn_death_minions(enemy):
    split_children = sum(1 for active_enemy in enemies if active_enemy.is_split_child)
    available_enemy_slots = max(0, MAX_ACTIVE_ENEMIES - len(enemies))
    available_split_slots = max(0, MAX_SPLIT_CHILDREN - split_children)
    spawn_count = min(enemy.death_spawns, available_enemy_slots, available_split_slots)

    for index in range(spawn_count):
        minion = create_enemy("swarm", enemy.x, enemy.y, enemy.target_index, enemy.path_index, allow_affix=False)
        minion.max_hp *= 0.55
        minion.hp = minion.max_hp
        minion.reward = max(0, enemy.reward // 6)
        minion.death_spawns = 0
        minion.affix = None
        minion.is_split_child = True
        minion.radius = 10
        minion.x += math.cos(index) * 10
        minion.y += math.sin(index) * 10
        enemies.append(minion)


def get_upgrade_options(tower):
    if tower is None:
        return []

    cost = tower.upgrade_cost
    if cost is None:
        return []

    if tower.tower_type is None:
        return [
            {
                "tower_type": tower_type,
                "title": data["tiers"][2],
                "cost": cost,
                "description": data["role"],
                "color": data["color"],
                "enabled": money >= cost,
            }
            for tower_type, data in TOWER_TYPES.items()
            if tower_type in ROOT_TOWER_IDS
        ]

    if tower.needs_branch_choice():
        return []

    data = TOWER_TYPES[tower.tower_type]
    branch = tower.branch_data()
    next_level = tower.level + 1
    research_cost = RESEARCH_UPGRADE_COSTS.get(tower.level, 0) if tower.level >= BASE_MAX_TOWER_LEVEL else 0
    min_towers = get_min_towers_for_upgrade(tower.level) if tower.level >= BASE_MAX_TOWER_LEVEL else 1
    if next_level == PARAGON_LEVEL:
        title = data["paragon"]
        description = ""
    elif next_level > PARAGON_LEVEL:
        title = f"Mastery {next_level}"
        description = ""
    else:
        title = tower_tier_name(tower.tower_type, next_level, tower.selected_branch)
        description = tower_tier_description(tower.tower_type, next_level, tower.selected_branch)

    return [
        {
            "tower_type": tower.tower_type,
            "title": title,
            "cost": cost,
            "research_cost": research_cost,
            "min_towers": min_towers,
            "description": description,
            "synergy": branch["synergy"] if branch else None,
            "keystone": branch["keystone"] if branch else None,
            "mastery": branch["mastery"] if branch else None,
            "color": data["color"],
            "enabled": money >= cost and tower.can_upgrade(),
        }
    ]


def get_branch_options(tower):
    if tower is None or not tower.needs_branch_choice():
        return []

    cost = tower.upgrade_cost
    options = []
    for branch_key, branch in BRANCH_DEFINITIONS[tower.tower_type].items():
        options.append(
            {
                "branch_key": branch_key,
                "title": branch["name"],
                "short": branch["short"],
                "role": branch["role"],
                "effect_preview": branch["effect_preview"],
                "focus": FOCUS_LABELS.get(branch["focus"], branch["focus"].title()),
                "synergy": branch["synergy"],
                "keystone": branch["keystone"],
                "mastery": branch["mastery"],
                "cost": cost,
                "color": branch["color"],
                "enabled": money >= cost,
            }
        )
    return options


def get_sell_refund(tower):
    if tower.is_paragon:
        return int(tower.money_spent * PARAGON_SELL_REFUND_RATE)
    return int(tower.money_spent * SELL_REFUND_RATE)


def sell_tower(tower):
    global money, selected_tower

    if tower not in towers:
        return False

    money += get_sell_refund(tower)
    towers.remove(tower)

    if selected_tower == tower:
        selected_tower = None

    return True


def get_shop_button_rects():
    rects = []
    start_x = MAP_WIDTH + 14
    start_y = 126
    button_w = 120
    button_h = 28
    gap = 4
    for index, tower_type in enumerate(current_shop_towers()):
        col = index % 2
        row = index // 2
        rect = pygame.Rect(start_x + col * (button_w + gap), start_y + row * (button_h + gap), button_w, button_h)
        rects.append((rect, tower_type))
    return rects


def current_shop_towers():
    return SHOP_TOWER_ORDER


def get_map_button_rects():
    return []


def get_new_map_button_rect():
    return pygame.Rect(MAP_WIDTH + 14, 552, UI_WIDTH - 28, 30)


def get_pause_button_rect():
    return pygame.Rect(MAP_WIDTH + 14, 76, 90, 28)


def get_speed_button_rects():
    return [
        (pygame.Rect(MAP_WIDTH + 112, 76, 42, 28), 1.0),
        (pygame.Rect(MAP_WIDTH + 160, 76, 42, 28), 2.0),
        (pygame.Rect(MAP_WIDTH + 208, 76, 42, 28), 3.0),
    ]


def get_audio_button_rects():
    return [
        (pygame.Rect(MAP_WIDTH + 14, 260, 120, 22), "sfx"),
        (pygame.Rect(MAP_WIDTH + 142, 260, 120, 22), "music"),
    ]


def get_upgrade_panel_rect():
    return pygame.Rect(MAP_WIDTH + 8, 286, UI_WIDTH - 16, 304)


def get_branch_button_rects(tower):
    panel = get_upgrade_panel_rect()
    rects = []
    for index, option in enumerate(get_branch_options(tower)):
        rect = pygame.Rect(panel.x + 14, panel.y + 112 + index * 35, panel.w - 28, 31)
        rects.append((rect, option))
    return rects


def visible_available_mutations(tower):
    if tower is None or tower.needs_branch_choice() or not tower.can_add_mutation():
        return []
    return tower.available_mutations[: max(0, MUTATION_SLOT_LIMIT - len(tower.mutations))]


def get_mutation_button_rects(tower):
    panel = get_upgrade_panel_rect()
    rects = []
    for index, mutation_key in enumerate(visible_available_mutations(tower)[:2]):
        rect = pygame.Rect(panel.x + 14, panel.y + 104 + index * 40, panel.w - 28, 36)
        rects.append((rect, mutation_key))
    return rects


def get_owned_mutation_badge_rects(tower):
    if tower is None:
        return []

    panel = get_upgrade_panel_rect()
    badge_x = panel.x + 126
    rects = []
    for index, mutation_key in enumerate(tower.mutations[:MUTATION_SLOT_LIMIT]):
        rect = pygame.Rect(badge_x + index * 42, panel.y + 76, 36, 18)
        rects.append((rect, mutation_key))
    return rects


def get_upgrade_button_rects(tower):
    if tower is not None and tower.needs_branch_choice():
        return []

    panel = get_upgrade_panel_rect()
    options = get_upgrade_options(tower)
    rects = []
    mutation_count = len(get_mutation_button_rects(tower))

    if options:
        y = panel.y + 106 + mutation_count * 40
        height = 58 if mutation_count == 0 else 50 if mutation_count == 1 else 32
        rect = pygame.Rect(panel.x + 14, y, panel.w - 28, height)
        rects.append((rect, options[0]))

    return rects


def get_sell_button_rect():
    panel = get_upgrade_panel_rect()
    return pygame.Rect(panel.x + 14, panel.bottom - 44, panel.w - 28, 30)


def handle_upgrade_panel_click(pos):
    global money, research_points

    if selected_tower is None:
        return False

    panel = get_upgrade_panel_rect()
    if not panel.collidepoint(pos):
        return False

    if get_target_button_rect().collidepoint(pos):
        selected_tower.cycle_target_mode()
        return True

    if get_sell_button_rect().collidepoint(pos):
        if sell_tower(selected_tower):
            play_sound("sell", 0.08)
        return True

    for rect, option in get_branch_button_rects(selected_tower):
        if rect.collidepoint(pos):
            if option["enabled"] and selected_tower.choose_branch(option["branch_key"]):
                money -= option["cost"]
                play_sound("upgrade", 0.08)
            return True

    for rect, mutation_key in get_mutation_button_rects(selected_tower):
        if rect.collidepoint(pos):
            if selected_tower.apply_mutation(mutation_key):
                play_sound("upgrade", 0.08)
            return True

    for rect, option in get_upgrade_button_rects(selected_tower):
        if rect.collidepoint(pos):
            if option["enabled"]:
                if selected_tower.upgrade(option["tower_type"]):
                    money -= option["cost"]
                    research_points -= option.get("research_cost", 0)
                    play_sound("upgrade", 0.08)
            return True

    return True


def draw_upgrade_panel():
    if selected_tower is None:
        return

    panel = get_upgrade_panel_rect()
    pygame.draw.rect(screen, (26, 30, 28), panel)
    pygame.draw.rect(screen, (120, 120, 100), panel, 2)

    data = TOWER_TYPES.get(selected_tower.tower_type)
    if selected_tower.is_paragon:
        tower_name = data["paragon"]
    elif selected_tower.selected_branch and selected_tower.level >= BRANCH_UNLOCK_LEVEL:
        tower_name = tower_tier_name(selected_tower.tower_type, selected_tower.level, selected_tower.selected_branch)
    else:
        tower_name = f"{data['label']} Tower" if data else "Basic Tower"
    draw_text(tower_name, panel.x + 14, panel.y + 12, (255, 255, 255))
    if selected_tower.tower_type == "support":
        stat_text = f"L{selected_tower.level} | Mana {int(selected_tower.support_mana)}/{int(selected_tower.support_max_mana)} | Range {int(selected_tower.effective_range())}"
    else:
        stat_text = f"L{selected_tower.level} | DMG {int(selected_tower.damage)} | Range {int(selected_tower.effective_range())}"
    draw_small_text(stat_text, panel.x + 14, panel.y + 38, (210, 210, 190))
    family = data.get("family", data["label"]) if data else "Basic"
    family = family.replace(" Family", "")
    branch = selected_tower.branch_data()
    if branch:
        progress = min(5, max(1, selected_tower.level - BRANCH_UNLOCK_LEVEL + 1))
        focus = FOCUS_LABELS.get(branch["focus"], branch["focus"].title())
        branch_text = f"{branch['short']} {focus} {progress}/5"
    elif selected_tower.needs_branch_choice():
        branch_text = "Pick branch"
    else:
        branch_text = "Branch at L3"
    details = f"{family} | {branch_text} | Traits {len(selected_tower.mutations)}/{MUTATION_SLOT_LIMIT}"
    draw_tiny_text(truncate_text(details, 42), panel.x + 14, panel.y + 64, branch["color"] if branch else (230, 220, 150))
    for rect, mutation_key in get_owned_mutation_badge_rects(selected_tower):
        mutation = MUTATION_TRAITS[mutation_key]
        pygame.draw.rect(screen, (34, 38, 34), rect)
        pygame.draw.rect(screen, mutation["color"], rect, 1)
        draw_tiny_text(mutation["short"], rect.x + 5, rect.y + 3, mutation["color"])
    if selected_tower.tower_type and selected_tower.level >= BASE_MAX_TOWER_LEVEL and selected_tower.level < MAX_TOWER_LEVEL:
        needed = RESEARCH_UPGRADE_COSTS[selected_tower.level]
        min_towers = get_min_towers_for_upgrade(selected_tower.level)
        draw_small_text(
            f"Tech {research_points}/{needed} | Towers {len(towers)}/{min_towers}",
            panel.x + 14,
            panel.y + 94,
            (230, 220, 150),
        )

    branch_buttons = get_branch_button_rects(selected_tower)
    if branch_buttons:
        draw_small_text("Pick Branch", panel.x + 14, panel.y + 92, (245, 235, 180))
        for index, (rect, option) in enumerate(branch_buttons):
            enabled = option["enabled"]
            fill = (34, 44, 38) if enabled else (48, 38, 38)
            outline = option["color"] if enabled else (115, 70, 70)
            text_color = (245, 245, 235) if enabled else (165, 140, 140)
            pygame.draw.rect(screen, fill, rect)
            pygame.draw.rect(screen, outline, rect, 2)
            draw_small_text(f"{index + 1}. {option['title']}", rect.x + 8, rect.y + 7, text_color)
            draw_tiny_text_right(f"${option['cost']}", rect.right - 8, rect.y + 10, text_color)
        draw_target_button()
        draw_sell_button()
        return

    for rect, mutation_key in get_mutation_button_rects(selected_tower):
        mutation = MUTATION_TRAITS[mutation_key]
        pygame.draw.rect(screen, (34, 42, 38), rect)
        pygame.draw.rect(screen, mutation["color"], rect, 2)
        draw_small_text(f"Mutate: {mutation['label']}", rect.x + 8, rect.y + 5, (245, 245, 235))
        description = truncate_text(mutation["description"], 34)
        draw_tiny_text(description, rect.x + 8, rect.y + 22, (215, 220, 200))

    options = get_upgrade_options(selected_tower)
    if not options:
        max_y = panel.y + 112 + len(get_mutation_button_rects(selected_tower)) * 40
        draw_text("MAX LEVEL", panel.x + 72, max_y, (255, 255, 255))
        if selected_tower.tower_type and selected_tower.level >= MAX_TOWER_LEVEL:
            draw_small_text("Mastery capped for now", panel.x + 54, max_y + 33, (190, 190, 180))
        else:
            draw_small_text("No further upgrades available", panel.x + 30, max_y + 33, (190, 190, 180))
        draw_target_button()
        draw_sell_button()
        return

    for rect, option in get_upgrade_button_rects(selected_tower):
        enabled = option["enabled"]
        fill = (42, 48, 44) if enabled else (48, 38, 38)
        outline = option["color"] if enabled else (115, 70, 70)
        text_color = (255, 255, 255) if enabled else (160, 140, 140)

        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, outline, rect, 2)
        draw_small_text(option["title"], rect.x + 10, rect.y + 6, text_color)
        price_text = f"${option['cost']}"
        if option.get("research_cost", 0):
            price_text += f" +{option['research_cost']} Tech"
        draw_small_text_right(price_text, rect.right - 8, rect.y + 6, text_color)
        if rect.h >= 42 and option["description"]:
            description = truncate_text(option["description"], 30)
            draw_small_text(description, rect.x + 10, rect.y + 24, (205, 205, 190) if enabled else text_color)

    draw_sell_button()
    draw_target_button()


def draw_sell_button():
    sell_rect = get_sell_button_rect()
    refund = get_sell_refund(selected_tower)
    pygame.draw.rect(screen, (58, 43, 38), sell_rect)
    pygame.draw.rect(screen, (215, 125, 85), sell_rect, 2)
    draw_small_text(f"Sell +${refund}", sell_rect.x + 10, sell_rect.y + 9, (255, 230, 210))


def draw_target_button():
    rect = get_target_button_rect()
    pygame.draw.rect(screen, (38, 48, 58), rect)
    pygame.draw.rect(screen, (110, 150, 190), rect, 2)
    draw_small_text(f"Target {selected_tower.target_mode.title()}", rect.x + 10, rect.y + 7, (225, 235, 245))


def get_start_wave_button_rect():
    return pygame.Rect(MAP_WIDTH + 14, 34, UI_WIDTH - 28, 34)


def get_target_button_rect():
    panel = get_upgrade_panel_rect()
    return pygame.Rect(panel.x + 14, panel.bottom - 82, panel.w - 28, 30)


def get_endless_button_rect():
    return pygame.Rect(340, 330, 220, 38)


def get_skill_button_rects():
    return [
        (pygame.Rect(292, 382, 150, 34), "money"),
        (pygame.Rect(458, 382, 150, 34), "damage"),
    ]


def get_reward_card_rects():
    if not pending_card_choices:
        return []

    card_w = 180
    card_h = 78
    gap = 20
    total_w = card_w * 3 + gap * 2
    start_x = (MAP_WIDTH - total_w) // 2
    y = 184
    return [
        (pygame.Rect(start_x + index * (card_w + gap), y, card_w, card_h), card_key)
        for index, card_key in enumerate(pending_card_choices[:3])
    ]


def map_seed_value():
    seed = active_map.get("seed")
    if isinstance(seed, int):
        return seed
    return (current_map_index + 1) * 1000


def generate_reward_card_choices(completed_wave):
    rng = random.Random(map_seed_value() * 1009 + completed_wave * 9173)
    card_keys = list(CARD_POOL)
    rng.shuffle(card_keys)
    return card_keys[:3]


def should_offer_reward_cards(completed_wave):
    return completed_wave > 0 and completed_wave % PROTOCOL_REWARD_INTERVAL == 0


def reward_card_effect_text(card_key):
    if card_key == "cpu_cache":
        return "+$60 CPU"
    if card_key == "research_grant":
        return "+2 Tech"
    if card_key == "core_patch":
        return "+4 HP"
    if card_key == "range_patch":
        return "+4% Range"
    if card_key == "damage_patch":
        return "+5% Damage"
    if card_key == "bounty_trace":
        return "+$2 Next Wave"
    return ""


def apply_reward_card(card_key):
    global money, research_points, lives, run_damage_bonus, run_range_bonus
    global next_wave_bounty_bonus, next_wave_bounty_wave, pending_card_choices

    if card_key not in pending_card_choices:
        return False

    if card_key == "cpu_cache":
        money += 60
    elif card_key == "research_grant":
        research_points += 2
    elif card_key == "core_patch":
        lives = min(STARTING_LIVES, lives + 4)
    elif card_key == "range_patch":
        run_range_bonus += 0.04
    elif card_key == "damage_patch":
        run_damage_bonus += 0.05
    elif card_key == "bounty_trace":
        next_wave_bounty_bonus += 2
        next_wave_bounty_wave = wave
    else:
        return False

    pending_card_choices = []
    play_sound("upgrade", 0.08)
    return True


def handle_reward_card_click(pos):
    for rect, card_key in get_reward_card_rects():
        if rect.collidepoint(pos):
            return apply_reward_card(card_key)
    return False


def complete_current_wave():
    global money, research_points, wave, spawned_this_wave, spawn_timer, wave_active, victory
    global next_wave_bounty_bonus, next_wave_bounty_wave, pending_card_choices

    completed_wave = wave
    for tower in towers:
        tower.waves_present += 1
    earned_research = get_research_reward(completed_wave)
    money += START_WAVE_BONUS + wave
    research_points += earned_research
    add_floating_text(MAP_WIDTH // 2 - 30, 90, f"+{earned_research} Tech", (150, 220, 255))
    play_sound("wave_complete", 0.3)

    if next_wave_bounty_wave == completed_wave:
        next_wave_bounty_bonus = 0
        next_wave_bounty_wave = None

    wave += 1
    spawned_this_wave = 0
    spawn_timer = 0
    wave_active = False

    if wave > MAX_WAVE and not endless_mode:
        victory = True
        pending_card_choices = []
    elif should_offer_reward_cards(completed_wave):
        pending_card_choices = generate_reward_card_choices(completed_wave)
    else:
        pending_card_choices = []


def start_wave():
    global wave_active, spawn_timer, spawned_this_wave, spawn_path_index

    if not wave_active and not game_over and not victory and not pending_card_choices:
        wave_active = True
        spawn_timer = 0
        spawned_this_wave = 0
        spawn_path_index = 0
        play_wave_start_sound()
        return True
    return False


def handle_command_click(pos):
    global endless_mode, stars, starting_money_bonus_level, tower_damage_bonus_level
    global victory, wave, wave_active, spawn_timer, spawned_this_wave
    global selected_build_type, selected_tower, paused, game_speed
    global sfx_enabled, music_enabled

    if get_start_wave_button_rect().collidepoint(pos):
        start_wave()
        return True

    for rect, tower_type in get_shop_button_rects():
        if rect.collidepoint(pos):
            selected_build_type = tower_type
            selected_tower = None
            return True

    if get_pause_button_rect().collidepoint(pos):
        paused = not paused
        return True

    for rect, speed in get_speed_button_rects():
        if rect.collidepoint(pos):
            game_speed = speed
            return True

    for rect, key in get_audio_button_rects():
        if rect.collidepoint(pos):
            if key == "sfx":
                sfx_enabled = not sfx_enabled
            else:
                music_enabled = not music_enabled
                update_music_state()
            return True

    if selected_tower is None and get_new_map_button_rect().collidepoint(pos):
        if can_change_map():
            generate_new_active_map()
        selected_build_type = None
        return True

    if victory and get_endless_button_rect().collidepoint(pos):
        endless_mode = True
        victory = False
        wave = max(wave, MAX_WAVE + 1)
        wave_active = True
        spawn_timer = 0
        spawned_this_wave = 0
        return True

    if game_over or victory:
        for rect, key in get_skill_button_rects():
            if rect.collidepoint(pos) and stars > 0:
                stars -= 1
                if key == "money":
                    starting_money_bonus_level += 1
                else:
                    tower_damage_bonus_level += 1
                return True

    return False


def award_run_stars():
    global stars, run_stars_awarded

    if run_stars_awarded:
        return

    stars += 3 if victory else 1
    run_stars_awarded = True


def wave_color(kind):
    colors = {
        "normal": (210, 210, 190),
        "fast": (235, 95, 190),
        "tank": (185, 115, 80),
        "swarm": (230, 135, 80),
        "shield": (185, 185, 205),
        "flying": (190, 130, 245),
        "armored": (150, 150, 165),
        "boss": (235, 80, 80),
    }
    return colors.get(kind, (210, 210, 190))


def draw_tooltip(lines, y):
    x = MAP_WIDTH + 12
    width = UI_WIDTH - 24
    height = 18 + len(lines) * 16
    rect = pygame.Rect(x, min(y, HEIGHT - height - 8), width, height)
    pygame.draw.rect(screen, (20, 23, 22), rect)
    pygame.draw.rect(screen, (180, 180, 145), rect, 1)
    for index, line in enumerate(lines):
        color = (255, 255, 235) if index == 0 else (215, 215, 195)
        draw_tiny_text(line, rect.x + 8, rect.y + 8 + index * 16, color)


def mutation_tooltip_lines(mutation_key, owned=False):
    mutation = MUTATION_TRAITS[mutation_key]
    lines = [f"Mutation: {mutation['label']}"]
    lines.extend(wrap_text(mutation["description"], 32))
    lines.append("Active on this tower" if owned else "Click to add this trait")
    return lines


def draw_sidebar_background():
    pygame.draw.rect(screen, (20, 24, 22), (MAP_WIDTH, 0, UI_WIDTH, HEIGHT))
    pygame.draw.line(screen, (75, 82, 70), (MAP_WIDTH, 0), (MAP_WIDTH, HEIGHT), 2)
    draw_text("Signal Defense", MAP_WIDTH + 14, 8, (245, 245, 230))


def draw_start_and_speed_controls():
    rect = get_start_wave_button_rect()
    start_enabled = not wave_active and not game_over and not victory and not pending_card_choices
    fill = (42, 70, 45) if start_enabled else (46, 48, 44)
    outline = (105, 210, 120) if start_enabled else (95, 95, 85)
    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, outline, rect, 2)
    label = "Start Wave" if not pending_card_choices else "Pick Bonus"
    draw_small_text(label, rect.x + 64, rect.y + 9, (245, 255, 245) if start_enabled else (155, 155, 145))

    pause_rect = get_pause_button_rect()
    pygame.draw.rect(screen, (42, 48, 58), pause_rect)
    pygame.draw.rect(screen, (110, 150, 190), pause_rect, 2)
    draw_small_text("Resume" if paused else "Pause", pause_rect.x + 16, pause_rect.y + 6, (225, 235, 245))

    for speed_rect, speed in get_speed_button_rects():
        active = game_speed == speed
        pygame.draw.rect(screen, (54, 58, 42) if active else (36, 38, 34), speed_rect)
        pygame.draw.rect(screen, (220, 200, 95) if active else (95, 95, 80), speed_rect, 2)
        draw_small_text(f"{int(speed)}x", speed_rect.x + 10, speed_rect.y + 6, (245, 235, 180))

    for audio_rect, key in get_audio_button_rects():
        active = sfx_enabled if key == "sfx" else music_enabled
        pygame.draw.rect(screen, (38, 52, 45) if active else (48, 38, 38), audio_rect)
        pygame.draw.rect(screen, (100, 190, 125) if active else (150, 85, 85), audio_rect, 2)
        label = "SFX ON" if key == "sfx" and active else "SFX OFF" if key == "sfx" else "Music ON" if active else "Music OFF"
        draw_tiny_text(label, audio_rect.x + 12, audio_rect.y + 5, (235, 240, 220))


def draw_reward_cards():
    if not pending_card_choices:
        return

    overlay = pygame.Surface((MAP_WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 8, 10, 138))
    screen.blit(overlay, (0, 0))

    draw_text("Pick Bonus", 372, 132, (245, 250, 255))
    for rect, card_key in get_reward_card_rects():
        card = CARD_POOL[card_key]
        pygame.draw.rect(screen, (24, 31, 34), rect)
        pygame.draw.rect(screen, card["color"], rect, 2)
        draw_small_text(card["label"], rect.x + 12, rect.y + 12, (255, 255, 245))
        draw_small_text(reward_card_effect_text(card_key), rect.x + 12, rect.y + 40, card["color"])


def draw_role_icon(icon_key, x, y, enabled=True):
    color = ROLE_ICON_COLORS.get(icon_key, (220, 220, 210))
    if not enabled:
        color = blend_color(color, (85, 75, 75), 0.58)

    if icon_key == "fast":
        for offset in (0, 4, 8):
            pygame.draw.line(screen, color, (x - 5, y - 4 + offset), (x + 6, y - 4 + offset), 2)
    elif icon_key == "single":
        pygame.draw.circle(screen, color, (x, y), 6, 2)
        pygame.draw.line(screen, color, (x - 8, y), (x + 8, y), 1)
        pygame.draw.line(screen, color, (x, y - 8), (x, y + 8), 1)
    elif icon_key == "aoe":
        pygame.draw.circle(screen, color, (x, y), 7, 2)
        pygame.draw.circle(screen, color, (x, y), 3, 1)
    elif icon_key == "slow":
        pygame.draw.circle(screen, color, (x, y), 6, 2)
        pygame.draw.line(screen, color, (x - 7, y - 7), (x + 7, y + 7), 1)
        pygame.draw.line(screen, color, (x + 7, y - 7), (x - 7, y + 7), 1)
    elif icon_key == "dot":
        pygame.draw.polygon(screen, color, [(x, y - 8), (x + 7, y), (x + 3, y + 7), (x - 5, y + 7), (x - 7, y)])
        pygame.draw.circle(screen, blend_color(color, (255, 255, 255), 0.25), (x + 1, y + 2), 2)
    elif icon_key == "support":
        pygame.draw.circle(screen, color, (x, y), 7, 1)
        pygame.draw.line(screen, color, (x - 5, y), (x + 5, y), 2)
        pygame.draw.line(screen, color, (x, y - 5), (x, y + 5), 2)
    elif icon_key == "air":
        pygame.draw.polygon(screen, color, [(x, y - 8), (x + 8, y + 6), (x, y + 2), (x - 8, y + 6)])
    elif icon_key == "hold":
        pygame.draw.rect(screen, color, (x - 7, y - 5, 14, 10), 2)
        pygame.draw.line(screen, color, (x - 5, y + 6), (x - 5, y + 9), 2)
        pygame.draw.line(screen, color, (x + 5, y + 6), (x + 5, y + 9), 2)
    elif icon_key == "armor":
        pygame.draw.polygon(screen, color, [(x, y - 8), (x + 7, y - 4), (x + 5, y + 5), (x, y + 9), (x - 5, y + 5), (x - 7, y - 4)], 2)
    else:
        pygame.draw.circle(screen, color, (x, y), 5)


def draw_tower_role_icons(tower_type, x, y, enabled=True):
    for index, icon_key in enumerate(TOWER_ROLE_ICONS.get(tower_type, ())[:3]):
        draw_role_icon(icon_key, x + index * 17, y, enabled)


def draw_tower_shop():
    draw_small_text("Build Towers", MAP_WIDTH + 14, 108, (235, 235, 220))

    for rect, tower_type in get_shop_button_rects():
        data = TOWER_TYPES[tower_type]
        selected = selected_build_type == tower_type
        affordable = money >= SHOP_COSTS[tower_type]
        fill = (38, 52, 42) if selected else (33, 38, 35)
        if not affordable:
            fill = (48, 38, 38)
        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, data["color"] if affordable else (120, 70, 70), rect, 2)
        sprite = images.get("towers", {}).get(tower_type, {}).get("idle")
        if sprite:
            mini = get_scaled_sprite(sprite, (24, 24))
            draw_sprite_centered(screen, mini, rect.x + 17, rect.y + 16)
            text_x = rect.x + 32
        else:
            text_x = rect.x + 7
        draw_tiny_text(data["label"], text_x, rect.y + 4, (245, 245, 235) if affordable else (165, 140, 140))
        draw_tiny_text(f"${SHOP_COSTS[tower_type]}", rect.right - 38, rect.y + 15, (225, 225, 205) if affordable else (150, 130, 130))


def draw_wave_timeline():
    y = 306 if selected_tower is None else 202
    draw_small_text("Wave Timeline", MAP_WIDTH + 14, y, (235, 235, 220))
    for index in range(6):
        preview_wave = wave + index
        row_y = y + 24 + index * 22
        kind = get_wave_enemy_kind(preview_wave)
        bosses = get_boss_count_for_wave(preview_wave)
        commanders = get_commander_count_for_wave(preview_wave)
        modifier = get_wave_modifier_data(preview_wave)
        color = wave_color("boss" if bosses else kind)
        pygame.draw.circle(screen, color, (MAP_WIDTH + 24, row_y + 8), 6)
        if modifier:
            pygame.draw.circle(screen, modifier["color"], (MAP_WIDTH + 24, row_y + 8), 8, 1)
        label = get_wave_label(preview_wave)
        if bosses:
            label += f" Bx{bosses}"
        if get_boss_protocol_for_wave(preview_wave) == "ransomware":
            label += " Lock"
        if commanders:
            label += " CMD"
        prefix = "Now" if index == 0 else f"W{preview_wave}"
        draw_tiny_text(f"{prefix}: {label}", MAP_WIDTH + 38, row_y + 1, (230, 230, 210))
        _, recommended = get_wave_recommendation(preview_wave)
        for icon_index, tower_type in enumerate(recommended[:2]):
            sprite = images.get("towers", {}).get(tower_type, {}).get("idle")
            if sprite:
                mini = get_scaled_sprite(sprite, (18, 18))
                draw_sprite_centered(screen, mini, MAP_WIDTH + 218 + icon_index * 20, row_y + 8)


def draw_wave_warning_panel():
    if wave_active or game_over or victory:
        return

    recommendations, tower_types = get_wave_recommendation(wave)
    modifier = get_wave_modifier_data(wave)
    panel = pygame.Rect(285, 16, 390, 72)
    pygame.draw.rect(screen, (24, 29, 28), panel)
    pygame.draw.rect(screen, modifier["color"] if modifier else (220, 200, 100), panel, 2)
    title = f"Next Traffic: {get_wave_label()}"
    if get_commander_count_for_wave(wave):
        title += " + Commander"
    draw_small_text(title, panel.x + 12, panel.y + 8, (255, 240, 170))
    for index, line in enumerate(recommendations):
        draw_tiny_text(line, panel.x + 12, panel.y + 34 + index * 16, (230, 230, 210))
    for index, tower_type in enumerate(tower_types):
        sprite = images.get("towers", {}).get(tower_type, {}).get("idle")
        if sprite:
            mini = get_scaled_sprite(sprite, (30, 30))
            draw_sprite_centered(screen, mini, panel.right - 84 + index * 28, panel.y + 39)

    if money >= 1000:
        pulse = 120 + int(80 * abs(math.sin(pygame.time.get_ticks() * 0.006)))
        draw_small_text("Spend money before starting!", panel.x + 98, panel.bottom - 22, (255, pulse, pulse))


def draw_boss_health_bar():
    bosses = active_bosses()
    if not bosses:
        return

    total_hp = sum(max(0, boss.hp) for boss in bosses)
    total_max = sum(boss.max_hp for boss in bosses)
    if total_max <= 0:
        return

    primary = bosses[0]
    bar = pygame.Rect(295, 94, 360, 22)
    ratio = max(0, min(1, total_hp / total_max))
    pygame.draw.rect(screen, (34, 22, 22), bar)
    pygame.draw.rect(screen, (190, 55, 55), (bar.x, bar.y, int(bar.w * ratio), bar.h))
    pygame.draw.rect(screen, (255, 205, 100), bar, 2)
    draw_small_text(primary.kind.title(), bar.x + 8, bar.y - 24, (255, 225, 150))
    tags = []
    if primary.shield_hits > 0:
        tags.append("Shield")
    if primary.flying:
        tags.append("Flying")
    if primary.death_spawns:
        tags.append("Summoner")
    if primary.boss_protocol == "ransomware":
        tags.append("Ransomware")
    if tags:
        draw_tiny_text(" / ".join(tags), bar.right - 110, bar.y - 18, (235, 220, 190))
    draw_tiny_text(f"{int(total_hp)}/{int(total_max)}", bar.x + 136, bar.y + 5, (255, 245, 230))


def draw_map_selector():
    draw_small_text("Map", MAP_WIDTH + 14, 488, (235, 235, 220))
    locked = not can_change_map()
    if locked:
        draw_tiny_text("Locked after building or starting", MAP_WIDTH + 58, 491, (155, 155, 140))

    seed_text = str(active_map.get("seed", "fallback"))
    draw_tiny_text(active_map.get("name", "Random Road"), MAP_WIDTH + 14, 516, (235, 245, 225))
    draw_tiny_text(f"Seed: {seed_text}", MAP_WIDTH + 14, 536, (190, 200, 180))

    rect = get_new_map_button_rect()
    fill = (38, 62, 44) if not locked else (32, 36, 33)
    outline = (105, 200, 120) if not locked else (90, 95, 82)
    color = (235, 245, 225) if not locked else (145, 145, 132)
    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, outline, rect, 2)
    draw_tiny_text("New Random Map", rect.x + 62, rect.y + 9, color)


def draw_sidebar_tooltips():
    mouse_pos = get_game_mouse_pos()

    for rect, tower_type in get_shop_button_rects():
        if rect.collidepoint(mouse_pos):
            data = TOWER_TYPES[tower_type]
            summary = TOWER_TOOLTIP_SUMMARY.get(tower_type, (data["role"], f"Best: {data['good_vs']}", f"Weak: {data['weakness']}"))
            lines = [
                f"{data['label']} - ${SHOP_COSTS[tower_type]}",
                summary[0],
                f"{summary[1]}   {summary[2]}",
            ]
            draw_tooltip(lines, 232)
            return

    if selected_tower:
        for rect, option in get_branch_button_rects(selected_tower):
            if rect.collidepoint(mouse_pos):
                lines = [
                    f"{option['title']} - ${option['cost']}",
                    option["role"],
                    option["effect_preview"],
                ]
                lines.append("Click to choose" if option["enabled"] else "Need money")
                draw_tooltip(lines, rect.y - 72)
                return

        for rect, mutation_key in get_owned_mutation_badge_rects(selected_tower):
            if rect.collidepoint(mouse_pos):
                draw_tooltip(mutation_tooltip_lines(mutation_key, owned=True), rect.y + 26)
                return

        for rect, mutation_key in get_mutation_button_rects(selected_tower):
            if rect.collidepoint(mouse_pos):
                draw_tooltip(mutation_tooltip_lines(mutation_key), rect.y - 82)
                return

        for rect, option in get_upgrade_button_rects(selected_tower):
            if rect.collidepoint(mouse_pos):
                cost_line = f"Cost: ${option['cost']}"
                if option.get("research_cost", 0):
                    cost_line += f" + {option['research_cost']} Tech"
                lines = [option["title"], cost_line]
                if option["description"]:
                    lines.append(option["description"])
                if not option["enabled"]:
                    lines.append("Need money, Tech, or towers")
                draw_tooltip(lines, rect.y - 86)
                return


def draw_command_ui():
    draw_sidebar_background()
    draw_start_and_speed_controls()
    draw_tower_shop()
    if selected_tower is None:
        draw_wave_timeline()
        draw_map_selector()


def draw_end_options():
    if not (game_over or victory):
        return

    award_run_stars()
    draw_text(f"Stars: {stars}", 390, 300, (255, 235, 120))

    if victory:
        rect = get_endless_button_rect()
        pygame.draw.rect(screen, (38, 52, 70), rect)
        pygame.draw.rect(screen, (110, 165, 230), rect, 2)
        draw_small_text("Continue Endless", rect.x + 50, rect.y + 10, (235, 245, 255))

    for rect, key in get_skill_button_rects():
        pygame.draw.rect(screen, (42, 45, 38), rect)
        pygame.draw.rect(screen, (180, 165, 90), rect, 2)
        if key == "money":
            label = f"+$25 Start L{starting_money_bonus_level}"
        else:
            label = f"+5% Damage L{tower_damage_bonus_level}"
        draw_small_text(label, rect.x + 8, rect.y + 9, (245, 235, 180))


def reset_game():
    global money, lives, score, research_points, wave, game_over, victory
    global enemies, towers, projectiles, effects
    global spawn_timer, spawned_this_wave, wave_active, selected_tower
    global endless_mode, run_stars_awarded, selected_build_type, paused, game_speed, spawn_path_index
    global screen_shake_timer, screen_shake_strength, boss_warning_timer
    global pending_card_choices, run_damage_bonus, run_range_bonus, next_wave_bounty_bonus, next_wave_bounty_wave

    money = STARTING_MONEY + starting_money_bonus_level * 25
    lives = STARTING_LIVES
    score = 0
    research_points = 0
    wave = 1
    game_over = False
    victory = False

    enemies = []
    towers = []
    projectiles = []
    effects = []

    spawn_timer = 0
    spawned_this_wave = 0
    wave_active = False
    selected_tower = None
    selected_build_type = None
    paused = False
    game_speed = 1.0
    generate_new_active_map()
    screen_shake_timer = 0
    screen_shake_strength = 0
    boss_warning_timer = 0
    pending_card_choices = []
    run_damage_bonus = 0.0
    run_range_bonus = 0.0
    next_wave_bounty_bonus = 0
    next_wave_bounty_wave = None
    endless_mode = False
    run_stars_awarded = False
    particle_manager.clear()


async def run_async(argv=None, exit_on_quit=False):
    global window_width, window_height, selected_tower, selected_build_type
    global sfx_enabled, music_enabled, screen_shake_timer, screen_shake_strength, boss_warning_timer
    global money, research_points, wave, spawned_this_wave, spawn_timer, wave_active
    global victory, game_over, lives, score
    global render_options, particle_manager, renderer_backend

    running = True
    if argv is None and is_web_runtime():
        argv = []
    render_options = parse_runtime_options(argv)
    particle_manager = ParticleManager(render_options.max_particles)
    renderer_backend = make_renderer(render_options, (WIDTH, HEIGHT), "Signal Defense v0.1")
    window_width, window_height = renderer_backend.window_size
    init_images()
    init_sounds()
    update_music_state()
    update_window_transform()

    while running:
        frame_dt = min(clock.tick(60) / 1000, 0.05)
        dt = 0 if paused else frame_dt * game_speed
        if screen_shake_timer > 0:
            screen_shake_timer = max(0, screen_shake_timer - frame_dt)
            if screen_shake_timer == 0:
                screen_shake_strength = 0
        if boss_warning_timer > 0:
            boss_warning_timer = max(0, boss_warning_timer - frame_dt)
        update_music_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                renderer_backend.resize((event.w, event.h))
                window_width, window_height = renderer_backend.window_size
                update_window_transform()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_m:
                    sfx_enabled = not (sfx_enabled or music_enabled)
                    music_enabled = sfx_enabled
                    update_music_state()
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3) and selected_tower:
                    branch_index = event.key - pygame.K_1
                    branch_options = get_branch_options(selected_tower)
                    if branch_index < len(branch_options):
                        option = branch_options[branch_index]
                        if option["enabled"] and selected_tower.choose_branch(option["branch_key"]):
                            money -= option["cost"]
                            play_sound("upgrade", 0.08)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                selected_tower = None
                selected_build_type = None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mouse_in_game_area(event.pos):
                    mx, my = get_game_mouse_pos()
                    if handle_reward_card_click((mx, my)):
                        continue
                    if pending_card_choices:
                        continue
                    if handle_command_click((mx, my)):
                        continue

                    if game_over or victory:
                        continue

                    if handle_upgrade_panel_click((mx, my)):
                        continue

                    clicked_tower = get_tower_at((mx, my))

                    if clicked_tower:
                        selected_tower = clicked_tower
                    else:
                        if can_place_tower((mx, my)):
                            sx, sy = get_build_site_at((mx, my))
                            cost = SHOP_COSTS[selected_build_type]
                            selected_tower = Tower(sx, sy, selected_build_type, cost)
                            towers.append(selected_tower)
                            money -= cost
                            selected_build_type = None
                            play_sound("build", 0.08)
                        else:
                            selected_tower = None

        if not game_over and not victory and not paused:
            enemies_per_wave = get_enemies_per_wave()
            spawn_interval = get_spawn_interval()

            if wave_active:
                spawn_timer += dt

            if wave_active and spawned_this_wave < enemies_per_wave:
                if spawn_timer >= spawn_interval:
                    if spawn_enemy():
                        spawned_this_wave += 1
                        spawn_timer = 0
                    else:
                        spawn_timer = 0

            if wave_active and spawned_this_wave >= enemies_per_wave and len(enemies) == 0:
                complete_current_wave()

            update_commander_auras()

            for enemy in enemies[:]:
                enemy.update(dt)

                if enemy.reached_end:
                    enemies.remove(enemy)
                    lives -= enemy.leak_damage
                    play_sound("leak", 0.2)
                    if lives <= 0:
                        game_over = True

                elif enemy.hp <= 0:
                    enemies.remove(enemy)
                    award_enemy_death_credit(enemy)
                    if enemy.death_spawns:
                        spawn_death_minions(enemy)
                    money += enemy.reward
                    add_floating_text(enemy.x - 8, enemy.y - 32, f"+${enemy.reward}", (245, 225, 120))
                    play_sound("boss_death" if enemy.boss else "death", 0.04)
                    if enemy.boss:
                        trigger_screen_shake(0.25, 6)
                    score += 10

            for tower in towers:
                tower.update(dt)

            for projectile in projectiles[:]:
                projectile.update(dt)
                if projectile.dead:
                    projectiles.remove(projectile)

            for effect in effects[:]:
                effect.update(dt)
                if effect.dead:
                    effects.remove(effect)

            if render_options.enable_particles:
                particle_manager.update(dt)

            evaluate_all_mutations()

        screen.fill((12, 14, 12))

        draw_terrain()
        draw_path()
        draw_build_preview()

        for tower in towers:
            tower.draw()

        if selected_tower in towers:
            selected_rect = build_rect_for_site((selected_tower.x, selected_tower.y))
            pygame.draw.rect(screen, (255, 235, 120), selected_rect, 3)
            data = TOWER_TYPES.get(selected_tower.tower_type)
            range_color = data["range_color"] if data else (255, 235, 120)
            pygame.draw.circle(screen, range_color, (selected_tower.x, selected_tower.y), int(selected_tower.effective_range()), 1)

        for enemy in enemies:
            enemy.draw()

        for projectile in projectiles:
            projectile.draw()

        for effect in effects:
            effect.draw()

        if render_options.enable_particles:
            particle_manager.draw(screen)

        draw_text(f"CPU: ${money}", 15, 15)
        draw_text(f"HP: {lives}", 150, 15)
        draw_text(f"Wave: {wave}/{MAX_WAVE}", 250, 15)
        draw_text(f"Tech: {research_points}", 390, 15)
        draw_small_text(
            f"Wave type: {get_wave_label()}",
            15,
            45,
            (210, 210, 190),
        )
        draw_wave_warning_panel()
        draw_boss_health_bar()
        if boss_warning_timer > 0:
            draw_text("BOSS INCOMING", 375, 126, (255, 110, 90))

        draw_command_ui()
        draw_upgrade_panel()
        draw_sidebar_tooltips()
        draw_reward_cards()

        if game_over:
            draw_text("GAME OVER - Press R to restart", 320, 280, (255, 80, 80))

        if victory:
            draw_text("YOU WIN - Press R to restart", 330, 280, (80, 255, 120))

        draw_end_options()

        window_width, window_height = renderer_backend.window_size
        update_window_transform()
        shake_x = 0
        shake_y = 0
        if render_options.enable_screen_shake and screen_shake_timer > 0 and screen_shake_strength > 0:
            ticks = pygame.time.get_ticks()
            shake_x = int(math.sin(ticks * 0.09) * screen_shake_strength)
            shake_y = int(math.cos(ticks * 0.11) * screen_shake_strength)
        renderer_backend.present(screen, scale, offset_x, offset_y, shake_x, shake_y, render_options.enable_glow)
        await asyncio.sleep(0)

    if renderer_backend is not None:
        renderer_backend.close()
    pygame.quit()
    if exit_on_quit:
        sys.exit()


def run(argv=None):
    try:
        asyncio.run(run_async(argv, exit_on_quit=True))
    except SystemExit:
        raise
    except Exception as exc:
        write_current_crash_log(exc)
        raise


if __name__ == "__main__":
    run()
