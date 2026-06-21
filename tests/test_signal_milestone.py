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
        app.money = config.STARTING_MONEY
        app.lives = config.STARTING_LIVES
        app.research_points = 0
        app.pending_card_choices = []
        app.run_damage_bonus = 0.0
        app.run_range_bonus = 0.0
        app.next_wave_bounty_bonus = 0
        app.next_wave_bounty_wave = None
        app.selected_ability = None
        app.ability_cooldowns = {"emp": 0.0, "quarantine": 0.0}

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

    def test_manual_abilities_apply_emp_and_quarantine_effects(self):
        shielded = app.Enemy(100, 40, 1, kind="shield", shield_hits=3)
        commander = app.Enemy(200, 40, 10, kind="commander", commander=True)
        commander.x = shielded.x + 10
        commander.y = shielded.y
        app.enemies.extend([shielded, commander])

        self.assertTrue(app.trigger_emp_pulse())
        self.assertEqual(shielded.shield_hits, 1)
        self.assertGreater(shielded.slow_timer, 0)
        self.assertGreater(app.ability_cooldowns["emp"], 0)
        self.assertLess(commander.hp, commander.max_hp)

        app.ability_cooldowns["quarantine"] = 0
        self.assertTrue(app.trigger_quarantine_zone((shielded.x, shielded.y)))
        self.assertGreater(shielded.freeze_timer, 0)
        self.assertLessEqual(shielded.slow_multiplier, 0.35)
        self.assertGreater(app.ability_cooldowns["quarantine"], 0)


if __name__ == "__main__":
    unittest.main()
