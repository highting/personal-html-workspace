import tempfile
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright
from scripts.build_content import build_content


class ReaderToolsTests(unittest.TestCase):
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
                page.mouse.move(box['x']+8+(box['width']-16)*.36,y)
                page.mouse.down()
                page.mouse.move(box['x']+box['width']-8,y,steps=12)
                self.assertEqual(slider.input_value(), '960')
                self.assertEqual(page.locator('.prose>p').first.bounding_box()['width'],960)
                self.assertLessEqual(abs(page.evaluate('point.getBoundingClientRect().top')-before),60)
                page.mouse.up()
                slider.focus(); page.keyboard.press('Home')
                self.assertEqual(page.locator('.prose>p').first.bounding_box()['width'],560)
                page.keyboard.press('ArrowRight')
                self.assertEqual(slider.input_value(),'568')
                self.assertEqual(slider.get_attribute('aria-valuetext'),'568 像素')
                page.keyboard.press('Escape')
                page.reload(); page.wait_for_function('window.contentReadingReady')
                self.assertEqual(slider.input_value(),'568')
                self.assertEqual(page.locator('.prose>p').first.bounding_box()['width'],568)
                page.click('#reset-reading-width')
                self.assertEqual(slider.input_value(),'704')
                page.keyboard.press('Escape')
                page.evaluate('localStorage.setItem("content-reading-width","wide")')
                page.reload(); page.wait_for_function('window.contentReadingReady')
                self.assertEqual(slider.input_value(),'792')
                page.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw Error("blocked")}})')
                page.reload(); page.wait_for_function('window.contentReadingReady')
                self.assertEqual(slider.input_value(),'704')
                slider.focus();page.keyboard.press('End')
                self.assertEqual(slider.input_value(),'960')
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
                self.assertEqual(page.locator('#reading-width-value').inner_text(), '960 px')
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
