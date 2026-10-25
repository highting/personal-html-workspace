# 第三方资源

## Noto Sans SC

新增学习、博客和汇报HTML的中文字体来自[Google Fonts官方固定提交](https://github.com/google/fonts/tree/a85815a42757630ce188fdad368c2dfc444d4773/ofl/notosanssc)。完整字体按需缓存且不入Git，构建器将实际字形子集与OFL许可内嵌成品。版本、SHA-256及来源见[字体说明](../assets/vendor/noto-sans-sc/README.md)，原许可见[OFL.txt](../assets/vendor/noto-sans-sc/OFL.txt)。不改变原小红书字体。

## 汇报字体与图标

汇报正文的英文字母、数字和斜体内嵌 Quarto 演示实际加载的 Source Sans Pro 1.050；目录、关闭与翻页图标使用同页的 Font Awesome Free 5.1 字体。文件按原字节保存，不加载外部字体服务或图标脚本；仅汇报使用，中文与混排标题仍采用上述 Noto Sans SC 子集。来源、哈希与原许可分别见[Source Sans Pro](../assets/vendor/source-sans-pro/README.md)和[Font Awesome](../assets/vendor/font-awesome/README.md)，完整 OFL 文本随成品内嵌。

## KaTeX

- 版本：0.16.11。
- 上游：[KaTeX](https://katex.org/)，npm 包 `katex@0.16.11`。
- 获取地址：`https://registry.npmmirror.com/katex/-/katex-0.16.11.tgz`。
- 上游包完整性：`sha512-RQrI8rlHY92OLf3rho/Ts8i/XvjgguEjOkO1BEXcU3N8BqPpSzBNwV/G0Ukr+P/l3ivvJUE/Fa/CwbS6HesGNQ==`。
- 仓库仅保留发行包的 `katex.min.js`、`katex.min.css`、`contrib/auto-render.min.js`、字体和原始 MIT 许可；位置为 `assets/vendor/katex`。
- 版权及完整许可见 [LICENSE](../assets/vendor/katex/LICENSE)。

## MiSans

普通主题使用 MiSans 字体。[官方来源与许可](https://hyperos.mi.com/font/zh/download/)。字体安装在操作系统用户环境，不随本仓库分发；代码和公式分别使用等宽字体与 KaTeX 数学字体。
