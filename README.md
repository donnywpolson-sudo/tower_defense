# Tower Defense

A Python/Pygame tower defense game with grid building, weapon tower upgrade trees, boss waves, research upgrades, generated pixel-art assets, and sound effects.

## Run

Double-click `Play Tower Defense.lnk` to start the game without opening a command prompt.

For development, run:

```powershell
.\.venv\Scripts\python.exe tower_defense.py
```

The root `tower_defense.py` file is a tiny compatibility launcher. The game code lives in `td_game/`.

## Regenerate Assets

```powershell
.\.venv\Scripts\python.exe tools\generate_assets.py
```

## Project Layout

```text
tower_defense.py          # stable Python entry point
Play Tower Defense.lnk    # player-facing double-click launcher
td_game/                  # game package
assets/                   # generated sprites and sounds
tools/generate_assets.py  # local asset generator
```
