---
title: 草稿验证为什么只接受连续前缀
description: 用同一组 token，看清候选、验证和缓存回退之间的对应。
---

## 从第一个分歧处停下

考虑贪心解码：每次选择概率最大的 token。已有前缀记为 P，草稿给出 a、b、c、e；目标模型在相应前缀下依次选择 a、b、d。下面是一组教学构造，字母代表 token，不代表单词。

<figure>
<svg viewBox="0 0 900 420" style="font-family:var(--default-font)" role="img" aria-label="草稿为P a b c e；目标模型在第三个候选处分歧，接受a b并输出d，丢弃c e。">
<path d="M590 40V350" stroke="var(--muted)" stroke-dasharray="6 6" fill="none"/>
<text x="610" y="30" font-size="25" text-anchor="start" fill="var(--text)">首个分歧</text>
<text x="25" y="102" font-size="26" text-anchor="start" fill="var(--text)">草稿</text>
<rect x="200" y="60" width="100" height="62" rx="6" fill="var(--node-bg)" stroke="var(--node-line)"/>
<text x="250" y="102" font-size="30" text-anchor="middle" fill="var(--text)">P</text>
<rect x="335" y="60" width="100" height="62" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="385" y="102" font-size="30" text-anchor="middle" fill="var(--text)">a</text>
<rect x="470" y="60" width="100" height="62" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="520" y="102" font-size="30" text-anchor="middle" fill="var(--text)">b</text>
<rect x="605" y="60" width="100" height="62" rx="6" fill="var(--compare-soft)" stroke="var(--compare)"/>
<text x="655" y="102" font-size="30" text-anchor="middle" fill="var(--text)">c</text>
<path d="M615 70L695 112" stroke="var(--compare)" stroke-width="2"/>
<rect x="740" y="60" width="100" height="62" rx="6" fill="var(--compare-soft)" stroke="var(--compare)"/>
<text x="790" y="102" font-size="30" text-anchor="middle" fill="var(--text)">e</text>
<path d="M750 70L830 112" stroke="var(--compare)" stroke-width="2"/>
<text x="25" y="212" font-size="26" text-anchor="start" fill="var(--text)">验证</text>
<rect x="200" y="170" width="100" height="62" rx="6" fill="var(--node-bg)" stroke="var(--node-line)"/>
<text x="250" y="212" font-size="30" text-anchor="middle" fill="var(--text)">P</text>
<rect x="335" y="170" width="100" height="62" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="385" y="212" font-size="30" text-anchor="middle" fill="var(--text)">a</text>
<rect x="470" y="170" width="100" height="62" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="520" y="212" font-size="30" text-anchor="middle" fill="var(--text)">b</text>
<rect x="605" y="170" width="100" height="62" rx="6" fill="var(--node-bg)" stroke="var(--node-line)"/>
<text x="655" y="212" font-size="30" text-anchor="middle" fill="var(--text)">d</text>
<text x="25" y="322" font-size="26" text-anchor="start" fill="var(--text)">输出</text>
<rect x="200" y="280" width="100" height="62" rx="6" fill="var(--node-bg)" stroke="var(--node-line)"/>
<text x="250" y="322" font-size="30" text-anchor="middle" fill="var(--text)">P</text>
<rect x="335" y="280" width="100" height="62" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="385" y="322" font-size="30" text-anchor="middle" fill="var(--text)">a</text>
<rect x="470" y="280" width="100" height="62" rx="6" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="520" y="322" font-size="30" text-anchor="middle" fill="var(--text)">b</text>
<rect x="605" y="280" width="100" height="62" rx="6" fill="var(--node-bg)" stroke="var(--node-line)"/>
<text x="655" y="322" font-size="30" text-anchor="middle" fill="var(--text)">d</text>
<text x="335" y="390" font-size="24" text-anchor="start" fill="var(--text)">接受连续匹配的 a、b</text>
<text x="650" y="390" font-size="24" text-anchor="start" fill="var(--text)">用 d 纠正</text>
</svg>
<figcaption>列位置保持不变；蓝色为匹配前缀，划线为丢弃候选。验证行展示对应位置的选择结果，不是另一份输入序列。</figcaption>
</figure>

为什么不能跳过 c、继续接受 e？e 的草稿上下文包含 c；目标模型已经选择 d，上下文随之改变，原来关于 e 的判断不能沿用。因此接受范围必须从左到右连续，输出 a、b 后接目标模型选出的 d。这里仅讲贪心验证，随机采样需要另行定义接受与纠正规则。[机制依据：Hugging Face](https://huggingface.co/blog/assisted-generation)。

## 输出 token 与有效缓存不是同一个长度

沿用上图的 P、a、b、c、e。目标模型验证这些候选时，会形成与候选路径有关的 KV 状态。下面画的是逻辑上可复用的前缀；物理内存可以复用，失效位置不能继续当成有效历史。

<figure>
<svg viewBox="0 0 900 490" style="font-family:var(--default-font)" role="img" aria-label="每个token画为上下K和V两格。三行中前缀P与a b保留；c e对应列被清空；处理d后第三列写入新的KV。">
<text x="25" y="30" font-size="25" text-anchor="start" fill="var(--text)">每列对应一个 token；上格 K，下格 V</text>
<text x="24" y="127" font-size="25" text-anchor="start" fill="var(--text)">验证后</text>
<rect x="200" y="90" width="100" height="28" fill="var(--node-bg)" stroke="var(--node-line)"/>
<rect x="200" y="120" width="100" height="28" fill="var(--node-bg)" stroke="var(--node-line)"/>
<text x="250" y="75" font-size="25" text-anchor="middle" fill="var(--text)">P</text>
<rect x="335" y="90" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<rect x="335" y="120" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="385" y="75" font-size="25" text-anchor="middle" fill="var(--text)">a</text>
<rect x="470" y="90" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<rect x="470" y="120" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="520" y="75" font-size="25" text-anchor="middle" fill="var(--text)">b</text>
<rect x="605" y="90" width="100" height="28" fill="var(--compare-soft)" stroke="var(--compare)"/>
<rect x="605" y="120" width="100" height="28" fill="var(--compare-soft)" stroke="var(--compare)"/>
<text x="655" y="75" font-size="25" text-anchor="middle" fill="var(--text)">c</text>
<path d="M613 97L697 141" stroke="var(--compare)" stroke-width="2"/>
<rect x="740" y="90" width="100" height="28" fill="var(--compare-soft)" stroke="var(--compare)"/>
<rect x="740" y="120" width="100" height="28" fill="var(--compare-soft)" stroke="var(--compare)"/>
<text x="790" y="75" font-size="25" text-anchor="middle" fill="var(--text)">e</text>
<path d="M748 97L832 141" stroke="var(--compare)" stroke-width="2"/>
<text x="24" y="257" font-size="25" text-anchor="start" fill="var(--text)">逻辑回退</text>
<rect x="200" y="220" width="100" height="28" fill="var(--node-bg)" stroke="var(--node-line)"/>
<rect x="200" y="250" width="100" height="28" fill="var(--node-bg)" stroke="var(--node-line)"/>
<text x="250" y="205" font-size="25" text-anchor="middle" fill="var(--text)">P</text>
<rect x="335" y="220" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<rect x="335" y="250" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="385" y="205" font-size="25" text-anchor="middle" fill="var(--text)">a</text>
<rect x="470" y="220" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<rect x="470" y="250" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="520" y="205" font-size="25" text-anchor="middle" fill="var(--text)">b</text>
<rect x="605" y="220" width="100" height="28" fill="none" stroke="var(--muted)" stroke-dasharray="5 5"/>
<rect x="605" y="250" width="100" height="28" fill="none" stroke="var(--muted)" stroke-dasharray="5 5"/>
<text x="655" y="205" font-size="25" text-anchor="middle" fill="var(--text)">c</text>
<text x="655" y="310" font-size="22" text-anchor="middle" fill="var(--text)">d 待计算</text>
<rect x="740" y="220" width="100" height="28" fill="none" stroke="var(--muted)" stroke-dasharray="5 5"/>
<rect x="740" y="250" width="100" height="28" fill="none" stroke="var(--muted)" stroke-dasharray="5 5"/>
<text x="790" y="205" font-size="25" text-anchor="middle" fill="var(--text)">e</text>
<text x="25" y="310" font-size="22" text-anchor="start" fill="var(--text)">保留前缀，失效后缀</text>
<text x="24" y="387" font-size="25" text-anchor="start" fill="var(--text)">处理 d 后</text>
<rect x="200" y="350" width="100" height="28" fill="var(--node-bg)" stroke="var(--node-line)"/>
<rect x="200" y="380" width="100" height="28" fill="var(--node-bg)" stroke="var(--node-line)"/>
<text x="250" y="335" font-size="25" text-anchor="middle" fill="var(--text)">P</text>
<rect x="335" y="350" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<rect x="335" y="380" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="385" y="335" font-size="25" text-anchor="middle" fill="var(--text)">a</text>
<rect x="470" y="350" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<rect x="470" y="380" width="100" height="28" fill="var(--accent-soft)" stroke="var(--accent)"/>
<text x="520" y="335" font-size="25" text-anchor="middle" fill="var(--text)">b</text>
<rect x="605" y="350" width="100" height="28" fill="var(--node-bg)" stroke="var(--node-line)"/>
<rect x="605" y="380" width="100" height="28" fill="var(--node-bg)" stroke="var(--node-line)"/>
<text x="655" y="335" font-size="25" text-anchor="middle" fill="var(--text)">d</text>
<rect x="740" y="350" width="100" height="28" fill="none" stroke="var(--muted)" stroke-dasharray="5 5"/>
<rect x="740" y="380" width="100" height="28" fill="none" stroke="var(--muted)" stroke-dasharray="5 5"/>
<text x="790" y="335" font-size="25" text-anchor="middle" fill="var(--text)">e</text>
<text x="200" y="466" font-size="22" text-anchor="start" fill="var(--text)">P 的整段缓存压缩为一列；格子表示结构，不表示实际张量维度。</text>
</svg>
<figcaption>教学构造：假定验证前向覆盖图示候选。这里只画目标模型缓存，不混用草稿模型的 KV。</figcaption>
</figure>

图中第二行已确认输出 d，但验证用的是含 c 的输入，不能把 KV(c) 改个名字当作 KV(d)。必须用正确前缀处理 d，再取得它的缓存；实现可把这项工作合并进下一轮前向。沿着相同列比较两图，就能区分“决定输出什么”和“哪些历史状态可继续用”。

改变输入再检验一次：若第一处就不匹配，a、b 也不能保留；若全部匹配，则没有图中的拒绝后缀。图中回退长度由首个分歧决定，不是固定删除两个位置。
