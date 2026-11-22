import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_site import verify

class SiteTests(unittest.TestCase):
    def test_site_links_categories_and_content(self):
        verify()

    def test_catalog_is_factual_about_status(self):
        data=json.loads((ROOT/'docs/data/catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['events']),1)
        self.assertEqual(data['events'][0]['status'],'reference_transcription')
        self.assertEqual(len(data['taxonomies']),6)

    def test_site_form_does_not_claim_to_call_ai(self):
        script=(ROOT/'docs/assets/site.js').read_text(encoding='utf-8')
        self.assertIn('生成 Agent 指令',(ROOT/'docs/index.html').read_text(encoding='utf-8'))
        self.assertIn('不是在本站执行 AI 生成',script)
        self.assertNotIn('api.openai.com',script)

    def test_skill_identical(self):
        p=ROOT/'.pi/skills/timeline-events/SKILL.md'
        a=ROOT/'.agent/skills/timeline-events/SKILL.md'
        self.assertEqual(p.read_bytes(),a.read_bytes())

if __name__=='__main__':
    unittest.main()
