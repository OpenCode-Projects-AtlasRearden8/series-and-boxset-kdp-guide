# Beyond One Book (KDP)

A plain-English author manual for the moment your publishing plan grows
**past a single title**: setting up a KDP series page, building a boxset
step by step, doing the trim-size math that decides whether a print bundle
even fits, pricing a ladder across the series, and the read-through and
99-cent launch arithmetic that decides whether a discount pays for itself —
plus a glossary, cost tables, and fill-in worksheets.

Written in the same beginner-first voice as *The Massive AI Manual* and
[dylanasdale.github.io](https://dylanasdale.github.io): clear, warm, step by
step, never condescending. Built by **Asdale Dynamics, LLC** — beginner
friendly AI education, books and guides, and practical tools. MIT licensed
(see `LICENSE`).

Everything runs locally. No accounts, no network calls, no API keys, no
tracking, nothing leaves the folder. All figures are **round planning
numbers**, not guarantees — verify final prices, page counts, and limits in
your own KDP dashboard against the current KDP help pages before you publish.
This is a planning guide; it is not affiliated with Amazon and it is not
legal, accounting, or tax advice.

## What's inside

Eight chapters, a glossary, and two fill-in worksheets:

| # | Chapter | Covers |
|---|---------|--------|
| 1 | Series page setup | how the series page gets built, naming + numbering rules, a 10-minute checklist |
| 2 | Boxset build steps | what goes in the bundle, the 12-step e-book and print build order, enrollment choices |
| 3 | Boxset trim math | words-per-page tables, the 828-page print ceiling, spine widths, print cost + royalty tables |
| 4 | Pricing ladders | rungs from 99¢ to omnibus, the 70%/35% e-book royalty band, and why $9.99 beats $14.99 |
| 5 | Read-through that pays | the rate that turns one sale into 2–3, back-matter signposts, and when a discount pays back |
| 6 | Per-book vs omnibus keywords | which search intents go on each book vs the bundle, and what to never duplicate |
| 7 | Launch calendar + 99-cent math | a week-by-week launch plan and the pay-back arithmetic of a $0.99 promo week |
| 8 | Wide vs KU round numbers | page-read wages vs wide margins per reader, and a 5-line decision rubric |
| 9 | Glossary | 25 terms in plain English, with a pointer back to the chapter where they matter |
| W1–W2 | Worksheets | launch-ladder planner (W1) and boxset cost planner (W2), both fill-in |

## Companion projects (this guide does not repeat them)

- **[kdp-profit-planner](https://github.com/dylanasdale)** — the exact
  per-book math: page counts by trim, printing cost, royalty per unit,
  break-even units, price scans, monthly projections. Use it when the round
  numbers here need to become *your* numbers.
- **[publishing-beyond-kdp-guide](https://github.com/dylanasdale)** —
  rights and reversions, ISBN decisions, non-Amazon channels (IngramSpark,
  libraries, audiobooks, direct sales), and author taxes. This guide only
  rounds off the *series-level* wide-vs-KU decision; the channel setup
  lives there.
- **[book-keyword-lab-cli](https://github.com/dylanasdale)** — scores and
  drafts your seven keyword slots. This guide's keyword chapter covers only
  the series-vs-omnibus split.
- **[kdp-interior-templates](https://github.com/dylanasdale)** and
  **[kdp-cover-bleed-checker-cli](https://github.com/dylanasdale)** — the
  print-ready file and cover art that the boxset build steps (chapter 2)
  assemble.

## How to run it

Requires Python 3.9+ (standard library only — no pip installs).

```bash
# Build the static HTML site into site/
python3 build.py

# Build and verify every expected page exists and links resolve
python3 build.py --check

# Build into a different folder
python3 build.py --out /tmp/opencode/site-preview

# Read the guide as written (no build needed)
# start with docs/00-start-here.md
```

Then open `site/index.html` in a browser. Serve it locally if you like:

```bash
python3 -m http.server 8080 --directory site
# visit http://localhost:8080
```

## Tests

```bash
python3 -m pytest tests/ -v
```

The tests cover the markdown→HTML converter, the full site build, internal
link resolution, page-order completeness, and the arithmetic of the worked
examples in the chapters (the cost tables and ladder math are recomputed and
checked, so the guide's numbers stay honest).

- License: MIT (see `LICENSE`)
- Status: planning guide with rounded example figures — **not** guarantees,
  and **not** legal, tax, or accounting advice. Confirm current KDP limits
  (page counts, royalty bands, promo rules) in KDP's own help pages before
  you act on them.
