# 发布进度

## v1.1.4 小羊开心表情小蹄子修正

2026-10-19 已发布：https://github.com/GiaoHYH/codex-pets/releases/tag/v1.1.4

- `v1.1.3` 开心素材含重复前蹄，已由本版本替换。
- 三张开心表情分别从四肢正确的身体基准生成，只改变脸部；最终循环为亮眼微笑、闭眼大笑的往返动画。
- 每帧固定胸前两只前蹄和下方两只后蹄，没有中央落地前蹄；角色高度统一为 178 px，脚底线为 194 px。
- 旧六连图因重复前蹄淘汰，另一张张嘴候选因尺寸偏小淘汰，均未打包。
- 像素对比确认只更新图集第 8 行；状态映射、桌面和手机预览、13 种表情总览、14 项安装器测试通过。
- 已从公开 Release 下载并核对所有 SHA256SUMS，远程包与构建产物一致，临时安装成功。
- 小羊图集 SHA-256：`6a4bd0284084e217811eb694e0a482b864b6bdbace65e480e5b0255c2c66d26f`。
- 小羊 ZIP SHA-256：`faceb5d3420c38bd4c5dc310d5580d3e20c2b63292a6584d0cca1905ae8b5456`。

## v1.1.3 小羊回复待查看开心表情

2026-10-19 已发布，后由 v1.1.4 替换：https://github.com/GiaoHYH/codex-pets/releases/tag/v1.1.3

- 小羊 `review` 行改为开心动画：合手微笑、亮眼大笑、闭眼笑，再倒序回到起点。
- 等待确认 `waiting` 仍使用抱臂傲娇表情，其他状态和卡皮巴拉素材保持原样。
- 两个抬手候选帧因含额外前蹄被淘汰，没有打包；最终六帧均只有两只前蹄和两只后蹄。
- 图集像素对比确认只更新第 8 行。
- 当前应用状态映射、桌面及手机预览、13 种表情总览和 14 项安装器测试通过。
- 已从公开 Release 下载并核对所有 SHA256SUMS，远程小羊包与构建产物一致，临时安装成功。
- 小羊图集 SHA-256：`fb8acfb7fdb222a0b8e6044c326850b6a4cb73156b36ce2f1763aee1d248fcc6`。
- 小羊 ZIP SHA-256：`bab1bf3ef1293b6c5c1b9a5ffe328041463e39e5413f4880810670c14da935c9`。

## v1.1.2 小羊委屈表情前肢修正

2026-10-19 已发布：https://github.com/GiaoHYH/codex-pets/releases/tag/v1.1.2

- 修正小羊委屈动作全部五帧：胸前两只前蹄、下方两只后蹄，中间为连续的圆肚子。
- 像素对比确认只更新小羊图集第 4 行，其他状态及卡皮巴拉素材保持原样。
- 本机已安装同一图集，表情总览和动画预览已更新。
- 五帧放大视觉检查、桌面及手机预览检查、14 项安装器测试通过。
- 从公开 Release 下载的安装器、目录、宠物包与 SHA256SUMS 全部校验通过。
- 小羊图集 SHA-256：`75ae37ced695c19e6538070af85a6eef9377718bd6e3b5f533a8aed4e6c2f8de`。
- 小羊 ZIP SHA-256：`c5b2596081c2dcdcfaf72f5dda2a2fbe459762af62a83b7dec80f498dba47c1f`。

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
