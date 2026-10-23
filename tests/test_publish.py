import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts.prepare_content import source_hash
from scripts.publish_blog import publish_blog
from scripts.publish_content import publish_content
from scripts.rednote_artifacts import QA_VERSION, load_pages, sha256, source_files
from scripts.content_review import record_content_review


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.sequence = 0

    def ready(self, scene):
        self.sequence += 1
        root = self.root / f'{scene}-{self.sequence}'
        run = root / 'output/_work/主题/run'
        artifacts = run / 'delivery'
        artifacts.mkdir(parents=True)
        source = run / 'source'
        source.mkdir()
        (source / 'main.md').write_text('# 原稿', encoding='utf-8')
        (artifacts / 'index.html').write_bytes(b'<html>new</html>')
        (artifacts / 'diagram.png').write_bytes(b'auxiliary')
        (artifacts / 'checks').mkdir()
        (artifacts / 'checks/page-99.png').write_bytes(b'check-only')
        images = []
        if scene == 'report':
            (artifacts / 'page-01.png').write_bytes(b'page-one')
            images = [{'file': 'page-01.png', 'sha256': hashlib.sha256(b'page-one').hexdigest()}]
        if scene in ('legacy', 'rednote'):
            (artifacts / '标题.txt').write_text('标题', encoding='utf-8')
            (artifacts / '配文.txt').write_text('配文', encoding='utf-8')
            (artifacts / 'card_1.png').write_bytes(b'card-one')
            (artifacts / 'html/pages').mkdir(parents=True)
            (artifacts / 'diagram.png').rename(artifacts / 'html/diagram.png')
            (artifacts / 'html/pages/card_1.html').write_text('<html>card one</html>', encoding='utf-8')
            rednote_qa = {'schema_version': QA_VERSION, 'scene': 'rednote', 'passed': True,
                          'issues': [], 'source_files': source_files(artifacts),
                          'pages': [{**page, 'sha256': sha256(artifacts / page['file'])}
                                    for page in load_pages(artifacts)]}
            (artifacts / 'qa-rednote.json').write_text(json.dumps(rednote_qa), encoding='utf-8')
        qa = {'passed': True, 'scene': scene, 'images': images, 'warnings': [],
              'html_sha256': hashlib.sha256((artifacts / 'index.html').read_bytes()).hexdigest()}
        (artifacts / 'qa.json').write_text(json.dumps(qa), encoding='utf-8')
        destination = root / 'output/主题'
        manifest = {'status': 'completed', 'scene': scene, 'source_dir': str(source),
                    'source_sha256': source_hash(source), 'artifact_dir': str(artifacts),
                    'delivery_dir': str(destination)}
        (run / 'run.json').write_text(json.dumps(manifest), encoding='utf-8')
        (run / 'delivery.md').write_text('已检查的制作记录\n', encoding='utf-8')
        if scene in ('learning', 'blog', 'report'):
            record_content_review(run, self.review_evidence())
        publisher = publish_blog if scene == 'legacy' else publish_content
        return root, run, artifacts, destination, publisher

    def review_evidence(self):
        return {
            'scope': '第一节覆盖问题与方法，第二节解释适用条件。',
            'content_review': '逐项核对第一节论断与材料，第二节保留比较条件。',
            'reader_review': '用第一节例子跟随关键步骤，图注说明对象对应关系。',
            'visual_review': '已查看全部明暗页与正文、图注、备注，重点和条件可辨。',
            'warning_decisions': {},
        }

    def snapshot(self, folder):
        return {p.relative_to(folder).as_posix(): p.read_bytes()
                for p in folder.rglob('*') if p.is_file()}

    def old_delivery(self, destination):
        (destination / 'nested').mkdir(parents=True)
        (destination / 'index.html').write_bytes(b'old-entry\x00\xff')
        (destination / 'nested/notes.txt').write_bytes(b'keep-old-notes')
        return self.snapshot(destination)

    def assert_no_staging(self, root, run):
        self.assertEqual({p.name for p in (root / 'output').iterdir()},
                         {'_work', '主题'} if (root / 'output/主题').exists() else {'_work'})
        expected = {'source', 'delivery', 'run.json', 'delivery.md'}
        if json.loads((run / 'run.json').read_text(encoding='utf-8'))['scene'] in ('learning', 'blog', 'report'):
            expected.add('content-review.json')
        self.assertEqual({p.name for p in run.iterdir()} - {'previous-deliveries'}, expected)

    def assert_no_backup(self, run):
        backups = run / 'previous-deliveries'
        self.assertEqual(list(backups.iterdir()) if backups.exists() else [], [])

    def test_copy_failure_preserves_entry_and_records(self):
        for scene in ('learning', 'legacy', 'rednote'):
            with self.subTest(scene=scene):
                root, run, artifacts, destination, publisher = self.ready(scene)
                old = self.old_delivery(destination)
                records = [(run / name).read_bytes() for name in ('run.json', 'delivery.md')]

                def fail_copy(src, dst, *args, **kwargs):
                    Path(dst).mkdir(parents=True, exist_ok=True)
                    shutil.copy2(Path(src) / 'index.html', Path(dst) / 'index.html')
                    raise OSError('injected partial copy failure')

                with patch('shutil.copytree', side_effect=fail_copy):
                    with self.assertRaisesRegex(OSError, 'injected partial copy'):
                        publisher(str(run), root)
                self.assertTrue(destination.is_dir())
                self.assertEqual(self.snapshot(destination), old)
                self.assertEqual([(run / name).read_bytes() for name in ('run.json', 'delivery.md')], records)
                self.assert_no_backup(run)
                self.assert_no_staging(root, run)

    def test_switch_failures_restore_entry_and_records(self):
        rename = Path.rename
        for scene in ('learning', 'legacy', 'rednote'):
            for phase in ('backup', 'install'):
                with self.subTest(scene=scene, phase=phase):
                    root, run, artifacts, destination, publisher = self.ready(scene)
                    old = self.old_delivery(destination)
                    records = [(run / name).read_bytes() for name in ('run.json', 'delivery.md')]

                    def fail_rename(path, target):
                        is_backup = path == destination
                        is_install = Path(target) == destination and path.parent.name != 'previous-deliveries'
                        if (phase == 'backup' and is_backup) or (phase == 'install' and is_install):
                            raise OSError('injected switch failure')
                        return rename(path, target)

                    with patch.object(Path, 'rename', fail_rename):
                        with self.assertRaisesRegex(OSError, 'injected switch'):
                            publisher(str(run), root)
                    self.assertEqual(self.snapshot(destination), old)
                    self.assertEqual([(run / name).read_bytes() for name in ('run.json', 'delivery.md')], records)
                    self.assert_no_backup(run)
                    self.assert_no_staging(root, run)

    def test_first_publication_failures_leave_no_entry_or_success_record(self):
        rename = Path.rename
        for scene in ('learning', 'legacy', 'rednote'):
            for phase in ('copy', 'install'):
                with self.subTest(scene=scene, phase=phase):
                    root, run, artifacts, destination, publisher = self.ready(scene)
                    records = [(run / name).read_bytes() for name in ('run.json', 'delivery.md')]

                    def fail_copy(src, dst, *args, **kwargs):
                        Path(dst).mkdir(parents=True, exist_ok=True)
                        (Path(dst) / 'partial.txt').write_bytes(b'partial')
                        raise OSError('injected first copy failure')

                    def fail_rename(path, target):
                        if Path(target) == destination:
                            raise OSError('injected first install failure')
                        return rename(path, target)

                    fault = patch('shutil.copytree', side_effect=fail_copy) if phase == 'copy' else patch.object(Path, 'rename', fail_rename)
                    with fault, self.assertRaisesRegex(OSError, 'injected first'):
                        publisher(str(run), root)
                    self.assertFalse(destination.exists())
                    self.assertEqual([(run / name).read_bytes() for name in ('run.json', 'delivery.md')], records)
                    self.assert_no_backup(run)
                    self.assert_no_staging(root, run)

    def test_success_keeps_old_version_and_all_auxiliary_files(self):
        for scene in ('learning', 'legacy', 'rednote', 'report'):
            with self.subTest(scene=scene):
                root, run, artifacts, destination, publisher = self.ready(scene)
                publisher(str(run), root)
                (destination / 'old-only.txt').write_bytes(b'old-extra')
                old = self.snapshot(destination)
                result = publisher(str(run), root)
                self.assertIn('published_at', result)
                self.assertEqual(self.snapshot(destination), self.snapshot(artifacts))
                backups = list((run / 'previous-deliveries').iterdir())
                self.assertEqual(len(backups), 1)
                self.assertEqual(self.snapshot(backups[0]), old)
                self.assert_no_staging(root, run)

    def test_report_rejects_extra_missing_and_changed_pages(self):
        for change in ('extra', 'missing', 'changed'):
            with self.subTest(change=change):
                root, run, artifacts, destination, publisher = self.ready('report')
                old = self.old_delivery(destination)
                records = [(run / name).read_bytes() for name in ('run.json', 'delivery.md')]
                if change == 'extra':
                    (artifacts / 'page-02.png').write_bytes(b'unchecked')
                elif change == 'missing':
                    (artifacts / 'page-01.png').unlink()
                else:
                    (artifacts / 'page-01.png').write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, '图片|页图'):
                    publisher(str(run), root)
                self.assertEqual(self.snapshot(destination), old)
                self.assertEqual([(run / name).read_bytes() for name in ('run.json', 'delivery.md')], records)
                self.assert_no_backup(run)
                self.assert_no_staging(root, run)

    def test_content_review_is_required_current_and_complete_before_publication(self):
        for scene in ('learning', 'blog', 'report'):
            for change in ('missing', 'schema', 'scene', 'source', 'html', 'scope',
                           'content_review', 'reader_review', 'visual_review', 'warning'):
                with self.subTest(scene=scene, change=change):
                    root, run, artifacts, destination, publisher = self.ready(scene)
                    old = self.old_delivery(destination)
                    review_path = run / 'content-review.json'
                    review = json.loads(review_path.read_text(encoding='utf-8'))
                    qa_path = artifacts / 'qa.json'
                    qa = json.loads(qa_path.read_text(encoding='utf-8'))
                    if change == 'missing':
                        review_path.unlink()
                    elif change == 'html':
                        # 即使重新通过页面 QA，旧内容审读也不能用于新 HTML。
                        (artifacts / 'index.html').write_text('<html>new claim</html>', encoding='utf-8')
                        qa['html_sha256'] = hashlib.sha256((artifacts / 'index.html').read_bytes()).hexdigest()
                    elif change == 'warning':
                        qa['warnings'] = ['核对成品文案: 待补充']
                    else:
                        if change in ('scope', 'content_review', 'reader_review', 'visual_review'):
                            review['evidence'][change] = ''
                        else:
                            key = {'schema': 'schema_version', 'scene': 'scene', 'source': 'source_sha256'}[change]
                            review[key] = 'outdated'
                        review_path.write_text(json.dumps(review), encoding='utf-8')
                    qa_path.write_text(json.dumps(qa), encoding='utf-8')
                    before = self.snapshot(run)
                    with self.assertRaisesRegex(ValueError, '审读|警告'):
                        publisher(str(run), root)
                    self.assertEqual(self.snapshot(destination), old)
                    self.assertEqual(self.snapshot(run), before)
                    self.assert_no_backup(run)

    def test_review_requires_reason_for_retained_warning_and_stays_out_of_delivery(self):
        root, run, artifacts, destination, publisher = self.ready('blog')
        qa_path = artifacts / 'qa.json'
        qa = json.loads(qa_path.read_text(encoding='utf-8'))
        warning = '核对成品文案: 本节对照两种排版示例'
        qa['warnings'] = [warning]
        qa_path.write_text(json.dumps(qa), encoding='utf-8')
        evidence = self.review_evidence()
        before = (run / 'content-review.json').read_bytes()
        for decisions in ({}, {warning: ''}, {warning: '正文讨论对象', '旧警告': '过期'}):
            evidence['warning_decisions'] = decisions
            with self.assertRaises(ValueError):
                record_content_review(run, evidence)
            self.assertEqual((run / 'content-review.json').read_bytes(), before)
        evidence['warning_decisions'] = {warning: '本文主题就是排版方法；这两份示例是论证对象，已核对没有占位内容。'}
        record_content_review(run, evidence)
        publisher(str(run), root)
        self.assertFalse((destination / 'content-review.json').exists())
        self.assertEqual((destination / 'index.html').read_bytes(), (artifacts / 'index.html').read_bytes())

    def test_review_cannot_stamp_unchecked_or_changed_html(self):
        for change in ('qa-failed', 'scene', 'html'):
            with self.subTest(change=change):
                _, run, artifacts, _, _ = self.ready('learning')
                before = (run / 'content-review.json').read_bytes()
                qa_path = artifacts / 'qa.json'
                qa = json.loads(qa_path.read_text(encoding='utf-8'))
                if change == 'qa-failed':
                    qa['passed'] = False
                elif change == 'scene':
                    qa['scene'] = 'report'
                else:
                    (artifacts / 'index.html').write_bytes(b'changed')
                qa_path.write_text(json.dumps(qa), encoding='utf-8')
                with self.assertRaises(ValueError):
                    record_content_review(run, self.review_evidence())
                self.assertEqual((run / 'content-review.json').read_bytes(), before)

    def test_rednote_rejects_missing_failed_and_stale_checks_without_touching_delivery(self):
        for scene in ('legacy', 'rednote'):
            for change in ('no-qa', 'failed', 'old-qa', 'changed', 'extra', 'stray', 'missing', 'source', 'resource', 'manifest'):
                with self.subTest(scene=scene, change=change):
                    root, run, artifacts, destination, publisher = self.ready(scene)
                    old = self.old_delivery(destination)
                    records = [(run / name).read_bytes() for name in ('run.json', 'delivery.md')]
                    qa_path = artifacts / 'qa-rednote.json'
                    if change == 'no-qa':
                        qa_path.unlink()
                    elif change in ('failed', 'old-qa'):
                        qa = json.loads(qa_path.read_text(encoding='utf-8'))
                        qa['passed' if change == 'failed' else 'schema_version'] = False
                        qa_path.write_text(json.dumps(qa), encoding='utf-8')
                    elif change == 'changed':
                        (artifacts / 'card_1.png').write_bytes(b'changed')
                    elif change == 'extra':
                        (artifacts / 'card_2.png').write_bytes(b'unchecked')
                    elif change == 'stray':
                        (artifacts / 'extra.png').write_bytes(b'unchecked')
                    elif change == 'missing':
                        (artifacts / 'card_1.png').unlink()
                    elif change == 'source':
                        (artifacts / 'html/pages/card_1.html').write_text('changed', encoding='utf-8')
                    elif change == 'resource':
                        (artifacts / 'html/style.css').write_text('changed', encoding='utf-8')
                    else:
                        (artifacts / 'rednote-pages.json').write_text(json.dumps({'pages': load_pages(artifacts)}), encoding='utf-8')
                    with self.assertRaises(ValueError):
                        publisher(str(run), root)
                    self.assertEqual(self.snapshot(destination), old)
                    self.assertEqual([(run / name).read_bytes() for name in ('run.json', 'delivery.md')], records)
                    self.assertFalse((artifacts / '预览.html').exists())
                    self.assert_no_backup(run)
                    self.assert_no_staging(root, run)


if __name__ == '__main__':
    unittest.main()
