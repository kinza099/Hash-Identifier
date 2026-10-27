"""Batch Hash Processing and Duplicate Hash Detection Engine.

Processes multiline hash lists and CSV/TXT uploads:
- Preserves original line/row numbers
- Identifies and ranks algorithms per line
- Summarizes total, valid, invalid, and duplicate entries
- Detects repeated hash strings and groups occurrences
- Supports CSV and JSON exports with memory-efficient incremental parsing
"""

import csv
import io
import json
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from core.detector import identify_hash

MAX_BATCH_ROWS = 10000


def parse_hash_input(raw_text: str, max_rows: int = MAX_BATCH_ROWS) -> List[Dict[str, Any]]:
    """Parse multiline text or raw input into structured lines with line numbers.

    Handles CRLF and LF line breaks. Blank or whitespace-only lines are tracked
    to preserve accurate line numbers without failing silently.
    Enforces maximum line processing limits to protect memory.
    """
    entries: List[Dict[str, Any]] = []

    for idx, line in enumerate(raw_text.splitlines(), start=1):
        if idx > max_rows:
            break
        stripped_val = line.strip()
        entries.append({
            "line_number": idx,
            "value": stripped_val,
            "is_empty": len(stripped_val) == 0,
        })

    return entries


def parse_csv_input(
    csv_text: str,
    column_name: Optional[str] = None,
    max_rows: int = MAX_BATCH_ROWS,
) -> List[Dict[str, Any]]:
    """Parse CSV text incrementally to extract hash values from a specified column or the first matching column.

    Streams rows incrementally without materializing all rows into memory at once.
    """
    reader = csv.reader(io.StringIO(csv_text))
    try:
        first_row = next(reader)
    except StopIteration:
        return []

    col_idx = 0
    is_header = False

    # Check if first row contains a 'hash' column name
    if column_name:
        for i, col in enumerate(first_row):
            if col.strip().lower() == column_name.lower():
                col_idx = i
                is_header = True
                break
    else:
        for i, col in enumerate(first_row):
            if any(k in col.strip().lower() for k in ["hash", "digest", "checksum"]):
                col_idx = i
                is_header = True
                break

    first_row_val = first_row[col_idx].strip() if col_idx < len(first_row) else ""
    if not is_header and any(c in first_row_val.lower() for c in ["hash", "digest", "algorithm"]):
        is_header = True

    entries: List[Dict[str, Any]] = []
    row_counter = 1

    # If first row was actual data (not a recognized header), process it as row 1
    if not is_header:
        entries.append({
            "line_number": 1,
            "value": first_row_val,
            "is_empty": len(first_row_val) == 0,
        })

    # Stream subsequent rows up to max_rows
    for row in reader:
        row_counter += 1
        if len(entries) >= max_rows:
            break
        val = row[col_idx].strip() if col_idx < len(row) else ""
        entries.append({
            "line_number": row_counter,
            "value": val,
            "is_empty": len(val) == 0,
        })

    return entries


def process_batch(
    raw_text: str,
    is_csv: bool = False,
    csv_column: Optional[str] = None,
    compact: bool = False,
    max_rows: int = MAX_BATCH_ROWS,
) -> Dict[str, Any]:
    """Scan and identify a batch of hashes.

    Returns detailed line-by-line identification results, duplicate tracking,
    summary metrics, and export structures.
    Uses single-pass normalization and precompiled dispatching for high throughput.
    """
    if is_csv:
        entries = parse_csv_input(raw_text, csv_column, max_rows=max_rows)
    else:
        entries = parse_hash_input(raw_text, max_rows=max_rows)

    results: List[Dict[str, Any]] = []
    seen_hashes: Dict[str, List[int]] = defaultdict(list)
    valid_count = 0
    invalid_count = 0
    empty_count = 0

    for item in entries:
        line_num = item["line_number"]
        val = item["value"]

        if item["is_empty"]:
            empty_count += 1
            results.append({
                "line_number": line_num,
                "input": "",
                "valid": False,
                "status": "EMPTY",
                "message": "Empty or blank line",
                "length": 0,
                "is_hex": False,
                "is_duplicate": False,
                "duplicate_occurrences": 1,
                "matches": [],
                "primary_algorithm": "None",
                "confidence": "none",
                "score": 0,
                "ambiguity_warning": None,
            })
            continue

        ident = identify_hash(val, compact=compact)
        is_valid = ident.get("valid", False) and len(ident.get("matches", [])) > 0
        is_hex = ident.get("is_hex", False)

        # Compute case-normalization key once per entry
        norm_key = val.lower() if is_hex else val
        seen_hashes[norm_key].append(line_num)

        if is_valid:
            valid_count += 1
            best_match = ident["matches"][0]
            types = best_match["types"]
            primary_alg = "/".join(types[:2]) + ("..." if len(types) > 2 else "")
            confidence = best_match["confidence"]
            score = best_match.get("score", 0)
            status = "VALID"
        else:
            invalid_count += 1
            primary_alg = "Unknown / Unmatched"
            confidence = "none"
            score = 0
            status = "INVALID"

        entry_res: Dict[str, Any] = {
            "line_number": line_num,
            "input": val,
            "_norm_key": norm_key,
            "valid": is_valid,
            "status": status,
            "message": ident.get("message") if not is_valid else "Matched format",
            "length": ident.get("length", len(val)),
            "is_hex": is_hex,
            "is_duplicate": False,
            "duplicate_occurrences": 1,
            "matches": ident.get("matches", []),
            "primary_algorithm": primary_alg,
            "confidence": confidence,
            "score": score,
            "ambiguity_warning": ident.get("ambiguity_warning"),
        }
        results.append(entry_res)

    # Second pass: mark duplicates using precomputed _norm_key (zero string rescanning)
    duplicate_groups_count = 0
    total_duplicate_entries = 0

    for lines in seen_hashes.values():
        if len(lines) > 1:
            duplicate_groups_count += 1
            total_duplicate_entries += (len(lines) - 1)

    for item in results:
        norm_key = item.pop("_norm_key", None)
        if not norm_key:
            continue
        lines_for_key = seen_hashes[norm_key]
        if len(lines_for_key) > 1:
            item["is_duplicate"] = True
            item["duplicate_occurrences"] = len(lines_for_key)
            item["duplicate_lines"] = lines_for_key

    return {
        "total_entries": len(entries),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "empty_count": empty_count,
        "duplicate_groups_count": duplicate_groups_count,
        "total_duplicate_entries": total_duplicate_entries,
        "unique_hashes_count": len(seen_hashes),
        "results": results,
    }


def find_duplicates(
    raw_text: str,
    case_sensitive: bool = False,
    max_rows: int = MAX_BATCH_ROWS,
) -> Dict[str, Any]:
    """Identify repeated hash values, group them together, and report occurrence lines.

    Preserves original casing in reports while grouping by chosen normalization.
    """
    entries = parse_hash_input(raw_text, max_rows=max_rows)
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    total_valid_entries = 0
    empty_lines = 0

    for item in entries:
        val = item["value"]
        if not val:
            empty_lines += 1
            continue

        total_valid_entries += 1
        key = val if case_sensitive else val.lower()
        groups[key].append(item)

    duplicate_groups: List[Dict[str, Any]] = []
    unique_items: List[Dict[str, Any]] = []

    for key, items in groups.items():
        original_values = [it["value"] for it in items]
        lines = [it["line_number"] for it in items]

        group_info = {
            "normalized_hash": key,
            "display_hash": items[0]["value"],
            "count": len(items),
            "lines": lines,
            "is_duplicate": len(items) > 1,
            "original_samples": original_values,
        }

        if len(items) > 1:
            duplicate_groups.append(group_info)
        else:
            unique_items.append(group_info)

    # Sort duplicate groups by count descending
    duplicate_groups.sort(key=lambda g: g["count"], reverse=True)

    total_duplicates_count = sum(g["count"] - 1 for g in duplicate_groups)

    return {
        "total_lines": len(entries),
        "total_hashes": total_valid_entries,
        "empty_lines": empty_lines,
        "unique_count": len(groups),
        "duplicate_groups_count": len(duplicate_groups),
        "repeated_occurrences_count": total_duplicates_count,
        "case_sensitive": case_sensitive,
        "duplicate_groups": duplicate_groups,
        "unique_items": unique_items,
        "disclaimer": (
            "Duplicate Detection Policy: Duplicate detection identifies identical or equivalent hash strings. "
            "It does not imply that different hash strings correspond to distinct file contents, nor does it replace cryptographic collision checking."
        ),
    }
