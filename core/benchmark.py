"""Hash Performance Benchmark Engine.

Measures actual real-time execution speeds of MD5, SHA-1, SHA-256, SHA-384, and SHA-512:
- Supports variable payload sizes (Small 64KB, Medium 1MB, Large 8MB, or custom)
- Utilizes warm-up iterations to minimize CPU cache cold-start effects
- High-resolution timing via time.perf_counter()
- Real throughput calculations (MB/s) and execution statistics
- Exportable to JSON and CSV
"""

import hashlib
import os
import platform
import time
from typing import Any, Dict, List, Optional

BENCHMARK_ALGORITHMS = ["md5", "sha1", "sha256", "sha384", "sha512"]
ALGORITHM_LABELS = {
    "md5": "MD5",
    "sha1": "SHA-1",
    "sha256": "SHA-256",
    "sha384": "SHA-384",
    "sha512": "SHA-512",
}

SIZE_PRESETS = {
    "small": 64 * 1024,         # 64 KB
    "medium": 1024 * 1024,      # 1 MB
    "large": 8 * 1024 * 1024,   # 8 MB
}


def run_benchmark(
    size_bytes: int = 1024 * 1024,
    iterations: int = 5,
    warmup: bool = True,
) -> Dict[str, Any]:
    """Execute real-time cryptographic hash benchmark across supported algorithms.

    Generates a deterministic pseudo-random byte payload so every algorithm
    hashes the exact same data bytes.
    """
    if size_bytes <= 0:
        size_bytes = 1024 * 1024
    if iterations <= 0:
        iterations = 1

    # Generate test payload: deterministic pseudo-random bytes
    # Repeating a 1024-byte pattern to avoid memory overhead of os.urandom for large sizes
    pattern = (b"HashAnalysisToolkitBenchmarkPayloadBlock" * 26)[:1024]
    blocks_needed = (size_bytes // 1024) + (1 if size_bytes % 1024 != 0 else 0)
    data = (pattern * blocks_needed)[:size_bytes]

    # Warm-up phase
    if warmup:
        for alg in BENCHMARK_ALGORITHMS:
            h = getattr(hashlib, alg)()
            h.update(data[:min(len(data), 65536)])
            _ = h.digest()

    results: List[Dict[str, Any]] = []

    for alg in BENCHMARK_ALGORITHMS:
        h_func = getattr(hashlib, alg)
        times: List[float] = []

        for _ in range(iterations):
            t0 = time.perf_counter()
            h = h_func()
            h.update(data)
            _ = h.hexdigest()
            t1 = time.perf_counter()
            times.append(t1 - t0)

        total_time = sum(times)
        avg_time = total_time / len(times)
        min_time = min(times)
        max_time = max(times)

        # Throughput in MB/s: (bytes processed / elapsed_sec) / (1024 * 1024)
        throughput_mbs = (size_bytes / (avg_time * 1024 * 1024)) if avg_time > 0 else 0.0

        results.append({
            "algorithm": ALGORITHM_LABELS[alg],
            "alg_key": alg,
            "iterations": iterations,
            "bytes_per_iteration": size_bytes,
            "total_bytes_processed": size_bytes * iterations,
            "avg_time_ms": round(avg_time * 1000, 3),
            "min_time_ms": round(min_time * 1000, 3),
            "max_time_ms": round(max_time * 1000, 3),
            "total_time_ms": round(total_time * 1000, 3),
            "throughput_mbs": round(throughput_mbs, 2),
        })

    # Sort results by throughput descending
    results.sort(key=lambda r: r["throughput_mbs"], reverse=True)

    environment = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "architecture": platform.machine(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return {
        "status": "COMPLETED",
        "size_bytes": size_bytes,
        "size_label": f"{size_bytes / (1024 * 1024):.2f} MB" if size_bytes >= 1024 * 1024 else f"{size_bytes / 1024:.1f} KB",
        "iterations": iterations,
        "environment": environment,
        "results": results,
        "disclaimer": (
            "Benchmark Environment Note: Throughput metrics reflect actual execution time on this host. "
            "Performance varies based on CPU SIMD/AVX instructions, architecture (32-bit vs 64-bit), "
            "hardware cryptographic acceleration, and operating system load. MD5 and SHA-1 may benchmark fast "
            "but are cryptographically compromised."
        ),
    }
