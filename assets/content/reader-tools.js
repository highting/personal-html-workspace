(() => {
  const article = document.querySelector('.prose');
  if (!article) return;
  const root = document.documentElement;
  const width = document.getElementById('reading-width');
  const widthValue = document.getElementById('reading-width-value');
  try {
    const saved = localStorage.getItem('content-reading-width-percent');
    if (saved && Number.isFinite(Number(saved))) width.value = saved;
  } catch (_) {}
  const applyWidth = () => {
    root.style.setProperty('--reading-width-ratio', Number(width.value) / 100);
    widthValue.textContent = width.value + '%';
    width.setAttribute('aria-valuetext', '页面宽度的 ' + width.value + '%');
    window.updateContentTocLayout();
  };
  applyWidth();
  let dragAnchor;
  width.addEventListener('pointerdown', () => { dragAnchor = window.captureContentPosition(); });
  addEventListener('pointerup', () => { dragAnchor = undefined; });
  addEventListener('pointercancel', () => { dragAnchor = undefined; });
  const updateWidth = () => {
    window.preserveContentPosition(applyWidth, dragAnchor);
    try { localStorage.setItem('content-reading-width-percent', width.value); } catch (_) {}
  };
  width.addEventListener('input', updateWidth);
  document.getElementById('reset-reading-width').addEventListener('click', () => {
    width.value = '60';
    updateWidth();
  });
  document.getElementById('print-article').addEventListener('click', () => window.print());
  let printDetails;
  addEventListener('beforeprint', () => {
    if (printDetails) return;
    printDetails = [...article.querySelectorAll('details')].map(node => [node, node.open]);
    printDetails.forEach(([node]) => { node.open = true; });
  });
  addEventListener('afterprint', () => {
    printDetails?.forEach(([node, open]) => { node.open = open; });
    printDetails = null;
  });

})();
