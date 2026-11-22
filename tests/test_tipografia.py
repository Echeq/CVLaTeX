# -*- coding: utf-8 -*-
"""Typographic preferences: font style and font size.

These tests only render TeX; they never run a LaTeX engine. The size rules
cover the `article` limitation (10/11/12pt) and the optional `scrextend`
override used for the other UI sizes.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import latex_gen  # noqa: E402

PREFS = {
    "paper": "a4",
    "margins": {"top": 2.0, "bottom": 2.0, "left": 2.0, "right": 2.0},
    "font_size": 11,
    "font_style": "",
}


def _tex(template="classic", **overrides):
    """build_tex() output for the canonical prefs plus the given overrides."""
    p = dict(PREFS)
    p.update(overrides)
    data = latex_gen.empty_data()
    data["template"] = template
    return latex_gen.build_tex(data, p)


def test_template_style_adds_no_override():
    assert "\\renewcommand{\\familydefault}" not in _tex()


@pytest.mark.parametrize(
    "style,command",
    [("serif", "\\rmdefault"), ("sans", "\\sfdefault"), ("mono", "\\ttdefault")],
)
def test_style_overrides_the_default_family(style, command):
    override = "\\renewcommand{\\familydefault}{%s}" % command
    tex = _tex(font_style=style)
    assert override in tex
    # The override must live in the preamble, after the template's own
    # definitions, so it wins over a template that sets \familydefault.
    assert tex.index(override) < tex.index("\\begin{document}")


def test_unknown_style_is_ignored():
    assert "\\familydefault" not in _tex(font_style="comic")


def test_style_wins_over_the_template_familydefault():
    override = "\\renewcommand{\\familydefault}{\\sfdefault}"
    tex = _tex(template="playful", font_style="sans")
    # The playful template already sets this; our override is the last one.
    assert tex.count(override) >= 2
    assert tex.rindex(override) < tex.index("\\begin{document}")


@pytest.mark.parametrize(
    "size,class_option,exact",
    [
        (9, "10pt", "9pt"),
        (10, "10pt", None),
        (11, "11pt", None),
        (12, "12pt", None),
        (14, "12pt", "14pt"),
    ],
)
def test_font_size_maps_to_the_article_sizes(size, class_option, exact):
    tex = _tex(font_size=size)
    assert "\\documentclass[%s]{article}" % class_option in tex
    if exact is None:
        assert "scrextend" not in tex
    else:
        assert "\\IfFileExists{scrextend.sty}" in tex
        assert "\\usepackage[fontsize=%s]{scrextend}" % exact in tex


def test_invalid_font_size_falls_back_to_the_default():
    tex = _tex(font_size="not-a-number")
    assert "\\documentclass[11pt]{article}" in tex
    assert "scrextend" not in tex


@pytest.mark.parametrize(
    "size,class_option,exact",
    [(99, "12pt", "20pt"), (1, "10pt", "8pt")],
)
def test_font_size_is_clamped_to_a_safe_range(size, class_option, exact):
    tex = _tex(font_size=size)
    assert "\\documentclass[%s]{article}" % class_option in tex
    assert "\\usepackage[fontsize=%s]{scrextend}" % exact in tex
