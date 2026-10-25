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
<h2>同一尺度，直接看出差距</h2>
<p>两组均值同为 \(12/3=4\)。把最小值与最大值连起来，线段长度就是极差。</p>
<figure>
<svg viewBox="0 0 900 540" role="img" aria-label="共同尺度对照：A组从2到6，极差4；B组从0到8，极差8。虚线为均值4。">
<path d="M110 130H810M110 355H810" fill="none" stroke="var(--node-line)" stroke-width="2"/>
<path d="M460 65V400" fill="none" stroke="var(--muted)" stroke-width="2" stroke-dasharray="6 9"/>
<path d="M285 130H635" stroke="var(--accent)" stroke-width="8"/>
<path d="M110 355H810" stroke="var(--compare)" stroke-width="8"/>
<g><text x="0" y="142" style="font-size:38px">A</text><text x="0" y="367" style="font-size:38px">B</text><text x="488" y="48" style="font-size:36px">均值 4</text></g>
<g fill="var(--accent)"><circle cx="285" cy="130" r="14"/><circle cx="460" cy="130" r="14"/><circle cx="635" cy="130" r="14"/></g>
<g fill="var(--compare)"><circle cx="110" cy="355" r="14"/><circle cx="460" cy="355" r="14"/><circle cx="810" cy="355" r="14"/></g>
<g text-anchor="middle"><text x="285" y="104" style="font-size:38px">2</text><text x="460" y="104" style="font-size:38px">4</text><text x="635" y="104" style="font-size:38px">6</text><text x="110" y="329" style="font-size:38px">0</text><text x="460" y="329" style="font-size:38px">4</text><text x="810" y="329" style="font-size:38px">8</text></g>
<path d="M285 158V185H635V158M110 383V410H810V383" fill="none" stroke="var(--muted)" stroke-width="2"/>
<g text-anchor="middle"><text x="460" y="237" style="font-size:38px">极差 4</text><text x="460" y="462" style="font-size:38px">极差 8</text><text x="460" y="524" style="font-size:36px">B 的范围是 A 的 2 倍</text></g>
</svg>
<figcaption>教学数据；原始点与上一页一致。</figcaption>
</figure>
<p class="card-claim">极差只看两端，不能描述完整分布。</p>
</div>

<div class="card-page">
<h2>遇到平均数，继续问三件事</h2>
<p>先看中心，再看分散程度，最后核对比较条件。</p>
<ol class="card-steps">
<li><strong>数据围绕哪里？</strong><p>两组中心相同，均值都是 4。</p></li>
<li><strong>数据散得多开？</strong><p>共用尺度画原始点，比较离散程度。</p></li>
<li><strong>比较条件一致吗？</strong><p>核对样本数量、单位与统计口径。</p></li>
</ol>
<p class="card-claim"><strong>看均值，也看它背后的数据。</strong></p>
</div>
