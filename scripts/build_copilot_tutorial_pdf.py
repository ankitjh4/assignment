#!/usr/bin/env python3
"""Build a simple PDF from docs/copilot-tutorial-for-students.md.

This script intentionally avoids third-party dependencies because the
assignment environment may not include pandoc, LaTeX, or ReportLab.
It implements the small subset of PDF needed for a classroom handout.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "copilot-tutorial-for-students.md"
OUTPUT = ROOT / "docs" / "GitHub-Copilot-Tutorial-for-Students.pdf"

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT = 54
RIGHT = 54
TOP = 48
BOTTOM = 42
BODY_SIZE = 10.5
BODY_LEADING = 13.2
CODE_SIZE = 9.5
CODE_LEADING = 12
TITLE_SIZE = 22
H1_SIZE = 16
H2_SIZE = 13


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def strip_inline_markup(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]*)\*", r"\1", text)
    return text


class PdfBuilder:
    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.lines: list[str] = []
        self.y = TOP
        self.page_no = 0
        self.in_code = False

    def new_page(self) -> None:
        if self.lines:
            self._footer()
            self.pages.append(self.lines)
        self.page_no += 1
        self.lines = []
        self.y = TOP

    def finish(self) -> None:
        if self.lines:
            self._footer()
            self.pages.append(self.lines)

    def _footer(self) -> None:
        footer = f"GitHub Copilot Tutorial for Students  |  {self.page_no}"
        self._raw_text(LEFT, 30, footer, "F1", 8)

    def ensure_space(self, needed: float) -> None:
        if self.y + needed > PAGE_HEIGHT - BOTTOM:
            self.new_page()

    def _raw_text(self, x: float, y_from_bottom: float, text: str, font: str, size: float) -> None:
        safe = escape_pdf_text(text)
        self.lines.append(f"BT /{font} {size:g} Tf {x:g} {y_from_bottom:g} Td ({safe}) Tj ET")

    def add_text_line(self, text: str, font: str = "F1", size: float = BODY_SIZE, leading: float = BODY_LEADING) -> None:
        self.ensure_space(leading)
        y_bottom = PAGE_HEIGHT - self.y
        self._raw_text(LEFT, y_bottom, text, font, size)
        self.y += leading

    def add_blank(self, height: float = 7) -> None:
        self.ensure_space(height)
        self.y += height

    def add_heading(self, text: str, level: int) -> None:
        self.add_blank(5 if self.y > TOP else 0)
        if level == 1:
            self.add_wrapped(text, width=48, font="F2", size=TITLE_SIZE, leading=27)
            self.add_blank(10)
        elif level == 2:
            self.add_wrapped(text, width=68, font="F2", size=H1_SIZE, leading=21)
            self.add_blank(5)
        else:
            self.add_wrapped(text, width=78, font="F2", size=H2_SIZE, leading=17)
            self.add_blank(3)

    def add_wrapped(
        self,
        text: str,
        *,
        width: int = 100,
        font: str = "F1",
        size: float = BODY_SIZE,
        leading: float = BODY_LEADING,
        indent: str = "",
    ) -> None:
        text = strip_inline_markup(text)
        wrapped = textwrap.wrap(
            text,
            width=width,
            initial_indent=indent,
            subsequent_indent=" " * len(indent),
            break_long_words=False,
            break_on_hyphens=False,
        )
        if not wrapped:
            self.add_blank()
            return
        for line in wrapped:
            self.add_text_line(line, font=font, size=size, leading=leading)

    def add_code(self, text: str) -> None:
        line = text.replace("\t", "    ")
        chunks = textwrap.wrap(
            line,
            width=96,
            initial_indent="",
            subsequent_indent="    ",
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]
        for chunk in chunks:
            self.add_text_line(chunk, font="F3", size=CODE_SIZE, leading=CODE_LEADING)


def render_markdown(builder: PdfBuilder, markdown: str) -> None:
    builder.new_page()
    pending_para: list[str] = []
    in_code = False

    def flush_para() -> None:
        nonlocal pending_para
        if pending_para:
            text = " ".join(part.strip() for part in pending_para).strip()
            if text:
                builder.add_wrapped(text)
                builder.add_blank(4)
            pending_para = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()

        if line.strip() == r"\newpage":
            flush_para()
            builder.new_page()
            continue

        if line.startswith("```"):
            flush_para()
            in_code = not in_code
            builder.add_blank(3)
            continue

        if in_code:
            builder.add_code(line)
            continue

        if not line.strip():
            flush_para()
            continue

        if line.startswith("# "):
            flush_para()
            builder.add_heading(line[2:].strip(), 1)
            continue

        if line.startswith("## "):
            flush_para()
            builder.add_heading(line[3:].strip(), 2)
            continue

        if line.startswith("### "):
            flush_para()
            builder.add_heading(line[4:].strip(), 3)
            continue

        if line.startswith("- "):
            flush_para()
            builder.add_wrapped("- " + line[2:].strip(), width=96, indent="")
            continue

        if re.match(r"^\d+\. ", line):
            flush_para()
            builder.add_wrapped(line, width=96)
            continue

        pending_para.append(line)

    flush_para()
    builder.finish()


def write_pdf(pages: list[list[str]], output: Path) -> None:
    objects: list[bytes] = []

    def add_obj(body: str | bytes) -> int:
        if isinstance(body, str):
            body = body.encode("latin-1")
        objects.append(body)
        return len(objects)

    catalog_id = add_obj("<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add_obj(b"")
    font_helv = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_bold = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    font_mono = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    page_ids: list[int] = []
    for page_lines in pages:
        stream = "\n".join(page_lines).encode("latin-1", errors="replace")
        content_id = add_obj(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
        )
        page_id = add_obj(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_helv} 0 R /F2 {font_bold} 0 R /F3 {font_mono} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [ {kids} ] /Count {len(page_ids)} >>".encode("latin-1")

    output.parent.mkdir(parents=True, exist_ok=True)
    data = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{idx} 0 obj\n".encode("ascii"))
        data.extend(obj)
        data.extend(b"\nendobj\n")

    xref_start = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    data.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    data.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )
    output.write_bytes(data)


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    builder = PdfBuilder()
    render_markdown(builder, markdown)
    write_pdf(builder.pages, OUTPUT)
    print(f"Wrote {OUTPUT} ({len(builder.pages)} pages)")


if __name__ == "__main__":
    main()
