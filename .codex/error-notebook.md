# Project Error Notebook

记录已确认并验证修复的项目问题；后续操作前先检查相关 Prevention check。

## ERR-20261003-027 — 原图内联尺寸阻碍弹窗适配

- Fingerprint: `image-viewer:source-inline-dimensions-override-fit`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: 克隆图像的width、height与max尺寸
- Symptom: 原SVG内联height为900px，适合窗口的图像区只有720px，图像仍保持900px而被裁切。
- Root cause: 克隆保留原图内联尺寸，优先级高于弹窗样式；仅修改image-width变量不能控制它。
- Wrong assumption/action: 认为正文里的图像尺寸约束会自动服从弹窗的适配规则。
- Correct approach: 弹窗控制克隆图像的尺寸，保留原图比例；适合窗口同时限制宽高，原图节点不变。
- Prevention check: 图像适配覆盖竖图、带固定内联尺寸的SVG/图片及缩放窗口，比较图像实际矩形与可视区域，而非只检查缩放变量。
- Verification: 对照测得修正前image=900、frame=720，修正后两者均720；明暗、720×500及CSS200%回归通过。
- Evidence: `tests/test_image_viewer.py`；本轮`fixed-image-check.json`与对照HTML。

## ERR-20261003-026 — 放大视图丢失图注中的条件

- Fingerprint: `image-viewer:image-only-clone-loses-figure-context`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: 图片/SVG弹窗与figure图注
- Symptom: Hyperball第二张图原图注含“不采用切向、小步长构图”，放大后弹窗图注数量为0。
- Root cause: 只克隆媒体节点，没有保留figure中的图注和技术条件。
- Wrong assumption/action: 认为图像本身能代表图文组合的完整解释。
- Correct approach: 在弹窗保留原图注的已渲染公式、链接及条件，正文仍保留图注；无图注图像清除上一张说明。
- Prevention check: 比较放大前后图注内容，覆盖公式与链接、引用ID去重和切换到无图注图像，并验证关闭后位置与焦点恢复。
- Verification: 真实两篇长文在Chrome原生100/150/200%明暗弹窗检查通过；4项相关测试及实际截图复核通过。
- Evidence: `tests/test_image_viewer.py`；`scripts/check_chrome_zoom.py`；本轮`viewer-captions`迭代记录。

## ERR-20261003-025 — 滚动提示伸出补充内容面板

- Fingerprint: `table-hint:absolute-note-without-owned-bottom-space`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: 宽表格方向提示与details嵌套布局
- Symptom: 24px字号时提示底边653.8125px，补充面板底边647.625px，提示伸出约6px。
- Root cause: 绝对定位提示不占布局空间；沿用普通表格留白，details末块24px外边距不足以容纳提示。
- Wrong assumption/action: 认为正文中既有留白也适用于所有嵌套面板和可调字号。
- Correct approach: 仅为实际溢出的表格保留足够下方间距，包含其提示；方向切换只改文字，不改间距。
- Prevention check: 表格提示同时检查普通正文和折叠面板，在最大字号核对提示底边与面板底边，并验证开启/关闭及窗口变化。
- Verification: 嵌套边界回归修正前失败、修正后通过；24px明暗截图已查看，表格/字号/导航/续读7项测试通过。
- Evidence: `tests/test_table_scroll.py::test_folded_table_rechecks_overflow_after_font_changes`；本轮`nested-light.png`与`nested-dark.png`。

## ERR-20261003-024 — 长代码收起预览裁切半行

- Fingerprint: `code-preview:parent-em-height-and-padding-clip-partial-line`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: `.code-block.is-collapsed`的字号、行高与裁切容器
- Symptom: 收起预览底部露出半截源行；只按行高修正pre高度后，行17仍跨过469.9375px裁切边界。
- Root cause: pre与code采用不同字号；pre的padding区域也允许溢出文字绘入，按父字号限制整体高度不能保证完整行边界。
- Wrong assumption/action: 认为父容器的整倍em高度或内容高度加上下padding就等于完整代码行预览。
- Correct approach: 代码字号放在pre，code继承；直接按code自身行高限制代码区，pre保留正常上下留白，展开时解除限制。
- Prevention check: 预览检查追踪源行的实际矩形与裁切边界，覆盖16/18/24px及100/150/200%布局缩放；同时验证展开和复制仍保留全部文本。
- Verification: 新完整行回归覆盖9组字号/缩放组合；6项代码与阅读测试通过，真实24行示例的默认明暗预览已查看。
- Evidence: `tests/test_code_wrap.py::test_collapsed_preview_does_not_show_partial_lines`；`assets/content/content.css`；本轮`collapsed-final-light.png`与`collapsed-final-dark.png`。

## ERR-20261003-023 — 原生缩放图块截图只覆盖首个实例

- Fingerprint: `qa:native-zoom-first-instance-only`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: `scripts/check_chrome_zoom.py` 的原生200%图块截图
- Symptom: 新长文有4张表和2段代码，原生截图只含第一张表和第一段代码；后续表头孤字与数组断行没有进入目视材料。
- Root cause: 每类选择器只使用first定位，宽表格还只拍摄初始横向位置。
- Wrong assumption/action: 认为同类内容的首个实例足以代表整篇长文的缩放排版。
- Correct approach: 逐块枚举图、代码、表格与补充内容；宽表格以横向分屏补拍，保留原生图面捕获和像素尺寸核对。
- Prevention check: 将正文图块数量与截图文件清单核对；混合内容长文必须查看后续实例及局部滚动区域，不能以QA通过推断全部内容已看完。
- Verification: 新Softmax长文的原生检查覆盖4张表、2段代码、长代码换行及宽表格右侧；明暗截图已查看，6组原生缩放检查通过。
- Evidence: `demos/content/softmax-longform/main.md`；本轮`Softmax-学习`的`work/before/native-zoom`与`delivery/checks/native-zoom`。

## ERR-20261003-022 — 续读未恢复代码显示状态

- Fingerprint: `reading:resume-location-without-code-view-state`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: 代码换行、长代码展开与续读位置恢复
- Symptom: 离开前开启换行并展开代码，续读后控件仍显示aria-pressed=false、aria-expanded=false。
- Root cause: 只保存章节位置和details状态，没有保存会改变内容高度的代码显示状态。
- Wrong assumption/action: 认为章节比例定位可以独立于可见内容的布局状态恢复。
- Correct approach: 先恢复显示状态再定位；按标题上下文和代码内容识别状态，避免按顺序错套到新增代码块。
- Prevention check: 续读验证必须覆盖换行、展开、代码插入与短结尾，核对实际可见源行而不只看scrollY。
- Verification: 状态回归修正前失败、修正后通过；原生200%Hyperball源行10前后位置相同，相关10项验证通过。
- Evidence: `tests/test_resume_views.py`；`assets/content/reading.js`；本轮`delivery/checks/resume-code-light.png`。

## ERR-20261003-021 — 原生缩放截图混用CSS与DIP视口

- Fingerprint: `qa:native-zoom-css-clip-applied-to-dip-surface`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: Chrome原生缩放下的自动化截图
- Symptom: 200%时CSS视口709×451，错误截图也只有该大小，出现截断或空白；布局指标却通过。
- Root cause: 默认截图裁剪按CSS视口或元素坐标给出clip，而原生zoom后的浏览器图面以DIP/设备像素表示。
- Wrong assumption/action: 认为改变Chrome原生zoom后，常规页面/元素截图可以直接用CSS坐标。
- Correct approach: 直接捕获完整浏览器表面，不传CSS clip；用视口分屏覆盖内容，并核对像素尺寸与innerWidth×DPR。
- Prevention check: 原生zoom验收必须同时核对缩放指标、PNG尺寸和实际画面；不以无溢出的机器结果代替目视检查。
- Verification: 200%下CSS视口709×451、DPR2，修正后完整图面1418×902；明暗图解、代码、表格、证明与报告截图已查看。
- Evidence: `scripts/check_chrome_zoom.py`；本轮`delivery/checks/native-zoom/`。

## ERR-20261003-020 — 字号重排导致当前阅读内容大幅位移

- Fingerprint: `reading:font-reflow-without-content-anchor`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: 长文字号控件与复杂公式/图文混排
- Symptom: Hyperball阅读版从18px调至20px后，同一字符由视口约140px移到约527px。
- Root cause: 只修改字号变量，依赖浏览器自动滚动锚定；复杂混排中该锚点不能稳定保持当前文字。
- Wrong assumption/action: 只验证字号数值和无溢出，没有追踪当前阅读内容。
- Correct approach: 修改字号前保存文字插入点；没有文字插入点时保存当前块内位置，重排后恢复其视口位置。
- Prevention check: 在真实长文中追踪可见文字，并覆盖浏览器自动锚定关闭的情况；允许自然换行，禁止大幅跳段。
- Verification: 最明显测点位移从386.7px降至约0.3px；真实原稿回归及完整46项测试通过。
- Evidence: `assets/content/content.js`；`tests/test_font_position.py`；本轮`font-positions.json`。

## ERR-20261003-019 — 短结尾无法成为当前章节

- Fingerprint: `navigation:short-last-section-never-reaches-active-threshold`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 2
- Scope: `assets/content/content.js` 与 `reading.js` 的长文目录高亮、续读标题与目录内部跟随
- Symptom: 已读到页底，目录仍选中倒数第二章；章节较多时当前项还可能位于目录可视区外。
- Root cause: 仅依据标题越过视口固定阈值选择章节，短结尾受最大滚动距离限制，永远无法到达该阈值；选中状态没有维护目录内部可见性。
- Wrong assumption/action: 认为每个章节标题最终都能滚过工具栏下方的判定线。
- Correct approach: 到达文末时选择最后一个可见标题；当前项变化时只调整目录容器scrollTop，避免scrollIntoView移动正文。
- Prevention check: 长文导航验证同时覆盖长目录、短结尾和隐藏的折叠标题；核对当前项、目录内可见性与正文位置。
- Verification: 32章短结尾测试修复前选中章节31，修复后选中结尾且在目录内可见；真实Hyperball文末选中总结，相关7项浏览器验证通过。
- Evidence: `tests/test_navigation.py::test_end_of_long_article_marks_last_section_and_keeps_it_in_toc`；`tests/test_resume_views.py::test_resume_prompt_names_a_short_final_section_at_page_end`；本轮`delivery/checks/light/navigation-end.png`。

## ERR-20261003-018 — 重命名目录后跨账户Git归属检查

- Fingerprint: `git:renamed-workspace-cross-account-ownership`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: 重命名后的本地仓库，在普通沙箱与提权命令间切换时的Git操作
- Symptom: 普通命令可读Git状态，提权提交却报告dubious ownership。
- Root cause: 仓库归属离线沙箱账户，而提权命令使用主账户；新路径没有被该账户信任。
- Wrong assumption/action: 认为只读状态成功，就能保证另一执行账户下的写入命令通过归属检查。
- Correct approach: 核对当前项目的绝对路径与归属后，仅对该次Git命令指定safe.directory，不写入全局通配信任。
- Prevention check: 重命名工作区或切换执行账户后，先核对目标仓库；已授权的本地Git操作可用 `git -c safe.directory=<已核对的项目根目录>`，失败后立即停止后续命令。
- Verification: 命令级精确路径设置后提交508ee79成功，工作区干净，全局Git安全配置未修改。
- Evidence: 本轮本地Git提交命令与提交508ee79。

## ERR-20261003-016 — 自动阅读标记与作者ID冲突

- Fingerprint: `reading:generated-id-collides-with-author-id`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: `assets/content/reading.js` 的折叠块、代码展开定位与续读
- Symptom: 正文已有同名ID时，恢复折叠状态会找到标题而非details，代码按钮也可能指向错误元素。
- Root cause: 自动标记只使用固定前缀和序号，未与文档已有ID去重。
- Wrong assumption/action: 假定模板内部前缀不会被可信HTML正文使用。
- Correct approach: 根据已有ID分配唯一标记；补充块优先按summary生成稳定名称，重复时追加后缀。
- Prevention check: 带作者自定义ID的正文必须验证全页ID唯一，且展开控件与续读指向正确元素。
- Verification: `test_generated_ids_do_not_shadow_author_ids`及44项回归通过。
- Evidence: `assets/content/reading.js`；`tests/test_reading.py`。

## ERR-20261003-017 — 章节定位重复计算顶部留白

- Fingerprint: `reading:double-anchor-scroll-offset`
- Status: active
- First seen: 2026-10-03
- Last seen: 2026-10-03
- Occurrences: 1
- Scope: 长文的章节链接、目录高亮与续读标题
- Symptom: 目录跳转后标题停在视口200px处，续读提示仍显示上一个小节。
- Root cause: 根元素100px的scroll-padding与目标标题100px的scroll-margin叠加，而当前章节判断阈值为140px。
- Wrong assumption/action: 在已有固定工具栏避让规则上又为标题添加同样的偏移。
- Correct approach: 统一由根元素scroll-padding提供避让，删除目标标题的重复设置。
- Prevention check: 核对真实文章目录跳转后的目标位置和当前章节；续读标题也应对应目标章节，不能只检查hash变化。
- Verification: Hyperball阅读版跳转“方法对照”小节后续读标题正确，恢复位置距视口顶部100px；明暗QA重跑通过。
- Evidence: `assets/content/content.css`；本次工作目录的`delivery/checks/resume.png`。

## ERR-20261002-015 — 汇报舞台缩放后偏移并被裁切

- Fingerprint: `report:intrinsic-grid-size-before-transform`
- Status: active
- First seen: 2026-10-02
- Last seen: 2026-10-02
- Occurrences: 1
- Scope: `assets/content/content.css` 的 `.presentation`、`.slide-stage`，以及 `render_content.py`
- Symptom: 720×500窗口中演示页偏向右下方并被裁切，文档整体横向溢出检查仍通过。
- Root cause: Grid根据1280×720舞台的未缩放固有尺寸计算轨道；transform缩小视觉内容，却没有让舞台相对可见容器正确居中。
- Wrong assumption/action: 认为缩放因子正确、整页没有横向滚动，就能证明演示舞台完整可见。
- Correct approach: 舞台相对演示容器绝对居中，以translate和scale组合定位；导出时恢复正常定位，保留1280×720固定页。
- Prevention check: 同时核对舞台四边在presentation容器内，覆盖1440×1000、960×667、720×500窗口；查看缩小窗口截图，不能只检查导出PNG或scrollWidth。
- Verification: 明暗720×500截图均显示完整居中舞台；汇报导航、备注、主题与PNG尺寸回归测试通过，三种窗口检查通过。
- Evidence: `tests/test_content.py::test_report_navigation_notes_theme_and_png_size`；`output/流程优化-汇报/checks/light/window-720.png`；`scripts/render_content.py`。

## ERR-20261002-014 — 管道 Python 中的 rg 默认检索 stdin

- Fingerprint: `inspection:rg-inherits-piped-stdin`
- Status: active
- First seen: 2026-10-02
- Last seen: 2026-10-02
- Occurrences: 1
- Scope: PowerShell here-string 启动Python后调用 `subprocess.run(['rg', ...])` 的跨文件改名检索
- Symptom: 外层rg已有命中，Python子进程的相同模式却返回1且没有文件清单，改名在写入前停止。
- Root cause: 子进程继承了传入Python代码的非交互stdin；没有显式搜索路径时，rg选择stdin而不是工作区。
- Wrong assumption/action: 认为当前工作目录会自动成为所有rg调用的检索范围。
- Correct approach: 在子进程命令中显式传入 `.` 或目标目录；涉及插件元数据时同时包含隐藏文件并排除 `.git/`。
- Prevention check: 从管道脚本调用rg时指定搜索路径；跨仓库配置改名核对隐藏的 `.claude-plugin/` 等目录，不能把空输出直接当成无匹配。
- Verification: 显式路径与隐藏文件范围的检索返回8个命中文件，全部完成替换，插件JSON及技能入口同步改名。
- Evidence: 本次改名脚本的rg参数；`.claude-plugin/`、`README.md`、`SKILL.md` 和 `skills/personal-html-workspace/`。

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
- Last seen: 2026-10-03
- Occurrences: 2
- Scope: 新长文模板的主题切换与 `tests/test_content.py`
- Symptom: 主题切换测试将 `scrollY` 从450变化到0或89误归为主题行为；改为视口点击后，未结束的锚点平滑滚动仍使位置变化。
- Root cause: 定位器点击会主动将控件滚入视口，且先前导航的平滑滚动尚未稳定；测试没有隔离这些位置变化。
- Wrong assumption/action: 把定位器点击和正在执行的平滑滚动等同于用户在稳定视口中的点击。
- Correct approach: 阅读工具栏固定在视口顶部；位置断言前先稳定滚动，在控件的真实视口坐标点击主题按钮。
- Prevention check: 验证阅读位置不变时，导航前关闭测试中的平滑滚动或等待其完成；避免定位器额外滚动，以真实视口点击复核，并确认主题确实改变。
- Verification: 单独视口点击从450切到深色后位置仍为450；`test_offline_learning_themes_math_navigation_and_position` 通过并核对主题记忆和离线公式。
- Evidence: `assets/content/content.css` 的固定工具栏；`tests/test_content.py`；`tests/test_navigation.py` 的文末主题切换采用实际视口坐标，复核正文位置不变。

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
