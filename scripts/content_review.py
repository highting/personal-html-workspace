"""记录内容审读并绑定最终 HTML；只核验记录与版本，不自动判断内容质量。"""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path


REVIEW_FIELDS = ('scope', 'content_review', 'reader_review', 'visual_review')


def review_template():
    return {**{field: '' for field in REVIEW_FIELDS}, 'warning_decisions': {}}


def validate_evidence(evidence, warnings):
    if not isinstance(evidence, dict):
        raise ValueError('内容审读必须是 JSON 对象')
    for field in REVIEW_FIELDS:
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            raise ValueError(f'内容审读缺少实际依据：{field}')
    decisions = evidence.get('warning_decisions')
    if not isinstance(decisions, dict) or set(decisions) != set(warnings):
        raise ValueError('需要逐项处理当前 QA 的文案警告，不能遗漏或沿用旧警告记录')
    if any(not isinstance(reason, str) or not reason.strip() for reason in decisions.values()):
        raise ValueError('保留可疑文案必须说明具体理由')


def validate_content_review(run, manifest, qa):
    path = Path(run) / 'content-review.json'
    if not path.is_file():
        raise ValueError('缺少最终内容审读记录，请完成审读后运行 content_review.py')
    review = json.loads(path.read_text(encoding='utf-8'))
    if review.get('schema_version') != 1 or review.get('scene') != manifest['scene']:
        raise ValueError('内容审读记录版本或场景不匹配')
    if (review.get('html_sha256') != qa['html_sha256']
            or review.get('source_sha256') != manifest['source_sha256']):
        raise ValueError('内容审读记录已过期，需要审读当前成品后重新记录')
    validate_evidence(review.get('evidence'), qa.get('warnings', []))
    return review


def record_content_review(run_dir, evidence):
    run = Path(run_dir).resolve()
    manifest = json.loads((run / 'run.json').read_text(encoding='utf-8'))
    if manifest['scene'] not in ('learning', 'blog', 'report'):
        raise ValueError('本审读记录用于 learning、blog、report；小红书沿用原验收流程')
    artifacts = run / 'delivery'
    qa = json.loads((artifacts / 'qa.json').read_text(encoding='utf-8'))
    if not qa['passed'] or qa['scene'] != manifest['scene']:
        raise ValueError('先完成当前场景的页面检查，再记录最终审读')
    html_hash = hashlib.sha256((artifacts / 'index.html').read_bytes()).hexdigest()
    if html_hash != qa['html_sha256']:
        raise ValueError('HTML 已改变，需要重新检查并审读')
    validate_evidence(evidence, qa.get('warnings', []))
    review = {
        'schema_version': 1, 'scene': manifest['scene'],
        'html_sha256': html_hash, 'source_sha256': manifest['source_sha256'],
        'reviewed_at': datetime.now().astimezone().isoformat(), 'evidence': evidence,
    }
    path = run / 'content-review.json'
    path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir')
    parser.add_argument('--review', required=True, help='已完成内容、读者和呈现审读的 JSON 文件')
    args = parser.parse_args()
    try:
        evidence = json.loads(Path(args.review).read_text(encoding='utf-8'))
        print(record_content_review(args.run_dir, evidence))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'审读记录失败：{error}\n')


if __name__ == '__main__':
    main()
