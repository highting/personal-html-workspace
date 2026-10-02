"""长文的代码与图注标记；内容仍由 Markdown/可信 HTML 提供。"""

from html import escape, unescape
import hashlib
import re

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.util import ClassNotFound


def enhance_code_blocks(body):
    def render(match):
        attributes, encoded = match.groups()
        code = unescape(encoded)

        def attribute(name):
            found = re.search(r'\b' + name + r'=["\'](.*?)["\']', attributes)
            return unescape(found.group(1)) if found else ''

        language = re.search(r'(?:^|\s)language-([\w+-]+)', attribute('class'))
        language = language.group(1) if language else 'text'
        try:
            lexer = get_lexer_by_name(language, stripnl=False, ensurenl=False)
        except ClassNotFound:
            lexer = TextLexer(stripnl=False, ensurenl=False)
        highlighted = highlight(code, lexer, HtmlFormatter(nowrap=True))
        if not code.endswith('\n'):
            highlighted = highlighted.removesuffix('\n')
        marked = set()
        for group in attribute('data-highlight').replace(',', ' ').split():
            if not re.fullmatch(r'\d+(?:-\d+)?', group):
                raise ValueError('data-highlight 使用行号或范围，例如 2 4-6')
            bounds = [int(value) for value in group.split('-')]
            marked.update(range(bounds[0], bounds[-1] + 1))
        lines = highlighted.splitlines(keepends=True)
        rendered = []
        for number, line in enumerate(lines, 1):
            newline = '\n' if line.endswith('\n') else ''
            line = line.removesuffix('\n')
            css_class = 'code-line is-highlighted' if number in marked else 'code-line'
            rendered.append(f'<span class="{css_class}" data-line="{number}">{line}</span>{newline}')
        filename = attribute('title')
        label = f'<span class="code-filename">{escape(filename)}</span>' if filename else ''
        key = hashlib.sha256((language + '\0' + filename + '\0' + code).encode()).hexdigest()[:20]
        return (f'<div class="code-block" data-lines="{len(lines)}" data-code-key="{key}">'
                f'<div class="code-toolbar"><div><span class="code-language">{escape(language)}</span>{label}</div>'
                '<button type="button" class="code-copy" aria-label="复制代码">复制代码</button></div>'
                f'<pre tabindex="0"><code class="language-{escape(language)}">{"".join(rendered)}</code></pre></div>')

    return re.sub(r'<pre><code([^>]*)>(.*?)</code></pre>', render, body, flags=re.S)


def group_figure_captions(body):
    """只组合明确的独立图片与紧随其后的“图N”图注，不猜测普通段落。"""
    return re.sub(
        r'<p>(<img\b[^>]+/?>)</p>\s*<p><em>(图\s*\d+.*?)</em></p>',
        r'<figure class="media-plate">\1<figcaption>\2</figcaption></figure>', body, flags=re.S,
    )
