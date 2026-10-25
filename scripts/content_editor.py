"""离线网页编辑入口，以及编辑稿与构建器共享的正文格式。"""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import webbrowser


ASSETS = Path(__file__).resolve().parent.parent / 'assets/content'


class AuthoringParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.in_data = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('id') == 'content-authoring-data':
            self.in_data = True

    def handle_data(self, data):
        if self.in_data:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_data = False


def read_authoring_data(html):
    parser = AuthoringParser()
    parser.feed(html)
    if not parser.parts:
        return None
    data = json.loads(''.join(parser.parts))
    if data.get('version') != 1 or not isinstance(data.get('body'), str):
        raise ValueError('不支持此编辑稿格式')
    return data


def authoring_json(data):
    # script 的 HTML 结束标签不能出现在 JSON 字符串中。
    return json.dumps(data, ensure_ascii=False, default=str).replace('<', '\\u003c')


def build_editor_launcher(output):
    template = (ASSETS / 'editor-launcher.html').read_text(encoding='utf-8')
    html = template.replace('@@EDITORCSS@@', (ASSETS / 'editor.css').read_text(encoding='utf-8'))
    html = html.replace('@@EDITORJS@@', (ASSETS / 'editor.js').read_text(encoding='utf-8'))
    target = Path(output).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(tempfile.gettempdir()) / 'html-craft-editor/index.html')
    parser.add_argument('--no-open', action='store_true')
    args = parser.parse_args()
    target = build_editor_launcher(args.output)
    print(target)
    if not args.no_open:
        webbrowser.open(target.as_uri())


if __name__ == '__main__':
    main()
