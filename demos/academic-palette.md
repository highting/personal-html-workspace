# 同组分数的稳定归一化

同一组有限分数共同减去最大值，使求出的指数值不超过1，避开大指数中间量；再归一化为权重，保留原来的元素对应关系。

<div class="figure-scene">
<svg viewBox="0 0 720 600" role="img" aria-label="三个分数减去共同最大值，再求指数并归一化">
<defs><marker id="stable-flow-arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L12 6L0 12Z" fill="var(--accent)"/></marker></defs>
<rect class="diagram-fill" x="100" y="40" width="520" height="116" rx="8"/>
<rect class="diagram-fill" x="100" y="236" width="520" height="116" rx="8"/>
<rect class="diagram-fill" x="100" y="432" width="520" height="116" rx="8"/>
<path class="diagram-line" d="M360 168V222" fill="none" stroke="var(--accent)" stroke-width="4" marker-end="url(#stable-flow-arrow)"/>
<path class="diagram-line" d="M360 364V418" fill="none" stroke="var(--accent)" stroke-width="4" marker-end="url(#stable-flow-arrow)"/>
<text class="figure-heading" x="360" y="84" text-anchor="middle" font-size="34">同一组分数</text>
<text x="360" y="126" text-anchor="middle" font-size="30">1002, 1001, 1000</text>
<text class="figure-heading" x="360" y="280" text-anchor="middle" font-size="34">减去共同最大值</text>
<text x="360" y="322" text-anchor="middle" font-size="30">0, −1, −2</text>
<text class="figure-heading" x="360" y="476" text-anchor="middle" font-size="34">求指数并归一化</text>
<text x="360" y="518" text-anchor="middle" font-size="30">0.6652, 0.2447, 0.0900</text>
</svg>
</div>

图中数据是教学构造，权重保留四位小数；舍入后相加可能与1略有差异。
