import asyncio
from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from scripts.build_content import build_content
from scripts.rednote_render import render_markdown_to_cards


class PaletteBridgeTests(unittest.TestCase):
    def test_shared_svg_colors_match_without_changing_card_typography(self):
        svg = '''<figure><svg viewBox="0 0 600 120">
<defs><marker id="arrow"><path id="arrow-fill" d="M0 0L10 5L0 10Z" fill="var(--accent)"/></marker></defs>
<rect id="node" class="diagram-fill" x="20" y="20" width="100" height="60"/>
<rect id="emphasis" class="diagram-emphasis-fill" x="150" y="20" width="100" height="60"/>
<rect id="comparison" class="diagram-compare-fill" x="280" y="20" width="100" height="60"/>
<rect id="secondary" class="diagram-secondary-fill" x="410" y="20" width="100" height="60"/>
<path id="primary-line" class="diagram-line" d="M20 100H120" fill="none" stroke="var(--accent)"/>
<path id="comparison-line" class="diagram-compare" d="M150 100H250" fill="none"/>
<path id="secondary-line" class="diagram-secondary" d="M280 100H380" fill="none"/>
<text id="label" x="30" y="60" font-size="24">同组</text>
</svg></figure>'''
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'main.md'
            source.write_text('# 语义配色\n\n' + svg, encoding='utf-8')
            reading = build_content(source, output=root / 'reading.html')
            asyncio.run(render_markdown_to_cards(
                str(source), str(root / 'card'), theme='academic',
                math_mode='off', output_format='html',
            ))
            card = root / 'card/pages/card_1.html'
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(offline=True)
                results = []
                for document in (reading, card):
                    page.goto(document.as_uri())
                    page.evaluate('document.fonts.ready')
                    results.append(page.evaluate('''() => Object.fromEntries(
                      ['node','emphasis','comparison','secondary','arrow-fill','primary-line','comparison-line','secondary-line','label']
                      .map(id => {const style=getComputedStyle(document.getElementById(id));return [id,{fill:style.fill,stroke:style.stroke}]}))'''))
                self.assertEqual(results[0], results[1])
                self.assertNotEqual(results[1]['node']['fill'], 'rgb(0, 0, 0)')
                self.assertNotEqual(results[1]['primary-line']['stroke'], 'none')
                self.assertEqual(page.locator('.card-content').evaluate('n => getComputedStyle(n).fontSize'), '38px')
                self.assertIn('Microsoft YaHei', page.locator('.card-content').evaluate('n => getComputedStyle(n).fontFamily'))
                browser.close()


if __name__ == '__main__':
    unittest.main()
