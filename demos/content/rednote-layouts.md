---
math: katex
---

<div class="card-page">
<h1>均值相同，<br>数据未必相似</h1>
<p class="card-lead">A 组是 2、4、6，B 组是 0、4、8。它们的均值都是 4，但散开的程度不同。</p>
<figure>
<svg viewBox="0 0 900 410" role="img" aria-label="A组在2、4、6，B组在0、4、8，共用0到8的数轴">
<path d="M110 130H810M110 290H810" fill="none" stroke="var(--node-line)" stroke-width="2"/>
<path d="M460 54V330" fill="none" stroke="var(--muted)" stroke-width="2" stroke-dasharray="6 9"/>
<g style="font-size:38px"><text x="0" y="142" style="font-size:38px">A</text><text x="0" y="302" style="font-size:38px">B</text><text x="488" y="62" style="font-size:36px">均值 4</text></g>
<g fill="var(--accent)"><circle cx="285" cy="130" r="15"/><circle cx="460" cy="130" r="15"/><circle cx="635" cy="130" r="15"/></g>
<g fill="var(--compare)"><circle cx="110" cy="290" r="15"/><circle cx="460" cy="290" r="15"/><circle cx="810" cy="290" r="15"/></g>
<g text-anchor="middle"><text x="110" y="385" style="font-size:36px">0</text><text x="285" y="385" style="font-size:36px">2</text><text x="460" y="385" style="font-size:36px">4</text><text x="635" y="385" style="font-size:36px">6</text><text x="810" y="385" style="font-size:36px">8</text></g>
</svg>
<figcaption>教学数据。两行共用尺度，虚线标出相同的均值。</figcaption>
</figure>
<p class="card-claim"><strong>均值保留了中心，却没有保留数据散开的程度。</strong></p>
</div>

<div class="card-page">
<h2>把中心和离散分开看</h2>
<p>两组数的总和都是 12，数量都是 3，所以均值同为 \(12/3=4\)。再比较最大值与最小值之差：</p>
<div class="card-comparison">
<div><h3>A 组</h3><p>2，4，6</p><p>极差：6 − 2 = 4</p><p>最远偏离均值 2。</p></div>
<div><h3>B 组</h3><p>0，4，8</p><p>极差：8 − 0 = 8</p><p>最远偏离均值 4。</p></div>
</div>
<p>在这组数里，B 的两端离中心更远。这个差别在平均数中消失了，却能从原始点和极差中看出来。</p>
<p class="card-claim">极差只看两端。它能帮助发现差别，也不能代替完整分布。</p>
</div>

<div class="card-page">
<h2>遇到平均数，继续问三件事</h2>
<p>先看这个数字回答了什么，再补足它没有告诉你的信息。</p>
<ol class="card-steps">
<li><strong>数据围绕哪里？</strong><p>先明确均值表示的中心。这个例子里，两组都是 4。</p></li>
<li><strong>数据散得多开？</strong><p>把原始点画在同一尺度上，再结合合适的离散指标。</p></li>
<li><strong>比较条件一致吗？</strong><p>核对样本数量、单位和统计口径，避免把不同问题混在一起。</p></li>
</ol>
<p class="card-claim"><strong>看均值，也看它背后的数据。</strong></p>
</div>
