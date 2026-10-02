from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content


class ResumeViewTests(unittest.TestCase):
    def test_resume_restores_wrapping_expansion_and_the_visible_code_line(self):
        code = 'message = "' + '长内容 ' * 80 + '"\n' + ''.join(f'value_{n} = {n}\n' for n in range(35))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 阅读状态\n\n## 计算\n\n说明。\n\n```python\n' + code + '```', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 800, 'height': 900}, offline=True)
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                page.evaluate('document.documentElement.style.scrollBehavior="auto"')
                page.locator('.code-wrap').click()
                page.locator('.code-expand').click()
                line = page.locator('.code-line[data-line="20"]')
                line.evaluate('n => scrollTo(0, n.getBoundingClientRect().top + scrollY - 140)')
                before = line.bounding_box()['y']
                page.wait_for_timeout(350)
                page.reload()
                page.wait_for_function('window.contentReadingReady')
                self.assertFalse(page.locator('.code-block').evaluate('n=>n.classList.contains("is-wrapped")'))
                page.locator('#resume-reading').click()
                self.assertEqual(page.locator('.code-wrap').get_attribute('aria-pressed'), 'true')
                self.assertEqual(page.locator('.code-expand').get_attribute('aria-expanded'), 'true')
                self.assertAlmostEqual(line.bounding_box()['y'], before, delta=3)
                browser.close()

    def test_resume_prompt_names_a_short_final_section_at_page_end(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 文末续读\n\n## 主体\n\n' + ('连续解释。' * 400) + '\n\n## 结尾\n\n短结论。', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000})
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                page.evaluate('document.documentElement.style.scrollBehavior="auto";scrollTo(0,document.documentElement.scrollHeight)')
                before = page.evaluate('scrollY')
                page.wait_for_timeout(350)
                page.reload()
                page.wait_for_function('window.contentReadingReady')
                self.assertEqual(page.locator('#resume-title').inner_text(), '结尾')
                page.locator('#resume-reading').click()
                self.assertAlmostEqual(page.evaluate('scrollY'), before, delta=3)
                browser.close()

    def test_inserted_code_does_not_receive_another_blocks_view_state(self):
        code = 'message = "' + '长内容 ' * 80 + '"\n' + 'value = 1\n' * 30
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            original = '# 同一文章\n\n## 计算\n\n```python\n' + code + '```'
            source.write_text(original, encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 800, 'height': 900})
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                page.locator('.code-wrap').click()
                page.locator('.code-expand').click()
                page.locator('.code-line[data-line="20"]').evaluate('n=>scrollTo(0,n.getBoundingClientRect().top+scrollY-140)')
                page.wait_for_timeout(350)
                source.write_text(original.replace('## 计算', '## 新引言\n\n```python\n' + code + '```\n\n## 计算'), encoding='utf-8')
                build_content(source, output=html)
                page.reload()
                page.wait_for_function('window.contentReadingReady')
                page.locator('#resume-reading').click()
                blocks = page.locator('.code-block')
                self.assertFalse(blocks.nth(0).evaluate('n=>n.classList.contains("is-wrapped")'))
                self.assertTrue(blocks.nth(1).evaluate('n=>n.classList.contains("is-wrapped")'))
                self.assertEqual(blocks.nth(1).locator('.code-expand').get_attribute('aria-expanded'), 'true')
                browser.close()


if __name__ == '__main__':
    unittest.main()
