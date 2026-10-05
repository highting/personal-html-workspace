import tempfile
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright
from scripts.build_content import build_content


class ReaderToolsTests(unittest.TestCase):
    def test_width_drag_keeps_track_fixed_and_values_monotonic(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 连续拖动\n\n' + '\n\n'.join(
                f'## 章节 {n}\n\n' + '调整宽度时保持同一段阅读文字。' * 80
                for n in range(8)), encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                for viewport, zoom in ((1920, 1), (1440, 1), (1200, 1), (960, 1), (720, 2)):
                    with self.subTest(viewport=viewport, zoom=zoom):
                        page = browser.new_page(viewport={'width': viewport, 'height': 1000}, offline=True)
                        page.goto(html.as_uri())
                        page.wait_for_function('window.contentReadingReady')
                        page.evaluate('''zoom => {
                            document.documentElement.style.zoom=zoom;
                            document.documentElement.style.scrollBehavior='auto';
                            scrollTo(0,700);
                        }''', zoom)
                        page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
                        slider = page.locator('#reading-width')
                        box = slider.bounding_box()
                        y = box['y'] + box['height'] / 2
                        start = box['x'] + box['width'] / 2
                        page.mouse.move(start, y)
                        page.mouse.down()
                        previous = int(slider.input_value())
                        for direction in (1, -1):
                            for step in range(1, 21):
                                fraction = .5 + direction * step / 40
                                page.mouse.move(box['x'] + 8 * zoom + (box['width'] - 16 * zoom) * fraction, y)
                                current = int(slider.input_value())
                                if direction == 1:
                                    self.assertGreaterEqual(current, previous)
                                else:
                                    self.assertLessEqual(current, previous)
                                actual = slider.bounding_box()
                                for coordinate in ('x', 'y', 'width', 'height'):
                                    self.assertAlmostEqual(actual[coordinate], box[coordinate], delta=1)
                                previous = current
                            page.mouse.up()
                            if direction == 1:
                                page.mouse.move(start, y)
                                page.mouse.down()
                                previous = int(slider.input_value())
                        page.close()
                browser.close()

    def test_percentage_tracks_viewport_and_side_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 百分比宽度\n\n## 开始\n\n' + '阅读正文。' * 100 +
                '\n\n<figure><svg viewBox="0 0 704 240" aria-label="示意图"></svg><figcaption>同栏图注</figcaption></figure>\n\n## 结尾\n\n结束。', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1920, 'height': 1080}, offline=True)
                page.goto(html.as_uri()); page.wait_for_function('window.contentReadingReady')
                page.locator('#reading-width').focus(); page.keyboard.press('End')
                for width in (1920, 1440, 2560, 960):
                    page.set_viewport_size({'width': width, 'height': 1080})
                    page.wait_for_function('w => Math.abs(document.querySelector(".prose").getBoundingClientRect().width-w*.8)<1',arg=width)
                    page.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
                    self.assertEqual(page.input_value('#reading-width'), '80')
                    self.assertEqual(page.locator('#reading-width-value').inner_text(), '80%')
                    prose = page.locator('.prose').bounding_box()
                    for selector in ('.article-header', '.prose figure'):
                        box = page.locator(selector).bounding_box()
                        self.assertAlmostEqual(box['x'],prose['x'],delta=1)
                        self.assertAlmostEqual(box['width'],prose['width'],delta=1)
                    media = page.locator('.prose figure > svg').bounding_box()
                    caption = page.locator('.prose figcaption').bounding_box()
                    self.assertAlmostEqual(caption['x'], media['x'], delta=1)
                    self.assertAlmostEqual(caption['width'], media['width'], delta=1)
                    self.assertTrue(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
                page.reload(); page.wait_for_function('window.contentReadingReady')
                self.assertEqual(page.input_value('#reading-width'), '80')
                self.assertEqual(page.locator('#reading-toolbar #toc-toggle').count(),0)
                page.locator('#toc-toggle').click()
                self.assertTrue(page.locator('#toc').is_visible())
                button = page.locator('#toc-toggle').bounding_box()
                menu = page.locator('#toc').bounding_box()
                self.assertGreater(menu['y'],button['y']+button['height'])
                page.keyboard.press('Escape')
                self.assertFalse(page.locator('#toc').is_visible())
                self.assertEqual(page.evaluate('document.activeElement.id'),'toc-toggle')
                page.click('#toolbar-collapse')
                self.assertTrue(page.locator('#toc-toggle').is_visible())
                page.click('#toc-toggle')
                self.assertTrue(page.locator('#toc').is_visible())
                browser.close()

    def test_width_slider_drag_keyboard_reset_and_saved_preference(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 拖动阅读宽度\n\n' + '\n\n'.join(
                f'## 章节 {n}\n\n' + '行长变化时，应留在正在阅读的这一段文字。' * 50
                for n in range(12)), encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
                page.goto(html.as_uri()); page.wait_for_function('window.contentReadingReady')
                page.evaluate('''() => {
                  document.documentElement.style.scrollBehavior='auto';
                  document.documentElement.style.overflowAnchor='none';
                  const text=document.querySelectorAll('.prose>p')[5].firstChild;
                  window.point=document.createRange();point.setStart(text,320);point.setEnd(text,321);
                  scrollTo(0,point.getBoundingClientRect().top+scrollY-112);
                }''')
                before = page.evaluate('point.getBoundingClientRect().top')
                self.assertEqual(page.locator('.reader-dialog').count(),0)
                self.assertTrue(page.locator('#print-article').is_visible())
                slider = page.locator('#reading-width')
                box = slider.bounding_box()
                y = box['y']+box['height']/2
                page.mouse.move(box['x']+8+(box['width']-16)*.5,y)
                page.mouse.down()
                page.mouse.move(box['x']+box['width']-8,y,steps=12)
                self.assertEqual(slider.input_value(), '80')
                self.assertAlmostEqual(page.locator('.prose>p').first.bounding_box()['width'],1152,delta=1)
                self.assertLessEqual(abs(page.evaluate('point.getBoundingClientRect().top')-before),60)
                page.mouse.up()
                slider.focus(); page.keyboard.press('Home')
                self.assertAlmostEqual(page.locator('.prose>p').first.bounding_box()['width'],576,delta=1)
                page.keyboard.press('ArrowRight')
                self.assertEqual(slider.input_value(),'41')
                self.assertEqual(slider.get_attribute('aria-valuetext'),'页面宽度的 41%')
                page.keyboard.press('Escape')
                page.reload(); page.wait_for_function('window.contentReadingReady')
                self.assertEqual(slider.input_value(),'41')
                self.assertAlmostEqual(page.locator('.prose>p').first.bounding_box()['width'],590.4,delta=1)
                page.click('#reset-reading-width')
                self.assertEqual(slider.input_value(),'60')
                page.keyboard.press('Escape')
                page.evaluate('localStorage.setItem("content-reading-width","wide")')
                page.reload(); page.wait_for_function('window.contentReadingReady')
                self.assertEqual(slider.input_value(),'60')
                page.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw Error("blocked")}})')
                page.reload(); page.wait_for_function('window.contentReadingReady')
                self.assertEqual(slider.input_value(),'60')
                slider.focus();page.keyboard.press('End')
                self.assertEqual(slider.input_value(),'80')
                browser.close()

    def test_palettes_print_width_and_animation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 阅读工具\n\n## 正文\n\n' + '阅读内容。' * 500 +
                '\n\n<details markdown="1"><summary>补充推导</summary>\n\n隐藏的唯一关键词。\n\n</details>\n\n'
                '```python\n' + 'x = 1\n' * 24 + 'print("deep_code_match")\n```\n\n'
                '<figure data-animation><svg viewBox="0 0 600 160" aria-label="两步流程">'
                '<g data-step="1" data-caption="输入"><text x="20" y="40">输入</text></g>'
                '<g data-step="2" data-caption="输出"><text x="20" y="100">输出</text></g>'
                '</svg><figcaption>计算步骤</figcaption></figure>', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True, reduced_motion='reduce')
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                backgrounds = set()
                page.evaluate('document.documentElement.style.scrollBehavior="auto"; scrollTo(0,500)')
                for palette in ['white', 'paper', 'warm', 'graphite', 'midnight', 'ink']:
                    page.select_option('#palette-select', palette)
                    self.assertEqual(page.evaluate('document.documentElement.dataset.palette'), palette)
                    self.assertAlmostEqual(page.evaluate('scrollY'), 500, delta=1)
                    backgrounds.add(page.evaluate('getComputedStyle(document.body).backgroundColor'))
                self.assertEqual(len(backgrounds), 6)
                page.reload(); page.wait_for_function('window.contentReadingReady')
                self.assertEqual(page.input_value('#palette-select'), 'ink')
                page.click('#theme-toggle')
                self.assertEqual(page.input_value('#palette-select'), 'warm')
                page.locator('#reading-width').focus()
                page.keyboard.press('End')
                self.assertEqual(page.locator('#reading-width-value').inner_text(), '80%')
                page.keyboard.press('Escape')
                self.assertEqual(page.locator('#search-open').count(), 0)
                figure = page.locator('figure[data-animation]')
                self.assertEqual(figure.get_attribute('data-current-step'), '2')
                page.click('[data-reset]'); self.assertEqual(figure.get_attribute('data-current-step'), '1')
                page.click('[data-play]'); page.wait_for_timeout(1750)
                self.assertEqual(figure.get_attribute('data-current-step'), '2')
                self.assertEqual(page.locator('[data-play]').inner_text(), '播放')
                page.click('[data-reset]')
                page.locator('details').evaluate('n=>n.open=false')
                page.evaluate('dispatchEvent(new Event("beforeprint"))')
                page.emulate_media(media='print')
                self.assertTrue(page.locator('details').evaluate('n=>n.open'))
                self.assertFalse(page.locator('.toolbar').is_visible())
                self.assertEqual(page.evaluate('getComputedStyle(document.body).backgroundColor'), 'rgb(255, 255, 255)')
                page.emulate_media(media='screen'); page.evaluate('dispatchEvent(new Event("afterprint"))')
                self.assertFalse(page.locator('details').evaluate('n=>n.open'))
                self.assertEqual(figure.get_attribute('data-current-step'), '1')
                self.assertEqual(errors, [])
                browser.close()

    def test_storage_unavailable_and_report_palettes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'main.md'
            source.write_text('# 第一页\n\n文字\n\n---\n\n# 第二页\n\n说明', encoding='utf-8')
            html = build_content(source, scene='report', output=root / 'index.html')
            with sync_playwright() as p:
                browser = p.chromium.launch(); page = browser.new_page(offline=True)
                page.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw Error("blocked")}})')
                page.goto(html.as_uri()); page.click('#next-slide')
                page.select_option('#palette-select', 'ink')
                self.assertEqual(page.locator('#slide-counter').inner_text(), '2 / 2')
                self.assertEqual(page.evaluate('document.documentElement.dataset.palette'), 'ink')
                browser.close()


if __name__ == '__main__':
    unittest.main()
