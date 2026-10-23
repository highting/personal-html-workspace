import unittest

from playwright.sync_api import sync_playwright
from scripts.check_chrome_zoom import scroll_menu_to_end


class ChromeZoomScrollTests(unittest.TestCase):
    def test_long_directory_reaches_last_item_without_scrolling_body(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={'width': 800, 'height': 600})
            links = ''.join(f'<a href="#item-{i}">章节 {i}</a>' for i in range(400))
            page.set_content('<style>body{height:4000px}nav{position:fixed;top:20px;left:20px;'
                             'width:220px;height:260px;overflow:auto;overscroll-behavior:contain}'
                             'a{display:block;height:30px}</style><nav>' + links + '</nav>')
            page.evaluate('scrollTo(0,500)')
            menu = page.locator('nav')
            self.assertTrue(scroll_menu_to_end(page, menu))
            self.assertLessEqual(menu.evaluate('n=>n.scrollHeight-n.clientHeight-n.scrollTop'), 2)
            self.assertEqual(page.evaluate('scrollY'), 500)
            self.assertTrue(menu.evaluate('''n=>{
                const box=n.getBoundingClientRect(), last=n.lastElementChild.getBoundingClientRect();
                return last.top>=box.top && last.bottom<=box.bottom+1;
            }'''))
            browser.close()

    def test_unscrollable_directory_does_not_claim_to_reach_end(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.set_content('<nav style="height:100px;width:220px;overflow:hidden">'
                             '<div style="height:2000px">目录</div></nav>')
            self.assertFalse(scroll_menu_to_end(page, page.locator('nav')))
            browser.close()


if __name__ == '__main__':
    unittest.main()
