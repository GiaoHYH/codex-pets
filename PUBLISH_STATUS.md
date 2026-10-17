# 发布进度

已完成，时间：2026-10-17（Asia/Shanghai）。

发布仓库：
https://github.com/GiaoHYH/codex-pets

Release：
https://github.com/GiaoHYH/codex-pets/releases/tag/v1.0.0

一行安装命令：

```sh
(set -e; pet_installer=$(mktemp); trap 'rm -f "$pet_installer"' EXIT; curl -fsSL 'https://github.com/GiaoHYH/codex-pets/releases/download/v1.0.0/install.py' -o "$pet_installer"; python3 "$pet_installer" --pet capybara-chibi)
```

已发布资源：
- `install.py`
- `pets.json`
- `capybara-chibi.zip`
- `SHA256SUMS`

校验结果：
- 11 项安装器测试通过。
- 已从 GitHub Release 真实下载并安装到临时 `CODEX_HOME`。
- 已验证默认选择写入 `desktop.selected-avatar-id = "custom:capybara-chibi"`。
- 已验证恢复功能。
- 最终图集 SHA-256：`57ea1fcc08d7219aa51f59cd440228204e8f18d44ce90a9cecb72a3f066afabc`。
- ZIP SHA-256：`fbf6343741f27018210d43eac142f0c2a9408947b553582c81c615c72fe56a6f`。

仅 `packages/capybara-chibi` 中的宠物文件被打包发布；工作区其他内容没有上传。
