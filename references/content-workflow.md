# 四场景工作流

以原 `main` 的小红书实现为基础，四场景按用途分路。新流程不替换 `rednote_render.py` 或原主题；学习/博客/汇报使用新增静态模板。先读根技能和[场景规则](content-scenes.md)。

## 准备材料

材料放 `inputs/<分类>/<主题>/` 或原 `blogs/`，保留附件相对路径；原稿只读。优先识别 `main.md`、`article.md`、`index.md`，其他格式按实际内容用对应工具读取，转换稿放 `work/`。

```bash
python -X utf8 scripts/prepare_content.py "inputs/机器学习/Softmax" --scene learning --name Softmax-学习
```

`--entry` 可指定相对主稿路径，`--mode html|images` 仅记录辅助图工具。脚本建立 `output/_work/<短名>/<时间戳>-<scene>-<mode>/` 的 `source/`、`work/`、`delivery/`，输出 `run.json` 与 `work/任务Prompt.txt`。同主题并存多个场景时用不同短名，新请求新建工作目录，同次修正复用。`source/` 是只读快照；其哈希用于交付核对。

读取 `prompts/common.txt` 和所选 `prompts/scenes/<scene>.txt`，按实际读者、目标、范围与材料策划；只读取所选场景。AI整理连续正文或汇报分页，不把原稿未经策划直接转换当作已完成。

## 学习与博客

在 `work/` 写好的 Markdown 支持 YAML 的 `title`、`description`、`author`、`date`；后两者只采用真实信息。标题可从第一个一级标题获取。h2章节、h3小节形成目录；内嵌SVG与本地图片可作图解，公式行内用 `\( ... \)`，独立用 `$$ ... $$`。

```bash
python -X utf8 scripts/build_content.py "<work_entry>" --scene learning --output "<run_dir>/work/index.html"
python -X utf8 scripts/render_content.py "<run_dir>/work/index.html" --scene learning --output-dir "<artifact_dir>"
```

博客将两处scene改为 `blog`。构建器可接收可信 `.html` 正文片段，直接放入 `.prose`；不是完整网页或未整理的Prompt。`--theme light|dark|system` 设置初始偏好，默认浅色，太阳/月亮按钮保存用户选择。桌面目录可完整收起，紧凑窗口用同一按钮开合目录。CSS/JS、KaTeX和数学字体内嵌，本地 `<img src>` 转为data URI；网络图片拒绝，需先本地化。

首次构建前显式执行 `python -X utf8 scripts/download_content_fonts.py`，下载并校验固定版本Noto Sans SC（思源黑体系列）缓存。构建器用FontTools/Brotli按实际字符制作WOFF2子集，中文正文、标题、SVG、代码中文和备注可离线显示；字体及OFL许可内嵌成品，完整缓存不入Git。来源见[字体说明](../assets/vendor/noto-sans-sc/README.md)。仍需核对实际中文字形与字体，而不只看CSS声明。

不引入React/Next/Astro后台；正文片段可按内容调整排版，模板不是固定图数或章节数的约束。来源链接允许联网跳转，但阅读不依赖联网。不要在成品追加制作记录或机器检查表。

## 技术汇报

Markdown围栏外的独立 `---` 作为分页符，代码和公式保持完整；每页标题用 `#` 或 `##`。`<!-- notes: 备注正文 -->` 保存口头说明。复杂内容可写可信HTML片段，完整页面遵循以下结构：

```html
<section class="slide" data-export-page data-notes="讲者备注">
  <p class="eyebrow">汇报主题</p>
  <div class="slide-body"><h2>本页主张</h2><p>证据与必要条件</p></div>
  <footer class="slide-footer"><span>主题或来源</span><span>01 / 04</span></footer>
</section>
```

同一HTML片段可包含多页；必须使用上述class和标记，正文在 `slide-body` 安全区内。使用 `.columns` 两栏、`.metric` 强调必要数值；数值只能来自真实材料或标注教学构造。固定页放不下就调整或增页。

```bash
python -X utf8 scripts/build_content.py "<work_entry>" --scene report --output "<run_dir>/work/index.html"
python -X utf8 scripts/render_content.py "<run_dir>/work/index.html" --scene report --output-dir "<artifact_dir>" --theme light
```

`render_content.py` 使用模板的 `setContentTheme` 和 `activateContentExport({index})`，验证主题切换、键盘翻页、备注和每页边界；不猜测其他演示框架接口。自定义HTML需保留模板约定。`--browser-executable` 可指定已有Chromium，默认复用Playwright共享缓存。

## 检查与汇总

检查器离线加载HTML，输出 `qa.json`、`preview-light.png`、`preview-dark.png` 与 `checks/` 的章节/逐页检查截图；汇报另交所选主题 `page-01.png` 等。实际查看所有主要图文区域及汇报全部页，测试目录直达、主题切换与备注。QA只处理可测问题，不证明内容或审美已通过。

记录来源、主线、图解、实际检查与未验证事项到 `delivery.md`，全部完成后才将 `run.json` 的 `status` 改为 `completed`。

```bash
python -X utf8 scripts/publish_content.py "<run_dir>"
```

学习/博客/汇报要求本场景QA通过，核对HTML与导出PNG哈希以及未修改的源快照。HTML/PNG修改后重新检查，不能手改通过结果。短路径更新到 `output/<短名>/`，旧交付保留在本次工作目录；回复优先链接 `index.html` 与所选场景成品。

## 小红书原流程

已有 `blogs/` 继续按[原工作区](workspace.md)使用 `prepare_blog.py` → `rednote_render.py` → `publish_blog.py`，制作规则见[小红书场景](rednote-scene.md)。新 `inputs/` 可用 `prepare_content.py --scene rednote` 准备，同一原渲染器输出到 `artifact_dir`，实际查看PNG及文案并标记completed后，`publish_content.py`转交原发布函数。小红书不使用新长文模板，不要求新 `qa.json` 来替代原逐张检查。

这里的“发布”只指本地成品汇总。脚本不调用AI或生图、不上传社交平台；插件安装与GitHub上传是独立操作。
