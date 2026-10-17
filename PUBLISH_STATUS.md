# 发布进度

## v1.1.1 卡皮巴拉正面左右扭胯修正

2026-10-17 已发布：https://github.com/GiaoHYH/codex-pets/releases/tag/v1.1.1

- 修正 `capybara-chibi` 的 `jumping` 行：动作改为正面左右扭胯，不再转身背对。
- 保留 `sheep-chibi` 发布包和安装命令。
- 14 项安装器测试通过。
- 已从公开 Release 真实下载安装器并安装 `capybara-chibi` 到临时 `CODEX_HOME`。
- 已验证默认选择写入 `desktop.selected-avatar-id = "custom:capybara-chibi"`。
- 本机当前安装图集已同步为同一版本。
- 卡皮巴拉图集 SHA-256：`d5bf50724d09becc22c139ca7f954086cd6bf701f5541ca59d2c2575c11e767f`。
- 卡皮巴拉 ZIP SHA-256：`b2f82a82f1225fc562cc85c45866d58c6c4867144a39ca583cc1ccd00971703f`。

卡皮巴拉一行安装命令：

```sh
(set -e; pet_installer=$(mktemp); trap 'rm -f "$pet_installer"' EXIT; curl --proto '=https' --tlsv1.2 -fsSL 'https://github.com/GiaoHYH/codex-pets/releases/download/v1.1.1/install.py' -o "$pet_installer"; python3 "$pet_installer" --pet capybara-chibi)
```

## v1.1.0 卷卷小羊

2026-10-17 已发布：https://github.com/GiaoHYH/codex-pets/releases/tag/v1.1.0

- 新增 `sheep-chibi.zip`，等待确认和回复未读均使用傲娇表情；悬停替换为坐着委屈地望着你。
- 14 项安装器测试通过，包含小羊离线 ID 推断和更新恢复。
- 已从公开 Release 下载安装器、目录、ZIP 与 SHA256SUMS，全部校验通过。
- 已使用远程安装器在临时目录实际下载、安装、核对默认选择和图集，并成功恢复。
- ZIP SHA-256：`4e240eab39e4a7497b77458f3fa0b51e2e327cd3c60c32b0283c1da02ce9dfbe`。
- 桌面与手机尺寸预览、所有九组动作、等待后回到日常、回复未读和悬停映射检查通过。
- 应用的约 3 秒表情时长、已读后进入日常和悬停优先规则仍由应用控制，资源包不修改应用程序。

一行命令见 README.md，或构建输出 `dist/INSTALL_COMMAND-sheep-chibi.txt`。

## v1.0.0 卡皮巴拉

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
