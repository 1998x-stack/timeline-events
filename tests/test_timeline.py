import json
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import timeline_events as t

class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples/us-china-trade-war-verified.json").read_text(encoding="utf-8"))

    def test_svg_is_valid_and_contains_dates(self):
        svg = t.render_svg(self.data)
        root = ET.fromstring(svg)
        self.assertEqual(root.attrib["viewBox"], "0 0 3200 2000")
        self.assertIn("2018.03", svg)
        self.assertIn("2025.05", svg)
        self.assertIn("6个关键节点", svg)

    def test_manifest_contains_all_evidence(self):
        manifest = t.render_manifest(self.data)
        self.assertIn("www.whitehouse.gov", manifest)
        self.assertIn("ustr.gov", manifest)
        self.assertEqual(manifest.count("### "), len(self.data["events"]))

    def test_reject_unknown_source(self):
        self.data["events"][0]["source_ids"] = ["fake"]
        with self.assertRaises(t.TimelineError):
            t.validate(self.data)

    def test_reject_unsorted_events(self):
        self.data["events"] = list(reversed(self.data["events"]))
        with self.assertRaises(t.TimelineError):
            t.validate(self.data)

    def test_reject_unsupported_future_event(self):
        self.data["events"][-1]["date"] = "2030-01-01"
        with self.assertRaises(t.TimelineError):
            t.validate(self.data)

    def test_reject_overflow_instead_of_clipping(self):
        self.data["events"][0]["description"] = "很长的文字" * 20
        with self.assertRaises(t.TimelineError):
            t.validate(self.data)

    def test_cli_svg(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "chart"
            rc = t.main([str(ROOT / "examples/us-china-trade-war-verified.json"), "--output", str(output), "--format", "svg"])
            self.assertEqual(rc, 0)
            self.assertTrue(output.with_suffix(".svg").is_file())
            self.assertTrue(output.with_name("chart.sources.md").is_file())

    def test_png_render_if_cairosvg_available(self):
        try:
            import cairosvg
        except ImportError:
            self.skipTest("CairoSVG optional")
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "chart"
            rc = t.main([str(ROOT / "examples/us-china-trade-war-verified.json"), "--output", str(output), "--format", "png"])
            self.assertEqual(rc, 0)
            self.assertGreater(output.with_suffix(".png").stat().st_size, 10000)

if __name__ == "__main__":
    unittest.main()
