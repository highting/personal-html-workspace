"""汇总四场景成品到短路径，保留历史版本；小红书复用原交付流程。"""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.prepare_content import ROOT, SCENES, source_hash
from scripts.publish_blog import publish_blog
from scripts.publish_utils import replace_delivery


def publish_content(run_dir, project_root=ROOT):
    output = Path(project_root).resolve() / 'output'
    run = Path(run_dir).resolve()
    if not run.is_relative_to(output / '_work'):
        raise ValueError('工作目录必须位于本项目 output/_work/ 内')
    manifest_path = run / 'run.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest['status'] != 'completed' or manifest['scene'] not in SCENES:
        raise ValueError('完成实际检查并标记 completed 后才能交付')
    source = Path(manifest['source_dir']).resolve()
    artifacts = Path(manifest['artifact_dir']).resolve()
    destination = Path(manifest['delivery_dir']).resolve()
    if source != run / 'source' or artifacts != run / 'delivery':
        raise ValueError('源快照与成品必须位于本次工作目录')
    if source_hash(source) != manifest['source_sha256']:
        raise ValueError('原始材料快照已被修改')
    if destination.parent != output or destination.name.startswith('_'):
        raise ValueError('交付目录必须是 output/ 下非下划线开头的单层目录')
    if manifest['scene'] == 'rednote':
        return publish_blog(str(run), project_root)
    qa = json.loads((artifacts / 'qa.json').read_text(encoding='utf-8'))
    if not qa['passed'] or qa['scene'] != manifest['scene']:
        raise ValueError('交付需要本场景通过的检查记录')
    if hashlib.sha256((artifacts / 'index.html').read_bytes()).hexdigest() != qa['html_sha256']:
        raise ValueError('HTML 已改变，需要重新检查')
    if manifest['scene'] == 'report':
        if not qa['images']:
            raise ValueError('汇报需要逐页 PNG')
        pages = {path.name for path in artifacts.iterdir()
                 if path.is_file() and re.fullmatch(r'page-\d+\.png', path.name)}
        if pages != {image['file'] for image in qa['images']}:
            raise ValueError('汇报页图与检查记录不一致，需要重新检查')
    for image in qa['images']:
        path = (artifacts / image['file']).resolve()
        if path.parent != artifacts or hashlib.sha256(path.read_bytes()).hexdigest() != image['sha256']:
            raise ValueError('交付图片与检查记录不一致')
    replace_delivery(artifacts, destination, run)
    manifest['published_at'] = datetime.now().astimezone().isoformat()
    manifest['published_html'] = str(destination / 'index.html')
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (run / 'delivery.md').open('a', encoding='utf-8') as record:
        record.write(f'\n成品目录：{destination}\n入口：index.html\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir')
    args = parser.parse_args()
    try:
        print(json.dumps(publish_content(args.run_dir), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'整理失败：{error}\n')


if __name__ == '__main__':
    main()
