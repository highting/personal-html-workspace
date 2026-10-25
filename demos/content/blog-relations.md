---
title: 合批共享权重，但不会消除各请求的历史 KV
description: 把共享计算与独立历史放进一张图，判断吞吐收益来自哪里。
---

## 两个请求共用什么

同一模型副本内，请求 A、B 可以合批执行，复用同一组模型参数。下面只画一层注意力的数据依赖：新位置的隐藏状态经过同一组投影权重，得到各自的 Q、K、V；注意力仍读取各请求自己的历史。这里假设两条不同前缀，不涉及跨请求前缀缓存共享。[依据：NVIDIA 的推理优化说明](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/)。

<figure>
<svg viewBox="0 0 960 760" style="font-family:var(--default-font)" role="img" aria-label="共享的三组投影矩阵作用于A和B的新隐藏状态；生成的Q查询各自KV块，当前K和V追加到相应缓存，得到各自注意力输出。格子只表示结构，不代表真实维度或数值。">
<defs><marker id="relation-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="var(--muted)"/></marker></defs>
<text x="480" y="32" font-size="27" text-anchor="middle" fill="var(--text)">同一组投影权重 · 两条请求复用</text>
<defs><clipPath id="relation-grid-325-56"><rect x="325" y="56" width="82" height="82" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-325-56)" fill-opacity="0.72">
<rect x="325" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="346" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="367" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="388" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="325" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="346" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="367" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="388" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="325" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="346" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="367" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="388" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="325" y="119" width="19" height="19" fill="var(--muted)"/>
<rect x="346" y="119" width="19" height="19" fill="var(--muted)"/>
<rect x="367" y="119" width="19" height="19" fill="var(--muted)"/>
<rect x="388" y="119" width="19" height="19" fill="var(--muted)"/>
</g>
<text x="366" y="170" font-size="25" text-anchor="middle" fill="var(--text)">Wq</text>
<defs><clipPath id="relation-grid-435-56"><rect x="435" y="56" width="82" height="82" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-435-56)" fill-opacity="0.72">
<rect x="435" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="456" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="477" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="498" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="435" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="456" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="477" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="498" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="435" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="456" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="477" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="498" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="435" y="119" width="19" height="19" fill="var(--muted)"/>
<rect x="456" y="119" width="19" height="19" fill="var(--muted)"/>
<rect x="477" y="119" width="19" height="19" fill="var(--muted)"/>
<rect x="498" y="119" width="19" height="19" fill="var(--muted)"/>
</g>
<text x="476" y="170" font-size="25" text-anchor="middle" fill="var(--text)">Wk</text>
<defs><clipPath id="relation-grid-545-56"><rect x="545" y="56" width="82" height="82" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-545-56)" fill-opacity="0.72">
<rect x="545" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="566" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="587" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="608" y="56" width="19" height="19" fill="var(--muted)"/>
<rect x="545" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="566" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="587" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="608" y="77" width="19" height="19" fill="var(--muted)"/>
<rect x="545" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="566" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="587" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="608" y="98" width="19" height="19" fill="var(--muted)"/>
<rect x="545" y="119" width="19" height="19" fill="var(--muted)"/>
<rect x="566" y="119" width="19" height="19" fill="var(--muted)"/>
<rect x="587" y="119" width="19" height="19" fill="var(--muted)"/>
<rect x="608" y="119" width="19" height="19" fill="var(--muted)"/>
</g>
<text x="586" y="170" font-size="25" text-anchor="middle" fill="var(--text)">Wv</text>
<path d="M315 178V184Q315 190 321 190H634Q640 190 640 184V178" fill="none" stroke="var(--muted)" stroke-width="2"/>
<path d="M315 190H64Q52 190 52 202V310Q52 322 64 322H186" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<path d="M640 190H896Q908 190 908 202V310Q908 322 896 322H774" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<text x="240" y="225" font-size="26" text-anchor="middle" fill="var(--text)">请求 A · 新位置隐藏状态</text>
<defs><clipPath id="relation-grid-130-244"><rect x="130" y="244" width="214" height="25" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-130-244)" fill-opacity="0.72">
<rect x="130" y="244" width="25" height="25" fill="var(--accent)"/>
<rect x="157" y="244" width="25" height="25" fill="var(--accent)"/>
<rect x="184" y="244" width="25" height="25" fill="var(--accent)"/>
<rect x="211" y="244" width="25" height="25" fill="var(--accent)"/>
<rect x="238" y="244" width="25" height="25" fill="var(--accent)"/>
<rect x="265" y="244" width="25" height="25" fill="var(--accent)"/>
<rect x="292" y="244" width="25" height="25" fill="var(--accent)"/>
<rect x="319" y="244" width="25" height="25" fill="var(--accent)"/>
</g>
<path d="M240 272V296" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<rect x="188" y="300" width="104" height="44" rx="10" class="diagram-fill"/>
<text x="240" y="330" font-size="23" text-anchor="middle" fill="var(--text)">投影</text>
<path d="M240 344V360M125 360H345" fill="none" stroke="var(--muted)" stroke-width="2"/>
<path d="M125 360V388" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<text x="82" y="412" font-size="25" text-anchor="end" fill="var(--text)">K</text>
<defs><clipPath id="relation-grid-90-392"><rect x="90" y="392" width="73" height="23" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-90-392)" fill-opacity="0.72">
<rect x="90" y="392" width="23" height="23" fill="var(--accent)"/>
<rect x="115" y="392" width="23" height="23" fill="var(--accent)"/>
<rect x="140" y="392" width="23" height="23" fill="var(--accent)"/>
</g>
<path d="M225 360V388" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<text x="182" y="412" font-size="25" text-anchor="end" fill="var(--text)">V</text>
<defs><clipPath id="relation-grid-190-392"><rect x="190" y="392" width="73" height="23" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-190-392)" fill-opacity="0.72">
<rect x="190" y="392" width="23" height="23" fill="var(--accent)"/>
<rect x="215" y="392" width="23" height="23" fill="var(--accent)"/>
<rect x="240" y="392" width="23" height="23" fill="var(--accent)"/>
</g>
<path d="M345 360V388" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<text x="302" y="412" font-size="25" text-anchor="end" fill="var(--text)">Q</text>
<defs><clipPath id="relation-grid-310-392"><rect x="310" y="392" width="73" height="23" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-310-392)" fill-opacity="0.72">
<rect x="310" y="392" width="23" height="23" fill="var(--accent)"/>
<rect x="335" y="392" width="23" height="23" fill="var(--accent)"/>
<rect x="360" y="392" width="23" height="23" fill="var(--accent)"/>
</g>
<path d="M125 420V437Q125 445 133 445H189Q197 445 197 453V506" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<path d="M225 420V454Q225 462 217 462H205Q197 462 197 470V506" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<path d="M345 420V541" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<text x="110" y="494" font-size="25" text-anchor="middle" fill="var(--text)">历史 KV A</text>
<defs><clipPath id="relation-grid-35-512"><rect x="35" y="512" width="172" height="56" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-35-512)" fill-opacity="0.72">
<rect x="35" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="64" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="93" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="122" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="151" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="180" y="512" width="27" height="27" fill="var(--accent)"/>
<rect x="35" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="64" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="93" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="122" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="151" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="180" y="541" width="27" height="27" fill="var(--accent)"/>
</g>
<rect x="177" y="509" width="34" height="62" rx="6" fill="none" stroke="var(--accent)" stroke-width="2"/>
<text x="130" y="606" font-size="23" text-anchor="middle" fill="var(--text)">同色列：本步追加</text>
<path d="M214 544H262" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<path d="M275 544H415Q425 544 421 554L400 602Q397 610 389 610H301Q293 610 290 602L269 554Q265 544 275 544Z" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="2"/>
<text x="345" y="586" font-size="26" text-anchor="middle" fill="var(--text)">注意力</text>
<path d="M345 612V649" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<defs><clipPath id="relation-grid-253-653"><rect x="253" y="653" width="178" height="28" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-253-653)" fill-opacity="0.72">
<rect x="253" y="653" width="28" height="28" fill="var(--accent)"/>
<rect x="283" y="653" width="28" height="28" fill="var(--accent)"/>
<rect x="313" y="653" width="28" height="28" fill="var(--accent)"/>
<rect x="343" y="653" width="28" height="28" fill="var(--accent)"/>
<rect x="373" y="653" width="28" height="28" fill="var(--accent)"/>
<rect x="403" y="653" width="28" height="28" fill="var(--accent)"/>
</g>
<text x="345" y="720" font-size="25" text-anchor="middle" fill="var(--text)">输出 A → 后续层</text>
<text x="720" y="225" font-size="26" text-anchor="middle" fill="var(--text)">请求 B · 新位置隐藏状态</text>
<defs><clipPath id="relation-grid-610-244"><rect x="610" y="244" width="214" height="25" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-610-244)" fill-opacity="0.72">
<rect x="610" y="244" width="25" height="25" fill="var(--compare)"/>
<rect x="637" y="244" width="25" height="25" fill="var(--compare)"/>
<rect x="664" y="244" width="25" height="25" fill="var(--compare)"/>
<rect x="691" y="244" width="25" height="25" fill="var(--compare)"/>
<rect x="718" y="244" width="25" height="25" fill="var(--compare)"/>
<rect x="745" y="244" width="25" height="25" fill="var(--compare)"/>
<rect x="772" y="244" width="25" height="25" fill="var(--compare)"/>
<rect x="799" y="244" width="25" height="25" fill="var(--compare)"/>
</g>
<path d="M720 272V296" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<rect x="668" y="300" width="104" height="44" rx="10" class="diagram-fill"/>
<text x="720" y="330" font-size="23" text-anchor="middle" fill="var(--text)">投影</text>
<path d="M720 344V360M605 360H825" fill="none" stroke="var(--muted)" stroke-width="2"/>
<path d="M605 360V388" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<text x="562" y="412" font-size="25" text-anchor="end" fill="var(--text)">K</text>
<defs><clipPath id="relation-grid-570-392"><rect x="570" y="392" width="73" height="23" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-570-392)" fill-opacity="0.72">
<rect x="570" y="392" width="23" height="23" fill="var(--compare)"/>
<rect x="595" y="392" width="23" height="23" fill="var(--compare)"/>
<rect x="620" y="392" width="23" height="23" fill="var(--compare)"/>
</g>
<path d="M705 360V388" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<text x="662" y="412" font-size="25" text-anchor="end" fill="var(--text)">V</text>
<defs><clipPath id="relation-grid-670-392"><rect x="670" y="392" width="73" height="23" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-670-392)" fill-opacity="0.72">
<rect x="670" y="392" width="23" height="23" fill="var(--compare)"/>
<rect x="695" y="392" width="23" height="23" fill="var(--compare)"/>
<rect x="720" y="392" width="23" height="23" fill="var(--compare)"/>
</g>
<path d="M825 360V388" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<text x="782" y="412" font-size="25" text-anchor="end" fill="var(--text)">Q</text>
<defs><clipPath id="relation-grid-790-392"><rect x="790" y="392" width="73" height="23" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-790-392)" fill-opacity="0.72">
<rect x="790" y="392" width="23" height="23" fill="var(--compare)"/>
<rect x="815" y="392" width="23" height="23" fill="var(--compare)"/>
<rect x="840" y="392" width="23" height="23" fill="var(--compare)"/>
</g>
<path d="M605 420V437Q605 445 613 445H669Q677 445 677 453V506" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<path d="M705 420V454Q705 462 697 462H685Q677 462 677 470V506" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<path d="M825 420V541" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<text x="590" y="494" font-size="25" text-anchor="middle" fill="var(--text)">历史 KV B</text>
<defs><clipPath id="relation-grid-515-512"><rect x="515" y="512" width="172" height="56" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-515-512)" fill-opacity="0.72">
<rect x="515" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="544" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="573" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="602" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="631" y="512" width="27" height="27" fill="var(--muted)"/>
<rect x="660" y="512" width="27" height="27" fill="var(--compare)"/>
<rect x="515" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="544" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="573" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="602" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="631" y="541" width="27" height="27" fill="var(--muted)"/>
<rect x="660" y="541" width="27" height="27" fill="var(--compare)"/>
</g>
<rect x="657" y="509" width="34" height="62" rx="6" fill="none" stroke="var(--compare)" stroke-width="2"/>
<text x="610" y="606" font-size="23" text-anchor="middle" fill="var(--text)">同色列：本步追加</text>
<path d="M694 544H742" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<path d="M755 544H895Q905 544 901 554L880 602Q877 610 869 610H781Q773 610 770 602L749 554Q745 544 755 544Z" fill="var(--compare-soft)" stroke="var(--compare)" stroke-width="2"/>
<text x="825" y="586" font-size="26" text-anchor="middle" fill="var(--text)">注意力</text>
<path d="M825 612V649" fill="none" stroke="var(--muted)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#relation-arrow)"/>
<defs><clipPath id="relation-grid-733-653"><rect x="733" y="653" width="178" height="28" rx="6"/></clipPath></defs>
<g clip-path="url(#relation-grid-733-653)" fill-opacity="0.72">
<rect x="733" y="653" width="28" height="28" fill="var(--compare)"/>
<rect x="763" y="653" width="28" height="28" fill="var(--compare)"/>
<rect x="793" y="653" width="28" height="28" fill="var(--compare)"/>
<rect x="823" y="653" width="28" height="28" fill="var(--compare)"/>
<rect x="853" y="653" width="28" height="28" fill="var(--compare)"/>
<rect x="883" y="653" width="28" height="28" fill="var(--compare)"/>
</g>
<text x="825" y="720" font-size="25" text-anchor="middle" fill="var(--text)">输出 B → 后续层</text>
</svg>
<figcaption>格子表示向量、矩阵与缓存结构，不按真实维度或数值绘制。蓝、橙分别贯穿请求 A、B；灰色权重共享，历史缓存分开。</figcaption>
</figure>

图顶部只有一组权重，下方却保留两条历史路径。合批能摊薄权重访问成本，但历史长度增加时，KV 的存储与读取仍要付出代价。共享参数不等于共享全部数据，也不意味着批量越大，每个请求越快。

## 把收益放回完整执行路径

<figure>
<svg style="font-family:var(--default-font)" viewBox="0 0 960 250" role="img" aria-label="请求先提交和排队，再执行模型计算，最后返回。共享权重和独立KV属于执行阶段，多卡时还可能包含通信。图形宽度不代表耗时。">
<defs><marker id="path-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="var(--muted)"/></marker></defs>
<g class="diagram-fill"><rect x="20" y="50" width="200" height="90" rx="12"/><rect x="740" y="50" width="200" height="90" rx="12"/></g>
<rect x="280" y="30" width="400" height="130" rx="12" fill="none" stroke="var(--node-line)"/>
<g fill="var(--text)" font-size="27" text-anchor="middle"><text x="120" y="103">提交与排队</text><text x="480" y="78">模型执行</text><text x="480" y="124">共享权重 + 独立 KV</text><text x="840" y="103">返回结果</text><text x="480" y="218">多卡执行时，还需计入通信</text></g>
<g fill="none" stroke="var(--muted)" stroke-width="2" marker-end="url(#path-arrow)"><path d="M220 95H276"/><path d="M680 95H736"/></g>
<path d="M480 162V184" fill="none" stroke="var(--muted)" stroke-dasharray="5 5"/>
</svg>
<figcaption>阶段关系示意，不按耗时比例绘制；通信是否发生及能否重叠取决于实际执行方案。</figcaption>
</figure>

评估合批时，应同时观察吞吐与请求延迟：权重复用带来的收益，是否被更长的等待、KV 访问或多卡通信抵消，需要在相同负载与统计口径下测量。关系图帮助确定该看哪里，不能代替测量结果。
