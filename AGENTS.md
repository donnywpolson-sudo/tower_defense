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

## Workflow

* Minimize tokens, reads, edits, commands, and output. Make the smallest safe change.
* Check `git status --short` before editing.
* Implement directly when clear; plan only for broad or risky work.
* Ask only to avoid wrong or destructive changes.
* Read targeted files only and search before opening many files.
* Skip generated, vendor, cache, build, data, log, and binary files unless relevant.
* Read files directly by path instead of asking for pasted logs, reports, or full output.
* Use short summaries instead of long copied output; ask for full logs only when a short summary is not enough.
* For multi-step work, read `CODEX_HANDOFF.md` first if it exists and update it at the end of the run with what changed, files changed, commands run, test results, remaining work, and the next recommended step. Do not create or update it for simple one-shot tasks.

## Scope Control

* Work only in this repo unless explicitly asked.
* Reuse existing patterns and preserve behavior and APIs unless the task requires changing them.
* Avoid rewrites, unrelated changes, speculative future work, and new dependencies unless clearly justified and reflected in `requirements.txt`.
* Do not add or modify secrets, credentials, lockfiles, migrations, or generated artifacts, and do not delete user work unless required or explicitly requested.
* Do not overwrite, revert, stage, commit, delete, move, or rename files unless explicitly asked.
* Ask before destructive operations.
* Keep changes small, reviewable, and focused on the requested behavior.

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

* Run the narrowest relevant pytest test first; broaden only when the change warrants it.
* Run `.\.venv\Scripts\python.exe -m pytest` for broad gameplay/system changes when practical.
* Run `.\.venv\Scripts\python.exe tools\validate_assets.py` when changing assets, asset manifests, or asset loading paths.
* Provide manual game check steps for visual, input, rendering, audio, or balance changes.
* If checks are run or cannot run, mention only important failures or unresolved risks under `Notes/blockers`.

## Output Format For Code Changes

Use this compact shape by default:

Changed:
- `path/file.ext`: what changed

Validation:
- Command: result

Manual check:
- Steps or not run, with reason

Notes:
- Risks, pre-existing dirty files, or follow-ups

## Final output

This section overrides any earlier Output Format, Tests, Validation, Manual Check, Added/Removed/Modified, or reporting sections in this file.

Final output only, using exactly these sections in this order:

## Changed
* Files changed and concise purpose, or "None."

## Notes/blockers
* Remaining risks, blockers, preserved user work, failed checks if important, or important caveats.
* Write "None." if there are no meaningful notes/blockers.

## Next
* The single most useful next action, or "None."

## Metrics
* Elapsed time: report if available from the runtime or command wrapper; otherwise write "not available to agent".
* Token usage: report final token usage if available from Codex runtime/tool output; otherwise write "not available to agent".

Do not estimate or fabricate elapsed time or token usage.
Do not include Tests, Validation, Manual Check, Why, Added, Removed, or Modified sections unless explicitly requested.
