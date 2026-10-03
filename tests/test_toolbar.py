from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright
from scripts.build_content import build_content


class ToolbarTests(unittest.TestCase):
    def test_fold_keeps_reading_position_focus_and_preference(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 阅读工具栏\n\n' + '\n\n'.join(
                f'## 章节 {n}\n\n' + '连续阅读时，收起工具栏不应打断当前文字。' * 60
                for n in range(1, 12)), encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(offline=True, viewport={'width': 1440, 'height': 1000})
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                for width, height in ((1440, 1000), (720, 500)):
                    page.set_viewport_size({'width': width, 'height': height})
                    page.evaluate('''() => {
                      document.documentElement.style.scrollBehavior = 'auto';
                      document.documentElement.style.overflowAnchor = 'none';
                      const text = document.querySelectorAll('.prose > p')[4].firstChild;
                      window.point = document.createRange();
                      point.setStart(text, 0); point.setEnd(text, 1);
                      scrollTo(0, point.getBoundingClientRect().top + scrollY - 112);
                    }''')
                    before = page.evaluate('point.getBoundingClientRect().top')
                    if width == 720:
                        box = page.locator('#toc-toggle').bounding_box()
                        page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                        self.assertTrue(page.locator('#toc').is_visible())
                    for selector, focus in (('#toolbar-collapse', 'toolbar-reveal'), ('#toolbar-reveal', 'toolbar-collapse')):
                        box = page.locator(selector).bounding_box()
                        page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                        self.assertAlmostEqual(page.evaluate('point.getBoundingClientRect().top'), before, delta=2)
                        self.assertEqual(page.evaluate('document.activeElement.id'), focus)
                        if focus == 'toolbar-reveal':
                            self.assertFalse(page.locator('#reading-toolbar').is_visible())
                            self.assertEqual(page.locator('#toolbar-reveal').get_attribute('aria-expanded'), 'false')
                            if width == 720:
                                self.assertFalse(page.locator('#toc').is_visible())
                    page.click('#theme-toggle')
                page.locator('#toolbar-collapse').focus()
                page.keyboard.press('Enter')
                page.reload()
                page.wait_for_function('window.contentReadingReady')
                self.assertFalse(page.locator('#reading-toolbar').is_visible())
                page.locator('#toolbar-reveal').focus()
                page.keyboard.press('Enter')
                self.assertTrue(page.locator('#reading-toolbar').is_visible())
                page.reload()
                page.wait_for_function('window.contentReadingReady')
                self.assertTrue(page.locator('#reading-toolbar').is_visible())
                page.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw Error("blocked")}})')
                page.reload()
                page.wait_for_function('window.contentReadingReady')
                page.click('#toolbar-collapse')
                self.assertTrue(page.locator('#toolbar-reveal').is_visible())
                browser.close()

    def test_media_matches_text_measure_and_zoom_bounds(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 图文层次\n\n## 阅读\n\n' + '保持正文的阅读行长。' * 80 +
                '\n\n<figure><svg viewBox="0 0 800 240" aria-label="宽图"></svg><figcaption>图注</figcaption></figure>', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(offline=True, viewport={'width': 1440, 'height': 1000})
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                text_width = page.locator('.prose > p').first.bounding_box()['width']
                self.assertAlmostEqual(page.locator('.prose > figure').bounding_box()['width'], text_width, delta=1)
                page.locator('#reading-width').focus()
                page.keyboard.press('End')
                page.keyboard.press('Escape')
                self.assertGreater(page.locator('.prose > p').first.bounding_box()['width'], text_width)
                for width, height in ((1440, 1000), (960, 667), (720, 500)):
                    page.set_viewport_size({'width': width, 'height': height})
                    for zoom in (1, 1.5, 2):
                        page.evaluate('z=>document.documentElement.style.zoom=z', zoom)
                        self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
                        page.click('#toolbar-collapse')
                        box = page.locator('#toolbar-reveal').bounding_box()
                        self.assertGreaterEqual(box['x'], 0)
                        self.assertLessEqual(box['x'] + box['width'], width + 1)
                        page.click('#toolbar-reveal')
                browser.close()


if __name__ == '__main__':
    unittest.main()
