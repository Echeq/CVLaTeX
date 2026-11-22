# Security Policy

## Supported versions

CVLaTeX 1.0 is stable. Only the latest `1.0.x` release receives security
fixes.

| Version | Supported |
| --- | --- |
| 1.0.x | :white_check_mark: |
| < 1.0 | :x: |

## Reporting a vulnerability

Please report vulnerabilities privately through
[GitHub Security Advisories](https://github.com/Echeq/CVLaTex/security/advisories/new)
for this repository. If that form is unavailable, open a regular
[issue](https://github.com/Echeq/CVLaTex/issues) that asks for a private
channel without describing the vulnerability itself.

Include the affected version, operating system, reproduction steps and the
impact you observed. **Never include passwords, tokens, private keys, personal
documents, CVs, photos or other secrets** in an advisory, an issue, a log or an
attachment. If a proof of concept needs a document, use synthetic data.

There is no bug bounty and no guaranteed response time: this is a
maintainer-run project and reports are handled on a best-effort basis.

## Scope and guarantees

CVLaTeX runs locally, stores preferences, autosaves and media in the per-user
application data directory, and talks only to `127.0.0.1` for its UI. It has no
accounts, telemetry, cloud sync or remote API. It may download TinyTeX at the
user's request. Release bundles are built by GitHub Actions from the tagged
source, and `SHA256SUMS.txt` lets you verify the downloaded archive.

### Local UI server

The interface is served by an embedded HTTP server bound to a random
`127.0.0.1` port:

- Every route requires a 32-byte per-session token, accepted once in the
  window URL and then echoed as an `HttpOnly`, `SameSite=Strict` cookie.
  Token comparisons use `hmac.compare_digest`.
- `Host` must be the exact loopback authority and a present `Origin` must match
  it; cross-origin requests are rejected with `403`.
- Paths are confined with `realpath` + `commonpath`. `/media/` only serves the
  flat `foto_*`, `logo_*`, `recorte_*` and `cv_*` files the app creates, and
  `/preview/` only serves flat PDFs from the build directory.
- Responses send `Content-Security-Policy`, `X-Frame-Options`,
  `Permissions-Policy`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: no-referrer`, `Cross-Origin-Resource-Policy: same-origin`
  and `Cache-Control: no-store`. The app UI allows scripts only from its own
  origin and `'unsafe-eval'` because pywebview injects its local bridge by
  evaluating a string; no remote content is loaded. The vendored PDF.js viewer
  gets the inline-script allowance it needs.
- The server is stopped when the window closes.

### Untrusted files and images

- Images received from the webview must be a PNG or JPEG data URL, must match
  the declared format by magic bytes, and are capped at **12 MB** each.
- `.cvjson` files are capped at **50 MB**. Embedded media is capped at 12 MB
  per image and 64 MB in total, and invalid or oversized entries are skipped
  instead of being written to the cache.
- Autosave refuses to write an envelope above the same 50 MB limit.
- `.tex` import only accepts files with the embedded CVLaTeX data block; foreign
  LaTeX is rejected instead of parsed heuristically.
- Every user value injected into a generated `.tex` file passes through
  `esc()`.

### TinyTeX downloads

- Official and SourceForge assets are verified against SHA-256 digests pinned
  in the source for the exact release version. A mismatch aborts the install.
- A custom mirror must use **HTTPS** and must publish `<url>.sha256`; a missing
  checksum aborts the install. Plain-HTTP mirrors and HTTPS-to-HTTP redirects
  are refused.
- Archives are extracted into a staging directory with `tarfile` data filters
  and swapped atomically, so a corrupt archive cannot destroy a working
  installation.
- A local archive chosen with **Install from downloaded file…** is trusted as
  provided by the user; verify its checksum yourself if you downloaded it from
  an untrusted mirror.

### Release integrity

- The release workflow runs the test suite, builds on Windows, Linux and macOS,
  verifies the archives and publishes `SHA256SUMS.txt`.
- The checksum manifest is **not signed**. It protects against a truncated or
  corrupted download, not against someone who can replace both the archive and
  the manifest on the release page.

## Known limitations

The project provides **no security guarantees**. In particular:

- Windows and macOS builds are **unsigned and not notarized**. Windows
  SmartScreen and macOS Gatekeeper may warn or block the first launch. Verify
  the SHA-256 checksum and build provenance before running a bundle.
- There is no Authenticode signature, Apple notarization, signed checksum
  manifest or reproducible-build attestation yet.
- The app does not sandbox the LaTeX engine. Compiling a hand-written `.tex`
  file can make TeX read local files through `\input` and include them in the
  PDF; only compile documents you trust.
- Users are responsible for the LaTeX engine they install or that the TinyTeX
  installer downloads, and for the documents and personal data they load.
- No independent audit of this codebase or its dependencies has been performed.
