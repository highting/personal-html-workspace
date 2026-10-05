# 项目当前状态

当前任务以用户最新指令为准，历史目标不自动授权继续工作、创建会话或提交 Git。

- 公共模板、脚本、测试和示例源稿留在仓库中；原稿仍在 `inputs/` 与 `blogs/`。
- 正式入口：`output/Hyperball-阅读版/index.html`、`output/Softmax-学习/index.html`、`output/Hyperball-汇报/index.html`、`output/Hyperball/预览.html`。总览为 `output/index.html`。
- 2026-10-03 已将历史工作版本、检查输出、生成示例、旧模板和停用环境统一封存到 `archive/` 并排除 Git。原交接完整保存在 `archive/handoffs/html-goal-handoff.md`，旧证据按 `archive/manifest.json` 的相对路径映射查找。
- 最近内容改稿：`archive/work/Softmax-学习/20261003-122841-109246-learning-html/`、`archive/work/Hyperball-阅读版/20261003-122841-137515-blog-html/`。内容审核见各自 `work/content-review.md`，验证边界保留在原 `run.json`。
- 历史 run 与 QA 按原字节保存，包含当时机器的绝对路径，只供追溯。改版重新 prepare 到当前 `output/_work/`，记录继承来源，重新构建与检查；不可直接发布归档 run。
- 当前环境用项目 `.venv/` 与用户共享 Playwright 缓存；换机器按依赖锁文件、字体准备脚本和环境说明重建。旧 `archive/environments/` 不作为运行依赖。
- `output/` 与 `archive/` 都不随 Git 分发。没有本地产物时按示例源稿重新生成；归档不是仓库运行的前提。
