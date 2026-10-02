"""准备四场景的材料快照、工作副本与任务规则，不调用生成模型。"""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.prepare_blog import select_entry

ROOT = Path(__file__).resolve().parent.parent
SCENES = ('learning', 'blog', 'report', 'rednote')


def source_hash(folder):
    digest = hashlib.sha256()
    for path in sorted(Path(folder).rglob('*')):
        if path.is_file():
            name = path.relative_to(folder).as_posix().encode()
            digest.update(len(name).to_bytes(8, 'big'))
            digest.update(name)
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def prepare_content(input_path, scene, mode='html', entry=None, output_name=None, project_root=ROOT):
    root = Path(project_root).resolve()
    source = (root / input_path).resolve()
    bases = [root / 'inputs', root / 'blogs']
    base = next((base for base in bases if source.is_relative_to(base)), None)
    if not source.is_dir() or base is None or len(source.relative_to(base).parts) < 2:
        raise ValueError('输入必须是 inputs/ 或 blogs/ 下的 <分类>/<主题> 文件夹')
    if scene not in SCENES or mode not in ('html', 'images'):
        raise ValueError('场景或辅助图模式无效')
    selected = select_entry(source, entry).relative_to(source)
    name = output_name or source.name
    destination = (root / 'output' / name).resolve()
    if destination.parent != root / 'output' or name.startswith('_'):
        raise ValueError('--name 必须是 output/ 下非下划线开头的单层目录名')
    run = root / 'output/_work' / name / f'{datetime.now():%Y%m%d-%H%M%S-%f}-{scene}-{mode}'
    run.mkdir(parents=True)
    shutil.copytree(source, run / 'source')
    shutil.copytree(source, run / 'work')
    (run / 'delivery').mkdir()
    prompt = (root / 'prompts/common.txt').read_text(encoding='utf-8') + '\n\n' + (root / f'prompts/scenes/{scene}.txt').read_text(encoding='utf-8')
    prompt += f'\n\n主题：{source.name}\n场景：{scene}\n辅助图模式：{mode}\n工作稿：{run / "work" / selected}\n原始快照只读。先阅读真实材料，再完成对应场景成品。\n'
    (run / 'work/任务Prompt.txt').write_text(prompt, encoding='utf-8')
    manifest = {
        'scene': scene, 'mode': mode, 'status': 'prepared', 'input_dir': str(source), 'entry': selected.as_posix(),
        'created_at': datetime.now().astimezone().isoformat(), 'run_dir': str(run),
        'source_dir': str(run / 'source'), 'source_sha256': source_hash(run / 'source'),
        'work_dir': str(run / 'work'), 'work_entry': str(run / 'work' / selected),
        'artifact_dir': str(run / 'delivery'), 'delivery_dir': str(destination),
        'title_file': str(run / 'delivery/标题.txt'), 'caption_file': str(run / 'delivery/配文.txt'),
    }
    (run / 'run.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (run / 'delivery.md').write_text(f'# {source.name}\n\n状态：已准备，尚未制作。\n\n记录来源、内容主线、图解位置、实际检查与未验证事项。\n', encoding='utf-8')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_dir')
    parser.add_argument('--scene', choices=SCENES, required=True)
    parser.add_argument('--mode', choices=('html', 'images'), default='html')
    parser.add_argument('--entry')
    parser.add_argument('--name')
    args = parser.parse_args()
    try:
        print(json.dumps(prepare_content(args.input_dir, args.scene, args.mode, args.entry, args.name), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(2, f'准备失败：{error}\n')


if __name__ == '__main__':
    main()
