(() => {
  window.contentReadingReady = false;
  const article = document.querySelector('.prose');
  const status = document.getElementById('reading-status');
  const root = document.documentElement;
  const usedIds = new Set([...document.querySelectorAll('[id]')].map(node => node.id));
  const uniqueId = base => {
    let id = base, suffix = 2;
    while (usedIds.has(id)) id = `${base}-${suffix++}`;
    usedIds.add(id);
    return id;
  };

  const copyText = async text => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (_) {
      // file:// 或剪贴板权限不可用时，仍允许在本地页面复制。
      const focused = document.activeElement;
      const input = document.createElement('textarea');
      input.value = text;
      input.readOnly = true;
      input.style.cssText = 'position:fixed;top:0;left:-9999px';
      document.body.append(input);
      input.select();
      let copied = false;
      try { copied = document.execCommand('copy'); } catch (_) {}
      input.remove();
      focused?.focus({preventScroll: true});
      return copied;
    }
  };

  const headings = [...article.querySelectorAll('h2,h3')];
  const codeBlocks = [...article.querySelectorAll('.code-block')];
  const codeKeyCounts = new Map();
  codeBlocks.forEach((block, index) => {
    const section = headings.filter(heading => heading.compareDocumentPosition(block) & Node.DOCUMENT_POSITION_FOLLOWING).at(-1);
    const base = `${section?.id || ''}:${block.dataset.codeKey || `code-${index + 1}`}`;
    const occurrence = (codeKeyCounts.get(base) || 0) + 1;
    codeKeyCounts.set(base, occurrence);
    block.dataset.readingKey = `${base}:${occurrence}`;
    const code = block.querySelector('code');
    const pre = block.querySelector('pre');
    const button = block.querySelector('.code-copy');
    const actions = document.createElement('div');
    actions.className = 'code-actions';
    const wrap = document.createElement('button');
    wrap.type = 'button';
    wrap.className = 'code-wrap';
    wrap.textContent = '换行';
    wrap.title = '自动换行';
    wrap.setAttribute('aria-label', '自动换行');
    wrap.setAttribute('aria-pressed', 'false');
    const updateWrapControl = () => {
      wrap.hidden = !block.classList.contains('is-wrapped') && pre.scrollWidth <= pre.clientWidth + 1;
    };
    wrap.addEventListener('click', () => {
      const enabled = block.classList.toggle('is-wrapped');
      wrap.setAttribute('aria-pressed', String(enabled));
      pre.scrollLeft = 0;
      updateWrapControl();
    });
    block.querySelector('.code-toolbar').append(actions);
    actions.append(wrap, button);
    new ResizeObserver(updateWrapControl).observe(pre);
    updateWrapControl();
    button.addEventListener('click', async () => {
      const copied = await copyText(code.textContent);
      button.textContent = copied ? '已复制' : '复制失败';
      status.textContent = copied ? '代码已复制' : '请手动选择代码复制';
      setTimeout(() => { button.textContent = '复制代码'; }, 2000);
    });
    if (Number(block.dataset.lines) > 20) {
      pre.id = pre.id || uniqueId(`code-${index + 1}`);
      const fold = document.createElement('button');
      fold.className = 'code-expand';
      fold.setAttribute('aria-controls', pre.id);
      const update = collapsed => {
        block.classList.toggle('is-collapsed', collapsed);
        fold.setAttribute('aria-expanded', String(!collapsed));
        fold.textContent = collapsed ? `展开全部 ${block.dataset.lines} 行` : '收起代码';
      };
      fold.addEventListener('click', () => {
        const collapsing = !block.classList.contains('is-collapsed');
        update(collapsing);
        if (collapsing && block.getBoundingClientRect().top < 76) block.scrollIntoView({block: 'start'});
      });
      update(true);
      block.append(fold);
    }
  });

  article.querySelectorAll('table').forEach(table => {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-wrap';
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', table.querySelector('caption')?.textContent || '数据表格');
    table.before(wrapper);
    wrapper.append(table);
  });

  headings.forEach(heading => {
    heading.dataset.title = heading.textContent;
    const anchor = document.createElement('a');
    anchor.className = 'heading-anchor';
    anchor.href = '#' + encodeURIComponent(heading.id);
    anchor.textContent = '#';
    anchor.setAttribute('aria-label', '复制章节链接：' + heading.dataset.title);
    anchor.title = '复制章节链接';
    anchor.addEventListener('click', async () => {
      const copied = await copyText(anchor.href);
      anchor.dataset.copied = String(copied);
      status.textContent = copied ? '章节链接已复制' : '请从地址栏复制章节链接';
      setTimeout(() => { delete anchor.dataset.copied; }, 2000);
    });
    heading.append(anchor);
  });

  const details = [...article.querySelectorAll('details')];
  details.forEach((detail, index) => {
    const label = detail.querySelector('summary')?.textContent.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '') || String(index + 1);
    if (!detail.id) detail.id = uniqueId(`supplement-${label}`);
  });
  const reveal = target => {
    for (let parent = target?.parentElement; parent; parent = parent.parentElement) {
      if (parent.tagName === 'DETAILS') parent.open = true;
    }
  };
  const revealHash = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const target = document.getElementById(id);
    if (target) { reveal(target); target.scrollIntoView({block: 'start'}); }
  };
  addEventListener('hashchange', revealHash);
  document.getElementById('toc-links').addEventListener('click', event => {
    const link = event.target.closest('a');
    if (link) reveal(document.getElementById(decodeURIComponent(link.hash.slice(1))));
  });

  // 按文章身份记录章节及章内比例，避免文件移动或字号变化后只凭像素定位。
  const key = 'content-reading:' + document.body.dataset.documentId;
  const banner = document.getElementById('resume-banner');
  let saved;
  try { saved = JSON.parse(localStorage.getItem(key)); } catch (_) {}
  let ready = false, timer;
  history.scrollRestoration = 'manual';
  const visibleHeadings = () => headings.filter(heading => heading.getClientRects().length);
  const position = () => {
    const visible = visibleHeadings();
    let current = visible[0];
    visible.forEach(heading => { if (heading.getBoundingClientRect().top <= 140) current = heading; });
    if (root.scrollHeight > innerHeight && scrollY >= root.scrollHeight - innerHeight - 2) current = visible.at(-1);
    if (!current) return null;
    const start = current.getBoundingClientRect().top + scrollY;
    const next = visible[visible.indexOf(current) + 1];
    const end = next ? next.getBoundingClientRect().top + scrollY : root.scrollHeight;
    return {section: current.id, progress: Math.max(0, Math.min(1, (scrollY + 100 - start) / Math.max(1, end - start))),
      openDetails: details.filter(detail => detail.open).map(detail => detail.id),
      codeViews: codeBlocks.map(block => ({key: block.dataset.readingKey,
        wrapped: block.classList.contains('is-wrapped'),
        expanded: block.querySelector('.code-expand')?.getAttribute('aria-expanded') === 'true'}))
        .filter(view => view.wrapped || view.expanded)};
  };
  const save = () => {
    if (!ready || scrollY < 180) return;
    const value = position();
    if (value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) {} }
  };
  addEventListener('scroll', () => { clearTimeout(timer); timer = setTimeout(save, 250); }, {passive: true});
  addEventListener('pagehide', save);
  document.addEventListener('visibilitychange', () => { if (document.hidden) save(); });

  document.getElementById('dismiss-reading').addEventListener('click', () => {
    banner.hidden = true;
    try { localStorage.removeItem(key); } catch (_) {}
  });
  document.getElementById('resume-reading').addEventListener('click', () => {
    const target = document.getElementById(saved.section);
    (saved.openDetails || []).forEach(id => {
      const detail = document.getElementById(id);
      if (detail?.tagName === 'DETAILS') detail.open = true;
    });
    (saved.codeViews || []).forEach(view => {
      const block = codeBlocks.find(block => block.dataset.readingKey === view.key);
      if (!block) return;
      if (view.wrapped && !block.classList.contains('is-wrapped')) block.querySelector('.code-wrap').click();
      if (view.expanded && block.classList.contains('is-collapsed')) block.querySelector('.code-expand')?.click();
    });
    reveal(target);
    banner.hidden = true;
    const visible = visibleHeadings();
    const next = visible[visible.indexOf(target) + 1];
    const start = target.getBoundingClientRect().top + scrollY;
    const end = next ? next.getBoundingClientRect().top + scrollY : root.scrollHeight;
    scrollTo({top: start + (end - start) * Math.max(0, Math.min(1, Number(saved.progress) || 0)) - 100, behavior: 'instant'});
  });

  const initializePosition = async () => {
    await document.fonts.ready;
    await Promise.all([...article.querySelectorAll('img')].map(image => image.decode().catch(() => {})));
    if (location.hash) revealHash();
    else {
      scrollTo({top: 0, behavior: 'instant'});
      const target = saved && headings.find(heading => heading.id === saved.section);
      if (target) {
        document.getElementById('resume-title').textContent = target.dataset.title;
        banner.hidden = false;
      }
    }
    ready = true;
    window.contentReadingReady = true;
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initializePosition, {once: true});
  else initializePosition();
})();
