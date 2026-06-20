"""Entity boundary for future extraction.

The active pygame entity classes still live in td_game.app because they use the
runtime surface, global lists, and audio callbacks directly. Keeping this module
small avoids a risky behavior rewrite while preserving a clean package target
for the next extraction step.
"""

ENTITY_CLASS_NAMES = ("Enemy", "Tower", "Projectile")


def __getattr__(name):
    if name in ENTITY_CLASS_NAMES:
        from . import app

        return getattr(app, name)
    raise AttributeError(name)
