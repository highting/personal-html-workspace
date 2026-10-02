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
    document.getElementById('font-smaller').addEventListener('click', () => setReadingSize(readingSize - 2));
    document.getElementById('font-larger').addEventListener('click', () => setReadingSize(readingSize + 2));
  }

  const figures = document.querySelectorAll('.prose img, .prose figure > svg, .slide-body img, .slide-body figure > svg');
  if (figures.length) {
    const viewer = document.createElement('dialog');
    viewer.className = 'image-viewer';
    viewer.setAttribute('aria-label', '查看大图');
    viewer.innerHTML = '<div class="image-viewer-bar"><span>查看大图</span><div class="tools"><button data-zoom="1">适合窗口</button><button data-zoom="1.5">放大</button><button data-close>关闭</button></div></div><div class="image-viewer-content"></div>';
    document.body.append(viewer);
    const content = viewer.querySelector('.image-viewer-content');
    let opener;
    viewer.querySelector('[data-close]').addEventListener('click', () => viewer.close());
    viewer.addEventListener('click', event => { if (event.target === viewer) viewer.close(); });
    viewer.addEventListener('close', () => { content.replaceChildren(); opener?.focus({preventScroll: true}); });
    viewer.querySelectorAll('[data-zoom]').forEach(button => button.addEventListener('click', () => {
      content.style.setProperty('--image-width', Number(button.dataset.zoom) * 100 + '%');
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
        copy.removeAttribute('id');
        // 保留SVG箭头、裁剪路径和引用，同时避免复制后ID冲突。
        const ids = new Map();
        copy.querySelectorAll('[id]').forEach(node => { ids.set(node.id, 'viewer-' + node.id); node.id = ids.get(node.id); });
        for (const node of [copy, ...copy.querySelectorAll('*')]) {
          for (const attribute of [...node.attributes]) {
            let value = attribute.value;
            ids.forEach((newId, oldId) => {
              value = value.replaceAll('url(#' + oldId + ')', 'url(#' + newId + ')');
              if (value === '#' + oldId) value = '#' + newId;
            });
            if (value !== attribute.value) node.setAttribute(attribute.name, value);
          }
        }
        content.style.setProperty('--image-width', '100%');
        content.replaceChildren(copy);
        viewer.showModal();
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
      link.textContent = heading.textContent;
      if (heading.tagName === 'H3') link.className = 'subheading';
      tocLinks.append(link);
    });
    const updateReading = () => {
      const available = root.scrollHeight - innerHeight;
      document.getElementById('reading-progress').style.width = `${available > 0 ? scrollY / available * 100 : 100}%`;
      let current = headings[0];
      headings.forEach(heading => { if (heading.getClientRects().length && heading.getBoundingClientRect().top < 160) current = heading; });
      [...tocLinks.children].forEach((link, index) => {
        if (headings[index] === current) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    };
    addEventListener('scroll', updateReading, { passive: true });
    document.querySelector('.prose').addEventListener('toggle', updateReading, true);
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
