---
title: 数值稳定的 Softmax：从公式到批量实现
description: 用同一组输入贯穿指数变换、归一化和批量计算，理解减去最大值解决了什么，以及它留下了哪些边界。
document_id: softmax-longform
---

Softmax 把一组分数变成非负、总和为 1 的权重。写成代码时，问题不只是翻译公式：输入可能整体很大，计算可能沿错误的轴展开，有限精度也可能让很小的权重变成零。下面把数学关系、实际数值和数据组织放在同一条主线上。

## 先确定哪些元素一起归一化

设一行有 \(N\) 个有限实数，记作 \(x=(x_1,\ldots,x_N)\)。Softmax 为每个元素分配权重：

$$
p_i=\frac{e^{x_i}}{\sum_{j=1}^{N}e^{x_j}}.
$$

指数把每个分数映射为正数，分母将同一组正数相加。每个分子都除以这个共同的总和，因此权重总和为 1。比较发生在这一行内部，不能把其他样本的分数混入分母。

取教学构造输入 \(x=(2,1,0)\)。指数约为 \((7.3891,2.7183,1)\)，总和约为 11.1073，归一化后得到 \((0.6652,0.2447,0.0900)\)。下表只显示四位小数，显示值的总和可能因四舍五入略微偏离 1；计算时不先对中间结果取整。

| 元素 | 输入分数 | 指数值（约） | 归一化权重（约） |
|---|---:|---:|---:|
| 第一个 | 2 | 7.3891 | 0.6652 |
| 第二个 | 1 | 2.7183 | 0.2447 |
| 第三个 | 0 | 1.0000 | 0.0900 |

较大的输入获得较大的权重，但权重并不是输入的线性缩放。差值进入指数，决定相对比例；输入的共同偏移则可以约去。这一区别正是稳定实现的依据。

## 大数值如何破坏直接计算

给每个分数加上 1000，得到 \((1002,1001,1000)\)。三个元素之间的差值没有改变，但直接求指数的中间量非常大。用 Python 的 `math.exp` 直接计算 `exp(1002.0)`，会得到 `OverflowError`。

最终的三个权重仍应该与上一组相同，问题出在计算路径：先生成了过大的中间量，再试图通过相除消去它。正确的数学结果不能保证每一条计算路径都能在有限精度中抵达它。

下面的对照关注中间量，两组输入是人工构造，不代表训练数据，也不能据此推断预测质量或运行速度。

| 输入 | 与最大值的差 | 直接求指数 | 平移后的指数（约） |
|---|---|---|---|
| `(2, 1, 0)` | `(0, -1, -2)` | 可以得到有限数 | `(1, 0.3679, 0.1353)` |
| `(1002, 1001, 1000)` | `(0, -1, -2)` | `math.exp` 溢出 | `(1, 0.3679, 0.1353)` |

## 同一常数为什么可以约去

对所有元素减去同一常数 \(m\)。在实数运算中，分子与分母同时获得因子 \(e^{-m}\)：

$$
\frac{e^{x_i-m}}{\sum_j e^{x_j-m}}
=\frac{e^{-m}e^{x_i}}{e^{-m}\sum_j e^{x_j}}
=\frac{e^{x_i}}{\sum_j e^{x_j}}.
$$

关键是“同一常数”。各个元素减去不同的数时，共同因子就不存在，权重通常会改变。这个证明讨论实数中的等价关系，不保证浮点计算逐位相同。

选择 \(m=\max_j x_j\)，就让所有 \(x_i-m\) 都不大于零。平移后的指数不超过 1，其中至少有一个为 1，因此避免先计算非常大的正指数。SciPy 的 [Softmax 文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.softmax.html)也说明其实现通过平移避免溢出。

<figure>
<svg viewBox="0 0 760 245" role="img" aria-label="同一行输入先减去最大值，再求指数并归一化">
<rect class="diagram-fill" x="20" y="46" width="210" height="124" rx="8"/>
<rect class="diagram-fill" x="275" y="46" width="210" height="124" rx="8"/>
<rect class="diagram-fill" x="530" y="46" width="210" height="124" rx="8"/>
<path class="diagram-line" d="M239 108h27m-8-6 8 6-8 6M494 108h27m-8-6 8 6-8 6" fill="none" stroke-width="2"/>
<text x="125" y="86" text-anchor="middle" font-size="22">同一行的输入</text>
<text x="125" y="128" text-anchor="middle" font-size="20">1002, 1001, 1000</text>
<text x="380" y="86" text-anchor="middle" font-size="22">减去最大值</text>
<text x="380" y="128" text-anchor="middle" font-size="20">0, −1, −2</text>
<text x="635" y="86" text-anchor="middle" font-size="22">求指数再归一化</text>
<text x="635" y="128" text-anchor="middle" font-size="20">权重总和为 1</text>
<text x="380" y="215" text-anchor="middle" font-size="20">每一行独立计算最大值和分母</text>
</svg>
<figcaption>图 1：减去同一行的最大值改变中间量的大小，保留实数运算中的归一化结果；矩形大小不编码数值。</figcaption>
</figure>

图中每一行都重复同一条计算路径。将输入整体提高 1000 不改变相对差值，但把某一个元素单独提高 1000 会改变差值，也就会改变归一化权重。

## 批量计算需要保留哪一维

输入有 \(B\) 行、每行 \(N\) 个分数，形状为 \((B,N)\)。目标是对每个样本独立归一化，所以最大值和指数总和都沿最后一维计算。输出仍为 \((B,N)\)，每一行的权重分别求和为 1。

在 NumPy 中，`keepdims=True` 让被归约的维度保留为长度 1。每行最大值的形状成为 \((B,1)\)，可广播到对应行的 \(N\) 个元素；分母也采用同样的形状。这种组织把“每一行使用自己的共同量”直接写进数组结构。参见 NumPy 的 [max](https://numpy.org/doc/stable/reference/generated/numpy.max.html) 与 [sum](https://numpy.org/doc/stable/reference/generated/numpy.sum.html) 参数说明。

| 操作 | 输入形状 | 输出形状 | 这一步的作用 |
|---|---|---|---|
| 沿最后一维求最大值 | \((B,N)\) | \((B,1)\) | 每行得到自己的平移量 |
| 减去每行最大值 | \((B,N)\) 与 \((B,1)\) | \((B,N)\) | 广播到本行所有元素 |
| 逐元素求指数 | \((B,N)\) | \((B,N)\) | 得到不超过 1 的中间权重 |
| 沿最后一维求和 | \((B,N)\) | \((B,1)\) | 每行得到共同分母 |
| 除以每行分母 | \((B,N)\) 与 \((B,1)\) | \((B,N)\) | 分别归一化每个样本 |

```{.python title="softmax_numpy.py" data-highlight="4-6"}
import numpy as np

def softmax(x):
    shifted = x - x.max(axis=-1, keepdims=True)
    weights = np.exp(shifted)
    return weights / weights.sum(axis=-1, keepdims=True)
```

这个片段假设 `x` 是非空的浮点数组，且元素有限。若改用整数数组或改变归约轴，需要重新核对数据类型和归一化对象。SciPy 的接口默认 `axis=None`，使用库函数时也要明确选择适合任务的轴，不能默认以为它总是逐行计算。

## 用标准库跑通同一个例子

下面用标准库实现逐行计算，便于独立运行。输入约定为非空、等长的行，各元素是有限浮点数；返回嵌套列表，外层对应样本，内层对应各样本的权重。列表实现把广播改成明确的逐行循环，数学步骤保持一致。

```{.python title="softmax_rows.py" data-highlight="7-10"}
from math import exp, fsum


def softmax_rows(rows):
    result = []
    for row in rows:
        maximum = max(row)
        weights = [exp(value - maximum) for value in row]
        denominator = fsum(weights)
        result.append([weight / denominator for weight in weights])
    return result


inputs = [
    [2.0, 1.0, 0.0],
    [1002.0, 1001.0, 1000.0],
    [-1000.0, -1000.0, -1000.0],
]
probabilities = softmax_rows(inputs)

for source, output in zip(inputs, probabilities):
    rounded = [round(value, 6) for value in output]
    print(source, "->", rounded)
    print("权重总和：", round(fsum(output), 12))
```

前两行输出均约为 `[0.665241, 0.244728, 0.090031]`；第三行三个分数相同，输出均约为 `0.333333`。打印得到的权重总和为 `1.0`。这里使用 `fsum` 求和，不先对概率四舍五入；显示值只用于方便阅读。

完整实现应与公式一起看：先得到每行最大值，再构造相对差值；指数和分母始终属于同一行。返回结果的行数与输入一致，各行的元素数量也保持不变。这些结构关系比仅检查总和更能发现轴或组织上的错误。

### 对照哪些结果才能发现错误

总和为 1 是必要检查，但不是充分检查。错误地对整个批次归一化，也能让整个数组的总和为 1；交换输出元素的位置，不影响总和，却破坏了输入与输出的对应关系。

| 检查对象 | 应观察到的关系 | 能发现的问题 |
|---|---|---|
| 每一行的总和 | 分别接近 1 | 把样本混在一起归一化 |
| 输入与输出的形状 | 行数和每行长度保持一致 | 错误归约或丢失维度 |
| 共同平移后的结果 | 与原结果近似一致 | 没有使用共同平移量 |
| 一行中相同的分数 | 获得相同权重 | 元素顺序或分母对应错误 |

这些是结构和数值关系检查，不是模型精度实验。容差需要结合数据类型和计算规模设定；三行小数组也不能覆盖所有输入规模。

## 稳定计算仍然有边界

减去最大值避免的是过大的正指数中间量。它不消除所有浮点问题：两个分数相差非常大时，较小元素的指数仍可能下溢到零。对有限输入来说，最大值对应的指数仍为 1，分母不会因为所有指数都下溢而变成零。

若输入含 `NaN` 或无穷，上述有限实数推导不能直接套用。正无穷减去正无穷并不是有限差值；全为负无穷的一行也需要应用自行定义处理策略。不要通过盲目替换非有限值，掩盖上游数据或建模上的问题。

计算 `log(softmax(x))` 与直接计算稳定的对数形式也是不同路径。先把很小的概率舍入为零，再取对数会丢失信息；任务需要对数概率时，应单独核对对应实现。不能把 Softmax 的稳定平移概括成所有相关损失都已经稳定。

## 把公式、轴和边界一起带回实现

理解代码可以抓住三个连续问题：哪些分数属于同一组，哪些中间量会过大，以及哪些维度必须保留以维持对应关系。共同平移解决计算路径上的指数溢出，逐行归约保证样本独立，边界约定限定推导和代码的适用范围。

用小数值核对顺序，再用共同平移后的大数值核对稳定性，最后检查每行的形状和总和。这条验证路径保留了对有限精度和非有限输入的必要判断。

<aside class="article-sources" aria-label="来源">
<p class="sources-title">来源</p>
<p><a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.softmax.html">SciPy softmax 文档</a>：定义、归一化轴和稳定平移。</p>
<p><a href="https://numpy.org/doc/stable/reference/generated/numpy.max.html">NumPy max</a> 与 <a href="https://numpy.org/doc/stable/reference/generated/numpy.sum.html">NumPy sum</a>：归约轴与 keepdims 参数。</p>
<p>文中的小数组是教学构造，数值由标准库代码计算，不表示模型实验结果。</p>
</aside>
