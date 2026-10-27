#!/usr/bin/env python3
"""Build the static HTML site for series-and-boxset-kdp-guide.

Converts the Markdown under docs/ into site/*.html with shared
navigation, using only the Python standard library. Local-first: no
network access, no external dependencies, nothing leaves the folder.

Usage:
    python3 build.py            # build the site into ./site
    python3 build.py --check    # build, then verify outputs and links
    python3 build.py --out DIR  # write to a different directory
"""

import argparse
import html
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
ASSETS = ROOT / "assets"
DEFAULT_OUT = ROOT / "site"

SITE_NAME = "Beyond One Book (KDP)"
SITE_TAGLINE = (
    "Series pages, boxsets, pricing ladders, read-through, and the "
    "99-cent launch — in plain English. By Asdale Dynamics, LLC."
)
FOOTER = (
    "Beyond One Book (KDP) · planning guide, not legal, accounting, or "
    "tax advice · verify current rules in your KDP dashboard · "
    "MIT License"
)
COPYRIGHT = "Copyright (c) 2026 Asdale Dynamics, LLC"

# (docs-subdirectory, filename), in reading order ---------------------------

PAGE_ORDER = [
    ("", "00-start-here.md"),
    ("", "01-series-page-setup.md"),
    ("", "02-boxset-build-steps.md"),
    ("", "03-boxset-trim-math.md"),
    ("", "04-pricing-ladders.md"),
    ("", "05-read-through-that-pays.md"),
    ("", "06-series-keywords.md"),
    ("", "07-launch-calendar-99-cent-math.md"),
    ("", "08-wide-vs-ku-round-numbers.md"),
    ("", "09-glossary.md"),
    ("worksheets", "worksheet-launch-ladder.md"),
    ("worksheets", "worksheet-boxset-costs.md"),
]

PAGE_TITLES = {
    "00-start-here": "Start here",
    "01-series-page-setup": "Series page setup",
    "02-boxset-build-steps": "Boxset build steps",
    "03-boxset-trim-math": "Boxset trim math",
    "04-pricing-ladders": "Pricing ladders",
    "05-read-through-that-pays": "Read-through that pays",
    "06-series-keywords": "Per-book vs omnibus keywords",
    "07-launch-calendar-99-cent-math": "Launch calendar and 99-cent math",
    "08-wide-vs-ku-round-numbers": "Wide vs KU round numbers",
    "09-glossary": "Glossary",
    "worksheets-worksheet-launch-ladder": "Worksheet: launch ladder",
    "worksheets-worksheet-boxset-costs": "Worksheet: boxset costs",
}


def page_slug(subdir: str, filename: str) -> str:
    """Strip .md, flatten 'worksheets/x' to 'worksheets-x', + '.html'."""
    base = filename[:-3]
    return (subdir + "-" + base + ".html") if subdir else base + ".html"


def page_title(subdir: str, filename: str) -> str:
    base = filename[:-3]
    key = (subdir + "-" + base) if subdir else base
    if key not in PAGE_TITLES:
        raise KeyError(
            f"No title registered for {subdir}/{filename} "
            f"(key {key!r}) — add it to PAGE_TITLES."
        )
    return PAGE_TITLES[key]


# ---------------------------------------------------------------------------
# Markdown -> HTML (small, purpose-built converter for the docs subset)
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Heading text -> anchor id."""
    slug = re.sub(r"<[^>]+>", "", text)
    slug = re.sub(r"[^a-z0-9 -]", "", slug.lower())
    slug = re.sub(r"[\s-]+", "-", slug.strip())
    return ("h-" + slug) if slug else "h"


def _is_known_doc(relpath: str) -> bool:
    return any(
        (relpath == fn) if subdir == "" else (relpath == subdir + "/" + fn)
        for subdir, fn in PAGE_ORDER
    )


def resolve_md_target(target: str, subdir: str) -> str:
    """Resolve a docs-relative .md target to docs-root form.

    Tries the link as-is (docs-root relative) and, if the link came from
    a worksheets page, also relative to that page's folder, so
    ``worksheet-launch-ladder.md`` inside worksheets/ resolves while
    ``00-start-here.md`` still finds the root chapter.
    """
    candidates = [target]
    if subdir and "/" not in target:
        candidates.insert(0, subdir + "/" + target)
    for cand in candidates:
        if _is_known_doc(cand):
            return cand
    return candidates[-1]


def _inline(text: str, subdir: str = "") -> str:
    """Render inline markdown to HTML.

    ``text`` must already be HTML-escaped; inline-code spans are stashed
    (their contents were escaped by the caller) so formatting never
    applies inside them.
    """
    stashed: list = []

    def stash_code(match):
        stashed.append(match.group(1))
        return f"\x00{len(stashed) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash_code, text)

    def render_link(match):
        label, target = match.group(1), match.group(2)
        target = target.strip()
        if target.endswith(".md") and not re.match(r"^[a-z]+://", target):
            # docs-relative path -> flat site page:
            # worksheet-launch-ladder.md from worksheets/ -> worksheets-...html
            target = resolve_md_target(target, subdir)
            target = target[:-3].replace("/", "-") + ".html"
        return f'<a href="{html.escape(target, quote=True)}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", render_link, text)

    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text, flags=re.S)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)

    def unstash(match):
        return f"<code>{stashed[int(match.group(1))]}</code>"

    return re.sub("\x00(\\d+)\x00", unstash, text)


class _Blocks:
    """State machine for the line-oriented converter."""

    def __init__(self, subdir: str = ""):
        self.subdir = subdir
        self.out: list = []
        self.paragraph: list = []   # raw source fragments of current para
        self.list_tag: str | None = None
        self.li_parts: list | None = None
        self.li_checked = False
        self.item_indent = 0

    # -- block closers ---------------------------------------------------

    def close_paragraph(self) -> None:
        if self.paragraph:
            text = html.escape(" ".join(self.paragraph))
            self.out.append(f"<p>{_inline(text, self.subdir)}</p>")
            self.paragraph.clear()

    def flush_item(self) -> None:
        if self.li_parts is not None:
            text = html.escape(" ".join(self.li_parts))
            cls = ' class="checked"' if self.li_checked else ""
            self.out.append(f"<li{cls}>{_inline(text, self.subdir)}</li>")
            self.li_parts = None
            self.li_checked = False

    def close_list(self) -> None:
        if self.list_tag:
            self.flush_item()
            self.out.append(f"</{self.list_tag}>")
            self.list_tag = None

    def open_list(self, tag: str) -> None:
        self.flush_item()
        if self.list_tag != tag:
            self.close_paragraph()
            if self.list_tag is not None:
                self.out.append(f"</{self.list_tag}>")
            self.out.append(f"<{tag}>")
        self.list_tag = tag

    def close_blocks(self) -> None:
        self.close_paragraph()
        self.close_list()


def md_to_html(md_text: str, subdir: str = "") -> str:
    """Convert the subset of Markdown used in docs/ into HTML."""
    b = _Blocks(subdir)
    lines = md_text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Fenced code block ------------------------------------------------
        if stripped.startswith("```") or stripped.startswith("~~~"):
            b.close_blocks()
            i += 1
            block = []
            while i < len(lines) and not (
                lines[i].strip().startswith("```")
                or lines[i].strip().startswith("~~~")
            ):
                block.append(lines[i])
                i += 1
            i += 1  # skip the closing fence
            b.out.append(
                "<pre><code>" + html.escape("\n".join(block)) + "</code></pre>"
            )
            continue

        # Blank line --------------------------------------------------------
        if not stripped:
            b.close_blocks()
            i += 1
            continue

        # Heading ------------------------------------------------------------
        match = re.match(r"^(#{1,4})\s+(.*)$", line)
        if match:
            b.close_blocks()
            level = len(match.group(1))
            body = _inline(html.escape(match.group(2)), subdir)
            b.out.append(f'<h{level} id="{_slugify(body)}">{body}</h{level}>')
            i += 1
            continue

        # Horizontal rule -----------------------------------------------------
        if re.fullmatch(r"(\*\*\*|---|___)\s*", stripped):
            b.close_blocks()
            b.out.append("<hr>")
            i += 1
            continue

        # GFM pipe table -------------------------------------------------------
        if (
            stripped.startswith("|")
            and stripped.endswith("|")
            and i + 1 < len(lines)
            and re.fullmatch(r"\|[\s\-:|]+\|", lines[i + 1].strip())
        ):
            b.close_blocks()
            header = [c.strip() for c in stripped.strip("|").split("|")]
            aligns = [
                c.strip() for c in lines[i + 1].strip().strip("|").split("|")
            ]
            b.out.append("<table><thead><tr>")
            for idx, cell in enumerate(header):
                align = ""
                if idx < len(aligns):
                    a = aligns[idx]
                    if a.startswith(":") and a.endswith(":"):
                        align = ' style="text-align:center"'
                    elif a.endswith(":"):
                        align = ' style="text-align:right"'
                b.out.append(f"<th{align}>{_inline(html.escape(cell), subdir)}</th>")
            b.out.append("</tr></thead><tbody>")
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [
                    c.strip() for c in lines[i].strip().strip("|").split("|")
                ]
                b.out.append("<tr>")
                for idx in range(len(header)):
                    cell = cells[idx] if idx < len(cells) else ""
                    b.out.append(f"<td>{_inline(html.escape(cell), subdir)}</td>")
                b.out.append("</tr>")
                i += 1
            b.out.append("</tbody></table>")
            continue

        # Blockquote -----------------------------------------------------------
        if stripped.startswith(">"):
            b.close_blocks()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            body = _inline(html.escape(" ".join(q for q in quote if q)), subdir)
            b.out.append(f"<blockquote>{body}</blockquote>")
            continue

        # Checkbox list items ----------------------------------------------
        check = re.match(r"^(\s*)[-*] \[([ xX])\]\s+(.*)$", line)
        if check:
            b.open_list("ul")
            b.item_indent = len(check.group(1))
            b.li_checked = check.group(2).lower() == "x"
            b.li_parts = [check.group(3).strip()]
            i += 1
            continue

        # Unordered / ordered list items --------------------------------------
        ul = re.match(r"^(\s*)[-*] (?!\[)(.*)$", line)
        ol = re.match(r"^(\s*)\d+[.)]\s+(.*)$", line)
        if ul or ol:
            kind = "ul" if ul else "ol"
            b.open_list(kind)
            marker = ul if ul else ol
            b.item_indent = len(marker.group(1))
            b.li_parts = [(ul or ol).group(2).strip()]
            i += 1
            continue

        # Continuation of a list item -----------------------------------------
        if b.li_parts is not None and (
            line.startswith("  ") or line.startswith("\t")
        ):
            b.li_parts.append(stripped)
            i += 1
            continue

        # Paragraph continuation or start ---------------------------------------
        if b.list_tag is not None and not line.startswith(" "):
            # unindented text that follows a list ends the list
            b.close_list()
        b.paragraph.append(stripped)
        i += 1

    b.close_blocks()
    return "\n".join(b.out)


# ---------------------------------------------------------------------------
# Site assembly
# ---------------------------------------------------------------------------

def _sidebar(current: str) -> str:
    parts = ['<nav class="toc" aria-label="Chapter navigation">']
    parts.append('<div class="toc-title">Contents</div>')
    parts.append("<ul>")
    for subdir, filename in PAGE_ORDER:
        slug = page_slug(subdir, filename)
        title = page_title(subdir, filename)
        cls = ' class="ws"' if subdir else ""
        active = " active" if slug == current else ""
        parts.append(f'<li{cls}{active}><a href="{slug}">{title}</a></li>')
    parts.append("</ul></nav>")
    return "\n".join(parts)


def _next_page(page_idx: int) -> tuple | None:
    if page_idx + 1 < len(PAGE_ORDER):
        return page_slug(*PAGE_ORDER[page_idx + 1]), page_title(
            *PAGE_ORDER[page_idx + 1]
        )
    return None


def _render_page(subdir: str, filename: str, body_html: str) -> str:
    idx = PAGE_ORDER.index((subdir, filename))
    slug = page_slug(subdir, filename)
    title = page_title(subdir, filename)

    prev_link = ""
    if idx > 0:
        prev_slug = page_slug(*PAGE_ORDER[idx - 1])
        prev_title = page_title(*PAGE_ORDER[idx - 1])
        prev_link = f'<a href="{prev_slug}">&larr; {prev_title}</a>'

    next_link = ""
    nxt = _next_page(idx)
    if nxt:
        next_slug, next_title = nxt
        next_link = f'<a href="{next_slug}">{next_title} &rarr;</a>'

    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="en">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append(
        '<meta name="viewport" content="width=device-width, '
        'initial-scale=1">'
    )
    parts.append(
        f"<title>{html.escape(title)} · {html.escape(SITE_NAME)}</title>"
    )
    parts.append(
        '<meta name="generator" content="local build.py, '
        'standard library only">'
    )
    parts.append('<link rel="stylesheet" href="base.css">')
    parts.append("</head>")
    parts.append("<body>")
    parts.append('<header class="topbar">')
    parts.append('<div class="topbar-inner">')
    parts.append(f'<a class="site-name" href="index.html">{SITE_NAME}</a>')
    parts.append(f'<span class="site-sub">{SITE_TAGLINE}</span>')
    parts.append("</div>")
    parts.append("</header>")
    parts.append('<div class="page">')
    parts.append(_sidebar(slug))
    parts.append('<main class="content">')
    parts.append(body_html)
    if prev_link or next_link:
        parts.append('<div class="pager">')
        parts.append(prev_link or "<span></span>")
        parts.append('<span class="spacer"></span>')
        parts.append(next_link or "<span></span>")
        parts.append("</div>")
    parts.append("</main>")
    parts.append("</div>")
    parts.append('<footer class="foot">')
    parts.append(f"{html.escape(FOOTER)} · {html.escape(COPYRIGHT)}")
    parts.append("</footer>")
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)


def render_subdir_page(subdir: str, filename: str, docs_dir: Path) -> str:
    md_path = docs_dir / subdir / filename if subdir else docs_dir / filename
    md_text = md_path.read_text(encoding="utf-8")
    return _render_page(subdir, filename, md_to_html(md_text, subdir))


def build_index(doc_pages: list) -> str:
    """Build index.html: hero + a card per chapter/worksheet."""
    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="en">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append(
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
    )
    parts.append(f"<title>{html.escape(SITE_NAME)}</title>")
    parts.append('<link rel="stylesheet" href="base.css">')
    parts.append("</head>")
    parts.append("<body>")
    parts.append('<header class="topbar">')
    parts.append('<div class="topbar-inner">')
    parts.append(f'<span class="site-name">{SITE_NAME}</span>')
    parts.append(f'<span class="site-sub">{SITE_TAGLINE}</span>')
    parts.append("</div></header>")
    parts.append('<div class="page"><main class="content">')

    parts.append('<section class="hero">')
    parts.append("<h1>Beyond One Book (KDP)</h1>")
    parts.append(
        "<p>A plain-English author manual for the trip <em>past</em> a "
        "single title: series pages, boxsets and the trim math that "
        "decides whether a print bundle fits, pricing ladders across a "
        "series, read-through that pays, launch calendars with real "
        "arithmetic, and the wide-vs-KU decision in round numbers. "
        "Every figure is a planning sketch you verify against the KDP "
        "help pages — nothing here is legal, accounting, or tax advice.</p>"
    )
    parts.append(
        '<p class="meta">Built by Asdale Dynamics, LLC · MIT License · '
        "this site was generated locally by build.py · "
        '<a href="00-start-here.html">Start here</a></p>'
    )
    parts.append("</section>")

    parts.append('<div class="cardgrid">')
    for subdir, filename in doc_pages[1:]:
        slug = page_slug(subdir, filename)
        title = page_title(subdir, filename)
        blurb = BLURBS.get(filename, "")
        parts.append('<div class="card">')
        parts.append(
            f'<h2><a href="{slug}">{html.escape(title)}</a></h2>'
        )
        parts.append(f"<p>{html.escape(blurb)}</p>")
        parts.append("</div>")
    parts.append("</div>")

    parts.append('<section class="companions">')
    parts.append("<h2>Companion tools (not repeated here)</h2>")
    parts.append("<ul>")
    for name, line in COMPANIONS:
        parts.append(f"<li><strong>{name}</strong> — {line}</li>")
    parts.append("</ul>")
    parts.append("</section>")

    parts.append("</main></div>")
    parts.append('<footer class="foot">')
    parts.append(f"{COPYRIGHT} · {html.escape(FOOTER)}")
    parts.append("</footer>")
    parts.append("</body></html>")
    return "\n".join(parts)


BLURBS = {
    "01-series-page-setup.md": (
        "How the store's series page is assembled from the series name "
        "and number fields — naming rules, numbering, the omnibus "
        "wrinkle, and a 10-minute checklist."
    ),
    "02-boxset-build-steps.md": (
        "What goes in a bundle, enrollment choices per product, and the "
        "12-step build order for the e-book and print boxsets."
    ),
    "03-boxset-trim-math.md": (
        "Words-per-page tables by trim, the ~800-page print ceiling, "
        "worked trilogy and omnibus examples, plus print cost/royalty "
        "and spine-width tables."
    ),
    "04-pricing-ladders.md": (
        "Rungs from the 99-cent door to the print bundle, the 70%/35% "
        "e-book bands, and why $9.99 pays a bundle more than $14.99."
    ),
    "05-read-through-that-pays.md": (
        "The compounding that turns one buyer into 2–3 sales, the "
        "back-matter plumbing, and the pay-back arithmetic of a 99-cent "
        "promo week."
    ),
    "06-series-keywords.md": (
        "Which search intents go on each individual book, which belong "
        "on the omnibus, and what to never duplicate across products."
    ),
    "07-launch-calendar-99-cent-math.md": (
        "A week-by-week launch rhythm and the pocket arithmetic of the "
        "99-cent week — why the dip runs after the full-price launch."
    ),
    "08-wide-vs-ku-round-numbers.md": (
        "Page-read wages at 0.4¢ vs wide margins per reader — the "
        "trade-off in round numbers, plus a five-line decision rubric."
    ),
    "09-glossary.md": (
        "25 series-and-boxset terms in one line each, pointing at the "
        "chapter where they matter."
    ),
    "worksheet-launch-ladder.md": (
        "Fill-in: series inventory, the ladder, a promo calendar, and "
        "the pay-back boxes for your own 99-cent week."
    ),
    "worksheet-boxset-costs.md": (
        "Fill-in: words-to-pages planning, the print-ceiling check, "
        "cost/royalty rows for your bundle, and a decision box."
    ),
}

COMPANIONS = [
    (
        "kdp-profit-planner",
        "the exact per-book math: pages by trim, printing cost, "
        "royalty per unit, break-even, price scans, projections.",
    ),
    (
        "publishing-beyond-kdp-guide",
        "rights, ISBNs, non-Amazon channels, libraries, audiobooks, "
        "direct sales, author taxes.",
    ),
    (
        "book-keyword-lab-cli",
        "scores and drafts your seven keyword slots; chapter 6 covers "
        "only the series-vs-omnibus split.",
    ),
    (
        "kdp-interior-templates / kdp-cover-bleed-checker-cli",
        "the print-ready interior and cover art that chapter 2's build "
        "steps assemble into a bundle.",
    ),
    (
        "kdp-sales-tracker-webapp / arc-review-tracker-webapp",
        "where your launch-week numbers and ARC replies actually live.",
    ),
]


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def check_links(site_dir: Path) -> list:
    """Return a sorted, deduplicated list of broken internal-link problems."""
    problems = []
    pages = sorted(site_dir.glob("*.html"))
    for page in pages:
        text = page.read_text(encoding="utf-8")
        page_ids = set(re.findall(r'id="([^"]+)"', text))
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            if href.startswith("#"):
                if href[1:] not in page_ids:
                    problems.append(f"{page.name}: missing anchor {href!r}")
                continue
            target, _, anchor = href.partition("#")
            if not (target.endswith(".html") or target.endswith(".css")):
                problems.append(f"{page.name}: odd link target {href!r}")
                continue
            if not (site_dir / target).exists():
                problems.append(f"{page.name}: broken internal link {href!r}")
                continue
            if target.endswith(".html") and anchor:
                doc = (site_dir / target).read_text(encoding="utf-8")
                if f'id="{anchor}"' not in doc:
                    problems.append(
                        f"{page.name}: link to missing anchor {href!r}"
                    )
    return sorted(set(problems))


def expected_slugs() -> set:
    expected = {"index.html", "base.css"}
    for subdir, filename in PAGE_ORDER:
        expected.add(page_slug(subdir, filename))
    return expected


def run_check(site_dir: Path) -> int:
    problems = []
    expected = expected_slugs()
    for name in sorted(expected):
        path = site_dir / name
        if not path.exists():
            problems.append(f"missing expected file: {name}")
            continue
        size = path.stat().st_size
        if size < 500:
            problems.append(f"suspiciously small file: {name} ({size} bytes)")
    if not problems:
        problems.extend(check_links(site_dir))
    if problems:
        print("CHECK FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(
        f"OK: {len(expected)} expected files present, links resolve, "
        f"nothing suspicious in {site_dir}"
    )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUT,
        help="output directory (default: ./site)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="build, then verify expected outputs and internal links",
    )
    args = parser.parse_args(argv)

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    for subdir, filename in PAGE_ORDER:
        html_text = render_subdir_page(subdir, filename, DOCS)
        out_path = out_dir / page_slug(subdir, filename)
        out_path.write_text(html_text, encoding="utf-8")

    (out_dir / "index.html").write_text(
        build_index(PAGE_ORDER), encoding="utf-8"
    )
    css = ASSETS / "base.css"
    if css.exists():
        shutil.copy(css, out_dir / "base.css")

    print(
        f"Built {len(PAGE_ORDER)} pages + index into {out_dir} "
        f"({sum(1 for _ in out_dir.glob('*.html'))} html files, "
        f"site built locally — no network used)."
    )

    if args.check:
        return run_check(out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
