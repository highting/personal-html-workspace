# Personal HTML Workspace

个人学习、博客、技术汇报和小红书卡片的内容制作工作区。日常制作复用当前模板与约束；公共模板修改单独提出。材料入口、分类、命名和版本以[工作区约定](references/workspace.md)为准。

本地内容入口为 `output/index.html`。正式成品留在 `output/`；历史工作版本、检查截图、示例渲染和旧文件统一存入 `archive/`。两者均不纳入 Git；新克隆的仓库不附带本机成品和归档。

## 以后怎样制作

1. 把新笔记拖进 `inputs/待分类/`。单文件直接放入，带配图和附件时拖整个文件夹；不用预先分类。
2. 在本项目会话中说：“处理新材料，做成学习长文。”也可选择博客、汇报、小红书中的一种或多种。代理负责归类到 `inputs/<内容分类>/<主题>/` 并复用当前模板。拖入不会自动唤起会话，无需使用 Web UI、填写配置或运行脚本。
3. 完成后打开 `output/Softmax-学习/index.html`；其他场景分别在 `Softmax-博客`、`Softmax-汇报`、`Softmax-小红书`。小红书打开 `预览.html`。分类总览由代理在交付时同步，发布脚本不会自动更新。
4. 以后直接说“修改 Softmax-学习 的第二节”，或“我更新了原稿，请重新生成”。新版本检查后替换相同入口，旧成品保留在 `output/_work/` 的本次记录中。

已有 `blogs/` 原稿和成品路径继续可用，无需迁移。也可以提供文件、粘贴笔记或给出本地路径，并要求代理先收进项目再制作。重名、多个版本和详细目录职责见[工作区约定](references/workspace.md)。

| 场景 | 内容组织 | 默认成品 |
|---|---|---|
| `learning` 个人学习 | 覆盖主题内相关知识，详细、直白地解释原因与过程 | 学习 HTML、章节目录、明暗切换 |
| `blog` 技术博客 | 聚焦具体知识点，用简明解释与图解讲清原理，不主动扩展 | 博客 HTML、阅读目录、明暗切换 |
| `report` 技术汇报 | 快速突出成果、依据与意义，图表或明确结论作为视觉重点 | 16:9 HTML、键盘翻页、默认收起的讲者备注、逐页 PNG |
| `rednote` 小红书 | 原 academic 连续图文流程 | 3:4 PNG、HTML 源页、标题与摘要配文 |

## 学习、博客与汇报

当前 Prompt 的读取入口见 [prompts/README.md](prompts/README.md)：共同规则保存在 `prompts/common.txt`，各场景规则保存在 `prompts/scenes/`。正常路线是“读取存储的 Prompt 与原稿 → 在 `output/_work/` 准备和制作 → 验收 → 更新 `output/<成品名>/`”；`work/任务Prompt.txt` 是本次规则与路径的快照，`archive/` 只用于历史归档，日常制作不依赖它。

材料通常先拖入 `inputs/待分类/`，代理归类后使用 `inputs/<分类>/<主题>/`，现有 `blogs/` 也可使用。直接说“把这个主题整理成学习长文”“写成技术博客”或“做成技术汇报”；场景之间分别策划，不只转换画幅。AI先阅读、策划并整理内容，脚本负责排版与检查。

```bash
python -X utf8 scripts/prepare_content.py "inputs/机器学习/Softmax" --scene learning --name Softmax-学习
# 在返回的 work/ 中制作本次正文；也可传入可信 HTML 片段
python -X utf8 scripts/build_content.py "<work_entry>" --scene learning --output "<run_dir>/work/index.html"
python -X utf8 scripts/render_content.py "<run_dir>/work/index.html" --scene learning --output-dir "<artifact_dir>"
# 实际查看两种主题、内容与交互，记录检查并标记 completed 后
python -X utf8 scripts/publish_content.py "<run_dir>"
```

用 `--scene blog` 构建博客。汇报使用 `--scene report`，在代码围栏外以独立 `---` 分页，用 `<!-- notes: 讲者备注 -->` 添加备注；导出 PNG 可选择 `--theme light` 或 `--theme dark`。完整命令与 HTML 片段协议见[四场景流程](references/content-workflow.md)，策划见[场景规则](references/content-scenes.md)。

学习与博客共用阅读模板，内容范围和解释深度分别按上述目标取舍，支持10–24px字号调节、图片/SVG点击放大、目录和阅读进度；汇报使用16:9逐页演示，支持翻页、备注和固定页导出。汇报的正文、图注、页脚、小字和备注都只保留实际要讲的内容，制作提醒与文档不足的解释留在工作记录；真实研究限制与必要条件仍保留。两类HTML面向桌面，检查缩放后的布局，不另做手机适配验收。明暗主题、SVG与配图遵循[统一视觉规则](references/visual-system.md)，普通节点使用协调的中性底色。中文字体、CSS、JavaScript、KaTeX及本地图片内嵌，可离线打开。模板源码见 `assets/content/`，示例稿见 `demos/content/`。

布局参考 [Nextra](https://github.com/shuding/nextra)（学习导航）、[AstroPaper](https://github.com/satnaing/astro-paper)（博客阅读）和 [Slidev](https://github.com/slidevjs/slidev)（技术演示）。当前查询约 13.9k、5.1k、48.9k 星；支持明暗主题的参考与设计记录见[模板设计](references/template-design.md)。本仓库模板独立实现，无需安装这些项目。

可查看[四场景示例源稿与生成方法](demos/content/README.md)。生成截图保留在本地 `archive/demo-renders/`。

## 小红书日常入口

小红书新材料也先拖入 `inputs/待分类/`，保留正文与配图的相对路径，再说“处理新材料，做成小红书图文”。已有主题可以点名：

> 把 inputs/机器学习/Hyperball 做成小红书图文，正文用 HTML 排成图片，辅助图用 HTML＋SVG，输出到 Hyperball-小红书。

或说“把 Hyperball 用图片模式生成小红书图文”。博客名唯一时可以省略分类；没有指定模式时默认 HTML。已建 `机器学习`、`论文阅读`、`工程实践`、`待分类`，可以自行新增分类。

新成品放在 `output/<主题短名>-小红书/`：最终图片、`标题.txt`、`配文.txt`、`预览.html` 都在同一层，HTML 源页在 `html/`。中间材料与版本记录放在 `output/_work/`。已有 `output/Hyperball/` 等入口改版时沿用原路径，不自动改名。

根目录 `AGENTS.md` 让后续本项目会话沿用约定。日常新建工作目录统一用 `prepare_content.py --scene rednote` 准备，兼容 `inputs/` 和已有 `blogs/` 并保存任务Prompt，通过 `publish_content.py` 汇总；`prepare_blog.py` 与 `publish_blog.py` 仅兼容历史调用和工作目录。准备时显式传 `--name`，更新时保留旧交付，详见[工作区约定](references/workspace.md)。

## 两种模式

| 模式 | 内容处理 | 交付 |
|---|---|---|
| [HTML 模式](references/html-mode.md) | 连续正文用 HTML，辅助解释图用 HTML＋SVG | 正文与辅助图 PNG、发布摘要及源文件 |
| [生图模式](references/image-mode.md) | 正文仍用 HTML，辅助解释图用 ImageGen | 正文与辅助图 PNG、发布摘要及源文件 |

两种模式共用[图文组织规则](references/content-plan.md)：先选小主题，用少量通俗文字在图片内讲清机制，辅助解释图穿插解释关系；可省难推导，保留理由与条件，不默认搬运长文全部内容。发布标题和封面标题不使用第一人称，直接表达主题或核心论点；配文采用作者第一人称，轻松自然、只作摘要。两套比较共用正文页与配文，只更换非正文视觉。字体沿用项目设置，参考图默认只用于字号和间距。仅请求辅助图时遵从该范围；原稿保留。

调用示例：“正文用 HTML 排成图片，辅助图用 HTML＋SVG，配文写摘要”；“正文页用 HTML，辅助图分别做 HTML＋SVG 和生图两套，让我比较”；“把这份精简后的文档做成小红书图文，不用 ImageGen”。

## 安装

### Claude Code Plugin

```bash
# 添加 marketplace
/plugin marketplace add highting/personal-html-workspace

# 安装插件
/plugin install personal-html-workspace@personal-html-workspace
```

安装后运行 `/reload-plugins` 加载技能。插件提供制作规则和脚本；Python 包、浏览器与字体仍需按下面的步骤准备。日常材料与成品建议在克隆的项目工作区中管理。

### 换电脑使用

准备 Git、Python 3.12 或 3.13（含 pip、venv），以及能在本项目目录中读取 `AGENTS.md` 和 `SKILL.md` 的代理工具。已在 Windows x64 的 Python 3.12.14、3.13.14 环境使用当前锁定依赖；macOS/Linux 的路径用法见下文，尚未逐平台验证。脚本本身不调用模型，内容整理与可选生图需要当前代理提供相应能力；纯 HTML 制作不要求生图工具、Node.js 或 npm。

```bash
git clone https://github.com/highting/personal-html-workspace.git
cd personal-html-workspace
python -m venv .venv
```

Windows PowerShell 下执行（无需激活虚拟环境）：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m playwright install chromium-headless-shell
.\.venv\Scripts\python.exe -X utf8 scripts/download_content_fonts.py
```

macOS/Linux 创建环境时通常使用 `python3 -m venv .venv`，后续使用 `.venv/bin/python`：

```bash
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip check
.venv/bin/python -m playwright install chromium-headless-shell
.venv/bin/python -X utf8 scripts/download_content_fonts.py
```

Linux 若提示缺少浏览器系统库，执行 `.venv/bin/python -m playwright install-deps chromium`，该步骤可能需要管理员权限。首次安装需联网下载 Python 包、Playwright 浏览器和约 17 MB 的固定版本中文字体；下载源、镜像与字体要求见[环境说明](references/environment.md)。字体下载脚本会核对 SHA-256。之后可用本地材料离线构建 HTML；来源网页访问和 AI 服务另计。

后文命令中的 `python` 均指这个虚拟环境的解释器；可替换为上述完整相对路径，或激活 `.venv` 后执行。不要复制另一台电脑的 `.venv` 或浏览器缓存。

新机器可先运行以下检查；Windows 将 `.venv/bin/python` 替换为 `.\.venv\Scripts\python.exe`：

```bash
.venv/bin/python -X utf8 scripts/build_content.py demos/content/learning.md --scene learning --output archive/demo-renders/learning/index.html
.venv/bin/python -X utf8 scripts/render_content.py archive/demo-renders/learning/index.html --scene learning --output-dir archive/demo-renders/learning
```

打开生成的 `archive/demo-renders/learning/index.html`，查看中文、公式、明暗切换和目录。机器检查通过不代替实际查看；全部回归可运行 `python -X utf8 -m unittest discover -s tests -v`。环境准备好后，在仓库根目录开始会话，按前面的材料投放与制作流程使用即可，无需把本仓库另装成个人技能。

### Git 分发范围

- 随仓库保留：制作脚本、公共模板、Prompt、流程文档、示例源稿、测试、依赖锁文件、KaTeX 资源，以及中文字体的下载清单与许可。新增的 `inputs/`、`blogs/` 原稿和附件需实际加入提交才会到远端。
- 不随 Git 分发：`.venv/`、浏览器缓存、下载的完整中文字体、`output/` 成品和 `archive/` 归档。新克隆没有本地总览与历史成品，首次交付时按工作区规则生成；需要迁移旧成品或归档时另行复制或备份。
- 新机器从原稿重新准备任务。历史 `run.json` 含原机器绝对路径，不能复制后直接继续发布；需要继承旧工作稿时，重新 prepare 并按[工作区约定](references/workspace.md)记录来源。
- 学习、博客、汇报的中文字体和本地资源内嵌在成品 HTML 中，成品可独立移动。小红书沿用系统字体；另一台电脑需准备相同字体才能尽量保持字形和分页，详见[字体要求](references/environment.md#字体与公式)。

---

## 小红书特性

- **默认技术风格**：直接使用 `academic`，不要求每次选择主题；其他主题仅显式选择，详见 [STYLES.md](STYLES.md)
- **自动分页**：根据内容渲染高度拆分为多张卡片，代码块、表格和 SVG 尽量保持完整
- **技术内容支持**：内置 KaTeX 数学公式资源，并支持表格和内嵌 SVG
- **academic 主题**：浅暖米色卡片（`#F7F4ED`），钴蓝／青蓝／琥珀橙，轻量几何和短标签；HTML 渲染中文优先微软雅黑，生图按 prompt 使用宋体／serif
- **Playwright 渲染**：高质量 HTML → PNG 输出
- **保留制作源文件**：可随 PNG 保存分页 HTML 与离线数学资源，便于后续修改和复现
- **独立生图流程**：正文仍由 HTML 排版，辅助解释图等非正文视觉使用 ImageGen

---

## 小红书渲染器接口

日常制作使用上面的[小红书日常入口](#小红书日常入口)：先用 `prepare_content.py --scene rednote` 建立工作目录，再将整理好的工作稿交给渲染器，验收后用 `publish_content.py` 汇总。以下是底层渲染命令，用于本次工作目录或独立示例检查，不替代准备、内容审核与交付流程。

```bash
python scripts/rednote_render.py <markdown_file> [options]
```

```bash
# 本次工作稿：academic 主题，导出 PNG 并保留 HTML 源页
python -X utf8 scripts/rednote_render.py "<work_entry>" --math katex --save-html -o "<artifact_dir>"

# 切换主题
python scripts/rednote_render.py content.md -t neo-brutalism

# academic 主题：技术图仍输出小红书封面和正文卡片，示例已启用 KaTeX
python scripts/rednote_render.py demos/academic.md -t academic -o archive/demo-renders/geometry

# academic 主题的对应对比图
python scripts/rednote_render.py demos/academic-comparison.md -t academic -o archive/demo-renders/comparison

# 交付 PNG，同时保留 HTML 制作源文件
python scripts/rednote_render.py demos/academic.md --save-html -o archive/demo-renders/geometry

# 显式选择其他主题时，仍使用本次成品暂存目录
python scripts/rednote_render.py "<work_entry>" -t retro -o "<artifact_dir>"
```

默认输出 `cover.png`（有封面标题时）和 `card_N.png`。所有主题共用固定画幅检查；内容过高时重排，不自动输出超长图。`--save-html` 同时在 `html/` 保存制作源文件和必要资源；仅用 `--format html` 检查中间源文件，不算完成配图。渲染脚本不调用 ImageGen。不同请求使用独立目录，不自动清理旧文件。

技术图示例：

| 示例 | 解释目标 |
|---|---|
| [向量几何](demos/academic.md) | 用直角三角形解释切向更新为何增加范数 |
| [对应对比](demos/academic-comparison.md) | 对比直接更新与归一化，区分临时端点和最终状态 |

两例依据欧氏向量加法、勾股定理与径向归一化构造，作为 `academic` 主题的卡片示例，不代表论文实验。假设非零权重、非零切向步长；向量角度、比例与投影关系保持真实。公式说明留在正文，图中只保留必要关系。

**参数说明**：

| 参数 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--output-dir` | `-o` | 输出目录 | 当前目录 |
| `--theme` | `-t` | 排版主题，其他主题显式指定 | `academic` |
| `--width` | `-w` | 图片宽度（CSS px） | `1080` |
| `--height` | | 图片高度（CSS px） | `1440` |
| `--dpr` | | 设备像素比 | `2` |
| `--math` | | 数学公式渲染：`off` 或 `katex` | 读取 `front matter.math` |
| `--save-html` | | PNG 之外保留 HTML 制作源文件 | 关闭 |

---

## 项目结构

```
personal-html-workspace/
├── AGENTS.md                   # 后续会话的四场景约定
├── inputs/                     # 新材料：分类/主题/正文与附件
├── prompts/                    # 公共规则与四场景任务规则
├── blogs/                      # 已有原稿兼容入口，新材料统一进 inputs/
├── output/
│   ├── index.html              # 本地分类总览
│   ├── <主题短名>-<场景>/       # 正式成品：学习/博客/汇报/小红书
│   └── _work/                  # 当前制作中的工作目录
├── archive/                    # 本地统一归档，整目录排除 Git
│   ├── work/                   # 已封存工作版本、来源快照与检查证据
│   ├── checks/                 # 从正式入口移出的 QA 与检查截图
│   ├── examples/               # 示例成品
│   ├── demo-renders/           # 从 demos 移出的生成图片
│   ├── legacy/                 # 早期模板与示例
│   ├── handoffs/               # 历史交接
│   ├── environments/           # 停用的本机验证环境
│   ├── history/、legacy-runs/  # 原有归档与早期制作记录
│   └── manifest.json           # 相对路径迁移清单与文件哈希
├── SKILL.md                    # 技能定义
├── README.md
├── requirements.txt            # Python 依赖
├── requirements.lock.txt       # 已验证的完整依赖版本
├── references/
│   ├── content-workflow.md     # 四场景准备、构建、检查与交付
│   ├── content-scenes.md       # 内容组织与场景验收
│   ├── visual-system.md        # 配色、字号、图解与交互规则
│   ├── template-design.md      # 高星项目参考与明暗模板设计
│   ├── rednote-scene.md        # 原 main 小红书制作规则
│   ├── workspace.md            # 统一材料入口、分类、命名与版本
│   ├── params.md               # 完整参数参考
│   ├── html-mode.md            # 分页 HTML 与 SVG 工作流
│   ├── content-plan.md         # 两种模式共用的图文组织与选点
│   ├── image-mode.md           # 正文 HTML 与非正文生图
│   ├── environment.md          # 大陆镜像安装与验证
│   └── third-party.md          # 资源来源和许可
├── assets/
│   ├── content/                # 新长文与汇报的离线明暗模板
│   ├── themes/                 # 各主题 CSS 文件
│   │   ├── default.css
│   │   ├── playful-geometric.css
│   │   ├── neo-brutalism.css
│   │   ├── botanical.css
│   │   ├── professional.css
│   │   ├── retro.css
│   │   ├── terminal.css
│   │   ├── sketch.css
│   │   ├── minimalist.css
│   │   └── academic.css
│   └── vendor/
│       └── katex/              # KaTeX 0.16.11 本地运行资源与许可
├── demos/                      # 可复用示例源稿，不放生成截图
├── tests/                      # 渲染、工作区、阅读交互、导航与配色回归
├── skills/
│   └── personal-html-workspace/
│       └── SKILL.md               # 插件入口，引用根目录规范
└── scripts/
    ├── prepare_content.py     # 四场景工作副本与任务规则
    ├── build_content.py       # 学习/博客/汇报的自包含明暗 HTML
    ├── render_content.py      # 明暗检查、离线检查与汇报逐页 PNG
    ├── publish_content.py     # 四场景短路径汇总与版本保留
    ├── download_content_fonts.py # 下载离线中文字体缓存
    ├── check_content_palettes.py # 六套配色检查
    ├── check_chrome_zoom.py   # Chrome 原生缩放检查
    ├── check_rednote.py       # 小红书源页检查与手机预览
    ├── content_markup.py     # 长文代码与图注标记
    ├── visual_qa.py           # 共享字号与制作残留检查
    ├── prepare_blog.py        # 准备小红书交付入口、原稿快照和工作副本
    ├── publish_blog.py        # 汇总图片、标题与配文并保留旧交付
    └── rednote_render.py      # 小红书卡片渲染
```

---

## 小红书注意事项

- 默认画布为 1080×1440 CSS px（本地沿用的小红书 3:4 比例）；PNG 物理像素乘以 `dpr`
- 总量过大先删重复与非必需旁支，必要解释仍放不下再重新分组增页，不缩字、截断因果或用超长图交付
- 生成后仍需查看实际图片，检查几何关系、文字重叠和遮挡；自动检查不能判断图意是否准确
- 字体使用系统已安装版本；默认 HTML＋SVG 渲染的 PNG 优先 `Microsoft YaHei`；生图指定宋体／serif 并检查实际结果
- KaTeX 资源随项目提供，公式渲染不依赖运行时网络
- SVG `<text>` 用于自然语言，LaTeX 标签放在 `.figure-label` HTML 层；具体写法见两份示例
- Windows 管道输出若遇到 `UnicodeEncodeError`，使用 `python -X utf8` 运行上述命令
- 图片可反复渲染覆盖

---

## License

新仓库保留原 `main` 的提交历史；原 `rednote-skill` 仓库继续保留。技能与插件名为 `personal-html-workspace`。小红书沿用原渲染流程，本轮按实际成品调整了academic字号与留白。

MIT License © 2026 Bakameow

Original work by ZhangJia (comeonzhj).
