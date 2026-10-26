"""Tests for Hash List Diff Analyzer Module."""

import pytest
from core.diff import analyze_diff


def test_diff_basic_sets():
    list_a = "hash1\nhash2\nhash3\nhash2"  # hash2 has duplicate in A
    list_b = "hash2\nhash3\nhash4\nhash5"

    diff = analyze_diff(list_a, list_b, case_sensitive=True)
    summary = diff["summary"]

    assert summary["common_count"] == 2  # hash2, hash3
    assert summary["added_count"] == 2   # hash4, hash5
    assert summary["removed_count"] == 1 # hash1
    assert summary["duplicate_occurrences_a"] == 1
    assert summary["duplicate_occurrences_b"] == 0

    common_hashes = {c["hash"] for c in diff["common"]}
    assert common_hashes == {"hash2", "hash3"}

    added_hashes = {a["hash"] for a in diff["added"]}
    assert added_hashes == {"hash4", "hash5"}

    removed_hashes = {r["hash"] for r in diff["removed"]}
    assert removed_hashes == {"hash1"}


def test_diff_case_normalization():
    list_a = "5F4DCC3B5AA765D61D8327DEB882CF99"
    list_b = "5f4dcc3b5aa765d61d8327deb882cf99"

    diff_ci = analyze_diff(list_a, list_b, case_sensitive=False)
    assert diff_ci["summary"]["common_count"] == 1
    assert diff_ci["summary"]["added_count"] == 0
    assert diff_ci["summary"]["removed_count"] == 0

    diff_cs = analyze_diff(list_a, list_b, case_sensitive=True)
    assert diff_cs["summary"]["common_count"] == 0
    assert diff_cs["summary"]["added_count"] == 1
    assert diff_cs["summary"]["removed_count"] == 1
