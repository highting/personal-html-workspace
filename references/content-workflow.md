# 四场景工作流

以原 `main` 的小红书实现为基础，四场景按用途分路。新流程不替换 `rednote_render.py` 或原主题；学习/博客/汇报使用新增静态模板。先读根技能和[场景规则](content-scenes.md)。

## 准备材料

用户将新材料拖入 `inputs/待分类/` 后，在会话中发出制作要求；代理先归类到 `inputs/<内容分类>/<主题>/`，不改正文或破坏附件相对路径，再运行准备脚本。已有分类和 `blogs/` 原地兼容，制作时原稿只读。分类、成品命名和版本按[工作区约定](workspace.md)。优先识别 `main.md`、`article.md`、`index.md`，已知正文显式传 `--entry`；其他格式用对应工具读取，转换稿放 `work/`。

```bash
python -X utf8 scripts/prepare_content.py "inputs/机器学习/Softmax" --scene learning --name Softmax-学习
```

`--entry` 指定相对主稿路径，`--mode html|images` 仅记录辅助图工具。新成品用 `<主题短名>-<场景>`，始终显式传 `--name`，并核对已有目标的来源、场景，防止入口互相覆盖。脚本建立 `output/_work/<成品名>/<时间戳>-<scene>-<mode>/` 的 `source/`、`work/`、`delivery/`，输出 `run.json` 与 `work/任务Prompt.txt`。新请求或已交付后的改版新建工作目录，同次修正复用。`source/` 是只读快照；其哈希用于交付核对。

读取 `prompts/common.txt`、所选 `prompts/scenes/<scene>.txt` 和[成品视觉规则](visual-system.md)，把prompt作为基础参考，按实际内容调整详略、顺序与布局。先生成代表性页面，实际查看后修正再完成全篇；制作说明、占位文案只留在工作记录。

## 学习与博客

在 `work/` 写好的 Markdown 支持 YAML 的 `title`、`description`、`author`、`date`；后两者只采用真实信息。标题可从第一个一级标题获取。h2章节、h3小节形成目录；内嵌SVG与本地图片可作图解，公式行内用 `\( ... \)`，独立用 `$$ ... $$`。

```bash
python -X utf8 scripts/build_content.py "<work_entry>" --scene learning --output "<run_dir>/work/index.html"
python -X utf8 scripts/render_content.py "<run_dir>/work/index.html" --scene learning --output-dir "<artifact_dir>"
```

博客将两处scene改为 `blog`，与学习共用模板，按论点与证据组织内容，详略服从读者目的。构建器可接收可信 `.html` 正文片段，直接放入 `.prose`。`--theme light|dark|system` 设置初始偏好，顶部配色选择器提供浅深各三套，太阳/月亮按钮切换并记住两种模式各自的选择；字号可调16–24px，图片和SVG支持点击/Enter放大、Esc关闭。放大视图保留原图注的条件、公式和链接，适合窗口同时按宽高计算；放大后可滚动或聚焦图像区用方向键查看，关闭恢复原位置与焦点。目录可收起。CSS/JS、KaTeX和数学字体内嵌，本地 `<img src>` 转为data URI；网络图片需先本地化。

顶部工具栏直接提供字号、正文宽度滑条（560–960px，默认704px）、恢复默认宽度、打印、目录、配色和明暗切换，不再使用阅读设置弹窗。宽度滑条拖动即时重排，整次拖动保持同一阅读锚点并记住数值；支持键盘方向键，窄窗口自动适应可用空间。打印按钮可打开浏览器对话框保存 PDF。浏览器 `Ctrl+F` / `⌘+F` 负责文内查找，不另外实现搜索。打印使用白底，完整展开补充内容和代码，保留动画完整步骤，结束后恢复折叠状态。

调节字号、正文宽度、收起桌面侧栏或开合顶部工具栏时保持当前可见的阅读内容；文字按插入点定位，图面和段间留白按当前块定位。工具栏右侧上箭头可隐藏整栏，右上角固定的下箭头可恢复；按钮常态只显示小图标，悬停说明和无障碍标签保留用途；记住手动选择，隐藏控件不进入Tab顺序，开合后焦点落在可见的对应按钮。自然换行仍可能让同一行末尾的词移到下一行，但不能因整篇重排而跳到相邻段落。缩小桌面视口或浏览器放大后，目录以当前视口中的可滚动浮层打开，不把面板插回文章开头；选择章节后收起，Esc收起并将焦点返回目录按钮；收起工具栏同时关闭目录浮层。

代码围栏可写为 `` ```{.python title="example.py" data-highlight="2 4-6"} ``，分别指定语言、文件名和重点行；普通 `` ```python `` 同样可用。代码在构建时由Pygments高亮，阅读时不联网；复制保留完整代码，超过20行提供展开按钮。无法访问剪贴板时明确提示，不显示虚假成功。

长行超出代码容器时提供“换行”按钮，读者可在原始行布局和软换行之间切换；短行不增加按钮。续行对齐代码正文，原始行号只显示一次，重点行覆盖整个逻辑行。显示换行不修改源文本，复制仍保留原有空格与换行。

宽表格只在实际溢出时显示方向提示，随左右位置更新；可通过Tab聚焦后用左右方向键滚动。表格区域采用图注或所在章节命名，未溢出的表格不增加Tab停留点。窗口、字号及折叠内容变化后重新判断，不通过截断内容消除溢出。

补充内容用 `<details markdown="1">` 包裹，第一项写 `<summary>补充内容标题</summary>`，中间留空行后写Markdown，最后关闭 `</details>`。核心条件与关键结论留在展开的主线中，不为展示功能强行折叠。检查器会展开补充内容与长代码后检查，默认状态另保留首屏截图。

章节标题自动获得稳定定位链接，悬停或键盘聚焦时显示复制按钮。链接打开优先定位目标并展开其所在补充内容。阅读位置保存在当前浏览器中，再次打开由读者点击“继续阅读”；不会自动跳转。可在front matter指定稳定的 `document_id`，默认按场景与标题区分；同名不同文章应使用不同ID。浏览器禁用本地存储时仍可阅读，文件链接只用于本机定位。

点击“继续阅读”时先恢复已展开的补充内容、代码换行与长代码展开状态，再按章节及章内位置定位。代码显示状态按所在标题、语言、文件名和源文本识别；代码内容改变时不套用旧状态。普通打开或章节链接仍采用默认代码布局，显示状态不会自动改成上次的选择。

长文图片和SVG可拖动右下角手柄，在正文栏内等比例调整大小；方向键微调，Home/End到最小/最大，双击手柄或点击恢复按钮回到原大小。每张图片的大小在当前浏览器中记住，图注不随图片缩窄，点击图片仍打开大图。独立Markdown图片后紧跟以“图1”等开头的斜体图注时，构建器将两者组合为figure；一般文字不自动当图注。原图保持原貌，自绘SVG使用主题变量。适合步骤演示时可按[视觉规则](visual-system.md#用动画解释变化)添加可控动画；默认完整静态图，打印/导出不截取随机中间态。

长文需要集中列出处时，可在工作稿写`<aside class="article-sources" aria-label="来源">`，内含`<p class="sources-title">来源</p>`及带链接的出处段落，最后关闭`</aside>`。它使用次要字号与正常字形，不加入正文目录；来源和图示说明由实际材料提供，模板不自动生成。关键论断的引用仍放在论断附近。

首次构建前显式执行 `python -X utf8 scripts/download_content_fonts.py`，下载并校验固定版本Noto Sans SC（思源黑体系列）缓存。构建器用FontTools/Brotli按实际字符制作WOFF2子集，中文正文、标题、SVG、代码中文和备注可离线显示；字体及OFL许可内嵌成品，完整缓存不入Git。来源见[字体说明](../assets/vendor/noto-sans-sc/README.md)。仍需核对实际中文字形与字体，而不只看CSS声明。

不引入React/Next/Astro后台；正文片段可按内容调整排版，模板不是固定图数或章节数的约束。来源链接允许联网跳转，但阅读不依赖联网。不要在成品追加制作记录或机器检查表。

## 技术汇报

Markdown围栏外的独立 `---` 作为分页符，代码和公式保持完整；每页标题用 `#` 或 `##`。`<!-- notes: 备注正文 -->` 保存口头说明。复杂内容可写可信HTML片段，完整页面遵循以下结构：

有独立标题页时，可在整篇front matter设置`cover: true`，仅让第一页采用较大标题和居中的简短内容组；未设置时第一页继续使用正文布局。封面同样检查510px正文安全区，长内容应调整或拆页。可信HTML可用`class="slide slide-cover"`明确选择该样式，不为每页增加独立模板。

```html
<section class="slide" data-export-page data-notes="讲者备注">
  <p class="eyebrow">汇报主题</p>
  <div class="slide-body"><h2>本页主张</h2><p>证据与必要条件</p></div>
  <footer class="slide-footer"><span>主题或来源</span><span>01 / 04</span></footer>
</section>
```

同一HTML片段可包含多页；必须使用上述class和标记，正文在 `slide-body` 安全区内。使用 `.columns` 两栏、`.metric` 强调必要数值；数值只能来自真实材料或标注教学构造。固定页放不下就调整或增页。

```bash
python -X utf8 scripts/build_content.py "<work_entry>" --scene report --output "<run_dir>/work/index.html"
python -X utf8 scripts/render_content.py "<run_dir>/work/index.html" --scene report --output-dir "<artifact_dir>" --theme light
```

`render_content.py` 使用模板的 `setContentTheme` 和 `activateContentExport({index})`，验证主题切换、键盘翻页、备注和每页边界；不猜测其他演示框架接口。自定义HTML需保留模板约定。`--browser-executable` 可指定已有Chromium，默认复用Playwright共享缓存。

## 检查与汇总

检查器离线加载HTML，输出 `qa.json`、明暗首屏与 `checks/` 的全篇、分屏、章节或逐页截图；汇报另交所选主题 `page-01.png` 等。长文检查16/24px字号、100/150/200% CSS布局缩放，另按实际浏览器条件验证原生缩放；不把CSS缩放或DPR记录为原生浏览器操作。学习/博客/汇报不单独验收手机适配。实际查看全部内容，测试目录、主题、字号、图像放大与备注；处理 `warnings` 中的可疑制作文案。QA不能证明内容或审美已通过。

已有完整桌面Chrome时，可运行 `check_chrome_zoom.py` 验证100/150/200%的原生页面缩放，传入 `--scene`、`--output-dir` 和 `--browser-executable`。脚本使用独立临时普通配置，通过Chrome外观设置的Page zoom控件操作，核对DPR、CSS视口和CSS zoom，输出 `qa-chrome-zoom.json` 与截图；不修改日常浏览器配置。Headless Shell不提供该设置界面。原生zoom下CSS视口与浏览器图面像素不同，截图直接捕获完整表面并分屏覆盖内容，不用CSS坐标裁图。键盘快捷键与其他浏览器需另行验证，记录必须写明实际方法。

在 `delivery.md` 分开记录内容审核与呈现验收：改稿结合代表性改前/改后段落；首次制作依据原材料、所选范围和代表性成稿，说明覆盖与取舍、知识组织、关键解释及图解是否支持读者应形成的判断，不制造前后对照。呈现验收记录实际视觉、交互和机器检查。保留来源与未验证事项，不能用截图或QA通过替代内容判断；全部完成后才将 `run.json` 的 `status` 改为 `completed`。

六套配色另运行 `check_content_palettes.py <artifact_dir>/index.html --scene <scene> --output-dir <artifact_dir>/checks/palettes`。它逐套检查语义文字对比度、桌面三档窗口的控件与内容边界，并保存首屏、图表/代码或逐页画面；长文另保存外置阅读工具栏、打印样式和动画步骤。原生缩放仍使用上述独立检查，不能将六套窗口检查记作六套原生缩放检查。实际查看正文、各配色代表画面和动画状态后交付。

```bash
python -X utf8 scripts/publish_content.py "<run_dir>"
```

学习/博客/汇报要求本场景QA通过，核对HTML与导出PNG哈希以及未修改的源快照。HTML/PNG修改后重新检查，不能手改通过结果。短路径更新到 `output/<成品名>/`，旧交付保留在本次工作目录；失败时不替换已有成品。代理随后同步 `output/index.html` 中对应的内容分类、主题和场景条目并核对链接，发布脚本不会自动更新总览。回复优先链接成品 `index.html`。

## 小红书原流程

`inputs/` 与已有 `blogs/` 的日常新建工作目录统一用 `prepare_content.py --scene rednote` 准备，保存共同与场景Prompt，再由 `rednote_render.py` 制图。用 `--save-html` 保存源页；混入独立辅助图片时按[小红书验收](rednote-scene.md#检查与交付)填写最终页清单。运行 `python -X utf8 scripts/check_rednote.py <artifact_dir>`，检查连续页序、PNG解码与尺寸、HTML资源、公式及标签实际大小，生成390px宽预览。逐张查看原图和预览、完成内容审核后才标记 `completed`，再用 `publish_content.py` 汇总。发布器要求当前版本 `qa-rednote.json` 通过，核对图片、源页、资源及清单的哈希；改变后必须重新检查，缺少或过期QA不能发布。`prepare_blog.py` 与 `publish_blog.py` 兼容历史调用和工作目录，但同样执行此门槛；历史成品不自动改写，再次交付需在新工作目录重新验收。小红书不使用长文模板，检查记录不能替代目视验收。

这里的“发布”只指本地成品汇总。脚本不调用AI或生图、不上传社交平台；插件安装与GitHub上传是独立操作。
