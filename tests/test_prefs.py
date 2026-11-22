# -*- coding: utf-8 -*-
"""Per-OS application data directory of prefs.

The module-level attributes (APP_DIR, CACHE_DIR, BUILD_DIR, TINYTEX_DIR,
PREFS_FILE) stay in place; only their base changes per platform. These tests
exercise the pure path helper (no filesystem writes, no GUI).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prefs  # noqa: E402


def test_app_dir_for_windows_uses_localappdata():
    result = prefs._app_dir_for(
        "win32", {"LOCALAPPDATA": r"C:\Users\Ana\AppData\Local"}, r"C:\Users\Ana"
    )
    assert result == os.path.join(r"C:\Users\Ana\AppData\Local", "CVLaTeX")
    # Without LOCALAPPDATA it falls back to the user home (legacy behavior).
    result = prefs._app_dir_for("win32", {}, r"C:\Users\Ana")
    assert result == os.path.join(r"C:\Users\Ana", "CVLaTeX")


def test_app_dir_for_macos_uses_application_support():
    result = prefs._app_dir_for("darwin", {}, "/Users/ana")
    assert result == os.path.join(
        "/Users/ana", "Library", "Application Support", "CVLaTeX"
    )


def test_app_dir_for_linux_uses_xdg_data_home():
    assert prefs._app_dir_for("linux", {}, "/home/ana") == os.path.join(
        "/home/ana", ".local", "share", "CVLaTeX"
    )
    assert prefs._app_dir_for(
        "linux", {"XDG_DATA_HOME": "/home/ana/.data"}, "/home/ana"
    ) == os.path.join("/home/ana/.data", "CVLaTeX")


def test_defaults_include_font_preferences():
    assert prefs.DEFAULTS["font_size"] == 11
    assert prefs.DEFAULTS["font_style"] == ""
    assert prefs.DEFAULTS["units"] == "cm"
    assert prefs.DEFAULTS["tinytex_url"] == ""
    assert prefs.DEFAULTS["split"] == 50
    assert prefs.DEFAULTS["split_vertical"] == 50
    assert prefs.DEFAULTS["layout_mode"] == "side"


def test_module_attributes_keep_the_expected_layout():
    for name in ("APP_DIR", "CACHE_DIR", "BUILD_DIR", "TINYTEX_DIR", "PREFS_FILE"):
        value = getattr(prefs, name)
        assert isinstance(value, str) and value
    assert prefs.CACHE_DIR == os.path.join(prefs.APP_DIR, "cache")
    assert prefs.BUILD_DIR == os.path.join(prefs.CACHE_DIR, "build")
    assert prefs.TINYTEX_DIR == os.path.join(prefs.APP_DIR, "tinytex")
    assert prefs.PREFS_FILE == os.path.join(prefs.APP_DIR, "prefs.json")
    # The live APP_DIR follows the running platform.
    assert prefs.APP_DIR == prefs._app_dir_for(sys.platform)


def test_migrate_legacy_app_dir_moves_old_data(tmp_path, monkeypatch):
    new_dir = tmp_path / "CVLaTeX"
    legacy = tmp_path / "CVLaTex"
    legacy.mkdir()
    (legacy / "prefs.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(prefs, "APP_DIR", str(new_dir))

    assert prefs.legacy_app_dir() == str(legacy)
    assert prefs.migrate_legacy_app_dir() is True
    assert not legacy.exists()
    assert (new_dir / "prefs.json").read_text(encoding="utf-8") == "{}"


def test_migrate_legacy_app_dir_keeps_existing_new_data(tmp_path, monkeypatch):
    new_dir = tmp_path / "CVLaTeX"
    legacy = tmp_path / "CVLaTex"
    new_dir.mkdir()
    legacy.mkdir()
    (new_dir / "prefs.json").write_text("new", encoding="utf-8")
    (legacy / "prefs.json").write_text("old", encoding="utf-8")
    monkeypatch.setattr(prefs, "APP_DIR", str(new_dir))

    assert prefs.migrate_legacy_app_dir() is False
    assert (new_dir / "prefs.json").read_text(encoding="utf-8") == "new"
    assert (legacy / "prefs.json").read_text(encoding="utf-8") == "old"


def test_migrate_legacy_app_dir_is_a_noop_without_old_data(tmp_path, monkeypatch):
    monkeypatch.setattr(prefs, "APP_DIR", str(tmp_path / "CVLaTeX"))
    assert prefs.migrate_legacy_app_dir() is False
