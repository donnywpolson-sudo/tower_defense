import json
import os
from dataclasses import dataclass
from pathlib import Path
import shutil
import sys
import urllib.error
import urllib.request
import zipfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from validate_assets import (
    EFFECT_ASSETS,
    ENEMY_FRAMES,
    ENEMY_TYPES,
    PROJECTILE_TYPES,
    TERRAIN_ASSETS,
    TOWER_FRAMES,
    TOWER_TYPES,
    missing_required_assets,
)


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CACHE = ROOT / "tools" / "_asset_downloads"
LICENSE_DIR = ASSETS / "licenses"
MANIFEST_PATH = ASSETS / "asset_manifest.json"

LICENSE_NAME = "Creative Commons CC0"
LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"

PACKS = {
    "tower_defense_top_down": {
        "name": "Kenney Tower Defense Top-Down",
        "page": "https://kenney.nl/assets/tower-defense-top-down",
        "url": "https://kenney.nl/media/pages/assets/tower-defense-top-down/729844df28-1677693738/kenney_tower-defense-top-down.zip",
    },
    "tower_defense": {
        "name": "Kenney Tower Defense",
        "page": "https://kenney.nl/assets/tower-defense",
        "url": "https://kenney.nl/media/pages/assets/tower-defense/39d625c6b5-1677699069/kenney_tower-defense.zip",
    },
    "interface_sounds": {
        "name": "Kenney Interface Sounds",
        "page": "https://kenney.nl/assets/interface-sounds",
        "url": "https://kenney.nl/media/pages/assets/interface-sounds/fa43c1dd4d-1677589452/kenney_interface-sounds.zip",
    },
    "impact_sounds": {
        "name": "Kenney Impact Sounds",
        "page": "https://kenney.nl/assets/impact-sounds",
        "url": "https://kenney.nl/media/pages/assets/impact-sounds/87b4ddecda-1677589768/kenney_impact-sounds.zip",
    },
}

ASSET_FOLDERS = (
    "sprites/towers",
    "sprites/enemies",
    "sprites/terrain",
    "sprites/projectiles",
    "sprites/effects",
    "sprites/ui",
    "sounds/towers",
    "sounds/enemies",
    "sounds/ui",
    "sounds/music",
    "licenses",
)


@dataclass(frozen=True)
class AssetRequest:
    destination: Path
    kind: str
    packs: tuple
    keywords: tuple
    target_size: tuple | None = None
    suffixes: tuple = (".png",)
    min_score: int = 24
    exact_source: str | None = None


def ensure_dirs():
    for folder in ASSET_FOLDERS:
        (ASSETS / folder).mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)


def download_pack(slug, pack):
    zip_path = CACHE / f"{slug}.zip"
    if zip_path.exists() and zip_path.stat().st_size > 0:
        return zip_path, "cached"

    request = urllib.request.Request(pack["url"], headers={"User-Agent": "tower-defense-asset-importer/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            zip_path.write_bytes(response.read())
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Could not download {pack['name']} from {pack['url']}: {exc}") from exc

    return zip_path, "downloaded"


def safe_extract(zip_path, target_dir):
    if target_dir.exists():
        return "cached"

    target_dir.mkdir(parents=True, exist_ok=True)
    target_root = target_dir.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            destination = (target_dir / member.filename).resolve()
            if target_root not in destination.parents and destination != target_root:
                raise RuntimeError(f"Unsafe archive path skipped: {member.filename}")
            archive.extract(member, target_dir)
    return "extracted"


def normalized_text(path):
    return path.as_posix().replace("_", " ").replace("-", " ").lower()


def build_requests():
    requests = []

    for tower_type in TOWER_TYPES:
        for frame in TOWER_FRAMES:
            destination = Path("sprites") / "towers" / f"{tower_type}_{frame}.png"
            requests.append(
                AssetRequest(
                    destination=destination,
                    kind="image",
                    packs=("tower_defense_top_down", "tower_defense"),
                    keywords=("tower", tower_type.replace("_", " "), frame.replace("_", " ")),
                    target_size=(48, 48),
                )
            )

    for enemy_type in ENEMY_TYPES:
        for frame in ENEMY_FRAMES:
            filename = f"{enemy_type}.png" if frame == "base" else f"{enemy_type}_{frame}.png"
            requests.append(
                AssetRequest(
                    destination=Path("sprites") / "enemies" / filename,
                    kind="image",
                    packs=("tower_defense_top_down", "tower_defense"),
                    keywords=("enemy", "unit", enemy_type.replace("_", " "), frame.replace("_", " ")),
                    target_size=(64, 64) if enemy_type == "boss" else (32, 32),
                )
            )
    requests.append(
        AssetRequest(
            destination=Path("sprites") / "enemies" / "boss_rage.png",
            kind="image",
            packs=("tower_defense_top_down", "tower_defense"),
            keywords=("boss", "enemy", "unit", "rage"),
            target_size=(64, 64),
        )
    )

    for terrain_name in TERRAIN_ASSETS:
        requests.append(
            AssetRequest(
                destination=Path("sprites") / "terrain" / f"{terrain_name}.png",
                kind="image",
                packs=("tower_defense_top_down", "tower_defense"),
                keywords=("terrain", "tile", "road" if "road" in terrain_name else "grass", terrain_name.replace("_", " ")),
                target_size=(54, 54),
            )
        )
    for marker_name in ("spawn_gate", "base_gate"):
        requests.append(
            AssetRequest(
                destination=Path("sprites") / "terrain" / f"{marker_name}.png",
                kind="image",
                packs=("tower_defense_top_down", "tower_defense"),
                keywords=("tower", "base", "gate", marker_name.replace("_", " ")),
                target_size=(48, 48),
            )
        )

    for projectile_type in PROJECTILE_TYPES:
        requests.append(
            AssetRequest(
                destination=Path("sprites") / "projectiles" / f"{projectile_type}.png",
                kind="image",
                packs=("tower_defense_top_down", "tower_defense"),
                keywords=("projectile", "weapon", "bullet", projectile_type.replace("_", " ")),
                target_size=(24, 24),
            )
        )

    for effect_name in EFFECT_ASSETS:
        requests.append(
            AssetRequest(
                destination=Path("sprites") / "effects" / f"{effect_name}.png",
                kind="image",
                packs=("tower_defense_top_down", "tower_defense"),
                keywords=("effect", effect_name.replace("_", " ")),
                target_size=(64, 64),
            )
        )

    decor_map = {
        "sprites/terrain/decor_tree.png": "PNG/Details/trees_1.png",
        "sprites/terrain/decor_rock.png": "PNG/Details/rocks_1.png",
        "sprites/terrain/decor_crystal.png": "PNG/Details/crystals_1.png",
    }
    for destination, exact_source in decor_map.items():
        requests.append(
            AssetRequest(
                destination=Path(destination),
                kind="image",
                packs=("tower_defense",),
                keywords=("decor",),
                target_size=(36, 36),
                min_score=0,
                exact_source=exact_source,
            )
        )

    sound_map = {
        "sounds/ui/build.ogg": ("interface_sounds", "Audio/select_001.ogg", ("select",)),
        "sounds/ui/upgrade.ogg": ("interface_sounds", "Audio/confirmation_003.ogg", ("confirmation",)),
        "sounds/ui/sell.ogg": ("interface_sounds", "Audio/back_001.ogg", ("back",)),
        "sounds/ui/wave.ogg": ("interface_sounds", "Audio/open_003.ogg", ("open",)),
        "sounds/ui/wave_fast.ogg": ("interface_sounds", "Audio/tick_004.ogg", ("tick",)),
        "sounds/ui/wave_tank.ogg": ("impact_sounds", "Audio/impactWood_heavy_000.ogg", ("impact", "heavy", "wood")),
        "sounds/ui/wave_shield.ogg": ("impact_sounds", "Audio/impactMetal_heavy_000.ogg", ("impact", "heavy", "metal")),
        "sounds/ui/wave_flying.ogg": ("interface_sounds", "Audio/open_004.ogg", ("open",)),
        "sounds/ui/wave_boss.ogg": ("impact_sounds", "Audio/impactBell_heavy_000.ogg", ("impact", "heavy", "bell")),
        "sounds/ui/wave_complete.ogg": ("interface_sounds", "Audio/confirmation_004.ogg", ("confirmation",)),
        "sounds/enemies/death.ogg": ("impact_sounds", "Audio/impactPunch_medium_000.ogg", ("impact", "punch")),
        "sounds/enemies/leak.ogg": ("impact_sounds", "Audio/impactSoft_heavy_000.ogg", ("impact", "soft")),
        "sounds/enemies/boss_spawn.ogg": ("impact_sounds", "Audio/impactWood_heavy_001.ogg", ("impact", "wood")),
        "sounds/enemies/boss_death.ogg": ("impact_sounds", "Audio/impactPlate_heavy_004.ogg", ("impact", "plate")),
        "sounds/enemies/shield_break.ogg": ("impact_sounds", "Audio/impactMetal_medium_000.ogg", ("impact", "metal")),
        "sounds/towers/archer.ogg": ("impact_sounds", "Audio/impactWood_light_000.ogg", ("impact", "wood")),
        "sounds/towers/sniper.ogg": ("impact_sounds", "Audio/impactMetal_medium_002.ogg", ("impact", "metal")),
        "sounds/towers/machine_gun.ogg": ("impact_sounds", "Audio/impactTin_medium_000.ogg", ("impact", "tin")),
        "sounds/towers/cannon.ogg": ("impact_sounds", "Audio/impactSoft_heavy_004.ogg", ("impact", "soft")),
        "sounds/towers/frost.ogg": ("impact_sounds", "Audio/impactGlass_light_002.ogg", ("impact", "glass")),
        "sounds/towers/tesla.ogg": ("interface_sounds", "Audio/glitch_001.ogg", ("glitch",)),
        "sounds/towers/poison.ogg": ("impact_sounds", "Audio/impactSoft_medium_000.ogg", ("impact", "soft")),
        "sounds/towers/flame.ogg": ("impact_sounds", "Audio/impactGeneric_light_000.ogg", ("impact", "generic")),
        "sounds/towers/mortar.ogg": ("impact_sounds", "Audio/impactSoft_heavy_001.ogg", ("impact", "soft")),
        "sounds/towers/gold.ogg": ("interface_sounds", "Audio/confirmation_001.ogg", ("confirmation",)),
        "sounds/towers/freeze.ogg": ("impact_sounds", "Audio/impactGlass_medium_000.ogg", ("impact", "glass")),
        "sounds/towers/chain.ogg": ("interface_sounds", "Audio/glitch_002.ogg", ("glitch",)),
    }
    for destination, (pack_slug, exact_source, keywords) in sound_map.items():
        requests.append(
            AssetRequest(
                destination=Path(destination),
                kind="sound",
                packs=(pack_slug,),
                keywords=keywords,
                suffixes=(".ogg",),
                min_score=0,
                exact_source=exact_source,
            )
        )

    return requests


def collect_candidates(extract_dirs):
    candidates = {}
    for slug, folder in extract_dirs.items():
        candidates[slug] = [
            path
            for path in folder.rglob("*")
            if path.is_file()
            and "__MACOSX" not in path.parts
            and path.suffix.lower() in {".png", ".wav", ".ogg"}
        ]
    return candidates


def score_candidate(path, request):
    text = normalized_text(path.relative_to(path.anchor if path.is_absolute() else Path(".")))
    score = 0

    for keyword in request.keywords:
        keyword = keyword.lower()
        if keyword and keyword in text:
            score += 12

    if request.destination.parts[1] in text:
        score += 6
    if request.kind == "image" and "png" in text:
        score += 1
    if request.kind == "sound" and path.suffix.lower() == ".wav":
        score += 3
    if "license" in text or "preview" in text or "sample" in text:
        score -= 20
    return score


def find_source(request, candidates, used_sources):
    if request.exact_source:
        wanted = request.exact_source.replace("\\", "/").lower()
        for pack_slug in request.packs:
            for candidate in candidates.get(pack_slug, []):
                if candidate in used_sources:
                    continue
                candidate_text = candidate.relative_to(CACHE / pack_slug).as_posix().lower()
                if candidate_text == wanted:
                    return candidate, pack_slug, 999
        return None, None, None

    ranked = []
    for pack_index, pack_slug in enumerate(request.packs):
        for candidate in candidates.get(pack_slug, []):
            if candidate.suffix.lower() not in request.suffixes:
                continue
            if candidate in used_sources:
                continue
            score = score_candidate(candidate, request) - pack_index
            ranked.append((score, candidate, pack_slug))

    if not ranked:
        return None, None, None

    ranked.sort(key=lambda item: (-item[0], item[1].as_posix()))
    best_score, best_path, best_pack = ranked[0]
    if best_score < request.min_score:
        return None, None, None
    return best_path, best_pack, best_score


def image_bytes(source, target_size):
    surface = pygame.image.load(str(source))
    if target_size:
        surface = pygame.transform.scale(surface, target_size)
    normalized = CACHE / "_normalized.png"
    pygame.image.save(surface, normalized)
    return normalized.read_bytes()


def sound_bytes(source):
    return source.read_bytes()


def write_if_changed(destination, content):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() == content:
        return "skipped"
    destination.write_bytes(content)
    return "copied"


def write_license_file():
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Kenney Assets",
        "",
        "This project may include curated assets imported from official Kenney asset packs.",
        "",
        "License: Creative Commons CC0 1.0 Universal",
        f"License URL: {LICENSE_URL}",
        "",
        "Source packs:",
    ]
    for pack in PACKS.values():
        lines.append(f"- {pack['name']}: {pack['page']}")
    lines.extend(
        [
            "",
            "Attribution is not required for CC0, but crediting Kenney is appreciated.",
            "Do not add ripped, trademarked, or unclear-license assets to this project.",
        ]
    )
    (LICENSE_DIR / "kenney_assets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(entries, skipped=None):
    manifest = {
        "license": LICENSE_NAME,
        "license_url": LICENSE_URL,
        "sources": {
            slug: {
                "name": pack["name"],
                "page": pack["page"],
                "url": pack["url"],
            }
            for slug, pack in PACKS.items()
        },
        "assets": entries,
        "skipped": skipped or [],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_import():
    ensure_dirs()
    write_license_file()

    print("Downloading official Kenney CC0 asset packs...")
    extract_dirs = {}
    downloaded = []
    failed = []
    for slug, pack in PACKS.items():
        try:
            zip_path, download_status = download_pack(slug, pack)
            extract_dir = CACHE / slug
            extract_status = safe_extract(zip_path, extract_dir)
            extract_dirs[slug] = extract_dir
            downloaded.append((slug, download_status, extract_status))
            print(f"  {pack['name']}: {download_status}, {extract_status}")
        except RuntimeError as exc:
            failed.append(str(exc))
            print(f"  {pack['name']}: failed")

    if not extract_dirs:
        write_manifest({}, [])
        print("No Kenney packs were available. Generated fallback assets are still untouched.")
        for error in failed:
            print(f"  {error}")
        return 1

    pygame.init()
    candidates = collect_candidates(extract_dirs)
    used_sources = set()
    copied = 0
    skipped = 0
    missing = []
    manifest_entries = {}

    for request in build_requests():
        source, pack_slug, score = find_source(request, candidates, used_sources)
        if source is None:
            missing.append(request.destination.as_posix())
            continue

        destination = ASSETS / request.destination
        try:
            content = image_bytes(source, request.target_size) if request.kind == "image" else sound_bytes(source)
        except pygame.error:
            missing.append(request.destination.as_posix())
            continue

        result = write_if_changed(destination, content)
        if result == "copied":
            copied += 1
        else:
            skipped += 1

        used_sources.add(source)
        manifest_entries[request.destination.as_posix()] = {
            "local_path": f"assets/{request.destination.as_posix()}",
            "source_pack": PACKS[pack_slug]["name"],
            "source_page": PACKS[pack_slug]["page"],
            "license": LICENSE_NAME,
            "license_url": LICENSE_URL,
            "original_path": source.relative_to(CACHE / pack_slug).as_posix(),
            "selection_score": score,
        }

    write_manifest(
        manifest_entries,
        [
            {
                "local_path": f"assets/{path}",
                "reason": "No matching Kenney source found; generated fallback kept.",
            }
            for path in missing
        ],
    )
    validation_missing = missing_required_assets()

    print("")
    print("Import summary:")
    print(f"  Copied: {copied}")
    print(f"  Skipped unchanged: {skipped}")
    print(f"  Missing Kenney matches, fallback kept: {len(missing)}")
    for path in missing[:25]:
        print(f"    fallback kept: assets/{path}")
    if len(missing) > 25:
        print(f"    ... {len(missing) - 25} more recorded in assets/asset_manifest.json")
    print(f"  Manifest entries: {len(manifest_entries)}")
    print(f"  Download/cache folder: {CACHE}")
    if failed:
        print("  Failed packs:")
        for error in failed:
            print(f"    {error}")
    if validation_missing:
        print("  Required files still missing:")
        for path in validation_missing:
            print(f"    assets/{path.as_posix()}")
        return 1

    print("  Required asset validation: OK")
    return 0


def main():
    try:
        return run_import()
    except zipfile.BadZipFile as exc:
        print(f"Downloaded file was not a valid ZIP: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
