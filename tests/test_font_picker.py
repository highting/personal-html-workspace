import tempfile
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright
from scripts.build_content import build_content


class FontPickerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        root = Path(cls.folder.name)
        source = root / 'main.md'
        source.write_text('# 字体选择\n\n' + '\n\n'.join(
            f'## 章节 {n}\n\n' + '字体变化后，应继续阅读当前文字。Reading with a different font. ' * 35
            for n in range(8)) + '\n\n公式 \\(x^2 + y^2\\)。\n\n```python\nprint("字体")\n```', encoding='utf-8')
        cls.html = build_content(source, output=root / 'index.html')

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def open_page(self, browser, script=None):
        page = browser.new_page(offline=True, viewport={'width': 1440, 'height': 1000})
        if script:
            page.add_init_script(script)
        page.goto(self.html.as_uri())
        page.wait_for_function('window.contentReadingReady')
        return page

    def test_search_keyboard_actual_fonts_position_and_saved_choice(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = self.open_page(browser)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            special = "['.code-block code','.katex .mord','.toolbar'].map(s=>getComputedStyle(document.querySelector(s)).fontFamily)"
            before_special = page.evaluate(special)
            cdp = page.context.new_cdp_session(page)
            cdp.send('DOM.enable'); cdp.send('CSS.enable')

            def fonts():
                root = cdp.send('DOM.getDocument')['root']['nodeId']
                node = cdp.send('DOM.querySelector', {'nodeId': root, 'selector': '.prose > p'})['nodeId']
                return cdp.send('CSS.getPlatformFontsForNode', {'nodeId': node})['fonts']

            self.assertTrue(any(font['isCustomFont'] for font in fonts()))
            page.evaluate('''() => {
              document.documentElement.style.scrollBehavior='auto';
              document.documentElement.style.overflowAnchor='none';
              const text=document.querySelectorAll('.prose>p')[4].firstChild;
              window.point=document.createRange();point.setStart(text,320);point.setEnd(text,321);
              scrollTo(0,point.getBoundingClientRect().top+scrollY-160);
            }''')
            before = page.evaluate('point.getBoundingClientRect().top')
            page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            box = page.locator('#font-picker-toggle').bounding_box()
            page.mouse.click(box['x']+box['width']/2, box['y']+box['height']/2)
            page.fill('#font-search', '浏览器等宽')
            self.assertEqual(page.locator('#font-options').get_by_role('option').count(), 1)
            page.keyboard.press('Enter')
            self.assertFalse(page.locator('#font-picker').is_visible())
            self.assertEqual(page.evaluate('document.activeElement.id'), 'font-picker-toggle')
            self.assertEqual(page.locator('.prose').evaluate('n=>getComputedStyle(n).fontFamily'), 'monospace')
            self.assertLessEqual(abs(page.evaluate('point.getBoundingClientRect().top') - before), 60)
            self.assertFalse(any(font['isCustomFont'] for font in fonts()))
            self.assertEqual(before_special, page.evaluate(special))
            page.reload(); page.wait_for_function('window.contentReadingReady')
            self.assertEqual(page.locator('#font-family-label').inner_text(), '浏览器等宽')
            page.click('#font-picker-toggle'); page.fill('#font-search', '不可能存在的字体')
            self.assertEqual(page.locator('#font-options').get_by_role('option').count(), 0)
            self.assertIn('没有匹配', page.locator('#font-picker-status').inner_text())
            page.keyboard.press('Escape')
            self.assertEqual(page.evaluate('document.activeElement.id'), 'font-picker-toggle')
            page.click('#font-picker-toggle'); page.fill('#font-search', 'Noto'); page.keyboard.press('Enter')
            self.assertTrue(any(font['isCustomFont'] for font in fonts()))
            self.assertEqual(errors, [])
            browser.close()

    def test_local_enumeration_dedup_search_persistence_and_retry(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = self.open_page(browser, '''window.fontCalls=0; window.fontFailure=false;
              window.queryLocalFonts=async()=>{
                fontCalls++;
                if(fontFailure) throw new DOMException('Denied','NotAllowedError');
                return [
                  {family:'Microsoft YaHei',fullName:'Microsoft YaHei',postscriptName:'MicrosoftYaHei'},
                  {family:'Microsoft YaHei',fullName:'Microsoft YaHei Bold',postscriptName:'MicrosoftYaHei-Bold'},
                  {family:'@Microsoft YaHei',fullName:'Vertical',postscriptName:'Vertical'},
                  ...Array.from({length:600},(_,i)=>({family:'Font '+String(i).padStart(3,'0'),fullName:'Font '+i,postscriptName:'Font'+i}))
                ];
              };''')
            page.click('#font-picker-toggle')
            self.assertEqual(page.evaluate('fontCalls'), 0)
            page.click('#load-local-fonts')
            self.assertEqual(page.locator('#font-options').get_by_role('option').count(), 606)
            page.fill('#font-search', '微软雅黑')
            self.assertEqual(page.locator('#font-options').get_by_role('option').count(), 1)
            page.keyboard.press('Enter')
            self.assertEqual(page.locator('#font-family-label').inner_text(), 'Microsoft YaHei')
            page.reload(); page.wait_for_function('window.contentReadingReady')
            self.assertEqual(page.locator('#font-family-label').inner_text(), 'Microsoft YaHei')
            self.assertEqual(page.evaluate('fontCalls'), 0)
            page.click('#font-picker-toggle'); page.evaluate('fontFailure=true'); page.click('#load-local-fonts')
            self.assertIn('未获字体访问授权', page.locator('#font-picker-status').inner_text())
            self.assertTrue(page.locator('#load-local-fonts').is_enabled())
            page.evaluate('fontFailure=false'); page.click('#load-local-fonts')
            self.assertIn('601', page.locator('#font-picker-status').inner_text())
            page.fill('#font-search', 'FONT 599')
            self.assertEqual(page.locator('#font-options').get_by_role('option').inner_text(), 'Font 599')
            page.keyboard.press('ArrowDown'); page.keyboard.press('Enter')
            self.assertEqual(page.locator('#font-family-label').inner_text(), 'Font 599')
            browser.close()

    def test_unsupported_empty_storage_and_panel_bounds(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = self.open_page(browser, '''window.queryLocalFonts=undefined;
              Object.defineProperty(window,'localStorage',{get(){throw Error('blocked')}});''')
            page.click('#font-picker-toggle')
            self.assertFalse(page.locator('#load-local-fonts').is_visible())
            self.assertIn('不支持', page.locator('#font-picker-status').inner_text())
            page.fill('#font-search', '系统'); page.keyboard.press('Enter')
            self.assertEqual(page.locator('.prose').evaluate('n=>getComputedStyle(n).fontFamily'), 'system-ui')
            for width, height in ((1440, 1000), (960, 667), (720, 500)):
                page.set_viewport_size({'width': width, 'height': height})
                for zoom in (1, 1.5, 2):
                    page.evaluate('z=>document.documentElement.style.zoom=z', zoom)
                    page.click('#font-picker-toggle')
                    box = page.locator('#font-picker').bounding_box()
                    self.assertGreaterEqual(box['x'], 0)
                    self.assertGreaterEqual(box['y'], 0)
                    self.assertLessEqual(box['x']+box['width'], width+1)
                    self.assertLessEqual(box['y']+box['height'], height+1)
                    self.assertTrue(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
                    page.keyboard.press('Escape')
            page.close()
            page = self.open_page(browser, 'window.queryLocalFonts=async()=>[]')
            page.click('#font-picker-toggle'); page.click('#load-local-fonts')
            self.assertIn('未返回字体列表', page.locator('#font-picker-status').inner_text())
            self.assertEqual(page.locator('#font-options').get_by_role('option').count(), 5)
            page.click('#toolbar-collapse')
            self.assertFalse(page.locator('#font-picker').is_visible())
            browser.close()


if __name__ == '__main__':
    unittest.main()
