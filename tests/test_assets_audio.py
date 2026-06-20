import os
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from td_game import app, mapgen, waves


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


class AssetAudioTests(unittest.TestCase):
    def test_generated_polish_assets_exist(self):
        required = [
            "sprites/towers/poison_idle.png",
            "sprites/towers/flame_fire_1.png",
            "sprites/towers/mortar_idle_2.png",
            "sprites/towers/gold_fire.png",
            "sprites/projectiles/poison.png",
            "sprites/projectiles/flame.png",
            "sprites/projectiles/mortar.png",
            "sprites/projectiles/gold.png",
            "sprites/effects/smoke.png",
            "sprites/effects/explosion_ring.png",
            "sprites/effects/frost_mist.png",
            "sprites/effects/lightning_spark.png",
            "sprites/effects/poison_cloud.png",
            "sprites/effects/flame_burst.png",
            "sprites/effects/coin_sparkle.png",
            "sounds/ui/wave_fast.wav",
            "sounds/ui/wave_tank.wav",
            "sounds/ui/wave_shield.wav",
            "sounds/ui/wave_flying.wav",
            "sounds/ui/wave_boss.wav",
            "sounds/towers/poison.wav",
            "sounds/towers/flame.wav",
            "sounds/towers/mortar.wav",
            "sounds/towers/gold.wav",
        ]

        missing = [path for path in required if not (ASSETS / path).exists()]

        self.assertEqual(missing, [])

    def test_wave_kind_maps_to_stinger_key(self):
        fast_wave = next(number for number in range(1, 20) if waves.get_wave_enemy_kind(number) == "fast")
        tank_wave = next(number for number in range(1, 20) if waves.get_wave_enemy_kind(number) == "tank")
        shield_wave = next(number for number in range(1, 20) if waves.get_wave_enemy_kind(number) == "shield")
        flying_wave = next(number for number in range(1, 20) if waves.get_wave_enemy_kind(number) == "flying")

        self.assertEqual(app.get_wave_stinger_key(fast_wave), "wave_fast")
        self.assertEqual(app.get_wave_stinger_key(tank_wave), "wave_tank")
        self.assertEqual(app.get_wave_stinger_key(shield_wave), "wave_shield")
        self.assertEqual(app.get_wave_stinger_key(flying_wave), "wave_flying")
        self.assertEqual(app.get_wave_stinger_key(5), "wave_boss")

    def test_fast_tower_sound_cooldowns_are_throttled(self):
        self.assertGreaterEqual(app.tower_sound_cooldown("machine_gun"), 0.04)
        self.assertGreaterEqual(app.tower_sound_cooldown("tesla"), 0.05)
        self.assertGreaterEqual(app.tower_sound_cooldown("poison"), 0.10)
        self.assertGreaterEqual(app.tower_sound_cooldown("mortar"), 0.12)

    def test_terrain_palette_keeps_path_readable(self):
        previous_map = app.active_map
        try:
            for theme in mapgen.THEMES:
                app.active_map = {"theme": theme, "paths": [[(0, 120), (900, 120)]], "seed": 1}
                palette = app.terrain_palette()
                road_vs_grass = sum(abs(a - b) for a, b in zip(palette["road"], palette["grass"]))
                edge_vs_road = sum(abs(a - b) for a, b in zip(palette["road_edge"], palette["road"]))

                self.assertGreater(road_vs_grass, 100)
                self.assertGreater(edge_vs_road, 50)
        finally:
            app.active_map = previous_map


if __name__ == "__main__":
    unittest.main()
