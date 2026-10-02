"""检查学习/博客/汇报 HTML 的明暗主题、离线资源与边界，并导出汇报 PNG。"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.visual_qa import inspect_palette, inspect_visuals


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inspect_page(page, scene):
    return page.evaluate('''scene => {
      const issues = [];
      if (document.querySelector('.katex-error')) issues.push('公式渲染错误');
      for (const image of document.images) if (!image.complete || !image.naturalWidth) issues.push('图片未加载');
      if (scene === 'report') {
        const slide = document.querySelector('[data-export-page]:not([hidden])');
        const body = slide?.querySelector('.slide-body');
        if (!body) return ['汇报页缺少 slide-body'];
        const bounds = body.getBoundingClientRect();
        if (body.scrollHeight > body.clientHeight + 2 || body.scrollWidth > body.clientWidth + 2) issues.push('汇报正文超出安全区');
        for (const node of body.querySelectorAll('*')) {
          if (node.closest('.katex') && !node.classList.contains('katex')) continue;
          const box = node.getBoundingClientRect();
          if (box.width && box.height && (box.right > bounds.right + 2 || box.left < bounds.left - 2 || box.bottom > bounds.bottom + 2)) {
            issues.push('汇报元素越界: ' + node.tagName); break;
          }
        }
      } else {
        if (!document.querySelector('.prose')?.textContent.trim()) issues.push('正文为空');
        if (document.documentElement.scrollWidth > innerWidth + 2) issues.push('文档横向溢出');
      }
      return issues;
    }''', scene)


def render_content(source, *, scene, output_dir, theme='light', browser_executable=None):
    if scene not in ('learning', 'blog', 'report'):
        raise ValueError('小红书使用原 rednote_render.py；本检查器用于 learning、blog、report')
    source, output = Path(source).resolve(), Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    generated = [(output, r'page-\d+\.png')]
    generated.extend((output / 'checks' / name, r'(?:page|section|screen)-\d+\.png') for name in ('light', 'dark'))
    for folder, pattern in generated:
        for previous in folder.glob('*.png'):
            if re.fullmatch(pattern, previous.name):
                if previous.resolve().parent != folder.resolve():
                    raise ValueError('旧导出文件必须位于指定成品目录内')
                previous.unlink()
    destination = output / 'index.html'
    if source != destination:
        shutil.copy2(source, destination)
    result = {'scene': scene, 'theme': theme, 'html_sha256': file_hash(destination),
              'passed': False, 'issues': [], 'warnings': [], 'themes': {}, 'images': []}
    with sync_playwright() as playwright:
        options = {'headless': True}
        if browser_executable:
            options['executable_path'] = browser_executable
        browser = playwright.chromium.launch(**options)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, offline=True)
        page = context.new_page()
        # 每轮检查从独立阅读状态开始，避免上一主题的截图滚动变成续读提示。
        page.add_init_script('try { localStorage.clear(); } catch (_) {}')
        resource_failures, script_errors = [], []
        page.on('requestfailed', lambda request: resource_failures.append(request.url))
        page.on('pageerror', lambda error: script_errors.append(str(error)))
        for selected_theme in ('light', 'dark'):
            page.set_viewport_size({'width': 1440, 'height': 1000})
            resource_failures.clear()
            script_errors.clear()
            page.goto(destination.as_uri(), wait_until='load')
            page.evaluate('document.fonts.ready')
            page.evaluate('''async () => { await Promise.all([...document.images].map(image => image.decode().catch(() => {}))); }''')
            if scene != 'report' and page.evaluate('typeof window.contentReadingReady !== "undefined"'):
                page.wait_for_function('window.contentReadingReady === true')
            page.evaluate('theme => window.setContentTheme(theme)', selected_theme)
            page.locator('#theme-toggle').click()
            switched = page.evaluate('document.documentElement.dataset.theme')
            if switched == selected_theme:
                result['issues'].append('明暗主题按钮未切换')
            page.locator('#theme-toggle').click()
            page.screenshot(path=str(output / f'preview-{selected_theme}.png'))
            checks = output / 'checks' / selected_theme
            checks.mkdir(parents=True, exist_ok=True)
            issues = []
            palette = inspect_palette(page)
            issues.extend('文字配色对比度不足: ' + item['fg'] + '/' + item['bg'] for item in palette if not item['passed'])
            visual_checks = []
            if scene == 'report':
                for width, height in ((1440, 1000), (960, 667), (720, 500)):
                    page.set_viewport_size({'width': width, 'height': height})
                    page.evaluate('window.dispatchEvent(new Event("resize"))')
                    fits = page.evaluate('''() => {
                      const frame = document.querySelector('.presentation').getBoundingClientRect();
                      const stage = document.querySelector('.slide-stage').getBoundingClientRect();
                      return stage.left >= frame.left - 2 && stage.right <= frame.right + 2 &&
                        stage.top >= frame.top - 2 && stage.bottom <= frame.bottom + 2;
                    }''')
                    if not fits:
                        issues.append(f'{width}×{height}窗口下演示舞台被裁切')
                    page.screenshot(path=str(checks / f'window-{width}.png'))
                page.set_viewport_size({'width': 1440, 'height': 1000})
                count = page.locator('[data-export-page]').count()
                if not count:
                    issues.append('没有汇报页')
                if count > 1:
                    page.keyboard.press('ArrowRight')
                    if page.locator('#slide-counter').inner_text() != f'2 / {count}':
                        issues.append('键盘翻页失败')
                    page.keyboard.press('Home')
                page.locator('#notes-toggle').click()
                if not page.locator('#speaker-notes').is_visible():
                    issues.append('讲者备注无法打开')
                page.locator('#notes-toggle').click()
                for index in range(count):
                    page.evaluate('index => window.activateContentExport({index})', index)
                    issues.extend(f'第 {index + 1} 页：{issue}' for issue in inspect_page(page, scene))
                    visual_checks.append(inspect_visuals(page, '[data-export-page]:not([hidden])', minimum=18))
                    image = checks / f'page-{index + 1:02d}.png'
                    page.locator('[data-export-page]:not([hidden])').screenshot(path=str(image))
                    if selected_theme == theme:
                        published = output / image.name
                        shutil.copy2(image, published)
                        result['images'].append({'file': image.name, 'sha256': file_hash(published)})
            else:
                issues.extend(inspect_page(page, scene))
                # 默认折叠状态已保留在首屏；完整检查还须覆盖补充内容和长代码。
                page.locator('.prose details').evaluate_all('nodes => nodes.forEach(node => node.open = true)')
                page.locator('.code-expand[aria-expanded="false"]').evaluate_all('nodes => nodes.forEach(node => node.click())')
                issues.extend(inspect_page(page, scene))
                headings = page.locator('.prose h2')
                for index in range(headings.count()):
                    headings.nth(index).scroll_into_view_if_needed()
                    page.screenshot(path=str(checks / f'section-{index + 1:02d}.png'))
                page.evaluate('document.documentElement.style.scrollBehavior = "auto"')
                page.evaluate('scrollTo(0, 0)')
                visual_checks.append(inspect_visuals(page, '.prose'))
                page.screenshot(path=str(checks / 'full.png'), full_page=True)
                height = page.evaluate('document.documentElement.scrollHeight')
                for index, top in enumerate(range(0, height, 900), 1):
                    page.evaluate('top => scrollTo(0, top)', top)
                    page.screenshot(path=str(checks / f'screen-{index:02d}.png'))
                # CSS布局缩放与字号分别检查；不把截图DPR当作浏览器布局缩放。
                for zoom in (1, 1.5, 2):
                    page.evaluate('zoom => document.documentElement.style.zoom = zoom', zoom)
                    for size in (16, 24):
                        page.evaluate('size => document.documentElement.style.setProperty("--reading-size", size + "px")', size)
                        issues.extend(f'布局缩放{zoom}、字号{size}: {issue}' for issue in inspect_page(page, scene))
                    page.evaluate('scrollTo(0, 0)')
                    page.screenshot(path=str(checks / f'zoom-{zoom:g}.png'))
                page.evaluate('document.documentElement.style.zoom = 1')
                page.evaluate('document.documentElement.style.setProperty("--reading-size", "18px")')
            for visual in visual_checks:
                issues.extend(visual['issues'])
                result['warnings'].extend(visual['warnings'])
            issues.extend('离线资源加载失败: ' + url for url in resource_failures)
            issues.extend('脚本错误: ' + error for error in script_errors)
            result['themes'][selected_theme] = {'passed': not issues, 'issues': issues, 'palette': palette, 'visual_checks': visual_checks}
            result['issues'].extend(f'{selected_theme}: {issue}' for issue in issues)
        context.close()
        browser.close()
    result['passed'] = not result['issues']
    result['warnings'] = sorted(set(result['warnings']))
    (output / 'qa.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not result['passed']:
        raise ValueError('检查失败，详见 qa.json：' + '; '.join(result['issues']))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html')
    parser.add_argument('--scene', choices=('learning', 'blog', 'report'), required=True)
    parser.add_argument('--output-dir', '-o', required=True)
    parser.add_argument('--theme', choices=('light', 'dark'), default='light', help='汇报 PNG 使用的主题；两种主题都会检查')
    parser.add_argument('--browser-executable')
    args = parser.parse_args()
    try:
        result = render_content(args.html, scene=args.scene, output_dir=args.output_dir,
                                theme=args.theme, browser_executable=args.browser_executable)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(2, f'检查失败：{error}\n')


if __name__ == '__main__':
    main()
