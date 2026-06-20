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
        "sprites/ui",
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


def tower_sprite(tower_type, color, accent, firing=False):
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    shadow(surface, (24, 26), 16)
    pygame.draw.circle(surface, color, (24, 13), 7)
    pygame.draw.rect(surface, color, (15, 20, 18, 17))
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
    elif tower_type == "barracks":
        pygame.draw.rect(surface, (130, 95, 55), (3, 25, 13, 18))
        pygame.draw.rect(surface, (130, 95, 55), (32, 25, 13, 18))
        pygame.draw.line(surface, (220, 220, 230), (9, 24), (9, 8), 2)
        pygame.draw.line(surface, (220, 220, 230), (38, 24), (38, 8), 2)
    elif tower_type == "support":
        pygame.draw.line(surface, (80, 60, 30), (9, 42), (9, 5), 3)
        pygame.draw.polygon(surface, accent, [(10, 5), (42, 13), (10, 23)])
    return surface


def enemy_sprite(kind, color, boss=False, flying=False):
    size = 64 if boss else 32
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    radius = 22 if boss else 12
    shadow(surface, (center, center + 2), radius)
    pygame.draw.circle(surface, color, (center, center), radius)
    pygame.draw.circle(surface, tuple(min(255, c + 45) for c in color), (center - radius // 3, center - radius // 3), max(3, radius // 3))
    pygame.draw.circle(surface, (35, 35, 35), (center - radius // 3, center - 2), 2)
    pygame.draw.circle(surface, (35, 35, 35), (center + radius // 3, center - 2), 2)
    if kind in ("shield", "armored") or boss:
        pygame.draw.circle(surface, (225, 225, 245), (center, center), radius + 4, 2)
    if flying:
        pygame.draw.arc(surface, (230, 220, 255), (center - radius - 7, center - 12, radius, 18), 2.8, 6.0, 3)
        pygame.draw.arc(surface, (230, 220, 255), (center + 7, center - 12, radius, 18), 3.4, 6.4, 3)
    if boss:
        pygame.draw.circle(surface, (255, 210, 90), (center, center), radius + 9, 2)
    return surface


def terrain_tile(kind):
    surface = pygame.Surface((54, 54), pygame.SRCALPHA)
    if kind == "grass":
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
        "barracks": ((185, 145, 85), (220, 220, 230)),
        "support": ((200, 185, 105), (235, 215, 90)),
    }
    for name, (color, accent) in tower_colors.items():
        save_surface(tower_sprite(name, color, accent), f"sprites/towers/{name}_idle.png")
        save_surface(tower_sprite(name, color, accent, True), f"sprites/towers/{name}_fire.png")

    enemy_colors = {
        "normal": (210, 60, 60),
        "fast": (235, 95, 190),
        "tank": (160, 80, 55),
        "swarm": (230, 120, 70),
        "shield": (170, 170, 190),
        "armored": (130, 130, 145),
        "flying": (185, 120, 245),
        "boss": (170, 55, 55),
    }
    for name, color in enemy_colors.items():
        save_surface(enemy_sprite(name, color, name == "boss", name == "flying"), f"sprites/enemies/{name}.png")

    for name in ("grass", "grass_dark", "road", "road_edge"):
        save_surface(terrain_tile(name), f"sprites/terrain/{name}.png")
    save_surface(marker("spawn"), "sprites/terrain/spawn_gate.png")
    save_surface(marker("base"), "sprites/terrain/base_gate.png")

    projectile_colors = {
        "archer": (210, 160, 90),
        "sniper": (245, 245, 230),
        "machine_gun": (255, 225, 100),
        "cannon": (80, 70, 60),
        "frost": (175, 240, 255),
        "tesla": (255, 245, 90),
    }
    for name, color in projectile_colors.items():
        save_surface(projectile(name, color), f"sprites/projectiles/{name}.png")

    for name in ("explosion", "frost_burst", "spark"):
        save_surface(effect(name), f"sprites/effects/{name}.png")


def generate_sounds():
    sound_map = {
        "sounds/ui/build.wav": [(360, 0.06), (520, 0.05)],
        "sounds/ui/upgrade.wav": [(520, 0.05), (760, 0.07)],
        "sounds/ui/sell.wav": [(320, 0.07), (220, 0.05)],
        "sounds/ui/wave.wav": [(420, 0.08), (580, 0.08)],
        "sounds/ui/wave_complete.wav": [(520, 0.06), (680, 0.06), (880, 0.08)],
        "sounds/enemies/death.wav": [(160, 0.05), (90, 0.06)],
        "sounds/enemies/leak.wav": [(130, 0.12)],
        "sounds/enemies/boss_spawn.wav": [(90, 0.12), (130, 0.12)],
        "sounds/enemies/boss_death.wav": [(180, 0.09), (120, 0.09), (80, 0.12)],
        "sounds/towers/archer.wav": [(620, 0.035)],
        "sounds/towers/sniper.wav": [(980, 0.045), (520, 0.03)],
        "sounds/towers/machine_gun.wav": [(720, 0.022)],
        "sounds/towers/cannon.wav": [(95, 0.10)],
        "sounds/towers/frost.wav": [(760, 0.05), (1020, 0.03)],
        "sounds/towers/tesla.wav": [(1150, 0.025), (870, 0.025)],
        "sounds/towers/freeze.wav": [(900, 0.08)],
        "sounds/towers/chain.wav": [(1200, 0.02), (980, 0.02)],
    }
    for relative, notes in sound_map.items():
        write_wav(relative, notes, 0.20)

    music = []
    for _ in range(16):
        music.extend([(220, 0.18), (330, 0.18), (294, 0.18), (392, 0.18)])
    write_wav("sounds/music/loop.wav", music, 0.045)


def main():
    pygame.init()
    ensure_dirs()
    generate_sprites()
    generate_sounds()
    print(f"Generated assets in {ASSETS}")


if __name__ == "__main__":
    main()
