from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import render_html as renderer

class HtmlTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'examples/reference-image-transcription.json').read_text(encoding='utf-8'))

    def test_original_content_and_layout(self):
        html=renderer.render_html(self.data,reference=True)
        self.assertIn('2048px',html)
        self.assertIn('中美贸易战时间轴',html)
        self.assertIn('2018.07—2026.11：8年4个月',html)
        self.assertIn('十个关键节点',html)
        self.assertIn('2027.01.10',html)
        self.assertEqual(html.count('class="event event--'),10)
        self.assertEqual(html.count('class="phase-card"'),4)
        self.assertEqual(html.count('class="insight-card"'),3)
        self.assertIn('未经独立事实审计',html)

    def test_mobile_reader_contains_all_nodes(self):
        html=renderer.render_html(self.data,reference=True)
        self.assertIn('class="mobile-event-list"',html)
        self.assertIn('max-width:760px',html)
        self.assertEqual(html.count('class="mobile-event-list"'),1)
        self.assertEqual(html.count('<time datetime='),10)

    def test_reference_flag_is_mandatory(self):
        self.data['metadata']['verification_state']='verified'
        with self.assertRaises(renderer.TimelineHtmlError):
            renderer.render_html(self.data,reference=True)

    def test_default_mode_rejects_unverified_image(self):
        with self.assertRaises((KeyError,ValueError,TypeError)):
            renderer.render_html(self.data)

    def test_escapes_injected_html_and_attribute(self):
        self.data['metadata']['title']='<img src=x onerror="alert(1)">'
        self.data['events'][0]['lines'][0]='<script>alert(1)</script>'
        html=renderer.render_html(self.data,reference=True)
        self.assertNotIn('<img src=x',html)
        self.assertNotIn('<script>alert(1)</script>',html)
        self.assertIn('&lt;img',html)
        self.assertIn('&lt;script&gt;',html)

    def test_rejects_reverse_order(self):
        self.data['events']=list(reversed(self.data['events']))
        with self.assertRaises(ValueError):
            renderer.render_html(self.data,reference=True)

    def test_rejects_oversized_manual_line(self):
        self.data['events'][0]['lines']=['错误'*100]
        with self.assertRaises(ValueError):
            renderer.render_html(self.data,reference=True)

    def test_reference_cli_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'example.html'
            code=renderer.main([str(ROOT/'examples/reference-image-transcription.json'),'--reference-transcription','--output',str(p)])
            self.assertEqual(code,0)
            self.assertIn('<html lang="zh-CN">',p.read_text(encoding='utf-8'))

    def test_default_mode_verified_example(self):
        # Existing SVG validation schema is preserved for researched events.
        dataset={
            'metadata':{'title':'有证据的事件示例','subtitle':'演示文本','updated_at':'2025-06-01'},
            'sources':[{'id':'s1','publisher':'某单位','title':'原始材料','url':'https://example.org/source'}],
            'events':[
                {'date':f'2024-0{i}','title':f'节点{i}','description':'可追溯文字说明','source_ids':['s1']}
                for i in range(1,5)
            ],
            'phases':[],'insights':[]
        }
        html=renderer.render_html(dataset)
        self.assertIn('引用来源',html)
        self.assertEqual(html.count('class="event event--'),4)
        self.assertIn('https://example.org/source',html)

if __name__=='__main__':
    unittest.main()
