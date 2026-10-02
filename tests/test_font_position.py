from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content

ROOT = Path(__file__).resolve().parent.parent


class FontPositionTests(unittest.TestCase):
    def test_resizing_keeps_current_text_visible_in_a_real_long_article(self):
        with tempfile.TemporaryDirectory() as folder:
            html = build_content(ROOT / 'blogs/论文阅读/Hyperball博客-图文版/Hyperball博客-图文版.md',
                                 scene='blog', output=Path(folder) / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                page.evaluate('''() => {
                  document.documentElement.style.scrollBehavior = 'auto';
                  // 不让浏览器自动锚定掩盖控件自身的定位能力。
                  document.documentElement.style.overflowAnchor = 'none';
                  const para = [...document.querySelectorAll('.prose > p')].find(p => p.textContent.startsWith('对于尺度不变的权重，Weight Decay'));
                  const node = para.querySelector('strong').firstChild;
                  const offset = Math.floor(node.textContent.length * .6);
                  const range = document.createRange();
                  range.setStart(node, offset); range.setEnd(node, offset + 1);
                  window.readingPoint = range;
                  scrollTo(0, range.getBoundingClientRect().top + scrollY - 140);
                }''')
                before = page.evaluate('readingPoint.getBoundingClientRect().top')
                button = page.locator('#font-larger').bounding_box()
                page.mouse.click(button['x'] + button['width'] / 2, button['y'] + button['height'] / 2)
                page.wait_for_timeout(100)
                after = page.evaluate('readingPoint.getBoundingClientRect().top')
                self.assertLessEqual(abs(after - before), 60)
                self.assertEqual(page.locator('#font-size').inner_text(), '20px')
                browser.close()


if __name__ == '__main__':
    unittest.main()
