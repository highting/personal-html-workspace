"""将学习稿、博客或汇报稿组装为可切换明暗主题的单文件 HTML。"""

import argparse
import base64
import hashlib
from functools import lru_cache
from html import escape, unescape
from io import BytesIO
import mimetypes
from pathlib import Path
import re
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.rednote_render import KATEX_DIR, convert_markdown_to_html, parse_markdown_file
from scripts.content_markup import enhance_code_blocks, group_figure_captions

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / 'assets/content'
LABELS = {'learning': '学习笔记', 'blog': '技术博客', 'report': '技术汇报'}
FONT_DIR = ROOT / 'assets/vendor/noto-sans-sc'


def font_assets(text):
    path = FONT_DIR / 'NotoSansSC-variable.ttf'
    if not path.is_file():
        raise ValueError('缺少中文字体缓存，请先运行 python scripts/download_content_fonts.py')
    options = subset.Options()
    options.recalc_timestamp = False
    with TTFont(path, recalcTimestamp=False) as font:
        sub = subset.Subsetter(options=options)
        sub.populate(text=text + ''.join(chr(code) for code in range(32, 127)))
        sub.subset(font)
        font.flavor = 'woff2'
        output = BytesIO()
        font.save(output)
    encoded = base64.b64encode(output.getvalue()).decode()
    css = '@font-face{font-family:"Content Sans";font-style:normal;font-weight:100 900;font-display:swap;src:url(data:font/woff2;base64,' + encoded + ') format("woff2");}'
    license_text = (FONT_DIR / 'OFL.txt').read_text(encoding='utf-8')
    return css, '<template id="font-license">' + escape(license_text) + '</template>'


@lru_cache(maxsize=1)
def math_assets():
    css = (KATEX_DIR / 'katex.min.css').read_text(encoding='utf-8')

    def inline_font(match):
        path = KATEX_DIR / match.group(1).strip('"\'')
        mime = {'.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf'}[path.suffix]
        return f'url(data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()})'

    css = re.sub(r'url\(([^)]+)\)', inline_font, css)
    scripts = []
    for path in (KATEX_DIR / 'katex.min.js', KATEX_DIR / 'contrib/auto-render.min.js'):
        scripts.append('<script>' + path.read_text(encoding='utf-8').replace('</script', '<\\/script') + '</script>')
    initialization = r'''<script>document.addEventListener('DOMContentLoaded', () => {
      renderMathInElement(document.getElementById('content'), {delimiters: [
        {left:'$$',right:'$$',display:true}, {left:'\\[',right:'\\]',display:true},
        {left:'\\(',right:'\\)',display:false}], throwOnError:false});
    });</script>'''
    return '<style>' + css + '</style>' + ''.join(scripts) + initialization


def inline_images(body, source):
    def replace(match):
        value = unescape(match.group(2))
        if value.startswith('data:'):
            return match.group(0)
        if re.match(r'^[a-zA-Z][\w+.-]*:', value) or value.startswith('//'):
            raise ValueError('单文件 HTML 的图片需使用本地文件或 data URI，不能依赖联网')
        path = (source.parent / value).resolve()
        mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        data = base64.b64encode(path.read_bytes()).decode()
        return match.group(1) + f'data:{mime};base64,{data}' + match.group(3)
    return re.sub(r'(<img\b[^>]*\bsrc=["\'])(.*?)(["\'])', replace, body, flags=re.I)


def split_slides(text):
    """仅将代码围栏外的独立 --- 作为页界；公式保持完整。"""
    pages, lines, fence, display = [], [], None, None
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        if fence is None:
            for left, right in (('$$', '$$'), (r'\[', r'\]')):
                if display == left and right in line:
                    display = None
                elif display is None and left in line:
                    tail = line.split(left, 1)[1]
                    if right not in tail:
                        display = left
        if fence is None and display is None and line.strip() == '---':
            if ''.join(lines).strip():
                pages.append(''.join(lines).strip())
            lines = []
        else:
            lines.append(line)
    if ''.join(lines).strip():
        pages.append(''.join(lines).strip())
    return pages


def build_content(source, *, scene='learning', output, title=None, theme='light'):
    if scene not in LABELS:
        raise ValueError('小红书继续使用 rednote_render.py；此构建器用于 learning、blog、report')
    if theme not in ('light', 'dark', 'system'):
        raise ValueError('主题必须为 light、dark 或 system')
    source = Path(source).resolve()
    is_html = source.suffix.lower() in ('.html', '.htm')
    parsed = {'metadata': {}, 'body': source.read_text(encoding='utf-8')} if is_html else parse_markdown_file(str(source))
    metadata, text = parsed['metadata'], parsed['body']
    heading = re.search(r'^#\s+(.+)$', text, re.M)
    title = title or str(metadata.get('title') or (heading.group(1) if heading else source.stem))
    convert = lambda body: body if is_html else convert_markdown_to_html(body, 'katex')
    if scene == 'report':
        pages = [text] if is_html else split_slides(text)
        if is_html and 'data-export-page' in text:
            body = text
        else:
            slides = []
            for index, page in enumerate(pages, 1):
                note = re.search(r'<!--\s*notes:\s*(.*?)-->', page, re.S | re.I)
                page = re.sub(r'<!--\s*notes:.*?-->', '', page, flags=re.S | re.I)
                slides.append(f'<section class="slide" data-export-page data-notes="{escape(note.group(1).strip() if note else "", quote=True)}" id="slide-{index}">'
                              f'<p class="eyebrow">{escape(title)}</p><div class="slide-body">{convert(page)}</div>'
                              f'<footer class="slide-footer"><span>{escape(title)}</span><span>{index:02d} / {len(pages):02d}</span></footer></section>')
            body = ''.join(slides)
    else:
        body = convert(text)
        body = re.sub(r'^\s*<h1[^>]*>.*?</h1>\s*', '', body, count=1, flags=re.S)
        body = group_figure_captions(enhance_code_blocks(body))
    body = inline_images(body, source)
    description = str(metadata.get('description', ''))
    meta = ' · '.join(str(metadata[key]) for key in ('author', 'date') if metadata.get(key))
    template = (TEMPLATES / ('report.html' if scene == 'report' else 'document.html')).read_text(encoding='utf-8')
    font_css, font_license = font_assets(unescape(body) + title + description + meta + '学习笔记技术博客技术汇报目录本文目录备注汇报目录讲者备注本页未附讲者备注。回到开头浅色深色上一页下一页翻页切换到主题跳到正文查看大图适合窗口放大关闭正文字号减小增大点击复制代码已复制复制失败请手动选择复制章节链接展开全部收起行上次读到继续阅读忽略补充说明向左右滚动查看完整表格前面的列→←↑−#')
    values = {
        'TITLE': escape(title), 'DESCRIPTION': f'<p class="description">{escape(description)}</p>' if description else '',
        'META': escape(meta), 'LABEL': LABELS[scene], 'SCENE': scene, 'THEME': theme,
        'DOCUMENTID': hashlib.sha256(str(metadata.get('document_id', scene + ':' + title)).encode()).hexdigest()[:20],
        'CSS': (TEMPLATES / 'content.css').read_text(encoding='utf-8'),
        'JS': (TEMPLATES / 'content.js').read_text(encoding='utf-8') + ('\n' + (TEMPLATES / 'reading.js').read_text(encoding='utf-8') if scene != 'report' else ''),
        'MATH': math_assets(), 'BODY': body,
        'FONT': font_css, 'FONTLICENSE': font_license,
    }
    html = re.sub(r'@@([A-Z]+)@@', lambda match: values[match.group(1)], template)
    destination = Path(output).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding='utf-8')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='已整理好的 Markdown 或可信 HTML 正文片段')
    parser.add_argument('--scene', choices=LABELS, default='learning')
    parser.add_argument('--output', '-o', required=True)
    parser.add_argument('--title')
    parser.add_argument('--theme', choices=('light', 'dark', 'system'), default='light')
    args = parser.parse_args()
    try:
        print(build_content(args.source, scene=args.scene, output=args.output, title=args.title, theme=args.theme))
    except (OSError, ValueError) as error:
        parser.exit(2, f'构建失败：{error}\n')


if __name__ == '__main__':
    main()
