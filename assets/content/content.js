(() => {
  const root = document.documentElement;
  const systemTheme = matchMedia('(prefers-color-scheme: dark)');
  let preference = root.dataset.defaultTheme || 'light';
  try { preference = localStorage.getItem('content-workbench-theme') || preference; } catch (_) {}
  const themeButton = document.getElementById('theme-toggle');
  window.setContentTheme = (theme, save = false) => {
    preference = theme;
    const actual = theme === 'system' ? (systemTheme.matches ? 'dark' : 'light') : theme;
    root.dataset.theme = actual;
    themeButton.setAttribute('aria-label', actual === 'dark' ? '切换到浅色主题' : '切换到深色主题');
    themeButton.title = actual === 'dark' ? '切换到浅色主题' : '切换到深色主题';
    if (save) { try { localStorage.setItem('content-workbench-theme', theme); } catch (_) {} }
  };
  setContentTheme(preference);
  themeButton.addEventListener('click', () => setContentTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', true));
  systemTheme.addEventListener('change', () => { if (preference === 'system') setContentTheme('system'); });

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
    headings.forEach((heading, index) => {
      if (!heading.id) heading.id = `section-${index + 1}`;
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
      headings.forEach(heading => { if (heading.getBoundingClientRect().top < 160) current = heading; });
      [...tocLinks.children].forEach((link, index) => {
        if (headings[index] === current) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    };
    addEventListener('scroll', updateReading, { passive: true });
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
