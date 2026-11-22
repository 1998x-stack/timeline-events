from __future__ import annotations
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/timeline-events'

class SkillStructureTests(unittest.TestCase):
    def test_complete_package(self):
        needed=('SKILL.md','README.md','schemas/timeline.schema.json','scripts/render_html.py','scripts/timeline_events.py','templates/timeline.html','templates/timeline.css','templates/timeline.interactions.js','references/README.md','references/html-design-spec.md','references/motion-design-spec.md','examples/reference-image-transcription.json','examples/us-china-trade-war-verified.json')
        self.assertTrue(all((SKILL/p).is_file() for p in needed))
    def test_synced_bundles(self):
        p=subprocess.run([sys.executable,str(ROOT/'scripts/sync_skill.py'),'--check'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
    def test_no_repo_bound_dependencies(self):
        source=(SKILL/'scripts/render_html.py').read_text(encoding='utf-8')
        self.assertIn('ROOT = Path(__file__).resolve().parents[1]',source)
        self.assertNotIn('parents[3]',source)
    def test_reference_mode_is_not_verified(self):
        import json
        data=json.loads((SKILL/'examples/reference-image-transcription.json').read_text(encoding='utf-8'))
        self.assertEqual(data['metadata']['verification_state'],'reference_transcription')

if __name__=='__main__':
    unittest.main()
