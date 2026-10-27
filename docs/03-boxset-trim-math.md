# Boxset trim math

An e-book bundle can be a million words; a print bundle has to *fit*.
This chapter is the arithmetic of whether your print boxset physically
exists, what it costs to print, and what list price leaves you money.
All figures are round planning numbers — the KDP printing calculator and
[kdp-profit-planner](https://github.com/dylanasdale) give you exact
values for *your* manuscript.

## Step 1: words per page by trim size

Rough planning figures for a novel-typeset manuscript (healthy margins,
standard line spacing — not a wall of 12-point text):

| Trim (in) | Words per page (plan with) | Words per page (often lands) |
|-----------|---------------------------:|-----------------------------:|
| 5 × 8     | 250                        | 260–300                      |
| 5.5 × 8.5 | 300                        | 310–340                      |
| 6 × 9     | 330                        | 350–400                      |

Plan with the **low** figure. It over-estimates your page count a
little, which is exactly what you want when the question is "will it
fit?"

Example: an 80,000-word novel at 6 × 9 →

```text
80,000 words ÷ 330 words/page ≈ 243 pages  (plan for ~250)
```

and [kdp-profit-planner](https://github.com/dylanasdale) computes the
same estimate per trim in one command — use it once your word count is
real instead of planned.

## Step 2: the print ceiling

KDP paperbacks have a maximum page count — around **800 pages** (the
published figure is 828 as of writing; check the current KDP help page)
— and hardcovers have a higher minimum (~75 pages) with their own caps.
The e-book has no such ceiling.

For a bundle, the arithmetic is:

```text
bundle pages ≈ pages(book 1) + pages(book 2) + ... 
               + 30–50 pages of shared front/back matter
```

The 30–50 extra pages covers the combined title page, series copyright
page, bundle table of contents, and unified back matter — plus each
book's divider page.

### Worked example: the trilogy, three ways

Three novels, 80,000 words each — three paper trims to compare:

| Trim     | Per book | Bundle + extras | Verdict |
|----------|---------:|----------------:|---------|
| 6 × 9    | ~250     | 3 × 250 + 40 = **790** | fits (barely) |
| 5.5 × 8.5 | ~267    | 3 × 267 + 40 = **841** | misses by ~15 pages |
| 5 × 8    | ~320     | 3 × 320 + 40 = **1,000** | far past the cap |

Notice the pattern that surprises everyone: the **smaller** the trim,
the **more** pages your bundle needs, because each page holds fewer
words. Print boxsets that don't fit in a small novel trim are very
common; the fixes, in order of effort:

1. **Wider trim** (6 × 9 or 6.14 × 9.21): a physically larger page
   holds more words per sheet, so the same manuscript needs fewer
   pages. Fine for a bundle, and it feels like a proper omnibus.
2. **Slightly tighter internal typesetting**: going from 330 to 380
   words per page on the same 6 × 9 turns 250,000 words from ~758 pages
   into ~658. Same book, about 100 fewer pages — the cheapest fix when
   you're just a pinch over, and best-done from a real page count, not
   a planned one.
3. **Split into two volumes** (*Parts One and Two*, published as two
   products): keeps cover art consistent and lets each volume carry
   half the extras. Common for 300k words or more.

### Worked example: the big omnibus

A five-book series at 65,000 words each = 325,000 words total:

```text
325,000 words ÷ 330 words/page ≈ 985 pages  (6 × 9)   → way over the cap
325,000 words ÷ 380 words/page ≈ 855 pages  (tight 6 × 9) → still over
```

Even generous typesetting can't claw back 200 pages. The natural fix:
**two print bundles**:

```text
Books 1–3: 195,000 words ÷ 330 ≈ 590 + 40  = ~630 pages  → fits
Books 4–5: 130,000 words ÷ 330 ≈ 394 + 40  = ~434 pages  → fits
```

Two bundles also let each sit on the series page beside its own books,
and give you two rungs on the print ladder instead of one shelf-
intimidating slab.

## Step 3: what a print bundle costs to print

The print cost is charged per copy printed, and your royalty comes off
the list price *after* that cost. Round-number planning formula for a
US paperback at the large page scale:

```text
print cost ≈ fixed part (about $0.85) + a bit over a cent per page
```

| Pages | Print cost (plan with) |
|------:|-----------------------:|
| 150   | ~$2.65                 |
| 300   | ~$4.45                 |
| 600   | ~$8.05                 |
| 800   | ~$10.45                |

## Step 4: what a bundle *earns* per sale at print

Print royalty on KDP = `(list price − print cost) × 60%` in round
numbers. So the same 800-page bundle at three list prices:

| List price | ~ $10.45 print cost | Royalty per book |
|-----------:|--------------------:|-----------------:|
| $16.99     | − $10.45 = $6.54    | ~$3.92           |
| $19.99     | − $10.45 = $9.54    | ~$5.72           |
| $24.99     | − $10.45 = $14.54   | ~$8.72           |

Two rules fall out of that table:

- **The floor rule:** list price must cover print cost plus your
  tolerance for return-shipping bookkeeping — below the print cost the
  "royalty" goes negative, and you fund it.
- **Compare fairly:** a three-book print bundle at $19.99 saves the
  reader roughly $10 versus buying three print singles at $9.99 each;
  the bundle has to *earn* a discount that size with real convenience
  (all three books, one buy, one spine you can shelve).

## Step 5: spine width (for cover art planning)

Cream paper (the novel thing):

```text
spine width ≈ 0.0025 inches per page
790-page bundle → 790 × 0.0025 ≈ 2.0 inches
```

White paper runs a bit thinner (about 0.0022 per page). The KDP cover
template writes your spine dimensions for you once the page count is
set, so use this only for early sketches — but note that a thin
(<80-page) spine shouldn't carry text, and a nearly 2-inch spine can
carry both title and author name comfortably.

## Summary card

- E-book bundle: no page ceiling, no print math to worry about.
- Print bundle: `total words ÷ words-per-page(trim) + ~40` must come in
  **under ~800 pages**.
- Wider paper (6 × 9 or larger) shrinks page count; smaller paper grows
  it.
- Print cost is about **$0.85 + $0.012 per page**; print royalty is
  **60% of (list − cost)**.
- When words don't fit: bigger trim, tighter typesetting, or *two
  bundles*.

Fill this all in for your series in
[Worksheet W2 — boxset costs](worksheets/worksheet-boxset-costs.md).

Next: [chapter 4 — pricing ladders](04-pricing-ladders.md).
