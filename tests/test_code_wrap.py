from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content


class CodeWrapTests(unittest.TestCase):
    def test_collapsed_preview_does_not_show_partial_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 长代码\n\n```python\n' + 'value = 1\n' * 35 + '```', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                for size in (16, 18, 24):
                    for zoom in (1, 1.5, 2):
                        page.evaluate('([size,zoom])=>{document.documentElement.style.setProperty("--reading-size",size+"px");document.documentElement.style.zoom=zoom}', [size, zoom])
                        partial = page.locator('.code-block').evaluate('''block => {
                          const bottom = Math.min(block.querySelector('pre').getBoundingClientRect().bottom,
                            block.querySelector('code').getBoundingClientRect().bottom);
                          return [...block.querySelectorAll('.code-line')].filter(line => {
                            const rect = line.getBoundingClientRect();
                            return rect.top < bottom - 1 && rect.bottom > bottom + 1;
                          }).map(line => line.dataset.line);
                        }''')
                        self.assertEqual(partial, [], (size, zoom))
                browser.close()

    def test_wrapping_preserves_source_line_numbers_and_expansion(self):
        code = '    result = "' + '长内容 & <value> ' * 30 + '"\n\n' + 'x = 1\n' * 24
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 代码换行\n\n```{.python data-highlight="1"}\n' + code + '```', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 800, 'height': 900}, offline=True)
                page.add_init_script('Object.defineProperty(navigator,"clipboard",{value:{writeText:async text=>window.copiedCode=text}})')
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                pre = page.locator('.code-block pre')
                self.assertGreater(pre.evaluate('n=>n.scrollWidth'), pre.evaluate('n=>n.clientWidth'))
                page.locator('.code-wrap').click()
                self.assertEqual(page.locator('.code-wrap').get_attribute('aria-pressed'), 'true')
                self.assertLessEqual(pre.evaluate('n=>n.scrollWidth'), pre.evaluate('n=>n.clientWidth') + 1)
                self.assertEqual(page.locator('.code-line').count(), len(code.splitlines()))
                self.assertEqual(page.locator('.code-line.is-highlighted').count(), 1)
                self.assertEqual(page.locator('.code-line').first.get_attribute('data-line'), '1')
                self.assertGreater(page.locator('.code-line').first.bounding_box()['height'], 40)
                self.assertGreater(page.locator('.code-line').nth(1).bounding_box()['height'], 10)
                page.locator('.code-copy').click()
                self.assertEqual(page.evaluate('window.copiedCode'), code)
                page.locator('.code-expand').click()
                self.assertEqual(page.locator('.code-expand').get_attribute('aria-expanded'), 'true')
                self.assertLessEqual(pre.evaluate('n=>n.scrollHeight'), pre.evaluate('n=>n.clientHeight') + 1)
                page.locator('.code-wrap').click()
                self.assertEqual(page.locator('.code-wrap').get_attribute('aria-pressed'), 'false')
                self.assertGreater(pre.evaluate('n=>n.scrollWidth'), pre.evaluate('n=>n.clientWidth'))
                self.assertEqual(page.locator('.code-block code').text_content(), code)
                browser.close()


if __name__ == '__main__':
    unittest.main()
