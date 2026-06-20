import math
import wave
from array import array
from pathlib import Path

import pygame


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def ensure_dirs():
    for path in [
        "sprites/towers",
        "sprites/enemies",
        "sprites/terrain",
        "sprites/projectiles",
        "sprites/effects",
        "sounds/towers",
        "sounds/enemies",
        "sounds/ui",
        "sounds/music",
    ]:
        (ASSETS / path).mkdir(parents=True, exist_ok=True)


def save_surface(surface, relative_path):
    pygame.image.save(surface, ASSETS / relative_path)


def shadow(surface, center, radius):
    pygame.draw.ellipse(surface, (0, 0, 0, 90), (center[0] - radius, center[1] + radius // 2, radius * 2, radius // 2))


def tower_sprite(tower_type, color, accent, firing=False, frame=0):
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    bob = 1 if frame % 2 else 0
    shadow(surface, (24, 26), 16)
    if firing:
        pygame.draw.circle(surface, (*accent, 70), (24, 24), 22)
    pygame.draw.circle(surface, color, (24, 13 - bob), 7)
    pygame.draw.rect(surface, color, (15, 20 - bob, 18, 17))
    pygame.draw.rect(surface, tuple(max(0, c - 45) for c in color), (16, 34, 16, 6))
    pygame.draw.line(surface, (35, 35, 35), (19, 36), (14, 43), 3)
    pygame.draw.line(surface, (35, 35, 35), (29, 36), (34, 43), 3)

    flash = (255, 240, 130) if firing else accent
    if tower_type == "archer":
        pygame.draw.arc(surface, (100, 62, 28), (4, 8, 24, 32), -1.25, 1.2, 3)
        pygame.draw.line(surface, (235, 210, 145), (9, 25), (39, 16), 2)
        if firing:
            pygame.draw.line(surface, flash, (36, 16), (47, 13), 2)
    elif tower_type == "sniper":
        pygame.draw.line(surface, (35, 35, 38), (18, 22), (44, 15), 5)
        pygame.draw.circle(surface, accent, (32, 18), 3)
        if firing:
            pygame.draw.line(surface, flash, (42, 15), (48, 13), 2)
    elif tower_type == "machine_gun":
        pygame.draw.rect(surface, (42, 42, 42), (25, 16, 19, 8))
        pygame.draw.circle(surface, (25, 25, 25), (44, 20), 4)
        if firing:
            pygame.draw.circle(surface, flash, (46, 20), 5)
    elif tower_type == "cannon":
        pygame.draw.rect(surface, (54, 45, 38), (22, 13, 22, 12))
        pygame.draw.circle(surface, (85, 75, 70), (43, 19), 6)
        if firing:
            pygame.draw.circle(surface, flash, (46, 19), 7)
    elif tower_type == "frost":
        pygame.draw.line(surface, (200, 245, 255), (9, 8), (39, 36), 4)
        pygame.draw.circle(surface, accent, (40, 37), 6)
        if firing:
            pygame.draw.circle(surface, (230, 255, 255), (40, 37), 10, 2)
    elif tower_type == "tesla":
        pygame.draw.line(surface, accent, (24, 3), (15, 22), 4)
        pygame.draw.line(surface, accent, (15, 22), (33, 22), 4)
        pygame.draw.line(surface, accent, (33, 22), (22, 42), 4)
        if firing:
            pygame.draw.circle(surface, (255, 255, 170), (24, 22), 18, 2)
    elif tower_type == "poison":
        pygame.draw.circle(surface, (42, 95, 48), (34, 16), 7)
        pygame.draw.rect(surface, (48, 105, 52), (29, 18, 10, 18))
        pygame.draw.circle(surface, accent, (35, 13), 3)
        if firing:
            pygame.draw.circle(surface, (165, 255, 120), (38, 13), 7, 2)
    elif tower_type == "barracks":
        pygame.draw.rect(surface, (130, 95, 55), (3, 25, 13, 18))
        pygame.draw.rect(surface, (130, 95, 55), (32, 25, 13, 18))
        pygame.draw.line(surface, (220, 220, 230), (9, 24), (9, 8), 2)
        pygame.draw.line(surface, (220, 220, 230), (38, 24), (38, 8), 2)
    elif tower_type == "flame":
        pygame.draw.polygon(surface, (120, 48, 32), [(29, 13), (45, 20), (29, 27)])
        pygame.draw.polygon(surface, accent, [(32, 14), (46, 20), (32, 26)])
        if firing:
            pygame.draw.polygon(surface, (255, 220, 90), [(37, 12), (48, 20), (37, 28)])
    elif tower_type == "mortar":
        pygame.draw.rect(surface, (58, 55, 50), (19, 15, 13, 22))
        pygame.draw.line(surface, (86, 78, 68), (25, 16), (42, 6), 7)
        pygame.draw.circle(surface, (42, 38, 34), (43, 6), 5)
        if firing:
            pygame.draw.circle(surface, (120, 110, 95), (43, 6), 8, 2)
    elif tower_type == "support":
        pygame.draw.line(surface, (80, 60, 30), (9, 42), (9, 5), 3)
        pygame.draw.polygon(surface, accent, [(10, 5), (42, 13), (10, 23)])
    elif tower_type == "gold":
        pygame.draw.circle(surface, accent, (36, 16), 8)
        pygame.draw.circle(surface, (135, 100, 32), (36, 16), 8, 2)
        pygame.draw.line(surface, (255, 245, 160), (36, 10), (36, 22), 2)
        if firing:
            pygame.draw.circle(surface, (255, 250, 170), (36, 16), 12, 2)
    return surface


def enemy_sprite(kind, color, boss=False, flying=False, frame=0):
    size = 64 if boss else 32
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    radius = 22 if boss else 12
    wobble = 1 if frame == 1 else -1 if frame == 2 else 0
    if frame == 3:
        color = tuple(min(255, c + 70) for c in color)
    shadow(surface, (center, center + 2), radius)
    body_radius = radius - 5 if kind == "split_child" else radius
    body_rect = pygame.Rect(center - body_radius, center - body_radius + wobble, body_radius * 2, body_radius * 2)

    if kind in ("tank", "armored") or boss:
        pygame.draw.rect(surface, color, body_rect, border_radius=5 if boss else 3)
        pygame.draw.rect(surface, tuple(max(0, c - 45) for c in color), body_rect, 2, border_radius=5 if boss else 3)
    else:
        pygame.draw.circle(surface, color, (center, center + wobble), body_radius)
        pygame.draw.circle(surface, tuple(min(255, c + 45) for c in color), (center - body_radius // 3, center - body_radius // 3), max(3, body_radius // 3))

    eye_y = center - 2 + wobble
    pygame.draw.circle(surface, (35, 35, 35), (center - body_radius // 3, eye_y), 2)
    pygame.draw.circle(surface, (35, 35, 35), (center + body_radius // 3, eye_y), 2)

    if kind == "normal":
        pygame.draw.line(surface, (215, 215, 185), (center + 5, center + 4), (center + 13, center + 12), 2)
    elif kind == "fast":
        pygame.draw.line(surface, (245, 230, 245), (3, center + 6), (11, center + 5), 2)
        pygame.draw.line(surface, (245, 230, 245), (2, center + 11), (10, center + 10), 2)
        pygame.draw.line(surface, (40, 35, 38), (center - 4, center + 9), (center - 9, center + 16), 2)
        pygame.draw.line(surface, (40, 35, 38), (center + 5, center + 9), (center + 11, center + 15), 2)
    elif kind in ("swarm", "split_child"):
        pygame.draw.circle(surface, tuple(min(255, c + 35) for c in color), (center - 8, center + 8), 4)
        pygame.draw.circle(surface, tuple(min(255, c + 20) for c in color), (center + 8, center + 8), 4)
    elif kind == "tank":
        pygame.draw.rect(surface, (95, 62, 42), (center - 9, center - 11, 18, 5), border_radius=2)
        pygame.draw.line(surface, (70, 45, 35), (center - 12, center + 12), (center + 12, center + 12), 3)
    if kind in ("shield", "armored") or boss:
        pygame.draw.circle(surface, (225, 225, 245), (center, center), radius + 4, 2)
    if kind == "shield":
        shield_points = [(center + 1, center - 13), (center + 14, center - 6), (center + 9, center + 12), (center + 1, center + 17), (center - 7, center + 12), (center - 12, center - 6)]
        pygame.draw.polygon(surface, (210, 220, 238), shield_points)
        pygame.draw.polygon(surface, (80, 90, 110), shield_points, 2)
    if kind == "armored":
        pygame.draw.rect(surface, (190, 195, 210), (center - 10, center - 16, 20, 7), border_radius=2)
        pygame.draw.line(surface, (80, 85, 95), (center - 10, center - 9), (center + 10, center - 9), 2)
    if kind == "shield_cracked":
        pygame.draw.circle(surface, (225, 225, 245), (center, center), radius + 4, 2)
        pygame.draw.line(surface, (45, 45, 65), (center - 6, center - 10), (center + 2, center + 1), 2)
        pygame.draw.line(surface, (45, 45, 65), (center + 2, center + 1), (center - 3, center + 12), 2)
    if flying:
        pygame.draw.arc(surface, (230, 220, 255), (center - radius - 7, center - 12, radius, 18), 2.8, 6.0, 3)
        pygame.draw.arc(surface, (230, 220, 255), (center + 7, center - 12, radius, 18), 3.4, 6.4, 3)
    if boss:
        pygame.draw.circle(surface, (255, 210, 90), (center, center), radius + 9, 2)
        pygame.draw.polygon(surface, (255, 210, 90), [(center - 14, center - 24), (center - 6, center - 34), (center, center - 24), (center + 8, center - 34), (center + 14, center - 24)])
    return surface


def terrain_tile(kind, theme=None):
    surface = pygame.Surface((54, 54), pygame.SRCALPHA)
    palettes = {
        "forest": {
            "grass": ((27, 42, 30), (44, 64, 36)),
            "grass_dark": ((20, 32, 24), (34, 50, 30)),
            "road": ((126, 98, 62), (150, 118, 74)),
            "road_edge": ((70, 58, 42), (100, 82, 55)),
        },
        "swamp": {
            "grass": ((26, 46, 38), (58, 82, 48)),
            "grass_dark": ((16, 33, 31), (34, 61, 48)),
            "road": ((86, 94, 59), (114, 128, 72)),
            "road_edge": ((43, 58, 44), (72, 88, 55)),
        },
        "snow": {
            "grass": ((165, 184, 184), (205, 224, 224)),
            "grass_dark": ((112, 138, 146), (166, 190, 196)),
            "road": ((112, 122, 130), (150, 160, 170)),
            "road_edge": ((70, 80, 92), (105, 115, 128)),
        },
        "lava": {
            "grass": ((46, 31, 30), (86, 45, 34)),
            "grass_dark": ((29, 24, 25), (68, 35, 30)),
            "road": ((78, 58, 50), (130, 70, 42)),
            "road_edge": ((38, 30, 30), (95, 42, 34)),
        },
    }
    theme = theme or "forest"
    if theme in palettes and kind in palettes[theme]:
        base, fleck = palettes[theme][kind]
    elif kind == "grass":
        base = (27, 42, 30)
        fleck = (44, 64, 36)
    elif kind == "grass_dark":
        base = (20, 32, 24)
        fleck = (34, 50, 30)
    elif kind == "road":
        base = (126, 98, 62)
        fleck = (150, 118, 74)
    else:
        base = (70, 58, 42)
        fleck = (100, 82, 55)
    surface.fill(base)
    for i in range(9):
        x = (i * 17 + len(kind) * 5) % 54
        y = (i * 11 + len(kind) * 7) % 54
        pygame.draw.rect(surface, fleck, (x, y, 10, 4), border_radius=2)
    return surface


def marker(kind):
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    color = (70, 185, 95) if kind == "spawn" else (190, 75, 75)
    pygame.draw.circle(surface, color, (24, 24), 21)
    pygame.draw.circle(surface, (20, 35, 25), (24, 24), 13)
    if kind == "spawn":
        pygame.draw.polygon(surface, (235, 245, 210), [(19, 14), (34, 24), (19, 34)])
    else:
        pygame.draw.rect(surface, (235, 210, 190), (16, 16, 16, 16), 3)
    return surface


def projectile(kind, color):
    surface = pygame.Surface((24, 24), pygame.SRCALPHA)
    if kind == "archer":
        pygame.draw.line(surface, color, (3, 15), (21, 8), 3)
        pygame.draw.polygon(surface, (230, 230, 190), [(20, 8), (15, 5), (17, 12)])
    elif kind == "sniper":
        pygame.draw.line(surface, color, (2, 12), (22, 12), 2)
        pygame.draw.circle(surface, (255, 255, 255), (19, 12), 3)
    elif kind == "machine_gun":
        pygame.draw.rect(surface, color, (8, 10, 9, 4), border_radius=2)
        pygame.draw.circle(surface, (255, 245, 160), (18, 12), 3)
    elif kind == "cannon":
        pygame.draw.circle(surface, color, (12, 12), 7)
        pygame.draw.circle(surface, (50, 45, 38), (9, 9), 2)
    elif kind == "frost":
        pygame.draw.circle(surface, color, (12, 12), 7, 2)
        pygame.draw.line(surface, color, (12, 3), (12, 21), 2)
        pygame.draw.line(surface, color, (3, 12), (21, 12), 2)
    elif kind == "tesla":
        pygame.draw.line(surface, color, (4, 12), (11, 5), 3)
        pygame.draw.line(surface, color, (11, 5), (9, 14), 3)
        pygame.draw.line(surface, color, (9, 14), (20, 8), 3)
    elif kind == "poison":
        pygame.draw.circle(surface, (82, 175, 75), (12, 12), 7)
        pygame.draw.circle(surface, color, (9, 9), 3)
        pygame.draw.circle(surface, (180, 255, 130), (15, 14), 2)
    elif kind == "flame":
        pygame.draw.polygon(surface, color, [(5, 18), (10, 5), (18, 12), (13, 21)])
        pygame.draw.polygon(surface, (255, 225, 85), [(9, 16), (11, 8), (16, 13), (13, 18)])
    elif kind == "mortar":
        pygame.draw.circle(surface, color, (12, 12), 8)
        pygame.draw.rect(surface, (55, 48, 40), (7, 7, 9, 9), border_radius=2)
    elif kind == "gold":
        pygame.draw.circle(surface, color, (12, 12), 7)
        pygame.draw.circle(surface, (145, 105, 30), (12, 12), 7, 2)
        pygame.draw.line(surface, (255, 245, 160), (12, 7), (12, 17), 2)
    else:
        pygame.draw.circle(surface, color, (12, 12), 4)
    return surface


def effect(kind):
    surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    if kind == "explosion":
        for radius, color in [(27, (150, 80, 45, 130)), (19, (230, 150, 75, 180)), (9, (255, 235, 140, 220))]:
            pygame.draw.circle(surface, color, (32, 32), radius)
    elif kind == "frost_burst":
        for radius, color in [(25, (120, 220, 255, 100)), (16, (190, 245, 255, 160)), (7, (240, 255, 255, 230))]:
            pygame.draw.circle(surface, color, (32, 32), radius, 2)
    elif kind == "spark":
        pygame.draw.circle(surface, (255, 245, 120, 200), (32, 32), 12)
        pygame.draw.line(surface, (255, 255, 255, 230), (32, 12), (32, 52), 2)
        pygame.draw.line(surface, (255, 255, 255, 230), (12, 32), (52, 32), 2)
    elif kind == "shield_break":
        pygame.draw.circle(surface, (210, 225, 255, 110), (32, 32), 24, 3)
        pygame.draw.line(surface, (245, 250, 255, 210), (18, 18), (31, 32), 3)
        pygame.draw.line(surface, (245, 250, 255, 210), (31, 32), (24, 49), 3)
        pygame.draw.line(surface, (245, 250, 255, 210), (41, 16), (34, 31), 2)
        pygame.draw.line(surface, (245, 250, 255, 210), (34, 31), (47, 45), 2)
    elif kind == "smoke":
        for center, radius, alpha in [((24, 36), 15, 80), ((36, 30), 18, 65), ((30, 22), 12, 55)]:
            pygame.draw.circle(surface, (95, 90, 82, alpha), center, radius)
    elif kind == "explosion_ring":
        pygame.draw.circle(surface, (255, 220, 105, 210), (32, 32), 26, 3)
        pygame.draw.circle(surface, (230, 105, 45, 150), (32, 32), 18, 3)
        pygame.draw.circle(surface, (95, 60, 38, 120), (32, 32), 30, 2)
    elif kind == "frost_mist":
        for radius, alpha in [(27, 70), (20, 100), (11, 150)]:
            pygame.draw.circle(surface, (185, 245, 255, alpha), (32, 32), radius)
        pygame.draw.line(surface, (235, 255, 255, 180), (18, 32), (46, 32), 2)
        pygame.draw.line(surface, (235, 255, 255, 180), (32, 18), (32, 46), 2)
    elif kind == "lightning_spark":
        pygame.draw.line(surface, (255, 255, 170, 230), (31, 7), (20, 30), 4)
        pygame.draw.line(surface, (255, 255, 170, 230), (20, 30), (37, 30), 4)
        pygame.draw.line(surface, (255, 255, 170, 230), (37, 30), (27, 57), 4)
        pygame.draw.circle(surface, (160, 220, 255, 120), (32, 32), 23, 2)
    elif kind == "poison_cloud":
        for center, radius, alpha in [((24, 33), 16, 115), ((36, 30), 18, 105), ((31, 21), 13, 90)]:
            pygame.draw.circle(surface, (100, 220, 80, alpha), center, radius)
        pygame.draw.circle(surface, (190, 255, 130, 170), (38, 24), 4)
    elif kind == "flame_burst":
        pygame.draw.polygon(surface, (255, 95, 35, 190), [(19, 53), (25, 20), (32, 8), (40, 24), (47, 53)])
        pygame.draw.polygon(surface, (255, 210, 85, 220), [(25, 52), (31, 25), (36, 17), (40, 52)])
    elif kind == "coin_sparkle":
        pygame.draw.circle(surface, (255, 220, 80, 180), (32, 32), 15)
        pygame.draw.circle(surface, (150, 110, 30, 180), (32, 32), 15, 2)
        pygame.draw.line(surface, (255, 255, 180, 230), (32, 9), (32, 55), 2)
        pygame.draw.line(surface, (255, 255, 180, 230), (9, 32), (55, 32), 2)
    return surface


def write_wav(relative_path, notes, volume=0.25, sample_rate=22050):
    samples = array("h")
    for frequency, duration in notes:
        count = int(sample_rate * duration)
        for index in range(count):
            fade = 1 - index / max(1, count)
            value = int(32767 * volume * fade * math.sin(2 * math.pi * frequency * index / sample_rate))
            samples.append(value)
    with wave.open(str(ASSETS / relative_path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(samples.tobytes())


def generate_sprites():
    tower_colors = {
        "archer": ((90, 180, 95), (230, 210, 150)),
        "sniper": ((120, 150, 170), (210, 220, 235)),
        "machine_gun": ((95, 115, 125), (255, 225, 100)),
        "cannon": ((150, 105, 70), (255, 180, 90)),
        "frost": ((90, 175, 225), (180, 245, 255)),
        "tesla": ((230, 210, 65), (255, 245, 90)),
        "poison": ((105, 190, 85), (165, 255, 120)),
        "barracks": ((185, 145, 85), (220, 220, 230)),
        "flame": ((225, 95, 45), (255, 170, 70)),
        "mortar": ((115, 105, 90), (205, 180, 130)),
        "support": ((200, 185, 105), (235, 215, 90)),
        "gold": ((220, 180, 65), (255, 225, 90)),
    }
    for name, (color, accent) in tower_colors.items():
        save_surface(tower_sprite(name, color, accent), f"sprites/towers/{name}_idle.png")
        save_surface(tower_sprite(name, color, accent, True), f"sprites/towers/{name}_fire.png")
        save_surface(tower_sprite(name, color, accent, False, 1), f"sprites/towers/{name}_idle_1.png")
        save_surface(tower_sprite(name, color, accent, False, 2), f"sprites/towers/{name}_idle_2.png")
        save_surface(tower_sprite(name, color, accent, True, 1), f"sprites/towers/{name}_fire_1.png")
        save_surface(tower_sprite(name, color, accent, True, 2), f"sprites/towers/{name}_fire_2.png")

    enemy_colors = {
        "normal": (210, 60, 60),
        "fast": (235, 95, 190),
        "tank": (160, 80, 55),
        "swarm": (230, 120, 70),
        "shield": (170, 170, 190),
        "armored": (130, 130, 145),
        "flying": (185, 120, 245),
        "boss": (170, 55, 55),
        "split_child": (255, 145, 70),
        "shield_cracked": (170, 170, 190),
    }
    for name, color in enemy_colors.items():
        is_boss = name == "boss"
        is_flying = name == "flying"
        save_surface(enemy_sprite(name, color, is_boss, is_flying), f"sprites/enemies/{name}.png")
        save_surface(enemy_sprite(name, color, is_boss, is_flying, 1), f"sprites/enemies/{name}_walk_1.png")
        save_surface(enemy_sprite(name, color, is_boss, is_flying, 2), f"sprites/enemies/{name}_walk_2.png")
        save_surface(enemy_sprite(name, color, is_boss, is_flying, 3), f"sprites/enemies/{name}_hit.png")
        if is_boss:
            save_surface(enemy_sprite(name, (220, 60, 50), is_boss, is_flying, 3), f"sprites/enemies/{name}_rage.png")

    for name in ("grass", "grass_dark", "road", "road_edge"):
        save_surface(terrain_tile(name), f"sprites/terrain/{name}.png")
    for theme in ("forest", "swamp", "snow", "lava"):
        for name in ("grass", "grass_dark", "road", "road_edge"):
            save_surface(terrain_tile(name, theme), f"sprites/terrain/{theme}_{name}.png")
    save_surface(marker("spawn"), "sprites/terrain/spawn_gate.png")
    save_surface(marker("base"), "sprites/terrain/base_gate.png")

    projectile_colors = {
        "archer": (210, 160, 90),
        "sniper": (245, 245, 230),
        "machine_gun": (255, 225, 100),
        "cannon": (80, 70, 60),
        "frost": (175, 240, 255),
        "tesla": (255, 245, 90),
        "poison": (125, 235, 95),
        "flame": (255, 120, 45),
        "mortar": (105, 95, 80),
        "gold": (255, 220, 90),
    }
    for name, color in projectile_colors.items():
        save_surface(projectile(name, color), f"sprites/projectiles/{name}.png")

    for name in (
        "explosion",
        "frost_burst",
        "spark",
        "shield_break",
        "smoke",
        "explosion_ring",
        "frost_mist",
        "lightning_spark",
        "poison_cloud",
        "flame_burst",
        "coin_sparkle",
    ):
        save_surface(effect(name), f"sprites/effects/{name}.png")


def generate_sounds():
    sound_map = {
        "sounds/ui/build.wav": [(360, 0.06), (520, 0.05)],
        "sounds/ui/upgrade.wav": [(520, 0.05), (760, 0.07)],
        "sounds/ui/sell.wav": [(320, 0.07), (220, 0.05)],
        "sounds/ui/wave.wav": [(420, 0.08), (580, 0.08)],
        "sounds/ui/wave_fast.wav": [(760, 0.035), (960, 0.035), (1160, 0.045)],
        "sounds/ui/wave_tank.wav": [(115, 0.08), (95, 0.08)],
        "sounds/ui/wave_shield.wav": [(620, 0.035), (330, 0.04), (260, 0.04)],
        "sounds/ui/wave_flying.wav": [(880, 0.06), (1180, 0.06)],
        "sounds/ui/wave_boss.wav": [(82, 0.08), (120, 0.055), (74, 0.055)],
        "sounds/ui/wave_complete.wav": [(520, 0.06), (680, 0.06), (880, 0.08)],
        "sounds/enemies/death.wav": [(160, 0.05), (90, 0.06)],
        "sounds/enemies/leak.wav": [(130, 0.12)],
        "sounds/enemies/boss_spawn.wav": [(90, 0.12), (130, 0.12)],
        "sounds/enemies/boss_death.wav": [(180, 0.09), (120, 0.09), (80, 0.12)],
        "sounds/enemies/shield_break.wav": [(520, 0.04), (260, 0.06)],
        "sounds/towers/archer.wav": [(620, 0.035)],
        "sounds/towers/sniper.wav": [(980, 0.045), (520, 0.03)],
        "sounds/towers/machine_gun.wav": [(720, 0.022)],
        "sounds/towers/cannon.wav": [(95, 0.10)],
        "sounds/towers/frost.wav": [(760, 0.05), (1020, 0.03)],
        "sounds/towers/tesla.wav": [(1150, 0.025), (870, 0.025)],
        "sounds/towers/poison.wav": [(430, 0.04), (360, 0.05)],
        "sounds/towers/flame.wav": [(190, 0.045), (260, 0.045)],
        "sounds/towers/mortar.wav": [(72, 0.12), (105, 0.05)],
        "sounds/towers/gold.wav": [(880, 0.035), (1320, 0.045)],
        "sounds/towers/freeze.wav": [(900, 0.08)],
        "sounds/towers/chain.wav": [(1200, 0.02), (980, 0.02)],
    }
    for relative, notes in sound_map.items():
        write_wav(relative, notes, 0.20)

    music = []
    for _ in range(16):
        music.extend([(220, 0.18), (330, 0.18), (294, 0.18), (392, 0.18)])
    write_wav("sounds/music/loop.wav", music, 0.045)
    boss_music = []
    for _ in range(18):
        boss_music.extend([(110, 0.16), (165, 0.16), (147, 0.16), (196, 0.16)])
    write_wav("sounds/music/boss_loop.wav", boss_music, 0.06)


def main():
    pygame.init()
    ensure_dirs()
    generate_sprites()
    generate_sounds()
    print(f"Generated assets in {ASSETS}")


if __name__ == "__main__":
    main()
