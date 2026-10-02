"""显式下载固定版本的 Noto Sans SC 中文字体；缓存不纳入 Git。"""

import hashlib
import json
import os
from pathlib import Path
import tempfile
from urllib.request import Request, urlopen

FONT_DIR = Path(__file__).resolve().parent.parent / 'assets/vendor/noto-sans-sc'


def download_content_fonts():
    manifest = json.loads((FONT_DIR / 'font-manifest.json').read_text(encoding='utf-8'))
    destination = FONT_DIR / 'NotoSansSC-variable.ttf'
    if destination.is_file() and hashlib.sha256(destination.read_bytes()).hexdigest() == manifest['sha256']:
        return {'output': str(destination), 'cached': True}
    request = Request(manifest['url'], headers={'User-Agent': 'personal-html-workspace/font-cache'})
    with urlopen(request, timeout=60) as response:
        data = response.read()
    if len(data) != manifest['bytes'] or hashlib.sha256(data).hexdigest() != manifest['sha256']:
        raise ValueError('字体大小或 SHA-256 与固定版本不一致')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=FONT_DIR, suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return {'output': str(destination), 'cached': False}


if __name__ == '__main__':
    print(json.dumps(download_content_fonts(), ensure_ascii=False, indent=2))
