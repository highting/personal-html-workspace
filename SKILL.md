---
name: personal-html-workspace
description: Turn source material into personal learning documents, technical blogs, presentation reports, or RedNote image posts. Use distinct scene workflows, offline HTML with light/dark themes, and the established academic card renderer for RedNote.
---

# Personal HTML Workspace

按读者和使用目的选择场景，再整理正文、必要图解和交付形式。学习和博客共用阅读模板，以内容详略适应目的；汇报用16:9逐页演示，小红书保留academic竖版图片。Prompt是基础参考，章节、图数和布局按实际生成效果调整，不为场景重复设计模板。

## 选择场景

| 意图 | scene | 默认交付 | 读取 |
|---|---|---|---|
| 系统理解概念、算法、推导与实现 | `learning` | 连续学习 HTML、章节目录、明暗切换 | [四场景流程](references/content-workflow.md)、[场景规则](references/content-scenes.md) |
| 面向读者组织技术论点与叙述 | `blog` | 连贯博客 HTML、阅读目录、明暗切换 | 同上 |
| 面向团队讲解证据、方案与取舍 | `report` | 16:9 演示 HTML、目录、键盘翻页、讲者备注、逐页 PNG | 同上 |
| 小红书图文、竖版卡片或已有制图任务 | `rednote` | 原 academic 3:4 PNG、HTML 源页、标题与摘要配文 | [原小红书流程](references/rednote-scene.md)、[工作区](references/workspace.md) |

沿用已明确的场景。只有“HTML/生图模式”时，不从工具推断场景；已有小红书任务沿用原行为。明确只请求辅助图或一图流时遵从其范围，不扩成整篇。没有场景线索且无法从上下文判断时，先确认成品用途。

## 共同约束

- 先阅读实际材料、图片和来源，核对变量、条件、公式、shape 与论证顺序。重要论断就近给来源；区分原文事实、教学构造、自行推导和推断，不虚构实验或因果结论。疑似技术错误单独指出，不静默猜测或修正。
- 连续长文保留概念引入、解释、必要推导与结论之间的连接。汇报每页围绕一个讲解任务；小红书图片独立串起选定范围的主线，配文只作摘要。
- 先选理解障碍，再制作实际图解。算法执行、shape 映射、数量尺度、几何或状态变化用 SVG/程序图，核对真实关系；适合表现变化时按视觉规则制作可暂停、逐步查看的SVG动画，保留完整静态状态。`html/images` 只决定合适的辅助视觉工具；正文可靠排版，精确关系不交给生图猜测。
- 原稿只读，制作发生在独立工作副本。默认输入 `inputs/<分类>/<主题>/`，现有 `blogs/` 继续使用；仅给主题名时搜索两个入口，唯一匹配直接处理。成品在 `output/<短名>/`，记录在 `output/_work/`。
- 新长文和汇报使用 `assets/content/` 的离线明暗模板，来源见[模板设计](references/template-design.md)。目录可收起，太阳/月亮图标切换主题；内嵌Noto Sans SC字形子集，标题和正文分别设置字重。首次显式运行 `download_content_fonts.py` 准备缓存。顶部配色包含浅色纯白/纸白/暖米与深色石墨/午夜蓝/暖墨，各套协调背景、文字、代码和图解颜色；证据原图不反色。切换保留阅读位置和当前汇报页。
- 实际打开HTML检查明暗截图、字体、公式、图解与边界；长文另查代码复制、章节直达、续读提示及折叠内容，操作与用法见[四场景流程](references/content-workflow.md)。机器检查不能代替技术与视觉判断。汇报正文不能侵入页脚，容量不足就调整分组和增页，不靠缩字或裁切。

## 执行入口

学习、博客和汇报读取 `prompts/common.txt`、所选 `prompts/scenes/<scene>.txt` 与[成品视觉规则](references/visual-system.md)，用 `prepare_content.py` 建立副本；按材料策划 Markdown 或可信 HTML 正文片段。`build_content.py` 组装自包含 HTML，`render_content.py` 检查明暗主题、离线资源和缩放，实际查看后用 `publish_content.py` 汇总。长文与汇报不单独验收手机适配；长文支持字号调节与图像放大。小红书另用 `check_rednote.py` 检查默认画幅并生成手机预览。成品不含草稿、占位或制作说明，构建器不能替代撰稿和目视检查。

小红书继续使用 `prepare_blog.py` → `rednote_render.py` → `publish_blog.py`；新 `inputs/` 也可用 `prepare_content.py --scene rednote` 准备，再调用同一原渲染器与 `publish_content.py` 的原交付路由。规则见[小红书流程](references/rednote-scene.md)，不将新阅读模板套入卡片。明暗阅读模板不会改变既有 PNG 默认效果。

脚本负责准备、排版、检查、截图和本地汇总，不调用生成模型、不发布社交平台。检查完成后才标记 `run.json` 为 `completed`；未验证事项如实记录。源码变更不表示已安装到个人技能目录。
