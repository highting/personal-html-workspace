# 内容制作工作区

本目录维护个人学习、博客、技术汇报和小红书卡片。先读取根目录 `SKILL.md`、`references/workspace.md` 和 `.codex/error-notebook.md`（若存在）；学习/博客/汇报再读 `references/content-workflow.md` 与 `content-scenes.md`，小红书读 `references/rednote-scene.md` 和所选模式说明。

- 输入：`inputs/<分类>/<主题>/`，兼容已有 `blogs/<分类>/<博客名>/`。完整文件夹保留正文与配图的相对路径，分类可新增，不移动或覆盖原稿。
- 交付入口：`output/<短名>/`。学习/博客默认是明暗可切换的连续 HTML；汇报交16:9 HTML、讲者备注和逐页PNG；小红书保持原图片、`标题.txt`、`配文.txt`、`预览.html` 结构。新场景用 `prepare_content.py`、`build_content.py`、`render_content.py`、`publish_content.py`；原小红书脚本和主题保留。`html/images` 仅决定辅助视觉工具，不改变场景或正文形态。
- 用户仅给主题名时在 `inputs/` 和 `blogs/` 定位，唯一匹配直接处理；同名或无法判断主稿时才询问。沿用已有场景和主题，不因没有重贴材料换题。
- `blogs/` 中的文件作为原始材料保留。中间材料放在 `output/_work/<短名>/<时间戳>-<模式>/` 的 `source/`、`work/` 和成品暂存 `delivery/`，不覆盖原稿；新生成使用新的工作目录，同次修正复用。更新短路径成品时先保留原有交付，避免残留旧图片。
- 交付直接链接短路径成品，不把 `work/` 当发布入口；`delivery.md`、`run.json` 记录主线、图解与真实检查。长文和汇报实际查看明暗两套截图、目录及关键交互；`render_content.py` 检查离线资源、公式、边界和汇报页。通过且实际查看完成后才标记 `completed`；HTML/PNG 有修改需重查，不手改 QA 绕过失败。
- 小红书继续遵循原浅暖米色 `#F7F4ED`、academic、字体、3:4与正文全在图片里的规则，标题直述主题，第一人称配文只作摘要。两套比较复用正文页，只替换非正文视觉。新长文/汇报的明暗模板不替换卡片效果，其他场景不强制发布配文。
- `assets/`、`scripts/`、`references/`、`skills/`、`tests/` 是公共工具；`demos/` 是示例。不要把单篇博客材料放进这些目录，也不要把临时安装文件放进博客输出。

完整目录规则和可直接使用的 prompt 见 `references/workspace.md`。
