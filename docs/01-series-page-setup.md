# Series page setup

The series page is how Amazon groups connected books in the store, and it
is not something KDP builds for you on request — it is assembled from
**metadata you type into each book at upload**. Get the fields right once,
and every future book assembles itself onto the page. Get them wrong, and
you'll be doing republish-and-wait loops.

## How the series page actually gets built

Inside KDP, each book has two series fields:

- a **series name** (what Amazon shows as the series title), and
- a **series number** (reading order).

When two or more published books share a matching series name, the store
builds a series page for them and orders the books by number. That's the
whole mechanism. It works across formats too: an e-book titled *The Alvin
Files: Case One* and a paperback *The Alvin Files: Case Two* appear
together when the series fields match.

Three things follow from that:

1. **The series name must match exactly, every time.** One book says
   *The Alvin Files*, the next says *Alvin Files, The* — no shared page,
   or (worse) two near-duplicate series pages. Exact match, eyeball it
   every time.
2. **Numbers, not words.** `1`, `2`, `3` — not *Part One*, *Book Two*,
   *the sequel*. The number field is what stores sort by, and it is
   stingy about what it accepts. Letters in that field often get dropped
   or rejected, so keep it a plain number.
3. **Each book carries its own number field.** Amazon does not infer
   "*obviously* this is book three" from the title. Type it in.

## The naming rules that save you pain

### Series name

- **Short enough to say in one breath.** It will be spoken by
  newsletters, read aloud in podcasts and audiobooks, and be written on
  a spine twice (each book and the boxset). One to four words is the
  comfortable range.
- **Put it everywhere the same way.** Since KDP matches on exact text,
  one working trick is to design a tight template, for example:
  `Title: The Alvin Files: Case One — Series: The Alvin Files (1)`.
- **A subtitle can carry a description.** If you want the cover text to
  stay clean (title alone), the subtitle field can hold the connective
  tissue: *A Dragonia Cozy Mystery* — but the **series name field**
  is still what builds the series page; the subtitle alone doesn't.
- **Don't number the omnibus.** KDP's number field is rigid — it takes a
  plain number, not "1–4". The normal pattern is to leave the boxset's
  series number **empty** (it still groups on the series page) and put
  *Books 1–4* in the subtitle or cover art. Check the drop of your book
  after upload to confirm the display you got.

### Series number

- Integers for full books; novellas from the same world can sit
  between as `1.5`, `2.5` if the field accepts the decimal (some store
  displays don't — verify with a cheap novella, not your flagship).
- Don't publish a book 4 if books 1–3 are still sitting as blanks —
  the series page will show a hole and readers won't know whether
  book 1 exists.
- For the **print** edition of each title, remember the fields are
  per-format: the paperback upload has its own series name and number
  line. A "missing" paperback from your series page is nearly always a
  dropped series field on the print upload.

## The five-minute maintenance loop

Do this each time you publish a new book into an existing series:

1. Copy the series name from your *previous* book's KDP dashboard page —
   don't retype it from memory.
2. Enter the next integer in the series number field.
3. After the book goes live, open the store's series page (find any book
   → click the series name) and check: all books present, numbers in
   order, all formats grouped.
4. If a book is missing or out of order, fix its fields and republish —
   metadata edits go live separately from content and don't need a full
   re-upload.

## The 10-minute checklist for a new series

- [ ] Series name chosen: short, easy to say, easy to read on a spine.
- [ ] It appears nowhere in a form that fights the legal naming — the
      series name field is not the place for a different version of your
      own name, your publisher name, or a URL.
- [ ] Book titles chosen with the number in or out — either is fine, but
      one system, not both (*Case Two* everywhere, or *The Alvin Files*
      + series number `2` everywhere, not a mix).
- [ ] All e-book uploads carry the identical series name.
- [ ] All print uploads carry the identical series name *and* number.
- [ ] Every book's **back matter** points to the next-in-series product
      page (set up in [chapter 5](05-read-through-that-pays.md)).
- [ ] A note in your publication tracker of what the series *name* is,
      character for character, including any colon and capitalization.

## What actually appears where

| Store surface | Built from | Your control |
|---------------|------------|--------------|
| The series page (store) | series name + number fields | naming and number hygiene |
| Order on that page | series number fields | ascending numbering |
| "Follow this series"-style buttons | the store itself | nothing — they only show when ≥ 2 books exist |
| Boxset grouping | series name on the boxset | number left blank, subtitle says "Books 1–4" |

## Where this gets deeper elsewhere

- Exact per-book royalty math by price → **kdp-profit-planner** CLI.
- The rights/ISBN questions you answer *before* filling in these fields →
  [publishing-beyond-kdp-guide](https://github.com/dylanasdale), chapters
  1–2.
- Naming a book well (title/subtitle work outside the series fields) →
  **blurb-craft-lab-cli**.

Next: [chapter 2 — boxset build steps](02-boxset-build-steps.md).
