"""Effect boundary for future extraction.

The current visual effect classes are runtime-coupled to td_game.app. This
module exposes the intended package location without duplicating stateful code.
"""

EFFECT_CLASS_NAMES = ("BurstEffect", "SparkEffect", "LightningEffect", "FloatingTextEffect")


def __getattr__(name):
    if name in EFFECT_CLASS_NAMES:
        from . import app

        return getattr(app, name)
    raise AttributeError(name)
