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
        path = generated["paths"][0]

        self.assertEqual(path[0][0], 0)
        self.assertEqual(path[-1][0], config.MAP_WIDTH)

    def test_generated_path_length_stays_near_current_maps(self):
        generated = mapgen.generate_random_map(97531)
        length = mapgen.path_length(generated["paths"][0])

        self.assertGreaterEqual(length, mapgen.MIN_PATH_LENGTH)
        self.assertLessEqual(length, mapgen.MAX_PATH_LENGTH)

    def test_generated_path_has_several_twists(self):
        generated = mapgen.generate_random_map(112233)
        path = generated["paths"][0]

        self.assertGreaterEqual(len(path), 2 * mapgen.MIN_TURNS + 2)

    def test_generated_points_stay_inside_playable_bounds(self):
        generated = mapgen.generate_random_map(86420)
        min_y = config.BUILD_GRID_TOP + config.PATH_WIDTH // 2
        max_y = config.HEIGHT - config.PATH_WIDTH // 2

        for x, y in generated["paths"][0]:
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, config.MAP_WIDTH)
            self.assertGreaterEqual(y, min_y)
            self.assertLessEqual(y, max_y)


if __name__ == "__main__":
    unittest.main()
