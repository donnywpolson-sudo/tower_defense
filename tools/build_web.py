import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from td_game.config import HEIGHT, WIDTH

BUILD_ROOT = ROOT / "build"
STAGING_DIR = BUILD_ROOT / "pygbag_project" / "signal_defense"
WEB_DIR = BUILD_ROOT / "web"
GAME_ASPECT = WIDTH / HEIGHT
FULLSCREEN_MARKER = "signal-defense-fullscreen-style"
FULLSCREEN_STYLE = f"""
<style id="{FULLSCREEN_MARKER}">
  html, body {{
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #050807 !important;
  }}

  body {{
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  canvas.emscripten {{
    position: fixed !important;
    left: 50% !important;
    top: 50% !important;
    right: auto !important;
    bottom: auto !important;
    width: min(100vw, calc(100vh * {GAME_ASPECT:.8f})) !important;
    height: min(100vh, calc(100vw / {GAME_ASPECT:.8f})) !important;
    max-width: 100vw;
    max-height: 100vh;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
    transform: translate(-50%, -50%) !important;
    background: #050807 !important;
    image-rendering: auto;
  }}

  #infobox {{
    background: rgba(5, 8, 7, 0.88) !important;
    color: #e8f7e8 !important;
    border: 1px solid #6de08a;
    border-radius: 6px;
  }}
</style>
"""


def ensure_within_root(path):
    resolved = path.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError(f"Refusing to operate outside workspace: {resolved}")
    return resolved


def clean_dir(path):
    resolved = ensure_within_root(path)
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=True)


def copy_tree(source, destination, *extra_ignores):
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".pytest_cache", *extra_ignores),
        dirs_exist_ok=True,
    )


def stage_project():
    clean_dir(STAGING_DIR)
    shutil.copy2(ROOT / "main.py", STAGING_DIR / "main.py")
    copy_tree(ROOT / "td_game", STAGING_DIR / "td_game")
    copy_tree(ROOT / "assets", STAGING_DIR / "assets", "*.wav")
    (STAGING_DIR / ".nojekyll").write_text("", encoding="utf-8")
    return STAGING_DIR


def build_with_pygbag(stage_dir):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pygbag",
            "--build",
            "--ume_block",
            "0",
            "--width",
            str(WIDTH),
            "--height",
            str(HEIGHT),
            str(stage_dir),
        ],
        cwd=ROOT,
        check=True,
    )
    pygbag_web_dir = stage_dir / "build" / "web"
    if not pygbag_web_dir.exists():
        raise RuntimeError(f"Pygbag did not create expected output: {pygbag_web_dir}")

    clean_dir(WEB_DIR)
    copy_tree(pygbag_web_dir, WEB_DIR)
    patch_web_index(WEB_DIR)
    return WEB_DIR


def patch_web_index(web_dir):
    index_path = web_dir / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html = html.replace(
        'platform.document.body.style.background = "#7f7f7f"',
        'platform.document.body.style.background = "#050807"',
    )
    if FULLSCREEN_MARKER not in html:
        html = html.replace("</head>", f"{FULLSCREEN_STYLE}\n</head>")
    index_path.write_text(html, encoding="utf-8")


def copy_existing_web_build():
    pygbag_web_dir = STAGING_DIR / "build" / "web"
    if not pygbag_web_dir.exists():
        raise RuntimeError(f"No existing Pygbag output found: {pygbag_web_dir}")
    if not (pygbag_web_dir / "index.html").exists():
        raise RuntimeError(f"Existing Pygbag output is incomplete: {pygbag_web_dir / 'index.html'}")

    clean_dir(WEB_DIR)
    copy_tree(pygbag_web_dir, WEB_DIR)
    patch_web_index(WEB_DIR)
    return WEB_DIR


def main(argv=None):
    parser = argparse.ArgumentParser(description="Stage and build Signal Defense for web/Pygbag.")
    parser.add_argument("--build", action="store_true", help="Run Pygbag after staging.")
    parser.add_argument("--copy-existing", action="store_true", help="Copy an already-built Pygbag web folder to build/web.")
    args = parser.parse_args(argv)

    if args.copy_existing:
        web_dir = copy_existing_web_build()
        print(f"Copied existing web output: {web_dir}")
        return

    stage_dir = stage_project()
    print(f"Staged web project: {stage_dir}")
    if args.build:
        web_dir = build_with_pygbag(stage_dir)
        print(f"Built web output: {web_dir}")
    else:
        print("Install pygbag and run this script with --build to create build/web.")


if __name__ == "__main__":
    main()
