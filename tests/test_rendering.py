import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from td_game.app import parse_runtime_options
from td_game.particles import ParticleManager
from td_game.rendering import PygameRenderer, RenderOptions, make_renderer


class BrokenOpenGLRenderer:
    def __init__(self, size, caption):
        raise RuntimeError("forced failure")


class RenderingTests(unittest.TestCase):
    def tearDown(self):
        pygame.display.quit()
        pygame.display.init()

    def test_parse_runtime_options(self):
        options = parse_runtime_options(["--renderer", "opengl", "--disable-glow", "--max-particles", "25"])
        self.assertEqual(options.renderer, "opengl")
        self.assertFalse(options.enable_glow)
        self.assertEqual(options.max_particles, 25)

    def test_particle_manager_expires_and_caps(self):
        manager = ParticleManager(max_particles=3)
        manager.emit(0, 0, (255, 255, 255), count=8, lifetime=0.1)
        self.assertLessEqual(len(manager.particles), 3)
        manager.update(1.0)
        self.assertEqual(len(manager.particles), 0)

    def test_pygame_renderer_factory(self):
        renderer = make_renderer(RenderOptions(renderer="pygame"), (64, 64), "test")
        self.assertIsInstance(renderer, PygameRenderer)
        renderer.close()

    def test_opengl_fallback(self):
        renderer = make_renderer(
            RenderOptions(renderer="opengl"),
            (64, 64),
            "test",
            opengl_cls=BrokenOpenGLRenderer,
        )
        self.assertIsInstance(renderer, PygameRenderer)
        renderer.close()


if __name__ == "__main__":
    unittest.main()
