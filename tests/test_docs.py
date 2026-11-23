# -*- coding: utf-8 -*-
"""Documentation wiring: market guides, competition package and media rules.

The guides are deliberately outside the release archive; these checks keep the
six market files, their README links and the [Insert:...] placeholders present
so the material can be filled in later without silently disappearing.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARKETS = ("en-US", "en-GB", "es-ES", "es-LATAM", "zh-CN", "ru-RU")


def _read(*parts):
    with open(os.path.join(ROOT, *parts), "r", encoding="utf-8") as f:
        return f.read()


def test_market_guides_exist_and_have_media_placeholders():
    for market in MARKETS:
        text = _read("docs", "markets", market + ".md")
        assert "[Insert:Image:{" in text, market
        assert "[Insert:Video:{" in text, market
        assert "## Sources" in text or "## Fuentes" in text, market


def test_market_index_links_every_guide():
    index = _read("docs", "markets", "README.md")
    for market in MARKETS:
        assert "(%s.md)" % market in index, market


def test_readme_links_every_market_guide():
    readme = _read("README.md")
    for market in MARKETS:
        assert "docs/markets/%s.md" % market in readme, market
    assert "docs/media/images/demo-poster.png" in readme
    assert "echeq.github.io/CVLaTeX/demo.html" in readme


def test_competition_and_media_docs_exist():
    competition = _read("docs", "competition", "README.md")
    assert "echeq.github.io/CVLaTeX/demo.html" in competition
    assert "../media/images/demo-poster.png" in competition
    assert "30 November 2026" in competition
    assert "ossrpp.tcode.com.cn" in competition
    assert "git.hust.edu.cn" in competition


def test_readme_demo_media_files_exist():
    video = os.path.join(ROOT, "docs", "media", "videos", "demo-en.mp4")
    poster = os.path.join(ROOT, "docs", "media", "images", "demo-poster.png")
    assert os.path.isfile(video) and os.path.getsize(video) > 100_000
    assert os.path.isfile(poster) and os.path.getsize(poster) > 10_000


def test_chinese_readme_and_language_switch():
    english = _read("README.md")
    chinese = _read("README.zh.md")
    assert "[中文](README.zh.md)" in english
    assert "[English](README.md)" in chinese
    assert "1027" in chinese and "918" in chinese
    assert "https://echeq.github.io/CVLaTeX/demo.html" in chinese
    assert "MIT" in chinese
    competition = _read("docs", "competition", "README.md")
    assert "../../README.zh.md" in competition

    media = _read("docs", "media", "README.md")
    assert "[Insert:Image:{" in media
    assert "[Insert:Video:{" in media
    assert os.path.isdir(os.path.join(ROOT, "docs", "media", "images"))
    assert os.path.isdir(os.path.join(ROOT, "docs", "media", "videos"))
