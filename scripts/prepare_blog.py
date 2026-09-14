"""准备独立工作目录与简短交付路径，保留原稿副本；不执行生成。"""

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENT_SUFFIXES = {'.md', '.markdown', '.docx', '.pdf', '.html', '.htm'}


def select_entry(blog: Path, entry: str | None) -> Path:
    if entry:
        selected = (blog / entry).resolve()
        if not selected.is_relative_to(blog) or not selected.is_file():
            raise ValueError('--entry 必须指向博客文件夹内的实际文件')
        return selected
    for name in ('main.md', 'article.md', 'index.md'):
        if (blog / name).is_file():
            return blog / name
    candidates = sorted(
        path for path in blog.rglob('*')
        if path.is_file() and path.suffix.lower() in DOCUMENT_SUFFIXES
    )
    if len(candidates) != 1:
        names = ', '.join(str(path.relative_to(blog)) for path in candidates)
        raise ValueError(f'无法确定唯一正文，请使用 --entry 指定。候选：{names or "无"}')
    return candidates[0]


def prepare_blog(blog_path: str, mode: str = 'html', entry: str | None = None,
                 project_root: Path = PROJECT_ROOT, output_name: str | None = None) -> dict:
    root = project_root.resolve()
    blog = (root / blog_path).resolve()
    inputs = (root / 'blogs').resolve()
    if not blog.is_dir() or not blog.is_relative_to(inputs):
        raise ValueError('博客必须是 blogs/ 内的现有文件夹')
    relative = blog.relative_to(inputs)
    if len(relative.parts) < 2:
        raise ValueError('路径应为 blogs/<分类>/<博客名>，不能只选择分类目录')
    if mode not in ('html', 'images'):
        raise ValueError('模式必须为 html 或 images；两种模式均交付图片')
    selected = select_entry(blog, entry).relative_to(blog)
    name = output_name or relative.name
    delivery = (root / 'output' / name).resolve()
    if delivery.parent != root / 'output' or name.startswith('_'):
        raise ValueError('--name 必须是 output/ 下的单层目录名，且不能以下划线开头')
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    run = root / 'output' / '_work' / name / f'{stamp}-{mode}'
    run.mkdir(parents=True, exist_ok=False)
    manifest = {
        'blog': relative.as_posix(),
        'input_dir': str(blog),
        'entry': selected.as_posix(),
        'mode': mode,
        'created_at': datetime.now().astimezone().isoformat(),
        'status': 'preparing',
        'run_dir': str(run),
        'source_dir': str(run / 'source'),
        'work_dir': str(run / 'work'),
        'work_entry': str(run / 'work' / selected),
        'artifact_dir': str(run / 'delivery'),
        'delivery_dir': str(delivery),
        'title_file': str(run / 'delivery' / '标题.txt'),
        'caption_file': str(run / 'delivery' / '配文.txt'),
    }
    manifest_path = run / 'run.json'
    try:
        shutil.copytree(blog, run / 'source')
        shutil.copytree(run / 'source', run / 'work')
        (run / 'delivery').mkdir()
        (run / 'delivery.md').write_text(
            f'# {relative.name}\n\n状态：已准备，尚未生成。\n\n'
            '生成完成后记录交付入口、阅读顺序或插入位置、来源及实际检查结果。\n',
            encoding='utf-8',
        )
        manifest['status'] = 'prepared'
    except OSError as exc:
        manifest['status'] = 'failed'
        manifest['error'] = str(exc)
        raise
    finally:
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8',
        )
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('blog', help='blogs/<分类>/<博客名>，支持绝对路径')
    parser.add_argument('--mode', choices=('html', 'images'), default='html',
                        help='正文统一用 HTML；html：非正文视觉用 HTML＋SVG；images：非正文视觉用生图工具')
    parser.add_argument('--entry', help='正文路径，相对于博客文件夹')
    parser.add_argument('--name', help='简短交付目录名，如 Hyperball；默认使用博客文件夹名')
    args = parser.parse_args()
    try:
        result = prepare_blog(args.blog, args.mode, args.entry, output_name=args.name)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'准备失败：{exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
