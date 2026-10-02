---
math: katex
---

# 切向更新为何增加权重范数

当更新方向与当前权重垂直时，新权重是直角三角形的斜边。只要步长非零，它就比原权重更长。

<div class="figure-scene">
<svg viewBox="0 0 900 610" role="img" aria-label="旧权重与切向更新垂直，新权重为更长的斜边">
<defs><marker id="weight-arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L12 6L0 12Z" fill="#3B5BDB"/></marker><marker id="step-arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L12 6L0 12Z" fill="#0891B2"/></marker></defs>
<path d="M130 490L650 490L650 170Z" fill="#EAE7DE"/>
<path d="M639.9 591.4A520 520 0 0 0 497.7 122.3" class="vector-reference" fill="none"/>
<line x1="130" y1="490" x2="650" y2="490" class="vector-primary" marker-end="url(#weight-arrow)"/>
<line x1="650" y1="490" x2="650" y2="170" class="vector-update" marker-end="url(#step-arrow)"/>
<line x1="130" y1="490" x2="650" y2="170" class="vector-primary" marker-end="url(#weight-arrow)"/>
<path d="M618 490L618 458L650 458" class="geometry-mark"/>
<circle cx="130" cy="490" r="5" fill="#263238"/>
<text x="65" y="550" style="font-size:36px">原点</text><text x="684" y="530" style="font-size:36px">更新前</text><text x="650" y="126" style="font-size:36px">更新后</text><text x="160" y="128" style="font-size:36px">原范数等长弧</text>
</svg>
<div class="figure-label primary" style="left:42%;top:91%;font-size:38px">\(W_t\)</div>
<div class="figure-label primary" style="left:38%;top:47%;font-size:38px">\(W_{t+1}\)</div>
<div class="figure-label updated" style="left:83%;top:52%;font-size:38px">\(-\eta u_t\)</div>
</div>

由 \(W_{t+1}=W_t-\eta u_t\) 且 \(u_t\perp W_t\)，勾股定理给出：

$$
\|W_{t+1}\|^2=\|W_t\|^2+\eta^2\|u_t\|^2
$$

因此当 \(\eta\|u_t\|>0\) 时，权重范数严格增大。这一结论以切向更新为条件；一般方向的更新不能直接套用。
