import unittest

from td_game import config, mapgen


class MapGenerationTests(unittest.TestCase):
    def test_same_seed_generates_same_map(self):
        first = mapgen.generate_random_map(24680)
        second = mapgen.generate_random_map(24680)

        self.assertEqual(first["seed"], second["seed"])
        self.assertEqual(first["theme"], second["theme"])
        self.assertEqual(first["paths"], second["paths"])

    def test_generated_path_starts_left_and_ends_right(self):
        generated = mapgen.generate_random_map(13579)

        for path in generated["paths"]:
            self.assertEqual(path[0][0], 0)
            self.assertEqual(path[-1][0], config.MAP_WIDTH)

    def test_generated_path_length_stays_near_current_maps(self):
        generated = mapgen.generate_random_map(97531)

        for path in generated["paths"]:
            length = mapgen.path_length(path)

            self.assertGreaterEqual(length, mapgen.MIN_PATH_LENGTH)
            self.assertLessEqual(length, mapgen.MAX_PATH_LENGTH)

    def test_generated_path_has_several_twists(self):
        generated = mapgen.generate_random_map(112233)
        path = generated["paths"][0]

        self.assertGreaterEqual(len(path), 2 * mapgen.MIN_TURNS + 2)

    def test_generated_maps_have_one_creep_path(self):
        for seed in range(1, 61):
            with self.subTest(seed=seed):
                generated = mapgen.generate_random_map(seed)

                self.assertEqual(len(generated["paths"]), 1)

    def test_generated_segments_are_cardinal(self):
        for seed in range(1, 61):
            with self.subTest(seed=seed):
                paths = mapgen.generate_random_map(seed)["paths"]

                self.assertTrue(mapgen.paths_are_orthogonal(paths))

    def test_generated_paths_have_at_least_one_overlap(self):
        for seed in range(1, 101):
            with self.subTest(seed=seed):
                paths = mapgen.generate_random_map(seed)["paths"]

                self.assertTrue(mapgen.paths_have_overlap(paths))

    def test_turnaround_path_can_move_back_left(self):
        generated = mapgen.generate_random_map(5)
        path = generated["paths"][0]

        self.assertEqual(generated["name"], "Random Turnaround")
        self.assertTrue(any(end[0] < start[0] for start, end in zip(path, path[1:])))

    def test_generated_points_stay_inside_playable_bounds(self):
        generated = mapgen.generate_random_map(86420)
        min_y = config.BUILD_GRID_TOP + config.PATH_WIDTH // 2
        max_y = config.HEIGHT - config.PATH_WIDTH // 2

        for path in generated["paths"]:
            for x, y in path:
                self.assertGreaterEqual(x, 0)
                self.assertLessEqual(x, config.MAP_WIDTH)
                self.assertGreaterEqual(y, min_y)
                self.assertLessEqual(y, max_y)

    def test_generated_paths_leave_tower_sized_corridors(self):
        for seed in range(1, 26):
            with self.subTest(seed=seed):
                paths = mapgen.generate_random_map(seed)["paths"]

                self.assertTrue(mapgen.paths_have_open_build_corridors(paths))

    def test_generated_paths_keep_enough_buildable_space(self):
        for seed in range(1, 26):
            with self.subTest(seed=seed):
                paths = mapgen.generate_random_map(seed)["paths"]

                self.assertGreaterEqual(
                    mapgen.count_buildable_sites_for_paths(paths),
                    mapgen.MIN_BUILDABLE_SITES,
                )

    def test_common_seeds_do_not_use_fallback_map(self):
        for seed in range(1, 26):
            with self.subTest(seed=seed):
                generated = mapgen.generate_random_map(seed)

                self.assertFalse(generated["name"].startswith("Random Fallback"))

    def test_common_seeds_use_multiple_route_styles(self):
        generated = [mapgen.generate_random_map(seed) for seed in range(1, 61)]
        styles = {item["name"] for item in generated}

        self.assertIn("Random Switchback", styles)
        self.assertIn("Random Turnaround", styles)
        self.assertNotIn("Random Diagonal", styles)
        self.assertNotIn("Random Split Lane", styles)


if __name__ == "__main__":
    unittest.main()
