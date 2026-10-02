# HTML 模板设计参考

查询日期：2026-10-02。星数是GitHub页面当时显示的近似值，会变化。

| 场景 | 参考项目 | 星数 | 采用的思路 |
|---|---|---|---|
| learning | [Nextra](https://github.com/shuding/nextra) | 13.9k | 分层章节导航、清楚的正文层级、明暗阅读 |
| blog | [AstroPaper](https://github.com/satnaing/astro-paper) | 5.1k | 克制的单文章阅读栏、导语、目录、主题偏好 |
| report | [Slidev](https://github.com/slidevjs/slidev) | 48.9k | 开发者演示、Markdown分页、目录、讲者备注、静态导出 |

三者均提供MIT许可。它们是布局与交互参考，本仓库的静态模板独立实现，不复制上游代码、不安装对应框架。原项目的署名和许可仍保留在仓库；现有内嵌KaTeX见[第三方资源](third-party.md)。

参考的实际功能来源：[Nextra文档主题](https://nextra.site/docs/docs-theme/built-ins)、[AstroPaper主题与布局设置](https://github.com/satnaing/astro-paper/wiki/Customization)、[AstroPaper明暗偏好](https://github.com/satnaing/astro-paper/wiki/Features)、[Slidev功能](https://github.com/slidevjs/slidev#features)、[Slidev颜色模式配置](https://sli.dev/custom/)。

学习页左侧分层导航，博客主阅读栏与右侧轻目录；目录在桌面和紧凑窗口均可收起。汇报固定16:9舞台。共用CSS变量管理浅色暖米色、深色墨蓝、文字、边界、代码与解释图；图内颜色按对象语义映射，证据原图不反色。太阳/月亮图标切换主题，支持浅/深/系统初始偏好，记住选择，不重载正文或汇报。

新增HTML采用Noto Sans SC（思源黑体系列）可变字体，正文400、标题600–650字重；构建时仅内嵌本篇实际字形的WOFF2子集及许可。字体来源与固定版本见[字体说明](../assets/vendor/noto-sans-sc/README.md)。代码等宽，中文由同一离线字体回退；数学使用KaTeX字形。实际字体以浏览器核验为准。

原 `main` 小红书的academic主题、字体、画幅和渲染代码保持不变。新模板只用于学习/博客/汇报，避免将新模板样式灌入原卡片。
