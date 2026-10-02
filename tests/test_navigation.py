from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content


class NavigationTests(unittest.TestCase):
    def test_end_of_long_article_marks_last_section_and_keeps_it_in_toc(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 长文导航\n\n' + '\n\n'.join(
                f'## 章节 {n}\n\n' + ('连续解释。' * 35) for n in range(1, 32)
            ) + '\n\n## 结尾\n\n简短结论。', encoding='utf-8')
            target = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 700}, offline=True)
                page.goto(target.as_uri())
                page.wait_for_function('window.contentReadingReady')
                page.evaluate('document.documentElement.style.scrollBehavior="auto";scrollTo(0,document.documentElement.scrollHeight)')
                page.wait_for_timeout(100)
                current = page.locator('#toc-links [aria-current="location"]')
                self.assertIn('结尾', current.inner_text())
                frame = page.locator('#toc').bounding_box()
                item = current.bounding_box()
                self.assertGreaterEqual(item['y'], frame['y'])
                self.assertLessEqual(item['y'] + item['height'], frame['y'] + frame['height'] + 1)
                before = page.evaluate('scrollY')
                button = page.locator('#theme-toggle').bounding_box()
                page.mouse.click(button['x'] + button['width'] / 2, button['y'] + button['height'] / 2)
                self.assertEqual(page.evaluate('document.documentElement.dataset.theme'), 'dark')
                self.assertAlmostEqual(page.evaluate('scrollY'), before, delta=2)
                browser.close()


if __name__ == '__main__':
    unittest.main()
