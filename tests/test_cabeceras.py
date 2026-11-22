# -*- coding: utf-8 -*-
"""Header rendering: the person's name, never a redundant document label.

For every template x language this checks that ``build_tex`` renders the
escaped name through ``\\cvfitname``, that the short label only appears when
the name is empty, and that no placeholder survives the substitution and the
data round-trip is exact. Sidebar/sidebar-right keep their name + profession
header (see test_sidebar.py); the label is not part of it. Real compilations
use the same skipif pattern as test_roundtrip_tex.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

import latex_engine  # noqa: E402
import latex_gen  # noqa: E402
import prefs  # noqa: E402
import tex_datos  # noqa: E402

TEMPLATES = latex_gen.TEMPLATES
IDIOMAS = ("es", "zh")
SIDEBAR = ("sidebar", "sidebar-right")

MOTOR_PDF = latex_engine.find_pdflatex()
MOTOR_CJK = latex_engine.find_xelatex()

# Short names without characters that esc() may split with \allowbreak.
NOMBRES = {"es": "Ana García", "zh": "张伟"}

# Long but realistic names: Latin with spaces/hyphen, CJK without spaces.
NOMBRES_LARGOS = {
    "es": "Alexander Maximilian von Hohenberg-Sauerbruch",
    "en": "Alexander Maximilian von Hohenberg-Sauerbruch",
    "zh": "亚历山大马克西米利安冯霍恩贝格绍尔布鲁赫",
}


@pytest.fixture()
def prefs_tmp(tmp_path, monkeypatch):
    """Isolate prefs (dirs and cache) from the user's machine."""
    app = tmp_path / "app"
    monkeypatch.setattr(prefs, "APP_DIR", str(app))
    monkeypatch.setattr(prefs, "CACHE_DIR", str(app / "cache"))
    monkeypatch.setattr(prefs, "BUILD_DIR", str(app / "cache" / "build"))
    monkeypatch.setattr(prefs, "PREFS_FILE", str(app / "prefs.json"))
    monkeypatch.setattr(prefs, "_CACHE", None)
    return tmp_path


def datos_cabecera(idioma, plantilla, nombre=None):
    """Minimal CV: only the header (name) in the given language/template."""
    d = latex_gen.empty_data()
    d["cv_language"] = idioma
    d["template"] = plantilla
    d["name"] = NOMBRES[idioma] if nombre is None else nombre
    return d


def datos_contactos(idioma="es", plantilla="classic"):
    """CV whose header carries every contact group in a known order."""
    d = datos_cabecera(idioma, plantilla)
    if idioma == "zh":
        d["phone"] = "13800000000"
        d["email"] = "zhangwei@example.com"
        d["address"] = "北京"
        d["school_name"] = "清华"
        d["profession"] = "工程师"
        d["extra_fields"] = [{"label": "国籍", "value": "中国"}]
        d["socials"] = [
            {"network": "github", "label": "", "value": "github.com/zhangwei"},
            {"network": "linkedin", "label": "", "value": "in/zhangwei"},
        ]
    else:
        d["phone"] = "600000000"
        d["email"] = "ana@example.com"
        d["address"] = "Madrid"
        d["school_name"] = "UPM"
        d["profession"] = "Dev"
        d["extra_fields"] = [{"label": "Nacimiento", "value": "12/05/1994"}]
        d["socials"] = [
            {"network": "github", "label": "", "value": "github.com/ana"},
            {"network": "linkedin", "label": "", "value": "linkedin.com/in/ana"},
        ]
    return d


def lineas_contacto(datos, L):
    """(personal, objective, socials) expected contact lines for ``datos``."""
    def line(label, value, mono=False):
        text = f"\\texttt{{{latex_gen.esc(value)}}}" if mono else latex_gen.esc(value)
        return f"\\textbf{{{label}}} {text}"

    extra = datos["extra_fields"][0]
    personal = [
        line(L["phone"], datos["phone"], mono=True),
        line(L["email"], datos["email"], mono=True),
        line(L["address"], datos["address"]),
        line(L["school_name"], datos["school_name"]),
        line(extra["label"] + ":", extra["value"]),
    ]
    objective = [line(L["profession"], datos["profession"])]
    social = [
        f"\\textbf{{{latex_gen.social_label(s['network'], s['label'], L)}:}} "
        f"\\texttt{{{latex_gen.esc(s['value'])}}}"
        for s in datos["socials"]
    ]
    return personal, objective, social


def cuerpo(tex):
    """Generated document after the preamble (where headers and body live)."""
    return tex[tex.index("\\begin{document}"):]


@pytest.mark.parametrize("plantilla", TEMPLATES)
@pytest.mark.parametrize("idioma", IDIOMAS)
def test_cabecera_espaciada(plantilla, idioma, prefs_tmp):
    datos = datos_cabecera(idioma, plantilla)
    tex = latex_gen.build_tex(datos, prefs.load())
    after = cuerpo(tex)

    corto = latex_gen.LANG[idioma]["title_short"]
    nombre = latex_gen.esc(datos["name"])

    assert nombre in after
    # A real name always wins: the redundant label is never rendered with it.
    assert corto not in tex
    assert "\\cvfitname" in after
    assert "{{" not in tex
    assert tex_datos.extract(tex) == datos

    if plantilla in SIDEBAR:
        # Header = name (large, accent, fitted) + profession + accent rule.
        assert (
            "{\\Huge\\bfseries\\color{accent}\\cvfitname{" + nombre + "}}"
        ) in after
        return

    # The name appears once: no duplicate below a banner either.
    assert after.count(nombre) == 1


@pytest.mark.parametrize("plantilla", TEMPLATES)
@pytest.mark.parametrize("idioma", IDIOMAS)
def test_cabecera_nombre_vacio_usa_etiqueta_corta(plantilla, idioma, prefs_tmp):
    """An empty name falls back to the short label, except in the sidebar."""
    datos = datos_cabecera(idioma, plantilla, nombre="")
    tex = latex_gen.build_tex(datos, prefs.load())
    after = cuerpo(tex)
    corto = latex_gen.LANG[idioma]["title_short"]

    assert "{{" not in tex
    assert tex_datos.extract(tex) == datos

    if plantilla in SIDEBAR:
        # The sidebar header is name + profession; with neither it is empty
        # and must never show the document label.
        assert corto not in tex
        assert "\\cvfitname{" + corto + "}" not in tex
        return

    assert corto in after
    assert "\\cvfitname" in after
    assert after.count(corto) == 1


@pytest.mark.parametrize("plantilla", TEMPLATES)
@pytest.mark.parametrize("idioma", ("es", "en", "zh"))
def test_cabecera_nombre_largo_se_ajusta(plantilla, idioma, prefs_tmp):
    """A very long name is still emitted whole and wrapped in \\cvfitname."""
    datos = datos_cabecera(idioma, plantilla, nombre=NOMBRES_LARGOS[idioma])
    tex = latex_gen.build_tex(datos, prefs.load())
    after = cuerpo(tex)
    nombre = latex_gen.esc(datos["name"])

    assert nombre in after
    assert "\\cvfitname" in after
    assert "{{" not in tex
    assert tex_datos.extract(tex) == datos
    assert after.count(nombre) == 1


@pytest.mark.parametrize("plantilla", TEMPLATES)
@pytest.mark.parametrize("idioma", IDIOMAS)
def test_cabecera_socials_dinamicos(plantilla, idioma, prefs_tmp):
    """Socials render in the header with their names and document language."""
    datos = datos_cabecera(idioma, plantilla)
    datos["socials"] = [
        {"network": "github", "label": "Ignorado", "value": "github.com/ana"},
        {"network": "website", "label": "", "value": "ana.dev"},
        {"network": "other", "label": "", "value": "otro.dev"},
        {"network": "other", "label": "Mastodon", "value": "mastodon/@ana"},
        {"network": "linkedin", "label": "", "value": "   "},
    ]
    tex = latex_gen.build_tex(datos, prefs.load())

    assert "\\textbf{GitHub:} \\texttt{github.com/ana}" in tex
    assert "\\textbf{%s:} \\texttt{ana.dev}" % latex_gen.LANG[idioma]["website"] in tex
    assert "\\textbf{%s:} \\texttt{otro.dev}" % latex_gen.LANG[idioma]["link"] in tex
    assert "\\textbf{Mastodon:} \\texttt{mastodon/@ana}" in tex
    assert "Ignorado" not in tex
    assert tex_datos.extract(tex) == datos


@pytest.mark.parametrize("plantilla", TEMPLATES)
@pytest.mark.parametrize("idioma", IDIOMAS)
def test_cabecera_orden_personal_objetivo_social(plantilla, idioma, prefs_tmp):
    """Personal data comes first, then the objective, then the social links."""
    datos = datos_contactos(idioma, plantilla)
    tex = latex_gen.build_tex(datos, prefs.load())
    L = latex_gen.LANG[idioma]
    personal, objective, social = lineas_contacto(datos, L)

    for entry in personal:
        assert tex.index(entry) < tex.index(objective[0])
    for entry in social:
        assert tex.index(objective[0]) < tex.index(entry)

    color = "white" if plantilla in SIDEBAR else "black!55"
    for entry in social:
        assert "{\\footnotesize\\color{" + color + "} " + entry + "}" in tex


@pytest.mark.parametrize("plantilla", ("sword", "tabbed"))
def test_cabecera_dos_columnas_prioriza_datos_personales(plantilla, prefs_tmp):
    """Personal data + objective fill the primary column, links the secondary."""
    datos = datos_contactos("es", plantilla)
    tex = latex_gen.build_tex(datos, prefs.load())
    L = latex_gen.LANG["es"]
    personal, objective, social = lineas_contacto(datos, L)

    # The primary column is emitted before the secondary one, so every
    # personal/objective line precedes the first social link.
    first_social = min(tex.index(entry) for entry in social)
    for entry in personal + objective:
        assert tex.index(entry) < first_social

    marker = (
        "\\begin{minipage}[t]{0.48\\linewidth}"
        if plantilla == "tabbed"
        else "\\parbox[t]{0.47\\linewidth}"
    )
    assert tex.count(marker) >= 2


def test_sword_sin_hairlines_entre_contactos(prefs_tmp):
    """The Sword header drops the per-row hairlines but keeps its bottom rule."""
    datos = datos_contactos("es", "sword")
    tex = latex_gen.build_tex(datos, prefs.load())

    # The old light separator between contact rows is gone...
    assert "{\\color{acento2}\\hrule height 0.4pt}" not in tex
    # ...while the rule that closes the whole header stays.
    assert "{\\color{accent}\\hrule height 0.7pt}" in tex


def test_sword_contact_grid_sin_hairlines():
    grid = latex_gen._sword_contact_grid(
        ["\\textbf{Teléfono:} \\texttt{600}"],
        ["\\textbf{Puesto al que aspiras:} Dev"],
        ["\\textbf{GitHub:} \\texttt{github.com/ana}"],
    )
    assert "\\hrule" not in grid
    assert "\\vspace{0.18em}" in grid
    assert grid.count("\\parbox[t]{0.47\\linewidth}") == 2
    assert grid.index("\\textbf{Teléfono:}") < grid.index("\\textbf{GitHub:}")


def test_sword_contact_grid_solo_social():
    """With no personal/objective content the links take the full width."""
    grid = latex_gen._sword_contact_grid(
        [], [], ["\\textbf{GitHub:} \\texttt{github.com/ana}"]
    )
    assert "\\parbox[t]{\\linewidth}" in grid
    assert "0.47\\linewidth" not in grid


def test_sword_contact_grid_balancea_sin_sociales():
    """Without links the personal data is split across the two columns."""
    grid = latex_gen._sword_contact_grid(
        ["\\textbf{Teléfono:} \\texttt{600}", "\\textbf{Correo:} \\texttt{a@b.co}"],
        [],
        [],
    )
    assert grid.count("\\parbox[t]{0.47\\linewidth}") == 2
    assert grid.index("\\textbf{Teléfono:}") < grid.index("\\textbf{Correo:}")


def test_school_logo_is_a_letterhead_above_the_header(tmp_path, prefs_tmp):
    """The logo sits in the top corner, before the name and contacts."""
    d = datos_contactos("es", "classic")
    logo = tmp_path / "logo.png"
    logo.write_bytes(b"\x89PNG\r\n\x1a\n")
    d["school_logo"] = str(logo)

    tex = latex_gen.build_tex(d, prefs.load())
    body = tex[tex.index("\\begin{document}"):]

    assert tex.count("logo_egresado.png") == 1
    assert "width=4cm" in tex
    assert "height=1.5cm" in tex
    assert body.index("logo_egresado.png") < body.index("\\cvfitname{")
    assert body.index("logo_egresado.png") < body.index(
        "\\textbf{%s}" % latex_gen.LANG["es"]["school_name"]
    )


def test_school_logo_can_use_the_right_corner(tmp_path, prefs_tmp):
    d = datos_contactos("es", "classic")
    logo = tmp_path / "logo.png"
    logo.write_bytes(b"\x89PNG\r\n\x1a\n")
    photo = tmp_path / "photo.png"
    photo.write_bytes(b"\x89PNG\r\n\x1a\n")
    d["school_logo"] = str(logo)
    d["school_logo_side"] = "right"
    d["photo"] = str(photo)

    tex = latex_gen.build_tex(d, prefs.load())

    # The right-corner logo shares the reserved media column with the photo;
    # it is not a separate full-width letterhead that moves the left text.
    assert "\\includegraphics[width=4cm,height=1.5cm" in tex
    assert tex.index("logo_egresado.png") < tex.index("foto.png")
    assert "{\\raggedleft \\includegraphics[width=4.5cm" not in tex


def test_school_logo_size_is_configurable_and_clamped(tmp_path, prefs_tmp):
    d = datos_contactos("es", "classic")
    logo = tmp_path / "logo.png"
    logo.write_bytes(b"\x89PNG\r\n\x1a\n")
    d["school_logo"] = str(logo)
    d["school_logo_width_cm"] = 3.2
    d["school_logo_height_cm"] = 1.2

    tex = latex_gen.build_tex(d, prefs.load())
    assert "width=3.2cm" in tex
    assert "height=1.2cm" in tex

    # The right media column caps the logo so it cannot overflow the layout.
    d["school_logo_side"] = "right"
    d["school_logo_width_cm"] = 9.0
    d["school_logo_height_cm"] = 9.0
    tex = latex_gen.build_tex(d, prefs.load())
    assert "width=4cm" in tex
    assert "height=2cm" in tex


def test_harvard_is_designed_without_a_photo(tmp_path, prefs_tmp):
    d = datos_contactos("es", "harvard")
    photo = tmp_path / "photo.png"
    photo.write_bytes(b"\x89PNG\r\n\x1a\n")
    d["photo"] = str(photo)

    tex = latex_gen.build_tex(d, prefs.load())

    assert "foto.png" not in tex


def test_sidebar_school_logo_is_at_the_top_of_the_bar(tmp_path, prefs_tmp):
    d = datos_contactos("es", "sidebar")
    logo = tmp_path / "logo.png"
    logo.write_bytes(b"\x89PNG\r\n\x1a\n")
    photo = tmp_path / "photo.png"
    photo.write_bytes(b"\x89PNG\r\n\x1a\n")
    d["school_logo"] = str(logo)
    d["photo"] = str(photo)

    tex = latex_gen.build_tex(d, prefs.load())

    assert tex.count("logo_egresado.png") == 1
    assert "width=4cm" in tex
    assert tex.index("logo_egresado.png") < tex.index("foto.png")


@pytest.mark.latex
@pytest.mark.skipif(MOTOR_PDF is None, reason="No LaTeX engine (pdflatex) installed")
@pytest.mark.parametrize("plantilla", TEMPLATES)
def test_compila_pdf_cabeceras_es(plantilla, prefs_tmp):
    datos = datos_cabecera("es", plantilla)
    tex = latex_gen.build_tex(datos, prefs.load())
    resultado = latex_engine.compile(tex, None, None)
    assert resultado["ok"], resultado["errores"]
    assert resultado["pdf"] and os.path.isfile(resultado["pdf"])


@pytest.mark.latex
@pytest.mark.skipif(
    MOTOR_PDF is None or MOTOR_CJK is None,
    reason="No LaTeX engines (pdflatex/xelatex) for CJK compilation",
)
@pytest.mark.parametrize("plantilla", TEMPLATES)
def test_compila_pdf_cabeceras_zh(plantilla, prefs_tmp):
    datos = datos_cabecera("zh", plantilla)
    tex = latex_gen.build_tex(datos, prefs.load())
    resultado = latex_engine.compile(tex, None, None)
    assert resultado["ok"], resultado["errores"]
    assert resultado["pdf"] and os.path.isfile(resultado["pdf"])
