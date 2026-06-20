from pathlib import Path
import traceback

from td_game.app import run


if __name__ == "__main__":
    try:
        run()
    except SystemExit:
        raise
    except Exception:
        Path("crash_log.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
