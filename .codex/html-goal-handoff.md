# 项目当前状态

当前任务以用户最新指令为准，历史目标不自动授权继续工作、创建会话或提交 Git。

- 公共模板、脚本、测试和示例源稿留在仓库中；原稿仍在 `inputs/` 与 `blogs/`。汇报样式独立在 `assets/content/report.css`，学习/博客继续共用阅读模板。
- 总览为 `output/index.html`。2026-10-23新增/改版入口：`output/Infra系统学习-学习/index.html`、`output/Infra系统学习-博客/index.html`、`output/Infra系统学习-汇报/index.html`、`output/Infra系统学习-小红书/预览.html`；其余既有主题在总览保留。
- 2026-10-03 已将历史工作版本、检查输出、生成示例、旧模板和停用环境统一封存到 `archive/` 并排除 Git。原交接完整保存在 `archive/handoffs/html-goal-handoff.md`，旧证据按 `archive/manifest.json` 的相对路径映射查找。
- 最近内容改稿：Infra四场景，迁移清单见 `archive/infra-20261023-manifest.json`。学习面向“了解训练流程、不熟悉底层系统”，18章、20图、3个状态演示；博客聚焦Prefill/Decode；汇报8页验证成果；小红书5张KV卡片。各run的`content-review.json`绑定最终HTML，实际检查见`delivery/checks/`；发布后离线与74个总览链接核验见`archive/checks/infra-delivery-20261023/`。
- 历史源快照和QA保留原字节；run记录保留创建时绝对路径，并可附归档迁移信息，只供追溯。改版重新 prepare 到当前 `output/_work/`，记录继承来源，重新构建与检查；不可直接发布归档 run。
- 当前环境用项目 `.venv/` 与用户共享 Playwright 缓存；换机器按依赖锁文件、字体准备脚本和环境说明重建。旧 `archive/environments/` 不作为运行依赖。
- `output/` 与 `archive/` 都不随 Git 分发。没有本地产物时按示例源稿重新生成；归档不是仓库运行的前提。
