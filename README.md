# Tower Defense

A Python/Pygame tower defense game with grid building, weapon tower upgrade trees, boss waves, research upgrades, polished generated assets, and sound effects.

## Run

Double-click `C:\Users\donny\Desktop\Play Tower Defense.exe` to start the game without opening a command prompt.

To rebuild the Desktop launcher:

```powershell
.\tools\build_desktop_launcher.ps1
```

To validate the launcher without starting the game:

```powershell
& "$env:USERPROFILE\Desktop\Play Tower Defense.exe" --check
```

For development, run:

```powershell
.\.venv\Scripts\python.exe tower_defense.py
```

## Play On iPhone

The project includes a Pygbag web build path so the game can run in Safari on iPhone.

Local web build:

```powershell
.\.venv\Scripts\python.exe -m pip install pygbag
.\.venv\Scripts\python.exe tools\build_web.py --build
```

After the build completes, Pygbag creates the browser version in `build/web`.

GitHub Pages deployment:

1. Push this repository to GitHub.
2. In the GitHub repository, open Settings -> Pages.
3. Set Build and deployment Source to GitHub Actions.
4. Run the "Deploy Signal Defense Web" workflow, or push to `main`/`master`.
5. Open the deployed Pages URL on your iPhone.
6. In Safari, use Share -> Add to Home Screen.

For best playability, rotate the iPhone to landscape. The desktop launcher and normal Python entry point still work.

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

The root `tower_defense.py` file is a tiny compatibility launcher. Most active gameplay still lives in `td_game/app.py`; smaller helper modules hold data, config, geometry, rendering, particles, assets, audio, and wave helpers.

## Regenerate Assets

```powershell
.\.venv\Scripts\python.exe tools\generate_assets.py
```

This creates local placeholder sprites and sounds. These files are original generated assets and are also the fallback if external assets are missing.

## Download Free Kenney Assets

Optional CC0 assets can be imported from Kenney's official site:

```powershell
.\.venv\Scripts\python.exe tools\download_free_assets.py
.\.venv\Scripts\python.exe tools\validate_assets.py
```

The importer downloads official Kenney ZIP packs into `tools/_asset_downloads/`, extracts them locally, and copies curated files into the existing `assets/` paths used by the game. It is safe to rerun.

Kenney assets used by this project are Creative Commons CC0. Attribution is not required, but crediting Kenney is appreciated. License/source notes are written to `assets/licenses/kenney_assets.md`, and imported files are tracked in `assets/asset_manifest.json`.

Do not add ripped assets, trademarked game assets, RuneScape assets, Bloons assets, Pokémon assets, or anything with unclear licensing.

## Project Layout

```text
tower_defense.py          # stable Python entry point
tools/build_desktop_launcher.ps1  # builds the Desktop EXE launcher
td_game/app.py            # main loop, entities, UI, and gameplay integration
td_game/config.py         # constants and tuning values
td_game/data.py           # tower, map, upgrade, and mutation data
td_game/waves.py          # wave preview/count helpers
td_game/rendering.py      # Pygame/OpenGL presentation backends
td_game/assets.py         # image/sound loading helpers
td_game/audio.py          # generated tone fallback helper
assets/                   # generated sprites and sounds used by the game
tools/generate_assets.py  # local asset generator
tools/download_free_assets.py  # optional Kenney CC0 asset importer
tools/validate_assets.py       # required asset path validator
tests/                    # lightweight smoke tests
```
