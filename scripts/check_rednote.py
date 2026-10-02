"""检查默认小红书源页并生成390px宽的最终PNG预览；仍需逐张目视验收。"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.visual_qa import inspect_visuals


def check_rednote(output_dir):
    output = Path(output_dir).resolve()
    checks = output / 'checks'
    checks.mkdir(exist_ok=True)
    for old in checks.glob('*-mobile.png'):
        if re.fullmatch(r'(cover|card_\d+)-mobile\.png', old.name):
            old.unlink()
    pages = sorted((output / 'html/pages').glob('*.html'),
                   key=lambda p: (p.stem != 'cover', int(re.search(r'\d+', p.stem)[0]) if re.search(r'\d+', p.stem) else 0))
    result = {'passed': False, 'issues': [], 'warnings': [], 'pages': []}
    if not pages:
        result['issues'].append('没有源页，请先用 --save-html 渲染')
    expected = {p.stem + '.png' for p in pages}
    actual = {p.name for p in output.glob('*.png') if re.fullmatch(r'(cover|card_\d+)\.png', p.name)}
    if expected != actual:
        result['issues'].append('PNG与源页清单不一致，请核对残留或缺失页')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(offline=True, viewport={'width': 1080, 'height': 1440})
        page = context.new_page()
        failures = []
        page.on('requestfailed', lambda request: failures.append(request.url))
        page.on('pageerror', lambda error: failures.append(str(error)))
        for source in pages:
            page.set_viewport_size({'width': 1080, 'height': 1440})
            page.goto(source.as_uri())
            page.evaluate('document.fonts.ready')
            visual = inspect_visuals(page, '.card-content,.cover-container', scale=390 / 1080)
            if page.locator('.katex-error').count():
                visual['issues'].append('公式渲染错误')
            if page.evaluate('document.documentElement.scrollHeight > 1440 || document.documentElement.scrollWidth > 1080'):
                visual['issues'].append('源页超出1080×1440画幅')
            png = output / (source.stem + '.png')
            if png.is_file():
                data = png.read_bytes()
                if struct.unpack('>II', data[16:24]) != (2160, 2880):
                    visual['issues'].append('PNG不是默认2160×2880尺寸')
                visual['sha256'] = hashlib.sha256(data).hexdigest()
                page.set_viewport_size({'width': 390, 'height': 520})
                page.set_content('<style>body{margin:0}img{display:block;width:390px;height:520px}</style><img>')
                page.locator('img').evaluate('(node,src) => node.src=src', png.as_uri())
                page.evaluate('document.images[0].decode()')
                page.screenshot(path=str(checks / f'{source.stem}-mobile.png'))
            result['pages'].append({'file': png.name, **visual})
            result['issues'].extend(f'{source.stem}: {i}' for i in visual['issues'])
            result['warnings'].extend(visual['warnings'])
        result['issues'].extend(failures)
        browser.close()
    result['warnings'] = sorted(set(result['warnings']))
    result['passed'] = not result['issues']
    (output / 'qa-rednote.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not result['passed']:
        raise ValueError('; '.join(result['issues']))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir')
    args = parser.parse_args()
    print(json.dumps(check_rednote(args.output_dir), ensure_ascii=False, indent=2))
