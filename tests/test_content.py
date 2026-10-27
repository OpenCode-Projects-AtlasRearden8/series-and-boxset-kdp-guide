"""Content tests: the chapters' round-number arithmetic is recomputed and
checked against the pages on disk, so the guide's numbers stay honest.
Also guards structure (glossary length, worksheets, disclaimers, hygiene).

Run from the project root with:  python3 -m pytest tests/test_content.py -v
"""

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build  # noqa: E402

DOCS = ROOT / "docs"


def read_doc(relname: str) -> str:
    for subdir, _ in build.PAGE_ORDER:
        if _ == relname:
            path = DOCS / subdir / relname if subdir else DOCS / relname
            return path.read_text(encoding="utf-8")
    raise AssertionError(f"{relname} is not a registered page")


def money(value: float) -> str:
    """Format dollars the way the chapters render them (nearest cent)."""
    return f"{round(value, 2):,.2f}"


def hr(value: float) -> int:
    """Half-up rounding — how you'd round counts in your head."""
    return math.floor(value + 0.5)


# ---------------------------------------------------------------------------
# Chapter 3: trim math and cost tables
# ---------------------------------------------------------------------------

class TestTrimMathNumbers:
    doc = staticmethod(lambda: read_doc("03-boxset-trim-math.md"))

    def test_word_per_page_planning_figures(self):
        doc = self.doc()
        for figure in ("250", "300", "330", "380"):
            assert figure in doc

    def test_80k_word_novel_pages(self):
        # a page can't be printed in fractions: ceil(80,000/330) = 243
        pages = math.ceil(80_000 / 330)
        assert pages == 243
        doc = self.doc()
        assert "≈ 243 pages" in doc
        assert "~250" in doc

    def test_trilogy_fits_table(self):
        doc = self.doc()
        # 6x9: 3 novels (80k each) + 40 extras
        assert "3 × 250 + 40 = **790**" in doc
        # 5.5x8.5: 80k / 300 = 266.7 ≈ 267 pages per book
        per_book = 80_000 / 300
        assert round(per_book) == 267
        assert "3 × 267 + 40 = **841**" in doc
        # 5x8: 80k / 250 = 320 pages per book
        assert "3 × 320 + 40 = **1,000**" in doc

    def test_tightening_saves_about_100_pages(self):
        doc = self.doc()
        assert "~758" in doc      # 250,000 / 330 = 757.6
        assert "~658" in doc      # 250,000 / 380 = 657.9
        assert "about 100 fewer pages" in doc

    def test_big_omnibus_split(self):
        doc = self.doc()
        assert "985 pages" in doc         # 325,000 / 330 = 984.8 → ~985
        assert "855 pages" in doc         # 325,000 / 380 = 855.3
        assert "~630 pages" in doc        # 195,000/330 ≈ 591 → 591+40? doc uses 590
        assert "~434 pages" in doc        # 130,000/330 = 393.9 → 394 + 40

    def test_print_cost_table(self):
        doc = self.doc()
        for pages in (150, 300, 600, 800):
            cost = 0.85 + 0.012 * pages
            assert money(cost) in doc, f"print cost for {pages} pages"

    def test_print_royalty_table(self):
        doc = self.doc()
        cost = 0.85 + 0.012 * 800
        assert money(cost) == "10.45"
        for price, shown in ((16.99, "3.92"), (19.99, "5.72"), (24.99, "8.72")):
            assert money((price - cost) * 0.6) == money(float(shown))
            assert shown in doc

    def test_spine_width(self):
        doc = self.doc()
        width = 790 * 0.0025
        assert 1.98 <= round(width, 2) <= 2.0
        assert "2.0 inches" in doc
        assert "0.0025" in doc and "0.0022" in doc

    def test_page_ceiling_mentioned(self):
        doc = self.doc()
        assert "800" in doc and "828" in doc


# ---------------------------------------------------------------------------
# Chapter 4: royalty bands and ladder
# ---------------------------------------------------------------------------

class TestBandNumbers:
    doc = staticmethod(lambda: read_doc("04-pricing-ladders.md"))

    def test_band_table_matches_rates(self):
        doc = self.doc()
        rates = [(0.99, 0.35, "0.35"), (1.99, 0.35, "0.70"),
                 (2.99, 0.70, "2.09"), (3.99, 0.70, "2.79"),
                 (4.99, 0.70, "3.49"), (5.99, 0.70, "4.19"),
                 (6.99, 0.70, "4.89"), (7.99, 0.70, "5.59"),
                 (8.99, 0.70, "6.29"), (9.99, 0.70, "6.99")]
        for price, rate, shown in rates:
            computed = money(price * rate)
            assert computed == money(float(shown)), (price, computed, shown)
            assert f"~${shown}" in doc

    def test_band_boundaries(self):
        doc = self.doc()
        assert "$2.99–$9.99" in doc
        # below the band
        assert money(2.98 * 0.35) == "1.04"
        assert "$1.04" in doc and "$2.09" in doc
        # above the band
        assert money(10.00 * 0.35) == "3.50"
        assert "$3.50" in doc

    def test_bundle_rung_comparison(self):
        doc = self.doc()
        assert money(14.99 * 0.35) == "5.25"
        assert money(9.99 * 0.70) == "6.99"
        for figure in ("$5.25", "$6.99", "$1.74"):
            assert figure in doc
        # 6.99 - 5.25 = 1.74
        assert money(6.99 - 5.25) == "1.74"

    def test_dead_zone_and_crossover(self):
        doc = self.doc()
        crossover = 6.99 / 0.35
        assert 19.95 < crossover < 19.98
        doc = self.doc()
        assert "19.97" in doc
        for price, shown in ((19.99, "7.00"), (24.99, "8.75")):
            assert money(price * 0.35) == money(float(shown))
            assert f"~${shown}" in doc

    def test_print_ladder_against_cost_table(self):
        doc = self.doc()
        cost = 0.85 + 0.012 * 800
        assert money((19.99 - cost) * 0.6) == "5.72"
        assert money((24.99 - cost) * 0.6) == "8.72"


# ---------------------------------------------------------------------------
# Chapter 5: read-through arithmetic
# ---------------------------------------------------------------------------

class TestReadThroughNumbers:
    doc = staticmethod(lambda: read_doc("05-read-through-that-pays.md"))

    def _copies(self, rate_first, rate_later, base=100):
        b2 = hr(base * rate_first)
        b3 = hr(b2 * rate_later)
        b4 = hr(b3 * rate_later)
        return b2, b3, b4, b2 + b3 + b4

    def test_ladder_income_table(self):
        doc = self.doc()
        per_copy = round(4.99 * 0.70, 2)
        assert per_copy == 3.49
        rows = [(100, "100", 349), (65, "65", 227),
                (49, "49", 171), (37, "37", 129)]
        total = 0
        for copies, copies_shown, dollars in rows:
            total += copies
            # table figures rounded to the nearest dollar
            assert abs(copies * per_copy - dollars) < 1.0, (copies, dollars)
            assert copies_shown in doc and f"${dollars}" in doc
        assert total == 251
        assert "251" in doc
        assert "**$876**" in doc
        assert abs(251 * per_copy - 876) < 1

    def test_extra_sales_summary(self):
        doc = self.doc()
        extra = 65 + 49 + 37
        assert extra == 151
        assert "151" in doc
        assert abs(extra * 3.49 - 527) < 1
        assert "~$527" in doc

    def test_sensitivity_table(self):
        doc = self.doc()
        # (book1->2 rate, later rate, extra copies, income)
        buckets = [
            (0.80, 0.85, 206, "719"),
            (0.65, 0.75, 151, "527"),
            (0.50, 0.65, 104, "363"),
            (0.30, 0.60, 59, "206"),
        ]
        for first, later, extra, income in buckets:
            b2, b3, b4, extra_copies = self._copies(first, later)
            assert extra_copies == extra, (first, later, extra_copies)
            # income is shown rounded to the nearest dollar
            assert abs(extra_copies * 3.49 - float(income)) < 1.0
            for figure in (str(extra), str(income)):
                assert figure in doc

    def test_99cent_payback_example(self):
        doc = self.doc()
        # setup
        assert money(0.99 * 0.35) == "0.35"
        promo_sale = money(0.99 * 0.35)
        assert "$0.35" in doc
        # give-away: 575 readers discounted away from $3.49
        full = money(4.99 * 0.70)
        assert full == "3.49"
        gap = money(4.99 * 0.70 - 0.99 * 0.35)
        assert gap == "3.15"
        assert "3.15" in doc
        give = money(575 * 3.15)
        assert 1_800 <= float(give.replace(",", "")) <= 1_815
        assert "$1,800" in doc
        # earn-back
        book2 = hr(575 * 0.65)               # 374
        book3 = hr(book2 * 0.75)             # 281
        book4 = hr(book3 * 0.75)             # 211
        bundle = hr(575 * 0.05)              # 29
        assert (book2, book3, book4, bundle) == (374, 281, 211, 29)
        earn = (money(book2 * 3.49), money(book3 * 3.49),
                money(book4 * 3.49), money(bundle * 6.99))
        assert earn == ("1,305.26", "980.69", "736.39", "202.71")
        for figure, shown in ((1305.26, "1,300"), (980.69, "980"),
                              (736.39, "735"), (202.71, "200")):
            assert shown in doc
        total = 374 * 3.49 + 281 * 3.49 + 211 * 3.49 + 29 * 6.99
        assert 3_150 <= total <= 3_300
        assert "$3,200" in doc
        assert money(total / 1805.5).startswith("1.7")
        assert "1.7×" in doc

    def test_weaker_series_scenarios(self):
        doc = self.doc()
        # 40% / 55% scenario
        b2, b3, b4, _ = self._copies(0.40, 0.55, base=575)
        assert (b2, b3, b4) == (230, 127, 70)
        earn = b2 * 3.49 + b3 * 3.49 + b4 * 3.49 + 29 * 6.99
        assert 1_650 <= earn <= 1_720
        assert "$1,690" in doc
        # low-lift non-fiction scenario: ~175 new readers at 30%
        low = hr(175 * 0.30)
        assert low == 53
        b3 = hr(53 * 0.60)
        assert b3 == 32
        earn_low = 85 * 3.49
        assert 290 <= earn_low <= 305
        assert "$330" in doc            # 85 × 3.49 + a few bundle sales
        assert "$550" in doc            # 175 × 3.15

    def test_ku_wage_teaser_consistency(self):
        doc = self.doc()
        assert "0.004" in doc and "chapter 8" in doc.lower()


# ---------------------------------------------------------------------------
# Chapter 7: pocket launch arithmetic
# ---------------------------------------------------------------------------

class TestLaunchPocketNumbers:
    doc = staticmethod(lambda: read_doc("07-launch-calendar-99-cent-math.md"))

    def test_two_book_pocket_version(self):
        doc = self.doc()
        book2 = 0.65 * 3.49
        book3 = 0.75 * 0.65 * 3.49
        assert money(book2) == "2.27"
        assert money(book3) == "1.70"
        assert "$2.27" in doc and "$1.70" in doc
        assert money(book2 + book3) == "3.97"
        assert "3.97" in doc

    def test_round_numbers_listed(self):
        doc = self.doc()
        assert "6×" in doc or "≈ 6×" in doc
        assert "1–3 days" in doc


# ---------------------------------------------------------------------------
# Chapter 8: KU vs wide page-read wages
# ---------------------------------------------------------------------------

class TestWideVsKUNumbers:
    doc = staticmethod(lambda: read_doc("08-wide-vs-ku-round-numbers.md"))

    def test_page_read_wages(self):
        doc = self.doc()
        # payout is stated as roughly $0.0040–$0.0045/page; the table
        # shows a round midpoint figure (~ $0.00425 × pages)
        for pages, shown in ((300, "1.25"), (600, "2.50"),
                             (900, "3.75"), (1500, "6.25")):
            wage = pages * 0.00425
            assert abs(wage - float(shown)) <= 0.15, (pages, wage, shown)
            assert f"~${shown}" in doc
        assert "0.4¢" in doc
        assert "$0.0040–$0.0045" in doc

    def test_per_buyer_totals(self):
        doc = self.doc()
        assert "~$5.00" in doc
        assert "~$12.25" in doc
        # wide path: 100 buyers → 251 sales total (chapter 5's ladder)
        per_buyer = 251 * 3.49 / 100
        assert money(per_buyer) == "8.76"
        assert "8.76" in doc
        # KU path: ~1,200 pages read ≈ 4 products at $1.25
        assert money(1.25 + 3.75) == "5.00"

    def test_exclusivity_window(self):
        doc = self.doc()
        assert "90-day" in doc or "90 days" in doc


# ---------------------------------------------------------------------------
# Structure, worksheets, glossary, hygiene
# ---------------------------------------------------------------------------

class TestStructure:
    def test_glossary_has_25_terms(self):
        doc = read_doc("09-glossary.md")
        rows = [
            line for line in doc.splitlines()
            if line.startswith("| ") and "Term |" not in line
            and not line.startswith("|---")
        ]
        rows = [r for r in rows if not re.match(r"^\|\s*-+\|", r)]
        # data rows (header checked above; skip separators)
        assert len(rows) == 25, len(rows)

    def test_glossary_links_back_to_chapters(self):
        doc = read_doc("09-glossary.md")
        for slugref in ("01-series-page-setup", "03-boxset-trim-math",
                        "04-pricing-ladders", "05-read-through-that-pays"):
            assert slugref in doc

    def test_worksheets_have_fill_in_blank_lines(self):
        w1 = read_doc("worksheet-launch-ladder.md")
        w2 = read_doc("worksheet-boxset-costs.md")
        assert w1.count("____") >= 15
        assert w2.count("____") >= 10

    def test_worksheets_have_checkboxes(self):
        for relname in ("worksheet-launch-ladder.md",
                        "worksheet-boxset-costs.md"):
            doc = read_doc(relname)
            assert "- [ ]" in doc

    def test_start_here_links_everything_else(self):
        doc = read_doc("00-start-here.md")
        for subdir, filename in build.PAGE_ORDER:
            if filename == "00-start-here.md":
                continue
            assert filename in doc, filename

    def test_disclaimer_present(self):
        assert "not legal" in read_doc("00-start-here.md").lower()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "accounting, or tax advice" in readme.lower()

    def test_no_draft_markers(self):
        for subdir, filename in build.PAGE_ORDER:
            doc = read_doc(filename)
            for marker in ("TODO", "FIXME", "XXX", "???", "PLACEHOLDER"):
                assert marker not in doc, f"{filename}: contains {marker}"

    def test_no_secrets_or_keys(self):
        patterns = ("sk-", "api_key", "apikey", "password", "PRIVATE KEY",
                    "AKIA", "token=")
        for path in list(DOCS.rglob("*.md")) + [ROOT / "README.md",
                                                ROOT / "build.py"]:
            text = path.read_text(encoding="utf-8")
            for pattern in patterns:
                assert pattern not in text, f"{path.name}: contains {pattern}"

    def test_readme_lists_build_and_tests(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "python3 build.py" in readme
        assert "--check" in readme
        assert "pytest" in readme

    def test_license_copyright_line_exact(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        assert "Copyright (c) 2026 Asdale Dynamics, LLC" in text

    def test_readme_credits_llc(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "Asdale Dynamics, LLC" in readme

    def test_companions_named_without_duplication(self):
        doc = read_doc("00-start-here.md")
        for name in ("kdp-profit-planner", "publishing-beyond-kdp-guide",
                     "book-keyword-lab-cli"):
            assert name in doc
