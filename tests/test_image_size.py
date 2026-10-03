import base64
from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright
from scripts.build_content import build_content


class ImageSizeTests(unittest.TestCase):
    def test_drag_keeps_ratio_caption_and_viewer_and_saves_size(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            source=root/'main.md'
            source.write_text('# 拖动图片\n\n## 图解\n\n正文说明。\n\n'
                '<figure><svg viewBox="0 0 800 360" aria-label="比例图"><rect width="800" height="360" class="diagram-fill"/></svg>'
                '<figcaption>图注保持完整，始终按正文栏宽排布。</figcaption></figure>',encoding='utf-8')
            target=build_content(source,output=root/'index.html')
            with sync_playwright() as p:
                browser=p.chromium.launch()
                page=browser.new_page(viewport={'width':1440,'height':1000},offline=True)
                page.goto(target.as_uri());page.wait_for_function('window.contentReadingReady')
                media=page.locator('.prose figure > svg')
                handle=page.locator('.image-resize-handle')
                caption=page.locator('figcaption')
                media.scroll_into_view_if_needed()
                original=media.bounding_box()
                caption_width=caption.bounding_box()['width']
                box=handle.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
                page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-180,y-80,steps=10);page.mouse.up()
                resized=media.bounding_box()
                self.assertLess(resized['width'],original['width']*.8)
                self.assertGreater(resized['width'],original['width']*.6)
                self.assertAlmostEqual(caption.bounding_box()['width'],caption_width,delta=1)
                scales=media.evaluate('n=>{const m=n.getScreenCTM();return [m.a,m.d]}')
                self.assertAlmostEqual(scales[0],scales[1],delta=.001)
                self.assertFalse(page.locator('.image-viewer').is_visible())
                saved=handle.get_attribute('aria-valuenow')
                page.reload();page.wait_for_function('window.contentReadingReady')
                self.assertEqual(handle.get_attribute('aria-valuenow'),saved)
                media.click()
                self.assertTrue(page.locator('.image-viewer').is_visible())
                self.assertEqual(page.locator('.image-viewer-caption').inner_text(),caption.inner_text())
                page.keyboard.press('Escape')
                handle.focus();page.keyboard.press('Home')
                self.assertEqual(handle.get_attribute('aria-valuenow'),'40')
                page.keyboard.press('End')
                self.assertEqual(handle.get_attribute('aria-valuenow'),'100')
                page.keyboard.press('ArrowLeft')
                page.locator('.image-size-reset').click()
                self.assertAlmostEqual(media.bounding_box()['width'],original['width'],delta=1)
                self.assertTrue(page.locator('.image-size-reset').is_hidden())
                box=handle.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
                page.mouse.move(x,y);page.mouse.down();page.mouse.move(x,y-60,steps=5);page.mouse.up()
                self.assertLess(media.bounding_box()['height'],original['height']-40)
                page.locator('.image-size-reset').click()
                page.emulate_media(media='print')
                self.assertFalse(handle.is_visible())
                browser.close()

    def test_png_drag_persists_and_reset_restores_original_size(self):
        with tempfile.TemporaryDirectory() as folder, sync_playwright() as p:
            root = Path(folder)
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
            png = page.evaluate('''() => {
              const canvas = document.createElement('canvas');
              canvas.width = 600; canvas.height = 300;
              const context = canvas.getContext('2d');
              context.fillStyle = 'gray'; context.fillRect(0, 0, 600, 300);
              return canvas.toDataURL('image/png');
            }''')
            source = root / 'main.md'
            source.write_text('# 位图尺寸记忆\n\n![位图](' + png + ')', encoding='utf-8')
            target = build_content(source, output=root / 'index.html')
            page.goto(target.as_uri())
            page.wait_for_function('window.contentReadingReady')
            media = page.locator('.prose img')
            handle = page.locator('.image-resize-handle')
            media.scroll_into_view_if_needed()
            original = media.bounding_box()
            box = handle.bounding_box()
            x, y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
            page.mouse.move(x, y)
            page.mouse.down()
            page.mouse.move(x - 160, y - 80, steps=10)
            page.mouse.up()
            resized = media.bounding_box()
            self.assertLess(resized['width'], original['width'] * .85)
            self.assertAlmostEqual(resized['width'] / resized['height'], 2, delta=.01)
            page.reload()
            page.wait_for_function('window.contentReadingReady')
            self.assertAlmostEqual(media.bounding_box()['width'], resized['width'], delta=1)
            page.locator('.image-size-reset').click()
            page.reload()
            page.wait_for_function('window.contentReadingReady')
            self.assertAlmostEqual(media.bounding_box()['width'], original['width'], delta=1)
            self.assertTrue(page.locator('.image-size-reset').is_hidden())
            browser.close()

    def test_raster_style_image_without_figure_and_storage_unavailable(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            encoded=base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300"><rect width="600" height="300" fill="gray"/></svg>').decode()
            source=root/'main.md'
            source.write_text('# 图片\n\n![本地图](data:image/svg+xml;base64,'+encoded+')',encoding='utf-8')
            target=build_content(source,output=root/'index.html')
            with sync_playwright() as p:
                browser=p.chromium.launch()
                page=browser.new_page(viewport={'width':960,'height':1000},offline=True)
                page.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw Error("blocked")}})')
                page.goto(target.as_uri());page.wait_for_function('window.contentReadingReady')
                media=page.locator('.prose img')
                handle=page.locator('.image-resize-handle')
                handle.focus();page.keyboard.press('Home')
                box=media.bounding_box()
                self.assertAlmostEqual(box['width']/box['height'],2,delta=.01)
                self.assertLess(box['width'],page.locator('.prose').bounding_box()['width'])
                media.click();self.assertTrue(page.locator('.image-viewer').is_visible())
                page.keyboard.press('Escape')
                self.assertFalse(page.locator('.image-viewer-caption').is_visible())
                browser.close()


if __name__=='__main__':
    unittest.main()
