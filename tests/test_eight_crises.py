"""Regression check for the Eight Crises evidence-backed long-form timeline."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/eight-crises-1949-2009.json"
PAGE = ROOT / "docs/events/eight-crises/index.html"
RENDERER = ROOT / "skills/timeline-events/scripts/render_html.py"


class EightCrisesTest(unittest.TestCase):
    def test_sources_and_chapters(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(len(data["events"]), 8)
        self.assertEqual(len(data["chapters"]), 8)
        self.assertGreaterEqual(len(data["sources"]), 15)
        self.assertEqual([e["date"] for e in data["events"]], sorted(e["date"] for e in data["events"]))
        ids = {s["id"] for s in data["sources"]}
        for ev, ch in zip(data["events"], data["chapters"]):
            self.assertTrue(ev["source_ids"])
            self.assertTrue(ch["source_ids"])
            self.assertTrue(set(ev["source_ids"]) <= ids)
            self.assertTrue(set(ch["source_ids"]) <= ids)
            for key in ("anchor", "background", "mechanism", "response", "assessment"):
                self.assertGreater(len(ch[key]), 20)
        self.assertIn("节点日期为各阶段代表性史实", data["metadata"]["subtitle"])

    def test_page_is_generated_by_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "index.html"
            result = subprocess.run([sys.executable, str(RENDERER), str(DATA),
                "--site-url", "../../index.html", "--output", str(output)],
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(PAGE.read_bytes(), output.read_bytes(),
                "Published page must be deterministic output of the canonical SKILL renderer")
            html = output.read_text(encoding="utf-8")
            self.assertEqual(html.count('class="research-chapter"'), 8)
            self.assertEqual(html.count('class="event event--'), 8)
            self.assertIn('prefers-reduced-motion', html)


if __name__ == "__main__":
    unittest.main()
