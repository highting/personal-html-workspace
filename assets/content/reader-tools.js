(() => {
  const article = document.querySelector('.prose');
  if (!article) return;
  const root = document.documentElement;
  const createDialog = (label, markup, opener) => {
    const dialog = document.createElement('dialog');
    dialog.className = 'reader-dialog';
    dialog.setAttribute('aria-label', label);
    dialog.innerHTML = `<header><h2>${label}</h2><button data-close aria-label="关闭${label}">关闭</button></header>${markup}`;
    document.body.append(dialog);
    dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener('close', () => {
      opener.focus({preventScroll: true});
    });
    dialog.addEventListener('keydown', event => {
      if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); dialog.close(); }
    });
    opener.addEventListener('click', () => dialog.showModal());
    return dialog;
  };
  const settings = createDialog('阅读设置', '<label class="setting-row">正文宽度<select id="reading-width"><option value="standard">标准</option><option value="wide">宽阔</option></select></label><div class="setting-row"><span>打印与保存 PDF</span><button id="print-article">打印</button></div><p class="help">Ctrl / ⌘ + F 使用浏览器查找；Esc 关闭弹窗。打印会展开补充内容和完整代码，动画保留完整步骤。</p>', document.getElementById('reader-settings'));
  const width = settings.querySelector('#reading-width');
  try { if (localStorage.getItem('content-reading-width') === 'wide') width.value = 'wide'; } catch (_) {}
  root.dataset.readingWidth = width.value;
  width.addEventListener('change', () => {
    window.preserveContentPosition(() => { root.dataset.readingWidth = width.value; });
    try { localStorage.setItem('content-reading-width', width.value); } catch (_) {}
  });
  settings.querySelector('#print-article').addEventListener('click', () => { settings.close(); window.print(); });
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
