"""Multi-Algorithm Hash Generation and File Integrity Verifier.

Supported Algorithms:
- MD5 (Legacy/Checksum — Broken for collision resistance)
- SHA-1 (Legacy — Broken for collision resistance)
- SHA-256 (NIST FIPS 180-4 — Recommended Standard)
- SHA-384 (NIST FIPS 180-4 — High Assurance Standard)
- SHA-512 (NIST FIPS 180-4 — High Performance 64-bit Standard)

Provides text hashing, chunked stream/file hashing, and strict integrity verification.
"""

import hashlib
import io
import re
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

SUPPORTED_ALGORITHMS = ["md5", "sha1", "sha256", "sha384", "sha512"]

ALGORITHM_DISPLAY_NAMES = {
    "md5": "MD5",
    "sha1": "SHA-1",
    "sha256": "SHA-256",
    "sha384": "SHA-384",
    "sha512": "SHA-512",
}

EXPECTED_HEX_LENGTHS = {
    "md5": 32,
    "sha1": 40,
    "sha256": 64,
    "sha384": 96,
    "sha512": 128,
}

ALGORITHM_SECURITY_WARNINGS = {
    "md5": (
        "Educational & Compatibility Warning: MD5 has known practical collision vulnerabilities "
        "(RFC 6151). It is cryptographically broken and must NOT be used for security-sensitive integrity verification "
        "or digital signatures against malicious adversaries."
    ),
    "sha1": (
        "Educational & Compatibility Warning: SHA-1 has demonstrated practical collision vulnerabilities "
        "(SHAttered attack, RFC 6194). It is deprecated by NIST and must NOT be used for security-sensitive integrity verification."
    ),
    "sha256": "Industry standard 256-bit hash. Recommended for file integrity, checksums, and cryptographic verification.",
    "sha384": "High-assurance 384-bit hash (NSA Suite B / CNSA). Recommended for high-security applications.",
    "sha512": "High-security 512-bit hash. Highly efficient on 64-bit platforms.",
}


MAX_TEXT_SIZE_BYTES = 16 * 1024 * 1024  # 16 MB


def hash_text(text: str, encoding: str = "utf-8", max_bytes: int = MAX_TEXT_SIZE_BYTES) -> Dict[str, Any]:
    """Generate hashes for a given string across all supported algorithms simultaneously.

    Unicode is fully supported and encoded to UTF-8 by default.
    Empty input is explicitly supported and produces standard canonical empty string digests.
    Enforces maximum payload size limits to prevent memory exhaustion.
    """
    if text is None:
        text = ""

    if len(text) > max_bytes:
        raise ValueError(f"Input text exceeds maximum allowed size ({max_bytes:,} bytes).")

    byte_data = text.encode(encoding)
    if len(byte_data) > max_bytes:
        raise ValueError(f"Encoded byte payload exceeds maximum allowed size ({max_bytes:,} bytes).")
    results: Dict[str, Dict[str, Any]] = {}

    for alg in SUPPORTED_ALGORITHMS:
        h = getattr(hashlib, alg)()
        h.update(byte_data)
        digest = h.hexdigest()
        results[alg] = {
            "algorithm": ALGORITHM_DISPLAY_NAMES[alg],
            "hash": digest,
            "length": len(digest),
            "security_warning": ALGORITHM_SECURITY_WARNINGS.get(alg),
            "is_legacy": alg in ("md5", "sha1"),
        }

    return {
        "input_length": len(text),
        "byte_length": len(byte_data),
        "encoding": encoding,
        "is_empty_input": len(text) == 0,
        "hashes": results,
    }


def hash_stream(
    stream: BinaryIO,
    algorithms: Optional[List[str]] = None,
    chunk_size: int = 65536,
) -> Dict[str, Any]:
    """Calculate cryptographic hashes of a binary stream incrementally in chunks.

    Reads in fixed chunk_size buffers to avoid loading large files into memory.
    """
    if algorithms is None:
        target_algs = list(SUPPORTED_ALGORITHMS)
    else:
        target_algs = [a.lower() for a in algorithms if a.lower() in SUPPORTED_ALGORITHMS]

    if not target_algs:
        raise ValueError(f"No valid algorithms specified. Supported: {SUPPORTED_ALGORITHMS}")

    hashers = {alg: getattr(hashlib, alg)() for alg in target_algs}
    total_bytes = 0

    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        total_bytes += len(chunk)
        for h in hashers.values():
            h.update(chunk)

    results: Dict[str, Dict[str, Any]] = {}
    for alg, h in hashers.items():
        digest = h.hexdigest()
        results[alg] = {
            "algorithm": ALGORITHM_DISPLAY_NAMES[alg],
            "hash": digest,
            "length": len(digest),
            "security_warning": ALGORITHM_SECURITY_WARNINGS.get(alg),
            "is_legacy": alg in ("md5", "sha1"),
        }

    return {
        "total_bytes": total_bytes,
        "hashes": results,
    }


def verify_integrity(
    calculated_hash: str,
    reference_hash: str,
    algorithm: str,
) -> Dict[str, Any]:
    """Verify calculated hash against a user-supplied reference hash.

    Normalizes harmless formatting differences (surrounding whitespace, uppercase/lowercase).
    Validates the reference hash format and length against the selected algorithm before comparison
    to avoid misleading mismatches.
    """
    alg_key = algorithm.lower().replace("-", "")
    if alg_key not in EXPECTED_HEX_LENGTHS:
        return {
            "verified": False,
            "status": "ERROR",
            "message": f"Unsupported verification algorithm: '{algorithm}'. Supported: MD5, SHA-1, SHA-256, SHA-384, SHA-512.",
        }

    expected_len = EXPECTED_HEX_LENGTHS[alg_key]
    alg_name = ALGORITHM_DISPLAY_NAMES[alg_key]

    clean_ref = reference_hash.strip().lower()
    clean_calc = calculated_hash.strip().lower()

    if not clean_ref:
        return {
            "verified": False,
            "status": "EMPTY_REFERENCE",
            "message": "No reference hash provided for verification.",
            "normalized_reference": "",
            "normalized_calculated": clean_calc,
            "algorithm": alg_name,
        }

    # Format check: must be hexadecimal
    if not re.match(r'^[0-9a-f]+$', clean_ref):
        return {
            "verified": False,
            "status": "INVALID_FORMAT",
            "message": f"The reference hash contains non-hexadecimal characters. A valid {alg_name} hash must consist only of characters 0-9 and a-f.",
            "normalized_reference": clean_ref,
            "normalized_calculated": clean_calc,
            "algorithm": alg_name,
        }

    # Length check for selected algorithm
    if len(clean_ref) != expected_len:
        return {
            "verified": False,
            "status": "LENGTH_MISMATCH",
            "message": (
                f"The reference hash length ({len(clean_ref)} characters) does not match the expected length "
                f"for {alg_name} ({expected_len} characters). Ensure you have selected the matching algorithm."
            ),
            "normalized_reference": clean_ref,
            "normalized_calculated": clean_calc,
            "expected_length": expected_len,
            "actual_length": len(clean_ref),
            "algorithm": alg_name,
        }

    is_match = (clean_calc == clean_ref)

    return {
        "verified": is_match,
        "status": "MATCH" if is_match else "MISMATCH",
        "message": (
            "Integrity Match Confirmed: The calculated file digest exactly equals the reference hash under "
            f"{alg_name}. Note: A hash match confirms content equality under this specific algorithm, "
            "but does not independently prove the file is safe, trustworthy, or free from malicious intent."
            if is_match
            else f"Integrity Mismatch: The calculated {alg_name} digest does NOT match the reference hash. The file may be corrupted, modified, or the reference hash belongs to a different version."
        ),
        "normalized_reference": clean_ref,
        "normalized_calculated": clean_calc,
        "algorithm": alg_name,
    }
