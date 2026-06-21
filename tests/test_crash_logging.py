import tempfile
import unittest
from pathlib import Path

from td_game.config import BASE_DIR
from td_game.crash_logging import write_crash_log


class CrashLoggingTests(unittest.TestCase):
    def test_write_crash_log_records_state_and_latest_file(self):
        with tempfile.TemporaryDirectory(dir=BASE_DIR) as tmp:
            log_dir = Path(tmp)
            try:
                raise RuntimeError("forced crash")
            except RuntimeError as exc:
                crash_path = write_crash_log(
                    exc,
                    {"wave": 23, "counts": {"enemies": 12}},
                    log_dir=log_dir,
                    legacy_path=None,
                )

            self.assertIsNotNone(crash_path)
            self.assertTrue(crash_path.exists())
            latest = log_dir / "latest_crash.txt"
            self.assertTrue(latest.exists())
            text = latest.read_text(encoding="utf-8")
            self.assertIn("RuntimeError: forced crash", text)
            self.assertIn('"wave": 23', text)
            self.assertIn('"enemies": 12', text)


if __name__ == "__main__":
    unittest.main()
