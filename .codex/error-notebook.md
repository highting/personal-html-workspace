# Project Error Notebook

记录已确认并验证修复的项目问题；后续操作前先检查相关 Prevention check。

## ERR-20261002-013 — 汇报缩页后残留旧导出图片

- Fingerprint: `content-export:stale-pages-after-rerender`
- Status: active
- First seen: 2026-10-02
- Last seen: 2026-10-02
- Occurrences: 1
- Scope: `scripts/render_content.py`、`scripts/publish_content.py` 的重复检查与成品汇总
- Symptom: 同一成品目录从两页改成一页重新导出后，`qa.images` 只列一页，但旧 `page-02.png` 仍存在，会被整体复制到短路径交付。
- Root cause: 检查器只覆盖当前页图，未清理自身上一轮生成的文件；发布函数核对当前清单后整体复制目录。
- Wrong assumption/action: 认为新 QA 清单能保证成品目录内没有多余旧图。
- Correct approach: 每轮检查前，仅清理约定名称的自有页图及明暗检查截图，保留独立配图和其他文件，再生成本轮结果。
- Prevention check: 导出和交付改动必须覆盖同一目录“多页→少页”的重跑，核对根级页图和两种主题检查截图均无旧页，同时验证独立配图保留。
- Verification: `test_rerender_with_fewer_pages_removes_previous_exports` 修复前失败、修复后通过；两页改一页后旧页图消失，`diagram.png` 保留。
- Evidence: `scripts/render_content.py` 的生成文件清理；`tests/test_content.py`。

## ERR-20261002-012 — 滚动位置检查混入自动化工具的滚动

- Fingerprint: `qa:automation-scroll-contaminates-theme-position-test`
- Status: active
- First seen: 2026-10-02
- Last seen: 2026-10-02
- Occurrences: 1
- Scope: 新长文模板的主题切换与 `tests/test_content.py`
- Symptom: 主题切换测试将 `scrollY` 从450变化到0或89误归为主题行为；改为视口点击后，未结束的锚点平滑滚动仍使位置变化。
- Root cause: 定位器点击会主动将控件滚入视口，且先前导航的平滑滚动尚未稳定；测试没有隔离这些位置变化。
- Wrong assumption/action: 把定位器点击和正在执行的平滑滚动等同于用户在稳定视口中的点击。
- Correct approach: 阅读工具栏固定在视口顶部；位置断言前先稳定滚动，在控件的真实视口坐标点击主题按钮。
- Prevention check: 验证阅读位置不变时，导航前关闭测试中的平滑滚动或等待其完成；避免定位器额外滚动，以真实视口点击复核，并确认主题确实改变。
- Verification: 单独视口点击从450切到深色后位置仍为450；`test_offline_learning_themes_math_navigation_and_position` 通过并核对主题记忆和离线公式。
- Evidence: `assets/content/content.css` 的固定工具栏；`tests/test_content.py`。

## ERR-20260914-011 — 封面未直接表达核心论点

- Fingerprint: `cover:explanatory-viewpoint-replaces-central-claim`
- Status: active
- First seen: 2026-09-14
- Last seen: 2026-09-14
- Occurrences: 1
- Scope: Hyperball 独立封面的主标题
- Symptom: 标题突出“用转角理解学习率”，用户指出应直接表达模型权重模长影响实际有效学习率。
- Root cause: 把用于讲解的几何视角当成了文章主张，核心变量关系没有进入主标题。
- Wrong assumption/action: 先围绕转角组织标题，再把有效学习率放到辅助解释中。
- Correct approach: 主标题直接表达模长对实际有效学习率的影响，转角用于图解这一关系。
- Prevention check: 制作封面前提炼文章的核心变量及关系，核对主标题是否直接表达该主张，不以读后感或辅助概念代替核心论点。
- Verification: 新封面主标题与图中有效学习率大小对应；手机尺寸检查通过，12 页主体图片保持不变。
- Evidence: `output/Hyperball/cover.png`；本次 `work/cover-check.json`；`SKILL.md` 的检查与交付规则。

## ERR-20260914-010 — DevTools 读取源文件被误算为离线资源失败

- Fingerprint: `qa:devtools-source-request-mixed-with-page-resources`
- Status: active
- First seen: 2026-09-14
- Last seen: 2026-09-14
- Occurrences: 1
- Scope: Playwright 离线 HTML 验收与 CDP 实际字体核验
- Symptom: 全部页面及公式已通过检查，启用 CDP 检查字体后，最后一页出现 `requestfailed`，类型为 `other`，原因为 `origin`，导致资源验收误失败。
- Root cause: 同一事件列表混入了页面资源加载与 DevTools 后续读取本地源文件的请求。
- Wrong assumption/action: 在 CDP 检查结束后，用整个会话的请求失败列表判断页面是否缺少资源。
- Correct approach: 所有页面完成离线加载、字体就绪及页面检查后先保存并断言资源结果，再进行 CDP 核验；其后检查工具发起的请求单独记录。
- Prevention check: 离线资源验收与 CDP 检查分阶段记录；先确认导航成功、公式和图片已加载、资源失败列表为空，再启用检查工具。不能将后续的 DevTools 源文件请求直接归为页面加载失败，也不能忽略验收阶段的真实失败。
- Verification: 同一组 12 页离线 HTML 的页面资源失败为零；实际字体为 Microsoft YaHei 与 KaTeX_Math；后续 CDP 的 `other/origin` 请求单独记录，交付验收通过。
- Evidence: `output/blogs/论文阅读/Hyperball博客-图文版/20260914-224417-977640-html/work/finalize.py`；同版本 `work/qa.json`。

## ERR-20260914-009 — 生图构造数值上图且等长约束失真

- Fingerprint: `imagegen:construction-instructions-rendered-as-content`
- Status: active
- First seen: 2026-09-14
- Last seen: 2026-09-14
- Occurrences: 1
- Scope: Hyperball 生图提示词与固定半径辅助解释图
- Symptom: 像素构造数值被绘成 250 px、600 等标签；固定半径图出现不等长半径和额外反向箭头。
- Root cause: 生图模型不能可靠区分数值构造说明与上图文案，也不能仅凭文字要求保证像素几何；对错误图局部编辑仍可能保留错误构图。
- Wrong assumption/action: 仅提供数值坐标和等长描述，没有从首轮提供已核对的几何参考。
- Correct approach: 删除构造数值标注；固定半径图改以已通过检查的 HTML 渲染图为几何参考，由 ImageGen 重新生成宋体版本，并查看实际输出。
- Prevention check: 提示词分离上图文案与构造说明，明确禁止绘制坐标和像素数值；等长、垂直、包含或投影关系是核心时优先提供已核对的参考图，逐张检查箭头方向与实际几何，不能以 prompt 中写了约束代替验收。
- Verification: 最终生图第 1 页无像素标注；第 4 页目视核对为近似等长半径、圆弧、单向更新及同一直线上的径向归一化，1086×1448，3:4。
- Evidence: `output/blogs/论文阅读/Hyperball博客-图文版/20260914-212946-714835-images/work/corrections.md`；同版本 `images/card_4.png`；HTML 对照版本 `20260914-212946-642098-html/work/compare-4.png`。

## ERR-20260914-008 — 相对脚本路径不能直接转换为资源 URI

- Fingerprint: `resources:relative-script-path-as-uri`
- Status: active
- First seen: 2026-09-14
- Last seen: 2026-09-14
- Occurrences: 1
- Scope: `scripts/rednote_render.py` 的 `SCRIPT_DIR` 与 KaTeX 资源路径
- Symptom: 使用相对路径经 `runpy.run_path` 启动渲染器时，报告 `relative path can't be expressed as a file URI`。
- Root cause: `Path(__file__).parent.parent` 在此启动方式下仍为相对路径，后续 KaTeX 资源调用 `as_uri()` 失败。
- Wrong assumption/action: 假设所有启动方式都会给出绝对 `__file__`。
- Correct approach: 先用 `Path(__file__).resolve()` 定位脚本，再构造资源路径。
- Prevention check: 需要生成 `file:` URI 的资源必须先解析成绝对路径；封装启动器验证时包含相对路径 `runpy` 调用。
- Verification: 相同相对路径启动方式成功导出 `output/html-mode-preview/index.html`；22 项测试通过。
- Evidence: `scripts/rednote_render.py` 的 `SCRIPT_DIR`；HTML CLI 验证。

## ERR-20260906-007 — 文档参数与当前脚本不一致

- Fingerprint: cli:documented-layout-flag-unsupported
- Status: active
- First seen: 2026-09-06
- Last seen: 2026-09-06
- Occurrences: 1
- Scope: scripts/rednote_render.py CLI
- Symptom: 按技能文档传入 --layout card 时，当前脚本报告 unrecognized arguments。
- Root cause: 当前 checkout 的 CLI 只暴露卡片渲染参数，文档仍包含另一版本的 layout 参数说明。
- Wrong assumption/action: 直接照文档命令执行，没有先核对当前脚本的 --help。
- Correct approach: 运行前先检查当前脚本的 CLI；本次卡片渲染省略 --layout，使用实际支持的参数完成验证。
- Prevention check: 脚本或文档发生版本变化后，以当前 checkout 的 --help 和实际渲染结果为准。
- Verification: 省略 --layout 后，重写稿成功生成 1 张封面和 8 张卡片。
- Evidence: scripts/rednote_render.py:955-984；SKILL.md 小红书卡片流程。

## ERR-20260906-006 — 主题与制作工具不应改变图文交付目标

- Fingerprint: `renderer:theme-output-contract`
- Status: active
- First seen: 2026-09-06
- Last seen: 2026-09-14
- Occurrences: 3
- Scope: 主题、HTML／生图模式路由、正文与辅助图组织、博客交付
- Symptom: 曾将 academic 改成横向单图，或只交 HTML；后又将整篇压成五张概念／辅助图，把缺失正文补成发布长配文。用户明确要求正文也在图片中，并固定由 HTML 生成。
- Root cause: 从主题风格、工具名称或“简洁”推断交付结构，没有先区分正文图片、非正文视觉和发布摘要。
- Wrong assumption/action: 将整篇文章等同于少量图解，或把生图模式扩大到正文页；看到宋体参考图又准备自动换字体。
- Correct approach: 正文用连续段落及必要公式构成完整图片文章，统一 HTML 渲染；非正文视觉才按模式使用 HTML＋SVG 或 ImageGen。两套比较复用相同正文页，配文只作摘要。参考图默认只借鉴字号和间距，字体沿用设置。
- Prevention check: 制作前分别列出正文页、辅助图及各自工具；不读发布摘要也应能沿图片理解主线。不要把“精简”变成提纲化，或用长配文补正文；正文容量不足就按完整语义增页，保持 3:4 和可读字号。
- Verification: 既有渲染验证输出 2160×2880 PNG、离线 HTML 并拒绝超高块；本轮根技能与插件入口通过 quick_validate，工作区文档和 CLI 帮助已统一新分工。当前 Hyperball 正文重制仍在 generating，未计作完成。
- Evidence: `SKILL.md`；`skills/rednote-render-skill/SKILL.md`；`references/content-plan.md`；`references/html-mode.md`；`references/image-mode.md`；`references/workspace.md`；`AGENTS.md`。

## ERR-20260906-005 — 浅色主题页码沿用白色

- Fingerprint: `theme:light-page-number-contrast`
- Status: active
- First seen: 2026-09-06
- Last seen: 2026-09-06
- Occurrences: 1
- Scope: `professional` 等浅色卡片主题
- Symptom: 卡片正文清晰，但页码使用白色，在浅色背景上几乎不可见。
- Root cause: 渲染器基础样式将 `.page-number` 固定为半透明白色，浅色主题未覆盖该规则。
- Wrong assumption/action: 只依据渲染命令成功判断卡片视觉可读性。
- Correct approach: 浅色主题显式覆盖 `.page-number` 为正文次要文字色，并在实际 PNG 中检查对比度。
- Prevention check: 每次切换浅色主题后目视检查页码、标签和正文的对比度；不要把命令成功当作视觉验收。
- Verification: `professional.css` 已覆盖 `.page-number`；最终卡片页码为深色且可读。
- Evidence: `assets/themes/professional.css`；`output/hyperball-xhs/images/card_1.png`。

## ERR-20260906-004 — 字体栈不等于实际字体

- Fingerprint: `fonts:css-family-without-installed-font`
- Status: active
- First seen: 2026-09-05
- Last seen: 2026-09-06
- Occurrences: 1
- Scope: 普通主题正文、Windows 字体环境
- Symptom: CSS 首选 MiSans，但浏览器实际使用 Microsoft YaHei。
- Root cause: 系统缺少可按 MiSans 家族名匹配的字体；含 misans 的文件名不能证明字体内部家族名称。
- Wrong assumption/action: 仅检索 CSS 或字体文件名就判断字体已生效。
- Correct approach: 从小米官方包安装原始字体到当前用户环境，重启渲染进程并核验平台字体。
- Prevention check: 字体变更后使用 Chromium CSS.getPlatformFontsForNode 检查中文、英文和代码实际字体，不能仅查看 computed font-family。
- Verification: 安装后 CDP 报告普通正文为 MiSans、terminal 代码为 Consolas。
- Evidence: `assets/themes/terminal.css`；`references/environment.md`。

## ERR-20260906-003 — 分页拆句丢失文本分隔

- Fingerprint: `pagination:lossy-sentence-separators`
- Status: active
- First seen: 2026-09-05
- Last seen: 2026-09-06
- Occurrences: 1
- Scope: `_split_body_to_sentences`、`_join_sentences`
- Symptom: 新英文切句规则不能拆分相邻中文句子，英文拆分重组时空格丢失。
- Root cause: 正则要求中文标点后有空白，随后 strip/split/join 消耗了原始分隔符。
- Wrong assumption/action: 只检查是否产生多个片段，没有检查片段能否无损拼回。
- Correct approach: 在零宽边界切句，保留空白；长句仅在原有词边界拆分。
- Prevention check: 切句或分页改动后断言 split 后 join 等于原文，覆盖中文相邻句子、英文空格和换行；代码、公式和 SVG 应保持完整。
- Verification: `test_sentence_split_rejoins_chinese_and_english_without_loss`、`test_tilde_fences_and_display_formulas_keep_blank_lines` 通过。
- Evidence: `scripts/rednote_render.py`；`tests/test_renderer.py`。

## ERR-20260906-002 — Markdown 与通用 SVG 样式破坏数学公式

- Fingerprint: `math:markdown-and-svg-interference`
- Status: active
- First seen: 2026-09-05
- Last seen: 2026-09-14
- Occurrences: 2
- Scope: `_stash_math`、KaTeX 资源、figure 越界检查
- Symptom: 公式显示为源码；根号 DOM 存在但截图缺失；合法根号被误报为画布越界。
- Root cause: Markdown 消耗公式分隔符；通用 SVG 选择器覆盖 KaTeX 内部图形；越界检查把用于裁剪的超宽 SVG 当作实际可见内容。运行时 CDN 还使卡片间的排版结果不一致。
- Wrong assumption/action: 只验证 HTML 包含 KaTeX 脚本，没有检验离线浏览器中的公式、根号和截图边界。
- Correct approach: 暂存公式而跳过代码示例，使用本地 KaTeX；图形样式限定到自有 SVG，数学越界检查使用公式外框而非内部图元。
- Prevention check: 公式链路或 SVG 样式改动后，在 offline context 中检查行内/独立公式数量、根号可见性及有效公式不会触发越界。KaTeX 内部排版及公式容器的少量纵向 scrollHeight 差异不等于画幅溢出；用页面边界和公式横向宽度判断，避免再次误拒合法根号；同时保留非法公式拒绝测试。
- Verification: `test_math_renders_offline_with_visible_radical_and_no_false_overflow`、`test_html_method_outputs_fixed_png_and_portable_sources` 通过；HTML 源文件移动目录后断网打开，公式保留 DOM。合法根号曾出现容器 scrollHeight 94、clientHeight 91，排除该内部纵向差异后仍能拒绝 2000px 超高内容块。
- Evidence: `scripts/rednote_render.py` 的 `export_html_document` 与 `HTML_DOCUMENT_CSS`；`assets/vendor/katex`；`tests/test_renderer.py`。

## ERR-20260906-001 — 中断安装遗留 Playwright 子进程和锁

- Fingerprint: `environment:orphan-playwright-installer-lock`
- Status: active
- First seen: 2026-09-05
- Last seen: 2026-09-06
- Occurrences: 1
- Scope: Windows Playwright 浏览器安装
- Symptom: 重装报告共享浏览器目录存在活动 `__dirlock`。
- Root cause: 终端任务中断后，Node 安装器与下载子进程仍存活并维护目录锁。
- Wrong assumption/action: 认为终端会话结束就代表整个安装进程树已退出，立即重装。
- Correct approach: 按命令行和父子关系识别本次任务的残留安装进程；结束后再清除确切锁目录，并只启动一个安装器。
- Prevention check: 安装被中断后，先确认没有本次安装的子进程存活；不得在另一个安装器仍运行时清锁或并发重装。
- Verification: 清理本次残留进程与锁后，Headless Shell、FFmpeg、Winldd 完成安装，Chromium 启动测试通过。
- Evidence: `references/environment.md`；共享缓存 `%LOCALAPPDATA%/ms-playwright`。
