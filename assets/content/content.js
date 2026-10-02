(() => {
  const root = document.documentElement;
  const systemTheme = matchMedia('(prefers-color-scheme: dark)');
  let preference = root.dataset.defaultTheme || 'light';
  try { preference = localStorage.getItem('personal-html-workspace-theme') || preference; } catch (_) {}
  const themeButton = document.getElementById('theme-toggle');
  window.setContentTheme = (theme, save = false) => {
    preference = theme;
    const actual = theme === 'system' ? (systemTheme.matches ? 'dark' : 'light') : theme;
    root.dataset.theme = actual;
    themeButton.setAttribute('aria-label', actual === 'dark' ? '切换到浅色主题' : '切换到深色主题');
    themeButton.title = actual === 'dark' ? '切换到浅色主题' : '切换到深色主题';
    if (save) { try { localStorage.setItem('personal-html-workspace-theme', theme); } catch (_) {} }
  };
  setContentTheme(preference);
  themeButton.addEventListener('click', () => setContentTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', true));
  systemTheme.addEventListener('change', () => { if (preference === 'system') setContentTheme('system'); });

  const fontOutput = document.getElementById('font-size');
  if (fontOutput) {
    let readingSize = 18;
    try { readingSize = Number(localStorage.getItem('personal-html-workspace-font-size')) || 18; } catch (_) {}
    const setReadingSize = size => {
      readingSize = Math.max(16, Math.min(24, size));
      root.style.setProperty('--reading-size', readingSize + 'px');
      fontOutput.textContent = readingSize + 'px';
      document.getElementById('font-smaller').disabled = readingSize === 16;
      document.getElementById('font-larger').disabled = readingSize === 24;
      try { localStorage.setItem('personal-html-workspace-font-size', readingSize); } catch (_) {}
    };
    setReadingSize(readingSize);
    const readingAnchor = () => {
      const article = document.querySelector('.prose');
      const left = article.getBoundingClientRect().left + 24;
      const top = document.querySelector('.toolbar').getBoundingClientRect().bottom + 24;
      for (let y = top; y <= top + 72; y += 24) {
        let range;
        if (document.caretPositionFromPoint) {
          const caret = document.caretPositionFromPoint(left, y);
          if (caret) { range = document.createRange(); range.setStart(caret.offsetNode, caret.offset); range.collapse(true); }
        } else range = document.caretRangeFromPoint?.(left, y);
        if (range?.startContainer.nodeType === Node.TEXT_NODE && article.contains(range.startContainer)) {
          const box = range.getBoundingClientRect();
          if (box.height) return {range, top: box.top};
        }
      }
      // 图面、公式或段间留白没有文字插入点时，按当前块的相对位置保持阅读。
      const block = [...article.children].find(node => {
        const box = node.getBoundingClientRect();
        return box.height && box.bottom > top && box.top < innerHeight;
      });
      if (block) {
        const box = block.getBoundingClientRect();
        const point = Math.max(top, box.top);
        return {block, fraction: (point - box.top) / box.height, top: point};
      }
    };
    const changeReadingSize = delta => {
      const anchor = readingAnchor();
      const previousAnchor = root.style.overflowAnchor;
      root.style.overflowAnchor = 'none';
      setReadingSize(readingSize + delta);
      if (anchor) {
        const box = anchor.range ? anchor.range.getBoundingClientRect() : anchor.block.getBoundingClientRect();
        const top = anchor.range ? box.top : box.top + box.height * anchor.fraction;
        scrollBy({top: top - anchor.top, behavior: 'instant'});
      }
      root.style.overflowAnchor = previousAnchor;
    };
    document.getElementById('font-smaller').addEventListener('click', () => changeReadingSize(-2));
    document.getElementById('font-larger').addEventListener('click', () => changeReadingSize(2));
  }

  const figures = document.querySelectorAll('.prose img, .prose figure > svg, .slide-body img, .slide-body figure > svg');
  if (figures.length) {
    const viewer = document.createElement('dialog');
    viewer.className = 'image-viewer';
    viewer.setAttribute('aria-label', '查看大图');
    viewer.innerHTML = '<div class="image-viewer-bar"><span class="image-viewer-title">查看大图</span><div class="tools"><button data-zoom="1">适合窗口</button><button data-zoom="1.5">放大</button><button data-close>关闭</button></div></div><div class="image-viewer-content"></div><div class="image-viewer-caption" hidden></div>';
    const title = viewer.querySelector('.image-viewer-title');
    const caption = viewer.querySelector('.image-viewer-caption');
    const uniqueId = (base, used) => {
      let id = base, suffix = 2;
      while (used.has(id)) id = `${base}-${suffix++}`;
      used.add(id);
      return id;
    };
    caption.id = uniqueId('image-viewer-caption', new Set([...document.querySelectorAll('[id]')].map(node => node.id)));
    caption.setAttribute('role', 'region');
    caption.setAttribute('aria-label', '图注');
    document.body.append(viewer);
    const content = viewer.querySelector('.image-viewer-content');
    content.setAttribute('role', 'region');
    content.setAttribute('aria-label', '图像，可用方向键滚动');
    let opener, ratio = 1, zoom = 1;
    const fitViewer = () => {
      if (!viewer.open) return;
      const scale = Number(getComputedStyle(root).zoom) || 1;
      viewer.style.width = Math.min(innerWidth / scale * .94, 1600) + 'px';
      viewer.style.maxHeight = innerHeight / scale * .92 + 'px';
      content.style.maxHeight = innerHeight / scale * .72 + 'px';
      caption.style.maxHeight = innerHeight / scale * .4 + 'px';
      content.style.setProperty('--image-width', '100%');
      const width = Math.min(content.clientWidth, content.clientHeight * ratio);
      content.style.setProperty('--image-width', zoom === 1 ? width + 'px' : zoom * 100 + '%');
      content.tabIndex = content.scrollWidth > content.clientWidth + 1 || content.scrollHeight > content.clientHeight + 1 ? 0 : -1;
      caption.tabIndex = caption.scrollHeight > caption.clientHeight + 1 ? 0 : -1;
      viewer.querySelectorAll('[data-zoom]').forEach(button => {
        button.setAttribute('aria-pressed', String(Number(button.dataset.zoom) === zoom));
      });
    };
    addEventListener('resize', fitViewer);
    viewer.querySelector('[data-close]').addEventListener('click', () => viewer.close());
    viewer.addEventListener('click', event => { if (event.target === viewer) viewer.close(); });
    viewer.addEventListener('close', () => {
      content.replaceChildren();
      caption.replaceChildren();
      caption.hidden = true;
      viewer.removeAttribute('aria-describedby');
      opener?.focus({preventScroll: true});
    });
    viewer.querySelectorAll('[data-zoom]').forEach(button => button.addEventListener('click', () => {
      zoom = Number(button.dataset.zoom);
      fitViewer();
      content.scrollTo(0, 0);
    }));
    figures.forEach(figure => {
      if (figure.closest('a')) return;
      figure.setAttribute('tabindex', '0');
      const label = figure.getAttribute('aria-label') || figure.getAttribute('alt') || '图解';
      figure.setAttribute('aria-label', label + '，点击放大');
      const open = () => {
        opener = figure;
        const copy = figure.cloneNode(true);
        copy.removeAttribute('tabindex');
        copy.setAttribute('aria-label', label);
        const box = figure.getBoundingClientRect();
        const viewBox = figure.viewBox?.baseVal;
        ratio = viewBox?.width && viewBox.height ? viewBox.width / viewBox.height :
          figure.naturalWidth && figure.naturalHeight ? figure.naturalWidth / figure.naturalHeight : box.width / box.height;
        copy.style.aspectRatio = String(ratio);
        copy.style.width = 'var(--image-width, 100%)';
        copy.style.height = 'auto';
        copy.style.maxWidth = 'none';
        copy.style.maxHeight = 'none';
        const sourceCaption = figure.closest('figure')?.querySelector('figcaption');
        caption.replaceChildren(...[...(sourceCaption?.childNodes || [])].map(node => node.cloneNode(true)));
        caption.hidden = !sourceCaption;
        if (sourceCaption) viewer.setAttribute('aria-describedby', caption.id);
        else viewer.removeAttribute('aria-describedby');
        title.textContent = label;
        title.title = label;
        viewer.setAttribute('aria-label', '查看大图：' + label);
        // 保留SVG箭头、裁剪路径和引用，同时避免复制后ID冲突。
        const ids = new Map();
        if (sourceCaption?.id) ids.set(sourceCaption.id, caption.id);
        const used = new Set([...document.querySelectorAll('[id]')].map(node => node.id));
        const nodes = [copy, ...copy.querySelectorAll('*'), ...caption.querySelectorAll('*')];
        nodes.filter(node => node.id).forEach(node => { ids.set(node.id, uniqueId('viewer-' + node.id, used)); node.id = ids.get(node.id); });
        for (const node of nodes) {
          for (const attribute of [...node.attributes]) {
            let value = attribute.value;
            ids.forEach((newId, oldId) => {
              value = value.replaceAll('url(#' + oldId + ')', 'url(#' + newId + ')');
              value = value.replaceAll('url("#' + oldId + '")', 'url("#' + newId + '")');
              value = value.replaceAll("url('#" + oldId + "')", "url('#" + newId + "')");
              if (value === '#' + oldId) value = '#' + newId;
            });
            if (attribute.name === 'aria-labelledby' || attribute.name === 'aria-describedby') {
              value = value.split(/\s+/).map(id => ids.get(id) || id).join(' ');
            }
            if (value !== attribute.value) node.setAttribute(attribute.name, value);
          }
        }
        zoom = 1;
        content.replaceChildren(copy);
        viewer.showModal();
        fitViewer();
        content.scrollTo(0, 0);
      };
      figure.addEventListener('click', open);
      figure.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); open(); } });
    });
  }

  const toc = document.getElementById('toc');
  const tocLinks = document.getElementById('toc-links');
  const tocButton = document.getElementById('toc-toggle');
  const isReport = document.body.classList.contains('scene-report');
  const compactLayout = matchMedia('(max-width: 1000px)');
  const updateTocState = () => tocButton.setAttribute('aria-expanded', String(isReport || compactLayout.matches ? toc.classList.contains('open') : !document.body.classList.contains('toc-hidden')));
  updateTocState();
  compactLayout.addEventListener('change', updateTocState);
  tocButton.addEventListener('click', () => {
    if (isReport || compactLayout.matches) toc.classList.toggle('open');
    else document.body.classList.toggle('toc-hidden');
    updateTocState();
  });
  const slides = [...document.querySelectorAll('[data-export-page]')];
  if (!slides.length) {
    const headings = [...document.querySelectorAll('.prose h2, .prose h3')];
    const headingIds = new Set([...document.querySelectorAll('[id]')].map(node => node.id));
    let chapterNumber = 0;
    headings.forEach((heading, index) => {
      if (!heading.id) {
        const base = heading.textContent.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '') || 'section';
        let id = base, suffix = 2;
        while (headingIds.has(id)) id = `${base}-${suffix++}`;
        heading.id = id;
        headingIds.add(id);
      }
      const link = document.createElement('a');
      link.href = `#${heading.id}`;
      if (heading.tagName === 'H3') {
        link.className = 'subheading';
        link.textContent = heading.textContent;
      } else {
        const index = document.createElement('span');
        index.className = 'toc-index';
        index.setAttribute('aria-hidden', 'true');
        index.textContent = String(++chapterNumber).padStart(2, '0');
        const title = document.createElement('span');
        title.textContent = heading.textContent;
        link.append(index, title);
      }
      tocLinks.append(link);
    });
    const count = document.getElementById('toc-count');
    if (count) { count.textContent = `${chapterNumber} 章节`; count.hidden = chapterNumber === 0; }
    const links = [...tocLinks.children];
    let previousCurrent;
    const updateReading = () => {
      const available = root.scrollHeight - innerHeight;
      document.getElementById('reading-progress').style.width = `${available > 0 ? scrollY / available * 100 : 100}%`;
      const visible = headings.filter(heading => heading.getClientRects().length);
      let current = visible[0], chapter;
      visible.forEach(heading => { if (heading.getBoundingClientRect().top < 160) current = heading; });
      // 短结尾不能滚到工具栏下方，也应在文末成为当前章节。
      if (available > 0 && scrollY >= available - 2) current = visible.at(-1);
      for (const heading of visible) {
        if (heading.tagName === 'H2') chapter = heading;
        if (heading === current) break;
      }
      links.forEach((link, index) => {
        if (headings[index] === current) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
        link.classList.toggle('toc-parent', current?.tagName === 'H3' && headings[index] === chapter);
      });
      const active = links[headings.indexOf(current)];
      if (active && current !== previousCurrent && toc.getClientRects().length) {
        const frame = toc.getBoundingClientRect(), item = active.getBoundingClientRect();
        if (item.top < frame.top) toc.scrollTop -= frame.top - item.top + 12;
        else if (item.bottom > frame.bottom) toc.scrollTop += item.bottom - frame.bottom + 12;
      }
      previousCurrent = current;
    };
    addEventListener('scroll', updateReading, { passive: true });
    addEventListener('resize', updateReading);
    new ResizeObserver(updateReading).observe(document.getElementById('content'));
    document.querySelector('.prose').addEventListener('toggle', updateReading, true);
    tocButton.addEventListener('click', () => { previousCurrent = null; updateReading(); });
    updateReading();
    return;
  }

  let current = 0;
  const notes = document.getElementById('speaker-notes');
  const notesButton = document.getElementById('notes-toggle');
  const previous = document.getElementById('previous-slide');
  const next = document.getElementById('next-slide');
  const showSlide = index => {
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, i) => { slide.hidden = i !== current; });
    document.getElementById('slide-counter').textContent = `${current + 1} / ${slides.length}`;
    document.getElementById('notes-content').textContent = slides[current].dataset.notes || '本页未附讲者备注。';
    previous.disabled = current === 0;
    next.disabled = current === slides.length - 1;
    [...tocLinks.children].forEach((link, i) => {
      if (i === current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };
  slides.forEach((slide, index) => {
    const link = document.createElement('a');
    link.href = `#slide-${index + 1}`;
    link.textContent = `${String(index + 1).padStart(2, '0')}  ${slide.querySelector('h1, h2, h3')?.textContent || '页面'}`;
    link.addEventListener('click', event => {
      event.preventDefault(); showSlide(index); toc.classList.remove('open'); tocButton.setAttribute('aria-expanded', 'false');
    });
    tocLinks.append(link);
  });
  const toggleNotes = () => { notes.hidden = !notes.hidden; notesButton.setAttribute('aria-expanded', String(!notes.hidden)); };
  notesButton.addEventListener('click', toggleNotes);
  previous.addEventListener('click', () => showSlide(current - 1));
  next.addEventListener('click', () => showSlide(current + 1));
  addEventListener('keydown', event => {
    if (document.querySelector('dialog[open]')) return;
    if (event.target.closest('input, textarea, select, [contenteditable]')) return;
    if (event.key === 'ArrowRight' || event.key === 'PageDown') { event.preventDefault(); showSlide(current + 1); }
    if (event.key === 'ArrowLeft' || event.key === 'PageUp') { event.preventDefault(); showSlide(current - 1); }
    if (event.key === 'Home') { event.preventDefault(); showSlide(0); }
    if (event.key === 'End') { event.preventDefault(); showSlide(slides.length - 1); }
    if (event.key.toLowerCase() === 'n') toggleNotes();
    if (event.key === 'Escape') { toc.classList.remove('open'); tocButton.setAttribute('aria-expanded', 'false'); notes.hidden = true; notesButton.setAttribute('aria-expanded', 'false'); }
  });
  const resizeSlides = () => root.style.setProperty('--slide-scale', String(Math.min((innerWidth - 48) / 1280, (innerHeight - 152) / 720)));
  addEventListener('resize', resizeSlides);
  window.activateContentExport = async ({ index }) => {
    document.body.classList.add('exporting'); showSlide(index); await document.fonts.ready;
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  };
  showSlide(0); resizeSlides();
})();
