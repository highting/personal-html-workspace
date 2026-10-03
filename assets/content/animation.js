(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('figure[data-animation]').forEach(figure => {
    const steps = [...figure.querySelectorAll('svg > [data-step]')];
    if (steps.length < 2) return;
    const controls = document.createElement('div');
    controls.className = 'animation-controls';
    controls.setAttribute('data-export-ui', '');
    controls.innerHTML = '<button data-play>播放</button><button data-previous aria-label="上一步">←</button><input type="range" min="1" aria-label="动画步骤"><button data-next aria-label="下一步">→</button><button data-reset>重置</button><button data-all>完整图</button>';
    const status = document.createElement('div');
    status.className = 'animation-status';
    status.setAttribute('role', 'status');
    const play = controls.querySelector('[data-play]');
    const slider = controls.querySelector('input');
    slider.max = steps.length;
    const previous = controls.querySelector('[data-previous]');
    const next = controls.querySelector('[data-next]');
    figure.append(controls, status);
    let current = steps.length - 1, timer;
    const stop = () => { clearInterval(timer); timer = null; play.textContent = '播放'; play.setAttribute('aria-pressed', 'false'); };
    const show = index => {
      current = index;
      steps.forEach((node, at) => { node.style.opacity = at <= index ? '1' : '.16'; });
      slider.value = index + 1;
      previous.disabled = index === 0; next.disabled = index === steps.length - 1;
      status.textContent = `${index + 1} / ${steps.length} · ${steps[index].dataset.caption || '步骤 ' + (index + 1)}`;
      figure.dataset.currentStep = index + 1;
    };
    play.addEventListener('click', () => {
      if (timer) { stop(); return; }
      if (current === steps.length - 1) show(0);
      play.textContent = '暂停'; play.setAttribute('aria-pressed', 'true');
      timer = setInterval(() => {
        show(current + 1);
        if (current === steps.length - 1) stop();
      }, 1600);
    });
    previous.addEventListener('click', () => { stop(); show(Math.max(0, current - 1)); });
    next.addEventListener('click', () => { stop(); show(Math.min(steps.length - 1, current + 1)); });
    slider.addEventListener('input', () => { stop(); show(Number(slider.value) - 1); });
    controls.querySelector('[data-reset]').addEventListener('click', () => { stop(); show(0); });
    controls.querySelector('[data-all]').addEventListener('click', () => { stop(); show(steps.length - 1); });
    const pause = () => { stop(); };
    document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
    new IntersectionObserver(entries => { if (!entries[0].isIntersecting) pause(); }).observe(figure);
    reduced.addEventListener('change', () => { stop(); show(steps.length - 1); });
    let beforePrint;
    addEventListener('beforeprint', () => { if (beforePrint === undefined) beforePrint = current; stop(); show(steps.length - 1); });
    addEventListener('afterprint', () => { if (beforePrint !== undefined) show(beforePrint); beforePrint = undefined; });
    document.addEventListener('content-export', () => { stop(); show(steps.length - 1); });
    // 默认完整静态图，不自动循环；减少动态效果偏好下也可手动逐步阅读。
    stop(); show(steps.length - 1);
    figure.querySelector('svg').addEventListener('click', stop);
    figure.querySelector('svg').addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') stop(); });
  });
})();
