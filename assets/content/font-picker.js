(() => {
  const toggle = document.getElementById('font-picker-toggle');
  if (!toggle) return;
  const root = document.documentElement;
  const panel = document.getElementById('font-picker');
  const search = document.getElementById('font-search');
  const list = document.getElementById('font-options');
  const status = document.getElementById('font-picker-status');
  const load = document.getElementById('load-local-fonts');
  const label = document.getElementById('font-family-label');
  const storageKey = 'content-reading-font';
  const presets = [
    {id: 'default', name: '默认字体', css: 'var(--default-font)', group: '默认', keywords: 'Noto Sans SC 思源黑体'},
    {id: 'system', name: '系统界面字体', css: 'system-ui', group: '系统', keywords: '系统默认'},
    {id: 'sans-serif', name: '浏览器无衬线', css: 'sans-serif', group: '浏览器配置', keywords: 'sans-serif 黑体'},
    {id: 'serif', name: '浏览器衬线', css: 'serif', group: '浏览器配置', keywords: 'serif 宋体'},
    {id: 'monospace', name: '浏览器等宽', css: 'monospace', group: '浏览器配置', keywords: 'monospace'}
  ];
  const aliases = {
    'Microsoft YaHei': '微软雅黑', 'Microsoft YaHei UI': '微软雅黑 UI',
    SimSun: '宋体', NSimSun: '新宋体', SimHei: '黑体', KaiTi: '楷体', FangSong: '仿宋', DengXian: '等线',
    'PingFang SC': '苹方', 'Songti SC': '宋体', 'Heiti SC': '黑体', 'Kaiti SC': '楷体',
    'Noto Sans SC': '思源黑体', 'Source Han Sans SC': '思源黑体', 'Noto Serif SC': '思源宋体'
  };
  const localOption = family => ({
    id: 'local:' + family, name: family, group: '本机字体', keywords: aliases[family] || '',
    css: '"' + family.replaceAll('\\', '\\\\').replaceAll('"', '\\"').replace(/[\n\r\f]/g, ' ') + '", var(--default-font)'
  });
  let chosen = presets[0], locals = [], visible = [], active = -1, anchor;
  let localStatus = '点击“加载本机字体”，授权后可搜索已安装字体。';
  if (typeof window.queryLocalFonts !== 'function') {
    load.hidden = true;
    localStatus = '当前浏览器不支持列出本机字体；仍可使用上方选项。';
  }
  try {
    const saved = localStorage.getItem(storageKey);
    chosen = presets.find(option => option.id === saved) || chosen;
    if (saved?.startsWith('local:') && saved.slice(6).trim()) {
      chosen = localOption(saved.slice(6));
      locals = [chosen];
    }
  } catch (_) {}
  const apply = option => {
    chosen = option;
    root.style.setProperty('--reading-font', option.css);
    label.textContent = option.name;
    toggle.title = '选择正文字体：' + option.name;
    toggle.setAttribute('aria-label', '正文字体：' + option.name);
  };
  apply(chosen);

  const setActive = (index, scroll = false) => {
    const options = [...list.querySelectorAll('[role="option"]')];
    active = options.length ? Math.max(0, Math.min(options.length - 1, index)) : -1;
    options.forEach((node, i) => node.classList.toggle('is-active', i === active));
    if (active < 0) search.removeAttribute('aria-activedescendant');
    else {
      const node = options[active];
      search.setAttribute('aria-activedescendant', node.id);
      // 只滚动候选列表，不让选项滚动带动正文。
      if (scroll) {
        const item = node.getBoundingClientRect(), frame = list.getBoundingClientRect();
        const scale = Number(getComputedStyle(root).zoom) || 1;
        if (item.top < frame.top) list.scrollTop -= (frame.top - item.top) / scale;
        else if (item.bottom > frame.bottom) list.scrollTop += (item.bottom - frame.bottom) / scale;
      }
    }
  };
  const render = () => {
    const query = search.value.trim().normalize('NFKC').toLocaleLowerCase();
    visible = [...presets, ...locals].filter(option =>
      `${option.name} ${option.keywords || ''}`.normalize('NFKC').toLocaleLowerCase().includes(query));
    const fragment = document.createDocumentFragment();
    let previousGroup;
    visible.forEach((option, index) => {
      if (option.group !== previousGroup) {
        const heading = document.createElement('p');
        heading.className = 'font-group';
        heading.textContent = option.group;
        fragment.append(heading);
        previousGroup = option.group;
      }
      const node = document.createElement('div');
      node.id = 'font-option-' + index;
      node.className = 'font-option';
      node.setAttribute('role', 'option');
      node.setAttribute('aria-selected', String(chosen.id === option.id));
      node.textContent = option.name;
      node.addEventListener('pointermove', () => { if (active !== index) setActive(index); });
      node.addEventListener('mousedown', event => event.preventDefault());
      node.addEventListener('click', () => choose(option));
      fragment.append(node);
    });
    list.replaceChildren(fragment);
    list.scrollTop = 0;
    setActive(Math.max(0, visible.findIndex(option => option.id === chosen.id)));
    status.textContent = (visible.length ? '' : '没有匹配的字体。') + localStatus;
  };
  const close = (focus = false) => {
    panel.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
    if (focus) toggle.focus({preventScroll: true});
  };
  const position = () => {
    const scale = Number(getComputedStyle(root).zoom) || 1;
    const box = toggle.getBoundingClientRect();
    const width = Math.min(320, innerWidth / scale - 24);
    panel.style.width = width + 'px';
    panel.style.left = Math.max(12, Math.min(box.left / scale, innerWidth / scale - width - 12)) + 'px';
    const top = Math.min(box.bottom / scale + 8, innerHeight / scale - 140);
    panel.style.top = Math.max(12, top) + 'px';
    panel.style.maxHeight = Math.max(100, innerHeight / scale - Math.max(12, top) - 12) + 'px';
  };
  const choose = option => {
    close(true);
    window.preserveContentPosition(() => apply(option), anchor);
    try { localStorage.setItem(storageKey, option.id); } catch (_) {}
  };
  toggle.addEventListener('click', () => {
    if (!panel.hidden) { close(); return; }
    anchor = window.captureContentPosition();
    search.value = '';
    render();
    panel.hidden = false;
    toggle.setAttribute('aria-expanded', 'true');
    position();
    search.focus({preventScroll: true});
  });
  search.addEventListener('input', render);
  search.addEventListener('keydown', event => {
    if (event.isComposing) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      setActive(active + (event.key === 'ArrowDown' ? 1 : -1), true);
    } else if (event.key === 'Enter' && active >= 0) {
      event.preventDefault();
      choose(visible[active]);
    }
  });
  panel.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.stopPropagation(); close(true); }
  });
  document.addEventListener('pointerdown', event => {
    if (!panel.hidden && !panel.contains(event.target) && !toggle.contains(event.target)) close();
  });
  document.addEventListener('focusin', event => {
    if (!panel.hidden && !panel.contains(event.target) && !toggle.contains(event.target)) close();
  });
  addEventListener('scroll', () => { if (!panel.hidden) close(); }, {passive: true});
  addEventListener('resize', () => { if (!panel.hidden) close(true); });
  addEventListener('beforeprint', () => close());
  load.addEventListener('click', async () => {
    load.disabled = true;
    status.textContent = '正在读取本机字体…';
    try {
      const fonts = await window.queryLocalFonts();
      const families = new Map();
      for (const font of fonts) {
        const family = font.family.trim();
        if (!family || family.startsWith('@')) continue;
        const key = family.toLocaleLowerCase();
        if (!families.has(key)) families.set(key, localOption(family));
        families.get(key).keywords += ' ' + font.fullName + ' ' + font.postscriptName;
      }
      locals = [...families.values()].sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
      if (chosen.id.startsWith('local:') && !locals.some(option => option.id === chosen.id)) locals.unshift(chosen);
      localStatus = families.size ? `已加载 ${families.size} 种本机字体；缺少的字形使用默认字体。` :
        '浏览器未返回字体列表；仍可使用上方选项。';
      load.textContent = '重新加载本机字体';
    } catch (error) {
      localStatus = error.name === 'NotAllowedError' ? '未获字体访问授权；可重试或使用上方选项。' :
        '当前页面无法读取本机字体；可重试或使用上方选项。';
    } finally {
      load.disabled = false;
      render();
    }
  });
})();
