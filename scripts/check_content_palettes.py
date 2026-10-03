"""检查六套配色的实际对比度、控件可达性与内容边界，保存代表画面。"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.render_content import inspect_page
from scripts.visual_qa import inspect_palette

PALETTES = ('white', 'paper', 'warm', 'graphite', 'midnight', 'ink')


def check_content_palettes(source, *, scene, output_dir):
    source, output = Path(source).resolve(), Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    result = {'html_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'passed': False,
              'scene': scene, 'palettes': {}, 'issues': []}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, offline=True)
        page.on('pageerror', lambda error: result['issues'].append(str(error)))
        page.on('requestfailed', lambda request: result['issues'].append('离线资源失败: ' + request.url))
        page.goto(source.as_uri()); page.evaluate('document.fonts.ready')
        if scene != 'report':
            page.wait_for_function('window.contentReadingReady')
        page.evaluate('document.documentElement.style.scrollBehavior="auto"')
        for palette in PALETTES:
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.select_option('#palette-select', palette)
            colors = inspect_palette(page)
            issues = [f"对比度不足: {c['fg']}/{c['bg']}" for c in colors if not c['passed']]
            if scene == 'report':
                page.keyboard.press('Home')
            else:
                page.evaluate('scrollTo(0,0)')
            page.screenshot(path=str(output / f'{palette}-top.png'))
            for width, height in ((1440, 1000), (960, 667), (720, 500)):
                page.set_viewport_size({'width': width, 'height': height})
                issues.extend(inspect_page(page, scene))
                controls_fit = page.locator('.toolbar').evaluate('''bar => [...bar.querySelectorAll('button,select')].every(n => {
                    const r=n.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.top>=0&&r.bottom<=innerHeight;
                })''')
                if not controls_fit:
                    issues.append(f'{width}px工具栏控件超出视口')
                if width == 720:
                    page.screenshot(path=str(output / f'{palette}-compact.png'))
            page.set_viewport_size({'width': 1440, 'height': 1000})
            if scene != 'report':
                for label, selector in [('figure', '.prose figure'), ('code', '.code-block'), ('table', '.table-block')]:
                    for i, node in enumerate(page.locator(selector).all(), 1):
                        node.scroll_into_view_if_needed()
                        page.screenshot(path=str(output / f'{palette}-{label}-{i}.png'))
            else:
                for i in range(page.locator('[data-export-page]').count()):
                    if i:
                        page.keyboard.press('ArrowRight')
                    issues.extend(inspect_page(page, scene))
                    page.screenshot(path=str(output / f'{palette}-slide-{i+1}.png'))
            result['palettes'][palette] = {'palette': colors, 'issues': issues, 'passed': not issues}
            result['issues'].extend(palette + ': ' + issue for issue in issues)
        if scene != 'report':
            page.evaluate('scrollTo(0,0)')
            page.locator('#reading-width').focus()
            page.screenshot(path=str(output / 'reading-toolbar.png'))
            figure = page.locator('figure[data-animation]').first
            if figure.count():
                figure.scroll_into_view_if_needed()
                page.click('[data-reset]')
                count = figure.locator('svg > [data-step]').count()
                for i in range(count):
                    if i:
                        page.click('[data-next]')
                    page.wait_for_timeout(450)
                    figure.screenshot(path=str(output / f'animation-step-{i+1}.png'))
                page.click('[data-all]')
            page.evaluate('dispatchEvent(new Event("beforeprint"))')
            page.emulate_media(media='print')
            page.evaluate('scrollTo(0,0)')
            page.screenshot(path=str(output / 'print-top.png'))
            if page.locator('.toolbar').is_visible():
                result['issues'].append('打印时工具栏未隐藏')
            page.emulate_media(media='screen')
            page.evaluate('dispatchEvent(new Event("afterprint"))')
        browser.close()
    result['passed'] = not result['issues']
    (output / 'qa-palettes.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    if not result['passed']:
        raise ValueError('; '.join(result['issues']))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--scene', required=True, choices=('learning', 'blog', 'report'))
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    print(check_content_palettes(args.source, scene=args.scene, output_dir=args.output_dir)['passed'])
