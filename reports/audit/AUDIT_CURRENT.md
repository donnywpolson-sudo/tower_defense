# Tower Defense Project Audit Prompt

You are auditing the local Tower Defense project at:

`C:\Users\donny\Desktop\tower_defense`

Goal: inspect the repository read-only and produce one concise, evidence-based audit report. Do not fix code, data, tests, docs, assets, build output, generated output, or reports unless the user explicitly asks for a single timestamped report file. Do not commit.

## Hard Rules

* Verify the local path and repo root before inspecting anything else. Stop if they are wrong.
* Record `git status --short` before and after checks.
* Treat every modified or untracked file as user work.
* Do not create, delete, rename, normalize, migrate, regenerate, reset, checkout, stash, commit, or revert anything.
* Do not install dependencies or run formatters.
* Do not run commands likely to write saves, logs, caches, bytecode, build output, or generated artifacts.
* Do not inspect generated output unless it is directly needed as audit evidence.
* Do not paste large source files or large command output.
* Evidence must be concise: path + line, function, class, config key, command, or test name when useful.
* Do not implement fixes.
* Do not recommend protected clone content. Translate the desired tower-defense feel into original tower names, enemies, maps, UI, upgrades, visuals, and audio.

## Repository Facts

* `tower_defense.py` is a tiny compatibility launcher.
* `main.py` is the web/Pygbag entry point.
* Most gameplay lives in `td_game/app.py`.
* Data, wave, map, rendering, assets, audio, particles, and crash logging live in `td_game/`.
* Generated assets and optional Kenney CC0 imports live in `assets/`.
* Validation/build scripts live in `tools/`.
* Tests live in `tests/`.

## Required Local Verification

Run from PowerShell:

```powershell
cd C:\Users\donny\Desktop\tower_defense
pwd
git rev-parse --show-toplevel
git status --short
Get-ChildItem -Force | Select-Object Mode,Length,LastWriteTime,Name
```

If `pwd` or `git rev-parse --show-toplevel` does not point at this repo, stop and report.

## Targeted Inspection

Read targeted files only:

* `AGENTS.md`
* `README.md`
* `requirements.txt`
* `tower_defense.py`
* `main.py`
* `td_game/app.py`
* `td_game/config.py`
* `td_game/data.py`
* `td_game/waves.py`
* `td_game/mapgen.py`
* `td_game/geometry.py`
* `td_game/rendering.py`
* `td_game/assets.py`
* `td_game/audio.py`
* `td_game/particles.py`
* `td_game/crash_logging.py`
* `tools/validate_assets.py`
* `tools/generate_assets.py`
* `tools/download_free_assets.py`
* `tools/build_web.py`
* `tools/build_desktop_launcher.ps1`
* targeted tests under `tests/`, especially `test_mapgen.py`, `test_tower_families.py`, `test_gameplay_smoke.py`, `test_signal_milestone.py`, `test_assets_audio.py`, `test_asset_pipeline.py`, `test_rendering.py`, and `test_crash_logging.py`
* `assets/asset_manifest.json`
* `assets/licenses/kenney_assets.md`
* top-level launcher helpers if present: `Open Local Version.cmd`, `Open Browser Version.url`

Skip `.venv/`, `.pytest_cache/`, `build/`, `dist/`, `tools/_asset_downloads/`, `__pycache__/`, `*.pyc`, binary files, and generated assets unless directly relevant.

## Search Terms

Use concise evidence searches:

```powershell
rg -n "TODO|FIXME|pass|NotImplemented|stub|tower|upgrade|wave|boss|research|reward|card|commander|paragon|mastery|placement|target|sell|refund|currency|lives|path|mapgen|projectile|sprite|animation|audio|music|settings|save|schema|validation|launcher|build|Signal Defense|Tower Defense|ransomware" AGENTS.md README.md requirements.txt tools td_game tests assets -g "!*.pyc" -g "!__pycache__/**"
rg -n "Bloons|BTD|PvZ|Plants vs Zombies|Kingdom Rush|RuneScape|OSRS|Pokemon" AGENTS.md README.md tools td_game tests assets -g "!*.pyc" -g "!__pycache__/**"
```

Report hits as concise evidence. Distinguish policy text, placeholder/fallback coverage, and unsafe gameplay/content drift.

## Safe Checks

Before validation, inspect `tools/validate_assets.py` and confirm it is read-only. If safe:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B tools\validate_assets.py
```

Run only targeted pytest checks that are useful for audit evidence and appear read-only. Do not run full pytest unless the user explicitly asks for it. Prefer one or a few of these: `tests/test_mapgen.py`, `tests/test_tower_families.py`, `tests/test_gameplay_smoke.py`, `tests/test_signal_milestone.py`, `tests/test_assets_audio.py`, `tests/test_asset_pipeline.py`, `tests/test_rendering.py`, `tests/test_crash_logging.py`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider tests\test_mapgen.py
```

If a direct game launch or visual check is needed, do it only when it is clearly safe and likely to add evidence; otherwise mark the area manually unverified.

After checks:

```powershell
git status --short
```

If the worktree changed, report it immediately and do not clean it up.

## Classification Required

For each audited system, classify it as exactly one of:

* fully implemented
* partially implemented
* partially wired
* present but unused
* stub/TODO
* missing
* manually unverified

Definitions:

* `fully implemented`: code, data, UI/reachability, and evidence support it.
* `partially implemented`: core logic exists, but important behavior or coverage is incomplete.
* `partially wired`: logic/data exists, but gameplay/UI reachability is incomplete or unclear.
* `present but unused`: module/data exists but no reachable caller or entry point was found.
* `stub/TODO`: placeholder, `pass`, TODO, or non-functional shell.
* `missing`: no meaningful implementation found.
* `manually unverified`: likely present, but requires runtime or visual confirmation.

If code or docs mention a feature but it is not reachable in play, do not mark it fully implemented.

## Systems To Audit

Audit implemented state, playability, tests, risks, and highest-yield improvements for:

* Core loop and UI: placement, branch choice, upgrades, selling, wave start, pause, speed, reward cards, research, victory/defeat, and resource flow.
* Tower families and aliases: `archer`, `sniper`, `machine_gun`, `cannon`, `frost`, `tesla`, `poison`, `barracks`, `support`, plus folded aliases like `flame`, `mortar`, and `gold`.
* Branch depth and progression: level 3 branch choice, paragon/mastery gates, late-game scaling, synergy, anti-air, splash, slow, boss pressure, and research gating.
* Wave system: enemy kinds, modifiers, commanders, bosses, boss protocols, preview/timeline, labels/stingers, difficulty curve, and spawn pacing.
* Map generation and pathing: static maps, generated switchback/turnaround maps, orthogonal segments, overlap, build corridors, spawn/end reachability, bounds, and theme readability.
* Combat/projectiles/effects: target selection, damage types, status effects, commander aura, split children, synergy damage, hit feedback, and readability.
* Economy/progression: money, lives, research points, costs, sell/refund, reward pacing, and scarcity.
* UI/HUD/input: placement ghost, range indicators, target priority, upgrade and branch panels, warnings, pause, and accessibility.
* Visuals/animation/assets/audio/style: sprites, particles, renderer backends, fallback art/audio, music, sound cues, placeholder gaps, and original theme fit.
* Settings/performance/rendering: Pygame/OpenGL fallback, scaling, framerate, input handling, and web/mobile readability.
* Diagnostics/crash handling: crash logging, error surfaces, and repro quality.
* Asset pipeline/licensing: generated assets, Kenney imports, manifest/license coverage, fallback behavior, and licensing drift.
* Tests: smoke, wave logic, tower families, map generation, rendering, audio, crash logging, and asset validation.
* Launcher/build/docs: `tower_defense.py`, `main.py`, `tools/build_web.py`, `tools/build_desktop_launcher.ps1`, `Open Local Version.cmd`, `Open Browser Version.url`, README command drift, and generated output boundaries.
* Originality/IP safety: protected-title drift, clone-like names/effects/maps/music/UI, and original tower-defense-safe content.

## Target Game Feel

Evaluate whether current systems support an original single-player tower defense with:

* clear tower placement and upgrade decisions
* readable waves, boss pressure, and useful previews
* distinct tower families with meaningful synergies
* resource pressure that makes sell/refund, research, and reward cards matter
* map/path readability and replayable build space
* strong audiovisual feedback for hits, upgrades, warnings, and wins/losses
* low-friction controls and readable UI at desktop and web/mobile sizes
* original names, lore, visuals, and audio rather than clone-like content

## Prioritization Rules

Rank recommendations by:

1. Failing validation/tests or asset/build compatibility risk.
2. Player value and clarity.
3. Improvements to the tower-placement / wave-clear / upgrade loop.
4. Low implementation risk and small scope.
5. Reuse of existing systems.
6. Testability.
7. Originality/IP safety.

Avoid broad rewrites, new dependencies, speculative architecture, and clone-like feature requests.

## Required Report Format

Output exactly:

```text
# Snapshot

* Local path:
* Repo root:
* Git status before:
* Git status after:
* Stack:
* Entry points:
* Run command:
* Test command:
* Asset validation command:
* Build command:
* Data files:
* Asset/license files:
* Checks run:
* Checks result:
* Worktree changed after checks:

# System Inventory

System | Status | Evidence | Notes

# Findings

Severity | Finding | Evidence | Why it matters | Recommended next step

# Tower Defense Feel Assessment

Area | Status | Evidence | Gap | Safe recommendation

# Originality/IP Safety

Risk | Evidence | Classification | Recommendation

# Tests And Validation

Check | Result | Evidence | Notes

# Manual Verification Needed

Manual check | Why | Steps

# Recommended Next Work

Rank | Feature/Fix | Why | Complexity | Risk | Files likely touched | Acceptance criteria | Suggested tests

# Next Codex Prompt

A scoped implementation prompt ready to paste. It must ask for one small, testable improvement and must repeat: do not copy protected content, preserve user work, and do not commit.
```
