# 四场景示例

这里是可复现的排版与工作流示例。学习与博客共用模板，以内容详略区分；汇报使用16:9演示。[小红书竖版稿](rednote.md)使用原渲染器，保留正文、图解与必要条件。制作说明只留在本页，不进入最终成品。

| 场景 | 浅色 | 深色 |
|---|---|---|
| [学习稿](learning.md) | ![学习浅色](previews/learning-light.png) | ![学习深色](previews/learning-dark.png) |
| [博客稿](blog.md) | ![博客浅色](previews/blog-light.png) | ![博客深色](previews/blog-dark.png) |
| [汇报稿](report.md) | ![汇报浅色](previews/report-light.png) | ![汇报深色](previews/report-dark.png) |

[Softmax完整学习文档](softmax-longform/main.md)包含7章、4张表、2段代码和流程图，用于检查密集正文、数值列、长代码收起/换行与原生缩放。标准库代码可独立运行，教学数据不代表模型实验。数值表预览：[浅色](previews/softmax-table-light.png)、[深色](previews/softmax-table-dark.png)。

图像放大视图保留原图注，并支持适合窗口与进一步放大：[浅色预览](previews/viewer-light.png)、[深色预览](previews/viewer-dark.png)。

按根README安装依赖并显式准备中文字体缓存，再从仓库根目录执行：

```bash
python -X utf8 scripts/build_content.py demos/content/learning.md --scene learning --output output/demo-learning/index.html
python -X utf8 scripts/render_content.py output/demo-learning/index.html --scene learning --output-dir output/demo-learning/delivery
```

博客和汇报改为对应文件名与scene。离线打开 `index.html`，目录按钮开合侧栏，太阳/月亮按钮切换主题，A−/A+调整正文字号，点击图片或SVG查看大图。汇报可用方向键、Home/End、N备注和目录直达；导出PNG的主题用 `render_content.py --theme light|dark` 指定。小红书运行 `rednote_render.py demos/content/rednote.md --math katex --save-html -o <目录>`，再用 `check_rednote.py <目录>` 生成手机预览并逐张检查。
