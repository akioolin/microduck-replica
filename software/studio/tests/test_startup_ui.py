"""Browser presentation of startup diagnostics (Node >=22)."""
import shutil
import subprocess
import unittest
from pathlib import Path

NODE = shutil.which("node")
ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(NODE, "Node >=22 is required for startup UI tests")
class StartupUiTest(unittest.TestCase):
    def test_startup_device_labels(self):
        version = subprocess.run([NODE, "--version"], capture_output=True, text=True, timeout=10)
        if int(version.stdout.strip().lstrip("v").split(".")[0]) < 22:
            self.skipTest("Node >=22 is required for ES module detection")
        result = subprocess.run([NODE, "--test", str(ROOT / "tests/startup_ui_unit.mjs")],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
