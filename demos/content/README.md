# 四场景示例

这里是可复现的排版与工作流示例。学习与博客共用模板，以内容详略区分；汇报使用16:9演示。[小红书竖版稿](rednote.md)使用原渲染器，保留正文、图解与必要条件。制作说明只留在本页，不进入最终成品。

源稿：[学习稿](learning.md)、[博客稿](blog.md)、[汇报稿](report.md)。学习/博客生成明暗截图，汇报只生成白底页并提供纸白背景选择，小红书为纸白图片。检查预览统一归档到本地 `archive/demo-renders/content/previews/`，不随Git分发，可按下方命令重新生成。

[Softmax完整学习文档](softmax-longform/main.md)用于检查密集正文、数值列、长代码收起/换行与原生缩放。标准库代码可独立运行，教学数据不代表模型实验。

图像放大视图保留原图注，并支持适合窗口与进一步放大。矩阵、向量条采用整体小圆角裁剪，内部格线保持笔直；缓存将K/V作为一个圆角块分隔，token略圆。复制图形时为每个SVG的`clipPath`与箭头设置唯一ID，并检查放大视图中的引用仍有效。

共享模板的视觉样例使用同一组明确的教学数据：A组为2、4、6，B组为0、4、8。两组均值都是4，极差分别为4和8；不代表实测成果。

- [汇报版式](report-layouts.md)：封面、完整证据表、就近标注的共同尺度图、三步过程。用 `build_content.py --scene report` 构建，再用 `render_content.py` 检查与导出。
- [小红书版式](rednote-layouts.md)：图文开篇、共同尺度范围图、有序步骤。每个完整语义页用一个 `div.card-page` 保持图文同页；用 `rednote_render.py --save-html` 生成，随后运行 `check_rednote.py` 并查看全部原图和390px预览。
- [学习连续状态图](learning-states.md)：同一组 token 贯穿草稿验证与 KV 回退，位置固定、失效范围明确；用 `--scene learning` 构建。它是可复用的局部讲解样例，不是完整的推测解码教程。
- [博客综合关系图](blog-relations.md)：共享权重只画一次，两条请求的历史 KV 分开，另画执行阶段；用 `--scene blog` 构建。

样例生成文件放 `archive/demo-renders/`。所有图均为可编辑内联 SVG，使用现有语义色，无新增框架。复用时替换实际对象、数据、条件与图注；长文横图用于竖版时重新安排，不直接缩小。学习/博客检查明暗、目录、缩放和图片放大；汇报查看全部白底 PNG 与纸白背景；小红书查看原图与390px预览。样例不能替代真实材料的内容审读。

图形方法参考：Datawrapper 的端点就近标注、Penn State 的主张与视觉证据、MLU Explain 的固定对象连续状态、Jay Alammar 的整体与局部对应。具体来源与采用范围见[模板设计](../../references/template-design.md)。只借表达方法，教学数据和图形由本项目重新构造，参考截图不嵌入交付。

按根README安装依赖并显式准备中文字体缓存，再从仓库根目录执行：

```bash
python -X utf8 scripts/build_content.py demos/content/learning.md --scene learning --output archive/examples/demo-learning/index.html
python -X utf8 scripts/render_content.py archive/examples/demo-learning/index.html --scene learning --output-dir archive/examples/demo-learning/delivery
```

博客和汇报改为对应文件名与scene。学习/博客离线打开 `index.html`，太阳/月亮按钮切换主题，A−/A+调整字号；目录可收起，图片或SVG可放大。汇报可用方向键、Home/End、N备注和目录直达，背景只可选纯白/纸白；PNG默认白底，不生成深色样张。小红书运行 `rednote_render.py demos/content/rednote.md --math katex --save-html -o <目录>`，再用 `check_rednote.py <目录>` 生成手机预览并逐张检查。
