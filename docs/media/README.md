# Media guide — images and videos

This repository uses a simple placeholder convention so screenshots, diagrams
and demo videos can be added later without rewriting the documents.

## Placeholder syntax

Use exactly one of these forms and replace only the text inside the braces:

```text
[Insert:Image:{Main window with the form and live preview}]
[Insert:Video:{Two-minute demo: first run, template switch, PDF export}]
```

When the file is ready, replace the placeholder with standard Markdown:

```markdown
![Main window with the form and live preview](images/main-window.png)

[Watch the two-minute demo](https://example.com/cvlatex-demo)
```

From `docs/markets/` or `docs/competition/`, use the `../media/images/...`
prefix instead.

## Folder layout

```text
docs/
├── media/
│   ├── README.md          ← this file
│   ├── images/            ← screenshots, diagrams, market examples
│   └── videos/            ← local video files (optional; prefer links)
├── markets/               ← six CV market guides
└── competition/           ← pitch, demo script and submission material
```

## Naming conventions

- Use lowercase kebab-case: `main-window.png`, `us-resume-example.webp`,
  `architecture.svg`, `demo-en.mp4`.
- Prefix by purpose when it helps: `demo-`, `market-us-`, `template-chinese-`.
- Keep one language suffix when there are localized captures:
  `main-window-en.png`, `main-window-es.png`, `main-window-zh.png`.
- Do not include personal data, real CVs, email addresses or phone numbers.

## Formats and size limits

| Asset | Preferred format | Notes |
| --- | --- | --- |
| Screenshot | PNG or WebP | ≤ 2 MB; 1440–1920 px wide |
| Diagram | SVG (or PNG) | Keep text legible at 100% |
| Short loop | GIF or WebM | ≤ 5 MB; 10–20 s |
| Demo video | MP4 (H.264) | 1080p; link it if larger than 50 MB |

Large videos should be hosted on YouTube, Bilibili or a release asset and
linked instead of committed. If a local file is unavoidable, use Git LFS and
add `*.mp4` / `*.mov` to `.gitattributes`.

## Where the media is referenced

- [`README.md`](../../README.md) — project demo and screenshots.
- [`docs/competition/README.md`](../competition/README.md) — submission
  package.
- [`docs/competition/demo-script.md`](../competition/demo-script.md) — shot
  list for the demo video.
- [`docs/markets/*.md`](../markets/) — per-market CV examples.

## Checklist before publishing

- [ ] Every `[Insert:Image:...]` / `[Insert:Video:...]` placeholder is
      replaced or intentionally left as a TODO.
- [ ] No personal data, tokens, API keys or local paths are visible.
- [ ] Images have meaningful alt text (in English, per the documentation
      standard).
- [ ] Videos are linked or optimized; the repository stays small.
- [ ] The same asset is not duplicated in several folders.
