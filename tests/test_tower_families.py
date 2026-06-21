import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from td_game import app, data


class TowerFamilyDataTests(unittest.TestCase):
    def test_tower_family_data_validates(self):
        self.assertEqual(data.validate_tower_family_data(), [])

    def test_flat_shop_has_eight_visible_families(self):
        shop_roots = data.SHOP_TOWER_ORDER

        self.assertEqual(
            shop_roots,
            ("machine_gun", "cannon", "frost", "poison", "support", "sniper", "tesla", "barracks"),
        )
        self.assertEqual(len(shop_roots), 8)
        self.assertNotIn("archer", shop_roots)
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
                self.assertTrue(branch["signature"])
                self.assertTrue(branch["primary_mechanic"])
                self.assertTrue(branch["keystone"])
                self.assertTrue(branch["synergy"])
                self.assertTrue(branch["mastery"])
                self.assertEqual(len(branch["milestones"]), 5)
                for level in range(6, 11):
                    self.assertTrue(branch["late_descriptions"][level])
                    self.assertTrue(branch["upgrade_effects"][level])

    def test_visible_branches_have_unique_identity(self):
        signatures = []
        primary_mechanics = []

        for tower_type in data.SHOP_TOWER_ORDER:
            for branch in data.BRANCH_DEFINITIONS[tower_type].values():
                signatures.append(branch["signature"])
                primary_mechanics.append(branch["primary_mechanic"])

        self.assertEqual(len(signatures), len(set(signatures)))
        self.assertEqual(len(primary_mechanics), len(set(primary_mechanics)))

    def test_legacy_towers_map_to_branch_mechanics(self):
        expected = {
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
        self.assertIn("poison", data.BRANCH_DEFINITIONS["poison"]["venom_cask"]["mechanics"])
        self.assertIn("burn", data.BRANCH_DEFINITIONS["poison"]["wildfire"]["mechanics"])
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
        self.assertIn("primary_mechanic", option)
        self.assertIn("signature", option)
        self.assertIn("upgrade_effect", option)
        self.assertIn("synergy", option)
        self.assertIn("keystone", option)
        self.assertIn("mastery", option)

    def test_visible_branch_upgrades_preview_late_identity_scaling(self):
        for tower_type in data.SHOP_TOWER_ORDER:
            for branch_key, branch in data.BRANCH_DEFINITIONS[tower_type].items():
                with self.subTest(tower_type=tower_type, branch_key=branch_key):
                    tower = app.Tower(100, 100, tower_type, data.SHOP_COSTS[tower_type])
                    self.assertTrue(tower.choose_branch(branch_key))
                    app.towers = [tower] * 10
                    app.research_points = 999
                    app.money = 999999

                    while tower.level < 10:
                        option = app.get_upgrade_options(tower)[0]
                        next_level = tower.level + 1
                        self.assertTrue(option["description"])
                        if next_level >= 6:
                            self.assertIn(branch["upgrade_effects"][next_level], option["description"])
                        self.assertTrue(tower.upgrade(tower.tower_type))


class TowerBranchBehaviorTests(unittest.TestCase):
    def setUp(self):
        app.towers.clear()
        app.enemies.clear()
        app.projectiles.clear()
        app.effects.clear()
        app.money = 999999
        app.research_points = 999
        app.wave = 10
        app.wave_active = True
        app.run_damage_bonus = 0.0
        app.run_range_bonus = 0.0

    def _branch_tower(self, tower_type, branch_key, level=6, x=100, y=100):
        tower = app.Tower(x, y, tower_type, data.SHOP_COSTS[tower_type])
        self.assertTrue(tower.choose_branch(branch_key))
        while tower.level < level:
            tower.level += 1
            if tower.level == app.PARAGON_LEVEL:
                tower.is_paragon = True
                tower.apply_paragon_stats()
            elif tower.level > app.PARAGON_LEVEL:
                tower.apply_mastery_stats()
            else:
                tower.apply_weapon_level_stats()
        return tower

    def _projectile_for(self, tower, target):
        return app.Projectile(tower.x, tower.y, target, tower)

    def test_war_banner_and_battery_grid_buff_differently(self):
        gunner = app.Tower(140, 100, "machine_gun", data.SHOP_COSTS["machine_gun"])
        enemy = app.Enemy(100, 40, 1)
        enemy.x = 150
        enemy.y = 100

        banner = self._branch_tower("support", "war_banner", level=6)
        app.towers[:] = [banner, gunner]
        app.enemies[:] = [enemy]
        banner.support_mana = banner.support_max_mana
        banner.update_support(0.1)

        self.assertGreater(gunner.support_range_bonus, 0)

        gunner.support_buff_timer = 0
        gunner.support_damage_bonus = 0
        gunner.support_rate_bonus = 0
        gunner.support_range_bonus = 0
        battery = self._branch_tower("tesla", "battery_grid", level=6)
        app.towers[:] = [battery, gunner]
        battery.overclock_pulse_timer = 0
        battery.update_battery_grid(0.1)

        self.assertGreater(gunner.support_rate_bonus, 0)
        self.assertEqual(gunner.support_range_bonus, 0)

    def test_spotter_marks_one_target_but_signal_scans_multiple(self):
        spotter = self._branch_tower("sniper", "spotter", level=6)
        target = app.Enemy(120, 40, 1)
        other = app.Enemy(120, 40, 1)
        target.x = other.x = 135
        target.y = 100
        other.y = 128
        app.enemies[:] = [target, other]

        self._projectile_for(spotter, target).apply_branch_effects()

        self.assertGreater(target.marked_timer, 0)
        self.assertEqual(other.marked_timer, 0)

        signal = self._branch_tower("support", "signal_tower", level=6)
        signal.support_mana = signal.support_max_mana
        app.towers[:] = [signal]
        target.marked_timer = 0
        other.marked_timer = 0
        signal.update_support(0.1)

        self.assertGreater(target.marked_timer, 0)
        self.assertGreater(other.marked_timer, 0)

    def test_glacier_lockdown_and_gunner_suppression_use_different_state(self):
        glacier = self._branch_tower("frost", "glacier", level=6)
        frost_target = app.Enemy(100, 40, 1)
        frost_target.x = 130
        frost_target.y = 100
        app.enemies[:] = [frost_target]

        self._projectile_for(glacier, frost_target).apply_branch_effects()

        self.assertGreater(frost_target.freeze_timer, 0)
        self.assertEqual(frost_target.suppression_stacks, 0)

        suppression = self._branch_tower("machine_gun", "suppression", level=6)
        fast_target = app.Enemy(100, 60, 1, kind="fast")
        fast_target.x = 130
        fast_target.y = 100
        app.enemies[:] = [fast_target]

        self._projectile_for(suppression, fast_target).apply_branch_effects()

        self.assertGreater(fast_target.suppression_stacks, 0)
        self.assertGreater(fast_target.slow_timer, 0)
        self.assertEqual(fast_target.freeze_timer, 0)

    def test_wildfire_ignites_while_terraformer_creates_crater_control(self):
        wildfire = self._branch_tower("poison", "wildfire", level=6)
        wildfire_target = app.Enemy(100, 40, 1)
        wildfire_target.x = 130
        wildfire_target.y = 100
        app.enemies[:] = [wildfire_target]

        self._projectile_for(wildfire, wildfire_target).apply_branch_effects()

        self.assertGreater(wildfire_target.burn_timer, 0)
        self.assertEqual(wildfire_target.slow_timer, 0)

        terraformer = self._branch_tower("cannon", "terraformer", level=6)
        crater_target = app.Enemy(100, 40, 1)
        crater_target.x = 130
        crater_target.y = 100
        app.enemies[:] = [crater_target]

        self._projectile_for(terraformer, crater_target).apply_branch_effects()

        self.assertGreater(crater_target.burn_timer, 0)
        self.assertGreater(crater_target.slow_timer, 0)

    def test_engineers_create_minefield_damage_without_contagion_state(self):
        engineers = self._branch_tower("barracks", "engineers", level=6)
        target = app.Enemy(160, 30, 1)
        target.x = engineers.x + 10
        target.y = engineers.y
        app.towers[:] = [engineers]
        app.enemies[:] = [target]

        before_hp = target.hp
        engineers.update_barracks(0.5)

        self.assertLess(target.hp, before_hp)
        self.assertGreater(target.barracks_hold_timer, 0)
        self.assertEqual(target.poison_timer, 0)


if __name__ == "__main__":
    unittest.main()
