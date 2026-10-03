"""检查小红书最终页序、HTML与独立图片，生成390px预览；仍需逐张目视验收。"""

import argparse
import json
from pathlib import Path
import re
import struct
import sys

from playwright.sync_api import Error, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.visual_qa import inspect_visuals
from scripts.rednote_artifacts import QA_VERSION, load_pages, sha256, source_files


def png_size(path):
    with path.open('rb') as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError('不是有效的 PNG 文件')
    return struct.unpack('>II', header[16:24])


def check_rednote(output_dir):
    output = Path(output_dir).resolve()
    result = {'schema_version': QA_VERSION, 'scene': 'rednote', 'passed': False,
              'issues': [], 'warnings': [], 'pages': [], 'source_files': {}}
    qa_path = output / 'qa-rednote.json'

    def save():
        qa_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # 新检查一开始就撤销旧的通过状态，异常或中断不能沿用旧 QA。
    save()
    try:
        pages = load_pages(output)
    except (ValueError, KeyError) as error:
        result['issues'].append(str(error))
        save()
        raise ValueError(str(error)) from error
    result['source_files'] = source_files(output)
    hashes = {item['file']: sha256(output / item['file']) for item in pages}
    checks = output / 'checks'
    checks.mkdir(exist_ok=True)
    for old in checks.glob('*-mobile.*'):
        if re.fullmatch(r'(cover|card_\d+)-mobile\.(png|html)', old.name):
            old.unlink()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(offline=True, viewport={'width': 1080, 'height': 1440})
        page = context.new_page()
        failures = []
        page.on('requestfailed', lambda request: failures.append(request.url))
        page.on('pageerror', lambda error: failures.append(str(error)))
        for item in pages:
            png = output / item['file']
            visual = {'issues': [], 'warnings': [], 'labels': []}
            try:
                width, height = png_size(png)
                visual['width'], visual['height'] = width, height
                if item['kind'] == 'html':
                    if (width, height) != (2160, 2880):
                        visual['issues'].append('HTML 页 PNG 不是默认2160×2880尺寸')
                    page.set_viewport_size({'width': 1080, 'height': 1440})
                    page.goto((output / item['source']).as_uri())
                    page.evaluate('document.fonts.ready')
                    page.evaluate('Promise.all([...document.images].map(n=>n.decode()))')
                    inspected = inspect_visuals(page, '.card-content,.cover-container', scale=390 / 1080)
                    visual['issues'].extend(inspected['issues'])
                    visual['warnings'].extend(inspected['warnings'])
                    visual['labels'] = inspected['labels']
                    if page.locator('.katex-error').count():
                        visual['issues'].append('公式渲染错误')
                    if page.evaluate('document.documentElement.scrollHeight > 1440 || document.documentElement.scrollWidth > 1080'):
                        visual['issues'].append('源页超出1080×1440画幅')
                else:
                    if width * 4 != height * 3 or width < 1080 or height < 1440:
                        visual['issues'].append('独立图片须为3:4且至少1080×1440')
                    visual['warnings'].append(f"{item['file']}: 位图文字、公式、几何与可读性需逐张目视核对")
                page.set_viewport_size({'width': 390, 'height': 520})
                # 用本地HTML包裹图片，避免about:blank的文件限制和图片文档的load等待。
                preview = checks / f'{png.stem}-mobile.html'
                preview.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0}img{display:block;width:390px;height:auto}</style>'
                                   f'<img src="../{png.name}" alt="{png.stem}">', encoding='utf-8')
                page.goto(preview.as_uri())
                page.evaluate('document.images[0].decode()')
                page.screenshot(path=str(checks / f'{png.stem}-mobile.png'))
            except (ValueError, Error) as error:
                visual['issues'].append(str(error))
            result['pages'].append({**item, 'sha256': hashes[item['file']], **visual})
            result['issues'].extend(f"{item['file']}: {issue}" for issue in visual['issues'])
            result['warnings'].extend(visual['warnings'])
        result['issues'].extend(failures)
        browser.close()
    if source_files(output) != result['source_files'] or any(sha256(output / name) != value for name, value in hashes.items()):
        result['issues'].append('检查过程中图片或源文件改变，请重新检查')
    result['warnings'] = sorted(set(result['warnings']))
    result['passed'] = not result['issues']
    save()
    if not result['passed']:
        raise ValueError('; '.join(result['issues']))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir')
    args = parser.parse_args()
    try:
        print(json.dumps(check_rednote(args.output_dir), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'检查失败：{error}\n')
