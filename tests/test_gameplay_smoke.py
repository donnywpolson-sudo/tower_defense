import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from td_game import app, config, data, mapgen, waves


class GameplaySmokeTests(unittest.TestCase):
    def setUp(self):
        app.enemies.clear()
        app.towers.clear()
        app.projectiles.clear()
        app.effects.clear()
        app.selected_build_type = None
        app.selected_tower = None
        app.active_map = mapgen.generate_random_map(12345)
        app.wave = 1
        app.money = config.STARTING_MONEY

    def test_wave_19_remains_shield_split_but_spawn_count_is_playable(self):
        self.assertEqual(waves.get_wave_label(19), "Shield + Split")
        self.assertLessEqual(waves.get_regular_enemy_count(19), 70)
        self.assertGreaterEqual(waves.get_spawn_interval(30), config.MIN_SPAWN_INTERVAL)

    def test_split_minion_spawn_is_capped(self):
        app.wave = 19
        source = app.Enemy(10, 10, 1, death_spawns=config.MAX_SPLIT_CHILDREN + 50)

        app.spawn_death_minions(source)

        self.assertEqual(len(app.enemies), config.MAX_SPLIT_CHILDREN)
        self.assertTrue(all(enemy.is_split_child for enemy in app.enemies))

    def test_tower_placement_rejects_path_and_accepts_empty_grid_square(self):
        app.selected_build_type = "archer"
        app.money = 999

        self.assertFalse(app.can_place_tower(self._point_on_path()))
        self.assertIsNotNone(self._find_valid_build_position())

    def test_tesla_mastery_keeps_fire_rate_under_control(self):
        tower = app.Tower(100, 100, "tesla", data.SHOP_COSTS["tesla"])
        for level in range(3, config.BASE_MAX_TOWER_LEVEL + 1):
            tower.level = level
            tower.apply_weapon_level_stats()

        tower.level = config.PARAGON_LEVEL
        tower.apply_paragon_stats()
        for level in range(config.PARAGON_LEVEL + 1, config.MAX_TOWER_LEVEL + 1):
            tower.level = level
            tower.apply_mastery_stats()

        self.assertGreaterEqual(tower.fire_rate, 0.075)

    def test_sidebar_control_boxes_do_not_overlap(self):
        always_visible = [app.get_start_wave_button_rect(), app.get_pause_button_rect()]
        always_visible.extend(rect for rect, _ in app.get_speed_button_rects())
        always_visible.extend(rect for rect, _ in app.get_shop_button_rects())
        always_visible.extend(rect for rect, _ in app.get_audio_button_rects())

        no_tower_selected = always_visible + [app.get_new_map_button_rect()]
        tower_selected = always_visible + [app.get_upgrade_panel_rect()]
        branch_tower = app.Tower(100, 100, "archer", data.SHOP_COSTS["archer"])
        branch_panel_controls = [rect for rect, _ in app.get_branch_button_rects(branch_tower)]
        branch_panel_controls.extend([app.get_target_button_rect(), app.get_sell_button_rect()])

        self._assert_no_rect_overlap(no_tower_selected)
        self._assert_no_rect_overlap(tower_selected)
        self._assert_no_rect_overlap(branch_panel_controls)
        self.assertLessEqual(max(rect.bottom for rect, _ in app.get_audio_button_rects()), 282)

    def _find_valid_build_position(self):
        for x in range(config.BUILD_TILE_SIZE // 2, config.MAP_WIDTH, config.BUILD_GRID_STEP):
            for y in range(config.BUILD_GRID_TOP + config.BUILD_TILE_SIZE // 2, config.HEIGHT, config.BUILD_GRID_STEP):
                if app.can_place_tower((x, y)):
                    return x, y
        return None

    def _point_on_path(self):
        path = app.current_paths()[0]
        for start, end in zip(path, path[1:]):
            if start[1] == end[1] and abs(end[0] - start[0]) > config.BUILD_TILE_SIZE:
                return ((start[0] + end[0]) // 2, start[1])
        return path[0]

    def _assert_no_rect_overlap(self, rects):
        for index, rect in enumerate(rects):
            for other in rects[index + 1:]:
                self.assertFalse(rect.colliderect(other), f"{rect} overlaps {other}")


if __name__ == "__main__":
    unittest.main()
