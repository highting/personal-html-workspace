import json
from pathlib import Path
import re
import tempfile
import unittest

from playwright.sync_api import sync_playwright
from scripts.build_content import build_content
from scripts.content_editor import authoring_json, build_editor_launcher, read_authoring_data


class ContentEditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        source = cls.root / 'main.md'
        fence = chr(96) * 3
        source.write_text(
            '---\ntitle: 编辑测试\nauthor: 测试作者\ndocument_id: editor-test\n---\n\n'
            '# 编辑测试\n\n## 第一节\n\n第一段普通文字。\n\n第二段有 **强调** 和 [链接](https://example.com)。\n\n'
            '含公式的段落：\\(x^2 + y^2\\)。\n\n' +
            fence + 'python\nprint("hello")\n' + fence + '\n\n'
            '<figure id="picture"><img src="picture.svg" alt="原图"><figcaption>原始图注。</figcaption></figure>\n\n'
            '<figure data-animation><svg viewBox="0 0 600 160" aria-label="两步图">'
            '<g data-step data-caption="起点"><text x="20" y="40">起点</text></g>'
            '<g data-step data-caption="终点"><text x="300" y="40">终点</text></g></svg></figure>\n\n'
            '## 第二节\n\n末段文字。\n', encoding='utf-8')
        (cls.root / 'picture.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="200">'
            '<rect width="600" height="200" fill="#EAE7DE"/></svg>', encoding='utf-8')
        cls.reading = build_content(source, output=cls.root / 'reading.html')
        report = cls.root / 'report.md'
        report.write_text('# 第一页\n\n第一页正文。\n\n---\n\n# 第二页\n\n第二页正文。\n\n'
                          '<!-- notes: 第二页讲者备注 -->', encoding='utf-8')
        cls.report = build_content(report, scene='report', output=cls.root / 'report.html')
        cls.launcher = build_editor_launcher(cls.root / 'editor.html')
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.temp.cleanup()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 1000}, offline=True)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def ready(self):
        self.page.locator('.content-editor').wait_for(state='visible')
        self.page.locator('.ce-loading').wait_for(state='hidden')
        frame = self.page.locator('.content-editor iframe').element_handle().content_frame()
        frame.wait_for_function('document.readyState === "complete"')
        return frame

    def open_editor(self, path=None):
        self.page.goto((path or self.reading).as_uri())
        self.page.locator('#edit-page').click()
        return self.ready()

    def click_action(self, name):
        self.page.locator('[data-action="' + name + '"]').click()
        return self.ready()

    def edit_text(self, frame, selector, text):
        frame.locator(selector).dblclick()
        frame.locator(selector).fill(text)
        frame.locator(selector).press('Enter')
        return self.ready()

    def save(self, name):
        with self.page.expect_download() as download:
            self.page.locator('[data-action="save"]').click()
        target = self.root / name
        download.value.save_as(target)
        return target

    def test_text_style_save_reopen_and_rebuild_preserve_source(self):
        frame = self.open_editor()
        frame = self.edit_text(frame, '.article-header h1', '改过的标题')
        frame = self.edit_text(frame, '.prose > p:nth-of-type(1)', '修改正文，保留 <尖括号> 与 & 符号。')
        frame.locator('.prose > p:nth-of-type(1)').click()
        field = self.page.locator('[data-style="font-size"]')
        field.fill('24')
        field.press('Tab')
        frame = self.ready()
        self.assertEqual(frame.locator('.prose > p:nth-of-type(1)').evaluate('n => getComputedStyle(n).fontSize'), '24px')
        target = self.save('edited-reading.html')
        data = read_authoring_data(target.read_text(encoding='utf-8'))
        self.assertEqual(data['metadata']['title'], '改过的标题')
        self.assertIn('&lt;尖括号&gt;', data['body'])
        self.assertNotIn('data-editor-key', data['body'])
        self.assertNotIn('heading-anchor', data['body'])
        self.assertNotIn('code-actions', data['body'])
        self.assertNotIn('katex-html', data['body'])
        self.assertIn('\\(x^2 + y^2\\)', data['body'])
        self.page.goto(target.as_uri())
        self.page.wait_for_function('window.contentReadingReady')
        self.assertEqual(self.page.title(), '改过的标题')
        self.assertEqual(self.page.locator('.code-actions').count(), 1)
        self.assertEqual(self.page.locator('.animation-controls').count(), 1)
        self.assertEqual(self.page.locator('.katex').count(), 1)
        self.assertIn('第一节', self.page.locator('#toc-links').inner_text())
        rebuilt = build_content(target, output=self.root / 'rebuilt.html')
        self.page.goto(rebuilt.as_uri())
        self.page.wait_for_function('window.contentReadingReady')
        self.assertEqual(self.page.locator('.prose').count(), 1)
        self.assertEqual(self.page.locator('.article-header h1').inner_text(), '改过的标题')
        self.assertEqual(self.page.locator('.prose > p:nth-of-type(1)').evaluate('n => getComputedStyle(n).fontSize'), '24px')
        self.assertEqual(self.page.locator('.code-actions').count(), 1)
        self.page.locator('#edit-page').click()
        frame = self.ready()
        frame = self.edit_text(frame, '.prose > p:nth-of-type(1)', '再次编辑。')
        self.assertEqual(frame.locator('.prose > p:nth-of-type(1)').inner_text(), '再次编辑。')
        self.save('edited-twice.html')

    def test_move_delete_undo_redo_and_protected_math(self):
        frame = self.open_editor()
        paragraph = '.prose > p:nth-of-type(1)'
        frame.locator(paragraph).click()
        frame = self.click_action('down')
        self.assertTrue(frame.locator('.prose > p:nth-of-type(1)').inner_text().startswith('第二段'))
        frame = self.click_action('delete')
        self.assertNotIn('第一段普通文字', frame.locator('.prose').inner_text())
        frame = self.click_action('undo')
        self.assertIn('第一段普通文字', frame.locator('.prose').inner_text())
        frame = self.click_action('undo')
        self.assertTrue(frame.locator(paragraph).inner_text().startswith('第一段'))
        frame = self.click_action('redo')
        self.assertTrue(frame.locator(paragraph).inner_text().startswith('第二段'))
        frame.locator('.prose > p', has_text='含公式').click()
        self.assertTrue(self.page.locator('[data-action="text"]').is_disabled())
        frame.locator('.prose > p', has_text='含公式').dblclick()
        self.assertEqual(frame.locator('[contenteditable]').count(), 0)
        self.assertEqual(frame.locator('.katex').count(), 1)
        self.save('moved.html')

    def test_replace_image_is_embedded_and_undoable(self):
        frame = self.open_editor()
        frame.locator('#picture img').click()
        self.assertFalse(frame.locator('.image-viewer').is_visible())
        before = frame.locator('#picture img').get_attribute('src')
        replacement = self.root / 'replacement.svg'
        replacement.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">'
                               '<circle cx="150" cy="150" r="140" fill="#3B5BDB"/></svg>', encoding='utf-8')
        self.page.locator('#editor-image-file').set_input_files(replacement)
        self.page.wait_for_function('document.querySelector(".ce-state").textContent.includes("未保存")')
        frame = self.ready()
        after = frame.locator('#picture img').get_attribute('src')
        self.assertNotEqual(after, before)
        self.assertTrue(after.startswith('data:image/svg+xml;base64,'))
        frame = self.click_action('undo')
        self.assertEqual(frame.locator('#picture img').get_attribute('src'), before)
        frame = self.click_action('redo')
        self.assertEqual(frame.locator('#picture img').get_attribute('src'), after)
        target = self.save('image-edited.html')
        self.page.goto(target.as_uri())
        self.page.wait_for_function('window.contentReadingReady')
        self.assertEqual(self.page.locator('#picture img').get_attribute('src'), after)

    def test_report_edit_keeps_current_slide_and_keyboard(self):
        frame = self.open_editor(self.report)
        frame.locator('#next-slide').click()
        frame = self.edit_text(frame, '.slide:not([hidden]) h1', '更改第二页')
        self.assertEqual(frame.locator('.slide:not([hidden]) h1').inner_text(), '更改第二页')
        frame.locator('.slide:not([hidden]) p').dblclick()
        frame.locator('[contenteditable]').press('Home')
        frame.locator('[contenteditable]').press('ArrowRight')
        self.assertEqual(frame.locator('.slide:not([hidden]) h1').inner_text(), '更改第二页')
        frame.locator('[contenteditable]').fill('编辑后的第二页正文。')
        frame.locator('[contenteditable]').press('Enter')
        self.ready()
        target = self.save('report-edited.html')
        rebuilt = build_content(target, scene='report', output=self.root / 'report-rebuilt.html')
        self.page.goto(rebuilt.as_uri())
        self.page.locator('#next-slide').click()
        self.assertEqual(self.page.locator('.slide:not([hidden]) h1').inner_text(), '更改第二页')
        self.assertEqual(self.page.locator('.slide').count(), 2)
        self.page.locator('#notes-toggle').click()
        self.assertEqual(self.page.locator('#notes-content').inner_text(), '第二页讲者备注')
        with self.assertRaisesRegex(ValueError, '场景'):
            build_content(target, scene='learning', output=self.root / 'wrong-scene.html')

    def test_launcher_upgrades_legacy_copy_without_touching_input(self):
        raw = self.reading.read_text(encoding='utf-8')
        for name, tag in [('content-editor-style', 'style'), ('content-editor-runtime', 'script'),
                          ('content-authoring-data', 'script'), ('edit-page', 'button')]:
            raw = re.sub(r'<' + tag + r'\b[^>]*\bid="' + name + r'"[^>]*>.*?</' + tag + '>', '', raw, flags=re.S)
        legacy = self.root / 'legacy.html'
        legacy.write_text(raw, encoding='utf-8')
        before = legacy.read_bytes()
        self.page.goto(self.launcher.as_uri())
        self.page.locator('#open-edit-document').set_input_files(legacy)
        frame = self.ready()
        frame = self.edit_text(frame, '.article-header h1', '旧网页的编辑副本')
        target = self.save('legacy-edited.html')
        self.assertEqual(legacy.read_bytes(), before)
        self.page.goto(target.as_uri())
        self.page.wait_for_function('window.contentReadingReady')
        self.assertEqual(self.page.locator('#edit-page').count(), 1)
        self.assertEqual(self.page.locator('.article-header h1').inner_text(), '旧网页的编辑副本')
        self.assertEqual(self.page.locator('.code-actions').count(), 1)
        self.assertEqual(self.page.locator('.katex').count(), 1)
        self.page.locator('#edit-page').click()
        frame = self.ready()
        self.assertEqual(frame.locator('.code-actions').count(), 1)

    def test_payload_escapes_script_end_and_round_trips(self):
        data = {'version': 1, 'scene': 'learning', 'body': '<p>甲</p><script>var x=1;</script>'}
        encoded = authoring_json(data)
        self.assertNotIn('</script', encoded)
        self.assertEqual(json.loads(encoded), data)
        html = '<script id="content-authoring-data" type="application/json">' + encoded + '</script>'
        self.assertEqual(read_authoring_data(html), data)

    def test_save_commits_focused_text_and_preview_keeps_reading_controls(self):
        frame = self.open_editor()
        frame.locator('.article-header h1').dblclick()
        frame.locator('.article-header h1').fill('输入后直接保存')
        target = self.save('focused-edit.html')
        data = read_authoring_data(target.read_text(encoding='utf-8'))
        self.assertEqual(data['metadata']['title'], '输入后直接保存')
        frame = self.ready()
        frame = self.click_action('preview')
        self.assertFalse(self.page.locator('.ce-inspector').is_visible())
        frame.locator('#picture img').click()
        self.assertTrue(frame.locator('.image-viewer').is_visible())
        frame.locator('.image-viewer').press('Escape')
        frame = self.click_action('preview')
        self.assertTrue(self.page.locator('.ce-inspector').is_visible())

    def test_launcher_preserves_postbuild_edits_and_image_width(self):
        html = self.reading.read_text(encoding='utf-8')
        # 只改可见正文，故意保留旧 authoring payload，模拟其他制作工具的后处理。
        html = html.replace('<p>第一段普通文字。</p>', '<p>其他工具已修订的正文。</p>', 1)
        target = self.root / 'postprocessed.html'
        target.write_text(html, encoding='utf-8')
        self.page.goto(self.launcher.as_uri())
        self.page.locator('#open-edit-document').set_input_files(target)
        frame = self.ready()
        self.assertEqual(frame.locator('.prose > p:nth-of-type(1)').inner_text(), '其他工具已修订的正文。')
        frame.locator('#picture img').click()
        before = frame.locator('#picture').bounding_box()['width']
        width = self.page.locator('[data-style="width"]')
        width.fill('50')
        width.press('Tab')
        frame = self.ready()
        self.assertAlmostEqual(frame.locator('#picture').bounding_box()['width'], before / 2, delta=2)
        saved = self.save('postprocessed-edited.html')
        data = read_authoring_data(saved.read_text(encoding='utf-8'))
        self.assertIn('其他工具已修订的正文', data['body'])
        self.assertIn('width: 50%', data['body'])

    def test_editor_keeps_current_palette_across_edits_and_preview(self):
        self.page.goto(self.reading.as_uri())
        self.page.evaluate('setContentPalette("ink")')
        self.page.locator('#edit-page').click()
        frame = self.ready()
        self.assertEqual(frame.locator('html').get_attribute('data-palette'), 'ink')
        self.assertEqual(self.page.locator('.content-editor').get_attribute('data-editor-theme'), 'dark')
        frame = self.edit_text(frame, '.article-header h1', '深色下编辑')
        self.assertEqual(frame.locator('html').get_attribute('data-palette'), 'ink')
        frame = self.click_action('preview')
        frame.locator('#palette-select').select_option('paper')
        self.assertEqual(self.page.locator('.content-editor').get_attribute('data-editor-theme'), 'light')
        self.save('palette-edited.html')

    def test_yaml_date_survives_authoring_payload_and_rebuild(self):
        source = self.root / 'dated.md'
        source.write_text('---\ntitle: 日期元数据\ndate: 2026-10-25\n---\n\n正文。', encoding='utf-8')
        target = build_content(source, output=self.root / 'dated.html')
        data = read_authoring_data(target.read_text(encoding='utf-8'))
        self.assertEqual(data['metadata']['date'], '2026-10-25')
        rebuilt = build_content(target, output=self.root / 'dated-rebuilt.html')
        self.page.goto(rebuilt.as_uri())
        self.assertEqual(self.page.locator('.article-meta').inner_text(), '2026-10-25')


if __name__ == '__main__':
    unittest.main()
