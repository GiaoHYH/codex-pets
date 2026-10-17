#!/usr/bin/env python3
"""Download, validate, install and select a Codex desktop pet. Python 3.9+."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import ssl
import stat
import struct
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
import uuid
import zipfile

DEFAULT_BASE_URL = ""  # Populated when creating release assets.
MAX_DOWNLOAD = 24 * 1024 * 1024
MAX_FILE = 20 * 1024 * 1024
PET_ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")


def fail(message):
    raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def https_url(url):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        fail("下载地址必须是 HTTPS，且不能包含用户名或密码。")
    return url


def download(url, limit=MAX_DOWNLOAD):
    request = Request(https_url(url), headers={"User-Agent": "codex-pet-switcher/1.0"})
    with urlopen(request, timeout=30, context=ssl.create_default_context()) as response:
        https_url(response.geturl())
        data = response.read(limit + 1)
    if len(data) > limit:
        fail("下载文件超过大小限制。")
    return data


def image_info(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR" and len(data) >= 26:
        width, height = struct.unpack(">II", data[16:24])
        return width, height, data[25] in (4, 6)
    if len(data) >= 20 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        offset = 12
        while offset + 8 <= len(data):
            kind = data[offset:offset + 4]
            length = int.from_bytes(data[offset + 4:offset + 8], "little")
            chunk = data[offset + 8:offset + 8 + length]
            if len(chunk) != length:
                break
            if kind == b"VP8X" and length >= 10:
                return (int.from_bytes(chunk[4:7], "little") + 1,
                        int.from_bytes(chunk[7:10], "little") + 1, bool(chunk[0] & 0x10))
            if kind == b"VP8L" and length >= 5 and chunk[0] == 0x2F:
                bits = int.from_bytes(chunk[1:5], "little")
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1, bool(bits & (1 << 28))
            offset += 8 + length + length % 2
    fail("宠物图集不是受支持的透明 PNG/WebP。")


def validate_package(data, expected_sha=None, expected_id=None):
    if len(data) > MAX_DOWNLOAD:
        fail("宠物包超过大小限制。")
    if expected_sha is not None and digest(data) != expected_sha:
        fail("宠物包 SHA-256 校验失败，未安装。")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)) or len(names) != 3:
            fail("宠物包必须恰好包含三个不同文件。")
        if not {"bundle.json", "pet.json"}.issubset(names):
            fail("宠物包缺少元数据。")
        for entry in entries:
            mode = entry.external_attr >> 16
            if (entry.filename not in {"bundle.json", "pet.json", "spritesheet.webp", "spritesheet.png"}
                    or entry.file_size > MAX_FILE or entry.is_dir()
                    or stat.S_ISLNK(mode) or entry.flag_bits & 1):
                fail("宠物包包含无效文件、路径或符号链接。")
        files = {name: archive.read(name) for name in names}
    bundle = json.loads(files["bundle.json"])
    manifest = json.loads(files["pet.json"])
    pet_id = bundle.get("id", "")
    if not isinstance(pet_id, str) or not PET_ID.fullmatch(pet_id):
        fail("宠物 ID 无效。")
    if expected_id is not None and pet_id != expected_id:
        fail("下载的宠物 ID 与所选宠物不一致。")
    if bundle.get("formatVersion") != 1 or manifest.get("id") != pet_id:
        fail("宠物包元数据不一致。")
    sprite = manifest.get("spritesheetPath")
    if sprite not in {"spritesheet.webp", "spritesheet.png"} or sprite not in files:
        fail("图集路径无效。")
    required_hashes = {"pet.json", sprite}
    hashes = bundle.get("sha256", {})
    if not isinstance(hashes, dict) or set(hashes) != required_hashes:
        fail("文件校验清单不完整。")
    if any(hashes[name] != digest(files[name]) for name in required_hashes):
        fail("宠物包内的文件校验失败。")
    version = manifest.get("spriteVersionNumber")
    if version not in (1, 2):
        fail("不支持的动画版本。")
    width, height, alpha = image_info(files[sprite])
    if (width, height) != (1536, 1872 if version == 1 else 2288) or not alpha:
        fail("图集尺寸或透明通道不符合宠物格式。")
    return pet_id, manifest, {name: files[name] for name in required_hashes}


def selection(text):
    section = re.search(r"(?ms)^\[desktop\][ \t]*\n(.*?)(?=^\[|\Z)", text)
    if not section:
        return None
    match = re.search(r'(?m)^[ \t]*selected-avatar-id[ \t]*=[ \t]*"([^"\n]*)"', section.group(1))
    return match.group(1) if match else None


def with_selection(text, value):
    section = re.search(r"(?ms)^\[desktop\][ \t]*\n(.*?)(?=^\[|\Z)", text)
    line = "selected-avatar-id = " + json.dumps(value) if value is not None else None
    if not section:
        return text.rstrip() + "\n\n[desktop]\n" + line + "\n" if line else text
    content = section.group(1)
    pattern = r"(?m)^[ \t]*selected-avatar-id[ \t]*=.*(?:\n|$)"
    if re.search(pattern, content):
        content = re.sub(pattern, (line + "\n") if line else "", content, count=1)
    elif line:
        content = content.rstrip() + "\n" + line + "\n\n"
    return text[:section.start(1)] + content + text[section.end(1):]


def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pet-switch-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        if path.exists():
            os.chmod(temporary, stat.S_IMODE(path.stat().st_mode))
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def config_text(home):
    path = home / "config.toml"
    if path.is_symlink():
        fail("config.toml 是符号链接，请先手动确认配置位置。")
    return path, path.read_text(encoding="utf-8") if path.exists() else ""


def install(data, home, expected_sha=None, expected_id=None, select=True):
    pet_id, manifest, files = validate_package(data, expected_sha, expected_id)
    home = home.expanduser().absolute()
    pets = home / "pets"
    pets.mkdir(parents=True, exist_ok=True)
    destination = pets / pet_id
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        fail("宠物目标位置不是普通目录。")
    config, old_config = config_text(home)
    next_config = with_selection(old_config, "custom:" + pet_id) if select else old_config
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    backup = home / "pet-backups" / pet_id / timestamp
    backup.mkdir(parents=True)
    receipt = {"petId": pet_id, "previousSelection": selection(old_config),
               "hadPreviousPet": destination.exists(), "selected": select,
               "packageSha256": digest(data)}
    atomic_text(backup / "receipt.json", json.dumps(receipt, indent=2) + "\n")
    atomic_text(backup / "config-before.toml", old_config)
    stage = Path(tempfile.mkdtemp(prefix=".install-", dir=str(pets)))
    moved_old = False
    installed = False
    try:
        for name, content in files.items():
            (stage / name).write_bytes(content)
        # Avoid overwriting a configuration edit made while the package was staged.
        if config_text(home)[1] != old_config:
            fail("配置在安装过程中被修改，请重试。")
        if destination.exists():
            os.replace(destination, backup / "pet")
            moved_old = True
        os.replace(stage, destination)
        installed = True
        if select:
            atomic_text(config, next_config)
    except Exception:
        if installed:
            shutil.rmtree(destination)
        if moved_old:
            os.replace(backup / "pet", destination)
        raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return pet_id, manifest.get("displayName", pet_id), backup


def restore(home, pet_id):
    if not PET_ID.fullmatch(pet_id):
        fail("宠物 ID 无效。")
    root = home / "pet-backups" / pet_id
    candidates = sorted(root.glob("*/receipt.json"), reverse=True) if root.exists() else []
    candidates = [path for path in candidates if not (path.parent / "restored").exists()]
    if not candidates:
        fail("没有可恢复的备份。")
    backup = candidates[0].parent
    receipt = json.loads(candidates[0].read_text())
    destination = home / "pets" / pet_id
    if destination.is_symlink():
        fail("宠物目标是符号链接，无法恢复。")
    if receipt["hadPreviousPet"] and not (backup / "pet").is_dir():
        fail("备份文件不完整。")
    config, old_config = config_text(home)
    next_config = with_selection(old_config, receipt["previousSelection"]) if receipt["selected"] else old_config
    holding = backup / "replaced-pet"
    moved = False
    restored = False
    try:
        if destination.exists():
            os.replace(destination, holding)
            moved = True
        if receipt["hadPreviousPet"]:
            os.replace(backup / "pet", destination)
            restored = True
        if receipt["selected"]:
            atomic_text(config, next_config)
        (backup / "restored").touch()
    except Exception:
        if restored:
            os.replace(destination, backup / "pet")
        if moved:
            os.replace(holding, destination)
        raise
    return backup


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pet", default="capybara-chibi", help="宠物 ID")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="GitHub Release 资源根地址")
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home()/".codex"))))
    parser.add_argument("--list", action="store_true", help="列出 Release 中的宠物")
    parser.add_argument("--restore", action="store_true", help="恢复上一次安装前的宠物和选择")
    parser.add_argument("--no-select", action="store_true", help="只安装，不更改默认选择")
    parser.add_argument("--package", type=Path, help="离线安装 ZIP 文件")
    parser.add_argument("--sha256", help="离线包的 SHA-256，可选")
    args = parser.parse_args(argv)
    try:
        if args.restore:
            backup = restore(args.codex_home.expanduser().absolute(), args.pet)
            print("已恢复：" + args.pet + "（备份 " + str(backup) + "）")
            return 0
        if args.package:
            data = args.package.read_bytes()
            expected = args.sha256
        else:
            if not args.base_url:
                fail("尚未配置 Release 地址，请使用 --base-url。")
            base = https_url(args.base_url.rstrip("/") + "/")
            catalog = json.loads(download(urljoin(base, "pets.json"), 1024*1024))
            if catalog.get("formatVersion") != 1 or not isinstance(catalog.get("pets"), list):
                fail("远程宠物目录格式无效。")
            if args.list:
                for item in catalog["pets"]:
                    print(item["id"] + "\t" + item["displayName"])
                return 0
            item = next((item for item in catalog["pets"] if item.get("id") == args.pet), None)
            if item is None:
                fail("该 Release 没有宠物 " + args.pet + "；可先运行 --list。")
            filename = item.get("asset", "")
            expected = item.get("sha256", "")
            if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*\.zip", filename) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                fail("远程资源名或校验值无效。")
            data = download(urljoin(base, filename))
        pet_id, name, backup = install(data, args.codex_home, expected, args.pet, not args.no_select)
        print("已安装：" + name + "（" + pet_id + "）")
        print("备份位置：" + str(backup))
        if not args.no_select:
            print("已保存默认选择。如当前界面未更新，在设置 → 宠物中刷新并重新选择，或重启应用。")
        return 0
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print("更换失败：" + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
