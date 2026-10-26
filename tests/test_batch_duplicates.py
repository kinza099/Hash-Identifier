"""Tests for Batch Scanner and Duplicate Detection Modules."""

import pytest
from core.batch import find_duplicates, parse_csv_input, parse_hash_input, process_batch


def test_batch_line_numbers_and_empties():
    raw = (
        "5f4dcc3b5aa765d61d8327deb882cf99\n"
        "\n"  # line 2 is blank
        "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12\n"
        "not_a_valid_hash\n"
        "5F4DCC3B5AA765D61D8327DEB882CF99"  # duplicate of line 1 (case-insensitive)
    )

    batch = process_batch(raw)
    assert batch["total_entries"] == 5
    assert batch["valid_count"] == 3
    assert batch["invalid_count"] == 1
    assert batch["empty_count"] == 1

    results = batch["results"]
    assert results[0]["line_number"] == 1
    assert results[0]["valid"] is True
    assert results[0]["is_duplicate"] is True

    assert results[1]["line_number"] == 2
    assert results[1]["status"] == "EMPTY"

    assert results[3]["line_number"] == 4
    assert results[3]["status"] == "INVALID"

    assert results[4]["line_number"] == 5
    assert results[4]["is_duplicate"] is True
    assert set(results[4]["duplicate_lines"]) == {1, 5}


def test_batch_csv_parsing():
    csv_text = "id,hash,filename\n1,5f4dcc3b5aa765d61d8327deb882cf99,test.txt\n2,2fd4e1c67a2d28fced849ee1bb76e7391b93eb12,doc.pdf"
    entries = parse_csv_input(csv_text, column_name="hash")
    assert len(entries) == 2
    assert entries[0]["value"] == "5f4dcc3b5aa765d61d8327deb882cf99"
    assert entries[1]["value"] == "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"


def test_find_duplicates_grouping():
    raw = (
        "hashA\n"
        "hashB\n"
        "hashA\n"
        "hashC\n"
        "hashA\n"
        "hashB\n"
    )

    res = find_duplicates(raw, case_sensitive=True)
    assert res["total_lines"] == 6
    assert res["total_hashes"] == 6
    assert res["unique_count"] == 3
    assert res["duplicate_groups_count"] == 2
    assert res["repeated_occurrences_count"] == 3  # 2 extra hashA + 1 extra hashB

    # Check hashA group
    group_a = next(g for g in res["duplicate_groups"] if g["normalized_hash"] == "hashA")
    assert group_a["count"] == 3
    assert group_a["lines"] == [1, 3, 5]


def test_duplicate_case_normalization():
    raw = "5f4dcc3b5aa765d61d8327deb882cf99\n5F4DCC3B5AA765D61D8327DEB882CF99"

    # Case-insensitive (default)
    res_ci = find_duplicates(raw, case_sensitive=False)
    assert res_ci["duplicate_groups_count"] == 1
    assert res_ci["duplicate_groups"][0]["count"] == 2

    # Case-sensitive
    res_cs = find_duplicates(raw, case_sensitive=True)
    assert res_cs["duplicate_groups_count"] == 0
    assert res_cs["unique_count"] == 2
