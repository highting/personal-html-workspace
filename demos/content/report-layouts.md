---
title: 均值与分布
cover: true
---

# 均值相同，分布仍然不同

<p class="report-lead">用两组数，分开看中心位置与离散程度。</p>

<!-- notes: 本组数字为教学构造。A组是2、4、6，B组是0、4、8。两组均值都是4，但相对均值的偏离不同。 -->

---

## 均值给出相同的中心位置

<div class="report-table-layout">
<div><table><thead><tr><th>指标</th><th class="report-value">A 组</th><th class="report-value">B 组</th></tr></thead><tbody><tr><td>数据</td><td class="report-value">2，4，6</td><td class="report-value">0，4，8</td></tr><tr><td>总和</td><td class="report-value">12</td><td class="report-value">12</td></tr><tr><td>数量</td><td class="report-value">3</td><td class="report-value">3</td></tr><tr class="report-highlight"><td>均值</td><td class="report-value">4</td><td class="report-value">4</td></tr></tbody></table><p class="report-detail">教学数据；每个数等权计入。</p></div>
</div>

<!-- notes: 先核对两个和都为12，再除以3。强调均值相等是确定事实，但它不能单独说明两组数据的分布相同。 -->

---

## 同一坐标下，B 组更分散

<figure class="report-figure">
<svg style="font-family:var(--default-font)" viewBox="0 0 1080 330" role="img" aria-label="A组2、4、6，极差4；B组0、4、8，极差8。两组共用0到8的尺度，均值4。">
<path d="M180 95H1000M180 240H1000" fill="none" stroke="var(--line)" stroke-width="2"/>
<path d="M590 42V270" fill="none" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="5 7"/>
<path d="M385 95H795" stroke="var(--accent)" stroke-width="6"/>
<path d="M180 240H1000" stroke="var(--compare)" stroke-width="6"/>
<g fill="var(--text)" font-size="26"><text x="30" y="104">A 组</text><text x="30" y="249">B 组</text><text x="610" y="30">均值 4</text></g>
<g fill="var(--accent)"><circle cx="385" cy="95" r="11"/><circle cx="590" cy="95" r="11"/><circle cx="795" cy="95" r="11"/></g>
<g fill="var(--compare)"><circle cx="180" cy="240" r="11"/><circle cx="590" cy="240" r="11"/><circle cx="1000" cy="240" r="11"/></g>
<g fill="var(--text)" font-size="26" text-anchor="middle"><text x="385" y="76">2</text><text x="590" y="76">4</text><text x="795" y="76">6</text><text x="180" y="221">0</text><text x="590" y="221">4</text><text x="1000" y="221">8</text></g>
<path d="M385 116V139H795V116M180 261V284H1000V261" fill="none" stroke="var(--muted)" stroke-width="1.5"/>
<g fill="var(--text)" font-size="25" text-anchor="middle"><text x="590" y="172">极差 4 · 最远偏离均值 2</text><text x="590" y="320">极差 8 · 最远偏离均值 4</text></g>
</svg>
<figcaption>教学数据 · 两行共用尺度；线段长度表示最大值与最小值之差。</figcaption>
</figure>
<p class="report-detail">极差只看两端；这里同时保留原始点，不将它当作完整的分布描述。</p>

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
