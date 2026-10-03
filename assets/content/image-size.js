(() => {
  const article = document.querySelector('.prose');
  if (!article) return;
  const storageKey = 'content-image-sizes:' + document.body.dataset.documentId;
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(storageKey)) || {}; } catch (_) {}
  const persist = () => { try { localStorage.setItem(storageKey, JSON.stringify(saved)); } catch (_) {} };

  article.querySelectorAll('img, figure > svg').forEach((media, index) => {
    if (media.closest('a')) return;
    let container = media.closest('figure');
    if (!container) {
      container = document.createElement('span');
      container.className = 'standalone-media';
      media.before(container);
      container.append(media);
    }
    container.classList.add('resizable-media');
    const source = media.getAttribute('src') || media.outerHTML;
    let hash = 0;
    for (let i = 0; i < source.length; i++) hash = (hash * 31 + source.charCodeAt(i)) | 0;
    const key = index + ':' + (hash >>> 0).toString(36);
    const original = ['width', 'height', 'max-width'].map(name => [name, media.style.getPropertyValue(name), media.style.getPropertyPriority(name)]);
    const label = (media.getAttribute('aria-label') || media.getAttribute('alt') || '图片').replace(/，点击放大$/, '');
    const handle = document.createElement('span');
    handle.className = 'image-resize-handle';
    handle.tabIndex = 0;
    handle.setAttribute('role', 'slider');
    handle.setAttribute('aria-label', '调整图片大小：' + label);
    handle.setAttribute('aria-valuemin', '40');
    handle.setAttribute('aria-valuemax', '100');
    handle.setAttribute('data-export-ui', '');
    handle.title = '拖动调整图片大小；双击恢复';
    handle.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 16 8-8m-3 8 3-3"/></svg>';
    const reset = document.createElement('button');
    reset.className = 'image-size-reset icon-button';
    reset.type = 'button';
    reset.setAttribute('aria-label', '恢复图片大小：' + label);
    reset.setAttribute('data-export-ui', '');
    reset.title = '恢复图片大小';
    reset.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 10a9 9 0 1 1 2.8 8.5M3 4v6h6"/></svg>';
    container.append(handle, reset);
    let percent = 100, drag;
    const positionControls = () => {
      if (!media.getClientRects().length) return;
      const frame = container.getBoundingClientRect(), box = media.getBoundingClientRect();
      const scale = frame.width / container.offsetWidth;
      if (!scale) return;
      const right = Math.max(0, 100 - (box.right - frame.left) / frame.width * 100);
      handle.style.right = right + '%';
      handle.style.top = (box.bottom - frame.top) / scale - 24 + 'px';
      reset.style.right = 'calc(' + right + '% + 30px)';
      reset.style.top = (box.bottom - frame.top) / scale - 25 + 'px';
    };
    const updateState = () => {
      handle.setAttribute('aria-valuenow', String(percent));
      handle.setAttribute('aria-valuetext', percent + '%');
      reset.hidden = percent === 100;
      positionControls();
    };
    const setSize = value => {
      percent = Math.max(40, Math.min(100, Math.round(value)));
      media.style.width = percent + '%';
      media.style.height = 'auto';
      media.style.maxWidth = '100%';
      updateState();
    };
    const resetSize = () => {
      original.forEach(([name, value, priority]) => {
        if (value) media.style.setProperty(name, value, priority);
        else media.style.removeProperty(name);
      });
      percent = 100;
      delete saved[key];
      persist();
      updateState();
      handle.focus({preventScroll: true});
    };
    if (Number.isFinite(saved[key])) setSize(saved[key]);
    else updateState();
    const observer = new ResizeObserver(positionControls);
    observer.observe(media);
    observer.observe(container);
    reset.addEventListener('click', resetSize);
    handle.addEventListener('dblclick', resetSize);
    handle.addEventListener('pointerdown', event => {
      if (event.button !== 0) return;
      event.preventDefault();
      handle.focus({preventScroll: true});
      const style = getComputedStyle(container);
      const box = media.getBoundingClientRect();
      drag = {id: event.pointerId, x: event.clientX, y: event.clientY, width: box.width, height: box.height,
        available: (container.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight)) * container.getBoundingClientRect().width / container.offsetWidth, percent};
      handle.setPointerCapture(event.pointerId);
      container.classList.add('is-resizing');
    });
    handle.addEventListener('pointermove', event => {
      if (!drag || event.pointerId !== drag.id) return;
      const dx = event.clientX - drag.x;
      const dy = (event.clientY - drag.y) * drag.width / drag.height;
      const delta = Math.abs(dx) >= Math.abs(dy) ? dx : dy;
      setSize((drag.width + delta) / drag.available * 100);
    });
    const finishDrag = event => {
      if (!drag || event.pointerId !== drag.id) return;
      if (event.type === 'pointercancel') setSize(drag.percent);
      else { saved[key] = percent; persist(); }
      drag = null;
      container.classList.remove('is-resizing');
    };
    handle.addEventListener('pointerup', finishDrag);
    handle.addEventListener('pointercancel', finishDrag);
    handle.addEventListener('keydown', event => {
      let value;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') value = percent - 4;
      if (event.key === 'ArrowRight' || event.key === 'ArrowUp') value = percent + 4;
      if (event.key === 'Home') value = 40;
      if (event.key === 'End') value = 100;
      if (value === undefined) return;
      event.preventDefault();
      setSize(value);
      saved[key] = percent;
      persist();
    });
  });
})();
