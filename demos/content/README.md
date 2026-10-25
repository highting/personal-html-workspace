# 四场景示例

这里是可复现的排版与工作流示例。学习与博客共用模板，以内容详略区分；汇报使用16:9演示。[小红书竖版稿](rednote.md)使用原渲染器，保留正文、图解与必要条件。制作说明只留在本页，不进入最终成品。

源稿：[学习稿](learning.md)、[博客稿](blog.md)、[汇报稿](report.md)。学习/博客生成明暗截图，汇报只生成白底页并提供纸白背景选择，小红书为纸白图片。检查预览统一归档到本地 `archive/demo-renders/content/previews/`，不随Git分发，可按下方命令重新生成。

[Softmax完整学习文档](softmax-longform/main.md)用于检查密集正文、数值列、长代码收起/换行与原生缩放。标准库代码可独立运行，教学数据不代表模型实验。

图像放大视图保留原图注，并支持适合窗口与进一步放大。

共享模板的视觉样例使用同一组明确的教学数据：A组为2、4、6，B组为0、4、8。两组均值都是4，极差分别为4和8；不代表实测成果。

- [汇报版式](report-layouts.md)：封面、左文右表、主图与开放对照、三步过程。用 `build_content.py --scene report` 构建，再用 `render_content.py` 检查与导出。
- [小红书版式](rednote-layouts.md)：图文开篇、开放对照、有序步骤。每个完整语义页用一个 `div.card-page` 保持图文同页；用 `rednote_render.py --save-html` 生成，随后运行 `check_rednote.py` 并查看全部原图和390px预览。

样例生成文件放 `archive/demo-renders/`。学习、博客复用阅读模板，重点检查内容与可读性；这两套样例专门用于小红书和汇报的视觉校准，不替代场景内容审读。

按根README安装依赖并显式准备中文字体缓存，再从仓库根目录执行：

```bash
python -X utf8 scripts/build_content.py demos/content/learning.md --scene learning --output archive/examples/demo-learning/index.html
python -X utf8 scripts/render_content.py archive/examples/demo-learning/index.html --scene learning --output-dir archive/examples/demo-learning/delivery
```

博客和汇报改为对应文件名与scene。学习/博客离线打开 `index.html`，太阳/月亮按钮切换主题，A−/A+调整字号；目录可收起，图片或SVG可放大。汇报可用方向键、Home/End、N备注和目录直达，背景只可选纯白/纸白；PNG默认白底，不生成深色样张。小红书运行 `rednote_render.py demos/content/rednote.md --math katex --save-html -o <目录>`，再用 `check_rednote.py <目录>` 生成手机预览并逐张检查。
