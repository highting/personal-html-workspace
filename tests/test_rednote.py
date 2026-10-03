import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from scripts.check_rednote import check_rednote
from scripts.rednote_artifacts import load_pages, validate_rednote_qa
from scripts.prepare_content import prepare_content
from scripts.publish_content import publish_content

def png_bytes(width=2160, height=2880):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    pixels = (b'\0' + b'\xf7\xf4\xed' * width) * height
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b'')


class RednoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)

    def html_page(self, name='card_1', body='<p>正文。</p>'):
        source = self.output / f'html/pages/{name}.html'
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;width:1080px;height:1440px;background:#F7F4ED}.card-content{font:38px/1.4 sans-serif;padding:80px}</style>'
                          '<article class="card-content">' + body + '</article>', encoding='utf-8')
        (self.output / f'{name}.png').write_bytes(png_bytes())

    def manifest(self, pages):
        (self.output / 'rednote-pages.json').write_text(json.dumps({'pages': pages}), encoding='utf-8')

    def test_default_html_checks_and_mobile_preview(self):
        self.html_page()
        result = check_rednote(self.output)
        self.assertTrue(result['passed'])
        self.assertEqual(result['pages'][0]['kind'], 'html')
        self.assertEqual(validate_rednote_qa(self.output), [self.output / 'card_1.png'])
        data = (self.output / 'checks/card_1-mobile.png').read_bytes()
        self.assertEqual(struct.unpack('>II', data[16:24]), (390, 520))

    def test_mixed_pages_keep_final_order_and_image_resolution(self):
        self.html_page('body_1')
        (self.output / 'body_1.png').rename(self.output / 'card_1.png')
        (self.output / 'card_2.png').write_bytes(png_bytes(1086, 1448))
        self.manifest([{'file': 'card_1.png', 'kind': 'html', 'source': 'html/pages/body_1.html'},
                       {'file': 'card_2.png', 'kind': 'image'}])
        result = check_rednote(self.output)
        self.assertEqual([p['kind'] for p in result['pages']], ['html', 'image'])
        self.assertEqual(result['pages'][1]['width'], 1086)
        self.assertTrue(result['warnings'])
        self.assertEqual([p.name for p in validate_rednote_qa(self.output)], ['card_1.png', 'card_2.png'])
        self.assertTrue((self.output / 'checks/card_2-mobile.png').is_file())

    def test_explicit_image_only_cover_is_supported(self):
        (self.output / 'cover.png').write_bytes(png_bytes(1080, 1440))
        self.manifest([{'file': 'cover.png', 'kind': 'image'}])
        self.assertTrue(check_rednote(self.output)['passed'])

    def test_bad_page_sequences_and_unlisted_images_are_rejected(self):
        self.html_page()
        self.html_page('card_3')
        with self.assertRaisesRegex(ValueError, '连续'):
            check_rednote(self.output)
        qa = json.loads((self.output / 'qa-rednote.json').read_text(encoding='utf-8'))
        self.assertFalse(qa['passed'])
        (self.output / 'card_3.png').unlink()
        (self.output / 'html/pages/card_3.html').unlink()
        (self.output / 'card_2.png').write_bytes(png_bytes())
        with self.assertRaisesRegex(ValueError, 'PNG'):
            check_rednote(self.output)
        self.manifest([{'file': 'card_1.png', 'kind': 'html', 'source': 'html/pages/card_1.html'},
                       {'file': 'card_1.png', 'kind': 'image'}])
        with self.assertRaisesRegex(ValueError, '重复'):
            load_pages(self.output)

    def test_arbitrarily_named_root_png_is_rejected(self):
        self.html_page()
        check_rednote(self.output)
        (self.output / 'extra.png').write_bytes(png_bytes())
        with self.assertRaisesRegex(ValueError, 'PNG'):
            validate_rednote_qa(self.output)
        with self.assertRaisesRegex(ValueError, 'PNG'):
            check_rednote(self.output)

    def test_png_decode_and_size_failures_revoke_previous_qa(self):
        self.manifest([{'file': 'card_1.png', 'kind': 'image'}])
        good = png_bytes(1080, 1440)
        for data in (b'not a png', good[:24], png_bytes(1080, 1500), png_bytes(540, 720)):
            with self.subTest(length=len(data)):
                (self.output / 'card_1.png').write_bytes(data)
                with self.assertRaises(ValueError):
                    check_rednote(self.output)
                self.assertFalse(json.loads((self.output / 'qa-rednote.json').read_text(encoding='utf-8'))['passed'])

    def test_html_formula_resource_and_canvas_failures_are_reported(self):
        for body in ('<span class="katex-error">错误公式</span>',
                     '<img src="missing.png">', '<div style="height:2000px">内容</div>'):
            with self.subTest(body=body):
                self.html_page(body=body)
                with self.assertRaises(ValueError):
                    check_rednote(self.output)
                self.assertFalse(json.loads((self.output / 'qa-rednote.json').read_text(encoding='utf-8'))['passed'])

    def test_interrupted_check_does_not_leave_a_passing_qa(self):
        self.html_page()
        check_rednote(self.output)
        with patch('scripts.check_rednote.sync_playwright', side_effect=RuntimeError('interrupted')):
            with self.assertRaises(RuntimeError):
                check_rednote(self.output)
        with self.assertRaisesRegex(ValueError, '重新'):
            validate_rednote_qa(self.output)

    def test_checked_mixed_delivery_can_publish_and_changed_image_cannot(self):
        root = self.output
        source = root / 'inputs/工程实践/主题'
        source.mkdir(parents=True)
        (source / 'main.md').write_text('# 正文', encoding='utf-8')
        (root / 'prompts/scenes').mkdir(parents=True)
        (root / 'prompts/common.txt').write_text('共同约束', encoding='utf-8')
        (root / 'prompts/scenes/rednote.txt').write_text('小红书', encoding='utf-8')
        run = prepare_content('inputs/工程实践/主题', 'rednote', mode='images', output_name='主题-小红书', project_root=root)
        self.output = Path(run['artifact_dir'])
        self.html_page()
        (self.output / 'card_2.png').write_bytes(png_bytes(1080, 1440))
        self.manifest([{'file': 'card_1.png', 'kind': 'html', 'source': 'html/pages/card_1.html'},
                       {'file': 'card_2.png', 'kind': 'image'}])
        (self.output / '标题.txt').write_text('主题', encoding='utf-8')
        (self.output / '配文.txt').write_text('我整理了这个问题。', encoding='utf-8')
        check_rednote(self.output)
        run['status'] = 'completed'
        (Path(run['run_dir']) / 'run.json').write_text(json.dumps(run), encoding='utf-8')
        result = publish_content(run['run_dir'], root)
        destination = Path(result['delivery_dir'])
        self.assertEqual([Path(p).name for p in result['published_images']], ['card_1.png', 'card_2.png'])
        old = (destination / 'card_2.png').read_bytes()
        (self.output / 'card_2.png').write_bytes(png_bytes(1086, 1448))
        with self.assertRaisesRegex(ValueError, '图片'):
            publish_content(run['run_dir'], root)
        self.assertEqual((destination / 'card_2.png').read_bytes(), old)
