from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content


class NavigationTests(unittest.TestCase):
    def test_directory_resize_keeps_gap_position_and_saved_width(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 可调目录\n\n' + '\n\n'.join(
                f'## 章节 {n}\n\n' + '目录调整宽度后继续阅读同一处文字。' * 100
                for n in range(20)) + '\n\n```python\n' + 'print("代码操作换行")\n' * 24 + '```', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                page.locator('#reading-width').focus()
                page.keyboard.press('End')
                page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
                page.evaluate('scrollTo(0, 1800)')
                page.wait_for_timeout(50)
                def point_top():
                    return page.evaluate('point.range ? point.range.getBoundingClientRect().top : point.block.getBoundingClientRect().top + point.block.getBoundingClientRect().height * point.fraction')
                page.evaluate('window.point = window.captureContentPosition()')
                before = point_top()
                page.locator('#toc-toggle').click()
                self.assertAlmostEqual(point_top(), before, delta=2)
                handle = page.locator('.toc-resize-handle')
                box = handle.bounding_box()
                page.mouse.move(box['x'] + 8, box['y'] + 50)
                page.mouse.down()
                page.mouse.move(box['x'] + 108, box['y'] + 50, steps=10)
                page.mouse.up()
                self.assertEqual(handle.get_attribute('aria-valuenow'), '300')
                self.assertAlmostEqual(point_top(), before, delta=2)
                for width, zoom in ((1440, 1), (960, 1), (720, 2)):
                    page.set_viewport_size({'width': width, 'height': 1000})
                    page.evaluate('z => document.documentElement.style.zoom = z', zoom)
                    page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
                    if not page.locator('#toc').is_visible():
                        page.locator('#toc-toggle').click()
                    toc, main = (page.locator(q).bounding_box() for q in ('#toc', '#content'))
                    self.assertGreaterEqual(toc['x'], 30 * zoom)
                    self.assertGreaterEqual(main['x'] - toc['x'] - toc['width'], 24 * zoom - 1)
                    self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
                page.evaluate('document.documentElement.style.zoom = 1')
                page.set_viewport_size({'width': 1440, 'height': 1000})
                page.reload()
                page.wait_for_function('window.contentReadingReady')
                page.locator('#toc-toggle').click()
                self.assertAlmostEqual(page.locator('#toc').bounding_box()['width'], 300, delta=1)
                page.keyboard.press('Escape')
                self.assertAlmostEqual(page.locator('.prose').bounding_box()['width'], 1152, delta=1)
                browser.close()

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
                page.evaluate('document.documentElement.style.overflowAnchor="none"')
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
                    page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
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
                    position = page.evaluate('''() => {
                      const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
                      return {top: target.getBoundingClientRect().top,
                        padding: parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop)};
                    }''')
                    self.assertAlmostEqual(position['top'], position['padding'], delta=2)
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
