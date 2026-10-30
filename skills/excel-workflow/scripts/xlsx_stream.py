#!/usr/bin/env python3
"""Zero-dependency XLSX streaming reader and manual-input extractor.

Reads directly from the XLSX ZIP archive without loading the workbook DOM into
memory, and verifies that the source file size and mtime_ns remain unchanged.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator
from zipfile import ZipFile

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_COL_RE = re.compile(r"^([A-Z]+)(\d+)$")


def clean_val(val: object) -> str:
    if val is None:
        return ""
    return re.sub(r"[\x00-\x1f\x7f]+", " ", str(val)).strip()


def sheet_paths(z: ZipFile) -> dict[str, str]:
    """Map visible worksheet titles to their internal ZIP member paths."""
    relroot = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rels = {r.attrib["Id"]: r.attrib["Target"] for r in relroot}
    out: dict[str, str] = {}
    for s in ET.fromstring(z.read("xl/workbook.xml")).iter(NS + "sheet"):
        rid = s.attrib[RNS + "id"]
        target = rels[rid]
        path = target.lstrip("/") if target.startswith("/") else "xl/" + target
        out[s.attrib["name"]] = path
    return out


def resolve_sheet_member(z: ZipFile, sheet_name: str) -> str:
    sheets = sheet_paths(z)
    if sheet_name in sheets:
        return sheets[sheet_name]
    candidate = f"xl/worksheets/{sheet_name}.xml"
    if candidate in z.namelist():
        return candidate
    raise KeyError(f"Worksheet {sheet_name!r} not found. Available: {list(sheets)}")


def shared_strings(z: ZipFile) -> list[str]:
    """Stream xl/sharedStrings.xml with bounded element memory."""
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    out: list[str] = []
    with z.open("xl/sharedStrings.xml") as fh:
        for _, elem in ET.iterparse(fh, events=("end",)):
            if elem.tag == NS + "si":
                out.append("".join(t.text or "" for t in elem.iter(NS + "t")))
                elem.clear()
    return out


def _decode_cell(attrs: bytes, inner: bytes, ss: list[str]) -> str:
    if b't="inlineStr"' in attrs:
        return "".join(
            html.unescape(t.decode("utf-8", errors="replace"))
            for t in re.findall(rb"<t[^>]*>(.*?)</t>", inner, re.S)
        )
    m_v = re.search(rb"<v>(.*?)</v>", inner, re.S)
    if not m_v:
        return ""
    raw_v = m_v.group(1).decode("utf-8", errors="replace")
    if b't="s"' in attrs:
        idx = int(raw_v)
        return ss[idx] if 0 <= idx < len(ss) else ""
    return html.unescape(raw_v)


def read_headers(xlsx_path: Path, sheet_name: str, header_row: int = 1) -> dict[str, str]:
    """Read a single header row from an XLSX worksheet without loading the sheet DOM."""
    xlsx_path = Path(xlsx_path)
    before = xlsx_path.stat()
    cell_re = re.compile(rb'<c\b[^>]*\br="([A-Z]+)\d+"([^>]*)>(.*?)</c>', re.S)
    row_num_re = re.compile(rb'\br="(\d+)"')
    headers: dict[str, str] = {}

    with ZipFile(xlsx_path) as z:
        member = resolve_sheet_member(z, sheet_name)
        ss = shared_strings(z)
        with z.open(member) as fh:
            buf = b""
            while True:
                chunk = fh.read(1024 * 1024)
                if not chunk:
                    break
                parts = (buf + chunk).split(b"</row>")
                buf = parts.pop()
                found = False
                for part in parts:
                    start = part.rfind(b"<row")
                    if start < 0:
                        continue
                    raw_row = part[start:]
                    m_rn = row_num_re.search(raw_row)
                    if not m_rn or int(m_rn.group(1)) != header_row:
                        continue
                    for m_cell in cell_re.finditer(raw_row):
                        col_let = m_cell.group(1).decode()
                        val = clean_val(_decode_cell(m_cell.group(2), m_cell.group(3), ss))
                        if val:
                            headers[col_let] = val
                    found = True
                    break
                if found:
                    break

    after = xlsx_path.stat()
    assert (before.st_size, before.st_mtime_ns) == (
        after.st_size,
        after.st_mtime_ns,
    ), f"Source file modified: {xlsx_path}"
    return headers


def iter_selected_rows(
    xlsx_path: Path,
    sheet_name: str,
    header_row: int,
    col_map: dict[str, str],
    chunk_size: int = 4 * 1024 * 1024,
) -> Iterator[tuple[int, dict[str, str]]]:
    """Stream selected columns from an XLSX worksheet while verifying source immutability."""
    xlsx_path = Path(xlsx_path)
    before = xlsx_path.stat()
    cols_pat = b"|".join(re.escape(c.encode()) for c in col_map)
    cell_re = re.compile(rb'<c\b[^>]*\br="(' + cols_pat + rb')\d+"([^>]*)>(.*?)</c>', re.S)
    row_num_re = re.compile(rb'\br="(\d+)"')

    with ZipFile(xlsx_path) as z:
        member = resolve_sheet_member(z, sheet_name)
        ss = shared_strings(z)
        with z.open(member) as fh:
            buf = b""
            while True:
                chunk = fh.read(chunk_size)
                if not chunk:
                    break
                parts = (buf + chunk).split(b"</row>")
                buf = parts.pop()
                for part in parts:
                    start = part.rfind(b"<row")
                    if start < 0:
                        continue
                    raw_row = part[start:]
                    m_rn = row_num_re.search(raw_row)
                    if not m_rn:
                        continue
                    rn = int(m_rn.group(1))
                    if rn <= header_row:
                        continue
                    row_dict: dict[str, str] = {}
                    for m_cell in cell_re.finditer(raw_row):
                        col_let = m_cell.group(1).decode()
                        val = clean_val(_decode_cell(m_cell.group(2), m_cell.group(3), ss))
                        if val:
                            row_dict[col_map[col_let]] = val
                    if row_dict:
                        yield rn, row_dict

    after = xlsx_path.stat()
    assert (before.st_size, before.st_mtime_ns) == (
        after.st_size,
        after.st_mtime_ns,
    ), f"Source file modified: {xlsx_path}"


def read_keyed_inputs(
    xlsx_path: Path,
    sheet_name: str = "sheet1",
    key_field: str = "ID",
    fields: list[str] | None = None,
    header_row: int = 1,
) -> dict[str, dict[str, str]]:
    """Extract manual review columns from an existing workbook keyed by a stable ID column."""
    xlsx_path = Path(xlsx_path)
    if not xlsx_path.exists():
        return {}
    headers = read_headers(xlsx_path, sheet_name, header_row)
    wanted = set(fields) | {key_field} if fields else set(headers.values())
    col_map = {col: name for col, name in headers.items() if name in wanted}
    if key_field not in col_map.values():
        raise KeyError(f"Key column {key_field!r} not found in row {header_row} of {sheet_name!r}")

    out: dict[str, dict[str, str]] = {}
    for _, row in iter_selected_rows(xlsx_path, sheet_name, header_row, col_map):
        key = row.get(key_field, "")
        if not key:
            continue
        if fields is None:
            out[key] = {k: v for k, v in row.items() if k != key_field}
        else:
            out[key] = {f: row.get(f, "") for f in fields if f in row}
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sheets = sub.add_parser("sheets", help="List worksheet names and internal XML paths")
    p_sheets.add_argument("xlsx", type=Path)

    p_headers = sub.add_parser("headers", help="Read header row column mapping")
    p_headers.add_argument("xlsx", type=Path)
    p_headers.add_argument("--sheet", required=True)
    p_headers.add_argument("--header-row", type=int, default=1)

    p_stream = sub.add_parser("stream", help="Stream selected columns as NDJSON")
    p_stream.add_argument("xlsx", type=Path)
    p_stream.add_argument("--sheet", required=True)
    p_stream.add_argument("--header-row", type=int, default=1)
    p_stream.add_argument("--cols", required=True, help='JSON object mapping column letter to field name, e.g. \'{"A":"code","B":"desc"}\'')
    p_stream.add_argument("--limit", type=int, default=0)

    p_inputs = sub.add_parser("inputs", help="Read manual review inputs keyed by a column header")
    p_inputs.add_argument("xlsx", type=Path)
    p_inputs.add_argument("--sheet", default="sheet1")
    p_inputs.add_argument("--key", required=True, help="Header name of the unique key column")
    p_inputs.add_argument("--fields", default="", help="Comma-separated header names to extract")
    p_inputs.add_argument("--header-row", type=int, default=1)

    args = parser.parse_args()
    if args.cmd == "sheets":
        with ZipFile(args.xlsx) as z:
            print(json.dumps(sheet_paths(z), ensure_ascii=False, indent=2))
    elif args.cmd == "headers":
        print(json.dumps(read_headers(args.xlsx, args.sheet, args.header_row), ensure_ascii=False, indent=2))
    elif args.cmd == "stream":
        col_map = json.loads(args.cols)
        count = 0
        for rn, row in iter_selected_rows(args.xlsx, args.sheet, args.header_row, col_map):
            print(json.dumps({"row": rn, **row}, ensure_ascii=False))
            count += 1
            if args.limit and count >= args.limit:
                break
    elif args.cmd == "inputs":
        field_list = [f.strip() for f in args.fields.split(",") if f.strip()] or None
        data = read_keyed_inputs(args.xlsx, args.sheet, args.key, field_list, args.header_row)
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
