from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

TOWER_TYPES = (
    "archer",
    "sniper",
    "machine_gun",
    "cannon",
    "frost",
    "tesla",
    "poison",
    "barracks",
    "flame",
    "mortar",
    "support",
    "gold",
)

TOWER_FRAMES = ("idle", "fire", "idle_1", "idle_2", "fire_1", "fire_2")
ENEMY_TYPES = (
    "normal",
    "fast",
    "tank",
    "swarm",
    "shield",
    "armored",
    "flying",
    "boss",
    "split_child",
    "shield_cracked",
)
ENEMY_FRAMES = ("base", "walk_1", "walk_2", "hit")
PROJECTILE_TYPES = (
    "archer",
    "sniper",
    "machine_gun",
    "cannon",
    "frost",
    "tesla",
    "poison",
    "flame",
    "mortar",
    "gold",
)
TERRAIN_ASSETS = (
    "grass",
    "grass_dark",
    "road",
    "road_edge",
    "forest_grass",
    "forest_grass_dark",
    "forest_road",
    "forest_road_edge",
    "swamp_grass",
    "swamp_grass_dark",
    "swamp_road",
    "swamp_road_edge",
    "snow_grass",
    "snow_grass_dark",
    "snow_road",
    "snow_road_edge",
    "lava_grass",
    "lava_grass_dark",
    "lava_road",
    "lava_road_edge",
)
EFFECT_ASSETS = (
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
)
UI_SOUNDS = (
    "build",
    "upgrade",
    "sell",
    "wave",
    "wave_fast",
    "wave_tank",
    "wave_shield",
    "wave_flying",
    "wave_boss",
    "wave_complete",
)
ENEMY_SOUNDS = ("death", "leak", "boss_spawn", "boss_death", "shield_break")
TOWER_SOUNDS = (
    "archer",
    "sniper",
    "machine_gun",
    "cannon",
    "frost",
    "tesla",
    "poison",
    "flame",
    "mortar",
    "gold",
    "freeze",
    "chain",
)
MUSIC = ("loop", "boss_loop")


def required_asset_paths():
    paths = []

    for tower_type in TOWER_TYPES:
        for frame in TOWER_FRAMES:
            paths.append(Path("sprites") / "towers" / f"{tower_type}_{frame}.png")

    for enemy_type in ENEMY_TYPES:
        for frame in ENEMY_FRAMES:
            filename = f"{enemy_type}.png" if frame == "base" else f"{enemy_type}_{frame}.png"
            paths.append(Path("sprites") / "enemies" / filename)
    paths.append(Path("sprites") / "enemies" / "boss_rage.png")

    for name in TERRAIN_ASSETS:
        paths.append(Path("sprites") / "terrain" / f"{name}.png")
    paths.append(Path("sprites") / "terrain" / "spawn_gate.png")
    paths.append(Path("sprites") / "terrain" / "base_gate.png")

    for projectile_type in PROJECTILE_TYPES:
        paths.append(Path("sprites") / "projectiles" / f"{projectile_type}.png")

    for effect_name in EFFECT_ASSETS:
        paths.append(Path("sprites") / "effects" / f"{effect_name}.png")

    for sound_name in UI_SOUNDS:
        paths.append(Path("sounds") / "ui" / f"{sound_name}.wav")
    for sound_name in ENEMY_SOUNDS:
        paths.append(Path("sounds") / "enemies" / f"{sound_name}.wav")
    for sound_name in TOWER_SOUNDS:
        paths.append(Path("sounds") / "towers" / f"{sound_name}.wav")
    for music_name in MUSIC:
        paths.append(Path("sounds") / "music" / f"{music_name}.wav")

    return paths


def missing_required_assets(asset_root=ASSETS):
    return [path for path in required_asset_paths() if not (asset_root / path).exists()]


def main():
    missing = missing_required_assets()
    if missing:
        print("Missing required assets:")
        for path in missing:
            print(f"  assets/{path.as_posix()}")
        return 1

    print(f"Asset validation OK: {len(required_asset_paths())} required files found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
