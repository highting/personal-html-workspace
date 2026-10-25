# 环境安装与验证

换电脑的完整安装顺序见 [README](../README.md#换电脑使用)。本项目已有 Windows x64 / Python 3.13.14 的浏览器验证记录；当前项目 `.venv` 使用 Python 3.12.14，包版本与 `requirements.lock.txt` 一致。macOS/Linux 尚未逐平台验证，不承诺跨系统像素完全相同。Python 包装入本项目 `.venv`，浏览器版本由 Playwright 管理并使用用户共享缓存，两者均不纳入 Git。

## Python 包

先按 README 建立虚拟环境。本文 `python` 指该环境的解释器：Windows 为 `.\.venv\Scripts\python.exe`，macOS/Linux 为 `.venv/bin/python`；不激活时直接替换命令中的 `python`。在项目根目录执行：

```powershell
python -m pip install -r requirements.lock.txt
python -m pip check
```

大陆网络可为安装命令增加 `-i https://mirrors.cloud.tencent.com/pypi/simple`，该镜像曾在本机完成安装。也可改用 `https://pypi.tuna.tsinghua.edu.cn/simple` 或 `https://mirrors.aliyun.com/pypi/simple`；镜像缺包或持续失败时使用官方 `https://pypi.org/simple`。使用单次命令的 `-i`，不修改其他项目的全局源配置。

虚拟环境中不使用 `--user`。使用 `python -m pip` 与 `python -m playwright`，确保安装与运行使用同一解释器。`requirements.lock.txt` 用于固定版本复现；`requirements.txt` 是兼容范围，升级依赖时使用，不作为默认换机安装入口。

## 无头浏览器

HTML 检查和 PNG 渲染需要 Chromium Headless Shell：

```bash
python -m playwright install chromium-headless-shell
```

Linux 缺少系统库时运行 `python -m playwright install-deps chromium`（可能需要管理员权限）。浏览器缓存由 Playwright 按系统管理，不能从另一台电脑直接复制使用；升级 Playwright 后重新安装对应浏览器。

下载慢时，PowerShell 可为本次进程设置 npmmirror：

```powershell
$env:PLAYWRIGHT_DOWNLOAD_HOST = 'https://npmmirror.com/mirrors/playwright'
$env:PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT = '120000'
python -m playwright install chromium-headless-shell
```

若下载实际持续超时，先等安装器退出。然后在新开的 PowerShell 窗口执行官方回退命令，使前面的进程级镜像设置不再生效：

```powershell
python -m playwright install chromium-headless-shell
```

本机曾遇到 npmmirror 文件 HEAD 可达但下载超时，最终从官方源完成 Headless Shell、FFmpeg 和 Winldd 的安装。Windows 默认缓存位于 `%LOCALAPPDATA%\ms-playwright`，无需加入仓库。升级 Playwright 后应重新执行浏览器安装命令。

如果中断安装后出现 `__dirlock`，先查看进程的命令行和父子关系。只有确认本次安装的残留进程已退出，才可删除确切的锁目录；不要在另一安装器仍运行时清锁或并发重装。

## 字体与公式

学习、博客、汇报在首次构建前执行：

```bash
python -X utf8 scripts/download_content_fonts.py
```

脚本从固定版本的 Google Fonts GitHub 地址下载约 17 MB 的 Noto Sans SC，按仓库中的 `font-manifest.json` 校验大小和 SHA-256；已有正确缓存时不重复下载。字体 TTF 被 Git 忽略，下载失败时构建会提示缺少缓存。受限网络下可在能访问该地址的机器下载同一文件，复制到 `assets/vendor/noto-sans-sc/NotoSansSC-variable.ttf` 后再运行下载脚本核验。成品内嵌实际字符的 WOFF2 子集及许可，不要求读者安装系统字体。

以下系统字体要求只用于原小红书主题，不影响上述三类 HTML：

普通主题使用 **MiSans 字体**，从[小米官方下载页](https://hyperos.mi.com/font/zh/download/)获取，解压后安装 `MiSans/ttf` 中需要的字重。在 Windows 中选择“安装”可安装到当前用户；重新启动渲染进程即可使用。字体应按下载页的许可使用，本仓库不分发 MiSans 字体文件。

本机已安装官方包的十个静态字重；普通主题曾通过 Chromium `CSS.getPlatformFontsForNode` 验证正文使用 `MiSans`、代码使用 `Consolas`。`academic` 的HTML封面和正文由主题CSS统一使用 `Microsoft YaHei`。生图辅助图按既有prompt使用宋体／serif。字体是否生效应检查实际渲染，不因参考截图使用某种字体就改变当前设置。

另一台机器缺少上述字体时，浏览器会使用系统可用的后备字体，中文外观和分页可能变化。需要保持小红书效果时，自行按许可准备相同字体并重新查看全部卡片；仓库不分发微软雅黑、Consolas 或 MiSans。不要仅凭 CSS 字体列表认定与原机器相同。

KaTeX 0.16.11 的 JS、CSS、字体已内置在 `assets/vendor/katex`。无需 Node.js 或 npm 即可渲染公式；资源来源及许可见 [third-party.md](third-party.md)。

## 验证与示例

```powershell
python -X utf8 -m unittest discover -s tests -v
python -X utf8 scripts/rednote_render.py demos/academic.md -t academic -o archive/demo-renders/geometry
python -X utf8 scripts/rednote_render.py demos/academic-comparison.md -t academic -o archive/demo-renders/comparison
```

测试包含真实浏览器输出、离线公式、根号可见性、画布越界、非法公式及分页内容保留；缺少依赖或浏览器会失败，应先完成安装。PNG 仍需目视核对几何、标签位置和遮挡。

`check_chrome_zoom.py` 是额外的桌面 Chrome 原生缩放检查，需要自行安装完整 Chrome 并通过 `--browser-executable` 指定本机路径；Headless Shell 不含 Chrome 设置界面。它不是基本构建的前提，原生缩放按实际浏览器条件检查并记录，不能将默认检查器的 CSS 缩放记作原生缩放。
