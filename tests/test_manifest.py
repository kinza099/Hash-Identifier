"""Tests for Hash Manifest Generator & Verifier Module."""

import pytest
from core.manifest import generate_manifest, manifest_to_csv, parse_manifest, verify_manifest


def test_generate_and_parse_manifest():
    files = [
        {"path": "docs/readme.txt", "size": 1024, "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
        {"path": "bin/app.exe", "size": 2048, "hash": "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"},
    ]

    manifest = generate_manifest(files, creator="Test Suite")
    assert manifest["total_files"] == 2
    assert manifest["total_bytes"] == 3072
    assert manifest["files"][0]["algorithm"] == "SHA-256"

    # CSV serialization and roundtrip parse
    csv_str = manifest_to_csv(manifest)
    parsed_csv = parse_manifest(csv_str)
    assert parsed_csv["total_files"] == 2
    assert parsed_csv["files"][0]["hash"] == files[1]["hash"] or parsed_csv["files"][0]["hash"] == files[0]["hash"]


def test_verify_manifest_all_cases():
    manifest_data = {
        "files": [
            {"path": "unchanged.txt", "size": 100, "hash": "aaa"},
            {"path": "modified.txt", "size": 200, "hash": "bbb"},
            {"path": "missing.txt", "size": 300, "hash": "ccc"},
        ]
    }

    current_files = [
        {"path": "unchanged.txt", "size": 100, "hash": "aaa"},
        {"path": "modified.txt", "size": 250, "hash": "modified_hash_zzz"},
        {"path": "newly_added.txt", "size": 50, "hash": "ddd"},
    ]

    res = verify_manifest(manifest_data, current_files)
    assert res["fully_intact"] is False
    assert res["status"] == "DISCREPANCY_DETECTED"

    summary = res["summary"]
    assert summary["unchanged_count"] == 1
    assert summary["modified_count"] == 1
    assert summary["missing_count"] == 1
    assert summary["newly_added_count"] == 1

    assert res["unchanged"][0]["path"] == "unchanged.txt"
    assert res["modified"][0]["path"] == "modified.txt"
    assert res["missing"][0]["path"] == "missing.txt"
    assert res["newly_added"][0]["path"] == "newly_added.txt"


def test_verify_manifest_fully_intact():
    manifest_data = {
        "files": [
            {"path": "file1.txt", "size": 100, "hash": "aaa"},
            {"path": "file2.txt", "size": 200, "hash": "bbb"},
        ]
    }

    current_files = [
        {"path": "file1.txt", "size": 100, "hash": "aaa"},
        {"path": "file2.txt", "size": 200, "hash": "bbb"},
    ]

    res = verify_manifest(manifest_data, current_files)
    assert res["fully_intact"] is True
    assert res["status"] == "SUCCESS"
    assert "Verification Complete" in res["verification_statement"]
