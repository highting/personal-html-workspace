import json
from pathlib import Path
import tempfile
import unittest

from scripts.prepare_blog import prepare_blog
from scripts.publish_blog import publish_blog
from scripts.rednote_artifacts import QA_VERSION, load_pages, sha256, source_files


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.blog = self.root / 'blogs' / '机器学习' / '中文 博客'
        self.blog.mkdir(parents=True)
        (self.blog / 'main.md').write_text('![图](images/图.svg)', encoding='utf-8')
        (self.blog / 'images').mkdir()
        (self.blog / 'images' / '图.svg').write_text('<svg/>', encoding='utf-8')

    def prepare(self, **kwargs):
        return prepare_blog(str(self.blog), project_root=self.root, **kwargs)

    def test_routes_copies_and_preserves_original(self):
        result = self.prepare()
        run = Path(result['run_dir'])
        self.assertEqual(run.parent, self.root / 'output/_work/中文 博客')
        self.assertEqual(Path(result['delivery_dir']), self.root / 'output/中文 博客')
        self.assertEqual(json.loads((run / 'run.json').read_text(encoding='utf-8')), result)
        work = Path(result['work_entry'])
        self.assertEqual((work.parent / 'images/图.svg').read_text(), '<svg/>')
        work.write_text('调整后的工作稿', encoding='utf-8')
        self.assertEqual((run / 'source/main.md').read_text(encoding='utf-8'), '![图](images/图.svg)')
        self.assertEqual((self.blog / 'main.md').read_text(encoding='utf-8'), '![图](images/图.svg)')
        self.assertEqual(list(Path(result['artifact_dir']).iterdir()), [])
        self.assertEqual(result['status'], 'prepared')
        self.assertEqual(result['mode'], 'html')
        self.assertEqual(Path(result['artifact_dir']).name, 'delivery')

    def test_new_runs_do_not_overwrite_previous_results(self):
        first = self.prepare(mode='images')
        image = Path(first['artifact_dir']) / '01-content.png'
        image.write_bytes(b'previous-result')
        second = self.prepare(mode='images')
        self.assertNotEqual(first['run_dir'], second['run_dir'])
        self.assertEqual(image.read_bytes(), b'previous-result')
        self.assertEqual(Path(second['artifact_dir']).name, 'delivery')

    def test_short_name_and_rejects_output_escape(self):
        result = self.prepare(output_name='Hyperball')
        self.assertEqual(Path(result['delivery_dir']), self.root / 'output/Hyperball')
        for name in ['../outside', '_work', 'nested/name']:
            with self.assertRaises(ValueError):
                self.prepare(output_name=name)

    def ready(self, result, images):
        artifact = Path(result['artifact_dir'])
        (artifact / '标题.txt').write_text('我用图理解一个问题', encoding='utf-8')
        (artifact / '配文.txt').write_text('我把这次阅读的思路画了下来。', encoding='utf-8')
        for number in images:
            (artifact / f'card_{number}.png').write_bytes(f'page-{number}'.encode())
            (artifact / 'html/pages').mkdir(parents=True, exist_ok=True)
            (artifact / f'html/pages/card_{number}.html').write_text('<html>card</html>', encoding='utf-8')
        qa = {'schema_version': QA_VERSION, 'scene': 'rednote', 'passed': True,
              'issues': [], 'source_files': source_files(artifact),
              'pages': [{**page, 'sha256': sha256(artifact / page['file'])} for page in load_pages(artifact)]}
        (artifact / 'qa-rednote.json').write_text(json.dumps(qa), encoding='utf-8')
        result['status'] = 'completed'
        (Path(result['run_dir']) / 'run.json').write_text(json.dumps(result), encoding='utf-8')

    def test_publish_keeps_materials_together_and_preserves_previous_delivery(self):
        first = self.prepare(output_name='Hyperball')
        self.ready(first, [1, 2])
        published = publish_blog(first['run_dir'], project_root=self.root)
        final = Path(published['delivery_dir'])
        self.assertTrue((final / '预览.html').is_file())
        self.assertEqual(Path(published['published_caption']).parent, final)
        self.assertEqual(Path(published['published_title']).parent, final)
        (final / '用户备注.txt').write_text('保留我', encoding='utf-8')
        second = self.prepare(output_name='Hyperball')
        self.ready(second, [1])
        publish_blog(second['run_dir'], project_root=self.root)
        self.assertTrue((final / 'card_1.png').is_file())
        self.assertFalse((final / 'card_2.png').exists())
        backups = list((Path(second['run_dir']) / 'previous-deliveries').iterdir())
        self.assertEqual((backups[0] / 'card_2.png').read_bytes(), b'page-2')
        self.assertEqual((backups[0] / '用户备注.txt').read_text(encoding='utf-8'), '保留我')

    def test_publish_rejects_incomplete_or_outside_destination(self):
        result = self.prepare()
        with self.assertRaisesRegex(ValueError, 'completed'):
            publish_blog(result['run_dir'], project_root=self.root)
        self.ready(result, [1])
        outside = self.root / 'outside'
        outside.mkdir()
        (outside / 'keep.txt').write_text('keep')
        result['delivery_dir'] = str(outside)
        (Path(result['run_dir']) / 'run.json').write_text(json.dumps(result), encoding='utf-8')
        with self.assertRaises(ValueError):
            publish_blog(result['run_dir'], project_root=self.root)
        self.assertEqual((outside / 'keep.txt').read_text(), 'keep')

    def test_ambiguous_manuscripts_require_entry_without_creating_output(self):
        (self.blog / 'main.md').rename(self.blog / '初稿.md')
        (self.blog / '修订稿.md').write_text('修订', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '无法确定唯一正文'):
            self.prepare()
        self.assertFalse((self.root / 'output').exists())
        result = self.prepare(entry='修订稿.md')
        self.assertEqual(result['entry'], '修订稿.md')

    def test_explicit_nested_document_keeps_relative_assets(self):
        (self.blog / '正文').mkdir()
        (self.blog / '正文/article.md').write_text('![图](../images/图.svg)', encoding='utf-8')
        result = self.prepare(entry='正文/article.md')
        self.assertTrue((Path(result['work_entry']).parent / '../images/图.svg').is_file())

    def test_rejects_outside_blog_and_entry(self):
        outside = self.root / 'outside.md'
        outside.write_text('outside', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.prepare(entry=str(outside))
        with self.assertRaises(ValueError):
            prepare_blog(str(self.root), project_root=self.root)
        with self.assertRaises(ValueError):
            prepare_blog('blogs/机器学习', project_root=self.root)
        self.assertFalse((self.root / 'output').exists())

    def test_unique_pdf_is_prepared_without_claiming_conversion(self):
        (self.blog / 'main.md').rename(self.blog / 'paper.pdf')
        result = self.prepare()
        self.assertEqual(result['entry'], 'paper.pdf')
        self.assertEqual(result['status'], 'prepared')
        self.assertFalse((Path(result['artifact_dir']) / 'index.html').exists())


if __name__ == '__main__':
    unittest.main()
