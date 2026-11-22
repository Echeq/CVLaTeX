import glob
import hashlib
import http.client
import os
import platform as _platform
import shutil
import socket
import subprocess
import sys
import tarfile
import threading
import time
import urllib.error
import urllib.request
import uuid
import zipfile
from urllib.parse import urlsplit

import messages
import prefs

TINYTEX_VERSION = "2026.08"
_TINYTEX_RELEASE = (
    f"https://github.com/rstudio/tinytex-releases/releases/download/v{TINYTEX_VERSION}"
)


def _tinyttex_bin_dirs(platform=None, machine=None):
    """Candidate bin dirs inside TINYTEX_DIR for `platform`, best first.

    Windows: bin/windows. macOS: bin/universal-darwin. Linux: the native
    architecture first (bin/aarch64-linux on arm64, bin/x86_64-linux
    otherwise) and the other one as fallback.
    """
    platform = sys.platform if platform is None else platform
    if platform == "win32":
        return ["bin/windows"]
    if platform == "darwin":
        return ["bin/universal-darwin"]
    arch = str(machine if machine is not None else _platform.machine()).lower()
    if arch in ("aarch64", "arm64"):
        return ["bin/aarch64-linux", "bin/x86_64-linux"]
    return ["bin/x86_64-linux", "bin/aarch64-linux"]


def _engine_exe(name, platform=None):
    """Executable file name of a TeX engine on `platform`."""
    platform = sys.platform if platform is None else platform
    return name + ".exe" if platform == "win32" else name


def _engine_path(root, relative, name, platform=None):
    """Native path of the engine `name` inside `root/<relative>`."""
    return os.path.join(
        root, *relative.replace("\\", "/").split("/"), _engine_exe(name, platform)
    )


def _archive_kind(platform=None):
    """Archive type of the TinyTeX asset for `platform` ("zip" or "tar")."""
    platform = sys.platform if platform is None else platform
    return "zip" if platform == "win32" else "tar"


# TinyTeX assets pinned for TINYTEX_VERSION, verified against the GitHub API
# for v2026.08: the Windows .zip keeps the historical name; Linux uses the
# x86_64 .tar.gz (root .TinyTeX, bin/x86_64-linux) and macOS the universal
# .tgz (root TinyTeX, bin/universal-darwin).
TINYTEX_URLS_BY_PLATFORM = {
    "win32": [f"{_TINYTEX_RELEASE}/TinyTeX-v{TINYTEX_VERSION}.zip"],
    "darwin": [f"{_TINYTEX_RELEASE}/TinyTeX-v{TINYTEX_VERSION}.tgz"],
    "linux": [f"{_TINYTEX_RELEASE}/TinyTeX-v{TINYTEX_VERSION}.tar.gz"],
}
TINYTEX_URLS = list(
    TINYTEX_URLS_BY_PLATFORM.get(sys.platform, TINYTEX_URLS_BY_PLATFORM["linux"])
)
# SourceForge mirrors the same releases and is usually reachable when GitHub
# is slow or blocked (notably from mainland China). It is tried only after the
# official asset and is verified against the same pinned SHA-256 digest.
_SOURCEFORGE_MIRROR = (
    "https://downloads.sourceforge.net/project/tinytex-releases.mirror/v%s"
    % TINYTEX_VERSION
)
TINYTEX_MIRROR_URLS_BY_PLATFORM = {
    "win32": [f"{_SOURCEFORGE_MIRROR}/TinyTeX-v{TINYTEX_VERSION}.zip"],
    "darwin": [f"{_SOURCEFORGE_MIRROR}/TinyTeX-v{TINYTEX_VERSION}.tgz"],
    "linux": [f"{_SOURCEFORGE_MIRROR}/TinyTeX-v{TINYTEX_VERSION}.tar.gz"],
}
TINYTEX_MIRROR_URLS = list(
    TINYTEX_MIRROR_URLS_BY_PLATFORM.get(
        sys.platform, TINYTEX_MIRROR_URLS_BY_PLATFORM["linux"]
    )
)
# SHA-256 of the exact assets published for TINYTEX_VERSION (GitHub API
# `digest` field). Pinning them means the installer does not trust a checksum
# served next to the archive: a compromised or truncated download always
# aborts, and the official/SourceForge assets never need a second request.
TINYTEX_SHA256_BY_ASSET = {
    f"TinyTeX-v{TINYTEX_VERSION}.zip": (
        "313314cdf15ad94e78931f6eff9bfc978f233ece7e5877f26467afe0b40f377b"
    ),
    f"TinyTeX-v{TINYTEX_VERSION}.tgz": (
        "c1e6ee0474300c72395647aa93aca0ea4bb600192e9a22bf539d57a583acb5c5"
    ),
    f"TinyTeX-v{TINYTEX_VERSION}.tar.gz": (
        "6f39005ce5c60863698793481352df75c051980b68a47726d49be9a00a377767"
    ),
}
TINYTEX_RELEASES_PAGE = (
    "https://github.com/rstudio/tinytex-releases/releases/tag/v%s" % TINYTEX_VERSION
)
ALLOWED_PHOTOS = {".jpg", ".jpeg", ".png"}
_LOCK = threading.Lock()
_SUBPROCESS_FLAGS = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW: no console window


class LatexError(Exception):
    pass


class DownloadError(LatexError):
    """Transient network failure; the installer may try the next mirror."""


def _check(path):
    try:
        result = subprocess.run(
            [path, "-version"],
            capture_output=True,
            timeout=20,
            creationflags=_SUBPROCESS_FLAGS,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _common_engine_paths(platform=None):
    """pdflatex paths of the usual manual TinyTeX/TeX Live/MiKTeX installs.

    GUI applications do not always inherit the shell PATH, especially on macOS
    and Windows, and a user may have installed TinyTeX outside the app's own
    data directory. These are the documented/default locations.
    """
    platform = sys.platform if platform is None else platform
    home = os.path.expanduser("~")
    exe = _engine_exe("pdflatex", platform)
    if platform == "win32":
        appdata = os.environ.get("APPDATA")
        localappdata = os.environ.get("LOCALAPPDATA")
        if appdata:
            yield os.path.join(appdata, "TinyTeX", "bin", "windows", exe)
        if localappdata:
            yield os.path.join(localappdata, "TinyTeX", "bin", "windows", exe)
            yield os.path.join(
                localappdata, "Programs", "TinyTeX", "bin", "windows", exe
            )
            yield from glob.glob(
                os.path.join(
                    localappdata, "Programs", "MiKTeX", "miktex", "bin", "*", exe
                )
            )
        yield os.path.join("C:\\", "TinyTeX", "bin", "windows", exe)
        yield os.path.join(
            "C:\\", "Program Files", "MiKTeX", "miktex", "bin", "x64", exe
        )
        yield from glob.glob(os.path.join("C:\\", "texlive", "*", "bin", "windows", exe))
    elif platform == "darwin":
        yield os.path.join(
            home, "Library", "TinyTeX", "bin", "universal-darwin", exe
        )
        yield os.path.join(
            home, "Library", "TinyTeX", "TinyTeX", "bin", "universal-darwin", exe
        )
        yield os.path.join("/Library", "TeX", "texbin", exe)
        yield os.path.join("/opt", "local", "bin", exe)
        yield os.path.join("/usr", "local", "bin", exe)
        yield from glob.glob(
            os.path.join("/usr", "local", "texlive", "*", "bin", "universal-darwin", exe)
        )
    else:
        yield os.path.join(home, ".TinyTeX", "bin", "x86_64-linux", exe)
        yield os.path.join(home, ".TinyTeX", "bin", "aarch64-linux", exe)
        yield os.path.join(home, "TinyTeX", "bin", "x86_64-linux", exe)
        yield from glob.glob(os.path.join(home, ".TinyTeX", "bin", "*", exe))
        yield os.path.join("/usr", "bin", exe)
        yield os.path.join("/usr", "local", "bin", exe)
        yield from glob.glob(os.path.join("/usr", "local", "texlive", "*", "bin", "*", exe))
        yield from glob.glob(os.path.join("/opt", "texlive", "*", "bin", "*", exe))


def _default_engine_roots():
    """Default app dirs, for a TinyTeX left behind by a redirected APP_DIR."""
    default = prefs.default_app_dir()
    current = os.path.abspath(default)
    legacy = os.path.join(os.path.dirname(current), prefs.LEGACY_APP_NAME)
    return [os.path.join(current, "tinytex"), os.path.join(legacy, "tinytex")]


def _candidate_paths(platform=None):
    """Every pdflatex candidate, best first, without duplicates."""
    platform = sys.platform if platform is None else platform
    seen = set()

    def emit(path):
        if not path:
            return
        key = os.path.normcase(os.path.abspath(path))
        if key in seen:
            return
        seen.add(key)
        yield path

    preferred = prefs.get("latex_path")
    if preferred:
        yield from emit(preferred)
    for root in (prefs.TINYTEX_DIR, os.path.join(prefs.legacy_app_dir(), "tinytex")):
        for relative in _tinyttex_bin_dirs(platform):
            yield from emit(_engine_path(root, relative, "pdflatex", platform))
    for path in _common_engine_paths(platform):
        yield from emit(path)
    for root in _default_engine_roots():
        for relative in _tinyttex_bin_dirs(platform):
            yield from emit(_engine_path(root, relative, "pdflatex", platform))
    for name in ("pdflatex", "pdflatex.exe"):
        found = shutil.which(name)
        if found:
            yield from emit(found)


_LAST_ENGINE = None


def reset_engine_cache():
    """Forget the resolved engine after a path change or a new install."""
    global _LAST_ENGINE
    _LAST_ENGINE = None


def find_pdflatex(platform=None):
    """Resolve pdflatex once; explicit-platform calls are for tests/diagnostics."""
    global _LAST_ENGINE
    if platform is None and _LAST_ENGINE:
        if os.path.isfile(_LAST_ENGINE) and _check(_LAST_ENGINE):
            return _LAST_ENGINE
        _LAST_ENGINE = None
    for path in _candidate_paths(platform):
        if os.path.isfile(path) and _check(path):
            if platform is None:
                _LAST_ENGINE = path
            return path
    return None


def pdflatex_diagnostics(platform=None):
    """Paths checked when detection fails; never runs the engine."""
    platform = sys.platform if platform is None else platform
    candidates = []
    for path in _candidate_paths(platform):
        candidates.append({"path": path, "exists": os.path.isfile(path)})
    return {
        "platform": platform,
        "prefs_path": prefs.get("latex_path"),
        "tinytex_dir": prefs.TINYTEX_DIR,
        "legacy_tinytex_dir": os.path.join(prefs.legacy_app_dir(), "tinytex"),
        "which": shutil.which("pdflatex"),
        "candidates": candidates[:30],
    }


def _raise_if_cancelled(cancel_event):
    """Abort with a localized error when the install was cancelled."""
    if cancel_event is not None and cancel_event.is_set():
        raise LatexError(messages.t("install_cancelled"))


def _tinytex_urls():
    """Download order: custom mirror, official asset, SourceForge fallback.

    Only HTTPS mirrors are accepted: the archive ends up executing `pdflatex`,
    so a plain-HTTP URL is ignored instead of silently downgrading transport.
    """
    urls = []
    custom = str(prefs.get("tinytex_url") or "").strip()
    if custom.lower().startswith("https://"):
        urls.append(custom)
    urls.extend(TINYTEX_URLS)
    urls.extend(TINYTEX_MIRROR_URLS)
    seen = set()
    ordered = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            ordered.append(url)
    return ordered


def _pinned_checksum(url):
    """Pinned SHA-256 for an official/mirror asset name, or None.

    The asset file name is the key, so a custom mirror that serves the same
    release file is verified against the same published digest.
    """
    name = str(url or "").split("?", 1)[0].rsplit("/", 1)[-1]
    return TINYTEX_SHA256_BY_ASSET.get(name)


def _download_once(url, part, progress, cancel_event=None):
    """One HTTP attempt; resumes from ``part`` with a Range request."""
    existing = os.path.getsize(part) if os.path.isfile(part) else 0
    headers = {"User-Agent": "CVLaTeX/1.0"}
    if existing:
        headers["Range"] = "bytes=%d-" % existing
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            # A HTTPS URL can still redirect to plain HTTP. The archive runs
            # pdflatex later, so refuse the downgrade instead of downloading it.
            if urlsplit(response.geturl() or url).scheme.lower() != "https":
                raise DownloadError(messages.t("install_insecure_mirror"))
            status = getattr(response, "status", 200)
            if existing and status != 206:
                # The server ignored the Range header: start over.
                existing = 0
            total = existing + int(response.headers.get("Content-Length") or 0)
            if total and existing >= total:
                return
            done = existing
            if total:
                progress(done, total)
            mode = "ab" if existing else "wb"
            with open(part, mode) as f:
                while True:
                    _raise_if_cancelled(cancel_event)
                    chunk = response.read(256 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    f.flush()
                    done += len(chunk)
                    progress(done, total or None)
            if total and done < total:
                raise DownloadError(messages.t("install_connection_error"))
    except DownloadError:
        raise
    except urllib.error.HTTPError as e:
        if e.code == 416 and existing:
            try:
                os.remove(part)
            except OSError:
                pass
            raise DownloadError(messages.t("install_connection_error")) from e
        raise DownloadError(messages.t("install_download_error").format(error=e)) from e
    except (
        urllib.error.URLError,
        http.client.HTTPException,
        socket.timeout,
        TimeoutError,
        ConnectionError,
        OSError,
    ) as e:
        raise DownloadError(messages.t("install_download_error").format(error=e)) from e


def _download(url, destination, progress, cancel_event=None, attempts=2):
    """Download with resume, URL marker and bounded retries.

    A partial file survives a network failure so a retry (or a later run) can
    continue with ``Range``. The marker prevents resuming a partial file from a
    different mirror.
    """
    part = destination + ".part"
    marker = destination + ".url"
    try:
        with open(marker, "r", encoding="utf-8") as f:
            previous = f.read().strip()
    except OSError:
        previous = ""
    if previous and previous != url:
        for path in (part, marker):
            try:
                os.remove(path)
            except OSError:
                pass
    try:
        os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
        with open(marker, "w", encoding="utf-8") as f:
            f.write(url)
    except OSError:
        pass

    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            _download_once(url, part, progress, cancel_event)
            os.replace(part, destination)
            try:
                os.remove(marker)
            except OSError:
                pass
            return
        except DownloadError as e:
            last_error = e
            _raise_if_cancelled(cancel_event)
            if attempt < attempts:
                time.sleep(min(2 ** attempt, 8))
    raise last_error or DownloadError(messages.t("install_connection_error"))


def _sha256_file(path):
    """Hex SHA-256 digest of a local file."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_checksum(text):
    """First 64-character hex token of a .sha256 payload, or None."""
    for token in str(text or "").split():
        token = token.strip().lower()
        if len(token) == 64 and all(c in "0123456789abcdef" for c in token):
            return token
    return None


def verify_sha256(path, expected):
    """Verify that `path` has the SHA-256 digest `expected`.

    A missing/unnamed checksum or a mismatch raises LatexError with a
    localized message; a match returns True.
    """
    digest = _parse_checksum(expected)
    if not digest:
        raise LatexError(messages.t("install_checksum_unavailable"))
    if _sha256_file(path).lower() != digest:
        raise LatexError(messages.t("install_checksum_mismatch"))
    return True


def _fetch_checksum(url, cancel_event=None):
    """Best-effort download of `<url>.sha256`: digest or None.

    Some tinytex-releases assets have no `.sha256` sibling (they 404): a
    missing, unreachable or unparseable checksum returns None so the caller
    can continue the install with a warning instead of aborting. A cancelled
    install still raises the localized LatexError.
    """
    request = urllib.request.Request(url, headers={"User-Agent": "CVLaTeX/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            text = response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError, ValueError):
        return None
    _raise_if_cancelled(cancel_event)
    return _parse_checksum(text)


def _extract_zip(archive_path, staging, progress):
    with zipfile.ZipFile(archive_path) as zf:
        infos = zf.infolist()
        total = sum(i.file_size for i in infos) or 1
        done = 0
        progress(0, total if total > 1 else None)
        for info in infos:
            zf.extract(info, staging)
            done += info.file_size
            progress(done, total)


def _tar_extract_member(tf, member, staging):
    """Extract one tar member; `filter="data"` on Python 3.12+."""
    try:
        tf.extract(member, staging, filter="data")
    except TypeError:
        # Python without extraction filters (no `filter` kwarg).
        tf.extract(member, staging)


def _extract_tar(archive_path, staging, progress):
    with tarfile.open(archive_path, "r:*") as tf:
        members = tf.getmembers()
        total = sum(m.size for m in members) or 1
        done = 0
        progress(0, total if total > 1 else None)
        for member in members:
            _tar_extract_member(tf, member, staging)
            done += member.size
            progress(done, total)


def _find_extracted_pdflatex(root, platform):
    for relative in _tinyttex_bin_dirs(platform):
        candidate = _engine_path(root, relative, "pdflatex", platform)
        if os.path.isfile(candidate):
            return relative
    return None


def _extract_archive(archive_path, progress, platform=None):
    """Extract and validate into a staging dir, then swap atomically.

    The previous installation is only moved aside after the new tree contains
    a usable pdflatex. A corrupt archive therefore leaves the old TinyTeX
    untouched, and a failed swap restores it.
    """
    platform = sys.platform if platform is None else platform
    staging = prefs.TINYTEX_DIR + ".tmp"
    previous = prefs.TINYTEX_DIR + ".old"
    if os.path.exists(staging):
        shutil.rmtree(staging, ignore_errors=True)
    os.makedirs(staging)
    try:
        # Manual installs may choose either archive format regardless of OS.
        if zipfile.is_zipfile(archive_path):
            _extract_zip(archive_path, staging, progress)
        else:
            _extract_tar(archive_path, staging, progress)
        directories = [
            d
            for d in os.listdir(staging)
            if os.path.isdir(os.path.join(staging, d))
        ]
        root = staging
        if len(directories) == 1:
            root = os.path.join(staging, directories[0])
        relative = _find_extracted_pdflatex(root, platform)
        if relative is None:
            raise LatexError(messages.t("install_invalid_zip"))

        if os.path.exists(previous):
            if os.path.isdir(previous):
                shutil.rmtree(previous)
            else:
                os.remove(previous)
        if os.path.exists(prefs.TINYTEX_DIR):
            shutil.move(prefs.TINYTEX_DIR, previous)
        try:
            os.makedirs(prefs.TINYTEX_DIR)
            for name in os.listdir(root):
                shutil.move(os.path.join(root, name), prefs.TINYTEX_DIR)
        except OSError:
            shutil.rmtree(prefs.TINYTEX_DIR, ignore_errors=True)
            if os.path.exists(previous):
                shutil.move(previous, prefs.TINYTEX_DIR)
            raise
        shutil.rmtree(previous, ignore_errors=True)
    except LatexError:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    except (zipfile.BadZipFile, tarfile.TarError, EOFError, OSError) as e:
        shutil.rmtree(staging, ignore_errors=True)
        raise LatexError(messages.t("install_unzip_error").format(error=e)) from e
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return _engine_path(prefs.TINYTEX_DIR, relative, "pdflatex", platform)


def install_from_archive(archive_path, progress, cancel_event=None, warn=None):
    """Install TinyTeX from a local .zip/.tar.gz/.tgz/.tar.xz archive."""
    _raise_if_cancelled(cancel_event)
    if not archive_path or not os.path.isfile(archive_path):
        raise LatexError(messages.t("install_archive_missing"))
    pdflatex = _extract_archive(archive_path, progress)
    _raise_if_cancelled(cancel_event)
    if not pdflatex or not _check(pdflatex):
        raise LatexError(messages.t("install_broken"))
    prefs.set("latex_path", pdflatex)
    reset_engine_cache()
    return pdflatex


def install_tinytex(progress, cancel_event=None, warn=None):
    """Download and install TinyTeX. progress(done, total), total None if unknown.

    Pass a ``threading.Event`` as ``cancel_event`` to abort promptly: the
    download loop checks it on every chunk and it is checked again before
    extraction. Aborting raises LatexError with a localized message.

    ``warn(message)`` (optional) receives localized warnings that do not stop
    the install. SHA-256 policy: official and SourceForge assets are verified
    against digests pinned in ``TINYTEX_SHA256_BY_ASSET``; a custom mirror must
    publish ``<url>.sha256``. A missing checksum aborts the install, and a
    mismatch always aborts. Only HTTPS mirrors are used.
    """
    _raise_if_cancelled(cancel_event)
    custom = str(prefs.get("tinytex_url") or "").strip()
    if custom and not custom.lower().startswith("https://") and warn is not None:
        warn(messages.t("install_insecure_mirror"))
    os.makedirs(prefs.APP_DIR, exist_ok=True)
    tmp = os.path.join(prefs.APP_DIR, "tinytex-download")
    last_download_error = None
    success = False
    try:
        for url in _tinytex_urls():
            progress(0, None)
            try:
                _download(url, tmp, progress, cancel_event)
            except DownloadError as e:
                # Slow/blocked host: keep the partial file for a resume and
                # try the next source (custom mirror, GitHub, SourceForge).
                last_download_error = e
                continue
            _raise_if_cancelled(cancel_event)
            try:
                expected = _pinned_checksum(url)
                if expected is None:
                    expected = _fetch_checksum(url + ".sha256", cancel_event)
                if expected is None:
                    raise LatexError(messages.t("install_checksum_unavailable"))
                verify_sha256(tmp, expected)
                pdflatex = install_from_archive(tmp, progress, cancel_event, warn)
            except LatexError:
                # A bad archive/checksum must not be retried from another URL.
                try:
                    os.remove(tmp)
                except OSError:
                    pass
                raise
            success = True
            return pdflatex
        raise last_download_error or DownloadError(
            messages.t("install_connection_error")
        )
    finally:
        if success and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def _read_log(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def _parse_errors(log):
    lines = log.splitlines()
    errors = []
    for i, line in enumerate(lines):
        if not line.startswith("!"):
            continue
        message = line[2:].strip()
        if "not found" in message:
            start = message.find("`")
            end = message.find("'", start)
            name = message[start + 1:end] if start != -1 and end != -1 else ""
            suffix = f" ({name})" if name else ""
            errors.append(messages.t("compile_missing_package").format(package=suffix))
            continue
        context = []
        for j in range(i + 1, min(i + 6, len(lines))):
            if lines[j].startswith("!"):
                break
            if not lines[j].strip():
                continue
            context.append(lines[j].strip())
            if "l." in lines[j]:
                break
        detail = " | ".join(context[:3])
        errors.append(f"{message} ({detail})" if detail else message)
    if not errors:
        if "Emergency stop" in log:
            errors.append(messages.t("compile_emergency_stop"))
        elif "Fatal error" in log:
            errors.append(messages.t("compile_fatal_error"))
        elif "File ended while scanning" in log:
            errors.append(messages.t("compile_unclosed_brace"))
    return errors[:25]


def find_xelatex(platform=None):
    platform = sys.platform if platform is None else platform
    path = find_pdflatex(platform)
    if path:
        candidate = os.path.join(os.path.dirname(path), _engine_exe("xelatex", platform))
        if os.path.isfile(candidate):
            return candidate
    return shutil.which("xelatex")


_CJK_RE = None
_FONTSPEC_RE = None


def _uses_xelatex(tex):
    """True when the document must be compiled with XeLaTeX.

    XeLaTeX is required for CJK text, but also for any document that loads
    `fontspec`: pdflatex aborts on it with "fontspec requires XeTeX or
    LuaTeX" even when the document has no CJK glyph at all (e.g. an empty
    CV whose zh font_engine emits fontspec).
    """
    global _CJK_RE, _FONTSPEC_RE
    if _CJK_RE is None:
        import re

        _CJK_RE = re.compile(
            "[\u4e00-\u9fff\uff00-\uffef\u3040-\u30ff\uac00-\ud7af\uf900-\ufaff]"
        )
        _FONTSPEC_RE = re.compile(
            r"\\usepackage\s*(?:\[[^\]]*\])?\s*\{fontspec\}|\\fontspec"
        )
    return bool(_CJK_RE.search(tex)) or bool(_FONTSPEC_RE.search(tex))


def compile(tex, photo=None, extras=None):
    pdflatex = find_pdflatex()
    if not pdflatex:
        return {
            "ok": False,
            "pdf": None,
            "errores": [messages.t("compile_no_engine")],
        }
    needs_xelatex = _uses_xelatex(tex)
    engine = find_xelatex() if needs_xelatex else pdflatex
    if needs_xelatex and not engine:
        return {
            "ok": False,
            "pdf": None,
            "errores": [messages.t("compile_needs_xelatex")],
        }
    with _LOCK:
        return _compile_unlocked(engine, tex, photo, extras)


def _copy_stable_pdf(source):
    """Copy the PDF to CACHE_DIR/out so exporting does not race the next compile."""
    destination_dir = os.path.join(prefs.CACHE_DIR, "out")
    os.makedirs(destination_dir, exist_ok=True)
    destination = os.path.join(destination_dir, "result_" + uuid.uuid4().hex + ".pdf")
    try:
        shutil.copy2(source, destination)
    except OSError:
        try:
            shutil.copyfile(source, destination)
        except OSError:
            return source
    return destination


def _compile_unlocked(engine, tex, photo=None, extras=None):
    os.makedirs(prefs.BUILD_DIR, exist_ok=True)
    for name in os.listdir(prefs.BUILD_DIR):
        try:
            os.remove(os.path.join(prefs.BUILD_DIR, name))
        except OSError:
            pass
    main_tex = os.path.join(prefs.BUILD_DIR, "main.tex")
    with open(main_tex, "w", encoding="utf-8") as f:
        f.write(tex)
    if photo and os.path.isfile(photo):
        ext = os.path.splitext(photo)[1].lower()
        if ext in ALLOWED_PHOTOS:
            try:
                shutil.copy2(photo, os.path.join(prefs.BUILD_DIR, "foto" + ext))
            except OSError:
                pass
    for name, source in (extras or {}).items():
        if os.path.isfile(source):
            try:
                shutil.copy2(source, os.path.join(prefs.BUILD_DIR, name))
            except OSError:
                pass
    try:
        subprocess.run(
            [
                engine,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-output-directory", prefs.BUILD_DIR,
                "main.tex",
            ],
            cwd=prefs.BUILD_DIR,
            capture_output=True,
            timeout=600,
            creationflags=_SUBPROCESS_FLAGS,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "pdf": None, "errores": [messages.t("compile_timeout")]}
    pdf = os.path.join(prefs.BUILD_DIR, "main.pdf")
    if os.path.isfile(pdf):
        return {"ok": True, "pdf": _copy_stable_pdf(pdf), "errores": []}
    log = _read_log(os.path.join(prefs.BUILD_DIR, "main.log"))
    errors = _parse_errors(log)
    if not errors:
        errors = [messages.t("compile_no_pdf")]
    return {"ok": False, "pdf": None, "errores": errors}
