# STATUS.md

## What was built

**Beyond One Book (KDP)** — a plain-English series-and-boxset author
manual for KDP-focused publishing, delivered as Markdown sources under
`docs/` plus a local, tested build script (`build.py`, standard library
only) that renders the whole guide as a static HTML site. Built by
Asdale Dynamics, LLC as a small-business/author tool. Complements
**kdp-profit-planner** (exact per-book royalty/printing math) and
**publishing-beyond-kdp-guide** (rights, ISBNs, non-Amazon channels,
direct sales, taxes) without repeating either — the split is explicit in
every chapter and in the README's companion table.

Content (9 chapters + 2 fill-in worksheets in `docs/`):

- **Series page setup** — how the store's series page assembles from the
  series name/number fields, naming and numbering rules, the omnibus
  wrinkle (number left blank, "Books 1–4" in the subtitle), and a
  10-minute checklist.
- **Boxset build steps** — contents choices, per-product enrollment
  (singles wide / bundle in KU is allowed), the 12-step e-book build
  order, print bundle notes, and the after-upload checks.
- **Boxset trim math** — words-per-page planning tables by trim, the
  ~800-page print ceiling (828 as of writing), worked trilogy and
  omnibus examples (fits / misses / split), print cost ≈ $0.85 +
  $0.012/page, print royalty = 60% × (list − cost), and spine widths.
- **Pricing ladders** — the 5-rung ladder (99¢ door → print bundle),
  the 70%/35% e-book bands ($2.99–$9.99), the $2.98/$2.99 and $9.99/$10
  cliffs, and why a $9.99 bundle (~$6.99) out-earns $14.99 (~$5.25),
  with the ~$20 crossover where 35% catches back up.
- **Read-through that pays** — the compounding table (100 → 65 → 49 →
  37), the sensitivity table at four read-through levels, six
  back-matter "signposts", and the full pay-back arithmetic of a
  99-cent week (~$1,800 given away → ~$3,200 earned back at healthy
  read-through ≈ 1.7×) plus the wash and losing cases.
- **Per-book vs omnibus keywords** — which search intents go on each
  book (genre/trope/reader-identity), which belong on the bundle
  (complete series / box set / omnibus), what to never duplicate, and a
  yearly audit ritual.
- **Launch calendar + 99-cent math** — week −14 → +12 rhythm, why the
  dip runs *after* the full-price launch week, the pocket arithmetic
  ($0.35 vs $3.49, ~$3.15 dip cost vs ~$3.97 pay-back per reader), and
  the 1–3-day price-ripple rule.
- **Wide vs KU round numbers** — page-read wages at ~0.4¢/page vs wide
  margins, a per-buyer comparison (~$5.00 KU-path vs ~$12.25 wide-path
  for a healthy series), and a 5-line decision rubric with
  per-product, 90-day enrollments as the escape hatch.
- **Glossary** — 25 terms, one line each, each linking to the chapter
  where the term matters.
- **Worksheet W1 (launch ladder)** — series inventory, ladder rows,
  promo calendar, and fill-in pay-back boxes with a 1.5×/1.1× decision
  threshold.
- **Worksheet W2 (boxset costs)** — words-to-pages planner, the
  print-ceiling check with fix options, cost/royalty rows, spine notes,
  bundle-rung band sanity, and a decision box.

Site extras: `site/index.html` landing page with chapter cards and a
companion-tools section; every page has a sticky sidebar TOC, prev/next
pager, callout blockquotes, print styles, and a mobile layout. No fonts,
assets, or anything else fetched from the network.

## How to run it

```bash
# Build the static site into ./site
python3 build.py

# Build and verify (expected files exist, sizes sane, links resolve)
python3 build.py --check

# Build elsewhere (e.g. for a preview)
python3 build.py --out /tmp/opencode/site-preview

# Read the sources directly — start with docs/00-start-here.md

# Serve locally, if you like:
python3 -m http.server 8080 --directory site

# Run the test suite
python3 -m pytest tests/ -v
```

Requires Python 3.9+ (standard library only; pytest only for tests).
Everything runs locally — no accounts, no API keys, no network calls,
nothing leaves the folder.

## Verification results (final run, this machine — Python 3.13.5, pytest 9.1.1)

- `python3 build.py --check` → OK: 14 expected files present (12 chapters
  + worksheets, index, css), all links resolve, nothing suspicious.
- `python3 -m pytest tests/ -v` → **83 passed**:
  - `tests/test_build.py` — markdown→HTML converter units (headings,
    paragraphs, bold/italic/code, links incl. docs-relative resolution
    from worksheets, lists, checkboxes, numbered steps, GFM tables with
    alignment, fences, blockquotes), page plumbing (titles, slugs,
    sidebar, pager), full-build e2e into a temp dir, and the link
    checker (missing targets, missing anchors).
  - `tests/test_content.py` — the chapters' arithmetic recomputed and
    checked against the pages on disk: band table, cliffs, bundle-rung
    comparison, dead zone/crossover, print cost/royalty tables, spine
    widths, trim examples, read-through compounding and sensitivity
    tables, the 99-cent pay-back example (money(gap) = $3.15, earn-back
    ≈ $3,200), pocket launch math, KU wages, glossary term count, worksheet
    fill-ins, disclaimers, no-draft-markers and no-secrets hygiene, and
    the exact `Copyright (c) 2026 Asdale Dynamics, LLC` line in LICENSE.
- Fix loop during development: converter link-resolution bug found and
  fixed by the tests (worksheet-relative links now resolve through a
  `resolve_md_target` step); banker's-rounding artifacts in the doc's
  mental arithmetic reconciled to half-up counting; several drafting
  typos/garbled sentences caught by re-reads and removed.
- `git init` + single plain commit (no remotes, nothing pushed).

## Known gaps / honest limits

- All figures are **round planning numbers**, not quotes: KDP page-count
  limits, royalty bands, print costs, KENP payouts, and promo rules
  change; the guide says so on every working page and instructs readers
  to verify in their own dashboard and the current KDP help pages. It is
  not affiliated with Amazon.
- Not legal, accounting, or tax advice — rights, ISBN policy, taxes, and
  channel setup live in **publishing-beyond-kdp-guide**; this manual
  takes that split on purpose.
- The worked examples use a *fictional healthy series at $4.99 singles*
  so the arithmetic stays round; your real read-through rates replace
  them in Worksheet W1 boxes.
- The markdown converter covers the subset used by `docs/` (headings,
  paragraphs, inline code/bold/italic/links, lists incl. checkboxes,
  GFM pipe tables with alignment, fenced code, blockquotes, rules); it
  is deliberately *not* a general-purpose markdown parser and will not
  handle constructs outside that set. Nested lists are intentionally
  unsupported (none are used).
- The HTML site is a local artifact, not a deployment; `site/` is
  gitignored by design (regenerable in one command). No pushing, no
  publishing, no remotes anywhere in the workflow.
- Companion cross-references point at sibling local projects by name
  (kdp-profit-planner, publishing-beyond-kdp-guide, book-keyword-lab-cli,
  kdp-interior-templates, kdp-cover-bleed-checker-cli,
  kdp-sales-tracker-webapp, arc-review-tracker-webapp); the assumed
  GitHub destination (github.com/dylanasdale) is placeholder text for
  hub links in README, as in sibling guides.
