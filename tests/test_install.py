import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def bundle(extra=None, wrong_sprite_hash=False, pet_id="capybara-chibi"):
    manifest = (ROOT / "packages" / pet_id / "pet.json").read_bytes()
    sprite_name = json.loads(manifest)["spritesheetPath"]
    sprite = (ROOT / "packages" / pet_id / sprite_name).read_bytes()
    hashes = {"pet.json": installer.digest(manifest), sprite_name: installer.digest(sprite)}
    if wrong_sprite_hash:
        hashes[sprite_name] = "0" * 64
    meta = {"formatVersion": 1, "id": pet_id, "sha256": hashes}
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("pet.json", manifest)
        archive.writestr(sprite_name, sprite)
        archive.writestr("bundle.json", json.dumps(meta))
        if extra:
            archive.writestr(extra, "untrusted")
    return out.getvalue()


class InstallTests(unittest.TestCase):
    def test_sheep_offline_infers_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "sheep.zip"
            package.write_bytes(bundle(pet_id="sheep-chibi"))
            home = Path(temp) / "home"
            self.assertEqual(installer.main(["--package", str(package), "--codex-home", str(home)]), 0)
            self.assertEqual(installer.selection((home / "config.toml").read_text()), "custom:sheep-chibi")
            self.assertTrue((home / "pets/sheep-chibi/spritesheet.png").exists())

    def test_explicit_wrong_pet_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "不一致"):
            installer.validate_package(bundle(pet_id="sheep-chibi"), expected_id="capybara-chibi")

    def test_sheep_update_restores_previous_atlas(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            previous = home / "pets/sheep-chibi"
            previous.mkdir(parents=True)
            (previous / "spritesheet.png").write_bytes(b"previous artwork")
            (home / "config.toml").write_text('[desktop]\nselected-avatar-id = "custom:sheep-chibi"\n')
            installer.install(bundle(pet_id="sheep-chibi"), home)
            installer.restore(home,"sheep-chibi")
            self.assertEqual((previous / "spritesheet.png").read_bytes(),b"previous artwork")

    def test_real_package_installs_and_selects(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            (home / "config.toml").write_text('[desktop]\nfollowUpQueueMode = "queue"\n\n[other]\nvalue = 9\n')
            pet_id, _, backup = installer.install(bundle(), home)
            self.assertEqual(pet_id, "capybara-chibi")
            self.assertTrue((home / "pets/capybara-chibi/spritesheet.webp").exists())
            text = (home / "config.toml").read_text()
            self.assertEqual(installer.selection(text), "custom:capybara-chibi")
            self.assertIn('followUpQueueMode = "queue"', text)
            self.assertIn('[other]\nvalue = 9', text)
            self.assertTrue((backup / "receipt.json").exists())

    def test_update_and_restore_previous_version_and_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            previous = home / "pets/capybara-chibi"
            previous.mkdir(parents=True)
            (previous / "old.txt").write_text("old pet")
            (home / "config.toml").write_text('[desktop]\nselected-avatar-id = "codex"\n')
            installer.install(bundle(), home)
            with (home / "config.toml").open("a") as handle:
                handle.write('otherOption = true\n')
            installer.restore(home, "capybara-chibi")
            self.assertEqual((previous / "old.txt").read_text(), "old pet")
            config = (home / "config.toml").read_text()
            self.assertEqual(installer.selection(config), "codex")
            self.assertIn('otherOption = true', config)

    def test_failed_config_write_rolls_back_pet(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            previous = home / "pets/capybara-chibi"
            previous.mkdir(parents=True)
            (previous / "old.txt").write_text("old pet")
            (home / "config.toml").write_text('[desktop]\nselected-avatar-id = "codex"\n')
            original = installer.atomic_text
            def reject_config(path, text):
                if path == home / "config.toml":
                    raise OSError("simulated failure")
                return original(path, text)
            with patch.object(installer, "atomic_text", side_effect=reject_config):
                with self.assertRaises(OSError):
                    installer.install(bundle(), home)
            self.assertEqual((previous / "old.txt").read_text(), "old pet")
            self.assertEqual(installer.selection((home / "config.toml").read_text()), "codex")

    def test_invalid_hash_does_not_touch_home(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / "new-home"
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                installer.install(bundle(), home, "0" * 64)
            self.assertFalse(home.exists())

    def test_internal_hash_failure(self):
        with self.assertRaisesRegex(ValueError, "校验失败"):
            installer.validate_package(bundle(wrong_sprite_hash=True))

    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            installer.validate_package(bundle(extra="../config.toml"))

    def test_symlink_destination_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            (home / "pets").mkdir()
            (home / "outside").mkdir()
            (home / "pets/capybara-chibi").symlink_to(home / "outside", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "普通目录"):
                installer.install(bundle(), home)
            self.assertFalse((home / "outside/pet.json").exists())

    def test_no_select_preserves_config(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            text = '[desktop]\nselected-avatar-id = "codex"\n'
            (home / "config.toml").write_text(text)
            installer.install(bundle(), home, select=False)
            self.assertEqual((home / "config.toml").read_text(), text)

    def test_restore_first_install_removes_new_pet(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            installer.install(bundle(), home)
            installer.restore(home, "capybara-chibi")
            self.assertFalse((home / "pets/capybara-chibi").exists())
            self.assertIsNone(installer.selection((home / "config.toml").read_text()))

    def test_http_download_rejected(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            installer.download("http://example.com/pet.zip")

    def test_remote_catalog_download_and_install(self):
        package = bundle()
        catalog = {"formatVersion": 1, "pets": [{"id": "capybara-chibi",
                   "displayName": "卡皮巴拉", "asset": "capybara-chibi.zip",
                   "sha256": installer.digest(package)}]}
        calls = []
        def fake_download(url, limit=installer.MAX_DOWNLOAD):
            calls.append(url)
            return json.dumps(catalog).encode() if url.endswith("pets.json") else package
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(installer, "download", side_effect=fake_download):
                result = installer.main(["--base-url", "https://github.com/example/pets/releases/download/v1.0.0",
                                         "--codex-home", temp])
            self.assertEqual(result, 0)
            self.assertEqual(calls, ["https://github.com/example/pets/releases/download/v1.0.0/pets.json",
                                     "https://github.com/example/pets/releases/download/v1.0.0/capybara-chibi.zip"])
            self.assertTrue((Path(temp) / "pets/capybara-chibi/spritesheet.webp").exists())


if __name__ == "__main__":
    unittest.main()
