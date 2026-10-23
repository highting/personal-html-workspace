# 制作 Prompt 入口

日常制作读取本目录保存的共同 Prompt 和所选场景 Prompt，再结合本次用户要求、真实材料与流程说明执行。查看或维护当前规则时，直接打开下列源文件。

| 适用范围 | 存储文件 | 作用 |
|---|---|---|
| 所有场景 | [common.txt](common.txt) | 材料依据、范围、解释、配图、成稿修订和真实验收 |
| 学习 | [scenes/learning.txt](scenes/learning.txt) | 主题内较广覆盖，详细、直白地讲清概念、原因与应用 |
| 博客 | [scenes/blog.txt](scenes/blog.txt) | 聚焦具体知识点，用简明解释与图解讲清原理，不主动扩展 |
| 汇报 | [scenes/report.txt](scenes/report.txt) | 快速突出成果，图表或结论作为重点，全部文案只含实际汇报内容 |
| 小红书 | [scenes/rednote.txt](scenes/rednote.txt) | 小主题、短而连贯的解释、图片正文与发布摘要 |

## 当前制作路线

1. 确定场景，读取 `common.txt`、对应 `scenes/<scene>.txt` 和[视觉规则](../references/visual-system.md)，阅读实际材料。
2. 从 `inputs/<分类>/<主题>/` 或已有 `blogs/<分类>/<主题>/` 运行 `prepare_content.py`，显式指定已知主稿和成品名；当前工作目录建立在 `output/_work/<成品名>/<批次>/`。
3. 在本次 `work/` 完成完整场景稿、内容修订、独立读者视角修订和图文分工；依据共同与场景 Prompt 的完成标准判断能否学懂主题、理解具体原理或快速看懂成果，未达到就继续改稿。
4. 稿件稳定后制作最终图解和页面。学习、博客、汇报用 `build_content.py` 与 `render_content.py`；小红书用 `rednote_render.py` 与 `check_rednote.py`。
5. 完成内容审核和实际呈现验收，通过后用 `publish_content.py` 更新 `output/<成品名>/`，保留旧版并同步总览。

具体参数、页面协议和检查要求见[四场景工作流](../references/content-workflow.md)；材料、目录和版本管理见[工作区约定](../references/workspace.md)。本页只提供读取入口，不另存一套重复的 Prompt 正文。

## 任务快照与历史归档

`prepare_content.py` 从当前项目的 `prompts/common.txt` 和 `prompts/scenes/<scene>.txt` 读取原文，追加主题、场景、辅助图模式与工作稿路径，保存到本次 `work/任务Prompt.txt`。它记录本次准备时采用的规则与路径；用户对话中的要求仍须结合执行。构建器读取的是工作正文，渲染器读取的是当前 HTML，发布器读取的是当前 `run.json` 和验收结果。

`archive/` 用于封存历史工作版本、检查证据和示例。新任务始终从当前 Prompt 与原稿重新准备，不从归档中恢复旧任务路径或调用发布器；确需继承历史工作稿时，在新任务中复制所需稿件并记录来源。查看当前 Prompt 和讲解日常制作流程时，使用本页的源文件链接，不使用历史 `任务Prompt.txt` 作为当前入口。
