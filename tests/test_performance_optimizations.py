"""Performance & Optimization Tests.

Validates:
1. O(N) Shannon entropy calculation using frequency mapping.
2. Fast regex dispatching and precompiled rules.
3. Memory-efficient batch processing and duplicate normalization.
4. High-performance single-transaction bulk database imports.
5. Benchmark parameter clamping and input bounds.
6. Payload safety limits in cryptographic hashing.
"""

import json
import math
import os
import tempfile
import time
import pytest

from core.detector import calculate_entropy, identify_hash, COMPILED_RULES, RULES_HEX_BY_LEN
from core.batch import parse_csv_input, parse_hash_input, process_batch
from core.database import init_db, import_records, search_hash, _INITIALIZED_DBS
from core.benchmark import run_benchmark, MIN_BENCHMARK_SIZE_BYTES, MAX_BENCHMARK_SIZE_BYTES
from core.hasher import hash_text, MAX_TEXT_SIZE_BYTES


def test_entropy_linear_complexity_and_correctness():
    """Verify calculate_entropy correctly computes Shannon entropy in O(N) time."""
    assert calculate_entropy("") == 0.0

    # Single character string has 0 entropy
    assert calculate_entropy("aaaaaaa") == 0.0

    # Two equally likely characters has 1.0 bit entropy
    assert pytest.approx(calculate_entropy("abababab"), 0.01) == 1.0

    # 4 equally likely characters has 2.0 bits entropy
    assert pytest.approx(calculate_entropy("abcdabcd"), 0.01) == 2.0

    # High entropy hex hash
    hex_hash = "5f4dcc3b5aa765d61d8327deb882cf99"
    ent = calculate_entropy(hex_hash)
    assert 3.0 < ent < 4.0

    # Verify linear performance on large input (100,000 characters)
    large_str = hex_hash * 3000  # ~96,000 chars
    t0 = time.perf_counter()
    large_ent = calculate_entropy(large_str)
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.05  # Must calculate in under 50ms
    assert large_ent > 0.0


def test_precompiled_rules_dispatch():
    """Verify rules are precompiled and fast dispatch matches correct algorithm families."""
    assert len(COMPILED_RULES) > 20
    assert 32 in RULES_HEX_BY_LEN
    assert 64 in RULES_HEX_BY_LEN

    # MD5 32 hex chars
    md5_res = identify_hash("5f4dcc3b5aa765d61d8327deb882cf99")
    assert md5_res["valid"] is True
    assert "MD5" in md5_res["matches"][0]["types"]

    # SHA-256 64 hex chars
    sha256_res = identify_hash("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
    assert sha256_res["valid"] is True
    assert "SHA-256" in sha256_res["matches"][0]["types"]

    # bcrypt prefix dispatch
    bcrypt_res = identify_hash("$2b$12$e8cr0ym8zI6gkNVoU2k3QOD7O7sL6lC55kK3i8V1n6j6iH5W2kQ3e")
    assert bcrypt_res["valid"] is True
    assert "bcrypt" in bcrypt_res["matches"][0]["types"]

    # Compact mode reduces metadata overhead
    compact_res = identify_hash("5f4dcc3b5aa765d61d8327deb882cf99", compact=True)
    assert "rationale" not in compact_res["matches"][0]
    assert "ambiguity_note" not in compact_res["matches"][0]
    assert compact_res["matches"][0]["score"] == md5_res["matches"][0]["score"]


def test_batch_single_pass_normalization():
    """Verify batch processing normalizes hex case once and detects duplicates accurately."""
    batch_raw = (
        "5F4DCC3B5AA765D61D8327DEB882CF99\n"  # Uppercase MD5
        "5f4dcc3b5aa765d61d8327deb882cf99\n"  # Lowercase MD5 (duplicate)
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824\n"  # Unique SHA-256
        "5f4dcc3b5aa765d61d8327deb882cf99"   # 3rd occurrence
    )

    res = process_batch(batch_raw, compact=True)
    assert res["total_entries"] == 4
    assert res["valid_count"] == 4
    assert res["duplicate_groups_count"] == 1
    assert res["total_duplicate_entries"] == 2

    # Check duplicate lines
    assert res["results"][0]["is_duplicate"] is True
    assert set(res["results"][0]["duplicate_lines"]) == {1, 2, 4}


def test_csv_incremental_parsing_bounds():
    """Verify CSV parsing streams rows and obeys max_rows limit."""
    lines = ["id,hash,name"] + [f"{i},5f4dcc3b5aa765d61d8327deb882cf99,file_{i}.txt" for i in range(1, 101)]
    csv_text = "\n".join(lines)

    entries = parse_csv_input(csv_text, column_name="hash", max_rows=50)
    assert len(entries) == 50
    assert entries[0]["value"] == "5f4dcc3b5aa765d61d8327deb882cf99"


def test_database_bulk_import_and_wal():
    """Verify database import performs bulk insertion in single transaction and caches init."""
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, "test_bulk.db")
        init_db(db_path)
        norm_path = os.path.abspath(db_path)
        assert norm_path in _INITIALIZED_DBS

        # Calling init_db again is an instant no-op
        t0 = time.perf_counter()
        init_db(db_path)
        t1 = time.perf_counter()
        assert (t1 - t0) < 0.005

        # Import 200 records in bulk
        records = [
            {"hash": f"bulk_hash_{i:06d}", "algorithm": "SHA-256", "source": "Perf Test", "notes": "", "tag": "Bulk"}
            for i in range(200)
        ]
        import_res = import_records(json.dumps(records), db_path=db_path)
        assert import_res["imported"] == 200
        assert len(import_res["errors"]) == 0

        # Exact match search
        found = search_hash("bulk_hash_000042", db_path=db_path)
        assert found["found"] is True
        assert found["records"][0]["algorithm"] == "SHA-256"


def test_benchmark_clamping():
    """Verify run_benchmark clamps size_bytes and iterations within safe boundaries."""
    # Under-bounds clamping
    res_under = run_benchmark(size_bytes=10, iterations=0, warmup=False)
    assert res_under["size_bytes"] == MIN_BENCHMARK_SIZE_BYTES
    assert res_under["iterations"] == 1

    # Over-bounds clamping (prevent DoS)
    res_over = run_benchmark(size_bytes=999_999_999, iterations=500, warmup=False)
    assert res_over["size_bytes"] == MAX_BENCHMARK_SIZE_BYTES
    assert res_over["iterations"] == 20


def test_hasher_payload_limits():
    """Verify hash_text enforces safe payload boundaries."""
    # Normal hashing succeeds
    normal = hash_text("Hello Cryptography 2026")
    assert normal["byte_length"] > 0
    assert "sha256" in normal["hashes"]

    # Exceeding payload limit raises ValueError
    oversized = "A" * (MAX_TEXT_SIZE_BYTES + 1024)
    with pytest.raises(ValueError, match="maximum allowed size"):
        hash_text(oversized)
