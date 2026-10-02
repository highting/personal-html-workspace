import tempfile
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content


class ReadingTests(unittest.TestCase):
    def test_code_copy_highlights_and_long_block_expansion_preserve_source(self):
        code = '# 中文注释\nprint("<tag> & value")\n\n' + ''.join(f'value_{n} = {n}\n' for n in range(24))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 代码阅读\n\n```{.python title="geometry.py" data-highlight="2 4-5"}\n' + code + '```', encoding='utf-8')
            target = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.add_init_script('Object.defineProperty(navigator, "clipboard", {value: {writeText: async text => window.copiedText = text}})')
                page.goto(target.as_uri())
                page.wait_for_function('window.contentReadingReady')
                self.assertEqual(page.locator('.code-filename').inner_text(), 'geometry.py')
                self.assertEqual(page.locator('.code-line.is-highlighted').count(), 3)
                self.assertGreater(page.locator('.code-block .k, .code-block .mi').count(), 0)
                page.locator('.code-copy').click()
                self.assertEqual(page.evaluate('window.copiedText'), code)
                self.assertEqual(page.locator('.code-copy').inner_text(), '已复制')
                pre = page.locator('.code-block pre')
                preview = page.locator('.code-block code')
                self.assertGreater(preview.evaluate('n => n.scrollHeight'), preview.evaluate('n => n.clientHeight'))
                page.locator('.code-expand').click()
                self.assertEqual(page.locator('.code-expand').get_attribute('aria-expanded'), 'true')
                self.assertLessEqual(pre.evaluate('n => n.scrollHeight'), pre.evaluate('n => n.clientHeight') + 1)
                page.evaluate('navigator.clipboard.writeText = async () => {throw Error("denied")}; document.execCommand = () => false')
                page.locator('.code-copy').click()
                self.assertEqual(page.locator('.code-copy').inner_text(), '复制失败')
                browser.close()

    def test_section_links_are_stable_and_open_folded_math(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 定位\n\n## 更新方向\n\n说明。\n\n'
                              '<details markdown="1"><summary>展开证明</summary>\n\n'
                              '### 内积为零\n\n$$\\sqrt{x^2+1}$$\n\n</details>\n\n## 更新方向\n\n其他说明。', encoding='utf-8')
            target = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.add_init_script('Object.defineProperty(navigator, "clipboard", {value: {writeText: async text => window.copiedText = text}})')
                page.goto(target.as_uri())
                page.wait_for_function('window.contentReadingReady')
                ids = page.locator('.prose h2').evaluate_all('nodes=>nodes.map(n=>n.id)')
                self.assertEqual(ids, ['更新方向', '更新方向-2'])
                self.assertFalse(page.locator('details').evaluate('n=>n.open'))
                page.locator('#toc-links a').nth(1).click()
                self.assertTrue(page.locator('details').evaluate('n=>n.open'))
                self.assertEqual(page.locator('.katex-error').count(), 0)
                self.assertEqual(page.locator('.katex').count(), 1)
                page.locator('.prose h3').hover()
                page.locator('.prose h3 .heading-anchor').click()
                copied = page.evaluate('window.copiedText')
                page.goto(copied)
                page.reload()
                page.wait_for_function('window.contentReadingReady')
                self.assertTrue(page.locator('details').evaluate('n=>n.open'))
                self.assertFalse(page.locator('#resume-banner').is_visible())
                browser.close()

    def test_resume_is_explicit_scoped_to_article_and_storage_optional(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 长文甲\n\n## 概念\n\n' + ('解释。' * 800) + '\n\n## 推导\n\n' + ('推导内容。' * 800), encoding='utf-8')
            first = build_content(source, output=root / 'first.html')
            source.write_text('# 长文乙\n\n## 概念\n\n其他内容。', encoding='utf-8')
            second = build_content(source, output=root / 'second.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 900})
                page.goto(first.as_uri())
                page.wait_for_function('window.contentReadingReady')
                page.evaluate('document.documentElement.style.scrollBehavior="auto"; scrollTo(0,document.getElementById("推导").getBoundingClientRect().top+scrollY+200)')
                page.wait_for_timeout(350)
                before = page.evaluate('scrollY')
                page.reload()
                page.wait_for_function('window.contentReadingReady')
                self.assertLess(page.evaluate('scrollY'), 2)
                self.assertTrue(page.locator('#resume-banner').is_visible())
                self.assertEqual(page.locator('#resume-title').inner_text(), '推导')
                page.locator('#resume-reading').click()
                self.assertAlmostEqual(page.evaluate('scrollY'), before, delta=3)
                page.goto(second.as_uri())
                page.wait_for_function('window.contentReadingReady')
                self.assertFalse(page.locator('#resume-banner').is_visible())
                page.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw Error("blocked")}})')
                page.goto(first.as_uri())
                page.wait_for_function('window.contentReadingReady')
                page.locator('#font-larger').click()
                self.assertEqual(page.locator('#font-size').inner_text(), '20px')
                browser.close()

    def test_generated_ids_do_not_shadow_author_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 定位冲突\n\n<h2 id="supplement-证明">正文</h2>\n\n'
                              '<h3 id="code-1">代码</h3>\n\n```python\n' + 'x = 1\n' * 24 +
                              '```\n\n<details><summary>证明</summary><p>补充内容。</p></details>', encoding='utf-8')
            target = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(target.as_uri())
                page.wait_for_function('window.contentReadingReady')
                ids = page.locator('[id]').evaluate_all('nodes=>nodes.map(n=>n.id)')
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(page.locator('details').get_attribute('id'), 'supplement-证明-2')
                self.assertEqual(page.locator('.code-block pre').get_attribute('id'), 'code-1-2')
                browser.close()


if __name__ == '__main__':
    unittest.main()
