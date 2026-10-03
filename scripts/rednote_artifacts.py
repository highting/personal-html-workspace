"""小红书最终页序与验收文件核对；检查器和发布器共用。"""

import hashlib
import json
from pathlib import Path
import re

PAGE_MANIFEST = 'rednote-pages.json'
QA_VERSION = 2


def image_pages(output):
    # 根目录PNG都是最终页；辅助资源应放html/，不能忽略任意命名的残留图片。
    return sorted(Path(output).glob('*.png'))


def load_pages(output):
    output = Path(output).resolve()
    sources = sorted((output / 'html/pages').glob('*.html'))
    manifest = output / PAGE_MANIFEST
    if manifest.is_file():
        pages = json.loads(manifest.read_text(encoding='utf-8'))['pages']
    else:
        pages = [{'file': p.stem + '.png', 'kind': 'html',
                  'source': p.relative_to(output).as_posix()} for p in sources]
        pages.sort(key=lambda item: 0 if item['file'] == 'cover.png' else
                   int(re.search(r'\d+', item['file'])[0]) if re.search(r'\d+', item['file']) else 0)
    if not isinstance(pages, list) or not pages:
        raise ValueError('没有最终页；HTML 制作请用 --save-html，独立图片请填写 rednote-pages.json')
    normalized = []
    for item in pages:
        name, kind = item.get('file', ''), item.get('kind', '')
        if not re.fullmatch(r'(cover|card_[1-9]\d*)\.png', name) or kind not in ('html', 'image'):
            raise ValueError('页清单须使用 cover.png 或 card_N.png，kind 为 html 或 image')
        page = {'file': name, 'kind': kind}
        if kind == 'html':
            source = (output / item.get('source', '')).resolve()
            if source.parent != output / 'html/pages' or source.suffix != '.html' or not source.is_file():
                raise ValueError(f'{name}: HTML 源页必须是 html/pages/ 下已有的 .html 文件')
            page['source'] = source.relative_to(output).as_posix()
        elif 'source' in item:
            raise ValueError(f'{name}: 独立图片页不填写 HTML source')
        normalized.append(page)
    names = [item['file'] for item in normalized]
    count = len(names) - names.count('cover.png')
    expected = (['cover.png'] if 'cover.png' in names else []) + [f'card_{i}.png' for i in range(1, count + 1)]
    if names != expected:
        raise ValueError('页序必须从 card_1.png 连续编号，无重复；cover.png 如有须置于首位')
    if set(names) != {p.name for p in image_pages(output)}:
        raise ValueError('最终 PNG 与页清单不一致，请核对残留或缺失页')
    used_sources = [item['source'] for item in normalized if item['kind'] == 'html']
    if len(used_sources) != len(set(used_sources)) or set(used_sources) != {p.relative_to(output).as_posix() for p in sources}:
        raise ValueError('HTML 源页与页清单不一致，请核对重复、残留或缺失源页')
    return normalized


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_files(output):
    output = Path(output)
    files = [p for p in (output / 'html').rglob('*') if p.is_file()]
    if (output / PAGE_MANIFEST).is_file():
        files.append(output / PAGE_MANIFEST)
    return {p.relative_to(output).as_posix(): sha256(p) for p in sorted(files)}


def validate_rednote_qa(output):
    output = Path(output)
    qa_path = output / 'qa-rednote.json'
    if not qa_path.is_file():
        raise ValueError('小红书交付前请先运行 check_rednote.py，缺少 qa-rednote.json')
    qa = json.loads(qa_path.read_text(encoding='utf-8'))
    if qa.get('schema_version') != QA_VERSION or qa.get('scene') != 'rednote' or qa.get('passed') is not True or qa.get('issues'):
        raise ValueError('小红书需要当前检查器通过的 QA，请重新运行 check_rednote.py')
    pages = load_pages(output)
    checked = qa.get('pages', [])
    descriptors = [{key: page[key] for key in ('file', 'kind', 'source') if key in page} for page in checked]
    if descriptors != pages:
        raise ValueError('小红书页序或制作类型已改变，需要重新检查')
    for page in checked:
        if sha256(output / page['file']) != page.get('sha256'):
            raise ValueError(f"小红书图片 {page['file']} 已改变，需要重新检查")
    if source_files(output) != qa.get('source_files'):
        raise ValueError('小红书 HTML、资源或页清单已改变，需要重新检查')
    return [output / page['file'] for page in pages]
