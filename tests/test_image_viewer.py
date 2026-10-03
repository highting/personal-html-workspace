from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content


class ImageViewerTests(unittest.TestCase):
    def test_report_viewer_keeps_caption_and_current_slide(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'report.md'
            source.write_text('# 关系\n\n<figure><svg viewBox="0 0 600 120" aria-label="映射">'
                              '<text x="30" y="80" font-size="24">输入与输出</text></svg>'
                              '<figcaption>图只说明映射，不代表统计数据。</figcaption></figure>'
                              '\n\n---\n\n# 结论\n\n说明。', encoding='utf-8')
            html = build_content(source, scene='report', output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 720, 'height': 500}, offline=True)
                page.goto(html.as_uri())
                page.evaluate('document.fonts.ready')
                page.locator('.slide-body svg').evaluate('node=>node.focus({preventScroll:true})')
                page.keyboard.press('Enter')
                self.assertIn('不代表统计数据', page.locator('.image-viewer-caption').inner_text())
                self.assertEqual(page.locator('.image-viewer-caption').evaluate('n=>getComputedStyle(n).fontSize'), '21.12px')
                page.keyboard.press('ArrowRight')
                self.assertEqual(page.locator('#slide-counter').inner_text(), '1 / 2')
                page.keyboard.press('Escape')
                page.keyboard.press('ArrowRight')
                self.assertEqual(page.locator('#slide-counter').inner_text(), '2 / 2')
                browser.close()

    def test_caption_references_fit_and_return_position(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'plain.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"/>', encoding='utf-8')
            source = root / 'main.md'
            source.write_text('# 图解\n\n## 条件\n\n' + '连续解释。' * 150 + '\n\n'
                              '<p id="viewer-arrow">正文。</p><p id="image-viewer-caption">出处。</p>'
                              '<figure><svg id="plot" viewBox="0 0 300 900" style="width:300px;height:900px;max-width:300px" role="img" aria-label="纵向关系" aria-describedby="figure-note">'
                              '<defs><marker id="arrow"><path d="M0 0L10 5L0 10Z"/></marker></defs>'
                              '<path d="M50 100V800" stroke="currentColor" marker-end="url(\'#arrow\')"/>'
                              '<text x="60" y="140" font-size="20">输入</text></svg>'
                              '<figcaption id="figure-note">图1：只说明几何关系，条件为 \\(x_i > 0\\)。'
                              '<span id="condition">不代表实验数据。</span><a href="#condition">条件</a></figcaption></figure>\n\n'
                              '![无图注原图](plain.svg)', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                for _ in range(3):
                    page.locator('#font-larger').click()
                page.evaluate('document.documentElement.style.scrollBehavior="auto"')
                original = page.locator('.prose figure > svg')
                caption_text = page.locator('.prose figcaption').inner_text()
                for theme in ('light', 'dark'):
                    for width, height, zoom in ((1440, 1000, 1), (720, 500, 1), (1440, 1000, 2)):
                        page.set_viewport_size({'width': width, 'height': height})
                        page.evaluate('([theme,zoom])=>{setContentTheme(theme);document.documentElement.style.zoom=zoom}', [theme, zoom])
                        original.evaluate('node=>node.focus({preventScroll:true})')
                        before = page.evaluate('scrollY')
                        page.keyboard.press('Enter')
                        viewer = page.locator('.image-viewer')
                        self.assertTrue(viewer.is_visible())
                        self.assertEqual(page.locator('.image-viewer-caption').inner_text(), caption_text)
                        self.assertEqual(page.locator('.image-viewer-caption .katex').count(), 1)
                        self.assertEqual(viewer.get_attribute('aria-describedby'), page.locator('.image-viewer-caption').get_attribute('id'))
                        self.assertEqual(page.locator('.image-viewer svg').get_attribute('aria-describedby'), viewer.get_attribute('aria-describedby'))
                        target = page.locator('.image-viewer-caption a').get_attribute('href').removeprefix('#')
                        self.assertEqual(page.locator('.image-viewer [id="' + target + '"]').inner_text(), '不代表实验数据。')
                        arrow = page.locator('.image-viewer marker').get_attribute('id')
                        self.assertEqual(page.locator('.image-viewer [marker-end]').get_attribute('marker-end'), f"url('#{arrow}')")
                        self.assertNotEqual(page.locator('.image-viewer svg').get_attribute('id'), 'plot')
                        ids = page.locator('[id]').evaluate_all('nodes=>nodes.map(n=>n.id)')
                        self.assertEqual(len(ids), len(set(ids)))
                        self.assertNotIn('点击放大', page.locator('.image-viewer svg').get_attribute('aria-label'))
                        self.assertTrue(viewer.evaluate('node=>{const r=node.getBoundingClientRect();return r.left>=-1&&r.right<=innerWidth+1&&r.top>=-1&&r.bottom<=innerHeight+1}'))
                        self.assertTrue(page.locator('.image-viewer-content').evaluate('node=>{const image=node.firstElementChild.getBoundingClientRect();const r=node.getBoundingClientRect();return image.width<=r.width+1&&image.height<=r.height+1}'))
                        page.locator('.image-viewer [data-zoom="1.5"]').click()
                        self.assertGreater(page.locator('.image-viewer-content').evaluate('n=>n.scrollWidth'), page.locator('.image-viewer-content').evaluate('n=>n.clientWidth'))
                        self.assertEqual(page.locator('.image-viewer [data-zoom="1.5"]').get_attribute('aria-pressed'), 'true')
                        page.locator('.image-viewer-content').focus()
                        page.keyboard.press('ArrowRight')
                        page.wait_for_function('document.querySelector(".image-viewer-content").scrollLeft>1')
                        self.assertAlmostEqual(page.evaluate('scrollY'), before, delta=2)
                        page.locator('.image-viewer [data-zoom="1"]').click()
                        self.assertEqual(page.locator('.image-viewer [data-zoom="1"]').get_attribute('aria-pressed'), 'true')
                        page.keyboard.press('Escape')
                        self.assertAlmostEqual(page.evaluate('scrollY'), before, delta=2)
                        self.assertTrue(original.evaluate('node=>node===document.activeElement'))
                page.evaluate('document.documentElement.style.zoom=1')
                plain = page.locator('.prose img')
                plain.evaluate('node=>node.focus({preventScroll:true})')
                page.keyboard.press('Enter')
                self.assertFalse(page.locator('.image-viewer-caption').is_visible())
                self.assertIsNone(page.locator('.image-viewer').get_attribute('aria-describedby'))
                self.assertEqual(page.locator('.image-viewer-title').inner_text(), '无图注原图')
                browser.close()


if __name__ == '__main__':
    unittest.main()
