import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import download_free_assets
import validate_assets


class AssetPipelineTests(unittest.TestCase):
    def test_required_assets_are_present(self):
        self.assertEqual(validate_assets.missing_required_assets(), [])

    def test_downloader_uses_official_kenney_cc0_sources(self):
        self.assertEqual(download_free_assets.LICENSE_NAME, "Creative Commons CC0")
        self.assertTrue(download_free_assets.PACKS)

        for pack in download_free_assets.PACKS.values():
            self.assertTrue(pack["page"].startswith("https://kenney.nl/assets/"))
            self.assertTrue(pack["url"].startswith("https://kenney.nl/media/pages/assets/"))
            self.assertTrue(pack["url"].endswith(".zip"))

    def test_downloader_asset_map_targets_existing_game_paths(self):
        requests = download_free_assets.build_requests()
        destinations = {request.destination.as_posix() for request in requests}

        self.assertIn("sprites/towers/archer_idle.png", destinations)
        self.assertIn("sprites/enemies/normal.png", destinations)
        self.assertIn("sprites/terrain/road.png", destinations)
        self.assertIn("sprites/projectiles/cannon.png", destinations)
        self.assertIn("sounds/ui/build.ogg", destinations)
        self.assertIn("sounds/towers/cannon.ogg", destinations)


if __name__ == "__main__":
    unittest.main()
