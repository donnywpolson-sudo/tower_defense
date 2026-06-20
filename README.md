# Tower Defense

A Python/Pygame tower defense game with grid building, weapon tower upgrade trees, boss waves, research upgrades, generated pixel-art assets, and sound effects.

## Run

Double-click `Play Tower Defense.lnk` to start the game without opening a command prompt.

For development, run:

```powershell
.\.venv\Scripts\python.exe tower_defense.py
```

Use a specific renderer:

```powershell
.\.venv\Scripts\python.exe tower_defense.py --renderer pygame
.\.venv\Scripts\python.exe tower_defense.py --renderer opengl
```

OpenGL mode uses ModernGL. If ModernGL is missing or the OpenGL context fails, the game prints a warning and falls back to the normal Pygame renderer.

Install packages:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Optional graphics flags:

```powershell
.\.venv\Scripts\python.exe tower_defense.py --disable-glow --disable-particles --disable-screen-shake
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
