# Boxset build steps

A boxset (also called a bundle or omnibus) is one product that contains
several books you already publish. It's the single most useful thing you
can build for a series with three or more books: it gives readers a
"get it all" option, it reuses work you've already done, it adds a
high-ticket rung to your pricing ladder, and — on some platforms — its
pages count toward readers' paid page reads, so a big bundle becomes a
long binge.

This chapter is the build order; the trim-and-cost math that decides
whether the print version fits is [chapter 3](03-boxset-trim-math.md).

## Decide before you build

### 1. Contents

- **Books 1–3** is the most common shape. Readers trust "start to finish"
  of a trilogy; bundles of 3 map neatly onto the trilogy habit.
- **Books 1–4/5** works well when your singles are short (novellas,
  category romances, episodic non-fiction).
- **Everything + extras** (bonus scene, prequel novella, author
  commentary) is a classic value-add for the *loyal* audience — it's how
  you justify a bundle price to readers who already own book one.
- Non-fiction bundle caution: overlapping chapters across your books look
  recycled. Interchapters that are genuinely new or re-sequenced materials
  feel like a bundle, not a blender.

### 2. Enrollment (e-book)

The bundle is **its own product with its own choice**. You can have your
singles wide (every store) and enroll only the bundle in Kindle Unlimited
if you choose — exclusivity is decided per product, not per author. The
two usual options:

- **Match the singles** (all in, or all out): simple, one story to tell.
- **Split choice** (singles wide, bundle in KU): the bundle grabs
  binge page reads while the singles keep earning elsewhere. It also
  means *one* checkout experience for the KU reader: one borrow covers
  three books.

There is a trade-off detail: KDP's rules on bundle contents (for
instance, whether outside-store links are allowed inside an enrolled
bundle) bite *now*, not after upload. Check the current KDP
bundles-and-boxsets help page for the exact list before you go.

### 3. Format

- **E-book bundle:** always exists on KDP, no page cap. Build it first.
- **Print bundle:** costs real money to print, has page-count caps that
  depend on trim size, and needs its own ISBN. Priced per chapter 3.

## The 12-step e-book bundle build

These steps assume you published the singles from clean source files; if
your sources are messy, allow extra time for step 3.

1. **Create a working folder** (`bundle-1-3/`) with `raw/` (source text),
   `build/` (outputs), and `assets/` (images).
2. **Fix a bundle title.** Either the series name alone (*The Alvin
   Files*) or series + contents (*The Alvin Files: Cases One to Three*).
   Avoid republishing the same visible title under two products.
3. **Choose one manuscript format for the bundle**: the margins, line
   spacing, chapter-break style, and — if you'll do print — a trim.
   Match the singles unless there's a reason: matching keeps readers
   sane and keeps the print math friendly
   ([chapter 3](03-boxset-trim-math.md)).
4. **Build one continuous manuscript** from the source text: series
   front matter (title page → copyright → table of contents), then book
   1 text, then book 2 text, then book 3 text, then back matter (author
   page + newsletter + review ask + the *next-in-series* product).
5. **Separate the book start pages.** Each book restarts on a right-hand
   page in print (and gets a full divider page in e-book) carrying only
   that book's title. Readers navigating a bundle flip around looking
   for these — make them visible and consistent.
6. **Stack the copyright material.** The bundle copyright page states
   the bundle copyright and lists each included book with its own
   original copyright and title. Do not publish duplicate full copyright
   pages per book-section — one clean stack at the front is the norm.
7. **Rebuild the table of contents.** In e-book form it's a jump link to
   three book starts and three per-book chapter lists (reader choice:
   "open at the series level, then dive"). In print, one combined TOC,
   with each book as a minor heading.
8. **Set the back matter once** — the bundle talks about the series as a
   whole, so your "books in this series" list now points to *other*
   products you sell (audio, print, the next bundle).
9. **Proofread in one pass, across books.** Bundles surface the
   inconsistencies that per-book publishing hides: a "Chapter One" in
   book 1 but a "Chapter 1" in book 2, two spellings of one character's
   name, back matter that repeats itself. Fix these at the manuscript
   level, not by nudging pages in the layout file.
10. **Generate e-book and print outputs separately** from the same
    source. You will need a fresh **ISBN for each format** of the bundle
    (KDP's free e-book identifier or a paid print ISBN per format — see
    publishing-beyond-kdp-guide, chapter 2, for the free-vs-buy math).
11. **Write the bundle listing** fresh: not a paste of book one's
    description. Lead with what's inside (X books, Y total words, and
    any extras), then the series hook.
12. **Set the price ladder** per [chapter 4](04-pricing-ladders.md),
    choose KU enrollment or not, and upload.

## The print bundle in one breath

Same manuscript, different container: choose the **trim** (bigger paper
= fewer pages, which is what saves oversize bundles), build a **cover
that includes a spine** (spine width ≈ `pages × about 0.0025"`, more in
chapter 3), get a **print ISBN**, and put it through the same quality
check you'd give any print book — a bundle is "just one big book" to the
printer.

## After upload

- Check the live product page: bundle title, contents note (for the
  numbers shown), series grouping, price shown, series page membership.
- Keep one bundle listing per contents — a bundle running a promo at the
  same time as its singles on promo is fine and normal; what looks spammy
  is duplicated listings of the *same* content, so don't fragment.
- Add the bundle to the back matter of the *next* book in the series:
  new readers meet the boxset here.

## Where this gets deeper elsewhere

- Behind-the-scenes checklist: **kdp-interior-templates** (build the
  correct-size interior before the bundle steps) and
  **kdp-cover-bleed-checker-cli** (check the cover file fits the trim).
- Pricing the bundle → [chapter 4](04-pricing-ladders.md).
- Whether the whole series (not just the bundle) should go wide →
  [chapter 8](08-wide-vs-ku-round-numbers.md).

*Planning guide, not a substitute for the KDP help pages: bundle rules and
page limits change. Verify current rules at upload time.*

Next: [chapter 3 — boxset trim math](03-boxset-trim-math.md).
