"""检查真实显示字号与制作残留；可疑文案只提示，不代替人工判断。"""

VISUAL_INSPECTION = r'''({selector, scale = 1, minimum = 12}) => {
  const roots = [...document.querySelectorAll(selector)];
  const visible = node => node.getClientRects().length && getComputedStyle(node).visibility !== 'hidden';
  const issues = [], warnings = [], labels = [];
  for (const root of roots.filter(visible)) {
    for (const node of root.querySelectorAll('svg text')) {
      if (!visible(node) || node.closest('.katex')) continue;
      const matrix = node.getScreenCTM();
      const px = parseFloat(getComputedStyle(node).fontSize) * Math.hypot(matrix.a, matrix.b) * scale;
      labels.push({text: node.textContent.trim(), px: Math.round(px * 10) / 10});
      if (px < minimum - .1) issues.push('图中文字过小: ' + node.textContent.trim() + ' (' + px.toFixed(1) + 'px)');
    }
    for (const node of root.querySelectorAll('h1,h2,h3,p,figcaption,text,.cover-title,.cover-subtitle')) {
      if (!visible(node) || node.closest('pre,code,.katex')) continue;
      const text = node.textContent.trim();
      if (/稿子示例|排版示例|草稿示例|占位文案|待补充|此处插入|依据用户博客整理|按用户要求生成/.test(text)) {
        warnings.push('核对成品文案: ' + text.slice(0, 100));
      }
    }
  }
  return {issues: [...new Set(issues)], warnings: [...new Set(warnings)], labels};
}'''


def inspect_visuals(page, selector, *, scale=1, minimum=12):
    return page.evaluate(VISUAL_INSPECTION, {'selector': selector, 'scale': scale, 'minimum': minimum})


def inspect_palette(page):
    """核对模板实际主题变量的文字对比度，不声称覆盖任意图片/透明叠层。"""
    return page.evaluate('''() => {
      const style = getComputedStyle(document.documentElement);
      const luminance = name => {
        const hex = style.getPropertyValue(name).trim().slice(1);
        const rgb = [0, 2, 4].map(i => parseInt(hex.slice(i, i + 2), 16) / 255)
          .map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
        return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
      };
      return [['--text','--bg'],['--muted','--bg'],['--accent','--bg'],
              ['--text','--figure-bg'],['--muted','--figure-bg'],['--text','--code-bg']].map(([fg,bg]) => {
        const a = luminance(fg), b = luminance(bg);
        const ratio = (Math.max(a,b) + .05) / (Math.min(a,b) + .05);
        return {fg, bg, ratio: Math.round(ratio * 100) / 100, passed: Number.isFinite(ratio) && ratio >= 4.5};
      });
    }''')
