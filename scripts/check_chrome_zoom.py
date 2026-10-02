"""在临时普通Chrome配置中验证原生页面缩放，不修改日常浏览器配置。"""

import argparse
import base64
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.render_content import inspect_page


def check_chrome_zoom(source, *, scene, output_dir, browser_executable):
    source, output = Path(source).resolve(), Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    result = {'scene': scene, 'method': 'Chrome Appearance / Page zoom',
              'html_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'passed': False, 'issues': [], 'checks': []}
    with tempfile.TemporaryDirectory(prefix='html-craft-zoom-') as folder:
        if not Path(folder).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve()):
            raise ValueError('Chrome检查配置必须位于临时目录')
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                folder, executable_path=browser_executable, headless=True,
                no_viewport=True, offline=True, args=['--window-size=1440,1000'])
            try:
                result['browser_version'] = context.browser.version
                page = context.new_page()
                cdp = context.new_cdp_session(page)
                def capture(path):
                    # 原生zoom后的CSS视口与DIP表面不同，不传CSS尺寸的clip。
                    page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
                    data = base64.b64decode(cdp.send('Page.captureScreenshot', {'format': 'png', 'fromSurface': True})['data'])
                    width, height = struct.unpack('>II', data[16:24])
                    expected = page.evaluate('({width: innerWidth * devicePixelRatio, height: innerHeight * devicePixelRatio})')
                    if abs(width - expected['width']) > 2 or abs(height - expected['height']) > 2:
                        result['issues'].append('原生缩放截图像素尺寸与视口不符: ' + path.name)
                    path.write_bytes(data)
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('requestfailed', lambda request: errors.append('资源加载失败: ' + request.url))
                page.goto(source.as_uri())
                page.evaluate('document.fonts.ready')
                if scene != 'report':
                    page.wait_for_function('window.contentReadingReady === true')
                metrics = lambda: page.evaluate('''() => ({width: innerWidth, height: innerHeight,
                  dpr: devicePixelRatio, css_zoom: getComputedStyle(document.documentElement).zoom})''')
                baseline = metrics()
                result['baseline'] = baseline
                settings = context.new_page()
                settings.goto('chrome://settings/appearance', wait_until='domcontentloaded')
                settings.locator('#zoomLevel').wait_for()
                for zoom in (1, 1.5, 2):
                    settings.locator('#zoomLevel').select_option(str(zoom))
                    page.bring_to_front()
                    expected_dpr = baseline['dpr'] * zoom
                    page.wait_for_function('expected => Math.abs(devicePixelRatio - expected) < .01',
                                           arg=expected_dpr)
                    current = metrics()
                    if current['css_zoom'] != '1' or abs(current['width'] * zoom - baseline['width']) > 2:
                        result['issues'].append(f'{zoom}: 缩放指标不符合Chrome原生缩放')
                    for theme in ('light', 'dark'):
                        page.evaluate('theme => setContentTheme(theme)', theme)
                        issues = inspect_page(page, scene)
                        sizes = []
                        if scene != 'report':
                            page.locator('.prose details').evaluate_all('nodes => nodes.forEach(node => node.open = true)')
                            page.locator('.code-expand[aria-expanded="false"]').evaluate_all('nodes => nodes.forEach(node => node.click())')
                            for size in (16, 24):
                                # 通过真实控件调整字号，覆盖阅读定位的重排逻辑。
                                while int(page.locator('#font-size').inner_text().removesuffix('px')) != size:
                                    value = int(page.locator('#font-size').inner_text().removesuffix('px'))
                                    page.locator('#font-larger' if value < size else '#font-smaller').click()
                                page.evaluate('document.fonts.ready')
                                size_issues = inspect_page(page, scene)
                                sizes.append({'size': size, 'issues': size_issues})
                                issues.extend(f'{size}px: {issue}' for issue in size_issues)
                            while int(page.locator('#font-size').inner_text().removesuffix('px')) > 18:
                                page.locator('#font-smaller').click()
                        else:
                            fits = page.evaluate('''() => {
                              const stage = document.querySelector('.slide-stage').getBoundingClientRect();
                              const frame = document.querySelector('.presentation').getBoundingClientRect();
                              return stage.left >= frame.left - 2 && stage.right <= frame.right + 2 &&
                                stage.top >= frame.top - 2 && stage.bottom <= frame.bottom + 2;
                            }''')
                            if not fits:
                                issues.append('演示舞台超出可见容器')
                        page.evaluate('scrollTo({top: 0, behavior: "instant"})')
                        image = f'chrome-zoom-{round(zoom * 100)}-{theme}.png'
                        capture(output / image)
                        detail_images = []
                        if zoom == 2 and scene != 'report':
                            for name, selector in (('figure', '.prose figure'), ('code', '.prose .code-block'),
                                                   ('table', '.prose .table-wrap'), ('details', '.prose details')):
                                if page.locator(selector).count():
                                    # 用完整视口分屏覆盖图块，不以CSS坐标裁剪DIP图面。
                                    (output / f'chrome-zoom-200-{theme}-{name}.png').unlink(missing_ok=True)
                                    box = page.locator(selector).first.evaluate('node => {const r=node.getBoundingClientRect();return {top:r.top+scrollY,height:r.height}}')
                                    step = page.evaluate('innerHeight - 120')
                                    for index, offset in enumerate(range(0, round(box['height']), max(1, round(step))), 1):
                                        page.evaluate('top => scrollTo({top, behavior: "instant"})', max(0, box['top'] + offset - 100))
                                        detail = f'chrome-zoom-200-{theme}-{name}-{index:02d}.png'
                                        capture(output / detail)
                                        detail_images.append(detail)
                        result['checks'].append({'zoom': zoom, 'theme': theme, 'metrics': current,
                                                 'font_sizes': sizes, 'issues': issues, 'image': image,
                                                 'detail_images': detail_images})
                        result['issues'].extend(f'{zoom}/{theme}: {issue}' for issue in issues)
                result['issues'].extend(errors)
            finally:
                context.close()
    result['passed'] = not result['issues']
    (output / 'qa-chrome-zoom.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not result['passed']:
        raise ValueError('原生缩放检查失败，详见qa-chrome-zoom.json')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html')
    parser.add_argument('--scene', choices=('learning', 'blog', 'report'), required=True)
    parser.add_argument('--output-dir', '-o', required=True)
    parser.add_argument('--browser-executable', required=True, help='完整桌面Chrome路径，不使用Headless Shell')
    args = parser.parse_args()
    result = check_chrome_zoom(args.html, scene=args.scene, output_dir=args.output_dir,
                               browser_executable=args.browser_executable)
    print(json.dumps(result, ensure_ascii=False, indent=2))
