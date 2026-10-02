# HTML 模板设计参考

查询日期：2026-10-02。星数是GitHub页面当时显示的近似值，会变化。

| 场景 | 参考项目 | 星数 | 采用的思路 |
|---|---|---|---|
| learning | [Nextra](https://github.com/shuding/nextra) | 13.9k | 分层章节导航、清楚的正文层级、明暗阅读 |
| blog | [AstroPaper](https://github.com/satnaing/astro-paper) | 5.1k | 克制的单文章阅读栏、导语、目录、主题偏好 |
| report | [Slidev](https://github.com/slidevjs/slidev) | 48.9k | 开发者演示、Markdown分页、目录、讲者备注、静态导出 |

三者均提供MIT许可。它们是布局与交互参考，本仓库的静态模板独立实现，不复制上游代码、不安装对应框架。原项目的署名和许可仍保留在仓库；现有内嵌KaTeX见[第三方资源](third-party.md)。

参考的实际功能来源：[Nextra文档主题](https://nextra.site/docs/docs-theme/built-ins)、[AstroPaper主题与布局设置](https://github.com/satnaing/astro-paper/wiki/Customization)、[AstroPaper明暗偏好](https://github.com/satnaing/astro-paper/wiki/Features)、[Slidev功能](https://github.com/slidevjs/slidev#features)、[Slidev颜色模式配置](https://sli.dev/custom/)。

学习与博客共用左侧目录和连续正文模板，区别在内容详略；目录可收起，字号可调16–24px，图片和SVG可点击放大。汇报固定16:9舞台。两类HTML以桌面与缩放使用为验收范围，不另做手机适配验收。共用CSS变量管理背景、文字、代码与图解；普通图形节点使用协调的中性底色，强调色按对象语义少量使用，详见[成品视觉规则](visual-system.md)。证据原图不反色。主题切换记住选择，不重载正文或汇报。

新增HTML采用Noto Sans SC（思源黑体系列）可变字体，正文400、标题600–650字重；构建时仅内嵌本篇实际字形的WOFF2子集及许可。字体来源与固定版本见[字体说明](../assets/vendor/noto-sans-sc/README.md)。代码等宽，中文由同一离线字体回退；数学使用KaTeX字形。实际字体以浏览器核验为准。

长文的代码复制、折叠与续读功能参考[NexT功能文档](https://theme-next.js.org/docs/theme-settings/miscellaneous)，章节定位参考[Blowfish](https://blowfish.page/docs/configuration/)，补充内容组织参考[Material折叠内容](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)。仅借鉴阅读行为，继续使用本项目单文件HTML；不引入它们的框架、评论或访问统计。代码高亮使用[Pygments](https://pygments.org/docs/quickstart/)，在构建阶段完成。

目录的层级区分和当前项跟随参考[Material导航与anchor following](https://squidfunk.github.io/mkdocs-material/setup/setting-up-navigation/#anchor-following)，在本模板内实现，不安装其框架。当前项跟随只调整目录内部滚动，主题切换不能移动正文阅读位置。

新模板只用于学习/博客/汇报，避免将新阅读样式灌入原卡片；小红书继续保留academic的画幅与字体约定。

长文标题区参考[AstroPaper实际文章](https://astro-paper.pages.dev/posts/astro-paper-v5/)的标题与真实元信息层级：正文不重复工具栏已有的身份标签。采用其连续阅读的组织思路，具体字号、留白和公式强调根据本项目长文实测，不照搬作者、日期或宣传组件。

来源区借鉴[Material脚注](https://squidfunk.github.io/mkdocs-material/reference/footnotes/)将补充信息与主线分开的组织方式。本模板使用作者明确提供的来源块，保留出处与图示说明，不自动改写引用或增加工具提示。

宽表格保持局部滚动的处理参考[W3C Reflow说明](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)，聚焦、区域命名与键盘滚动参考[MDN overflow](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow#accessibility)。本项目按真实溢出添加方向提示，不将这些局部检查称为完整无障碍认证。

文字颜色按语义角色区分的思路参考[Carbon颜色tokens](https://www.carbondesignsystem.com/building-blocks/foundations/color/tokens)。本项目的深色长文正文亮度依据真实长文对照微调，标题和图内标签保留原文字色；不照搬Carbon的具体值，也不通过随意减小字重制造层级。

图像放大视图保留图注的思路参考[PhotoSwipe Caption](https://photoswipe.com/caption/)，原图注同时在正文可读。本项目继续使用原生dialog，复制已渲染的公式和链接，按自身窗口与主题排版，不安装PhotoSwipe或复制其示例样式。

行内数学重排依据[KaTeX选项说明](https://katex.org/docs/options.html)：其默认允许在最外层关系或二元运算符后断行。本项目让短表达式整体随段落换行，较长表达式仍在受限宽度内重排，不改变渲染模式或数学记号。

汇报的可选封面借鉴[Slidev的cover与default布局分工](https://sli.dev/builtin/layouts.html)：标题页强调主标题与上下文，正文页承载证据。本项目通过一个样式修饰类及显式`cover: true`选择，不安装Slidev、不自动将所有第一页视作封面。

代码的文件名、重点行与复制操作参考[Nextra代码功能](https://nextra.site/docs/guide/syntax-highlighting)，长行可选换行借鉴[Elementor Code Highlight的Word Wrap](https://elementor.com/help/code-highlight-pro/)行为。只在出现水平溢出时提供换行入口，以控制工具栏密度；不引入相关框架或插件。
