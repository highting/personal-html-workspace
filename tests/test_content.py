import json
from pathlib import Path
import struct
import tempfile
import unittest

from playwright.sync_api import sync_playwright
from scripts.build_content import build_content, split_slides
from scripts.prepare_content import prepare_content
from scripts.publish_content import publish_content
from scripts.render_content import render_content
from scripts.visual_qa import inspect_visuals

ROOT = Path(__file__).resolve().parent.parent


class ContentTests(unittest.TestCase):
    def test_slide_separator_preserves_code_and_math(self):
        source = '# 第一页\n\n```text\n---\n```\n\n$$\na\n---\nb\n$$\n\n---\n\n# 第二页'
        pages = split_slides(source)
        self.assertEqual(len(pages), 2)
        self.assertIn('```text\n---\n```', pages[0])
        self.assertIn('a\n---\nb', pages[0])

    def test_local_image_is_embedded_and_network_image_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'figure.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
            source = root / 'main.md'
            source.write_text('# 图\n\n![图](figure.svg)', encoding='utf-8')
            target = build_content(source, output=root / 'index.html')
            self.assertIn('data:image/svg+xml;base64,', target.read_text(encoding='utf-8'))
            source.write_text('![图](https://example.com/image.png)', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, '不能依赖联网'):
                build_content(source, output=root / 'index.html')

    def test_prepare_keeps_original_and_publish_rejects_stale_html(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'inputs/技术/主题').mkdir(parents=True)
            (root / 'inputs/技术/主题/main.md').write_text('# 原稿', encoding='utf-8')
            (root / 'prompts/scenes').mkdir(parents=True)
            (root / 'prompts/common.txt').write_text('公共规则', encoding='utf-8')
            (root / 'prompts/scenes/blog.txt').write_text('博客规则', encoding='utf-8')
            manifest = prepare_content('inputs/技术/主题', 'blog', project_root=root)
            self.assertEqual((Path(manifest['source_dir']) / 'main.md').read_text(encoding='utf-8'), '# 原稿')
            artifacts = Path(manifest['artifact_dir'])
            (artifacts / 'index.html').write_text('<html>修改后的正文</html>', encoding='utf-8')
            (artifacts / 'qa.json').write_text(json.dumps({'passed': True, 'scene': 'blog', 'html_sha256': 'outdated', 'images': []}), encoding='utf-8')
            manifest['status'] = 'completed'
            (Path(manifest['run_dir']) / 'run.json').write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'HTML 已改变'):
                publish_content(manifest['run_dir'], project_root=root)
            self.assertFalse(Path(manifest['delivery_dir']).exists())


class ContentBrowserTests(unittest.TestCase):
    def test_reading_size_and_zoomable_images_preserve_position_and_svg_references(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'image.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"><rect width="200" height="100" fill="#EAE7DE"/></svg>', encoding='utf-8')
            source = root / 'main.md'
            source.write_text('# 阅读控制\n\n## 正文\n\n' + ('连续文字。' * 150) + '\n\n'
                              '<figure><svg viewBox="0 0 600 200" aria-label="路径">'
                              '<defs><marker id="arrow"><path d="M0 0L10 5L0 10Z"/></marker></defs>'
                              '<path d="M30 100H550" marker-end="url(#arrow)"/>'
                              '<text x="30" y="50" font-size="20">输入</text></svg></figure>\n\n'
                              '![图片](image.svg)', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
                page.goto(html.as_uri())
                page.evaluate('document.fonts.ready')
                for _ in range(3):
                    page.locator('#font-larger').click()
                self.assertEqual(page.locator('#font-size').inner_text(), '24px')
                self.assertEqual(page.locator('.prose').evaluate('n => getComputedStyle(n).fontSize'), '24px')
                page.reload()
                self.assertEqual(page.locator('#font-size').inner_text(), '24px')
                for selector in ('.prose figure > svg', '.prose img'):
                    original = page.locator(selector)
                    original.scroll_into_view_if_needed()
                    before = page.evaluate('scrollY')
                    original.click()
                    self.assertTrue(page.locator('.image-viewer').is_visible())
                    if selector.endswith('svg'):
                        self.assertEqual(page.locator('.image-viewer [marker-end]').get_attribute('marker-end'), 'url(#viewer-arrow)')
                        self.assertEqual(page.locator('#arrow').count(), 1)
                    page.locator('.image-viewer [data-zoom="1.5"]').click()
                    self.assertGreater(page.locator('.image-viewer-content').evaluate('n=>n.scrollWidth'),
                                       page.locator('.image-viewer-content').evaluate('n=>n.clientWidth'))
                    page.keyboard.press('Escape')
                    self.assertFalse(page.locator('.image-viewer').is_visible())
                    self.assertAlmostEqual(page.evaluate('scrollY'), before, delta=2)
                browser.close()

    def test_visual_inspection_flags_tiny_labels_and_draft_copy_but_not_code(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.set_content('<article><p>这是排版示例</p><pre><code>待补充</code></pre>'
                             '<svg width="200" viewBox="0 0 600 200"><text x="10" y="20" font-size="18">输入</text></svg></article>')
            result = inspect_visuals(page, 'article')
            self.assertEqual(len(result['issues']), 1)
            self.assertEqual(len(result['warnings']), 1)
            self.assertAlmostEqual(result['labels'][0]['px'], 6)
            browser.close()

    def test_offline_learning_themes_math_navigation_and_position(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 学习\n\n## 定义\n\n行内 \\(x_i\\)，独立：\n\n$$\\sqrt{x^2+1}$$\n\n' + ('连续解释。' * 250) + '\n\n## 边界\n\n条件。', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                context = browser.new_context(offline=True, viewport={'width': 1440, 'height': 900})
                page = context.new_page()
                failures = []
                page.on('requestfailed', lambda request: failures.append(request.url))
                page.goto(html.as_uri())
                page.evaluate('document.fonts.ready')
                self.assertEqual(page.locator('.katex').count(), 2)
                self.assertEqual(page.locator('#toc-links a').count(), 2)
                page.locator('#toc-toggle').click()
                self.assertFalse(page.locator('#toc').is_visible())
                self.assertEqual(page.locator('#toc-toggle').get_attribute('aria-expanded'), 'false')
                page.locator('#toc-toggle').click()
                self.assertTrue(page.locator('#toc').is_visible())
                self.assertEqual(page.locator('#theme-toggle svg:visible').count(), 1)
                page.evaluate('document.documentElement.style.scrollBehavior = "auto"')
                page.locator('#toc-links a').nth(1).click()
                page.wait_for_function('scrollY > 300')
                page.evaluate('scrollTo(0, 450)')
                before = page.evaluate('scrollY')
                button = page.locator('#theme-toggle').bounding_box()
                page.mouse.click(button['x'] + button['width'] / 2, button['y'] + button['height'] / 2)
                self.assertEqual(page.evaluate('document.documentElement.dataset.theme'), 'dark')
                self.assertAlmostEqual(page.evaluate('scrollY'), before, delta=2)
                self.assertNotEqual(page.locator('body').evaluate('node => getComputedStyle(node).backgroundColor'), 'rgb(247, 244, 237)')
                page.reload()
                self.assertEqual(page.evaluate('document.documentElement.dataset.theme'), 'dark')
                page.set_viewport_size({'width': 800, 'height': 900})
                page.locator('#toc-toggle').click()
                self.assertTrue(page.locator('#toc').is_visible())
                self.assertEqual(failures, [])
                session = context.new_cdp_session(page)
                session.send('DOM.enable')
                session.send('CSS.enable')
                dom = session.send('DOM.getDocument')['root']['nodeId']
                for selector in ('.prose p', 'h1'):
                    node = session.send('DOM.querySelector', {'nodeId': dom, 'selector': selector})['nodeId']
                    fonts = session.send('CSS.getPlatformFontsForNode', {'nodeId': node})['fonts']
                    self.assertTrue(any(font['isCustomFont'] and 'Noto' in font['familyName'] for font in fonts))
                browser.close()

    def test_report_navigation_notes_theme_and_png_size(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            html = build_content(ROOT / 'demos/content/report.md', scene='report', output=root / 'index.html')
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000})
                page.goto(html.as_uri())
                for width, height in ((960, 667), (720, 500)):
                    page.set_viewport_size({'width': width, 'height': height})
                    page.evaluate('window.dispatchEvent(new Event("resize"))')
                    stage = page.locator('.slide-stage').bounding_box()
                    frame = page.locator('.presentation').bounding_box()
                    self.assertGreaterEqual(stage['x'], frame['x'])
                    self.assertGreaterEqual(stage['y'], frame['y'])
                    self.assertLessEqual(stage['x'] + stage['width'], frame['x'] + frame['width'])
                    self.assertLessEqual(stage['y'] + stage['height'], frame['y'] + frame['height'])
                page.set_viewport_size({'width': 1440, 'height': 1000})
                page.keyboard.press('ArrowRight')
                self.assertEqual(page.locator('#slide-counter').inner_text(), '2 / 4')
                page.locator('#theme-toggle').click()
                self.assertEqual(page.locator('#slide-counter').inner_text(), '2 / 4')
                page.keyboard.press('n')
                self.assertTrue(page.locator('#speaker-notes').is_visible())
                self.assertIn('学习稿', page.locator('#notes-content').inner_text())
                page.keyboard.press('End')
                self.assertEqual(page.locator('#slide-counter').inner_text(), '4 / 4')
                page.locator('#toc-toggle').click()
                page.locator('#toc-links a').first.click()
                self.assertEqual(page.locator('#slide-counter').inner_text(), '1 / 4')
                browser.close()
            result = render_content(html, scene='report', output_dir=root / 'delivery')
            self.assertTrue(result['passed'])
            self.assertEqual(len(result['images']), 4)
            image = (root / 'delivery/page-01.png').read_bytes()
            self.assertEqual(struct.unpack('>II', image[16:24]), (1280, 720))

    def test_report_rejects_content_beyond_safe_area(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 超高页\n\n<div style="height:900px">完整但过高的内容</div>', encoding='utf-8')
            html = build_content(source, scene='report', output=root / 'index.html')
            with self.assertRaisesRegex(ValueError, '安全区|越界'):
                render_content(html, scene='report', output_dir=root / 'delivery')
            self.assertFalse(json.loads((root / 'delivery/qa.json').read_text(encoding='utf-8'))['passed'])

    def test_rerender_with_fewer_pages_removes_previous_exports(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 第一页\n\n内容。\n\n---\n\n# 第二页\n\n内容。', encoding='utf-8')
            html = build_content(source, scene='report', output=root / 'index.html')
            render_content(html, scene='report', output_dir=root / 'delivery')
            (root / 'delivery/diagram.png').write_bytes(b'diagram')
            source.write_text('# 单页\n\n修正后的完整内容。', encoding='utf-8')
            build_content(source, scene='report', output=html)
            result = render_content(html, scene='report', output_dir=root / 'delivery')
            self.assertEqual(len(result['images']), 1)
            self.assertFalse((root / 'delivery/page-02.png').exists())
            self.assertFalse((root / 'delivery/checks/dark/page-02.png').exists())
            self.assertTrue((root / 'delivery/diagram.png').exists())


if __name__ == '__main__':
    unittest.main()
