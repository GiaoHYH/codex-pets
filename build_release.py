#!/usr/bin/env python3
"""Create self-contained, checksummed GitHub Release assets from local pets."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pet_installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def build(repo=None, tag="v1.0.0", output=None):
    if repo and not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("仓库格式必须为 owner/repo。")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", tag):
        raise ValueError("Release 标签格式无效。")
    output = Path(output or ROOT / "dist")
    output.mkdir(parents=True, exist_ok=True)
    base = "https://github.com/" + repo + "/releases/download/" + tag if repo else ""
    source = (ROOT / "install.py").read_text()
    source = source.replace('DEFAULT_BASE_URL = ""', "DEFAULT_BASE_URL = " + json.dumps(base), 1)
    (output / "install.py").write_text(source)
    catalog = {"formatVersion": 1, "version": tag, "pets": []}
    for directory in sorted((ROOT / "packages").iterdir()):
        if not directory.is_dir():
            continue
        manifest_data = (directory / "pet.json").read_bytes()
        manifest = json.loads(manifest_data)
        pet_id = manifest["id"]
        if not installer.PET_ID.fullmatch(pet_id) or pet_id != directory.name:
            raise ValueError("目录和宠物 ID 不一致：" + directory.name)
        sprite = manifest["spritesheetPath"]
        if sprite not in {"spritesheet.png", "spritesheet.webp"}:
            raise ValueError("图集文件名无效。")
        files = {"pet.json": manifest_data, sprite: (directory / sprite).read_bytes()}
        bundle = {"formatVersion": 1, "id": pet_id, "version": tag,
                  "sha256": {name: sha256(data) for name, data in files.items()}}
        files["bundle.json"] = (json.dumps(bundle, ensure_ascii=False, indent=2) + "\n").encode()
        asset = pet_id + ".zip"
        with zipfile.ZipFile(output / asset, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(files):
                entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, files[name])
        data = (output / asset).read_bytes()
        installer.validate_package(data, expected_id=pet_id)
        catalog["pets"].append({"id": pet_id, "displayName": manifest["displayName"],
                                "description": manifest.get("description", ""),
                                "asset": asset, "sha256": sha256(data), "bytes": len(data)})
    (output / "pets.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    assets = [output / "install.py", output / "pets.json"] + [output / p["asset"] for p in catalog["pets"]]
    (output / "SHA256SUMS").write_text("".join(sha256(path.read_bytes()) + "  " + path.name + "\n" for path in assets))
    command = ""
    commands = {}
    if base:
        for pet in catalog["pets"]:
            commands[pet["id"]] = "(set -e; pet_installer=$(mktemp); trap 'rm -f \"$pet_installer\"' EXIT; curl --proto '=https' --tlsv1.2 -fsSL '" + base + "/install.py' -o \"$pet_installer\"; python3 \"$pet_installer\" --pet " + pet["id"] + ")"
            (output / ("INSTALL_COMMAND-" + pet["id"] + ".txt")).write_text(commands[pet["id"]] + "\n")
        command = commands.get("sheep-chibi") or next(iter(commands.values()), "")
    notes = """卷卷小羊与宠物快捷更换工具。

v1.1.2 修正小羊委屈动作的重复前肢：所有帧均只有胸前两只前蹄和下方两只后蹄，中间为连续的圆肚子。其他状态与卡皮巴拉素材保持原样。

新增奶白卷毛小羊女生：等待确认和回复未读状态显示抱臂傲娇脸；原跳跃动作改成坐着委屈地望着你。保留卡皮巴拉安装选项，卡皮巴拉的原跳跃动作是正面左右扭胯，不转身。

应用限制：正式选择/确认触发 waiting，普通文字回复未读触发 review，已读后是 idle。当前桌面应用等待动画约 3 秒后回到日常，悬停会覆盖为原 jumping 状态（现为委屈表情）。宠物包无法修改应用的状态识别和播放时长。

安装器会校验 ZIP 和图集、保留旧宠物备份，并保存默认选择。支持按包内 ID 离线安装。需要 Python 3.9 或更新版本。如果应用缓存旧图集，重新选择宠物或重启应用。
"""
    for pet in catalog["pets"]:
        if pet["id"] in commands:
            notes += "\n" + pet["displayName"] + "：\n\n```sh\n" + commands[pet["id"]] + "\n```\n"
    (output / "RELEASE.md").write_text(notes)
    if command:
        (output / "INSTALL_COMMAND.txt").write_text(command + "\n")
    return catalog


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="GitHub owner/repo")
    parser.add_argument("--tag", default="v1.0.0")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.repo, args.tag, args.output), ensure_ascii=False, indent=2))
