import tempfile
import shutil
import struct
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from playwright.async_api import async_playwright
import scripts.rednote_render as renderer

from scripts.rednote_render import (
    _collapse_display_math_lines,
    _is_atomic_block,
    _normalize_render_options,
    _split_body_to_paragraphs,
    _split_body_to_sentences,
    convert_markdown_to_html,
    generate_cover_html,
    generate_card_html,
    parse_markdown_file,
    render_html_to_png,
    render_markdown_to_cards,
)


class RendererUnitTests(unittest.TestCase):
    def test_trailing_tags_are_extracted_without_truncating_body(self):
        body = '# 中间标题\n\n正文 #not-a-tag\n\n#Python #机器学习'
        html = convert_markdown_to_html(body)

        self.assertIn('中间标题', html)
        self.assertIn('正文', html)
        self.assertIn('class="tags-container"', html)
        self.assertIn('#Python', html)

    def test_markdown_heading_is_not_a_tag(self):
        html = convert_markdown_to_html('# Introduction')

        self.assertIn('<h1>Introduction</h1>', html)
        self.assertNotIn('tags-container', html)

    def test_tag_text_is_escaped(self):
        html = convert_markdown_to_html('正文\n\n#tag_1')
        self.assertIn('#tag_1', html)

    def test_cover_metadata_is_escaped(self):
        html = generate_cover_html(
            {'title': '<不应成为标签>', 'subtitle': 'A & B'},
            'academic', 1600, 900,
        )
        self.assertIn('&lt;不应成为标签&gt;', html)
        self.assertIn('A &amp; B', html)
        self.assertNotIn('<不应成为标签>', html)
        self.assertIn('<div class="cover-emoji"></div>', html)

    def test_front_matter_must_be_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.md'
            path.write_text('---\n- item\n---\n\n正文', encoding='utf-8')
            with self.assertRaises(ValueError):
                parse_markdown_file(str(path))

    def test_empty_front_matter_values_are_not_mappings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.md'
            for value in ('[]', 'false', '0', '""'):
                with self.subTest(value=value):
                    path.write_text(f'---\n{value}\n---\n正文', encoding='utf-8')
                    with self.assertRaises(ValueError):
                        parse_markdown_file(str(path))

    def test_yaml_off_disables_math(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'off.md'
            path.write_text('---\nmath: off\n---\n正文', encoding='utf-8')
            metadata = parse_markdown_file(str(path))['metadata']
            self.assertEqual(_normalize_render_options(metadata)['math_mode'], 'off')

    def test_atomic_blocks_keep_internal_blank_lines(self):
        body = '前文\n\n```python\nline_1\n\nline_2\n```\n\n后文'
        paragraphs = _split_body_to_paragraphs(body)

        self.assertEqual(len(paragraphs), 3)
        self.assertTrue(_is_atomic_block(paragraphs[1]))
        self.assertIn('line_1\n\nline_2', paragraphs[1])

    def test_long_english_paragraph_splits_at_word_boundaries(self):
        source = ' '.join(['technicalword'] * 100)
        sentences = _split_body_to_sentences(source)

        self.assertGreater(len(sentences), 1)
        self.assertTrue(all(len(sentence) <= 240 for sentence in sentences))

    def test_sentence_split_rejoins_chinese_and_english_without_loss(self):
        for source in ('第一句。第二句！第三句？', 'First sentence. Next sentence!',
                       'alpha  beta\nthird line', 'word ' * 150):
            with self.subTest(source=source[:40]):
                parts = _split_body_to_sentences(source)
                self.assertEqual(renderer._join_sentences(parts), source)
                self.assertGreater(len(parts), 1)

    def test_tilde_fences_and_display_formulas_keep_blank_lines(self):
        for block in ('~~~python\n<div>\n\nx = 1\n~~~', '$$\na+b\n\n+c\n$$'):
            with self.subTest(block=block):
                self.assertEqual(_split_body_to_paragraphs('before\n\n' + block + '\n\nafter'),
                                 ['before', block, 'after'])
                self.assertTrue(_is_atomic_block(block))

    def test_math_mode_does_not_change_code_examples(self):
        source = '```tex\n\\[\nx_1 < x_2\n\\]\n```\n\n' + '`\\(x\\)`'
        self.assertEqual(convert_markdown_to_html(source, 'katex'),
                         convert_markdown_to_html(source, 'off'))

    def test_svg_block_is_atomic(self):
        body = '说明\n\n<svg viewBox="0 0 10 10">\n\n<circle />\n\n</svg>\n\n结论'
        paragraphs = _split_body_to_paragraphs(body)

        self.assertEqual(len(paragraphs), 3)
        self.assertTrue(_is_atomic_block(paragraphs[1]))

    def test_figure_panel_keeps_nested_svg_together(self):
        body = '说明\n\n<div class="figure-panel">\n\n<svg>\n\n<circle />\n\n</svg>\n\n</div>\n\n结论'
        paragraphs = _split_body_to_paragraphs(body)

        self.assertEqual(len(paragraphs), 3)
        self.assertTrue(_is_atomic_block(paragraphs[1]))

    def test_render_options_and_katex_assets(self):
        self.assertEqual(
            _normalize_render_options({'math': 'katex'})['math_mode'], 'katex'
        )
        with self.assertRaises(ValueError):
            _normalize_render_options({'math': 'mathjax'})

        html = generate_card_html('公式：\\(x^2\\)', 'academic', 1, 1,
                                  1600, 900, 'katex')
        self.assertIn("'MiSans'", html)
        self.assertIn('katex.min.css', html)
        self.assertIn('__REDNOTE_MATH_READY__', html)
        self.assertIn('file:///', html)
        self.assertNotIn('cdn.jsdelivr.net', html)

    def test_display_math_lines_are_collapsed_before_nl2br(self):
        source = '\\[\nR_t^2\n+ U^2\n\\]'
        self.assertEqual(
            _collapse_display_math_lines(source), '\\[R_t^2 + U^2\\]'
        )

        html = convert_markdown_to_html(source, 'katex')
        self.assertIn('\\[R_t^2 + U^2\\]', html)
        self.assertNotIn('<br', html)

    def test_inline_math_delimiters_survive_markdown(self):
        html = convert_markdown_to_html(
            '稳态条件为 \\(R_{t+1}^2-R_t^2\\approx0\\)', 'katex'
        )

        self.assertIn('\\(R_{t+1}^2-R_t^2\\approx0\\)', html)


class RendererBrowserTests(unittest.IsolatedAsyncioTestCase):
    async def test_html_method_outputs_fixed_png_and_portable_sources(self):
        paragraphs = [f'段落{i}：' + '检查跨页顺序和内容完整性。' * 12 for i in range(8)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = root / 'source'
            source_dir.mkdir()
            (source_dir / '图 #1.svg').write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="60">'
                '<path d="M10 50 L90 10" stroke="#3B5BDB"/></svg>', encoding='utf-8')
            source = source_dir / 'content.md'
            source.write_text(
                '---\ntitle: 分页验证\nmath: katex\n---\n\n'
                + '\n\n'.join(paragraphs)
                + '\n\n' + r'$$\sqrt{\frac{\eta}{2\lambda}}$$'
                + '\n\n<img src="图%20%231.svg" alt="本地示意图">', encoding='utf-8')
            output = root / 'output'
            count = await render_markdown_to_cards(str(source), str(output), save_html=True)
            self.assertGreater(count, 1)
            pngs = list(output.glob('*.png'))
            self.assertEqual(len(pngs), count + 1)
            for png in pngs:
                self.assertEqual(struct.unpack('>II', png.read_bytes()[16:24]), (2160, 2880))
            moved = root / 'moved'
            shutil.move(str(output), str(moved))
            shutil.rmtree(source_dir)
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                try:
                    context = await browser.new_context(offline=True, viewport={'width': 1400, 'height': 900})
                    page = await context.new_page()
                    failures = []
                    page.on('requestfailed', lambda request: failures.append(request.url))
                    await page.goto((moved / 'html' / 'index.html').as_uri())
                    self.assertEqual(await page.locator('iframe').count(), count + 1)
                    text_parts = []
                    formulas = 0
                    for frame in page.frames[1:]:
                        await frame.evaluate('document.fonts.ready')
                        self.assertEqual(await frame.evaluate('document.body.scrollWidth'), 1080)
                        self.assertEqual(await frame.evaluate('document.body.scrollHeight'), 1440)
                        formulas += await frame.locator('.katex').count()
                        if await frame.locator('.card-content').count():
                            text_parts.append(await frame.locator('.card-content').inner_text())
                        for img in await frame.locator('img').all():
                            self.assertTrue(await img.evaluate('(el) => el.complete && el.naturalWidth > 0'))
                    joined = ''.join(text_parts).replace('\n', '')
                    position = -1
                    for paragraph in paragraphs:
                        found = joined.find(paragraph)
                        self.assertGreater(found, position)
                        position = found
                    self.assertEqual(formulas, 1)
                    self.assertEqual(failures, [])
                    for viewport_width in (700, 1800):
                        await page.set_viewport_size({'width': viewport_width, 'height': 900})
                        box = await page.locator('iframe').first.bounding_box()
                        self.assertEqual(box['width'], 1080)
                        self.assertGreaterEqual(box['x'], 0)
                finally:
                    await browser.close()

    async def test_png_rejects_oversized_block_instead_of_producing_long_image(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'oversized.md'
            source.write_text('<div style="height:2000px">保留全文</div>', encoding='utf-8')
            output = Path(directory) / 'output'
            with self.assertRaisesRegex(ValueError, '超出固定画幅'):
                await render_markdown_to_cards(str(source), str(output), save_html=True)
            self.assertEqual(list(output.glob('*.png')), [])
            self.assertFalse((output / 'html' / 'index.html').exists())

    async def test_math_renders_offline_with_visible_radical_and_no_false_overflow(self):
        source = r'行内 \(x_1\) 与根号：' + '\n\n' + r'$$\sqrt{\frac{\eta}{2\lambda}}$$'
        html = generate_card_html(source, 'academic', 1, 1, 1600, 900, 'katex')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'math.html'
            path.write_text(html, encoding='utf-8')
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                try:
                    context = await browser.new_context(offline=True)
                    page = await context.new_page()
                    requests = []
                    page.on('request', lambda request: requests.append(request.url))
                    await page.goto(path.as_uri())
                    await renderer._wait_for_renderers(page, 'katex')
                    self.assertEqual(await page.locator('.katex').count(), 2)
                    self.assertEqual(await page.locator('.katex-error').count(), 0)
                    radical = page.locator('.sqrt .hide-tail')
                    box = await radical.bounding_box()
                    self.assertGreater(box['height'], 10)
                    self.assertGreater(box['width'], 10)
                    margin = await radical.locator('svg').evaluate('(el) => getComputedStyle(el).marginTop')
                    self.assertEqual(margin, '0px')
                    self.assertFalse(any(url.startswith(('http:', 'https:')) for url in requests))
                finally:
                    await browser.close()
            await render_html_to_png(html, str(Path(directory) / 'math.png'),
                                     1600, 900, 1, 'katex')

    async def test_oversized_block_pagination_terminates_without_content_loss(self):
        block = '```python\n' + 'long_line\n' * 100 + '```'
        with patch.object(renderer, 'measure_card_height', new=AsyncMock(return_value=2000)):
            cards = await renderer.auto_split_body(block, 'sketch', 1080, 1440, 1)
        self.assertEqual(cards, [block])

    async def test_academic_is_a_standard_card_theme(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'academic.md'
            source.write_text('---\ntitle: 学术卡片\n---\n\n简短正文', encoding='utf-8')
            output = Path(directory) / 'output'
            count = await render_markdown_to_cards(str(source), str(output), 'academic', 800, 600, 1)
            self.assertEqual(count, 1)
            self.assertEqual({p.name for p in output.iterdir()}, {'cover.png', 'card_1.png'})

if __name__ == '__main__':
    unittest.main()
