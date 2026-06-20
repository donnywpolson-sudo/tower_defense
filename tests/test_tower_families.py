import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from td_game import app, data


class TowerFamilyDataTests(unittest.TestCase):
    def test_tower_family_data_validates(self):
        self.assertEqual(data.validate_tower_family_data(), [])

    def test_root_shop_has_only_eight_families(self):
        shop_roots = tuple(tower_type for tab in data.SHOP_TABS.values() for tower_type in tab)

        self.assertEqual(shop_roots, data.ROOT_TOWER_IDS)
        self.assertEqual(len(shop_roots), 8)
        for legacy_id in data.LEGACY_TOWER_ALIASES:
            self.assertNotIn(legacy_id, shop_roots)

    def test_every_root_tower_has_three_branches(self):
        for tower_type in data.ROOT_TOWER_IDS:
            self.assertEqual(len(data.BRANCH_DEFINITIONS[tower_type]), 3)
            self.assertEqual(tuple(data.BRANCH_DEFINITIONS[tower_type]), data.TOWER_TYPES[tower_type]["branch_options"])

    def test_every_branch_has_readable_depth_metadata(self):
        for tower_type in data.ROOT_TOWER_IDS:
            for branch in data.BRANCH_DEFINITIONS[tower_type].values():
                self.assertIn(branch["focus"], data.FOCUS_LABELS)
                self.assertTrue(branch["keystone"])
                self.assertTrue(branch["synergy"])
                self.assertTrue(branch["mastery"])
                self.assertEqual(len(branch["milestones"]), 5)

    def test_legacy_towers_map_to_branch_mechanics(self):
        expected = {
            "poison": ("archer", "trapline"),
            "flame": ("cannon", "terraformer"),
            "mortar": ("cannon", "artillery"),
            "gold": ("support", "research_lab"),
        }

        for legacy_id, target in expected.items():
            self.assertEqual(data.normalize_tower_type(legacy_id), target)
            root, branch = target
            self.assertIn(branch, data.BRANCH_DEFINITIONS[root])

    def test_folded_extra_tower_mechanics_still_exist_in_branches(self):
        self.assertIn("poison", data.BRANCH_DEFINITIONS["archer"]["trapline"]["mechanics"])
        self.assertIn("poison", data.BRANCH_DEFINITIONS["machine_gun"]["ammo_fabricator"]["mechanics"])
        self.assertIn("burn", data.BRANCH_DEFINITIONS["cannon"]["terraformer"]["mechanics"])
        self.assertIn("mortar", data.BRANCH_DEFINITIONS["cannon"]["artillery"]["mechanics"])
        self.assertIn("bounty", data.BRANCH_DEFINITIONS["barracks"]["mercenary_guild"]["mechanics"])
        self.assertIn("research", data.BRANCH_DEFINITIONS["support"]["research_lab"]["mechanics"])


class TowerBranchUpgradeTests(unittest.TestCase):
    def setUp(self):
        app.towers.clear()
        app.enemies.clear()
        app.projectiles.clear()
        app.effects.clear()
        app.money = 999
        app.research_points = 0

    def test_tier_two_root_tower_must_choose_branch(self):
        tower = app.Tower(100, 100, "archer", data.SHOP_COSTS["archer"])

        self.assertEqual(tower.level, 2)
        self.assertIsNone(tower.selected_branch)
        self.assertTrue(tower.needs_branch_choice())
        self.assertFalse(tower.can_upgrade())
        self.assertEqual(app.get_upgrade_options(tower), [])
        self.assertEqual(len(app.get_branch_options(tower)), 3)

    def test_branch_choice_locks_and_enters_tier_three(self):
        tower = app.Tower(100, 100, "archer", data.SHOP_COSTS["archer"])

        self.assertTrue(tower.choose_branch("trapline"))
        self.assertEqual(tower.level, data.BRANCH_UNLOCK_LEVEL)
        self.assertEqual(tower.selected_branch, "trapline")
        self.assertFalse(tower.needs_branch_choice())
        self.assertFalse(tower.choose_branch("deadeye"))

    def test_branch_options_disable_when_money_is_low(self):
        tower = app.Tower(100, 100, "archer", data.SHOP_COSTS["archer"])
        app.money = 0

        self.assertTrue(app.get_branch_options(tower))
        self.assertTrue(all(not option["enabled"] for option in app.get_branch_options(tower)))

    def test_branch_options_expose_depth_without_extra_menu(self):
        tower = app.Tower(100, 100, "archer", data.SHOP_COSTS["archer"])
        option = app.get_branch_options(tower)[0]

        self.assertIn("focus", option)
        self.assertIn("synergy", option)
        self.assertIn("keystone", option)
        self.assertIn("mastery", option)


if __name__ == "__main__":
    unittest.main()
