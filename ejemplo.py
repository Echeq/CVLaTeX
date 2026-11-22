"""Sample CVs for CVLaTeX.

Return dicts with the same shape as ``latex_gen.empty_data()`` filled with a
realistic software-engineering student profile, so the user sees how to
complete each form section. The three languages tell the same story; only the
prose and labels are localized.

The sample is deliberately simple and uses the project owner's public
identifiers: Elvis Enrique Chen Qiu / 陈昌发, HUST Software Engineering,
GitHub and LinkedIn handles ``ECHEQ``, and the example address
``echeq@github.com``. The phone number is fake.
"""

import copy

import latex_gen


_LANGUAGES = ("zh", "es", "en")

# Shared, deliberately public sample identifiers. The phone number is fake.
_EMAIL = "echeq@github.com"
_PHONE = "123-456-78"
_SOCIALS = (
    {"network": "github", "label": "", "value": "github.com/ECHEQ"},
    {"network": "linkedin", "label": "", "value": "linkedin.com/in/ECHEQ"},
)

_UNIVERSITY = {
    "es": "Universidad de Ciencia y Tecnología de Huazhong (HUST)",
    "en": "Huazhong University of Science and Technology (HUST)",
    "zh": "华中科技大学",
}

_TEXT = {
    "es": {
        "name": "ELVIS ENRIQUE CHEN QIU",
        "profession": "Estudiante de Ingeniería de Software",
        "address": "Wuhan, Hubei, China",
        "summary": (
            "Estudiante de Ingeniería de Software en HUST (China), centrado en "
            "aplicaciones de escritorio multiplataforma, herramientas LaTeX y "
            "código abierto. Creador de CVLaTeX, un editor de CV local con 12 "
            "plantillas y exportación a PDF, Word y LaTeX."
        ),
        "location_label": "Ubicación",
        "location_value": "Wuhan, China",
        "availability_label": "Disponibilidad",
        "availability_value": "Prácticas / jornada completa",
        "work_position": "Mantenedor de código abierto",
        "work_end": "Actualidad",
        "work_achievements": (
            "Diseñé y construí CVLaTeX, un editor de CV local con 12 plantillas "
            "LaTeX, exportación a PDF/Word/LaTeX y sin cuenta ni nube.\n"
            "Añadí más de 900 pruebas automatizadas y CI para tres sistemas operativos; "
            "documenté convenciones de CV para seis mercados."
        ),
        "internship_position": "Becario de Ingeniería de Software",
        "internship_company": "Laboratorio de Ingeniería de Software de HUST",
        "internship_achievements": (
            "Desarrollé un proyecto de curso sobre APIs REST y bases de datos, "
            "con pruebas automatizadas y documentación técnica."
        ),
        "project1_name": "CVLaTeX",
        "project1_organization": "Proyecto personal",
        "project1_description": (
            "Editor de escritorio para crear CV con plantillas LaTeX, vista "
            "previa PDF, exportación a Word y LaTeX, autosave local y soporte "
            "para chino, español e inglés."
        ),
        "project1_result": "900+ tests, CI en 3 sistemas y licencia MIT",
        "university_project_name": "Taller de código abierto de HUST",
        "university_project_course": "Coordinador",
        "university_project_description": (
            "Coordiné talleres de Git y LaTeX para estudiantes de primero y "
            "segundo curso.\n"
            "Acompañé a 8 equipos en la publicación de sus primeros proyectos."
        ),
        "university_project_result": "40 estudiantes y 8 proyectos publicados",
        "degree": "Ingeniería de Software",
        "skill_languages": "Programación",
        "skill_tools": "Herramientas",
        "skill_other": "Otros",
        "skill_other_values": "Qt/QML, APIs REST, CI/CD",
        "language1": "Chino",
        "language1_level": "Nativo",
        "language2": "Inglés",
        "language2_level": "C1 — Avanzado",
        "language3": "Español",
        "language3_level": "B2 — Intermedio alto",
    },
    "en": {
        "name": "ELVIS ENRIQUE CHEN QIU",
        "profession": "Software Engineering student",
        "address": "Wuhan, Hubei, China",
        "summary": (
            "Software Engineering student at HUST (China), focused on "
            "cross-platform desktop applications, LaTeX tooling and open "
            "source. Creator of CVLaTeX, a local-first CV editor with 12 "
            "templates and PDF, Word and LaTeX export."
        ),
        "location_label": "Location",
        "location_value": "Wuhan, China",
        "availability_label": "Availability",
        "availability_value": "Internship / full time",
        "work_position": "Open-source maintainer",
        "work_end": "Present",
        "work_achievements": (
            "Designed and built CVLaTeX, a local-first CV editor with 12 LaTeX "
            "templates, PDF/Word/LaTeX export and no account or cloud.\n"
            "Added over 900 automated tests and a three-OS CI pipeline; documented "
            "CV conventions for six markets."
        ),
        "internship_position": "Software Engineering Intern",
        "internship_company": "HUST Software Engineering Laboratory",
        "internship_achievements": (
            "Built a course project around REST APIs and databases, with "
            "automated tests and technical documentation."
        ),
        "project1_name": "CVLaTeX",
        "project1_organization": "Personal project",
        "project1_description": (
            "Desktop editor that builds a CV from LaTeX templates, with PDF "
            "preview, Word and LaTeX export, local autosave and Chinese, "
            "Spanish and English support."
        ),
        "project1_result": "900+ tests, 3-OS CI and MIT license",
        "university_project_name": "HUST Open Source Workshop",
        "university_project_course": "Co-organizer",
        "university_project_description": (
            "Ran Git and LaTeX workshops for first- and second-year students.\n"
            "Supported 8 teams publishing their first projects."
        ),
        "university_project_result": "40 students and 8 published projects",
        "degree": "Software Engineering",
        "skill_languages": "Programming",
        "skill_tools": "Tools",
        "skill_other": "Other",
        "skill_other_values": "Qt/QML, REST APIs, CI/CD",
        "language1": "Chinese",
        "language1_level": "Native",
        "language2": "English",
        "language2_level": "C1 — Advanced",
        "language3": "Spanish",
        "language3_level": "B2 — Upper intermediate",
    },
    "zh": {
        "name": "陈昌发",
        "profession": "软件工程专业学生",
        "address": "中国湖北武汉",
        "summary": (
            "华中科技大学软件工程专业学生，专注于跨平台桌面应用、LaTeX 工具与"
            "开源项目。CVLaTeX 的作者：一款本地优先、内置 12 套模板并支持 "
            "PDF/Word/LaTeX 导出的简历编辑器。"
        ),
        "location_label": "所在地",
        "location_value": "中国武汉",
        "availability_label": "求职意向",
        "availability_value": "实习 / 全职",
        "work_position": "开源项目维护者",
        "work_end": "至今",
        "work_achievements": (
            "设计并开发 CVLaTeX：一款本地优先的简历编辑器，内置 12 套 LaTeX "
            "模板，支持 PDF/Word/LaTeX 导出，无需账号或云端。\n"
            "添加超过 900 个自动化测试和三平台 CI；为六个市场整理简历规范。"
        ),
        "internship_position": "软件工程实习生",
        "internship_company": "华中科技大学软件工程实验室",
        "internship_achievements": (
            "完成 REST API 与数据库课程项目，包含自动化测试和技术文档。"
        ),
        "project1_name": "CVLaTeX",
        "project1_organization": "个人项目",
        "project1_description": (
            "桌面简历编辑器：使用 LaTeX 模板生成简历，支持 PDF 预览、Word 与 "
            "LaTeX 导出、本地自动保存，以及中文、西班牙语和英语。"
        ),
        "project1_result": "900+ 个测试、三平台 CI、MIT 许可证",
        "university_project_name": "华中科技大学开源工作坊",
        "university_project_course": "组织者",
        "university_project_description": (
            "为大一、大二学生组织 Git 与 LaTeX 工作坊。\n"
            "指导 8 支队伍发布他们的第一个开源项目。"
        ),
        "university_project_result": "40 名学生、8 个项目",
        "degree": "软件工程",
        "skill_languages": "编程语言",
        "skill_tools": "工具",
        "skill_other": "其他",
        "skill_other_values": "Qt/QML、REST API、CI/CD",
        "language1": "中文",
        "language1_level": "母语",
        "language2": "英语",
        "language2_level": "C1 — 高级",
        "language3": "西班牙语",
        "language3_level": "B2 — 中高级",
    },
}


def _normalize_language(cv_language):
    """Return ``zh``, ``es`` or ``en``; fall back to ``es`` and never raise."""
    try:
        lang = str(cv_language or "es").strip().lower()
    except Exception:
        return "es"
    return lang if lang in _LANGUAGES else "es"


def _build_sample(lang):
    """Build the HUST software-engineering story with the text of ``lang``."""
    text = _TEXT[lang]
    university = _UNIVERSITY[lang]

    d = copy.deepcopy(latex_gen.empty_data())
    d["cv_language"] = lang
    d["template"] = "classic"
    d["name"] = text["name"]
    d["profession"] = text["profession"]
    d["email"] = _EMAIL
    d["phone"] = _PHONE
    d["address"] = text["address"]
    d["socials"] = copy.deepcopy(list(_SOCIALS))
    d["school_name"] = university

    d["extra_fields"] = [
        {"label": text["location_label"], "value": text["location_value"]},
        {"label": text["availability_label"], "value": text["availability_value"]},
    ]

    d["summary"] = text["summary"]

    d["work"] = [
        {
            "work_mode": "remote",
            "position": text["work_position"],
            "company": "CVLaTeX",
            "start": "2026",
            "end": text["work_end"],
            "achievements": text["work_achievements"],
            "logo": "",
        },
    ]

    d["internships"] = [
        {
            "work_mode": "onsite",
            "position": text["internship_position"],
            "company": text["internship_company"],
            "start": "2025",
            "end": "2025",
            "achievements": text["internship_achievements"],
            "logo": "",
        },
    ]

    d["projects"] = [
        {
            "name": text["project1_name"],
            "organization": text["project1_organization"],
            "start": "2026",
            "end": text["work_end"],
            "description": text["project1_description"],
            "result": text["project1_result"],
            "link": "github.com/ECHEQ/CVLaTeX",
            "logo": "",
        },
    ]

    d["university_projects"] = [
        {
            "name": text["university_project_name"],
            "course": text["university_project_course"],
            "organization": university,
            "start": "2025",
            "end": "2025",
            "description": text["university_project_description"],
            "result": text["university_project_result"],
            "link": "",
            "logo": "",
        },
    ]

    d["education"] = [
        {
            "degree_type": "bachelor",
            "degree": text["degree"],
            "institution": university,
            "start": "2022",
            "end": "2026",
            "grade": "",
            "logo": "",
        },
    ]

    d["skills"] = [
        {"category": text["skill_languages"], "values": "Python, Java, JavaScript, SQL"},
        {"category": text["skill_tools"], "values": "Git, Docker, Linux, LaTeX"},
        {"category": text["skill_other"], "values": text["skill_other_values"]},
    ]

    d["languages"] = [
        {"language": text["language1"], "level": text["language1_level"]},
        {"language": text["language2"], "level": text["language2_level"]},
        {"language": text["language3"], "level": text["language3_level"]},
    ]

    # One separator block so the sample also demonstrates the free dividers.
    d["blocks"] = [
        {
            "id": "sample-divider",
            "type": "separator",
            "style": "line",
            "position": "work",
        },
    ]

    return d


def sample_data(cv_language="es"):
    """Return the sample CV in ``cv_language`` (``zh``, ``es`` or ``en``)."""
    return _build_sample(_normalize_language(cv_language))


def sample_data_zh():
    """Return the Chinese sample CV (same story as the Spanish one)."""
    return sample_data("zh")


def sample_data_en():
    """Return the English sample CV (same story as the Spanish one)."""
    return sample_data("en")
