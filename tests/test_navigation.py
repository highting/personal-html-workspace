from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content


class NavigationTests(unittest.TestCase):
    def test_toc_toggle_keeps_current_text_and_compact_menu_is_visible(self):
        paragraph = 'Explaining layout changes with a continuous paragraph. 内容和公式各有阅读节奏。' * 24
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 阅读目录\n\n' + '\n\n'.join(
                f'## 章节 {n}\n\n{paragraph}\n\n{paragraph}' for n in range(1, 17)
            ), encoding='utf-8')
            target = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
                page.goto(target.as_uri())
                page.wait_for_function('window.contentReadingReady')
                page.evaluate('document.documentElement.style.scrollBehavior="auto";document.documentElement.style.overflowAnchor="none"')
                def toggle():
                    button = page.locator('#toc-toggle').bounding_box()
                    page.mouse.click(button['x'] + button['width'] / 2, button['y'] + button['height'] / 2)
                for size in (18, 24):
                    while int(page.locator('#font-size').inner_text().removesuffix('px')) < size:
                        page.locator('#font-larger').click()
                    page.evaluate('''() => {
                      const range = document.createRange();
                      const text = document.querySelectorAll('.prose > p')[20].firstChild;
                      range.setStart(text, 0); range.setEnd(text, 1);
                      window.readingPoint = range;
                      scrollTo(0, range.getBoundingClientRect().top + scrollY - 112);
                    }''')
                    before = page.evaluate('readingPoint.getBoundingClientRect().top')
                    for _ in range(2):
                        toggle()
                        self.assertAlmostEqual(page.evaluate('readingPoint.getBoundingClientRect().top'), before, delta=2)
                # 桌面已收起侧栏的偏好不能隐藏缩小窗口中的浮层。
                toggle()
                for width, height in ((960, 667), (720, 500)):
                    page.set_viewport_size({'width': width, 'height': height})
                    page.evaluate('scrollTo(0, 3000)')
                    before = page.evaluate('scrollY')
                    toggle()
                    menu = page.locator('#toc').bounding_box()
                    self.assertGreaterEqual(menu['y'], 76)
                    self.assertLessEqual(menu['y'] + menu['height'], height)
                    self.assertAlmostEqual(page.evaluate('scrollY'), before, delta=2)
                    self.assertEqual(page.locator('#toc-toggle').get_attribute('aria-expanded'), 'true')
                    page.mouse.move(menu['x'] + menu['width'] / 2, menu['y'] + menu['height'] / 2)
                    for _ in range(2):
                        page.mouse.wheel(0, 2000)
                        page.wait_for_timeout(100)
                    self.assertAlmostEqual(page.evaluate('scrollY'), before, delta=2)
                    last = page.locator('#toc-links a').last.bounding_box()
                    self.assertLessEqual(last['y'] + last['height'], menu['y'] + menu['height'])
                    page.keyboard.press('Escape')
                    self.assertFalse(page.locator('#toc').is_visible())
                    self.assertEqual(page.evaluate('document.activeElement.id'), 'toc-toggle')
                    toggle()
                    link = page.locator('#toc-links a').nth(10)
                    href = link.get_attribute('href')
                    link.click()
                    page.wait_for_function('hash => decodeURIComponent(location.hash) === decodeURIComponent(hash)', arg=href)
                    self.assertFalse(page.locator('#toc').is_visible())
                    self.assertEqual(page.locator('#toc-toggle').get_attribute('aria-expanded'), 'false')
                browser.close()

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
