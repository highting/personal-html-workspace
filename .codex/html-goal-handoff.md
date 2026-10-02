# HTML持续优化交接

目标保持完整：持续优化HTML、排版、视觉、实用功能和配色；借鉴成熟设计，用真实长文生成、查看、验证，每轮保留记录并提交本地Git。不能将一次改进的完成当作持续目标完成。

## 工作区与约束

- 实际仓库：`D:/Project/html-craft`，分支`codex/personal-html-workspace`。当前会话的旧cwd/写入根仍可能显示`D:/Project/RedNote-Render-Skill-main`；命令显式指定实际workdir。需要写入时使用已授权的提权工具执行。
- Git跨执行账户时用命令级`git -c safe.directory=D:/Project/html-craft`，不设置全局通配信任。只做本地提交，不推送。
- 阅读根`AGENTS.md`、`SKILL.md`、`references/content-workflow.md`、`visual-system.md`和完整错题本；本页是交接基础，主代理完整阅读。
- 学习/博客共用连续HTML；报告是16:9演示HTML和PNG；小红书仍为academic浅暖米色3:4图片、正文全在图中。不要将共享阅读样式套入小红书。
- 视觉优先，配色克制；评论、点赞、访问量、分享、装饰动画暂缓。原稿与source快照只读，最终成品不含制作说明。
- 使用桌面和缩放验证，不另做手机适配。字号、图像放大、目录、代码与表格、续读都按实际内容检查。

## 当前位置

- 用户入口`inputs/`没有第二篇长文；`blogs/`只有Hyperball及配图说明。无需重复全仓寻找材料。
- 已新编写`demos/content/softmax-longform/main.md`作为完整学习文档：7章、4表、2代码段、1流程图。标准库代码已执行；NumPy片段按官方API核对，未安装或运行NumPy。
- Hyperball成品：`output/Hyperball-阅读版/index.html`。对应run为`output/_work/Hyperball-阅读版/20261002-232954-821907-blog-html/`，工作稿`work/Hyperball博客-图文版.md`。
- Softmax成品：`output/Softmax-学习/index.html`。对应run为`output/_work/Softmax-学习/20261003-030343-927225-learning-html/`，工作稿`work/main.md`。
- 两篇技术内容与快照未被视觉迭代改写。各轮`delivery.md`及`work/iterations/`保存依据和对照；发布器保留上一版短路径交付。以run.json、QA哈希和当前Git为权威，不手改QA通过状态。

## 已有实现

- 共享模板：标题区不重复身份标签；章节目录分层、跟随当前项且识别短结尾；16–24px字号保持当前文字位置；明暗主题保持位置。
- 图面与图注分组，来源区采用正常字形；数值列可右对齐并使用等宽数字。表头/短代码不拆开，宽表格局部滚动并按真实溢出显示方向提示、提供键盘聚焦。
- 代码在构建时高亮，支持文件名、重点行、复制、长代码收起及可选换行；预览按代码区完整视觉行裁切。续读先恢复折叠/代码显示状态，再定位。
- 深色正文`--reading-text: #D6DEEA`，标题/图中标签`--text: #E5EAF2`，字体字重未改。颜色对比度与实际字体已核对。
- 公式外部间距在长文中采用1.1em，随字号变化，内部高度及8px上下安全留白保留。两篇明暗正文42屏独立复核后，只采纳了有对照依据的公式节奏调整。
- 短行内公式按整体换行，长表达式限定在容器宽度内并保留KaTeX断行。24px下真实短表达式已由两行变为一行，50项求和仍能多行重排；字号定位与根号可见性回归通过。
- 图像弹窗保留原图注、已渲染公式与链接；克隆ID和引用去重，支持带引号URL引用；按宽高适合窗口，放大后可用方向键滚动，关闭恢复原位置/焦点。报告弹窗保留当前页。
- 本轮图注与窗口适配的依据位于两篇run的`work/iterations/20261003-viewer-captions/`。已复现原图注丢失、固定尺寸竖图900px被720px窗口裁切，并验证修正。

## 验证工具

- Python使用`.venv/Scripts/python.exe`。默认Playwright Headless Shell可用；其完整Chromium路径不存在，勿重复安装。
- 原生缩放使用`C:/Program Files/Google/Chrome/Application/chrome.exe`与`scripts/check_chrome_zoom.py`，独立临时普通配置，通过Chrome外观设置Page zoom操作100/150/200%。Ctrl快捷键与其他浏览器未单独验证。
- 原生zoom必须捕获完整CDP表面并核对尺寸，不能用CSS坐标裁图。脚本包含全部图表/代码实例、宽表横向区域及各缩放下的图像弹窗。
- 重查仅清理本工具约定命名的截图，保留独立配图。两图→一图及同前缀非工具文件保留已实际验证。
- 修改HTML后重建、重查、实际看图，再标completed并publish。配色与字体检查不等于完整无障碍认证。

## 继续方向

两篇完整视觉复核与行内公式调整已完成。下一轮转到技术汇报模板的真实呈现，检查现有报告的标题页、正文图文密度和16:9视觉层级，保持场景边界，不机械套用长文布局。需要新会话时使用本页及现有run记录接续，不重做已验证的探索和基线。
