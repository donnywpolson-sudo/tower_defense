from __future__ import annotations

import json
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from .config import BASE_DIR


def write_crash_log(exc, state=None, log_dir=None, legacy_path=BASE_DIR / "crash_log.txt"):
    """Write a timestamped crash report and a latest-crash pointer."""
    timestamp = datetime.now(timezone.utc)
    stamp = timestamp.strftime("%Y%m%d-%H%M%S")
    target_dir = Path(log_dir) if log_dir is not None else BASE_DIR / "crash_logs"
    state_text = json.dumps(state or {}, indent=2, sort_keys=True, default=repr)
    report = "\n".join(
        [
            "Signal Defense crash report",
            f"timestamp_utc: {timestamp.isoformat()}",
            f"python: {sys.version.replace(chr(10), ' ')}",
            f"platform: {platform.platform()}",
            f"executable: {sys.executable}",
            f"argv: {sys.argv}",
            "",
            "state:",
            state_text,
            "",
            "traceback:",
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        ]
    )

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        crash_path = target_dir / f"crash-{stamp}.txt"
        crash_path.write_text(report, encoding="utf-8")
        (target_dir / "latest_crash.txt").write_text(report, encoding="utf-8")
        if legacy_path is not None:
            Path(legacy_path).write_text(report, encoding="utf-8")
        return crash_path
    except Exception:
        if legacy_path is not None:
            try:
                Path(legacy_path).write_text(report, encoding="utf-8")
            except Exception:
                pass
        return None
