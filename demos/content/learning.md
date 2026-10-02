---
title: 数值稳定的 Softmax
description: 从概率归一化到减去最大值，理解一个等价变换如何避免指数溢出。
---

## 先看要计算什么

Softmax将一组实数转换为一组非负、和为1的权重。这里用教学构造向量 \(x=[2,1,0]\) 说明计算关系；它不表示模型实验结果。对第 \(i\) 个元素，先求指数，再除以所有指数的和：

$$
p_i=\frac{e^{x_i}}{\sum_{j=1}^{n}e^{x_j}}
$$

指数把每个元素映射为正数，归一化让它们可按相对权重比较。沿行计算时，输入形状从 \((B,N)\) 到输出 \((B,N)\)；归一化分母若保留维度，形状为 \((B,1)\)，再广播到每个元素。

<figure>
<svg viewBox="0 0 620 180" role="img" aria-label="输入向量经过指数变换和归一化，输出权重">
<rect class="diagram-fill" x="12" y="34" width="152" height="94" rx="8"/><rect class="diagram-fill" x="234" y="34" width="152" height="94" rx="8"/><rect class="diagram-fill" x="456" y="34" width="152" height="94" rx="8"/>
<path class="diagram-line" d="M174 81h44m-10-6 10 6-10 6M396 81h44m-10-6 10 6-10 6" fill="none" stroke-width="2"/>
<text x="88" y="70" text-anchor="middle" font-size="18">输入</text><text x="88" y="104" text-anchor="middle" font-size="20">[2, 1, 0]</text>
<text x="310" y="70" text-anchor="middle" font-size="18">指数变换</text><text x="310" y="104" text-anchor="middle" font-size="19">正数权重</text>
<text x="532" y="70" text-anchor="middle" font-size="18">归一化</text><text x="532" y="104" text-anchor="middle" font-size="19">总和为 1</text>
</svg>
<figcaption>图只表示计算映射，不以矩形长度编码数值。比较关系由同一组输入和公式给出。</figcaption>
</figure>

## 减去常数不改变结果

对全部输入减去同一个常数 \(m\)，分子与分母同时乘以 \(e^{-m}\)，因此相约后仍得到原结果。选取最大值 \(m=\max_j x_j\)，就让每个指数的输入都不大于零：

$$
\frac{e^{x_i-m}}{\sum_j e^{x_j-m}}
=\frac{e^{-m}e^{x_i}}{e^{-m}\sum_j e^{x_j}}
=p_i
$$

在实数运算中这是恒等变换；在浮点运算中，它避免直接对很大的正数求指数。极小项仍可能下溢，不能据此声称所有数值误差都消失。

### 对应到实现

```{.python title="softmax.py" data-highlight="1 3"}
shifted = x - x.max(axis=-1, keepdims=True)
weights = np.exp(shifted)
probabilities = weights / weights.sum(axis=-1, keepdims=True)
```

最大值和分母都保留最后一维，便于沿每行广播。这里先解释了数学变换，再给出对应的计算片段；运行时需先导入NumPy并提供合适数组。

## 使用边界

上述说明假设输入是有限实数；包含无穷或NaN时应按实际应用另行定义行为。这里解释数值稳定性，不声称改变模型预测能力，也没有给出运行速度实验。

来源：[SciPy softmax 文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.softmax.html)。
