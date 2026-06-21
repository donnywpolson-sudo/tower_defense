import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from td_game import app, config, mapgen, waves


class SignalMilestoneTests(unittest.TestCase):
    def setUp(self):
        app.enemies.clear()
        app.towers.clear()
        app.projectiles.clear()
        app.effects.clear()
        app.active_map = mapgen.generate_random_map(12345)
        app.wave = 1
        app.wave_active = False
        app.money = config.STARTING_MONEY
        app.lives = config.STARTING_LIVES
        app.research_points = 0
        app.pending_card_choices = []
        app.run_damage_bonus = 0.0
        app.run_range_bonus = 0.0
        app.next_wave_bounty_bonus = 0
        app.next_wave_bounty_wave = None

    def test_wave_modifier_metadata_and_commander_schedule(self):
        self.assertEqual(waves.get_wave_modifier(19), "split")
        self.assertEqual(waves.get_wave_label(19), "Shield + Fragmenting")
        self.assertIn("recommendation", waves.get_wave_modifier_data(19))
        self.assertEqual(waves.get_commander_count_for_wave(8), 1)
        self.assertEqual(waves.get_commander_count_for_wave(9), 0)
        self.assertEqual(waves.get_commander_count_for_wave(10), 0)

        expected = waves.get_regular_enemy_count(8) + waves.get_commander_count_for_wave(8)
        self.assertEqual(app.get_enemies_per_wave(8), expected)

    def test_commander_applies_aura_resistance_to_nearby_packets(self):
        app.wave = 8
        commander = app.create_enemy("commander")
        packet = app.Enemy(100, 40, 1)
        packet.x = commander.x + 20
        packet.y = commander.y
        app.enemies.extend([commander, packet])

        app.update_commander_auras()
        dealt = packet.take_damage(100)

        self.assertGreater(packet.commander_aura_timer, 0)
        self.assertAlmostEqual(dealt, 86)

    def test_reward_card_choices_are_deterministic_and_cards_apply(self):
        first = app.generate_reward_card_choices(4)
        second = app.generate_reward_card_choices(4)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 3)

        app.pending_card_choices = ["cpu_cache"]
        app.money = 0
        self.assertTrue(app.apply_reward_card("cpu_cache"))
        self.assertEqual(app.money, 60)

        app.pending_card_choices = ["damage_patch"]
        self.assertTrue(app.apply_reward_card("damage_patch"))
        self.assertAlmostEqual(app.run_damage_bonus, 0.05)

        app.pending_card_choices = ["bounty_trace"]
        app.wave = 7
        self.assertTrue(app.apply_reward_card("bounty_trace"))
        self.assertEqual(app.next_wave_bounty_bonus, 2)
        self.assertEqual(app.next_wave_bounty_wave, 7)

    def test_channeler_spends_mana_on_buffs_and_enemy_debuffs(self):
        support = app.Tower(100, 100, "support", app.SHOP_COSTS["support"])
        gunner = app.Tower(140, 100, "machine_gun", app.SHOP_COSTS["machine_gun"])
        enemy = app.Enemy(155, 95, 1)
        enemy.x = 155
        enemy.y = 95
        app.towers.extend([support, gunner])
        app.enemies.append(enemy)
        app.wave_active = True

        support.support_mana = support.support_max_mana
        support.update_support(0.1)

        self.assertGreater(gunner.support_buff_timer, 0)
        self.assertGreater(gunner.support_damage_bonus, 0)
        self.assertLess(support.support_mana, support.support_max_mana)

        gunner.support_buff_timer = 5.0
        support.support_mana = support.support_max_mana
        support.support_cast_cooldown = 0
        support.update_support(0.1)

        self.assertGreater(enemy.marked_timer, 0)
        self.assertGreater(enemy.vulnerable_timer, 0)

    def test_ransomware_boss_protocol_locks_nearby_towers(self):
        app.wave = 10
        boss = app.create_boss_enemy()
        tower = app.Tower(180, 180, "sniper", app.SHOP_COSTS["sniper"])
        boss.x = tower.x + 24
        boss.y = tower.y
        app.enemies.append(boss)
        app.towers.append(tower)

        recommendations, _ = app.get_wave_recommendation(10)

        self.assertEqual(boss.boss_protocol, "ransomware")
        self.assertTrue(any("Ransomware" in line for line in recommendations))
        self.assertTrue(boss.trigger_ransomware_lock())
        self.assertGreater(tower.locked_timer, 0)

        tower.update(0.1)

        self.assertEqual(app.projectiles, [])


if __name__ == "__main__":
    unittest.main()
