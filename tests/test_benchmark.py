"""Tests for Hash Performance Benchmark Module."""

import pytest
from core.benchmark import run_benchmark


def test_benchmark_execution():
    # Run with small payload 64 KB and 3 iterations for fast test execution
    bench = run_benchmark(size_bytes=64 * 1024, iterations=3, warmup=True)

    assert bench["status"] == "COMPLETED"
    assert bench["size_bytes"] == 64 * 1024
    assert bench["iterations"] == 3
    assert len(bench["results"]) == 5  # md5, sha1, sha256, sha384, sha512

    for r in bench["results"]:
        assert r["avg_time_ms"] >= 0
        assert r["throughput_mbs"] > 0
        assert r["iterations"] == 3

    assert "python_version" in bench["environment"]
    assert "platform" in bench["environment"]
    assert "Benchmark Environment Note" in bench["disclaimer"]
