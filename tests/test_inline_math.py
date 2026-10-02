from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content

class InlineMathTests(unittest.TestCase):
    def test_short_real_expression_stays_together_and_long_expression_reflows(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            # 与真实长文中的同一段解释和公式保持一致，不依赖本机输出目录。
            source = root / 'main.md'
            source.write_text('# 行内公式\n\n## 推导\n\n最后一步使用了切向近似，忽略内积项。再利用 '
                              '\\(\\eta\\lambda\\ll1\\) 时的近似 '
                              '\\((1-\\eta\\lambda)^2\\approx1-2\\eta\\lambda\\)，得到：\n\n'
                              '根号 \\(\\sqrt{x^2+1}\\)。\n\n长表达式 \\(' +
                              '+'.join(f'a_{{{i}}}' for i in range(50)) + '\\)。', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                for width, height, zoom in ((1440, 1000, 1), (720, 500, 1), (1440, 1000, 2)):
                    page.set_viewport_size({'width': width, 'height': height})
                    page.evaluate('zoom=>document.documentElement.style.zoom=zoom', zoom)
                    for size in (16, 18, 24):
                        page.evaluate('size=>document.documentElement.style.setProperty("--reading-size",size+"px")', size)
                        for theme in ('light', 'dark'):
                            page.evaluate('theme=>setContentTheme(theme)', theme)
                            maths = page.locator('.prose .katex')
                            rows = maths.nth(1).evaluate('n=>new Set([...n.querySelectorAll(".katex-html>.base")].map(x=>Math.round(x.getBoundingClientRect().top))).size')
                            self.assertEqual(rows, 1, (width, size, zoom, theme))
                            long_rows = maths.last.evaluate('n=>new Set([...n.querySelectorAll(".katex-html>.base")].map(x=>Math.round(x.getBoundingClientRect().top))).size')
                            self.assertGreater(long_rows, 1)
                            self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), page.evaluate('innerWidth') + 2)
                            self.assertEqual(page.locator('.katex-error').count(), 0)
                            self.assertGreater(page.locator('.sqrt svg').bounding_box()['height'], 0)
                browser.close()


if __name__ == '__main__':
    unittest.main()
