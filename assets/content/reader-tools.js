(() => {
  const article = document.querySelector('.prose');
  if (!article) return;
  const root = document.documentElement;
  const width = document.getElementById('reading-width');
  const widthValue = document.getElementById('reading-width-value');
  try {
    const saved = localStorage.getItem('content-reading-width');
    if (saved === 'wide') width.value = '792';
    else if (saved && Number.isFinite(Number(saved))) width.value = saved;
  } catch (_) {}
  const applyWidth = () => {
    root.style.setProperty('--text-width', width.value + 'px');
    widthValue.textContent = width.value + ' px';
    width.setAttribute('aria-valuetext', width.value + ' 像素');
  };
  applyWidth();
  let dragAnchor;
  width.addEventListener('pointerdown', () => { dragAnchor = window.captureContentPosition(); });
  addEventListener('pointerup', () => { dragAnchor = undefined; });
  addEventListener('pointercancel', () => { dragAnchor = undefined; });
  const updateWidth = () => {
    window.preserveContentPosition(applyWidth, dragAnchor);
    try { localStorage.setItem('content-reading-width', width.value); } catch (_) {}
  };
  width.addEventListener('input', updateWidth);
  document.getElementById('reset-reading-width').addEventListener('click', () => {
    width.value = '704';
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
