"""Tests for build.py: converter units, site build, link checking.

Run from the project root with:  python3 -m pytest tests/ -v
"""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build  # noqa: E402


# ---------------------------------------------------------------------------
# Converter unit tests
# ---------------------------------------------------------------------------

class TestHeadings:
    def test_h1_gets_anchor_id(self):
        out = build.md_to_html("# Hello World")
        assert out == '<h1 id="h-hello-world">Hello World</h1>'

    def test_heading_levels(self):
        out = build.md_to_html("## Two\n\n### Three\n\n#### Four")
        for level in (2, 3, 4):
            assert f"<h{level} " in out

    def test_heading_with_inline_formatting(self):
        out = build.md_to_html("## A **bold** title")
        assert "<strong>bold</strong>" in out

    def test_slug_ignores_python_headings(self):
        out = build.md_to_html("## Pricing ladders (KDP-only)")
        assert 'id="h-pricing-ladders-kdp-only"' in out


class TestParagraphs:
    def test_soft_wrap_joins_lines(self):
        out = build.md_to_html("first line\nsecond line")
        assert "<p>first line second line</p>" in out

    def test_bold_across_wrapped_lines(self):
        out = build.md_to_html("text **bold across\nwrapped lines** ends")
        assert "<strong>bold across wrapped lines</strong>" in out

    def test_italic(self):
        out = build.md_to_html("say *this quietly*")
        assert "<em>this quietly</em>" in out

    def test_blank_line_separates_paragraphs(self):
        out = build.md_to_html("one\n\n\nthree")
        assert out.count("<p>") == 2

    def test_html_escaped(self):
        out = build.md_to_html("a <script>tag</script>")
        assert "<script>" not in out
        assert "&lt;script&gt;" in out


class TestInlineCode:
    def test_code_span(self):
        out = build.md_to_html("run `python3 build.py` now")
        assert "<code>python3 build.py</code>" in out

    def test_code_protects_markdown(self):
        out = build.md_to_html("use `**not bold**` here")
        assert "<strong>" not in out
        assert "<code>**not bold**</code>" in out

    def test_html_escaped_in_code(self):
        out = build.md_to_html("tag `<div>`")
        assert "&lt;div&gt;" in out


class TestLinks:
    def test_md_link_becomes_html_link(self):
        out = build.md_to_html("see [chapter two](01-series-page-setup.md)")
        assert 'href="01-series-page-setup.html"' in out

    def test_worksheet_link_maps_to_flat_slug(self):
        out = build.md_to_html("see [W1](worksheets/worksheet-launch-ladder.md)")
        assert 'href="worksheets-worksheet-launch-ladder.html"' in out

    def test_worksheet_link_from_worksheets_dir(self):
        out = build.md_to_html(
            "back and [forth](worksheet-boxset-costs.md)",
            subdir="worksheets",
        )
        assert 'href="worksheets-worksheet-boxset-costs.html"' in out

    def test_root_link_from_worksheets_dir(self):
        out = build.md_to_html(
            "back to [start](00-start-here.md)", subdir="worksheets"
        )
        assert 'href="00-start-here.html"' in out

    def test_external_link_untouched(self):
        out = build.md_to_html(
            "[hub](https://dylanasdale.github.io)")
        assert 'href="https://dylanasdale.github.io"' in out

    def test_link_text_keeps_formatting(self):
        out = build.md_to_html("[**bold** link](01-series-page-setup.md)")
        assert "<a href=" in out and "bold" in out


class TestLists:
    def test_bullet_list(self):
        out = build.md_to_html("- one\n- two")
        assert "<ul>" in out and "<li>one</li>" in out and "</ul>" in out

    def test_ordered_list(self):
        out = build.md_to_html("1. one\n2. two")
        assert "<ol>" in out and "<li>one</li>" in out and "</ol>" in out

    def test_multiline_item_joins(self):
        out = build.md_to_html("- first\n  continued\n- second")
        assert "<li>first continued</li>" in out

    def test_checkbox_items(self):
        out = build.md_to_html("- [ ] to do\n- [x] done")
        assert '<li class="checked">done</li>' in out
        assert "<li>to do</li>" in out

    def test_numbered_steps_with_continuation(self):
        out = build.md_to_html("1. **Step one** with\n   detail\n2. next")
        assert "<li><strong>Step one</strong> with detail</li>" in out


class TestTables:
    def test_pipe_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        out = build.md_to_html(md)
        assert "<table><thead><tr>" in out
        assert "<th>A</th>" in out and "<th>B</th>" in out
        assert "</tr></thead><tbody>" in out
        assert "<td>1</td>" in out and "<td>2</td>" in out
        assert "</tbody></table>" in out

    def test_alignment(self):
        md = "| A | B |\n|--:|---|\n| 1 | 2 |"
        out = build.md_to_html(md)
        assert '<th style="text-align:right">A</th>' in out

    def test_table_cell_inline_formatting(self):
        md = "| A |\n|---|\n| **bold** |"
        out = build.md_to_html(md)
        assert "<td><strong>bold</strong></td>" in out

    def test_row_short_fills_blanks(self):
        md = "| A | B |\n|---|---|\n| 1 |"
        out = build.md_to_html(md)
        assert "<td></td>" in out


class TestFencesAndQuotes:
    def test_fenced_code_preserved(self):
        out = build.md_to_html("```text\nplain lines kept\n```")
        assert "plain lines kept" in out
        assert "<pre><code>" in out

    def test_fenced_code_escapes_html(self):
        out = build.md_to_html("```text\n<b>no</b>\n```")
        assert "&lt;b&gt;" in out

    def test_blockquote(self):
        out = build.md_to_html("> wise words")
        assert "<blockquote>wise words</blockquote>" in out

    def test_hr(self):
        out = build.md_to_html("before\n\n---\n\nafter")
        assert "<hr>" in out


# ---------------------------------------------------------------------------
# Page plumbing
# ---------------------------------------------------------------------------

class TestPagePlumbing:
    def test_every_page_has_title(self):
        for subdir, filename in build.PAGE_ORDER:
            assert build.page_title(subdir, filename)

    def test_slugs_unique(self):
        slugs = [build.page_slug(s, f) for s, f in build.PAGE_ORDER]
        assert len(slugs) == len(set(slugs))

    def test_output_names_flat(self):
        assert build.page_slug("worksheets", "worksheet-launch-ladder.md") == (
            "worksheets-worksheet-launch-ladder.html"
        )
        assert build.page_slug("", "09-glossary.md") == "09-glossary.html"

    def test_missing_title_raises(self):
        with pytest.raises(KeyError):
            build.page_title("", "missing-file.md")


def test_render_page_contains_sidebar_and_pager(tmp_path):
    html_text = build._render_page("", "00-start-here.md", "<p>x</p>")
    assert 'class="toc"' in html_text
    assert 'class="pager"' in html_text
    assert "01-series-page-setup.html" in html_text
    # the final page has no next link
    last = build._render_page("worksheets", "worksheet-boxset-costs.md", "<p>x</p>")
    assert "&rarr;" not in last
    # the glossary still has worksheets after it
    gloss = build._render_page("", "09-glossary.md", "<p>x</p>")
    assert "&rarr;" in gloss


# ---------------------------------------------------------------------------
# Full build (e2e) and link checking
# ---------------------------------------------------------------------------

class TestSiteBuild:
    def test_full_build_into_tmp(self, tmp_path):
        code = build.main(["--out", str(tmp_path)])
        assert code == 0
        expected = build.expected_slugs()
        for name in expected:
            path = tmp_path / name
            assert path.exists(), f"missing {name}"
            assert path.stat().st_size > 500, f"too small: {name}"

    def test_index_lists_all_pages(self, tmp_path):
        build.main(["--out", str(tmp_path)])
        index = (tmp_path / "index.html").read_text(encoding="utf-8")
        for subdir, filename in build.PAGE_ORDER:
            slug = build.page_slug(subdir, filename)
            assert f'href="{slug}"' in index

    def test_chapter_sidebar_links_to_glossary(self, tmp_path):
        build.main(["--out", str(tmp_path)])
        chapter = (tmp_path / "04-pricing-ladders.html").read_text(
            encoding="utf-8"
        )
        for name in (
            "00-start-here.html", "09-glossary.html",
            "worksheets-worksheet-launch-ladder.html",
        ):
            assert f'href="{name}"' in chapter

        worksheet = (
            tmp_path / "worksheets-worksheet-launch-ladder.html"
        ).read_text(encoding="utf-8")
        assert 'href="worksheets-worksheet-boxset-costs.html"' in worksheet
        # a worksheet links back to the start page via root-relative path
        assert 'href="00-start-here.html"' in worksheet

    def test_no_broken_links(self, tmp_path):
        build.main(["--out", str(tmp_path)])
        assert build.check_links(tmp_path) == []

    def test_run_check_reports_missing(self, tmp_path):
        build.main(["--out", str(tmp_path)])
        (tmp_path / "09-glossary.html").unlink()
        # rebuild glossary as empty so only the check finds the hole
        problems = build.check_links(tmp_path)
        # glossary is referenced from other pages; its absence shows up
        # only in run_check (expected files), which we test directly:
        code = build.run_check(tmp_path)
        assert code == 1

    def test_check_ok_on_fresh_build(self, tmp_path):
        assert build.main(["--out", str(tmp_path), "--check"]) == 0


class TestLinkChecker:
    def _make_site(self, tmp_path):
        (tmp_path / "a.html").write_text(
            '<div id="sec">top</div><a href="b.html">b</a><a href="c.html">c</a>',
            encoding="utf-8",
        )
        (tmp_path / "b.html").write_text(
            '<a href="a.html#sec">sec</a>', encoding="utf-8",
        )

    def test_links_resolve(self, tmp_path):
        self._make_site(tmp_path)
        (tmp_path / "c.html").write_text("y", encoding="utf-8")
        assert build.check_links(tmp_path) == []

    def test_missing_target_found(self, tmp_path):
        self._make_site(tmp_path)
        problems = build.check_links(tmp_path)
        assert any("c.html" in p for p in problems)

    def test_missing_anchor_found(self, tmp_path):
        self._make_site(tmp_path)
        (tmp_path / "b.html").write_text(
            '<a href="a.html#missing">sec</a>', encoding="utf-8"
        )
        problems = build.check_links(tmp_path)
        assert any("#missing" in p for p in problems)

    def test_page_anchor_respected(self, tmp_path):
        self._make_site(tmp_path)
        (tmp_path / "c.html").write_text("y", encoding="utf-8")
        assert build.check_links(tmp_path) == []
