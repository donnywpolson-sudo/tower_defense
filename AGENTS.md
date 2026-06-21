# tower_defense instructions

## Project Facts

* Stack: Python, Pygame, optional ModernGL renderer, pytest, Pygbag web build.
* Run command: `.\.venv\Scripts\python.exe tower_defense.py`.
* Renderer variants: `.\.venv\Scripts\python.exe tower_defense.py --renderer pygame` and `.\.venv\Scripts\python.exe tower_defense.py --renderer opengl`.
* Test command: `.\.venv\Scripts\python.exe -m pytest`.
* Main source: `td_game/`.
* Main entry points: `tower_defense.py`, `main.py`, and `td_game/app.py`.
* Tests: `tests/`.
* Asset tools: `tools/generate_assets.py`, `tools/download_free_assets.py`, and `tools/validate_assets.py`.
* Web build: `.\.venv\Scripts\python.exe tools\build_web.py --build`, output under `build/web`.

## Repository Rules

* Check `git status --short` before editing.
* Work only in this repo unless explicitly asked.
* Do not overwrite user work or revert unrelated changes.
* Do not stage, commit, delete, move, or rename files unless explicitly asked.
* Keep changes small, reviewable, and focused on the requested behavior.
* Do not add dependencies unless clearly justified and reflected in `requirements.txt`.
* Do not add generated artifacts unless the task specifically requires them.

## Implementation Rules

Prefer:

* Small playable improvements over broad rewrites.
* Reusing existing systems in `td_game/` before adding new architecture.
* Clear separation between gameplay logic, data/config, rendering, assets, audio, and tests.
* Deterministic, repo-relative scripts and tests.
* Simple, readable code over clever compact code.

Avoid:

* Big-bang rewrites of `td_game/app.py`.
* Opportunistic refactors outside the touched behavior.
* Hardcoded one-off content when existing data/config structures can be extended.
* Breaking the stable `tower_defense.py` entry point.

## Gameplay And UI Priorities

When choosing implementation details, prioritize:

1. Clear tower placement, upgrades, targeting, and wave feedback.
2. Readable visuals at desktop and web/mobile sizes.
3. Smooth performance before adding heavier effects.
4. Boss waves, research upgrades, tower families, and progression clarity.
5. Fast manual verification in the running game.

## Asset And Licensing Rules

* Use original generated assets or clearly licensed assets only.
* Kenney imports must come from the project tooling and preserve/update `assets/licenses/kenney_assets.md` and `assets/asset_manifest.json` when relevant.
* Do not add ripped assets, trademarked game assets, Bloons assets, RuneScape assets, Pokemon assets, or assets with unclear licensing.
* When changing asset paths or manifests, run the asset validator if available.

## Testing Rules

When changing code:

* Run the narrowest relevant pytest test first.
* Run `.\.venv\Scripts\python.exe -m pytest` for broad gameplay/system changes when practical.
* Run `.\.venv\Scripts\python.exe tools\validate_assets.py` when changing assets, asset manifests, or asset loading paths.
* Provide manual game check steps for visual, input, rendering, audio, or balance changes.

## Output Format For Code Changes

Use this compact shape by default:

```md
Changed:
- `path/file.ext`: what changed

Validation:
- Command: result

Manual check:
- Steps or not run, with reason

Notes:
- Risks, pre-existing dirty files, or follow-ups
```