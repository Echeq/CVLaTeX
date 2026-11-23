# Changelog

All notable changes to CVLaTeX are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-11-23

### Fixed

- Tabbed now starts the logo/photo media column on the same row as the name.
- Blue ribbon keeps the blue band for the name only; logo and photo sit on the
  white area below it, next to the contacts.
- Creative shortens the red name plate to 0.68 text width when media is present,
  leaving the top-right column for the school logo and photo.
- Harvard uses a compact centred header and a smaller logo gap instead of the
  large blank strip above the name.
- The README demo is encoded at 720p/30 fps and opens in a real HTML5 video
  player on GitHub Pages (`docs/demo.html`); GitHub does not play repository
  MP4s inline. The original 1080p recording stays outside the repository.

## [1.0.0] - 2026-11-22

### Added

- Typography preferences: Serif/Sans/Monospace font style and 9/10/11/12/14 pt
  sizes in Settings. Both apply to the PDF, the Word export and the exported
  `.tex`; sizes outside 10/11/12 pt use `scrextend` when available and fall
  back to the nearest standard size.
- A **45-second demo video** (`docs/media/videos/demo-en.mp4`) and its poster
  image, linked from the README and the competition package.
- Market CV guides for the United States, United Kingdom, Spain, Latin
  America, China and Russia, with sources and image/video placeholders.
- Competition package (`docs/competition/`) and media conventions
  (`docs/media/`), plus six market summaries in `Help → Dedicated to each
  market`.
- A credits line that states the app is for students, recent graduates and
  professionals, with or without a university degree.
- `Add → Optional sections` can create the Social networks and Extra details
  cards on demand. A new CV no longer shows those empty cards by default; a
  hint points to Add and the sample CV. Saved CVs that use them keep them.
- `Add → CV sections` creates Profile, Education, Work, Internships, Projects,
  Campus activities, Skills, Languages and References. A new CV starts with
  Personal details only; empty sections stay hidden until added or filled.
- Added sections get an empty editable entry and focus their first field.
  Clicking a list/custom block row opens its editor directly; new blocks are
  scrolled into view, so the Edit button is no longer required.
- Section headers now include a confirmed **remove** action that clears the
  section content and hides it until it is added again.
- The Add menu is reorganized around the user's task: **Sections** first
  (including custom sections and list blocks), **Extras**, **Separators** and
  **Manage custom content**. The form's Custom content card is hidden until a
  block exists.
- The left form now switches to one field per row when the panel is narrow,
  gives the school-logo field the full row, groups the photo width/height
  controls, and uses a compact media card. Section spacing and labels were
  tightened so the panel reads as one column instead of a cramped grid.
- The school logo is now an optional letterhead mark above the name, with a
  selectable **left or right corner** and an adjustable **size in centimetres**
  (clamped to the media column/bar). A right-corner logo shares the reserved
  media column with the photo, so the name/contact text on the left keeps its
  position instead of being pushed by the logo. Choosing it opens a crop editor
  with a locked wide area (2:1, 3:1 or 4:1, default 3:1), so a long
  institutional logo stays long; the crop can be reopened with `Adjust area…`
  and the original image is kept in the project.
- The photo and the logo now start at the top margin, level with the name, and
  keep a clear vertical gap instead of leaving a blank strip above the image.
- **Harvard** is intentionally photo-free; the form hides the photo controls
  for that template and the PDF/Word exports ignore a saved photo.
- `Settings → Measurement units` switches the photo width/height fields between
  centimetres and inches while the document keeps using centimetres internally.
  The crop editor also offers photo shapes (Free, 1:1, 4:5, 3:4).
- The sample CV now uses the project's public identity (Elvis Enrique Chen Qiu
  / 陈昌发, HUST Software Engineering, GitHub/LinkedIn `ECHEQ`,
  `echeq@github.com`, fake phone `123-456-78`) and includes a free separator
  block.
- LaTeX engine diagnostics, a manual TinyTeX download/install-from-file path
  and an optional trusted download mirror.
- Security hardening for local data: CSP, `X-Frame-Options`,
  `Permissions-Policy` and `Cross-Origin-Resource-Policy` headers on the
  loopback server; 12 MB image and 50 MB `.cvjson` limits; PNG/JPEG magic-byte
  validation; and bounded embedded media (12 MB each, 64 MB total).
- TinyTeX downloads now verify official assets against SHA-256 digests pinned
  in the source, require `<url>.sha256` for custom mirrors and accept only
  HTTPS mirrors (including refusing HTTPS-to-HTTP redirects); a missing
  checksum aborts instead of warning.

### Changed

- The visible product name is back to **CVLaTeX** for presentation. The app
  data directory, window icons and `.tex` data markers now use `CVLaTeX`;
  existing `CVLaTex` prefs/autosave files and TinyTeX installs are migrated or
  detected on first run. Release archives from v1.0.0 use the `CVLaTeX` name;
  the pre-1.0 archives kept the historical `CVLaTex` spelling.
- The `Add` menu is grouped into Layout, Blocks and Optional sections, with
  block actions together instead of split across two sections.
- The preview bar has a simple **Vertical / Side by side** button that stacks
  the preview above the form and remembers the choice. The default is side by
  side; no automatic switching unless `Settings → Layout → Automatic` is
  selected. The stacked mode has a draggable horizontal divider and a remembered
  preview height. Automatic detection uses the real content box and
  `ResizeObserver`, and covers narrow half-screens (1280×1080).
- `Settings → LaTeX engine → Check` now scans the app folder, the legacy
  `CVLaTeX` folder, the usual TinyTeX/TeX Live/MiKTeX locations and `PATH`,
  saves the first working engine and shows a diagnostics panel on failure.

### Fixed

- The top menu buttons have larger hit targets, reducing misclicks after a
  window resize; the remaining offset on Hyprland is the compositor's known
  stale-pointer bug and is documented in Troubleshooting.
- TinyTeX installed outside the app's own folder (for example
  `%APPDATA%\TinyTeX`, `~/.TinyTeX`, `/Library/TeX/texbin` or a TeX Live
  install) is now detected instead of reported as missing.
- TinyTeX downloads resume after a dropped connection, retry, and fall back
  to a SourceForge mirror; a custom mirror can be configured for slow or
  blocked networks.
- A failed or corrupt TinyTeX extraction no longer deletes a working
  installation: the archive is validated in a staging folder and swapped
  atomically.
- The close guard and other modals no longer open underneath a stuck splitter
  drag veil in the vertical layout: pointer capture and blur/visibility
  handlers end the drag, and modals now sit above the veil with wrapping
  footers and focus on the primary button. In stacked/narrow windows the close
  guard stacks its three actions at full width with 38 px hit targets, which
  also mitigates Hyprland's stale-pointer offset after a surface resize.
- The initial CSP blocked pywebview's string-injected bridge, leaving the form
  blank and the preview stuck on “Loading”. The app document now allows
  `'unsafe-eval'` for that local bridge while still rejecting inline scripts.

### Known limitations

- The Windows and macOS bundles are **unsigned and not notarized**; Windows
  SmartScreen and macOS Gatekeeper may warn or block the first launch. Verify
  the SHA-256 checksum before running them.
- The Linux bundle needs WebKitGTK 4.1 and GObject introspection from the
  distribution; the macOS build is Apple Silicon only.
- PDF compile tests skip, rather than fail, when no `pdflatex`/`xelatex`
  engine is installed.
- Distribution is archive-based: no installer, package repository,
  auto-updater or universal macOS binary.

## [0.3.0] - 2026-11-06

Product rename from CVLaTeX to CVLaTex. The GitHub repository was already named
CVLaTex; this release aligns the application name, binaries, archives,
documentation and per-user data directory with it.

### Added

- Automatic migration of the old per-user data directory (`CVLaTeX`) to
  `CVLaTex` on first launch, preserving `prefs.json`, autosave, cache and the
  TinyTeX installation.
- `.tex` import keeps accepting the legacy `% CVLaTeX-DATA-BEGIN` /
  `% CVLaTeX-DATA-END` markers, while new exports use the `CVLaTex` markers.

### Changed

- Product name, window titles, credits, documentation, generated `.tex`
  comments and release assets now use `CVLaTex`.
- Binaries and archives are now `CVLaTex`, `CVLaTex.exe`, `CVLaTex.app` and
  `CVLaTex-v<version>-...`.
- Version bumped to 0.3.0.

### Fixed

- Existing `.cvjson` projects, `.tex` files with either marker spelling,
  preferences and TinyTeX installs keep working after the rename.

### Known limitations

- The Windows and macOS bundles are **unsigned and not notarized**. Windows
  SmartScreen and macOS Gatekeeper may warn or block the first launch; verify
  the SHA-256 checksum before deciding to run them.
- The Linux bundle needs WebKitGTK 4.1 and GObject introspection from the
  distribution (`python3-gi`, `gir1.2-webkit2-4.1` on Debian/Ubuntu; the
  `-dev` package is additionally required to build). Keep the executable bit.
- PDF compile tests skip, rather than fail, when no `pdflatex`/`xelatex`
  engine is installed; Word and `.tex` export and the schema/round-trip tests
  always run.
- Distribution is archive-based: a `.exe` on Windows, a bare executable on
  Linux and a `.zip` containing `CVLaTex.app` on macOS. There is no installer,
  package repository, auto-updater or universal macOS binary.

## [0.2.1] - 2026-11-06

Bug-fix release for the Linux bundle. v0.2.0 shipped a Linux executable that
exited immediately with `ModuleNotFoundError: No module named '_struct'`; this
release rebuilds it with a consistent Python installation and adds a bootstrap
smoke test to the release pipelines.

### Added

- Linux bundle bootstrap smoke test in the build and release workflows: the
  built executable is started once and the job fails if PyInstaller reports a
  missing module or a NULL bootstrap module.

### Changed

- The Linux build now clears an ambient `LD_LIBRARY_PATH` before creating the
  venv and running PyInstaller, so the standard library and the bundled
  `libpython` come from the same Python installation.

### Fixed

- Linux releases no longer fail at startup with
  `ModuleNotFoundError: No module named '_struct'` when CI's `setup-python`
  exposes its own `libpython`. The distro Python has `_struct` built in, so
  PyInstaller could omit it while bundling the action toolcache `libpython`.

### Known limitations

- The Windows and macOS bundles are **unsigned and not notarized**. Windows
  SmartScreen and macOS Gatekeeper may warn or block the first launch; verify
  the SHA-256 checksum before deciding to run them.
- The Linux bundle needs WebKitGTK 4.1 and GObject introspection from the
  distribution (`python3-gi`, `gir1.2-webkit2-4.1` on Debian/Ubuntu; the
  `-dev` package is additionally required to build). Keep the executable bit.
- PDF compile tests skip, rather than fail, when no `pdflatex`/`xelatex`
  engine is installed; Word and `.tex` export and the schema/round-trip tests
  always run.
- Distribution is archive-based: a `.exe` on Windows, a bare executable on
  Linux and a `.zip` containing `CVLaTex.app` on macOS. There is no installer,
  package repository, auto-updater or universal macOS binary.

## [0.2.0] - 2026-10-26

Second release and the first public pre-release assembled by CI: v0.1.0 was a manual upload, while v0.2.0 is built and published from a `v0.2.0` tag. Every bundle carries all 12 templates, the web assets and the vendored PDF.js viewer.

### Added

- Sword template: a Chinese-style layout with a slanted navy name banner, a two-column contact grid with personal data on the left and profile links on the right (no row hairlines), and navy section plates over gray bars. The shipped template set is now 12: Classic, Harvard, Modern, Creative, Chinese (standard), Sidebar (left), Sidebar (right), Black tabs, Blue ribbon, Navy minimal, Playful and Sword.
- Release staging via `tools/stage_assets.py`: only `web/` and the twelve templates' `.tex` files enter the bundle, so personal reference files never ship.
- Release packaging via `tools/package_release.py`: versioned `.zip`/`.tar.gz` archives that include `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`, `CHANGELOG.md` and `SECURITY.md` next to the binary or `.app` bundle, with a printed entry listing for verification.
- `tools/windows_version.py` generates the PyInstaller Windows version resource from `version.py`.
- A tag-driven release workflow that tests, builds the three native archives, checks their contents and checksums, and publishes them as a GitHub pre-release.

### Changed

- CV headers now show the person's name instead of the redundant document title, and long names auto-fit their banner or column.
- The default body order is now education-first: Education, Profile, Work, Internships, Projects, Campus activities, Skills & certificates, Languages, References. Personal data comes before the job objective and the profile links in both PDF and Word, and the `university_projects` / `skills` labels are now Campus activities and Skills & certificates.
- The Word export now renders a per-template layout instead of one generic document: Classic, Harvard, Modern, Creative, Chinese, Sidebar (left), Sidebar (right), Black tabs, Blue ribbon, Navy minimal, Playful and Sword each get their matching header, section-heading shape, entry line, bullet marker, separators and palette, with preferences overriding the template colors.
- Word export honours the 1–3 columns of the five entry-list sections in the Latin templates; the Chinese-style templates keep their three-column entries and ignore that setting, as in the PDF.
- The built-in sample CVs are now clearly fictional in all three languages (Alejandro Ruiz Martín, `alex.ruiz@example.com`, `github.com/example`, Madrid), with the same career story, dates and entry counts as before.

### Fixed

- Release builds no longer bundle the author's reference CV (`templates/chinese/Elvis Chen CV.docx`) or `templates/picture samples/`; the staging step copies template `.tex` files explicitly.
- The Windows deployment is a `.zip` containing `CVLaTex.exe`, the Linux one is a `.tar.gz` containing the executable with its mode preserved, and the macOS one is a `.zip` containing `CVLaTex.app`.

### Known limitations

- The Windows and macOS bundles are **unsigned and not notarized**. Windows SmartScreen and macOS Gatekeeper may warn or block the first launch; verify the SHA-256 checksum before deciding to run them. Code signing and notarization are deferred to a later release.
- The Linux bundle needs WebKitGTK 4.1 and GObject introspection from the distribution (`python3-gi`, `gir1.2-webkit2-4.1` on Debian/Ubuntu; the `-dev` package is additionally required to build). Keep the executable bit.
- PDF compile tests skip, rather than fail, when no `pdflatex`/`xelatex` engine is installed; Word and `.tex` export and the schema/round-trip tests always run.
- Distribution is archive-based: a `.zip` containing `CVLaTex.exe` on Windows, a `.tar.gz` containing a bare executable on Linux and a `.zip` containing `CVLaTex.app` on macOS. There is no installer, package repository, auto-updater or universal macOS binary.
- Word export approximates the PDF instead of reproducing it pixel for pixel. Its shapes use no DrawingML or VML and nothing is rotated, so the Sword blade tip and the Blue ribbon wing are stair-stepped; the Sidebar bar starts at the top margin (not the paper edge) and continues on later pages, while the PDF draws it on page 1 only. Cambria, Calibri and Microsoft YaHei are requested explicitly and are substituted when the machine lacks them.

## [0.1.0] - 2026-10-22

First public pre-release. CVLaTex is a cross-platform desktop CV editor for
Windows, Linux and macOS: a local form, LaTeX templates and a compiled preview,
with no account and no server.

### Added

- Desktop editor built on Python, pywebview and a local HTTP server, with a
  form on the left and a live PDF preview on the right.
- 11 LaTeX templates: Classic, Harvard, Modern, Creative, Chinese (standard),
  Sidebar (left), Sidebar (right), Black tabs, Blue ribbon, Navy minimal and
  Playful, grouped as ATS Friendly, Chinese styles and Normal CV.
- Localized sample CVs in Spanish, English and Chinese that tell the same
  career story, independent of the selected template.
- PDF preview through the native webview on Windows and macOS, and through the
  vendored PDF.js 3.11.174 viewer on Linux; a system-viewer fallback is offered
  when PDF.js cannot render.
- PDF export with `pdflatex`/`xelatex`; Word (`.docx`) export with python-docx
  and LaTeX (`.tex`) export with an embedded data block, both without a LaTeX
  engine.
- LaTeX import from CVLaTex-generated `.tex` files; foreign files are rejected
  instead of parsed heuristically.
- `.cvjson` v3 project files with embedded photo and logos; v1/v2 files are
  migrated after writing a `.v2.bak` backup.
- Autosave with recovery on the next start, and a close guard with Save / Exit
  without saving / Cancel when the document has unsaved changes.
- First-run UI language picker (Spanish, English, Chinese, Russian) before the
  LaTeX setup wizard, and a separate per-CV document language.
- TinyTeX download and installation from the setup wizard, cancelable and
  checksum-verified when the release publishes a checksum.
- Free blocks (columns, period + description, separator line, color band,
  blank space, custom section) interleaved with the standard sections.
- Document color palette (primary, secondary, text, gray) affecting PDF, Word
  and `.tex` output.
- Photo and logo normalization, with a crop editor and re-editable crop.
- Debounced automatic compilation and a latest-only compile queue: a burst of
  edits produces one compile, and requests made while a compile is running
  collapse into a single follow-up instead of queueing in parallel.

### Changed

- Sidebar and Sidebar (right) draw the accent bar and reserve the 7 cm margin
  only on the first page; later pages use the configured margins and the full
  text width.

### Fixed

- Non-ASCII text in async bridge pushes no longer truncates or drops the
  script in the WebKitGTK backend (`ensure_ascii=True` is kept on every push).
- Linux PDF preview fallback when PDF.js fails to load or render.

### Known limitations

- The Windows and macOS bundles are **unsigned and not notarized**. Windows
  SmartScreen and macOS Gatekeeper may warn or block the first launch; verify
  the SHA-256 checksum before deciding to run them.
- The Linux bundle needs WebKitGTK 4.1 and GObject introspection from the
  distribution (`python3-gi`, `gir1.2-webkit2-4.1` on Debian/Ubuntu; the
  `-dev` package is additionally required to build). Keep the executable bit.
- PDF compile tests skip, rather than fail, when no `pdflatex`/`xelatex` engine
  is installed; Word and `.tex` export and the schema/round-trip tests always
  run.
- Distribution is archive-based: a `.exe` on Windows, a bare executable on
  Linux and a `.zip` containing `CVLaTex.app` on macOS. There is no installer,
  package repository, auto-updater or universal macOS binary.

[1.0.1]: https://github.com/Echeq/CVLaTex/releases/tag/v1.0.1
[1.0.0]: https://github.com/Echeq/CVLaTex/releases/tag/v1.0.0
[0.3.0]: https://github.com/Echeq/CVLaTex/releases/tag/v0.3.0
[0.2.1]: https://github.com/Echeq/CVLaTex/releases/tag/v0.2.1
[0.2.0]: https://github.com/Echeq/CVLaTex/releases/tag/v0.2.0
[0.1.0]: https://github.com/Echeq/CVLaTex/releases/tag/v0.1.0
