"""Publication must require executed target-code tests on both architectures."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/compare-reports.py"


class ReportRequirements(unittest.TestCase):
    def compare(self, arm, amd):
        with tempfile.TemporaryDirectory() as directory:
            files = [Path(directory) / name for name in ["arm.json", "amd.json"]]
            for path, report in zip(files, [arm, amd]):
                path.write_text(json.dumps(report))
            return subprocess.run([sys.executable, str(SCRIPT), *map(str, files)], capture_output=True, text=True)

    def reports(self):
        common = {"passed": True, "samples": [{"sample": str(i), "bytes": 131072, "sha256": str(i)} for i in range(5)],
                  "m68k_copy_regression": {"sdk_upload_download": "passed", "compiler_default": "passed", "negative_control": "reproduced", "far_branch": "passed", "cpu_policy": "passed"}}
        return [{**common, "platform": platform} for platform in ["linux/arm64", "linux/amd64"]]

    def test_complete_reports_are_accepted(self):
        self.assertEqual(self.compare(*self.reports()).returncode, 0)

    def test_old_reports_cannot_publish(self):
        arm, amd = self.reports()
        del amd["m68k_copy_regression"]
        result = self.compare(arm, amd)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing executed SDK copy regression", result.stderr)

    def test_failed_negative_control_cannot_publish(self):
        arm, amd = self.reports()
        amd["m68k_copy_regression"] = {**amd["m68k_copy_regression"], "negative_control": "passed"}
        self.assertNotEqual(self.compare(arm, amd).returncode, 0)


if __name__ == "__main__":
    unittest.main()
