from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright
from scripts.build_content import build_content


class SvgZoomTests(unittest.TestCase):
    def test_native_zoom_scales_svg_and_saved_manual_size(self):
        chrome = Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
        if not chrome.is_file():
            self.skipTest('需要完整Chrome的原生页面缩放控件')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# SVG缩放\n\n## 图\n\n正文。\n\n'
                              '<figure><svg viewBox="0 0 760 240" aria-label="示意图">'
                              '<text x="20" y="40" font-size="18">图中文字</text></svg>'
                              '<figcaption>同栏图注</figcaption></figure>', encoding='utf-8')
            html = build_content(source, output=root / 'index.html')
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    str(root / 'chrome-profile'), executable_path=str(chrome), headless=True,
                    no_viewport=True, offline=True, args=['--window-size=1440,1000'])
                page = context.new_page()
                page.goto(html.as_uri())
                page.wait_for_function('window.contentReadingReady')
                svg = page.locator('.prose figure > svg')
                physical_width = lambda: svg.evaluate('n=>n.getBoundingClientRect().width*devicePixelRatio')
                settings = context.new_page()
                settings.goto('chrome://settings/appearance', wait_until='domcontentloaded')
                zoom_control = settings.locator('#zoomLevel')
                zoom_control.wait_for()
                baseline_dpr = page.evaluate('devicePixelRatio')
                original_width = physical_width()
                for zoom in (.8, .5, 1):
                    zoom_control.select_option(str(zoom))
                    page.wait_for_function('dpr=>Math.abs(devicePixelRatio-dpr)<.01', arg=baseline_dpr*zoom)
                    self.assertAlmostEqual(physical_width(), original_width*zoom, delta=2)
                handle = page.locator('.image-resize-handle')
                handle.focus()
                page.keyboard.press('Home')
                self.assertEqual(handle.get_attribute('aria-valuenow'), '40')
                manual_width = physical_width()
                for zoom in (.8, 1):
                    zoom_control.select_option(str(zoom))
                    page.wait_for_function('dpr=>Math.abs(devicePixelRatio-dpr)<.01', arg=baseline_dpr*zoom)
                    self.assertAlmostEqual(physical_width(), manual_width*zoom, delta=2)
                    page.reload()
                    page.wait_for_function('window.contentReadingReady')
                    self.assertEqual(handle.get_attribute('aria-valuenow'), '40')
                    self.assertAlmostEqual(physical_width(), manual_width*zoom, delta=2)
                page.locator('.image-size-reset').click()
                self.assertAlmostEqual(physical_width(), original_width, delta=2)
                page.locator('#reading-width').focus()
                page.keyboard.press('Home')
                self.assertLessEqual(svg.bounding_box()['width'], page.locator('.prose').bounding_box()['width']+1)
                context.close()


if __name__ == '__main__':
    unittest.main()
