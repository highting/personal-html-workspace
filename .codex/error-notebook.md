# Project Error Notebook

经验证的根因与预防检查；上限20,000字符。历史验证未在本次压缩中重跑。

完整历史见[压缩前快照](../archive/maintenance/error-notebook-20261025-editor/source.md)。短路径及旧证据迁移规则沿用快照；原稿和source不改。

默认元数据：`Status: active`，`Occurrences: 1`，`First seen`、`Last seen`各自默认为ID日期。下表“—”沿用该字段默认值；重复ID以指纹区分。

|ID / Fingerprint|First seen|Last seen|Occurrences|
|---|---|---|---|
|ERR-20261022-088|—|2026-10-25|6|
|ERR-20261003-050|—|2026-10-25|2|
|ERR-20261004-082|—|2026-10-25|2|
|ERR-20261003-072|—|2026-10-23|2|
|ERR-20261003-064 / `animation:step-reveal-substitutes-for-algorithm-state-transitions`|—|—|2|
|ERR-20261003-048|—|2026-10-23|2|
|ERR-20261003-038|—|2026-10-23|4|
|ERR-20261003-033|—|—|2|
|ERR-20261003-020|—|—|2|
|ERR-20261003-019|—|—|2|
|ERR-20261003-018|—|—|3|
|ERR-20261002-013|—|2026-10-03|2|
|ERR-20261002-012|—|2026-10-03|6|
|ERR-20260914-010|—|2026-10-22|2|
|ERR-20260906-006|—|2026-09-14|3|
|ERR-20260906-004|2026-09-05|—|1|
|ERR-20260906-003|2026-09-05|—|1|
|ERR-20260906-002|2026-09-05|2026-09-14|2|
|ERR-20260906-001|2026-09-05|—|1|

|ID|Fingerprint|Root cause|Prevention check|Verification / Evidence|
|---|---|---|---|---|
|ERR-20261025-101|`build:yaml-date-json`|新增JSON序列化不能处理YAML日期对象。|核对既有元数据类型；日期保持原显示字符串。|日期构建/重建通过；`tests/test_content_editor.py`。|
|ERR-20261025-100|`editor:preview-palette-reset`|冷启动快照未包含当前配色，预览恢复默认。|进入编辑时传当前配色，重绘后恢复；核对iframe实际主题与截图。|明暗编辑及原生三档通过；`tests/test_content_editor.py`、`qa-editor.json`。|
|ERR-20261025-099|`editor:stale-authoring-payload`|旧正文覆盖外部修订HTML。|冷启动按文件实际正文建编辑模型；导出时同步payload，不以旧payload覆盖文件。|后处理正文与图片宽度保存通过；`test_content_editor.py::test_launcher_preserves_postbuild_edits_and_image_width`。|
|ERR-20261025-098|`qa:async-editor-readiness`|未出现遮罩被误判隐藏，取错框架。|先等编辑器可见再等就绪，按其iframe定位，不取frames[-1]。|旧稿导入、另存、重开通过；`test_content_editor.py::ready`。|
|ERR-20261025-097|`appearance:shared-reading-theme-leaks-into-presentation`|长文明暗偏好及检查循环泄漏到汇报。|仅学习/博客保留明暗；汇报默认纯白，仅white/paper且独立保存偏好，不生成深色样张；小红书固定纸白#FAF9F6，不用纯白。模板、提示词、渲染/配色/缩放检查同步分路。|52项测试通过，覆盖阅读偏好隔离与背景记忆；`content.js`、`test_reader_tools.py`及本轮`qa.json`仅含light。|
|ERR-20261025-096|`typography:cjk-math-ink-exceeds-tight-line-box`|实际中文字形/根号超紧行盒。|改字号/行高后，检查独立中文标题、空副标题封面及根号分式的scroll/client尺寸；标题留足行高，展示公式增加上下内距，不放宽越界断言。|标题1.35行高、公式0.35em内距后26项回归通过，独立标题高度/滚高均81px；`archive/checks/template-focus-20261025/preview-check.json`。|
|ERR-20261025-095|`workflow:unchecked-validation-exit-before-commit`|非零子命令未阻断后续。|提交/发布/迁移前显式检查每项exit_code；非零立即停，不能打印后继续。|许可空白清理后暂存检查为0；`assets/vendor/font-awesome/LICENSE.txt`。|
|ERR-20261025-094|`qa:three-digit-hex-in-six-digit-palette-parser`|解析器漏三位色值及根节点覆盖。|语义色用`#RRGGBB`并核对根节点实际颜色；扩展语法先补解析测试。|八页明暗、六色、原生三档通过；`scripts/visual_qa.py:45`。|
|ERR-20261023-093|`qa:native-zoom-strict-float-edge-comparison`|滚动尺寸取整与矩形亚像素不一致。|原生缩放几何用2px容差，同时核对滚动终态和截图，不放宽内容安全区。|三场景原生三档通过；`scripts/check_chrome_zoom.py`。|
|ERR-20261023-092|`qa:production-copy-scanner-misses-containers-and-notes`|扫描漏容器、备注及制作词。|收集实际文本节点并单查备注；覆盖行内拆词、列表/表格/页脚与合法代码引用，全文仍须审读。|样例准确报3项、28项检查通过；`scripts/visual_qa.py`。|
|ERR-20261023-091|`content:shared-scope-trimming-blurs-learning-and-blog-depth`|共同精简混淆学习/博客深度。|学习覆盖主题内重要相关知识并补理解断点；博客只补当前原理所需前提，讲通即止，保留理由条件。|四场景加载及边界复核通过；`prompts/scenes/learning.txt`。|
|ERR-20261022-090|`image-viewer:svg-styles-depend-on-uncloned-figure`|SVG类仅在figure，克隆后失配。|SVG绘制样式不只依赖外部容器；放大后比fill/stroke、字号、锚点并实看。|两SVG放大样式一致；`verify_report.py`及viewer截图。|
|ERR-20261022-089|`qa:font-query-before-cdp-css-enable`|未启用CDP域即查询字体。|同会话先`DOM.enable`、`CSS.enable`再查字体；启用工具前冻结资源结果。|字体、备注、导航通过；`verify_report.py`。|
|ERR-20261022-088|`report:prose-completeness-overrides-audience-and-evidence`|混淆观众页、口头展开与制作说明，默认个人成果主线不适合所有用途；中文视觉未校准。|先辨别成果/进展/方案/分享的目的与听众，再按主判断、证据、条件、口头展开审页组；视觉效果优先、文稿焦点其次。指定参照同视口比标题、行长、双栏；制作说明不入正文/备注，边界保留，数据不造。|历史16张PNG、六色、原生缩放通过；`archive/checks/quarto-template-20261025/`。本次类型规则及四场景Prompt加载通过。|
|ERR-20261005-087|`publish:normalized-text-hash-compared-with-raw-bytes`|规范化文本哈希与字节哈希混用。|明确规范化文本/原字节契约，两端读取一致；HTML与QA继续用原字节SHA-256。|四入口字节一致；`published-html.json`。|
|ERR-20261005-086|`animation:svg-child-visibility-overrides-hidden-parent`|子元素可见性覆盖父组隐藏。|停用整组用`display:none`，再激活清除；检查有/无指针转换和回退。|199动画全帧通过；`animation-qa.json`。|
|ERR-20261005-085|`content:raw-runtime-and-math-caption-cross-markdown-escaping`|运行时/公式被普通Markdown转义。|构建后注入原始运行时；先保护公式再转义普通文字；离线查pageerror、KaTeX和交互。|21页无脚本/公式错；`final-integrity.json`。|
|ERR-20261005-084|`browser:download-event-timeout-confused-with-missing-local-file`|下载超时误判未落盘。|按确切文件名重新观察，核对本地时间/大小/内容；已落盘不重下，预览加载完成再下载。|16份材料回收且哈希一致；`received-manifest.json`。|
|ERR-20261005-083|`content:external-markdown-assumed-uniform-syntax`|假定标题/围栏/链接语法统一。|抽查实际语法，按稳定ID核对全集；兼容波浪线围栏，经Markdown/HTMLParser查真实链接及拆分后路径。|309图位、247代码块通过；`check_received.py`。|
|ERR-20261004-082|`delivery:overview-record-links-have-mixed-file-types`|总览混淆记录文件与目录入口。|发布前解析目标并预构建总览；目录查实际入口，不一律`is_file`；中途失败从已完成阶段恢复，不重发。|74链接有效，旧交付/source保持；`archive-manifest.json`。|
|ERR-20261004-081|`trace:rolling-array-alias-write-not-mapped-to-storage-row`|写变量名未映射实际rows。|按对象身份核对别名、行切换、取模下标；同值写入也须标已计算，不能凭值猜别名。|两DP别名逐项通过；`alias-check.json`。|
|ERR-20261004-080|`animation:compact-filter-reuses-primary-method-focus`|主解法过滤删补充解法对象。|逐解法保留真实运算对象；无变化补机制，不松断言；实测SVG默认尺寸与控件距离并看窗口图。|199动画及六色通过；`algorithm-player.js`。|
|ERR-20261004-079|`animation:cell-center-connection-obscures-grid-values`|中心连线遮住格内数值。|箭头从文字区外进出；实看首次写入、入栈与终态，不只验画布边界。|数值清晰、五动画通过；`animation-qa-chapter09.json`。|
|ERR-20261004-078|`qa:heading-innertext-includes-permalink-control`|标题文本含定位控件。|按稳定ID与解码href对应，实点并核对hash；不用整节点innerText或first。|五篇导航通过；`browser-review.json`。|
|ERR-20261004-080|`math:absolute-mathml-without-local-positioning-container`|隐藏MathML缺局部包含块，扩大scrollWidth。|`.katex`设`position:relative`，窄栏长公式局部横滚；同时查scrollWidth与图面，不裁正文。|768恢复720，23页通过；`assets/content/content.css`。|
|ERR-20261004-079|`typography:left-aligned-media-with-full-column-caption`|图面左对齐而图注占整栏。|图面/图注居中且同宽；查默认、40%、刷新、重置、缩放；缓存即时受100%容器上限约束。|23页实看及几何通过；`assets/content/image-size.js`。|
|ERR-20261004-078|`navigation:compact-toc-overlay-without-article-separation`|浮层遮挡正文。|展开目录让正文临时让位，留24–64px；关闭恢复宽度并保锚点；检查代码换行、公式、图注与目录滚动。|23页92组及23回归通过；`tests/test_navigation.py`。|
|ERR-20261004-077|`workflow:archived-demonstration-confused-with-active-prompt-source`|归档演示被当当前Prompt入口。|查看规则直接链当前`prompts/`源文件；制作在`output/_work/`，archive只追溯，不新建演示替代规则。|Prompt与快照比对通过；`prompts/README.md`。|
|ERR-20261004-076|`prompt-maintenance:sample-polishing-displaces-generation-workflow`|样例返修挤占公共Prompt维护。|样例用于定位/验证规则缺口；先完整改稿、内容/读者修订、图文分工再制HTML，不机械轮数或重复确认。|六规则、四场景加载通过；`prompts/common.txt`。|
|ERR-20261004-075|`rednote:batch-html-sources-outside-canonical-pages-directory`|源页父目录违反契约。|源页统一`html/pages/card_N.html`，汇总前查父目录、页序、文件集与资源引用。|三图配对及手机预览通过；`scripts/rednote_artifacts.py:37-39`。|
|ERR-20261003-074|`qa:css-zoom-measured-before-resize-observer-layout-sync`|测量早于观察器布局同步。|等两次`requestAnimationFrame`再测稳定边界，保留原断言；瞬态另记，不混作最终布局。|CSS组合及原生缩放通过；`render_check.py`。|
|ERR-20261003-073|`qa:sequential-interaction-checks-inherit-player-and-fragment-state`|用例继承动画终态和URL片段。|显式建立播放器、URL、折叠/存储前提；每主题实点重置，普通续读清片段，另测章节直达。|明暗全状态/续读通过；`interactions.json`。|
|ERR-20261003-072|`qa:fixed-wheel-count-assumes-toc-height`|固定滚轮次数不适配长目录。|按scrollHeight/clientHeight滚至终态，检测停滞及总时限；到底继续滚，查正文隔离。|400项目录及三场景通过；`scripts/check_chrome_zoom.py`。|
|ERR-20261003-071|`navigation:global-smooth-scroll-for-long-distance-anchors`|全局smooth导致远距眩晕。|默认`scroll-behavior:auto`直接定位；默认运动偏好实测远距前后跳转，保留避让/展开/高亮并同步自包含成品。|导航和位置采样通过；`assets/content/content.css:32`。|
|ERR-20261003-064|`animation:step-reveal-substitutes-for-algorithm-state-transitions`|固定淡入代替真实算法状态。|批量前实看核心运算，逐步对照代码的对象/条件/前后状态/输出；淡入、变量轮播、步号不算机制，DP初值须可辨。|199动画逐帧/回退通过；`assets/content/animation.js:21`。|
|ERR-20261003-070|`qa:svg-text-and-content-box-assumptions`|SVG误用innerText，外框含边距。|用可见text的`textContent`；比例扣除边框内距，分查内容坐标/外框/DPR/像素。|6组语义、17章原生通过；`check_semantics.py`。|
|ERR-20261003-069|`animation:stable-svg-allocation-confused-with-live-state`|创建顺序混作图层，容量混作长度。|面积层固定背景；负下标按当前长度；核对成员身份、标注和中间态，用`Array.isArray`区分包装。|面积49及温度栈可辨；`algorithm-mechanics.js`。|
|ERR-20261003-068|`animation:tree-layout-unions-future-rewired-edges`|全帧边并集污染原树布局。|输入树按初始边布局，构造新树才补关系；当前连接单独更新，查初态/断接边/终态。|114两解法及回退通过；`mechanism-review/114*.png`。|
|ERR-20261003-067|`trace:read-hook-bypasses-precomputation-capture-limit`|新读取钩子绕过采集范围。|所有观测入口共用范围；原算法完整执行，范围外不先序列化再丢；查耗时/体量/原输出。|约5秒、9058状态且输出正确；`execution_trace.py::Recorder.read`。|
|ERR-20261003-066|`qa:rounded-native-zoom-value-does-not-match-option`|显示比例误作精确option值。|先核对option值/标签；仍查DPR与屏幕图面，不把等待超时归因SVG。|0.8/0.5/1档通过；`tests/test_svg_zoom.py`。|
|ERR-20261003-065|`migration:replace-merged-runtime-as-single-script-module`|整体替换script误删邻接模块。|先查构建组装，按模块独有边界替换；核对次数、逆向字节及邻接主题/就绪/交互。|13项相关回归通过；`scripts/build_content.py:145`。|
|ERR-20261003-064|`svg:viewport-relative-width-cancels-native-browser-zoom`|vw宽度抵消原生缩小。|SVG以viewBox为CSS基准；实用原生缩小档比较矩形×DPR；覆盖手动调图、记忆/恢复、宽窄栏，CSS zoom不能替代。|123SVG原生五档通过；`assets/content/image-size.js`。|
|ERR-20261003-063|`reading:range-track-reflows-with-controlled-width`|滑条轨道随正文移动。|工具栏独立最大1184px；逐步实拖查轨道固定、数值双向单调，覆盖目录切换/缩放/锚点。|反跳/位移为0，10回归通过；`tests/test_reader_tools.py`。|
|ERR-20261003-062|`content:multiline-heading-rewrite-without-line-mode`|多行正则未启用re.M且未查零替换。|查替换计数、每题唯一h2 ID、跨文件链接/片段；实点首页深链，不以退出码替代。|100题ID、517链接通过；`final-links.json`。|
|ERR-20261003-061|`qa:table-fit-fixture-assumes-old-reading-width`|临界尺寸fixture沿用旧栏宽。|布局模型变更先复核测试前提，提示同时断言scrollWidth/clientWidth，不改正确功能迁就旧断言。|字号/面板/键盘通过；`tests/test_table_scroll.py`。|
|ERR-20261003-060|`rednote:local-image-preview-from-blank-or-image-document`|blank/图片文档不适合PNG预览。|生成引用最终PNG的本地HTML包装，等待decode；覆盖纯图/混排，查尺寸与实际画面。|纯图/混排/390px通过；`scripts/check_rednote.py`。|
|ERR-20261003-059|`rednote:publication-without-checked-final-page-manifest`|completed未绑定最终页、QA、资源。|统一manifest，纯HTML配对、混排标html/image，不伪造位图源页；查页序/PNG/资源/哈希及缺失、过期、增删改，拒绝不改旧入口/记录。|混排及全量测试通过；`scripts/rednote_artifacts.py`。|
|ERR-20261003-058|`reading:font-size-floor-confused-with-default-readability`|默认可读字号误作硬下限。|默认18px，可选10–24px步长2；保持10/12可达，查记忆、禁用边界与阅读锚点。|10px刷新保留，位移<16px；`font-size/result.json`。|
|ERR-20261003-057|`qa:font-permission-granted-to-wrong-browser-context`|CDP授权缺页面context。|用`Target.getTargetInfo`取上下文，显式授权并确认页面granted再解释空列表/超时。|返回224字体；`native-enumeration.json`。|
|ERR-20261003-056|`reading:fixed-pixel-cap-instead-of-page-percentage`|正文宽度固定像素。|宽度40%–80%、默认60%，保存比例，无固定像素上限；多视口测记忆/目录/连续实拖锚点，目录布局按后续让位规则。|四视口80%正确；`tests/test_reader_tools.py`。|
|ERR-20261003-055|`qa:resume-banner-reflow-invalidates-raw-scrolly-comparison`|提示栏重排使scrollY不可直接比较。|恢复测试比较同一文字/段落及视口位置，覆盖提示栏、折叠、字号重排。|明暗续读及交互通过；`qa-interaction.json`。|
|ERR-20261003-054|`qa:windows-clipboard-crlf-compared-to-dom-lf`|剪贴板LF规范化为CRLF。|源码取`code.textContent`，等复制完成，仅规范化CRLF，严格保留空格缩进与逻辑行。|规范化后逐字符一致；`interactions.json`。|
|ERR-20261003-053|`migration:drop-panel-tree-removes-sibling-controls`|删图容器连带按钮/说明。|先清点SVG、控件、说明及事件依赖；只解包容器保非SVG节点，迁后查数量并实点。|三按钮及状态恢复；`work/review/interactions.json`。|
|ERR-20261003-052|`migration:lazy-image-decode-blocks-reading-ready`|旧lazy图片阻塞ready。|迁后查图片complete、`contentReadingReady`与续读；按当前就绪契约处理旧lazy，本篇设eager。|三图及ready恢复；`delivery/qa.json`。|
|ERR-20261003-051|`maintenance:powershell-concatenation-in-path-pair`|数组内加法与逗号边界不明。|路径拼接分别加括号；迁移前逐对解析绝对路径并核对工作区范围，不边解析边移动。|38项11289文件哈希一致；`archive/manifest.json`。|
|ERR-20261003-050|`content:fixed-figure-count-overrides-explanatory-need`|图数或全篇总量替代局部解释需求。|学习/博客优先文稿质量与有效图片密度；按重要知识段复核图解分布，补机制空档，不能以全篇图多代替覆盖。图数按解释收益取舍，无固定配额，用户指定则遵从。|历史四场景一/零图审核完成；`references/content-plan.md`。本次核实Infra末章缺图并更新共同/场景规则，四场景Prompt加载通过。|
|ERR-20261003-049|`authoring:latex-backslashes-consumed-by-outer-script-string`|外层JS先消费LaTeX转义。|数学原文单独补丁保存再读取；逐层查分隔符、反斜杠、控制字符及公式DOM/图面。|KaTeX及200%图核对通过；`Hyperball博客-图文版.md`。|
|ERR-20261003-048|`content:quality-review-confused-with-rendering-checks`|页面QA替代理解审核。|全读原稿/成稿，按范围核对解释、数值来源、图文和边界；审读绑定当前HTML/快照，缺失/空白/过期/未处理警告不发布，HTML改后重审。|无审读被拒，30组用例通过；`scripts/content_review.py`。|
|ERR-20261003-047|`publish:move-old-entry-before-copy-without-rollback`|移旧再复制且无回滚。|同层完整暂存后备旧并切换，失败恢复且不写成功；临时目录注入复制/移动/安装故障，查首次发布、旧版、备份、记录及清理范围。|5测试22场景通过；`scripts/publish_utils.py::replace_delivery`。|
|ERR-20261003-046|`qa:fixed-capture-offset-under-wrapped-toolbar`|固定截图偏移不适应工具栏换行。|定位/步长读实际scroll-padding；工具栏高度变化后复核覆盖范围。|原生100/150/200%通过；`scripts/check_chrome_zoom.py`。|
|ERR-20261003-045|`image-size:absolute-pixel-handle-stale-during-reflow`|手柄缓存像素早于观察器更新。|横向用相对容器右边界比例；窗口/CSS缩放切换即时测，不用延时掩盖瞬时滚动。|三窗口三CSS档通过；`assets/content/image-size.js`。|
|ERR-20261003-044|`reading:reanchor-on-every-range-input-accumulates-drift`|每次input重选锚点导致漂移。|pointerdown保存一次锚点，整次实拖复用，结束/取消清除；键盘单步按当前位置。|12步实拖回归通过；`tests/test_reader_tools.py`。|
|ERR-20261003-043|`typography:automatic-media-outset-breaks-column-alignment`|媒体自动加宽破坏统一栏。|文字/媒体容器/图注/表格/代码默认同栏，图在栏内等比调；缩小图及图注按后续居中规则。仅用户明确要求时才加宽媒体栏。|图文宽差<1px；`tests/test_toolbar.py`。|
|ERR-20261003-042|`typography:removing-section-rules-weakens-boundaries`|减装饰误删章节分隔。|长文主章节保细线和留白；模板借鉴不覆盖用户阅读标记。|明暗全文边界实看；`assets/content/content.css`。|
|ERR-20261003-041|`typography:balanced-description-lines-break-text-column`|balance压短导语使栏宽不一。|中文导语自然换行；标题/导语/续读/正文同栏并查实际行长，不只查无溢出。|四区边界差<1px；`alignment.json`。|
|ERR-20261003-040|`toolbar:single-flex-row-overflows-after-new-control`|单行工具栏依赖视口断点。|始终允许flex换行并自适应高度；新增控件查小窗口叠加CSS缩放，原生检查另做。|九组合无溢出；`tests/test_toolbar.py`。|
|ERR-20261003-039|`css:substring-rule-removal-matches-unrelated-selector`|子串mark误匹配wordmark。|删除按完整选择器，立即查diff与共享首屏图面。|wordmark恢复、四HTML核对；`assets/content/content.css`。|
|ERR-20261003-038|`qa:generic-dialog-locator-after-new-dialog-added`|通用定位混淆组件归属。|图像弹窗限`.image-viewer`、正文SVG限figure直接子、字体限`#font-options`、成品限正式区；不用first掩歧义。|20回归与17章放大通过；`tests/test_image_viewer.py`。|
|ERR-20261003-037|`reading:custom-search-duplicates-browser-find`|单篇HTML套用站内搜索。|区分站内发现与单篇查找；单篇沿用Ctrl+F，不重建文内搜索/快捷键。|无搜索入口及Ctrl+K处理；`assets/content/document.html`。|
|ERR-20261003-036|`svg:compound-path-marker-end-only-on-final-vertex`|一个path仅末顶点有marker。|多箭头分别用path共用marker，逐条查头部与方向。|原图及390px两箭头完整；`colors-after.json`。|
|ERR-20261003-035|`renderer:html-only-output-path-assumed-save-html-layout`|HTML与PNG路径分支不同。|按实际output_format/save_html分支和清单定位，不跨模式猜路径。|card/pages路径回归通过；`scripts/rednote_render.py`。|
|ERR-20261003-034|`palette:academic-missing-shared-svg-variables-and-classes`|academic缺共享SVG变量/类。|跨模板实际生成并查变量、类、填充/线/文字；新规则限自绘类，保原字体画幅。|节点/箭头/字体/390px通过；`tests/test_palette_bridge.py`。|
|ERR-20261003-033|`qa:assumed-pillow-installed-for-browser-pixel-check`|假定环境有PIL/lxml。|先核对实际依赖；简单像素用Canvas，链接用HTMLParser，不为单次核验加依赖。|像素及51链接通过；`archive/maintenance/finish-width-review.py`。|
|ERR-20261003-032|`qa:raw-unicode-href-compared-with-encoded-location-hash`|中文href与编码hash不同。|双方统一URL解码后比片段，再查目录状态和布局。|中文导航及4回归通过；`tests/test_navigation.py`。|
|ERR-20261003-031|`navigation:toc-scroll-chains-into-article`|目录滚动边界链入正文。|`overscroll-behavior:contain`；滚至末项后继续滚，核对末项可见且正文不动。|末项可达且正文保持；`tests/test_navigation.py`。|
|ERR-20261003-030|`navigation:compact-toc-in-document-flow`|目录在文章开头，打开后不在视口。|中段/末尾打开查视口边界、隐藏偏好/断点、末项和正文位置，覆盖小窗口及原生缩放；布局沿用后续让位约定。|960×667/720×500可见；`positions.json`。|
|ERR-20261003-029|`inspection:windows-gbk-stdout-for-math-dom`|stdout沿用GBK导致数学字输出失败。|文件编码与stdout分别核对；Windows管道/CLI显式`-X utf8`，不改正文绕过输出失败。|DOM及字号JSON输出成功；`fraction-bounds.json`。|
|ERR-20261003-028|`prepare:known-main-entry-omitted-with-supporting-markdown`|已知主稿仍依赖唯一候选。|含辅助Markdown或已知主稿时显式`entry`/`--entry`；辅助材料随目录保留，不重复问已知入口。|七页渲染/缩放/快照通过；`run.json`。|
|ERR-20261003-027|`image-viewer:source-inline-dimensions-override-fit`|克隆内联尺寸覆盖弹窗适配。|弹窗接管克隆尺寸，同时限宽高并保比例，不改原节点；覆盖竖图/固定内联尺寸和缩放窗口，查实际矩形。|图高900降720匹配frame；`fixed-image-check.json`。|
|ERR-20261003-026|`image-viewer:image-only-clone-loses-figure-context`|仅克隆媒体丢图注条件。|弹窗保图注公式/链接/条件，ID去重；无图注清旧说明，关闭恢复位置与焦点。|两篇原生三档明暗通过；`tests/test_image_viewer.py`。|
|ERR-20261003-025|`table-hint:absolute-note-without-owned-bottom-space`|绝对提示无底部空间。|仅溢出表格留足提示空间，切方向不改间距；最大字号查普通/折叠面板底边及开关/窗口变化。|嵌套边界及7测试通过；`nested-light.png`。|
|ERR-20261003-024|`code-preview:parent-em-height-and-padding-clip-partial-line`|pre/code字号和padding露半行。|字号设pre由code继承，按code行高限代码区；追踪源行边界，覆盖16/18/24px与三CSS档，展开/复制保全。|九组合及6测试通过；`tests/test_code_wrap.py`。|
|ERR-20261003-023|`qa:native-zoom-first-instance-only`|截图只取首实例。|枚举图/代码/表格/补充块，宽表分屏补拍；数量对截图清单，实看后续实例，不以QA推断已看完。|4表2代码及右侧实看；`delivery/checks/native-zoom`。|
|ERR-20261003-022|`reading:resume-location-without-code-view-state`|未保存代码换行/展开高度。|先恢复显示再定位；按标题上下文和代码内容识别，覆盖代码插入/短结尾并核对可见源行。|状态及源行位置回归通过；`tests/test_resume_views.py`。|
|ERR-20261003-021|`qa:native-zoom-css-clip-applied-to-dip-surface`|CSS clip误用于原生DIP图面。|不传CSS clip，捕获完整浏览器表面再视口分屏；核对PNG尺寸与innerWidth×DPR并实看。|200%图面1418×902；`scripts/check_chrome_zoom.py`。|
|ERR-20261003-020|`reading:font-reflow-without-content-anchor`|字号/目录重排依赖浏览器锚定。|变更前保存文字插入点或块内位置，再恢复视口位置；真实长文追踪同一文字，覆盖自动锚定关闭。|位移约0.3/0.02px；`tests/test_font_position.py`。|
|ERR-20261003-019|`navigation:short-last-section-never-reaches-active-threshold`|短末章达不到阈值，当前项失效。|文末选最后可见标题，只调目录scrollTop，不滚正文；查长目录/短结尾/折叠隐藏标题。|32章及真实文末通过；`tests/test_navigation.py`。|
|ERR-20261003-018|`git:renamed-workspace-cross-account-ownership`|切账户后新路径未被信任。|先核对目标绝对路径与账户，仅本次命令用`git -c safe.directory=<根目录>`，不全局通配信任；失败即停。|508ee79成功且全局未改；提交命令记录。|
|ERR-20261003-016|`reading:generated-id-collides-with-author-id`|自动ID与作者ID冲突。|按已有ID分配唯一值，summary稳定命名并去重；检查控件/续读目标及全页ID。|44回归通过；`test_generated_ids_do_not_shadow_author_ids`。|
|ERR-20261003-017|`reading:double-anchor-scroll-offset`|padding/margin重复避让。|仅根scroll-padding负责顶部避让；实查目录目标位置、当前章节和续读标题，不只查hash。|跳转距顶100px、标题正确；`assets/content/content.css`。|
|ERR-20261002-015|`report:intrinsic-grid-size-before-transform`|Grid按未缩放舞台布局。|舞台相对容器绝对居中，translate+scale；导出恢复正常定位保1280×720；多窗口查四边及截图，不只查scrollWidth。|小窗完整居中，PNG通过；`scripts/render_content.py`。|
|ERR-20261002-014|`inspection:rg-inherits-piped-stdin`|管道Python使rg继承stdin。|子进程显式搜索`.`/目标目录；跨配置检索含隐藏目录排除`.git`，不把空结果当无匹配。|8命中完成替换；`.claude-plugin/`、`SKILL.md`。|
|ERR-20261002-013|`content-export:stale-pages-after-rerender`|缩页后旧图被整体复制。|只清约定自有页图；发布核对根级`page-\d+\.png`集合与QA/哈希，测多→少和增删改；保独立配图/checks及旧入口/记录。|非法页图拒绝且旧版不变；`tests/test_publish.py`。|
|ERR-20261002-012|`qa:automation-scroll-contaminates-theme-position-test`|定位器滚动/动画污染位置。|先稳定滚动或关闭测试smooth，真实视口坐标点击，确认主题改变；隔离工具额外滚动与延迟事件。|误差<2px、25回归通过；`tests/test_navigation.py`。|
|ERR-20260914-011|`cover:explanatory-viewpoint-replaces-central-claim`|封面讲解视角取代核心关系。|先提炼文章核心变量关系，主标题直接表达，不以辅助概念/读后感替代。|标题与有效学习率一致；`cover-check.json`。|
|ERR-20260914-010|`qa:devtools-source-request-mixed-with-page-resources`|资源事件混入后续DevTools请求。|页面/图片/公式/字体就绪且资源失败为零后，复制列表冻结阶段结果再启CDP；后续请求另记，不忽略真实资源错。|12页/10页离线通过；`interaction-check.json`。|
|ERR-20260914-009|`imagegen:construction-instructions-rendered-as-content`|构造数值被生图渲染为文字。|分离上图文案/构造说明，禁坐标像素标注；核心几何提供已核对参考图，逐张查方向/等长等关系。|无像素标注、几何近似正确、3:4；`card_4.png`。|
|ERR-20260914-008|`resources:relative-script-path-as-uri`|相对__file__不能直接as_uri。|资源生成file URI前`Path(__file__).resolve()`，覆盖相对runpy启动。|相对启动导出及22测试通过；`scripts/rednote_render.py`。|
|ERR-20260906-007|`cli:documented-layout-flag-unsupported`|文档参数与checkout CLI不符。|脚本/文档版本变化先查当前`--help`，以实际参数和渲染为准。|省略layout后封面+8卡完成；`scripts/rednote_render.py:955-984`。|
|ERR-20260906-006|`renderer:theme-output-contract`|主题/工具被误用于推断交付结构。|小红书正文完整且统一HTML制图，辅助视觉才分HTML/SVG或生图；比较复用正文，配文仅摘要，容量不足增页，保3:4/字号；参考图不自动换字体。|2160×2880及离线HTML通过；`references/content-plan.md`。|
|ERR-20260906-005|`theme:light-page-number-contrast`|浅色页码沿用白色。|浅色主题显式设页码次要文字色；实看PNG中页码/标签/正文对比。|页码覆盖后可读；`assets/themes/professional.css`。|
|ERR-20260906-004|`fonts:css-family-without-installed-font`|CSS字体栈未证明实际字体。|字体变更后用`CSS.getPlatformFontsForNode`查中/英/代码实际字体，不只查computed family。|正文MiSans、代码Consolas；`references/environment.md`。|
|ERR-20260906-003|`pagination:lossy-sentence-separators`|split/strip/join丢原分隔符。|零宽切分保空白，长句仅原词边界拆；断言split后join等于原文，覆盖中英/换行并保代码/公式/SVG完整。|无损重组测试通过；`tests/test_renderer.py`。|
|ERR-20260906-002|`math:markdown-and-svg-interference`|Markdown/SVG干扰公式，CDN不稳。|保护公式但跳过代码示例，用本地KaTeX，自绘样式不碰内部SVG；离线查数量/根号/实际公式外框，少量内部纵差不算溢出，仍拒非法公式。|离线根号通过、2000px块仍拒；`tests/test_renderer.py`。|
|ERR-20260906-001|`environment:orphan-playwright-installer-lock`|中断安装子进程仍持锁。|按命令行/父子关系核对本次残留；确认安装树退出再清确切锁目录，禁止并发安装器。|安装及Chromium启动通过；`references/environment.md`。|
