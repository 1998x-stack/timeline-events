from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/timeline-events'
sys.path.insert(0, str(ROOT / 'scripts'))
import timeline_events as engine

class TimelineEngineTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL/'examples/us-china-trade-war-verified.json').read_text(encoding='utf-8'))
    def test_valid_xml(self):
        svg = engine.render_svg(self.data)
        tree = ET.fromstring(svg)
        self.assertEqual(tree.get('viewBox'), '0 0 3200 2000')
        self.assertIn('6个关键节点', svg)
    def test_evidence_manifest(self):
        markdown = engine.render_manifest(self.data)
        self.assertEqual(markdown.count('### '), 6)
        self.assertIn('www.whitehouse.gov', markdown)
    def test_reject_missing_source(self):
        self.data['events'][0]['source_ids'] = ['missing']
        with self.assertRaises(ValueError):
            engine.validate(self.data)
    def test_reject_time_reversal(self):
        self.data['events'].reverse()
        with self.assertRaises(ValueError):
            engine.validate(self.data)
    def test_svg_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            result = engine.main([str(SKILL/'examples/us-china-trade-war-verified.json'), '--output', str(Path(temp)/'test'), '--format', 'svg'])
            self.assertEqual(result, 0)
            self.assertTrue((Path(temp)/'test.svg').is_file())
    def test_portable_standalone_skill(self):
        for mirror in (ROOT/'.pi/skills/timeline-events', ROOT/'.agent/skills/timeline-events'):
            with tempfile.TemporaryDirectory() as temp:
                target = Path(temp)/'out.html'
                process = subprocess.run([sys.executable, str(mirror/'scripts/render_html.py'), str(mirror/'examples/reference-image-transcription.json'), '--reference-transcription','--output',str(target)], capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertIn('class="event-dot"', target.read_text(encoding='utf-8'))

if __name__ == '__main__':
    unittest.main()
