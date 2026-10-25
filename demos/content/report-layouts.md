---
title: 均值与分布
cover: true
---

# 均值相同，分布仍然不同

<p class="report-lead">用两组数，分开看中心位置与离散程度。</p>

<!-- notes: 本组数字为教学构造。A组是2、4、6，B组是0、4、8。两组均值都是4，但相对均值的偏离不同。 -->

---

## 均值给出相同的中心位置

<div class="report-split report-table-layout">
<div><h3>两组均值都是 4</h3><p>总和与数量相同，得到的平均数也相同。</p><p class="report-detail">均值没有保留每个数偏离中心的程度。</p></div>
<div><table><thead><tr><th>指标</th><th class="report-value">A 组</th><th class="report-value">B 组</th></tr></thead><tbody><tr><td>数据</td><td class="report-value">2，4，6</td><td class="report-value">0，4，8</td></tr><tr><td>总和</td><td class="report-value">12</td><td class="report-value">12</td></tr><tr><td>数量</td><td class="report-value">3</td><td class="report-value">3</td></tr><tr class="report-highlight"><td>均值</td><td class="report-value">4</td><td class="report-value">4</td></tr></tbody></table><p class="report-detail">教学数据；每个数等权计入。</p></div>
</div>

<!-- notes: 先核对两个和都为12，再除以3。强调均值相等是确定事实，但它不能单独说明两组数据的分布相同。 -->

---

## 同一坐标下，B 组更分散

<figure class="report-figure">
<svg viewBox="0 0 1080 290" style="height:270px" role="img" aria-label="A组位于2、4、6，B组位于0、4、8；共用0到8的坐标，均值都在4">
<path d="M180 90H1000M180 210H1000" fill="none" stroke="var(--line)" stroke-width="2"/>
<path d="M590 28V248" fill="none" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="5 7"/>
<g fill="var(--text)" font-size="26"><text x="30" y="99">A 组</text><text x="30" y="219">B 组</text><text x="610" y="30">均值 4</text></g>
<g fill="var(--accent)"><circle cx="385" cy="90" r="12"/><circle cx="590" cy="90" r="12"/><circle cx="795" cy="90" r="12"/></g>
<g fill="var(--compare)"><circle cx="180" cy="210" r="12"/><circle cx="590" cy="210" r="12"/><circle cx="1000" cy="210" r="12"/></g>
<g fill="var(--muted)" font-size="24" text-anchor="middle"><text x="180" y="280">0</text><text x="385" y="280">2</text><text x="590" y="280">4</text><text x="795" y="280">6</text><text x="1000" y="280">8</text></g>
</svg>
<figcaption>两行使用相同尺度；虚线标出共同均值。</figcaption>
</figure>
<div class="report-comparison"><div><h3>A 组：极差 4</h3><p>6 − 2 = 4，最远偏离均值 2。</p></div><div><h3>B 组：极差 8</h3><p>8 − 0 = 8，最远偏离均值 4。</p></div></div>

<!-- notes: 图中位置按数值线性映射，没有截轴或错开坐标。极差只使用最大值与最小值，这个例子不把极差当作完整的分布描述。 -->

---

## 比较数据时，分三步看

<div class="report-timeline">
<div><p class="round">01</p><strong>看中心</strong><p>均值回答数据大致围绕哪里。</p></div>
<div><p class="round">02</p><strong>看离散</strong><p>结合原始点与极差，看数据分散到什么程度。</p></div>
<div><p class="round">03</p><strong>看条件</strong><p>确认样本数量、单位与比较口径一致。</p></div>
</div>
<p class="report-takeaway report-rule">一个平均数，不能代替对分布的观察。</p>
<p class="report-detail">这里用极差说明差别；它只反映两端，不能描述分布的全部特征。</p>

<!-- notes: 将这个顺序用于本组教学数据：均值都是4，极差分别是4和8，样本数都为3。真实比较还需要结合数据来源和问题选择统计量。 -->
