(() => {
  if (document.documentElement.hasAttribute('data-editor-preview')) return;

  // 在阅读脚本和 KaTeX 增强 DOM 之前捕获模板；编辑模型始终使用原始正文。
  const originalHtml = '<!doctype html>\n' + document.documentElement.outerHTML;
  const editorScript = document.getElementById('content-editor-runtime').textContent;
  const editorStyle = document.getElementById('content-editor-style').textContent;
  const parse = html => new DOMParser().parseFromString(html, 'text/html');
  const keySelector = key => '[data-editor-key="' + key + '"]';
  const candidates = 'h1,h2,h3,h4,h5,h6,p,li,blockquote,figure,figcaption,div,section,aside,table,td,th,ul,ol,details,summary,pre,img,svg';
  const voidTags = new Set(['IMG', 'SVG', 'TABLE', 'UL', 'OL', 'DETAILS', 'FIGURE', 'PRE']);
  let session;

  function region(doc) {
    return doc.querySelector('.prose') || doc.querySelector('.slide-stage');
  }

  function roots(doc) {
    return [...doc.querySelectorAll('.article-header, .prose, .slide-body')];
  }

  function payload(doc) {
    const node = doc.getElementById('content-authoring-data');
    return node ? JSON.parse(node.textContent) : null;
  }

  function writePayload(doc) {
    const previous = payload(doc);
    const title = doc.querySelector('.article-header h1')?.textContent || doc.title;
    doc.title = title;
    const footerTitle = doc.querySelector('.article-footer > span');
    if (footerTitle) footerTitle.textContent = title;
    const scene = doc.body.classList.contains('scene-report') ? 'report' :
      doc.body.classList.contains('scene-blog') ? 'blog' : 'learning';
    const data = {
      version: 1, scene,
      metadata: {...previous?.metadata, title},
      documentId: doc.body.dataset.documentId || previous?.documentId || '',
      body: region(doc).innerHTML,
      header: doc.querySelector('.article-header')?.innerHTML || ''
    };
    let node = doc.getElementById('content-authoring-data');
    if (!node) {
      node = doc.createElement('script');
      node.id = 'content-authoring-data';
      node.type = 'application/json';
      doc.body.append(node);
    }
    node.textContent = JSON.stringify(data).replace(/</g, '\\u003c');
  }

  function prepareDocument(html) {
    const doc = parse(html);
    if (!region(doc) || !doc.body.matches('.scene-learning, .scene-blog, .scene-report')) {
      throw new Error('请选择本项目生成的学习、博客或汇报 HTML。');
    }
    const data = payload(doc);
    if (data) {
      if (data.version !== 1 || typeof data.body !== 'string') throw new Error('不支持此编辑稿格式。');
    }
    // 文件正文是冷启动的原始结构，也可能在生成后由其他工具修订；不要用旧 payload 覆盖它。
    // 旧成品通过独立入口打开后，也会得到相同的离线编辑能力。
    doc.getElementById('content-editor-style')?.remove();
    const style = doc.createElement('style');
    style.id = 'content-editor-style';
    style.textContent = editorStyle;
    doc.head.append(style);
    doc.getElementById('content-editor-runtime')?.remove();
    const script = doc.createElement('script');
    script.id = 'content-editor-runtime';
    script.textContent = editorScript;
    const runtime = [...doc.body.children].find(node => node.tagName === 'SCRIPT' && !node.type);
    if (runtime) runtime.id = 'content-runtime';
    doc.body.insertBefore(script, runtime || null);
    if (!doc.getElementById('edit-page')) {
      const button = doc.createElement('button');
      button.id = 'edit-page';
      button.type = 'button';
      button.textContent = '编辑';
      button.title = '编辑文字、样式和图片';
      button.setAttribute('data-export-ui', '');
      (doc.querySelector('.toolbar .tools') || doc.body).append(button);
    }
    writePayload(doc);
    return doc;
  }

  function start(html, filename, initialView) {
    const model = prepareDocument(html);
    session?.destroy();
    session = createEditor(model, filename, initialView);
  }

  function createEditor(model, filename, initialView) {
    let nextKey = 0, selected = '', activeText = null, editing = true, loading = false, imageLoading = false;
    let revision = 0, savedRevision = 0, serial = 0, position = 0, renderSerial = 0;
    const history = [], originalStyles = new Map();
    const shell = document.createElement('section');
    shell.className = 'content-editor';
    shell.setAttribute('role', 'dialog');
    shell.setAttribute('aria-modal', 'true');
    shell.setAttribute('aria-label', '网页编辑器');
    shell.setAttribute('data-export-ui', '');
    shell.innerHTML = '<header class="ce-topbar"><strong class="ce-title">网页编辑</strong>' +
      '<span class="ce-state" role="status">尚未修改</span>' +
      '<button data-action="undo" title="撤销（Ctrl+Z）">撤销</button><button data-action="redo" title="重做（Ctrl+Shift+Z）">重做</button>' +
      '<button data-action="preview">预览</button><button class="ce-primary" data-action="save">另存 HTML</button>' +
      '<button data-action="close">关闭</button></header>' +
      '<div class="ce-canvas"><iframe title="可编辑网页" sandbox="allow-scripts allow-same-origin allow-downloads allow-modals"></iframe><div class="ce-loading">正在载入网页…</div></div>' +
      '<aside class="ce-inspector"><h2>选择一个元素</h2><p class="ce-selection">单击选择，双击修改普通文字。</p>' +
      '<div class="ce-row"><button data-action="parent">选择外层</button><button data-action="text">修改文字</button></div>' +
      '<h3>文字与布局</h3><div class="ce-fields">' +
      '<label>字号 · px<input data-style="font-size" data-unit="px" type="number" min="8" max="160" placeholder="默认"></label>' +
      '<label>宽度 · %<input data-style="width" data-unit="%" type="number" min="10" max="100" placeholder="自动"></label>' +
      '<label>文字颜色<input data-style="color" type="color"></label>' +
      '<label>背景颜色<input data-style="background-color" type="color"></label>' +
      '<label>上间距 · px<input data-style="margin-top" data-unit="px" type="number" min="0" max="200" placeholder="默认"></label>' +
      '<label>下间距 · px<input data-style="margin-bottom" data-unit="px" type="number" min="0" max="200" placeholder="默认"></label>' +
      '<label>内边距 · px<input data-style="padding" data-unit="px" type="number" min="0" max="160" placeholder="默认"></label>' +
      '<label>对齐<select data-style="text-align"><option value="">默认</option><option value="left">左对齐</option><option value="center">居中</option><option value="right">右对齐</option></select></label></div>' +
      '<div class="ce-row"><button data-action="reset-style">还原本次样式</button></div>' +
      '<label class="ce-file" hidden>替换图片<input id="editor-image-file" type="file" accept="image/png,image/jpeg,image/webp,image/gif,image/svg+xml"></label>' +
      '<h3>内容块</h3><div class="ce-row"><button data-action="up">上移</button><button data-action="down">下移</button><button data-action="delete">删除</button></div>' +
      '<p class="ce-notice" role="status">修改保存在当前编辑会话中，请用“另存 HTML”保留。</p></aside>';
    document.body.append(shell);
    const background = [...document.body.children].filter(node => node !== shell).map(node => [node, node.inert]);
    background.forEach(([node]) => { node.inert = true; });
    const frame = shell.querySelector('iframe');
    const status = shell.querySelector('.ce-state');
    const notice = shell.querySelector('.ce-notice');
    const source = key => model.querySelector(keySelector(key));
    const live = key => frame.contentDocument?.querySelector(keySelector(key));
    const button = action => shell.querySelector('[data-action="' + action + '"]');
    const fields = [...shell.querySelectorAll('[data-style]')];
    const lockedRoots = node => node?.matches('.prose, .article-header, .slide-body');
    const canSelect = node => node?.dataset.editorKey && !lockedRoots(node);
    const parentSource = node => node?.parentElement.closest('[data-editor-key]');

    function assignKeys() {
      roots(model).forEach(root => {
        [root, ...root.querySelectorAll(candidates)].forEach(node => {
          if (node.closest('svg') && node.tagName.toLowerCase() !== 'svg') return;
          if (!node.dataset.editorKey) node.dataset.editorKey = 'e' + (++nextKey);
          if (!originalStyles.has(node.dataset.editorKey)) originalStyles.set(node.dataset.editorKey, node.getAttribute('style'));
        });
      });
    }

    function textAllowed(node) {
      if (!node || voidTags.has(node.tagName) || node.closest('.code-block, pre, svg')) return false;
      if (node.querySelector('img,svg,code,pre,table,button,input,textarea,select,script,style,iframe,math')) return false;
      if (node.querySelector('p,div,section,li,ul,ol,figure,details')) return false;
      return !/\\[([]|\$\$/.test(node.textContent);
    }

    function selectedImage(node) {
      if (!node) return null;
      const images = node.matches('img') ? [node] : [...node.querySelectorAll('img')];
      return images.length === 1 ? images[0] : null;
    }

    function colorHex(value) {
      const rgb = value.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      return rgb ? '#' + rgb.slice(1).map(n => Number(n).toString(16).padStart(2, '0')).join('') : '#ffffff';
    }

    function updatePanel() {
      const node = source(selected), view = live(selected);
      shell.querySelector('.ce-inspector h2').textContent = node ? '已选元素' : '选择一个元素';
      shell.querySelector('.ce-selection').textContent = node ?
        (node.matches('figure') ? '图与图注' : node.tagName.toLowerCase()) + ' · ' + (node.textContent.trim().slice(0, 50) || '图片 / 图形') :
        '单击选择，双击修改普通文字。';
      fields.forEach(input => {
        input.disabled = !node || loading;
        if (!node || !view) { if (input.type !== 'color') input.value = ''; return; }
        const name = input.dataset.style;
        const current = node.style.getPropertyValue(name);
        const computed = frame.contentWindow.getComputedStyle(view).getPropertyValue(name);
        if (input.type === 'color') {
          const transparent = name === 'background-color' && computed === 'rgba(0, 0, 0, 0)';
          input.value = colorHex(transparent ? frame.contentWindow.getComputedStyle(frame.contentDocument.body).backgroundColor : computed);
          input.title = transparent ? '当前背景透明，选择颜色后设为实色' : '';
        }
        else if (input.tagName === 'SELECT') input.value = current;
        else input.value = current.endsWith(input.dataset.unit) ? parseFloat(current) : '';
        if (input.type === 'number' && name !== 'width') input.placeholder = String(Math.round(parseFloat(computed)) || 0);
      });
      button('parent').disabled = !canSelect(parentSource(node));
      button('text').disabled = !textAllowed(node) || loading;
      ['up', 'down', 'delete', 'reset-style'].forEach(action => { button(action).disabled = !node || loading; });
      button('up').disabled ||= !node?.previousElementSibling?.dataset.editorKey;
      button('down').disabled ||= !node?.nextElementSibling?.dataset.editorKey;
      // 标题区保留结构；正文与每页中的内容块可以增减位置。
      button('delete').disabled ||= !!node?.closest('.article-header') || node?.matches('td,th,summary');
      button('up').disabled ||= !!node?.closest('.article-header') || node?.matches('td,th,summary');
      button('down').disabled ||= !!node?.closest('.article-header') || node?.matches('td,th,summary');
      shell.querySelector('.ce-file').hidden = !selectedImage(node);
      button('undo').disabled = position === 0;
      button('redo').disabled = position === history.length;
      button('save').disabled = imageLoading;
      status.textContent = imageLoading ? '正在载入图片…' :
        revision !== savedRevision ? '有未保存的修改' : savedRevision ? '已导出副本' : '尚未修改';
    }

    function select(key) {
      frame.contentDocument?.querySelectorAll('[data-editor-selected]').forEach(n => n.removeAttribute('data-editor-selected'));
      selected = canSelect(source(key)) ? key : '';
      if (selected && editing) live(selected)?.setAttribute('data-editor-selected', '');
      updatePanel();
    }

    function viewState() {
      const doc = frame.contentDocument;
      const slides = doc ? [...doc.querySelectorAll('[data-export-page]')] : [];
      return {x: frame.contentWindow?.scrollX || 0, y: frame.contentWindow?.scrollY || 0,
        slide: Math.max(0, slides.findIndex(slide => !slide.hidden)),
        theme: doc?.documentElement.dataset.theme, palette: doc?.documentElement.dataset.palette};
    }

    function exportDocument(preview = false) {
      const doc = model.cloneNode(true);
      if (preview) {
        doc.documentElement.setAttribute('data-editor-preview', '');
      } else {
        doc.querySelectorAll('[data-editor-key]').forEach(node => node.removeAttribute('data-editor-key'));
      }
      writePayload(doc);
      return '<!doctype html>\n' + doc.documentElement.outerHTML;
    }

    async function render(view = viewState()) {
      const ticket = ++renderSerial;
      assignKeys();
      loading = true;
      shell.querySelector('.ce-loading').hidden = false;
      updatePanel();
      frame.onload = async () => {
        const doc = frame.contentDocument, win = frame.contentWindow;
        await doc.fonts.ready;
        await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
        if (ticket !== renderSerial) return;
        if (view.theme) win.setContentTheme?.(view.theme);
        if (view.palette) win.setContentPalette?.(view.palette);
        const syncTheme = () => { shell.dataset.editorTheme = doc.documentElement.dataset.theme; };
        syncTheme();
        new win.MutationObserver(syncTheme).observe(doc.documentElement, {attributes: true, attributeFilter: ['data-theme']});
        const slides = [...doc.querySelectorAll('[data-export-page]')];
        if (slides.length && view.slide) doc.querySelectorAll('#toc-links a')[Math.min(view.slide, slides.length - 1)]?.click();
        win.scrollTo(view.x, view.y);
        doc.getElementById('edit-page')?.addEventListener('click', () => setEditing(true));
        doc.addEventListener('click', choose, true);
        doc.addEventListener('dblclick', doubleClick, true);
        doc.addEventListener('keydown', keydown, true);
        doc.documentElement.toggleAttribute('data-editor-active', editing);
        if (editing) doc.querySelectorAll('.prose details').forEach(node => { node.open = true; });
        loading = false;
        shell.querySelector('.ce-loading').hidden = true;
        select(selected);
        const slideBody = doc.querySelector('.slide:not([hidden]) .slide-body');
        if (slideBody && slideBody.scrollHeight > slideBody.clientHeight + 2) {
          notice.textContent = '当前页内容超出可见区域，请缩短文字或调整尺寸、间距后再保存。';
        }
      };
      frame.srcdoc = exportDocument(true);
    }

    function commit(command) {
      command.beforeRevision = revision;
      command.afterRevision = ++serial;
      command.redo();
      history.splice(position);
      history.push(command);
      if (history.length > 80) history.shift();
      position = history.length;
      revision = command.afterRevision;
      render();
    }

    function attribute(key, name, value) {
      const before = source(key).getAttribute(name);
      if (before === value) return;
      const apply = next => { const node = source(key); if (next === null) node.removeAttribute(name); else node.setAttribute(name, next); };
      commit({undo: () => apply(before), redo: () => apply(value)});
    }

    function finishText() {
      if (!activeText) return false;
      const {key, node, before} = activeText;
      activeText = null;
      node.removeAttribute('contenteditable');
      const next = node.innerHTML;
      if (before !== next) {
        const apply = html => { source(key).innerHTML = html; };
        commit({undo: () => apply(before), redo: () => apply(next)});
        return true;
      }
      return false;
    }

    function beginText() {
      const node = source(selected), view = live(selected);
      if (!textAllowed(node) || !view) {
        notice.textContent = '公式、代码和图形按整体调整；普通文字可以双击修改。';
        return;
      }
      if (activeText?.key === selected) return;
      finishText();
      // 去掉标题定位按钮等运行时子节点，只编辑原有的文字与行内标记。
      view.innerHTML = node.innerHTML;
      view.setAttribute('contenteditable', 'plaintext-only');
      view.spellcheck = false;
      activeText = {key: selected, node: view, before: node.innerHTML};
      view.addEventListener('blur', finishText, {once: true});
      view.focus({preventScroll: true});
      notice.textContent = '直接输入文字。Enter 完成，Shift+Enter 换行；另存 HTML 保留修改。';
    }

    function targetKey(event) {
      let node = event.target.closest('[data-editor-key]');
      if (event.target.closest('[data-export-ui], .code-toolbar, .code-expand, .code-wrap')) return '';
      const media = event.target.closest('img,svg');
      if (media) {
        const group = media.closest('figure') || media.closest('p');
        node = group?.dataset.editorKey ? group : node;
      }
      const block = event.target.closest('.code-block');
      if (block?.dataset.editorKey) node = block;
      return node?.dataset.editorKey || '';
    }

    function choose(event) {
      if (!editing || event.target.closest('[contenteditable]')) return;
      const key = targetKey(event);
      if (!canSelect(source(key))) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      if (activeText) finishText();
      select(key);
    }

    function doubleClick(event) {
      if (!editing || activeText) return;
      const key = targetKey(event);
      if (!canSelect(source(key))) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      select(key);
      beginText();
    }

    function setEditing(value) {
      finishText();
      editing = value;
      shell.classList.toggle('ce-preview', !editing);
      button('preview').textContent = editing ? '预览' : '继续编辑';
      frame.contentDocument?.documentElement.toggleAttribute('data-editor-active', editing);
      select(selected);
      // 宽度变化由原页面自己的布局观察器处理。
      if (editing) frame.contentDocument?.querySelectorAll('.prose details').forEach(node => { node.open = true; });
    }

    function move(direction) {
      const node = source(selected);
      const other = direction < 0 ? node.previousElementSibling : node.nextElementSibling;
      if (!other?.dataset.editorKey) return;
      const key = selected, otherKey = other.dataset.editorKey;
      const swap = () => {
        const a = source(key), b = source(otherKey);
        if (a.nextElementSibling === b) b.after(a); else b.before(a);
      };
      commit({undo: swap, redo: swap});
    }

    function remove() {
      const node = source(selected), parentKey = node.parentElement.dataset.editorKey;
      const key = selected, html = node.outerHTML, next = node.nextElementSibling?.dataset.editorKey;
      if (!parentKey) return;
      commit({
        redo: () => source(key).remove(),
        undo: () => {
          const fragment = model.createElement('template');
          fragment.innerHTML = html;
          source(parentKey).insertBefore(fragment.content.firstElementChild, next ? source(next) : null);
          selected = key;
        }
      });
    }

    function save() {
      if (imageLoading) { notice.textContent = '图片正在载入，完成后再保存。'; return; }
      finishText();
      const blob = new Blob([exportDocument()], {type: 'text/html;charset=utf-8'});
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      const name = (filename || model.title || '网页').replace(/\.html?$/i, '').replace(/-编辑$/, '');
      link.download = name.replace(/[\\/:*?"<>|]/g, '-') + '-编辑.html';
      link.href = url;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 30000);
      savedRevision = revision;
      updatePanel();
      notice.textContent = '已发起下载。请保留下载的 HTML；重新打开仍可继续编辑。';
    }

    function action(name) {
      if (name !== 'text' && activeText) finishText();
      if (name === 'save') { save(); return; }
      if (name === 'preview') { setEditing(!editing); return; }
      if (name === 'close') {
        if (revision !== savedRevision && !confirm('尚有未保存的修改。关闭编辑会放弃这些修改，是否关闭？')) return;
        destroy(); return;
      }
      if (name === 'undo' && position) {
        const command = history[--position];
        command.undo(); revision = command.beforeRevision; render(); return;
      }
      if (name === 'redo' && position < history.length) {
        const command = history[position++];
        command.redo(); revision = command.afterRevision; render(); return;
      }
      if (loading) return;
      const node = source(selected);
      if (!node) return;
      if (name === 'parent') select(parentSource(node)?.dataset.editorKey);
      if (name === 'text') beginText();
      if (name === 'reset-style') attribute(selected, 'style', originalStyles.get(selected));
      if (name === 'up' || name === 'down') move(name === 'up' ? -1 : 1);
      if (name === 'delete') remove();
    }

    function keydown(event) {
      const input = event.target.closest('input,textarea,select,[contenteditable]');
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
        event.preventDefault(); event.stopImmediatePropagation(); save(); return;
      }
      if (input) {
        if (activeText && event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
          event.preventDefault(); event.stopImmediatePropagation(); finishText();
        }
        if (activeText && event.key === 'Escape') {
          event.preventDefault(); event.stopImmediatePropagation(); finishText();
        }
        return;
      }
      const key = event.key.toLowerCase();
      let name;
      if ((event.ctrlKey || event.metaKey) && key === 'z') name = event.shiftKey ? 'redo' : 'undo';
      if ((event.ctrlKey || event.metaKey) && key === 'y') name = 'redo';
      if (editing && key === 'delete') name = 'delete';
      if (editing && key === 'enter') name = 'text';
      if (name && !button(name).disabled) {
        event.preventDefault(); event.stopImmediatePropagation(); action(name);
      }
    }

    shell.addEventListener('click', event => {
      const control = event.target.closest('[data-action]');
      if (control && !control.disabled) action(control.dataset.action);
    });
    fields.forEach(input => input.addEventListener('change', () => {
      if (!selected || loading || !input.checkValidity()) return;
      const node = source(selected), copy = node.cloneNode(false);
      const value = input.value ? input.value + (input.dataset.unit || '') : '';
      if (value) copy.style.setProperty(input.dataset.style, value);
      else copy.style.removeProperty(input.dataset.style);
      attribute(selected, 'style', copy.getAttribute('style'));
    }));
    shell.querySelector('#editor-image-file').addEventListener('change', async event => {
      const file = event.target.files[0], node = selectedImage(source(selected));
      if (!file || !node) return;
      const key = node.dataset.editorKey, selection = selected;
      if (!/^image\/(png|jpeg|webp|gif|svg\+xml)$/.test(file.type)) {
        notice.textContent = '请选择 PNG、JPEG、WebP、GIF 或 SVG 图片。'; return;
      }
      const reader = new FileReader();
      imageLoading = true;
      updatePanel();
      reader.onload = async () => {
        const probe = new Image();
        probe.src = reader.result;
        try { await probe.decode(); }
        catch {
          imageLoading = false; updatePanel();
          notice.textContent = '图片无法读取，请选择其他文件。'; return;
        }
        imageLoading = false;
        updatePanel();
        if (!source(key) || selected !== selection) {
          notice.textContent = '所选元素已改变，图片未替换。'; return;
        }
        const before = source(key).getAttribute('src'), srcset = source(key).getAttribute('srcset');
        const apply = (src, sizes) => {
          const image = source(key);
          image.setAttribute('src', src);
          if (sizes === null) image.removeAttribute('srcset'); else image.setAttribute('srcset', sizes);
        };
        commit({undo: () => apply(before, srcset), redo: () => apply(reader.result, null)});
        notice.textContent = '图片已嵌入网页；另存后无需单独携带图片文件。';
      };
      reader.onerror = () => { imageLoading = false; updatePanel(); notice.textContent = '图片读取失败，请重试。'; };
      reader.readAsDataURL(file);
      event.target.value = '';
    });
    const beforeUnload = event => {
      if (activeText || imageLoading || revision !== savedRevision) { event.preventDefault(); event.returnValue = ''; }
    };
    addEventListener('beforeunload', beforeUnload);
    shell.addEventListener('keydown', keydown, true);
    function destroy() {
      renderSerial++;
      removeEventListener('beforeunload', beforeUnload);
      background.forEach(([node, inert]) => { node.inert = inert; });
      shell.remove();
      document.getElementById('edit-page')?.focus({preventScroll: true});
    }
    assignKeys();
    render(initialView || {x: 0, y: 0, slide: 0});
    button('preview').focus();
    return {destroy};
  }

  const opener = document.getElementById('open-edit-document');
  opener?.addEventListener('change', async () => {
    const file = opener.files[0];
    if (!file) return;
    const status = document.getElementById('editor-open-status');
    try {
      start(await file.text(), file.name);
      status.textContent = '';
    } catch (error) { status.textContent = error.message; }
    opener.value = '';
  });
  document.getElementById('edit-page')?.addEventListener('click', () => {
    // 启动快照早于后续阅读脚本的解析，此时补回完整脚本文本。
    const original = parse(originalHtml);
    if (!original.getElementById('content-runtime')) {
      const runtime = document.getElementById('content-runtime');
      if (runtime) original.body.append(runtime.cloneNode(true));
    }
    const slides = [...document.querySelectorAll('[data-export-page]')];
    start('<!doctype html>\n' + original.documentElement.outerHTML, document.title, {x: scrollX, y: scrollY,
      slide: Math.max(0, slides.findIndex(slide => !slide.hidden)),
      theme: document.documentElement.dataset.theme, palette: document.documentElement.dataset.palette});
  });
})();
