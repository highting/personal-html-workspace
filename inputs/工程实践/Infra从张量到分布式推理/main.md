# Infra 教学文档 从张量到分布式推理

本讲义按配套学习计划的 A–L 模块展开，面向已有 Muon/MuonH 优化器经验、希望系统掌握训练与推理 Infra 的学习者。重点是建立连续的因果关系：张量如何存储，GPU 如何执行，数据如何跨设备流动，系统如何调度这些工作。

配套文件：[知识脉络版学习计划](C:/Users/highting/Documents/Codex/2026-10-03/codex-threads-01a10065-db54-7b20-9229/outputs/Infra学习计划_知识脉络版.md)。

阅读时先完成正文中的手算例子，再做章末实验，最后脱稿回答自测。实验是待执行任务；示例数值用于教学，不是你项目的实测结果。涉及 MuonH 更新公式、实际 mesh、缓存键、通信次数和性能数字的结论，仍需对照项目源码与日志。

正文中的“配图建议”是后续插图制作说明，包含位置、对象、箭头和要表达的结论；当前文档没有把这些建议当作已经绘制的图片。

## 学习顺序

| 模块 | 本章要回答的问题 | 前置 |
|---|---|---|
| A 张量表示与数值基础 | 一个张量怎样对应存储与精度 | 基本 PyTorch 与矩阵运算 |
| B GPU 执行与测量 | 数据什么时候可用，时间怎样测 | A |
| C 性能模型 | 运算量、流量与资源如何限制速度 | A、B |
| D 集合通信与协议 | 多个 rank 如何协同得到正确结果 | A–C |
| E 训练布局与项目 | 分片状态如何贯穿训练和更新 | D |
| F 基础算子 | 如何安排线程、访存和归约 | A–C |
| G GEMV 与 GEMM | 数据复用怎样改变执行效率 | F |
| H Transformer 与 Attention | 分块计算怎样保持 Attention 语义 | F、G |
| I 编译与 CUDA Graph | 如何降低框架和提交开销 | B、F |
| J 推理状态与调度 | 请求、token 和 KV 如何一起变化 | H 的形状与原理 |
| K 框架阅读 | 概念在哪里变成对象与状态 | I、J |
| L 分布式推理 | 多设备、多阶段如何协作 | D、G、J、K |

## 张量表示与数值基础

### 从逻辑坐标到物理地址

张量可以从两个层面理解。逻辑层说明它有多少个维度、每个维度多长；存储层说明某个逻辑元素实际位于哪段内存。改变逻辑视图不一定移动元素，移动元素也不一定改变 shape。

设张量的元素大小为 \(s\) 字节，逻辑坐标为 \((i_0,\ldots,i_{k-1})\)，步长为 \((t_0,\ldots,t_{k-1})\)，存储偏移为 \(o\)，则普通 strided tensor 的地址映射为：

$$
\operatorname{addr}(i_0,\ldots,i_{k-1})
=\operatorname{base}+s\left(o+\sum_{j=0}^{k-1}i_jt_j\right).
$$

步长的单位通常是元素，乘上 \(s\) 后才成为字节。一个连续的 \(3\times4\) 行主序矩阵，stride 为 \((4,1)\)：向下一行跨 4 个元素，向右一列跨 1 个元素。转置后 shape 为 \(4\times3\)，stride 为 \((1,4)\)，但原始 12 个元素可以完全不动。

例如原矩阵元素依次为 0 到 11，原坐标 \((1,2)\) 对应元素 6。转置后的坐标 \((2,1)\) 仍通过 \(2\times1+1\times4=6\) 指向同一元素。这就是 view：一份存储，多个索引解释。

> **配图建议 A1｜逻辑矩阵与存储地址。** 左边画一个 \(3\times4\) 矩阵，元素标 0–11；中间画同一份 12 格线性存储；右边画 \(4\times3\) 转置视图。用同色箭头连接元素 6，分别标注 stride \((4,1)\) 与 \((1,4)\)。不要把转置画成已经搬动了线性存储。

### 连续性与复制为什么影响性能

“连续”是相对于指定内存格式和逻辑遍历顺序而言的。对常见行主序二维张量，最后一维连续，并且一行紧接下一行，通常就能按一段连续区域遍历。转置 view 的各逻辑行可能变为大步长访问；它合法，却不一定适合下游 kernel。

`view()` 在形状与步长兼容时共享存储，不能满足条件时会失败；`reshape()` 可以通过 view 实现，也可能复制；`contiguous()` 在已经满足目标连续布局时可返回原张量，否则创建连续结果；`clone()` 创建副本。因此判断是否发生拷贝，不能只看函数名，应结合布局、共享关系与测量。[Tensor Views](https://docs.pytorch.org/docs/2.14/tensor_view.html)

这个区分直接连接你的 row shard 优化。若三个 rank 的接收段恰好是完整矩阵的连续行，接收缓冲区按正确行顺序排列，就可能直接把它解释为完整矩阵。若收集的是连续的“列分片各自副本”，将它们首尾拼接通常不会自然形成完整矩阵的行主序存储，需要重排或不同的索引解释。

### 别名与缓冲区生命周期

假设 \(a\) 和 \(b\) 共享存储，执行对 \(a\) 的原地写入会改变 \(b\) 看到的值。缓冲区复用因此要回答两件事：旧值最后一次在哪里被读取；是否还有别名或异步工作会读取旧值。

以候选权重 \(C=W-\eta U\) 为例，如果后面只需要 \(C\) 及其范数，而不再需要独立的 \(U\)，就可以考虑用更新缓冲区承载 \(C\)。但如果动量状态恰好与该缓冲区共享存储，覆盖它会改变下一步的算法状态。形状相同不构成复用的充分条件。

先用一张生命周期表列出每个张量的生产位置、最后使用位置、dtype、元素数和共享对象。只有存活区间不冲突、算子允许对应别名关系时，才复用存储。

> **配图建议 A2｜中间张量存活区间。** 横轴画“NS、归一化、候选权重、范数、回缩、写回”；纵轴列更新、候选权重、输出三个逻辑张量。上半图用三条独立存储条，下半图用一条可分阶段复用的存储条。用红色竖线标记旧值最后使用点，旁注“异步消费者完成后才可覆盖”。

### dtype 改变的不只是内存大小

FP32、FP16、BF16 每元素分别通常占 4、2、2 字节。FP32 有 8 位指数和 23 位尾数字段，FP16 为 5 和 10，BF16 为 8 和 7，另各有 1 位符号位。BF16 的指数范围接近 FP32，但表示相邻数值的精细程度明显更低；它与 FP16 不是“谁全面更精确”的关系。

存储精度、乘法输入精度、累加精度和输出精度可以不同。低精度输入配合 FP32 累加，可以降低累积误差，但不能恢复输入量化时已丢失的信息。多次加法的舍入还与顺序有关，所以数学上等价的两条归约路径未必逐位一致。[PyTorch 数值精度说明](https://docs.pytorch.org/docs/stable/notes/numerical_accuracy.html)

对你的 BF16 前置优化，应比较“先拼接后逐元素转换”与“先逐元素转换后拼接”。如果拼接只搬运数据，元素对应、舍入方式完全相同，而且中间没有算术，那么两者可以产生相同的 BF16 输入。这里改变的是转换位置和传输字节数，而不是必然引入一种新的低精度算法。

### 实验与自测

实验：创建坐标矩阵，完成转置、切片、`reshape()` 和一次原地修改；预测哪些视图会受影响，再验证。给一段更新绘制生命周期表，提出一个可复用位置和一个不可复用位置。

**问：释放 Python 变量后，显存为什么可能不下降？** 可能仍有其他引用或 view，也可能设备工作未完成；即使张量占用减少，缓存分配器也可能保留空闲区域以供后续使用。应区分活跃张量占用、分配器保留空间和设备总体占用。

**问：为什么分配次数从 9 变 1 不等于峰值显存降为九分之一？** 次数没有表达每次分配大小和同时存活关系；九次分配可能顺序发生并复用缓存，单次分配也可能更大。

## GPU 执行与可靠测量

### CPU 提交与 GPU 执行是两条时间线

在常见 CUDA 路径中，Python 调用经框架和运行时把工作提交给 GPU，然后 CPU 继续执行。函数返回往往说明工作已经提交，不说明设备已经完成。CPU 若需要读取 GPU 结果，或主动同步，就可能等待此前排队的工作。

因此，一段很短的 Python 调用区间可以对应很长的 GPU 工作；反过来，一次看似无关的同步调用可以承担之前积累的等待。分析优化器耗时前，必须知道计时区间从哪里开始、是否包含同步、GPU 队列中此前有什么工作。

### thread 到 SM 的组织关系

一个 kernel 的 grid 由许多 thread block 构成；block 在 NVIDIA 文档中也常称 CTA。block 内线程可以使用共享内存并进行 block 范围同步。普通 kernel 不应假定不同 block 按固定次序执行，也不能直接用 block 内屏障同步整个 grid。

NVIDIA GPU 的 warp 通常包含 32 个线程。硬件以 warp 为重要调度单位执行指令，线程仍有各自的寄存器和地址。分支可能使同一个 warp 的不同线程走不同路径，影响执行效率；但不能把所有线程简单理解为永远锁步而忽略同步要求。

SM 是承载 block、warp 调度和计算资源的单元。寄存器服务线程局部数据，shared memory 服务 block 协作；L1/L2 缓存与设备显存组成更远的存储层。寄存器资源用尽还可能产生 spill，使本来期待位于近端的数据进入更昂贵的访问路径。[CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

> **配图建议 B1｜执行组织与存储作用域。** 画 GPU 包含多个 SM，每个 SM 内放两三个 block，每个 block 内画若干 warp。寄存器靠近线程，shared memory 画在 block 旁，L2 画在 SM 外侧共享区域，显存画在最外层。避免把“一个 block 永久占满一个 SM”画成固定对应关系。

### stream 顺序与跨 stream 依赖

同一个 stream 中的工作按顺序执行。不同 stream 可以重叠，但“可以”不表示有足够资源或硬件条件保证并行，也不表示依赖会自动推断。

设 stream A 产生张量 \(X\)，stream B 消费 \(X\)。B 的消费必须等待 A 的生产完成。可以在 A 上记录 event，再让 B 等待这个 event；也可以让 B 等待 A 在指定时点已入队的工作。等待边连接的是设备执行关系，CPU 不必在这个位置停住。

另一个问题是内存何时可以复用。B 已经排队读取 \(X\)，但 Python 提前释放了引用；如果分配器不知道 B 仍在使用这段存储，就可能过早复用。`record_stream()` 用于向分配器声明跨 stream 使用，不能代替前面的生产者到消费者依赖。也可在明确管理生命周期时用事件和同步归还关系保障安全。[`Tensor.record_stream`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.record_stream.html)

> **配图建议 B2｜就绪依赖与释放依赖。** 画 A、B 两条水平 stream。A 上有“写 X”，B 上有“读 X”；第一条箭头从写完成指向读开始，标“数据就绪”。第二条从读完成指向“存储可复用”，标“生命周期结束”。在旁边分别列 event/wait 与 allocator 使用声明，突出两者解决不同问题。

### 三种时间与三种工具

CPU 提交时间回答宿主发起工作需要多久；CUDA Event 的设备时间戳差回答两个设备标记点之间经过多久；带正确同步边界的 wall-clock 回答调用方等待整个区间需要多久。

Event 时间不直接测 Python 函数耗时，但两个标记间可能包含 GPU 空闲、资源竞争和等待，并不总等于 kernel duration 的简单相加。多 stream 区间如果没有建立开始和结束依赖，还可能漏掉目标工作。计时必须先确定要测的是一个 kernel、一段设备执行，还是端到端步骤。[CUDA Event API](https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/group__CUDART__EVENT.html)

`torch.profiler` 适合把框架操作与设备工作联系起来；`nsys` 适合观察 CPU、stream、kernel 与通信的时间线；`ncu` 适合研究选定 kernel 的硬件行为。先用系统视角找到值得研究的 kernel，再进入细粒度指标，才能避免优化不在关键路径上的工作。

实验应固定 shape、dtype、设备、版本和输入分布，分开首次初始化与稳态，记录多次样本的分布。`ncu` 为采集不同指标可能重放执行，采集环境下的时间不能直接代替正常运行基准。[NCU Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html)

### 显存的三个读数

`memory_allocated()` 主要描述当前张量占用；`memory_reserved()` 描述缓存分配器管理的空间，包含已用与可复用部分；设备监控还可能包含 CUDA context、其他库和进程的占用。`empty_cache()` 释放的是可释放缓存，不会让仍被活跃张量使用的内存消失。[PyTorch CUDA memory management](https://docs.pytorch.org/docs/2.14/notes/cuda.html#memory-management)

判断优化峰值显存，要在相同执行范围记录峰值和时间线。只看函数结束时的读数，可能看不到中间曾同时存活的完整输入、NS 输出和候选权重。

### 实验与自测

实验：对固定矩阵乘分别测提交时间、Event 时间和同步 wall-clock；保存一张时间线并标出三种区间。再增加一个跨 stream 消费者，画出依赖后再运行。

**问：为什么一个 `wait` 很慢不能直接证明网络很慢？** 等待可能包含其他 rank 尚未到达、之前计算未结束、资源竞争和实际传输。需要对齐多个 rank 的时间线和阶段边界。

**问：如何判断通信计算重叠是否有用？** 比较相同工作量的完整区间是否变短，同时检查重叠是否拖慢计算或通信。两条色块重叠只说明同时活跃，不证明净收益。

## 访存与计算成本模型

### 从工作量和数据量开始

设完成一个运算需要 \(F\) 次浮点运算，某一存储层需要传输 \(V\) 字节，算力上限为 \(P_{\max}\)，该层有效带宽为 \(B\)。忽略启动、依赖等因素时，可用下式理解两个基本限制：

$$
T\gtrsim\max\left(\frac{F}{P_{\max}},\frac{V}{B}\right),
\qquad I=\frac{F}{V}.
$$

其中 \(I\) 是计算强度，单位为 FLOP/B。对应 roofline 的吞吐上界为 \(\min(P_{\max},IB)\)。这个模型用于判断应重点改善复用、带宽利用还是计算利用，不表示真实时间只由这两项组成。

峰值必须匹配实际运算路径：FP32、TF32、BF16 Tensor Core、稀疏计算不是同一个上限。带宽与流量也必须来自相同层级，不能把 L1 请求量除以 DRAM 带宽。

### 一组可手算的算子

以下先假设所有元素占 \(s\) 字节，输入理想地只读一次，输出不读取旧值，FMA 算两个 FLOPs。

| 运算 | 计算量 | 理想数据量 | 关键认识 |
|---|---:|---:|---|
| \(y=ax+b\)，标量 a/b | 约 \(2N\) | 约 \(2Ns\) | 融合能避免中间结果读写 |
| 矩阵转置 | 数学 FLOPs 近乎 0 | \(2Ns\) | 应看有效带宽和事务，而非 FLOP/s |
| 求和 | \(N-1\) | \((N+1)s\) | 多阶段实现还需 partial 的写读 |
| GEMV | \(2MK\) | \((MK+K+M)s\) | 矩阵通常占据主要流量 |
| GEMM | \(2MKN\) | \((MK+KN+MN)s\) | 多个输出共享输入，存在较高复用机会 |

以 GEMV 为例，当 \(MK\) 远大于其余项时，\(I\approx2/s\)。BF16 存储下约为 1 FLOP/B。方阵 GEMM 边长为 \(n\) 时，\(I\approx2n/(3s)\)，可随规模增长。差别来自同一输入参与多少个输出，而不是 GEMM 使用了不同的数学乘法。

上述流量是理想模型。naive GEMM 的程序可能多次读取同一 A/B 元素；缓存会接住一部分读取，实际 DRAM 流量又可能少于源码访问量。应分开记录算法最小 IO、实现访问模型和硬件实测流量。

> **配图建议 C1｜两类瓶颈与规模变化。** 画对数坐标 roofline，横轴计算强度，纵轴吞吐；一条带宽斜线和一条算力水平线。标 GEMV 与不同规模 GEMM 的教学位置，避免使用未经实测的具体 GPU 数据。旁边画小任务受 launch 限制而低于 roofline 的点。

### 合并访存与 bank conflict

同一个 warp 的线程若读取相邻且合适对齐的地址，硬件通常能用较少内存事务覆盖请求。若每个线程都跨很大步长，可能搬来许多缓存线或 sector，却只用其中少量字节。算法要求读取的元素数没变，实际传输与事务效率却变了。

shared memory 被划分为多个 bank。在经典 32 bank、4 字节字的教学模型下，地址映射可简化为字索引模 32。线程读取不同地址却落在同一个 bank 时可能串行化；同址广播等情况需单独分析，不能把所有同 bank 访问都判作冲突。

这解释了转置优化的两个层次：先通过 shared memory 重排，让 global load/store 都尽量连续；再分析 tile 的 shared-memory 访问是否产生 bank conflict。第二步不自动由第一步解决。

### 驻留资源与 latency hiding

GPU 可以在某个 warp 等待数据时调度其他就绪 warp，这称为隐藏延迟。但可驻留的 warp/block 数受寄存器、shared memory、线程数和硬件上限约束。

occupancy 表示活跃 warp 数相对上限的比例，不等于计算单元利用率。提高它可能提供更多可调度工作，也可能因减少每线程资源引起 spill，或减少数据复用。真正的问题是有没有足够的就绪工作，以及工作能否有效使用执行资源。

设 GPU 有 \(N_{\mathrm{SM}}\) 个 SM，每个能驻留 \(b\) 个当前 kernel 的 block，理想的一批容量为 \(N_{\mathrm{SM}}b\)。grid 的 block 数与这个容量的比值可帮助理解 wave 和尾部利用不足。但资源分配有架构相关取整粒度，\(b\) 不能仅靠一个未经取整的寄存器乘法决定。[CUDA Best Practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)

SMSP 是观察 SM 内子分区调度与执行资源的一种视角。指标分析从执行规模、资源限制、流量/吞吐开始，再看就绪 warp 和 stall 原因；不应凭一个高 stall 百分比直接认定某种优化。

### 关键路径与优化上限

假设一个串行区间里目标部分占比为 \(f\)，该部分加速 \(s\) 倍，则整体理想加速比为：

$$
S=\frac{1}{(1-f)+f/s}.
$$

这是明确分母、没有重叠等条件下的简化模型。若 profiler 分项本来互相重叠，就不能把分项占比直接代入。优化还可能把瓶颈从计算转到通信，使第二轮优化面对不同约束。

**实验：**先预测一个转置版本和一个 GEMM 版本应改善的指标，再 profile。若时间改善但预测指标未变，重新寻找解释，不事后把任何变化都当成成功证据。

**自测：为什么通信字节减少一半，耗时未必减少一半？** 启动、打包、同步、对端到达和共享链路竞争可能占据主要成本；节省的传输还可能本来被计算覆盖。

## 集合通信与分布式协议

### rank 和 group 定义谁参与协作

一个常见训练配置是一个进程控制一张 GPU，进程在通信域中有 rank。global rank 标识全局进程；group rank 标识它在某个子组中的位置。通信操作的参与者由 process group 决定，不一定是全部 GPU。

SPMD 表示多个进程运行相同程序，但每个进程处理不同数据、持有不同状态。相同代码不保证所有进程走相同分支：本地梯度缺失、空 shard 或局部异常都可能让控制流分叉。涉及 collective 时，必须把这些局部差异协调成兼容的协议。

### 从数据需求理解 collective

假设三个 rank 分别持有向量 \(x_0,x_1,x_2\)，形状均为 \(n\)。`all_reduce(SUM)` 让各 rank 得到 \(x_0+x_1+x_2\)，结果仍为 \(n\)；`all_gather` 让各 rank 得到三份输入的拼接，结果为 \(3n\)。前者合并同一逻辑位置的贡献，后者保留不同来源的元素。

`reduce_scatter` 可以理解为先按元素归约，再让每个 rank 保留不同片段。若每份输入长度为 \(3n\)，归约后的全局向量仍为 \(3n\)，每个 rank 最终得到 \(n\)。它常用于“各设备都计算了梯度贡献，但只需保存自己的梯度分片”。

`all_to_all` 允许每个发送者给每个接收者不同片段。设 \(S_{ij}\) 是 rank i 发给 rank j 的元素数，那么 rank i 的发送 split 是矩阵 \(S\) 的第 i 行，rank j 的接收 split 是第 j 列。变长通信至少需要满足每条发送边和对应接收边的长度、类型及布局约定相容。

例如：

$$
S=\begin{pmatrix}1&2&0\\3&1&2\\0&4&1\end{pmatrix}.
$$

rank 1 发送分段为 \((3,1,2)\)，接收分段为 \((2,1,4)\)。发送总长 6，接收总长 7，这并不矛盾。各 rank 的本地发送/接收长度可以不同，但全局边数必须匹配。`all_to_all_single` 的 split 通常按输入/输出第一维计数；展平后才与标量元素数一致。[PyTorch distributed](https://docs.pytorch.org/docs/2.14/distributed.html)

> **配图建议 D1｜同一份输入的四种通信语义。** 画三个 rank 各持红、绿、蓝数组。分别画 all-gather 保留颜色并拼接、all-reduce 对应位置求和、reduce-scatter 求和后分片、all-to-all 按目的地交换。每个输出注明形状，避免只画箭头而看不出是否做了求和。

### 共同调用序列为什么是正确性条件

假设 rank 0 有参数 A 的梯度，rank 1 没有。若 rank 0 进入 A 的 `all_gather`，rank 1 跳过并进入参数 B 的 `all_gather`，两边即使 tensor 长度一样，也可能错误地把不同参数的数据当成同一次通信。错误不一定表现为立即报错，也可能是挂起或静默数据错误。

可以让每个 rank 按共同参数顺序构造标记向量，用 `MAX` 归约得出哪些参数在至少一个 rank 上有梯度。所有 rank 再依据同一个结果安排通信。但 `MAX` 只解决“有人有梯度吗”，没有定义缺失 rank 应如何提供数值：是零贡献、空片段、无数据所有权还是应该报错，必须由项目语义决定。

合并多个参数组的标记也有条件：它们必须有兼容的参与者和统一顺序。不同 process group 不能只因为都使用 `MAX` 就随意拼成一次通信。

### 异步通信不是任意使用结果

`async_op=True` 通常返回代表通信工作的 `Work`，允许宿主继续安排其他工作。消费结果前仍需建立依赖。常见 CUDA 后端下，`Work.wait()` 会为当前 CUDA stream 建立等待关系，不能一概当作整个设备和 CPU 都已彻底同步；后端、阻塞等待配置等会影响具体行为。跨 stream 消费时应按所用版本的文档明确等待位置。

输入/输出 buffer 也必须在通信使用期间保持有效。通信已提交并不意味着发送 buffer 可以立刻被覆盖，接收 buffer 也不能在数据就绪前被下游 kernel 读取。

### ring all-reduce 的成本从哪里来

教学上可把大小为 \(V\) 字节的向量分成 \(p\) 块，在 \(p\) 个 rank 的 ring 上执行 reduce-scatter，再执行 all-gather。每个阶段经历 \(p-1\) 轮，每轮每个 rank 发送约 \(V/p\) 字节，因此每 rank 的总发送量约为：

$$
V_{\mathrm{send}}=2\frac{p-1}{p}V.
$$

接收量相同；若把发送与接收相加，数值会再翻倍。这个公式描述理想单 ring 模型，不是所有 NCCL 算法或拓扑的恒定流量。NCCL 的 collective 语义与内部使用的算法应分开理解。[NCCL collective 文档](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/collectives.html)

简单通信模型 \(T\approx n\alpha+V/B_{\mathrm{eff}}\) 中，\(\alpha\) 表示每次启动的固定成本。合并小消息主要减少第一项；降低 dtype 字节数主要影响第二项；批量打包可能同时减少启动次数并增加拷贝和临时空间。只有把新增成本列出来，才能判断净收益。

### 网络拓扑决定数据实际怎么走

PCIe 和 NVLink 描述设备互联的一部分；RDMA 是远程内存访问机制，InfiniBand/RoCE 是常见网络技术。GPUDirect RDMA 允许支持的设备与配置减少经 CPU 内存中转的路径，但不意味着任意部署都自动获得网卡标称带宽。

设备的有效通信成本还受 GPU/NIC 亲和关系、PCIe 拓扑、NUMA、交换网络和并发流量影响。不能根据“64 张卡”推断具体链路，更不能默认 L40S 项目具有某种 NVLink 互联；应读取机器拓扑和设备规格。

换算时，800 Gbit/s 等于十进制 100 GB/s，但单链路单向带宽和每 GPU 多链路双向聚合带宽不是同一口径。实际 payload 还可能小于链路流量，后者包含协议、冗余路径和其他开销。[GPUDirect RDMA](https://docs.nvidia.com/cuda/gpudirect-rdma/)

> **配图建议 D2｜拓扑与通信量口径。** 画两台服务器，每台两个 GPU、一个 NIC，区分节点内连线与节点间连线。给一条 shard 从源 GPU 到目标 GPU 的路径着色。图例分别列“逻辑数据”“每 rank 发送”“链路实际流量”，明确它们并非同一个计数。

### 实验与自测

实验：用上面的 split 矩阵构造带源 rank、目标 rank、局部序号的数据，核对每个接收段。再人为改变一个接收长度，在运行前通过协议表找出错误，不把死锁当作主要调试方法。

**问：all-gather 调用变为零能否说明没有通信？** 不能。工作可能变为 all-to-all、点对点通信或其他 collective；必须沿完整数据流统计。

**问：通信 kernel 占用 SM 有什么后果？** 常见路径会与计算争用执行和存储资源；重叠可能减少空闲，也可能降低两者速度。具体占用取决于版本、算法和硬件，需实测，不能固定写成某个比例。

## 训练布局与 Muon 项目复盘

### 全局张量和本地张量

DTensor 在逻辑上表示一个全局张量，并用 mesh 和 placements 描述它如何分布在设备上。mesh 是组织通信维度的逻辑结构，不自动保证它与物理拓扑相符。

设全局矩阵 \(X\) 为 \(6\times4\)，分布到三个 rank。`Shard(0)` 可让每个 rank 持有连续两行，local shape 为 \(2\times4\)，行 offset 为 0、2、4。`Replicate` 让每个 rank 都持有完整 \(6\times4\)。`Partial(sum)` 则让每个 rank 持有 \(6\times4\) 的局部贡献，三份相加才是逻辑矩阵。

`to_local()` 取出本地表示，不自动把它变成完整逻辑结果。`redistribute()` 改变 placement，可能触发通信；例如从 shard 到 replicate 通常需要收集，从 partial 到 replicate 需要归约，从 partial 到 shard 可以使用归约分片。[DTensor API](https://docs.pytorch.org/docs/2.14/distributed.tensor.html)

### 为什么 Partial 不能当普通分片处理

若 \(X\) 被互不重叠且完整覆盖的 \(X_r\) 分片，则：

$$
\|X\|_F^2=\sum_r\|X_r\|_F^2.
$$

这是因为每个逻辑元素恰好被平方一次。复制布局会把相同元素重复计数；partial 布局的问题则更根本。若 \(X=A+B\)，那么：

$$
\|A+B\|_F^2=\|A\|_F^2+\|B\|_F^2+2\langle A,B\rangle.
$$

本地先平方再相加会丢掉交叉项。用标量即可看出错误：两个 rank 的贡献分别为 1 和 2，全局值为 3，平方为 9；本地平方和却是 5。除非能证明特殊结构消除了交叉项，否则必须先正确合并逻辑贡献。

> **配图建议 E1｜三种 placement 与范数。** 三列分别画 shard、replicate、partial。shard 用不重叠行块；replicate 用同色完整副本；partial 用同形矩阵并写“求和才得到全局值”。底部分别写“平方和可合并”“避免重复计数”“存在交叉项”。

### DDP 到状态分片

DDP 的典型思路是各 rank 持有完整模型，处理不同样本，反向后同步梯度，使各副本在相同初始状态和更新规则下保持一致。通信同步解决的是数据并行贡献的合并，并不直接降低每个 rank 的模型状态存储。

训练显存包含参数、梯度、优化器状态、激活和临时张量。Adam 类方法通常为参数维护一阶、二阶状态；混合精度实现还可能维护其他副本。状态分片把这些大对象分散存储，需要时再通信。减少参数/状态常驻空间也不会自动消除激活显存。

FSDP 将参数分片保存，在计算某个模块时收集所需参数；反向产生梯度后，按策略归约并分片。这样用通信换取存储节省。[DDP 设计](https://docs.pytorch.org/docs/stable/notes/ddp.html)、[FSDP2](https://docs.pytorch.org/docs/stable/distributed.fsdp.fully_shard.html)

### 参数生命周期不是一张固定时序图

以“前向后重新分片”的教学配置为例：前向前 all-gather 参数 → 执行前向 → 释放完整参数表示 → 反向前重新 all-gather → 执行反向 → 归约并分片梯度 → 在分片状态上执行优化器更新。

若配置保留前向后的完整参数，就可能减少一次后续收集，同时延长完整参数的存活时间。预取尝试把下一模块通信与当前计算重叠，也可能提高瞬时显存。梯度累积和同步策略又会改变梯度的存活与通信时点。

因此要先确认 FSDP1/FSDP2、包装/分组边界、reshard 和 prefetch 配置，再画实际时序。不能因为前向时曾有完整参数，就认为 optimizer 阶段仍持有它。

> **配图建议 E2｜FSDP 的通信显存取舍。** 上下两条时间线分别画“前向后重新分片”和“保留完整参数”的教学配置。标 all-gather、forward、backward、reduce-scatter，并用背景带宽表示完整参数存活区间。说明时间线是示例，不代表所有默认配置。

### HSDP 中什么被复制

用六个 rank 组成二维逻辑 mesh。设两行代表两个副本组，每行三张卡共同保存一份分片模型。第一行 rank 0、1、2 持有 shard 0、1、2；第二行 rank 3、4、5 持有相应副本。

此教学约定下，行内是分片通信组，列内是对应 shard 的复制通信组。全局矩阵范数可以在一行内对三个 shard 求和；若把六个 rank 全部加起来，就把每个逻辑元素计算两遍。具体 mesh 维度如何映射到 shard/replica，要依据实现配置，不能靠横纵方向猜。

梯度既涉及分片组内的贡献组合，也涉及副本间的一致性；平均还是求和、缩放发生在哪一步，都要和损失归一化、batch 定义一致。只看到 collective 名称不足以判断最终梯度尺度。

> **配图建议 E3｜HSDP 数据所有权。** 画 \(2\times3\) rank 网格，列颜色对应 shard。横向括号写“组成一份逻辑模型”，纵向括号写“相同 shard 的副本”。在范数示例中只对一行画求和箭头，再用红色标出全网格求和会重复计数。

### 本地更新成立的条件

如果更新是逐元素函数，例如 \(W_i\leftarrow f(W_i,G_i,M_i,V_i)\)，而这些状态在本地以一致方式对齐，那么各 shard 独立更新可以得到全局逐元素更新的对应片段。AdamW fallback 的本地路径应从这个性质论证。

但全局耦合运算不同。矩阵 NS 中的 \(XX^\top\) 涉及不同行之间的内积；若按任意行分片独立计算，就漏掉跨分片块。只有本地数据恰好覆盖原算法定义的完整矩阵或完整 head 计算单元，才可能直接本地执行。

本地“完整”的判断因此涉及逻辑边界、offset、shape 和原算法的分组方式。如果原本对整矩阵做 NS，改成逐 head NS 通常改变算法；不能把它当作纯系统快路径。

### NS owner 为什么需要成本模型

你已经掌握 Muon 算法，这里只连接系统成本。对转置处理后 \(X\in\mathbb{R}^{r\times c}\)、\(r\le c\)，考虑：

$$
A=XX^\top,\qquad X' = aX+(bA+c_0A^2)X.
$$

这里 \(c_0\) 是多项式系数，与列数 \(c\) 区分。三个主要矩阵乘的成本分别约为 \(2r^2c\)、\(2r^3\)、\(2r^2c\)，每轮合计 \(4r^2c+2r^3\)，尚未计逐元素工作。

相同元素数可以有很不同的计算量。例如 \(64\times1024\) 与 \(256\times256\) 都有 65536 个元素，但按该公式每轮约为 17.30 MFLOPs 与 100.66 MFLOPs。按矩阵个数甚至元素数均分，都可能产生明显不平衡。

owner 教学方案把每个完整计算单元分配给一个 rank：输入 shard 发到 owner → owner 重建并计算 → 结果发回需要它的 rank。它消除的是多个 rank 对同一完整输入重复计算的部分，同时新增打包、路由、等待和 owner 显存压力。

可以先按估计成本降序，把下一个矩阵分配给当前累计负载最小的 owner。这是易于解释的启发式，不保证全局最优；矩阵 shape 的硬件效率、通信拓扑和超大单任务都会使 FLOPs 模型产生偏差。

> **配图建议 E4｜owner 数据流与负载。** 左侧画六个不同形状的逻辑矩阵，每个由三色 shard 组成；中间画三个 owner，把各 shard 按矩阵汇集；右侧画结果切片回传。下方用柱状图对比“按个数均分”和“按估计成本分配”的教学负载，明确数值非项目测量。

### 分片回缩为什么只需要少量统计量

以下使用一个教学更新，不能直接替代项目的真实 MuonH 公式。设候选权重 \(C=W-\eta U\)，希望把非零 \(C\) 缩放到 Frobenius 范数为 \(\rho\) 的球面：

$$
W'=\rho\frac{C}{\|C\|_F}.
$$

若各 rank 持有互不重叠的 \(C_r\)，可先计算 \(q_r=\|C_r\|_F^2\)，归约得到 \(q=\sum_rq_r\)，再各自更新 \(W'_r=\rho C_r/\sqrt q\)。只要后续所需全局信息就是这个统计量，就不必收集完整 \(C\)。

如果目标是投影到半径为 \(\rho\) 的球内，则缩放系数是 \(\min(1,\rho/\|C\|_F)\)，含义不同。零范数处理、epsilon、逐 head 范数、衰减位置和状态更新都必须按真实公式确定。数学上的平方和恒等式也不保证浮点逐位一致。

分片回缩进一步改变 NS 结果的消费方式。若每个 rank 只需自己的更新切片来构造 \(C_r\)，随后用少量统计量求缩放系数，owner 就可能只回传所需切片。这个收益依赖后续算子的数据需求，不能孤立地删掉完整结果回传。

> **配图建议 E5｜完整回缩与分片回缩。** 左图把所有候选权重收集成大矩阵再求范数；右图各 shard 计算平方和，仅汇合几个标量，再把同一缩放系数广播或归约结果共享到各 shard。箭头粗细表示数据量类别，不使用未经测量的耗时比例。

### 缓存和本地 fallback 的工程边界

布局缓存适用于 shape、offset、mesh、参数身份等在稳态保持不变的情况。缓存键必须能区分影响结果的配置，失效条件要涵盖参数替换和布局变化。恢复训练时是重建布局还是复用对象，也影响失效规则。

系数序列缓存与 tensor 结果缓存不同。前者复用确定配置下的构造结果，后者可能保留设备存储并引入数据时效问题。容量上限是资源约束，不自动证明缓存键正确或命中一定有收益。

本地 AdamW 路径要核对参数、梯度、一阶/二阶状态和计步是否一致。`torch.no_grad()` 避免把更新构造成需要追踪的梯度图，但不会自动保证数值语义和存储别名正确。绕过 DTensor 分派、使用 `foreach`、使用 fused kernel 分别作用于不同层次，可以组合，也可能收益重叠。

### 项目验收与自测

把每个优化放回真实一步更新中，记录输入输出 shape/dtype、group、通信次数、buffer 最后使用点和结果误差。性能按单项及关键组合做消融，不能直接相加各自收益。

**问：NS 为什么一般不能各 shard 独立做，范数却可以？** NS 包含跨分片耦合的矩阵乘；对不重叠 shard 的平方范数是可加统计量。区别在运算结构，不在是否都使用 GPU。

**问：owner 方案在三卡有效，64 卡为什么可能无效？** 矩阵数量与形状、任务粒度、跨节点路由、打包、最慢 owner 和内存峰值都可能变化。需要同配置端到端测量。

**问：现有项目数字如何准备面试证据？** 每条数字附配置、对照路径、统计边界、原始日志、结论和未验证范围。特别区分 NS 调用数、logical payload、存储分配数、CPU 时间与完整训练吞吐。

## 从访存映射到归约和 softmax

### elementwise 建立索引与边界意识

对 \(y_i=f(x_i)\)，各输出独立，最直接的做法是让不同线程处理不同 \(i\)。一维 launch 中常用 \(i=\text{blockIdx.x}\times\text{blockDim.x}+\text{threadIdx.x}\)。grid 向上取整后，尾部线程可能满足 \(i\ge N\)，因此访问前需要边界条件。

数据特别多时，一个线程可按整个 grid 的线程总数为步长循环处理多个位置，即 grid-stride loop。它使 launch 规模与数据规模解耦，但并不免除边界检查。二维和非连续数据则要回到 stride 地址公式，不能把逻辑索引直接当连续地址。

考虑 \(t=ax\)、\(y=t+b\)。两个独立 kernel 会写出再读回 \(t\)，融合后可以在寄存器中完成中间运算，只写最终结果。收益来自减少中间 IO 和 launch，计算公式基本没变。若融合导致寄存器压力过大、破坏并行性，收益也可能消失。

### transpose 的困难在写入方向

设输入 \(A\) 是行主序 \(M\times N\)，输出 \(B\) 为 \(N\times M\)，满足 \(B_{j,i}=A_{i,j}\)。若相邻线程沿输入 j 方向读取，它们访问相邻地址；直接写 \(B_{j,i}\) 时，相邻线程相差 M 个元素，写入可能变得分散。

shared-memory tile 让两个方向解耦：先由一组线程合并读取输入 tile，存入 shared memory；完成 block 同步后，重新安排线程从 tile 的另一方向读取，再合并写入输出。正确索引不仅要交换 tile 内坐标，也要交换 tile 在大矩阵中的 block 坐标。

在经典 FP32、32 bank 教学模型中，\(32\times32\) tile 的按列访问可能让线程落到同一 bank；为每行增加一个 padding 元素形成 \(32\times33\)，能改变行起点的 bank 映射。但这个结论依赖元素宽度、访问形式和硬件，不能把加一列当成所有情况的定理。

边界 tile 的读写需要分别检查源矩阵和目标矩阵坐标；block 同步则必须由应参与的线程一致到达。不能让少数边界线程提前返回，使其余线程独自进入需要全 block 参与的屏障。

> **配图建议 F1｜转置如何重排访问。** 上半图画 naive：32 个线程从一行连续读取，却分散写到 32 行。下半图画 tiled：连续读入 shared tile，经过同步后换方向连续写出。另加一个小图标出 32 与 33 的行跨度如何映射到 bank。

### reduce 为什么需要分层

求和 \(s=\sum_{i=0}^{N-1}x_i\) 的输入很多、输出很少。若一个线程顺序求和，其他线程没有工作；若所有线程直接写同一个结果，会产生冲突。因此通常先各线程计算局部和，再以树形结构合并。

以 8 个值为例，第一层形成 4 个两两和，第二层形成 2 个和，第三层得到最终值。串行依赖深度从 8 量级降为 \(\log_2 8\)，总加法数仍约为 7。真正实现中还要考虑数据加载、同步和线程利用。

warp 内可通过 shuffle 交换寄存器值，减少 shared memory 往返。block 内多个 warp 可各自产生一个 partial，写入 shared memory，同步后再由一个 warp 合并。shuffle 的参与 mask、源 lane 是否有效、边界线程如何贡献都必须明确；不能无条件对部分活跃 warp 使用全参与假设。

当 N 很大时，让多个 block 各自产生一个 partial，再启动第二个 kernel 合并。第二次 launch 提供自然的跨 block 阶段边界。atomic 也可累积，但可能有竞争、非固定归约顺序，并不总比两阶段更快。

> **配图建议 F2｜局部归约到全局归约。** 画“每线程局部和 → 每 warp 一个值 → 每 block 一个值 → 第二个 kernel 最终值”的漏斗。标出 shuffle、shared memory 屏障和 kernel 边界，避免画成不同 block 用普通屏障直接同步。

### stable softmax 把归约与逐元素运算连接起来

对一行 \(x_1,\ldots,x_N\)，softmax 为 \(p_i=e^{x_i}/\sum_je^{x_j}\)。大正值可能导致指数溢出。设 \(m=\max_jx_j\)，同时约去分子分母中的 \(e^m\)，得到：

$$
p_i=\frac{e^{x_i-m}}{\sum_je^{x_j-m}}.
$$

这保持数学结果不变，并使每个指数输入不大于零。实现包含 max reduce、逐元素 exp、sum reduce、归一化，正好组合了前面的两类基本能力。

若一行能合理地驻留在近端存储，可在一个 kernel 内保留中间结果，避免独立阶段反复读写整行。行太宽时，寄存器和 shared memory 压力增大，可能需要多阶段设计；“融合”不能无限扩大。[Triton fused softmax](https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html)

mask 通常让无效位置不参与最大值和指数和，但全行无有效元素必须另作约定；直接计算 \(-\infty-(-\infty)\) 会产生无效数。教学实验应先限定每行至少有一个有效元素，再扩展边界语义。

**实验：**transpose 覆盖矩形和非整 tile；reduce 覆盖小规模、跨多个 block 和大动态范围数值；softmax 覆盖短行、宽行和 mask。将参考结果、误差容限及支持范围写在同一张实验卡上。

**自测：softmax 为什么不能只凭 FLOPs 判断性能？** exp、比较、除法、归约与数据传输使用不同资源；它们都写成常数次 FLOPs 会掩盖真正的吞吐和依赖限制。

## GEMV 到 GEMM 与 Triton 分块

### GEMV 的线程安排取决于矩阵布局

GEMV 计算 \(y=Ax\)，其中 \(A\) 为 \(M\times K\)，\(x\) 为 K，输出为 M。每行是一个长度 K 的点积。

若每线程负责一整行，在同一循环步，warp 各线程可能分别访问不同的行，地址相隔 K 个元素。改成一个 warp 合作处理一行，让相邻 lane 处理相邻 k，就可能改善矩阵读取，再通过 warp 归约形成一个输出。代价是新增线程间合并，且当 M 很小或 K 很短时工作分配未必合适。

向量 x 会被多行使用，可由缓存或显式策略复用；但矩阵 A 的每个元素通常只为一个输出贡献一次。这使 GEMV 很难像大 GEMM 那样通过输入复用获得高计算强度。若矩阵换成转置布局，适合的线程映射也会变，不能只改一个 shape 而沿用原性能结论。

### GEMM 的核心是多个输出共同使用输入

GEMM 为 \(C=AB\)，A 为 \(M\times K\)，B 为 \(K\times N\)，C 为 \(M\times N\)。元素 \(C_{ij}\) 是 A 的第 i 行与 B 的第 j 列的点积。

如果每个输出独立从显存读取 A/B，许多元素会重复加载。分块方法让一个工作单元负责 \(B_M\times B_N\) 个输出，每次加载 \(B_M\times B_K\) 的 A tile 和 \(B_K\times B_N\) 的 B tile，更新整块输出。

这次加载搬入约 \((B_MB_K+B_KB_N)s\) 字节，完成约 \(2B_MB_NB_K\) FLOPs，因此忽略最终输出时：

$$
I_{\mathrm{tile}}\approx\frac{2B_MB_N}{s(B_M+B_N)}.
$$

若 \(B_M=B_N=T\)，则 \(I_{\mathrm{tile}}\approx T/s\)。它解释 tile 增大如何提高局部复用，但不代表整个 kernel 的实际 DRAM 强度，因为不同工作单元仍可能重复读 A/B，而 L2 又可能接住其中一部分读取。

> **配图建议 G1｜一个输出 tile 的累积。** 左边画 A 的一条 \(B_M\times K\) 横带，上方画 B 的一条 \(K\times B_N\) 竖带，交汇处画 C tile。沿 K 方向用三个颜色依次选出 A/B 小块，箭头指向同一个输出累加器，说明不是每个 K tile 写一个最终输出。

### tile 参数为何需要取舍

更大的输出 tile 需要保存更多累加器；更多 pipeline stage 可能同时保存更多加载数据。二者可以提高复用或覆盖延迟，也可能增加寄存器/shared memory，占用更多资源，减少同时驻留的 block，甚至引起 spill。

tile 的维度还应匹配 shape。大方形 tile 在细长矩阵上可能有大量无效位置，mask 虽然保证正确性，却不会让所有浪费自动消失。小矩阵可能 block 数不足，单个 tile 很高效也无法填满整个 GPU。

Tensor Core 提供特定矩阵运算路径，能提高相应 dtype/形状下的吞吐；但调用矩阵运算 API 不代表整个 kernel 已高效。数据供给、累加器、布局转换和尾部工作仍可能限制速度。

### 从 Triton program 理解实现

Triton 的一个 program 通常处理一块逻辑数据。`program_id` 决定它负责哪个输出 tile；offset 表达 tile 中每个元素对应的地址；mask 处理越界；`tl.load`/`tl.store` 描述读写；`tl.dot` 表达块矩阵乘。编译器进一步映射到 warp、寄存器和硬件指令。

典型 GEMM 的逻辑是：确定输出行列 → 初始化 FP32 累加器 → 沿 K 加载 A/B tile → 累积块乘法 → 按输出 dtype 转换并写回。理解这条数据流后，再研究 `num_warps`、pipeline、程序顺序与 autotune。[Triton GEMM](https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html)

程序重排可能让相邻执行的 tile 更容易复用同一 A 或 B 的缓存数据。它影响 CTA/program 之间的局部性，和单个 tile 内共享数据是两个层次。

**实验：**固定 dtype 和连续布局，对三种 shape 比较至少两组 tile。记录时间、误差、寄存器、shared memory、grid 大小与实际流量。调参目标是缩短时间，并能解释胜负，不是让某个资源指标达到最大。

**自测：为什么同样的 FLOPs，两种矩阵形状耗时不同？** tile 利用、并行规模、Tensor Core 路径、缓存复用、尾部 mask 和资源约束都可能不同。FLOPs 只衡量数学工作量的一部分。

## Transformer 形状与 FlashAttention

### 先把模型还原成张量操作

设输入隐藏状态为 \(X\in\mathbb{R}^{B\times T\times D}\)，B 为 batch，T 为 token 数，D 为隐藏宽度。线性投影可将前两维视作 \(BT\)，变为 \((BT\times D)(D\times D_{\mathrm{out}})\)。这就是为什么 token 数影响 GEMM 的行维和权重复用。

一个常见 Transformer block 包括归一化、Attention、输出投影、残差，以及另一个归一化和 MLP；具体采用 pre-norm/post-norm、LayerNorm/RMSNorm 和门控 MLP 由模型决定。残差要求相加两侧 shape 一致，通常回到 \(B\times T\times D\)。

MLP 常把隐藏宽度扩展到中间维度再投回；门控结构会多出一个投影和逐元素乘法。归一化通常涉及最后一维的统计归约。因此，前面的 GEMM、reduce 和 elementwise 已覆盖大部分基础计算结构。

### Q K V 与 head 的形状

设 query head 数为 \(H_q\)，KV head 数为 \(H_{kv}\)，每个 head 的宽度为 d。可用以下逻辑布局讲解：

$$
Q:[B,T_q,H_q,d],\qquad K,V:[B,T_k,H_{kv},d].
$$

实际 kernel 可以使用不同维度顺序，必须同时看 stride。MHA 通常 \(H_q=H_{kv}\)；MQA 令 \(H_{kv}=1\)；GQA 让一组 query heads 共享一个 KV head，常见分组数为 \(H_q/H_{kv}\)。KV cache 的容量按 KV head 数计算。[GQA 论文](https://arxiv.org/abs/2305.13245)

RoPE 对 Q/K 的成对通道施加与位置有关的旋转，使点积能表达相对位置信息；它通常不改变张量 shape。缓存的是何种处理后的 K，要看模型实现。关键是新 query 与历史 key 必须使用一致的位置约定。

### 普通 Attention 为什么产生大中间矩阵

先只看一个 head，令 \(Q\) 为 \(N_q\times d\)，\(K,V\) 为 \(N_k\times d\)。定义：

$$
S=\frac{QK^\top}{\sqrt d}+M,\qquad
P=\operatorname{softmax}_{\mathrm{row}}(S),\qquad
O=PV.
$$

mask M 让不允许关注的位置不参与 softmax。S、P 的 shape 都是 \(N_q\times N_k\)，O 为 \(N_q\times d\)。自注意力 prefill 常有 \(N_q=N_k=N\)，中间矩阵随 \(N^2\) 增长。

例如单 head、N=4096，得分矩阵包含约 1678 万元素，BF16 存储约 32 MiB；还没有计 batch、多个 head 或其他中间结果。这里的计算量仍然存在，但是否必须把完整 S/P 写入显存，是可以改变的实现选择。

> **配图建议 H1｜Attention 的形状与 IO。** 按 QK 转置乘、softmax、PV 三段画矩阵，分别标 \(N_q\times d\)、\(N_k\times d\)、\(N_q\times N_k\)、\(N_q\times d\)。用红框突出 S/P 中间存储，用蓝色标最终必须输出的 O。

### online softmax 合并的是统计量

分块计算的难点是 softmax 分母依赖整行。对每个 tile 独立归一化，再拼接输出，会让每个 tile 各自概率和为 1，破坏整行分布。

处理一行得分时，可以维护已处理部分的最大值 m 和归一化尺度下的指数和 \(\ell\)。对于新的得分块 \(s_j\)，更新为：

$$
m'=\max(m,\max_js_j),\qquad \alpha=e^{m-m'},
$$

$$
\ell'=\alpha\ell+\sum_je^{s_j-m'}.
$$

为什么旧和要乘 \(\alpha\)？旧 \(\ell\) 使用 \(e^m\) 作为共同缩放尺度，新尺度变成 \(e^{m'}\)，所有旧项必须乘 \(e^{m-m'}\) 才能和新项相加。

Attention 还维护未归一化的向量累加器 z，shape 为 d：

$$
z'=\alpha z+\sum_je^{s_j-m'}V_j,
\qquad O=\frac{z}{\ell}\quad\text{在全部块处理完后}.
$$

旧 z 也必须修正尺度；只更新分母而不更新输出累加器会得到错误答案。初始化可使用空状态，再从第一个有效块建立统计；实际实现需要正确处理全 mask 块，避免无效的无穷运算。

### 一个完整手算例子

令四个得分为 \((\ln1,\ln2,\ln3,\ln4)\)，对应标量 V 为 \((1,2,3,4)\)。完整 softmax 权重正比于 \((1,2,3,4)\)，所以输出为 \((1+4+9+16)/10=3\)。

分成两个 tile。第一块结束时 \(m=\ln2\)，\(\ell=1/2+1=1.5\)，\(z=(1/2)\times1+1\times2=2.5\)。第二块使最大值变为 \(\ln4\)，故 \(\alpha=1/2\)。新分母为 \(0.5\times1.5+3/4+1=2.5\)，新累加器为 \(0.5\times2.5+(3/4)\times3+1\times4=7.5\)，最终仍为 3。

> **配图建议 H2｜两个 tile 的尺度修正。** 左右画两个得分块，下方各列 m、指数和、输出累加器。中间画“最大值从 ln2 变为 ln4”，用两条箭头把旧 \(\ell\) 和旧 z 同时乘 1/2。末尾画 7.5/2.5=3，并与完整 softmax 对照。

### FlashAttention 把统计合并放进分块矩阵乘

对一块 Q，逐块读取 K/V，计算一个小得分块，更新 m、\(\ell\)、z，最终只写出 O。这样不必把完整 \(N_q\times N_k\) 中间矩阵物化到显存。它仍计算相同 Attention 语义，在有限精度下数值可能因运算次序而变化，不等于和参考路径逐位一致。[FlashAttention](https://arxiv.org/abs/2205.14135)

FA2 进一步减少非矩阵乘工作，改进沿序列维度的并行划分和 warp 间工作分配，降低某些共享内存通信成本。理解重点是“谁负责哪块输出，谁共享哪些统计量，哪里需要同步”，而不是背一个速度倍数。[FlashAttention-2](https://arxiv.org/html/2307.08691v1)

causal prefill 中，第 i 个 query 只能读取允许位置的 key，通常体现为三角区域。完全在未来区域的 tile 可跳过，跨对角线 tile 需要元素级 mask。chunked prefill 的 query 是完整上下文中的一段，判断应使用全局位置，不能仅比较 tile 内坐标。

FA 避免了大中间结果，但不同 Q tile 可能重复读取 K/V，实际 IO 取决于分块、缓存和调度。因此不能直接把 Q/K/V 输入大小之和写成所有 HBM 流量。

**实验：**先完成上述手算，再实现限定 shape/dtype 的非 causal 前向，随后加入 causal。对照输出误差、边界 mask、临时存储与时间；参考 [Triton fused attention](https://triton-lang.org/main/getting-started/tutorials/06-fused-attention.html)，并固定教程对应版本。

**自测：为什么在线统计只存很小的状态，却能得到完整输出？** 每个得分块对分母和加权分子的贡献可以在统一指数尺度下相加；m 负责数值稳定性，\(\ell\) 和 z 保留最终归一化所需的充分信息。

## 编译与 CUDA Graph

### 一条运算链可以在不同层次优化

考虑由十几个逐元素运算构成的更新。它可能依次经过 Python 解释、框架分派、算子实现选择、kernel 提交、GPU 执行。即使每个 kernel 都很快，前面几层的固定开销仍可能让 GPU 等待。

本地 DTensor fallback 减少某些布局分派和包装开销；融合让多个算子共享中间值，减少 kernel 数和 IO；编译可以分析图并生成更适合的执行代码；CUDA Graph 把一次满足约束的设备执行组织捕获为可重放结构，减少重复提交成本。这些技术的作用位置不同。

### torch.compile 的几个组成部分

TorchDynamo 在 Python 执行过程中捕获可以编译的图，并记录保证该图适用的条件，即 guards。训练场景中 AOTAutograd 参与前向/反向图的处理。TorchInductor 进一步进行图级优化、调度和代码生成；GPU 路径可能生成 Triton kernel，也可能调用现有库，不是所有计算都变成自写 Triton。

如果控制流或操作无法纳入同一图，可能产生 graph break，将执行拆成多个区间。输入 shape、dtype 或其他受 guard 约束的属性变化，可能导致复用失效或重编译。动态 shape 支持与约束随后端和版本变化，不能把一次固定 shape 编译成功外推到所有请求。[PyTorch compiler](https://docs.pytorch.org/docs/stable/torch.compiler.html)、[`torch.compile`](https://docs.pytorch.org/docs/stable/generated/torch.compile.html)

编译首次耗时通常显著高于稳态。评价收益时，应分别看编译成本、后续执行次数和每次节省量；只有执行足够多次，前期成本才可能被摊薄。

### CUDA Graph 为什么关注地址

普通执行每次都需要逐项提交工作。捕获后，graph 保存设备工作及其依赖，重放时用更少的宿主交互启动同样的执行组织。它不会自动把数学算法换成另一个算法，也不会必然融合已有 kernel。

被捕获的 kernel 参数包含内存地址等信息。常见使用方式是准备稳定的输入输出缓冲区，把本次数据写入固定位置，再重放 graph。形状和控制流变化需要满足 graph 的支持约束，工程上常按 batch/shape 分档捕获，并用 padding 或不同 graph 处理请求。[PyTorch CUDA Graphs](https://docs.pytorch.org/docs/2.14/notes/cuda.html#cuda-graphs)

这里重新用到了 A 章：一个缓冲区既要地址稳定，又要生命周期覆盖重放；旧输出如果被下一次重放覆盖，调用方就不能继续把它当作独立结果使用。

> **配图建议 I1｜三种执行组织。** 并排画 eager 的多次 CPU 提交、融合后的少数 kernel、CUDA Graph 的一次 replay 触发多个节点。使用不同颜色标“kernel 内容变化”和“提交方式变化”，不要把 compile 与 graph 画成互斥选项。

### 如何设计有解释力的对照

选择固定 shape 的短运算链，分别测 eager、手动融合、compile、graph，以及适用时的组合。每种先验证输出，再分开首次处理与稳态时间；用 nsys 查看提交间隙，用内存/算子记录确认中间 IO 是否变化。

如果 compile 减少 kernel 数而 graph 主要压缩空洞，两者的收益来源就不同。若原工作是一段饱和的大 GEMM，CPU 原本不在关键路径上，减少提交也可能几乎不改变时间。

**自测：CUDA Graph 为什么不能直接解决所有动态推理问题？** 请求组成、shape、KV 地址和控制流不断变化，需要引擎先将其组织为可重放的执行形式；捕获本身不负责请求调度和 KV 管理。

## Prefill Decode 与 KV 生命周期

### 自回归生成中的两种计算形态

生成模型先读取 prompt，根据最后位置的输出分布采样下一个 token；随后把新 token 送入模型，重复生成。prefill 处理尚未计算的新 prompt 位置，decode 在已有上下文状态上推进生成。

对没有额外复杂结构的 causal Transformer，历史 token 在某层的 K/V 不依赖未来 token。保存它们后，下一步只需计算新增位置的 Q/K/V，并让新 Q 关注历史与新增 K/V，无需重新计算所有历史位置的表示。

一次 prefill 可令 \(T_q=T_k=S\)，而一次普通 decode 每个请求常有 \(T_q=1\)、\(T_k\approx S+1\)。由此可见，decode 不是“没有矩阵运算”，而是投影 GEMM 的 token 维较小、Attention query 维较小，但读取的历史维可能很大。

### 线性投影与 Attention 要分别建模

一次线性投影处理 T 个 token，权重 shape 为 \(D_{in}\times D_{out}\)，主要 FLOPs 为 \(2TD_{in}D_{out}\)。若权重读取主导并理想读一次，忽略激活流量：

$$
I_{\mathrm{weight}}\approx\frac{2T}{s}.
$$

T 增大使同一权重服务更多 token，这解释 batching 对低 batch decode 的潜在价值。但更多并发请求需要更多 KV，可能延长排队或单次迭代时间；吞吐提升与单请求延迟不是同一个目标。

Attention 则还随历史长度增加 KV 访问。prefill 的较大 query 数提供更多复用，decode 的少量 query 可能主要读取大量历史 K/V。不同模型、batch、量化、长度和硬件会改变瓶颈，因此应从实际 shape 和 profile 下结论。

> **配图建议 J1｜prefill 与 decode 的矩阵形状。** 左侧画多个 prompt token 组成高矩阵参与权重乘法，Attention 为近方形；右侧画每请求一个新 token，投影矩阵较矮，Attention 为细长矩阵。另画 decode batch 扩大后矩阵行数增加，旁注 KV 容量也随请求数增长。

### KV 容量如何估算

每层每个 token 保存一份 K 和一份 V。设层数为 L、历史长度为 S、KV head 数为 \(H_{kv}\)、head dimension 为 d、每元素 s 字节，则单请求未计分页、padding、复制和量化元数据时：

$$
V_{\mathrm{KV}}=2LSH_{kv}ds.
$$

例：L=32、S=4096、\(H_{kv}=8\)、d=128、BF16，则为 536870912 字节，即 512 MiB。若 16 个请求都独立保存同长度 KV，总逻辑容量为 8 GiB。共享前缀、shard、replica 和物理布局会改变实际占用。

KV 通常按最大可用设备空间规划池，而每个请求逐步申请其中的块。不能把池预留量、正在被请求引用的块和逻辑 KV 字节数混为一谈。

### 分页解决连续分配与碎片问题

若给每个请求预留一段足够容纳最大长度的连续空间，短请求会浪费容量；若不断扩大连续区域，又可能需要搬迁。PagedAttention 的思路是把逻辑序列切成固定 token 数的块，物理块可分散放在池中，通过 block table 查找。[PagedAttention 论文](https://arxiv.org/abs/2309.06180)

设每块容纳 b 个 token，逻辑位置 t 对应块号 \(\lfloor t/b\rfloor\) 和块内偏移 \(t\bmod b\)。block table 将逻辑块号映射到物理块号，kernel 再结合 layer/head/通道布局计算地址。

例如 b=4，请求已有 10 个 token，需要 3 个块；它们可映射到物理块 7、2、9，最后一个只用两格。新增 token 先填剩余空间，用满后再申请新块。分页减少外部连续分配困难，但末块仍可能有内部碎片，也增加地址映射和管理工作。

> **配图建议 J2｜block table 与增长。** 上方画请求 token 0–9 分成三个逻辑块，下方画非连续物理块 7、2、9。中间放映射表；用虚线表示末块空闲位置。右侧再画 token 10、11 填入原末块、token 12 申请新块的过程。

### continuous batching 管理随时间变化的请求集合

静态 batch 常让一组请求一起开始，短请求完成后，空出的槽位不能立即被新请求充分利用。continuous batching 在迭代边界重新组合活跃请求，让完成者退出、等待者进入。

调度器需要同时考虑可用 token budget、KV 容量、请求状态和时延目标。一个长 prompt 可能消耗很多本轮 token 预算；一个已有长历史的 decode 请求虽然只生成一个新 token，却要读取大量 KV。因此“本轮 token 数”不是完整成本模型。

教学例子：A、B 正在 decode，C 是等待 prefill 的长请求。若本轮全部执行 C，A/B 的下一 token 会等待；若永远优先 A/B，C 的首 token 可能等待过久。调度是在吞吐、公平性、TTFT 和 ITL 之间分配有限执行时间。

TTFT 是从定义的请求起点到首 token 的时间；ITL 是相邻输出 token 之间的间隔；TPOT 常概括首 token 之后的平均每 token 时间；吞吐是单位时间产出的 token 数。测试必须说明起点是否含排队、分词和网络，以及吞吐统计的是输入、输出还是总 token。

### chunked prefill 缩短单次占用

把长 prompt 的 prefill 分成多个 chunk，可以在迭代间插入 decode 工作。每个 chunk 的 token 仍需关注允许的历史上下文，不能把 chunk 当成独立句子重新开始。

较小 chunk 可以降低一次长 prefill 阻塞其他请求的时间，但会增加调度轮次和提交次数，还可能使 GEMM 变小、降低复用。较大 chunk 可能提高计算效率，却加重已有 decode 的延迟。调节 token budget 时，应同时观察 TTFT、ITL 分布、吞吐和内存，而非只看平均步时。[vLLM 优化与调度](https://docs.vllm.ai/en/latest/configuration/optimization/)

> **配图建议 J3｜长 prefill 对 decode 的干扰。** 画同一组 A/B decode 和 C prefill 的两条时间线：整段 C 与分块 C。每个 decode 输出时点画圆点，让读者直接看到 ITL；把 C 的首 token 位置也标出，展示不同目标可能相互牵制。

### 前缀复用与回收

当请求共享同一模型和有效执行条件下的相同 token 前缀，前缀 K/V 可以复用。命中让新请求跳过部分重复 prefill，但后续 decode 仍需读取这些 KV 参与 Attention。相同后缀但前缀不同通常不能这样复用，因为该后缀的隐藏状态受此前上下文影响。[vLLM prefix caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/)

实现中可用块 hash 将前缀链与内容关联，或者用 radix tree 组织公共前缀路径。hash/key 还必须区分会影响结果的模型配置、适配器等条件；仅用肉眼看到的字符串相同不充分。RadixAttention/Radix Cache 的学习重点是共享节点、引用、命中与淘汰，而不是把“树”当作一种新 Attention 数学公式。[SGLang 论文](https://arxiv.org/abs/2312.07104)

多个请求共享块时，用引用计数或等价机制避免提前释放。若实现允许共享尚未填满的块，分支写入前可能需要 copy-on-write，防止修改其他请求的数据。只缓存完整块的方案可能在这一点采用不同策略。

结束请求会释放它的引用，但块可能继续作为可复用缓存保留；真正容量不足时再淘汰未被活跃请求依赖的缓存。cache 命中率、可用容量与排队因此彼此关联。[vLLM prefix cache 设计](https://docs.vllm.ai/en/latest/design/prefix_caching/)

### 实验与自测

实验：设块大小为 4、物理池有 8 个块，模拟两条共享 8-token 前缀的请求和一条独立请求，逐轮记录 block table、引用计数、KV 增长和回收。再加入长 prefill，比较两种 token budget 的调度表。

**问：分页和前缀缓存分别省什么？** 分页改善物理存储管理和容量利用；前缀缓存复用已完成的计算与其 KV。两者可结合，但不是同一项优化。

**问：缓存命中率提高，服务延迟一定下降吗？** 未必。缓存占用、路由、获取成本、排队和剩余计算仍可能主导。需要观察完整请求路径。

## 从轻量框架到生产代码

### 先定义系统里流动的状态

推理引擎不只是调用模型。它需要知道每条请求已经处理多少 prompt、已经产生多少 token、有哪些 KV、下一步能否运行、是否已结束。这些状态跨越多次模型调用，不能只保存在一次 forward 的局部变量里。

可先用一张概念表建立全局视角。下面的对象名称用于教学，不保证与某个版本的类名完全一致。

| 对象 | 保存什么 | 决定什么 |
|---|---|---|
| request/sequence | token、采样参数、已计算长度、结束状态 | 请求进度与语义 |
| scheduler | 等待/运行集合、预算和策略 | 本轮执行哪些请求、多少 token |
| cache manager | block table、空闲块、共享关系 | KV 存在哪里，何时可释放 |
| model runner | 模型、输入组织、设备执行配置 | 如何把调度结果变成实际计算 |
| sampler | logits、采样配置、随机状态 | 下一个 token 或一组候选 |
| engine | 上述组件的调用与结果汇总 | 完成一次服务迭代 |

### 跟踪一条请求的完整生命周期

请求进入后先获得 token 序列和采样参数，并进入等待状态。调度器检查 token budget 与 KV 容量，决定本轮计算范围；cache manager 为未命中的位置分配物理块；runner 构造 token、position、序列长度、slot mapping 和 block table 等执行输入。

模型执行时，当前 token 的 K/V 写入对应槽位，Attention 通过元数据找到需要的历史 KV。最终 logits 经 sampler 得到新 token，engine 更新请求长度、完成状态和输出。若达到 EOS、长度上限或取消条件，就释放请求依赖的资源；未结束者进入后续迭代。

这些步骤存在明确的数据依赖：不能先让 runner 写 KV 再决定目标槽位；不能把请求标为完成并回收块后，仍有未完成 GPU 工作使用这些块。A、B 章的生命周期原则在系统层再次出现。

> **配图建议 K1｜请求时序图。** 纵向泳道设 request、scheduler、cache manager、runner/GPU、sampler。横向按时间画“接纳、分块、执行、采样、更新、回收”；在 runner 调用旁注明 token 数和 KV slot 信息。用虚线区分控制消息与实际张量数据。

### 轻量框架阅读应该留下什么

先选 [Nano-vLLM](https://github.com/GeeeekExplorer/nano-vllm) 或 [Mini-SGLang](https://github.com/sgl-project/mini-sglang) 中一个固定 commit。目标是用少量对象解释完整路径，而非尽快读完所有行。

第一遍只找入口、主循环和对象关系；第二遍沿一条请求记录状态变化；第三遍换成两条不同长度请求，观察 batching 和 KV 回收；第四遍再定位一个性能机制，例如 prefix cache 或 graph replay。

每读到一个分支，写出它在保护什么不变量。例如“可用物理块不足”为什么暂停接纳；“前缀命中”使已计算长度怎样变化；“请求完成”为什么只是减少引用而不总是立即销毁块。

### 生产框架按问题向下追

轻量框架形成全局图后，在 vLLM 或 SGLang 中选择一个主框架。先从功能文档确认语义和配置，再找入口符号、状态对象、执行路径、测试及统计指标。不要因为名字相同就假设两个框架有完全相同的数据结构。

第一次只追三件事：chunked prefill 如何计算本轮 token budget；prefix cache 如何命中、增加引用和淘汰；runner 如何把 scheduler 的决定转成具体 KV 写入与 Attention 输入。

代码证据卡要包含版本/commit、入口符号与 `file:line`、关键对象、前后状态、张量 shape、调用链和测试位置。这样面试时才能从“我知道原理”走到“我知道这段实现维护什么条件”。

本讲义没有替你完成某一固定仓库版本的源码审计，因此不会编造文件行号。实验执行时再补齐这部分证据。

### 从观察定位责任边界

如果 GPU 时间线出现空洞，先判断是否没有可执行请求、CPU batch 构造慢、KV 分配受阻、编译/捕获发生，或 GPU 在等待通信。只有明确空洞的上游原因，才能选对 scheduler、cache manager 或 runner 作为调查入口。

**自测：scheduler 决定 batch，为什么还需要 runner？** 前者决定语义上的工作集合，后者把它映射为设备可执行的输入、地址、kernel 和 graph。合适的调度策略并不自动生成高效执行。

**实验：**为一条 10-token prompt、最多生成 3 token 的教学请求画完整轨迹，记录每一步已计算长度、待计算 token、KV 引用和停止条件；再添加一个共享前缀请求，标出省略的步骤。

## 分布式推理与系统取舍

### Tensor Parallel 从线性层切分理解

设 \(Y=XW\)，X 为 \(T\times D_{in}\)，W 为 \(D_{in}\times D_{out}\)。若沿 W 的输出维切成 \(W_0,W_1\)，各 rank 计算 \(Y_r=XW_r\)，得到不同输出列。这是输出维切分；若下游能直接消费列分片，就不必立即收集完整 Y。

若沿 W 的输入维切分，同时把 X 的对应列分成 \(X_0,X_1\)，各 rank 计算 \(Z_r=X_rW_r\)，此时每个 \(Z_r\) shape 都是 \(T\times D_{out}\)，但它们是局部贡献：

$$
Y=\sum_rZ_r.
$$

于是需要归约得到完整 Y，或按下游布局进行 reduce-scatter。前一种输出是 shard，后一种输出是 partial，这与 DTensor 语义完全对应。

对于 \(Y=\phi(XW_1)W_2\)，可先按 \(W_1\) 输出维分片，本地应用逐元素 \(\phi\)，再按 \(W_2\) 输入维分片，最后归约。这样能跨两个线性层保留中间分片，减少不必要的中间收集。[Megatron-LM](https://arxiv.org/abs/1909.08053)

> **配图建议 L1｜TP 的 shard 与 partial。** 左图画 W 按列切、Y 各自不同列；右图画 W 按行切、X 配套切，两个同形 Z 用加号合成 Y。再用细箭头把两图连接成两层 MLP，标明非线性只允许在已正确形成的局部输出上应用。

TP 增大后，每 rank 的矩阵更小，计算可能减少，但通信启动次数不一定减少，小 GEMM 效率还可能下降。prefill token 多时更容易摊薄通信，低 batch decode 对延迟更敏感。Attention head、KV head 数和并行度之间还可能存在整除、复制或特殊切分关系，不能默认 KV 总能均分到任意 TP 数。[vLLM parallelism](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/)

### Pipeline Parallel 把层划给不同设备

PP 让不同 stage 执行不同层，stage 间传递激活。单条数据要顺序经过各 stage；若只有一个小请求，上游完成后等待、下游尚未开始，就容易出现气泡。

将工作拆成多个 microbatch 或调度多个请求，可以让各 stage 同时处理不同工作。一个理想化的纯前向流水模型中，p 个等时长 stage 处理 m 个 microbatch，需要约 \(m+p-1\) 个时间单位，而每个 stage 有 m 个单位的有效工作，平均利用率约为 \(m/(m+p-1)\)。真实推理还受不等 stage、通信和自回归依赖影响，不能直接照搬训练流水公式。

PP 的收益来自模型容量和多工作并行；代价是 stage 通信、气泡和调度复杂度。请求数量少时，更多 stage 未必降低单请求 token 延迟。

### Expert Parallel 把 token 路由到专家

MoE 的路由器为每个 token 选择一个或少数专家。若专家分布在不同设备，输入 token 需要派发到相应专家，得到输出后再返回并按门控权重合并：

$$
y_i=\sum_{e\in\mathcal{E}(i)}g_{i,e}f_e(x_i).
$$

其中 \(\mathcal{E}(i)\) 是 token i 选择的专家集合。EP 因此常包含 dispatch 和 combine 两段通信。负载由 token 路由决定，按专家数平均放置不保证运行时均衡。

这与 NS owner 的联系在于“把计算分配到拥有完整任务的设备，再送回结果”；区别是专家任务由路由动态决定，单个 token 可能去多个专家，还有门控合并和专家容量等语义。不能直接把两个协议视为同一实现。

### Context Parallel 切分上下文与 KV 工作

长上下文使 Attention 计算和 KV 存储增长。CP 可把序列或 KV 相关工作分布到多个 rank，再通过通信形成正确结果。它并不只是把普通矩阵任意切开后各算各的 softmax。

一个教学方法是把 K/V 按历史位置分片，让各 rank 对同一个 query 计算局部统计 \(m_r,\ell_r,z_r\)。令 \(m=\max_rm_r\)，可以合并：

$$
\ell=\sum_re^{m_r-m}\ell_r,\qquad
z=\sum_re^{m_r-m}z_r,\qquad O=z/\ell.
$$

这把 H 章的在线合并推广到多个设备。实际实现还可能选择移动 K/V 块、不同 ring 或其他切分，以权衡 query 复制、通信和内存；上述公式不代表所有 CP 实现的固定协议。

DCP、PCP 常用于区分 decode/prefill 的上下文并行策略，但具体切分和约束以框架版本为准。DP attention 在某些系统中指 Attention 子计算的分布方式，可能与 MoE 的其他并行组合；它不应被直接等同于若干完整模型副本各接一批请求。

### PD 分离把阶段资源拆开

prefill 与 decode 的计算粒度、内存占用和延迟目标不同。PD 分离让两类 worker 分别服务两个阶段，便于分别配置资源和扩展规模，但必须把 prefill 产生的 KV 交给 decode worker。

一次交接至少涉及请求状态、KV 位置或内容、模型与位置编码兼容性、传输完成通知、目标地址映射以及原副本的回收。若两侧 TP/CP 或 KV 布局不同，还可能需要重新分片和转换。[vLLM PD 文档](https://docs.vllm.ai/en/latest/features/disagg_prefill/)

传输的简单下界为 \(V_{\mathrm{transfer}}/B_{\mathrm{effective}}\)。用前面 512 MiB 的 KV 教学例子，假设有效带宽为十进制 100 GB/s，纯传输约需 5.37 ms；这不包含路由、启动、转换、同步和排队。网络缓存命中或只传缺失块会改变 V。

PD 是否有收益，要比较减少的阶段干扰与新增传输、协调和资源空闲。平均吞吐上升也可能伴随首 token 或尾延迟变差，因此应以目标服务指标评估。

> **配图建议 L2｜PD 交接与资源生命周期。** 画 router、prefill worker、KV 传输层、decode worker 四个对象。数据粗箭头传 KV，细箭头传请求和就绪通知；用锁形标记表示 KV 在目标确认使用前不能回收。下方列“减少干扰”和“新增传输/排队”两项待测成本。

### Speculative decoding 用便宜草稿换取批量验证

普通自回归一次推进一个 token，target 模型需要反复执行小步计算。speculative decoding 让较便宜的 draft 先提出多个 token，target 在一个可并行的验证计算中判断这串候选能接受多少，从而提高每次 target 调用推进的 token 数。

收益取决于 draft 成本、验证成本和接受长度。设一次过程耗时为 \(T_d+T_v+T_o\)，平均提交 k 个新 token，普通逐 token target 耗时为 \(T_t\)，简化加速条件是 \((T_d+T_v+T_o)/k<T_t\)。这里 k 必须统计实际提交 token，而非仅用提议长度。

随机采样下，验证不能简单等同于“两个模型 argmax 一样”。设给定相同已接受上下文后，target 分布为 p，draft 分布为 q，draft 提议 x，以：

$$
a(x)=\min\left(1,\frac{p(x)}{q(x)}\right)
$$

接受。实际从 q 采出的 x 满足正概率条件；若拒绝，从残差分布：

$$
r(x)=\frac{\max(p(x)-q(x),0)}{\sum_y\max(p(y)-q(y),0)}
$$

采样。接受分支贡献 \(\min(p(x),q(x))\)，拒绝分支补上 \((p(x)-q(x))_+\)，两者相加为 p(x)，这说明为什么修正可以保留 target 分布。p、q 都必须包含实际采样策略后的有效概率约定。[Speculative Decoding](https://arxiv.org/abs/2211.17192)

用两 token 例子：p=(0.6,0.4)，q=(0.2,0.8)。第一个 token 总被接受，第二个以 0.5 接受；直接接受贡献为 (0.2,0.4)，剩余 0.4 的拒绝概率全部补到第一个 token，最终恢复 (0.6,0.4)。如果拒绝后直接从 p 重采样，一般不能得到这个正确合成结果。

多 token 提议需要按已接受前缀依次判定，首次拒绝后的草稿不能直接继续提交。全部接受时，某些标准算法会利用 target 额外分布再生成一个 token。KV 管理也要区分暂存候选与正式提交位置，在拒绝时撤销无效后缀。greedy decoding 的匹配规则是另一种设置，应分开讨论。

> **配图建议 L3｜草稿验证与 KV 提交。** 画 draft 提出 a、b、c、d，target 接受 a、b，在 c 拒绝并修正为 x。将 a/b 的 KV 标为提交，将 c/d 标为丢弃或回退，x 标为新状态。旁边用两 token 概率条展示接受质量与残差质量相加恢复 p。

### KV 生态按职责理解

推理规模扩大后，KV 可能位于本 GPU、其他 GPU、CPU 内存或远端存储。系统需要知道数据在哪里、如何取得、是否值得取得，以及何时可以淘汰。

Mooncake 的相关组件涉及 KV 中心的服务、传输与存储；学习时沿“某块 KV 在哪产生、如何定位、怎样到达消费者”追踪。[Mooncake](https://github.com/kvcache-ai/Mooncake)

LMCache 关注与推理引擎结合的 KV 缓存、复用和分层存储；学习时比较远端/CPU 取回成本与重新计算成本，并检查缓存格式和引擎布局如何衔接。[LMCache](https://docs.lmcache.ai/)

Dynamo 涉及分布式推理 worker、路由和服务协作；学习时考察请求送到哪里、KV 局部性如何影响选择、资源怎样随负载扩展。[Dynamo](https://docs.nvidia.com/dynamo/)

这些是阅读入口，不是互斥分类；实际项目的职责会重叠。假设读取一块 KV 花 20 ms、重新计算花 8 ms，命中不一定值得使用；若重新计算会挤占关键 GPU 工作，单看这两个数又不够，需要纳入资源和排队成本。

### symmetric memory 与 NVSHMEM

传统 collective 要求参与者按协议共同执行操作。one-sided 远端访问允许发起方通过远端地址相关的接口读写目标数据，不要求目标在同一时刻发起一条对应 receive；但目标何时可消费、何时可复用存储仍需同步协议。

NVSHMEM 以 processing element 和对称内存组织分布式地址空间。各 PE 以约定方式分配对应区域，通过本地对称地址及目标 PE 指定远端对象；这不等于所有进程拿到同一个可任意互换的裸指针，也不等于 unified memory 自动迁移机制。[NVSHMEM programming model](https://docs.nvidia.com/nvshmem/api/latest/using.html)

其价值之一是把某些通信发起与同步更接近 GPU 执行路径。但更直接的访问能力不会取消一致性、完成语义、顺序和生命周期问题。学这一层时，应先画出生产、远端写、完成通知、消费和回收，再读具体 API。

### TensorRT 与 TensorRT LLM

TensorRT 面向推理执行优化，涉及模型表示、优化、算子实现选择、精度和运行时。可把它理解为将模型变成适合目标环境执行的推理方案，具体构建与运行方式随版本变化。[TensorRT](https://docs.nvidia.com/deeplearning/tensorrt/latest/)

TensorRT-LLM 则围绕 LLM 的执行、优化 kernel、并行与服务功能提供专门能力。它与调度引擎、CUDA Graph、编译工具链处于相关但不同的层次，不能只当作 `torch.compile` 的另一个名字。[TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/)

进入专项时，选一个固定模型和 shape 范围，对比模型转换/编译成本、精度、稳态吞吐、时延和动态请求支持。不要以一个大 batch 离线吞吐结果替代在线服务结论。

### 实验与自测

实验：用小矩阵验证 TP 两种切分；用三个 rank 的局部 Attention 统计验证 CP 合并；为一个长 prompt 计算 KV 传输量；用两 token 概率表验证 speculative sampling。

**问：TP、EP、CP 和 PD 分别切什么？** TP 切层内张量计算，EP 分布专家并路由 token，CP 切上下文相关工作，PD 拆分推理阶段。它们可以组合，但必须重新核对数据布局和通信。

**问：增加 GPU 后为什么单请求反而变慢？** 更小的局部计算可能降低硬件效率，通信与同步增加，流水气泡变多；新增设备也可能主要提高容量或总吞吐，而非该工作负载的单请求延迟。

## 综合练习与证据整理

### 用一张表贯穿整条路线

| 观察到的现象 | 首先检查 | 可区分原因的实验 |
|---|---|---|
| optimizer 区间很长 | 计时边界与前序等待 | 对齐 CPU、GPU、各 rank 时间线 |
| 通信次数减少但没有加速 | 新增打包、消息大小、关键路径 | 分开通信准备、通信与消费者等待 |
| 显存读数没有下降 | 活跃占用、缓存保留、峰值时点 | 同配置记录生命周期与峰值 |
| kernel occupancy 高但慢 | 实际流量、依赖、指令与 spill | 只改变 block/tile，比较相关指标 |
| decode 越来越慢 | 历史 KV、batch、通信和排队 | 固定其他条件扫描历史长度 |
| 前缀命中却 TTFT 变差 | 缓存获取和路由成本 | 对比本地命中、远端命中与重算 |
| owner 最慢 rank 拖累步骤 | 任务成本、数据量、内存与拓扑 | 按阶段比较 rank 负载与等待 |

### 四次阶段验收

完成 E 后，脱稿画你的优化器一次更新，标每步 shape、dtype、group 和 buffer 生命周期；为一个快路径给出成立条件和反例。

完成 H 后，用一个具体 shape 推导 FLOPs 与字节量，解释一个 naive 到优化版本的变化；手算 online softmax，并说明 mask 与数值边界。

完成 K 后，追踪一条请求从进入到回收的状态，指出 scheduler、KV manager 与 runner 的责任；提交三张具有固定 commit 和源码位置的特性卡。

完成 L 后，给定模型、请求分布、GPU 与网络条件，提出一个系统方案，说明数据如何分布、主要成本、预期收益以及哪组实验能证伪判断。

### 实验报告模板

每份报告写清问题和假设、输入 shape/dtype/stride、版本与设备、参考结果、优化变化、计时边界、误差指标、原始报告和结论范围。先验证正确性，再比较性能；性能差异若与假设不符，保留结果并修正解释。

数值对照可同时报告最大绝对误差与相对误差，对接近零的参考值明确处理方式。训练优化器还需比较状态、多步累积和最终训练行为；单步误差小不能独立证明长期收敛一致。

对现有项目，最后补齐四类材料：真实更新公式与状态顺序；实际 mesh 和参数布局；owner 输入输出协议；基线与优化后同配置计时。本文已经给出分析方法，这些项目事实必须来自代码和实验。

## 配图制作与后续 HTML 转换说明

正文共设置 25 个配图位置，编号按模块字母分组。每个位置已给出绘制对象、连线意义和应避免的误读。配图应紧跟相关推导，图中的变量、颜色和形状与正文保持一致。

| 配图 | 主题 | 最适合的呈现方式 |
|---|---|---|
| A1、A2 | 地址视图、生命周期 | 静态矩阵图与时间条，可增加悬停联动 |
| B1、B2 | 执行层级、stream 依赖 | 层级图与双时间线 |
| C1 | roofline 与规模 | 可调整规模的图，区分模型与测量 |
| D1、D2 | collective、拓扑 | 数据块流动与路径图 |
| E1–E5 | placement、FSDP、HSDP、owner、回缩 | 共享同一 rank 配色的组图 |
| F1、F2 | 转置与归约 | 线程地址连线与分层合并动画 |
| G1 | GEMM tile | 可逐步推进 K tile 的矩阵图 |
| H1、H2 | Attention shape、在线统计 | 形状图与手算步骤对照 |
| I1 | eager、融合、graph | 三条对照时间线 |
| J1–J3 | P/D、分页、调度 | 形状图、block table 和请求时间线 |
| K1 | 请求生命周期 | 跨组件时序图 |
| L1–L3 | TP、PD、speculation | 数据切分、交接时序和候选提交图 |

HTML 以本文章节顺序为主导航，每个知识点保留原理、例子、配图、实验、自测与答案。答案可以折叠，但正文推导不应被省略为摘要。进度分别记录“理解、实现、测量、复述”，避免一个完成状态掩盖未验证部分。

所有示例图注明“教学示例”；未执行的实验不绘制成真实 benchmark。项目实测图等源码与日志核验后再补。公式保留 LaTeX，代码字段使用等宽字体；版本敏感的 API 与框架特性保留来源链接。
