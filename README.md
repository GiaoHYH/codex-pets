# 宠物快捷更换

从 GitHub Releases 下载宠物包，校验后安装，并保存为 Codex/ChatGPT 桌面应用的默认宠物。当前内置 `capybara-chibi`：Q 版卡皮巴拉，原跳跃动作已改成扭屁股。

## 一行远程安装

构建脚本会生成带真实仓库地址的 `dist/INSTALL_COMMAND.txt`。命令下载临时安装器，安装完成后清理临时文件。安装器内的资源地址固定到同一个 Release 标签。

当前发布仓库的一行安装命令：

```sh
(set -e; pet_installer=$(mktemp); trap 'rm -f "$pet_installer"' EXIT; curl -fsSL 'https://github.com/GiaoHYH/codex-pets/releases/download/v1.0.0/install.py' -o "$pet_installer"; python3 "$pet_installer" --pet capybara-chibi)
```

需要 Python 3.9+ 和 curl。安装器只使用 Python 标准库，不依赖 Pillow。默认安装到 `$CODEX_HOME/pets/`，未设置 CODEX_HOME 时使用 `~/.codex/pets/`。

发布为公开仓库时，下载安装不需要 GitHub 登录。命令会执行 Release 中的安装器，应从你信任的仓库运行。

## 其他操作

安装器下载到本地后，同一工具支持：

```sh
python3 install.py --list                      # 列出该 Release 的宠物
python3 install.py --pet capybara-chibi         # 下载、安装并选中
python3 install.py --pet capybara-chibi --restore  # 恢复上一次更换前的状态
python3 install.py --pet capybara-chibi --no-select # 只安装
python3 install.py --package dist/capybara-chibi.zip # 离线安装
```

自定义远程地址用 `--base-url https://.../releases/download/标签`。测试或便携目录用 `--codex-home /指定目录`。

更换过程先验证包 SHA-256、内部文件校验、图集尺寸和透明通道，再安装。ZIP 只允许固定的三个文件，不解压任意路径。旧宠物和上次选择保存在 `~/.codex/pet-backups/<宠物ID>/<时间>/`；安装写入失败会回滚。恢复时只还原宠物选择，保留其他配置变化。

应用如果缓存了旧形象，需要在“设置 → 宠物”中刷新并重新选择，或重新启动应用。安装器只更新本地资源和默认选择，不强制关闭应用。

## 构建与发布

```sh
python3 -m unittest discover -s tests -v
python3 build_release.py --repo GiaoHYH/codex-pets --tag v1.0.0
gh release create v1.0.0 dist/install.py dist/pets.json dist/capybara-chibi.zip dist/SHA256SUMS --repo GiaoHYH/codex-pets --title 'Q 版卡皮巴拉与宠物快捷更换' --notes-file dist/RELEASE.md
```

新增宠物时，将合法的 `pet.json` 和对应 `spritesheet.webp` 或 `spritesheet.png` 放入 `packages/<宠物ID>/`，重新构建即可。只发布 `dist/` 的指定资源，不上传工作区中的其他文件或配置备份。
