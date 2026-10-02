from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content


class TableScrollTests(unittest.TestCase):
    def test_folded_table_rechecks_overflow_after_font_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 参数\n\n## 参数解释\n\n<details><summary>更多参数</summary>'
                              '<table><tr><th>参数</th></tr><tr><td><code>configuration_' +
                              'value_' * 12 + '</code></td></tr></table></details>', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 800, 'height': 1000}, offline=True)
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                hint = page.locator('.table-scroll-hint')
                self.assertFalse(hint.is_visible())
                page.locator('summary').click()
                page.locator('#font-smaller').click()
                hint.wait_for(state='hidden')
                for _ in range(4):
                    page.locator('#font-larger').click()
                hint.wait_for(state='visible')
                self.assertLessEqual(hint.bounding_box()['y'] + hint.bounding_box()['height'],
                                     page.locator('details').bounding_box()['y'] + page.locator('details').bounding_box()['height'])
                for _ in range(4):
                    page.locator('#font-smaller').click()
                hint.wait_for(state='hidden')
                self.assertEqual(page.locator('.table-wrap').get_attribute('tabindex'), '-1')
                browser.close()

    def test_hint_tracks_overflow_keyboard_and_resize_without_moving_text(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 表格阅读\n\n## 对照\n\n'
                              '<p id="table-scroll-1">前文。</p>\n\n'
                              '<table style="min-width:700px"><caption>数值对照</caption>'
                              '<tr><th>输入</th><th>输出</th></tr>'
                              '<tr><td>第一组</td><td>0.665241</td></tr></table>\n\n'
                              '<p id="after-table">表后正文。</p>\n\n' + '后续解释。' * 400,
                              encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                table = page.locator('.table-wrap')
                hint = page.locator('.table-scroll-hint')
                self.assertFalse(hint.is_visible())
                self.assertEqual(table.get_attribute('tabindex'), '-1')
                page.set_viewport_size({'width': 720, 'height': 1000})
                hint.wait_for(state='visible')
                self.assertEqual(table.get_attribute('aria-label'), '数值对照')
                self.assertEqual(table.get_attribute('aria-describedby'), hint.get_attribute('id'))
                self.assertNotEqual(hint.get_attribute('id'), 'table-scroll-1')
                self.assertIn('向右', hint.inner_text())
                table.focus()
                before = page.locator('#after-table').bounding_box()['y']
                page.keyboard.press('ArrowRight')
                page.wait_for_function('document.querySelector(".table-wrap").scrollLeft > 1')
                self.assertAlmostEqual(page.locator('#after-table').bounding_box()['y'], before, delta=1)
                table.evaluate('node=>node.scrollLeft=node.scrollWidth')
                page.wait_for_function('document.querySelector(".table-scroll-hint").textContent.includes("向左")')
                self.assertIn('向左', hint.inner_text())
                self.assertAlmostEqual(page.locator('#after-table').bounding_box()['y'], before, delta=1)
                page.keyboard.press('ArrowLeft')
                page.wait_for_function('(()=>{const n=document.querySelector(".table-wrap");return n.scrollLeft<n.scrollWidth-n.clientWidth-1})()')
                page.set_viewport_size({'width': 1440, 'height': 1000})
                hint.wait_for(state='hidden')
                self.assertEqual(table.get_attribute('tabindex'), '-1')
                self.assertIsNone(table.get_attribute('aria-describedby'))
                browser.close()


if __name__ == '__main__':
    unittest.main()
