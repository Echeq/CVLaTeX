# -*- coding: utf-8 -*-
"""Input hardening: image magic bytes, upload limits and media materialization.

The HTTP session gate lives in tests/test_http.py. These tests cover the
bridge entry points that receive untrusted data from the webview or from a
.cvjson file: save_image, choose_photo, open_cv and materialize_media.
"""

import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

import main  # noqa: E402
import messages  # noqa: E402
import prefs  # noqa: E402

PNG = main.PNG_SIGNATURE
JPEG = main.JPEG_SIGNATURE


@pytest.fixture()
def prefs_tmp(tmp_path, monkeypatch):
    app = tmp_path / "app"
    monkeypatch.setattr(prefs, "APP_DIR", str(app))
    monkeypatch.setattr(prefs, "CACHE_DIR", str(app / "cache"))
    monkeypatch.setattr(prefs, "BUILD_DIR", str(app / "cache" / "build"))
    monkeypatch.setattr(prefs, "PREFS_FILE", str(app / "prefs.json"))
    monkeypatch.setattr(prefs, "_CACHE", None)
    return tmp_path


def _data_url(mime, raw):
    return "data:%s;base64,%s" % (mime, base64.b64encode(raw).decode("ascii"))


def test_save_image_accepts_valid_png_and_rejects_spoofed_bytes(prefs_tmp):
    api = main.Api(None)
    result = api.save_image(_data_url("image/png", PNG + b"payload"))
    assert result["ok"] is True
    assert result["url"].startswith("/media/")
    assert os.path.isfile(result["path"])

    spoofed = api.save_image(_data_url("image/png", b"<html>not an image</html>"))
    assert spoofed["ok"] is False
    assert spoofed["errores"] == [messages.t("image_invalid_content")]


def test_save_image_rejects_a_jpeg_declared_as_png(prefs_tmp):
    api = main.Api(None)
    result = api.save_image(_data_url("image/png", JPEG + b"payload"))
    assert result["ok"] is False
    assert result["errores"] == [messages.t("image_invalid_content")]


def test_save_image_enforces_the_data_url_and_decoded_size_limits(
    prefs_tmp, monkeypatch
):
    api = main.Api(None)
    monkeypatch.setattr(main, "MAX_IMAGE_BYTES", 4)
    monkeypatch.setattr(main, "MAX_DATA_URL_CHARS", 8)
    result = api.save_image(_data_url("image/png", PNG + b"payload"))
    assert result["ok"] is False
    assert "MB" in result["errores"][0]
    leftovers = (
        [name for name in os.listdir(prefs.CACHE_DIR) if name.startswith("foto_")]
        if os.path.isdir(prefs.CACHE_DIR)
        else []
    )
    assert leftovers == []


def test_choose_photo_validates_magic_bytes_and_size(prefs_tmp, monkeypatch):
    api = main.Api(None)
    bad = prefs_tmp / "bad.png"
    bad.write_bytes(b"not really a png")
    monkeypatch.setattr(api, "choose_file", lambda *args, **kwargs: str(bad))
    assert api.choose_photo() == {
        "ok": False,
        "error": messages.t("image_invalid_content"),
    }

    good = prefs_tmp / "good.jpg"
    good.write_bytes(JPEG + b"payload")
    monkeypatch.setattr(api, "choose_file", lambda *args, **kwargs: str(good))
    saved = api.choose_photo()
    assert saved["ok"] is True
    assert saved["url"].startswith("/media/")

    monkeypatch.setattr(main, "MAX_IMAGE_BYTES", 4)
    too_big = api.choose_photo()
    assert too_big["ok"] is False
    assert "MB" in too_big["error"]


def test_open_cv_rejects_files_above_the_size_limit(prefs_tmp, monkeypatch):
    api = main.Api(None)
    path = prefs_tmp / "big.cvjson"
    path.write_text(json.dumps({"version": 3, "data": {"name": "x"}}), encoding="utf-8")
    monkeypatch.setattr(main, "MAX_CVJSON_BYTES", 8)
    monkeypatch.setattr(api, "choose_file", lambda *args, **kwargs: str(path))
    result = api.open_cv()
    assert result["ok"] is False
    assert result["errores"] == [messages.t("file_too_large").format(size=1)]


def test_materialize_media_skips_invalid_magic_and_keeps_the_original_path(prefs_tmp):
    original = str(prefs_tmp / "photo.png")
    data = {"photo": original, "name": "Ana"}
    media = {
        original: {
            "name": "photo.png",
            "b64": base64.b64encode(b"<html>not an image</html>").decode("ascii"),
        }
    }
    result = main.materialize_media(data, media)
    assert result["photo"] == original
    assert not os.path.isdir(prefs.CACHE_DIR) or not os.listdir(prefs.CACHE_DIR)


def test_materialize_media_writes_valid_images_and_respects_the_total_cap(
    prefs_tmp, monkeypatch
):
    first = str(prefs_tmp / "one.png")
    second = str(prefs_tmp / "two.png")
    data = {"photo": first, "photo_original": second}
    media = {
        first: {"name": "one.png", "b64": base64.b64encode(PNG + b"one").decode()},
        second: {"name": "two.png", "b64": base64.b64encode(PNG + b"two").decode()},
    }
    monkeypatch.setattr(main, "MAX_MEDIA_TOTAL_BYTES", len(PNG) + 3)
    result = main.materialize_media(data, media)
    assert result["photo"] != first
    assert os.path.isfile(result["photo"])
    # The second image does not fit: its original path is left untouched.
    assert result["photo_original"] == second
    assert len(os.listdir(prefs.CACHE_DIR)) == 1


def test_collect_media_skips_oversized_and_invalid_files(prefs_tmp, monkeypatch):
    valid = prefs_tmp / "valid.png"
    valid.write_bytes(PNG + b"ok")
    invalid = prefs_tmp / "invalid.png"
    invalid.write_bytes(b"not a png")
    data = {"photo": str(valid), "photo_original": str(invalid)}
    media = main.collect_media(data)
    assert set(media) == {str(valid)}
    assert base64.b64decode(media[str(valid)]["b64"]) == PNG + b"ok"

    monkeypatch.setattr(main, "MAX_MEDIA_BYTES", 4)
    assert main.collect_media(data) == {}


def test_new_security_messages_are_localized_in_four_languages():
    for key in (
        "image_too_large",
        "image_invalid_content",
        "file_too_large",
        "install_insecure_mirror",
    ):
        texts = [messages.t(key, lang) for lang in ("es", "en", "zh", "ru")]
        assert all(isinstance(text, str) and text.strip() for text in texts)
        assert len(set(texts)) == 4
