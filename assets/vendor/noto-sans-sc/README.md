# Noto Sans SC

新增学习、博客与汇报模板使用Noto Sans SC（思源黑体系列）可变字体，字重100–900。固定版本与SHA-256见 `font-manifest.json`；[官方源文件](https://github.com/google/fonts/tree/a85815a42757630ce188fdad368c2dfc444d4773/ofl/notosanssc)，许可见 `OFL.txt`。

首次显式执行 `python -X utf8 scripts/download_content_fonts.py`，下载约17MB的可复现本地缓存。缓存TTF被Git忽略。`build_content.py` 用FontTools按本篇实际字符生成WOFF2子集，并将子集及许可内嵌到单文件HTML，离线打开无需字体服务器或操作系统安装。

只用于新长文与汇报，原小红书渲染器与字体不变。字体包存在不等于实际使用，需核对中文正文、标题、SVG标签和代码中文；数学主要字形仍使用KaTeX字体。
