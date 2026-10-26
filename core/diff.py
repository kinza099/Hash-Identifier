"""Hash List Diff Analyzer Engine.

Compares two hash lists (List A and List B):
- Common hashes (intersection of A and B)
- Added to List B (present in B, absent from A)
- Removed from List A (present in A, absent from B)
- Unique to List A
- Unique to List B
- In-list duplicate tracking and counts
- Documented normalization policy
"""

from collections import Counter
from typing import Any, Dict, List, Set, Tuple

from core.batch import parse_hash_input


def analyze_diff(
    text_a: str,
    text_b: str,
    case_sensitive: bool = False,
) -> Dict[str, Any]:
    """Compare Hash List A and Hash List B.

    Comparison Policy:
    - Added: Present in List B, absent from List A.
    - Removed: Present in List A, absent from List B.
    - Common: Present in both List A and List B.
    - Duplicates within each list are tracked and reported separately.
    """
    entries_a = parse_hash_input(text_a or "")
    entries_b = parse_hash_input(text_b or "")

    # Filter out empty lines while tracking line numbers
    valid_a = [e for e in entries_a if not e["is_empty"]]
    valid_b = [e for e in entries_b if not e["is_empty"]]

    # Map normalized key -> first original display value & list of line numbers
    map_a: Dict[str, Dict[str, Any]] = {}
    lines_a: Dict[str, List[int]] = {}
    for it in valid_a:
        key = it["value"] if case_sensitive else it["value"].lower()
        if key not in map_a:
            map_a[key] = it["value"]
            lines_a[key] = []
        lines_a[key].append(it["line_number"])

    map_b: Dict[str, Dict[str, Any]] = {}
    lines_b: Dict[str, List[int]] = {}
    for it in valid_b:
        key = it["value"] if case_sensitive else it["value"].lower()
        if key not in map_b:
            map_b[key] = it["value"]
            lines_b[key] = []
        lines_b[key].append(it["line_number"])

    keys_a = set(map_a.keys())
    keys_b = set(map_b.keys())

    common_keys = sorted(keys_a & keys_b)
    added_keys = sorted(keys_b - keys_a)      # in B, not in A
    removed_keys = sorted(keys_a - keys_b)    # in A, not in B

    common_items = [
        {
            "hash": map_b[k],
            "lines_in_a": lines_a[k],
            "lines_in_b": lines_b[k],
            "count_in_a": len(lines_a[k]),
            "count_in_b": len(lines_b[k]),
        }
        for k in common_keys
    ]

    added_items = [
        {
            "hash": map_b[k],
            "lines_in_b": lines_b[k],
            "count_in_b": len(lines_b[k]),
        }
        for k in added_keys
    ]

    removed_items = [
        {
            "hash": map_a[k],
            "lines_in_a": lines_a[k],
            "count_in_a": len(lines_a[k]),
        }
        for k in removed_keys
    ]

    # Internal duplicate calculations
    duplicates_in_a = sum(len(lines) - 1 for lines in lines_a.values() if len(lines) > 1)
    duplicates_in_b = sum(len(lines) - 1 for lines in lines_b.values() if len(lines) > 1)

    return {
        "summary": {
            "total_lines_a": len(entries_a),
            "total_hashes_a": len(valid_a),
            "unique_hashes_a": len(keys_a),
            "duplicate_occurrences_a": duplicates_in_a,
            "total_lines_b": len(entries_b),
            "total_hashes_b": len(valid_b),
            "unique_hashes_b": len(keys_b),
            "duplicate_occurrences_b": duplicates_in_b,
            "common_count": len(common_keys),
            "added_count": len(added_keys),
            "removed_count": len(removed_keys),
            "case_sensitive": case_sensitive,
        },
        "common": common_items,
        "added": added_items,        # Added in List B (present in B, absent in A)
        "removed": removed_items,    # Removed from List A (present in A, absent in B)
        "policy": (
            "Comparison Direction: List B is analyzed relative to baseline List A. "
            "'Added' represents values present in B but absent from A. "
            "'Removed' represents values present in A but missing in B. "
            "Normalization: Case-insensitive hex matching by default."
        ),
    }
