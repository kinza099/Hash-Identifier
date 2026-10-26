"""Tests for Multi-Algorithm Hash Generator & File Integrity Verifier."""

import io
import pytest
from core.hasher import hash_stream, hash_text, verify_integrity


def test_empty_string_test_vectors():
    res = hash_text("")
    hashes = res["hashes"]
    assert hashes["md5"]["hash"] == "d41d8cd98f00b204e9800998ecf8427e"
    assert hashes["sha1"]["hash"] == "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    assert hashes["sha256"]["hash"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert hashes["sha384"]["hash"] == "38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da274edebfe76f65fbd51ad2f14898b95b"
    assert hashes["sha512"]["hash"] == "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
    assert res["is_empty_input"] is True


def test_known_phrase_test_vectors():
    phrase = "The quick brown fox jumps over the lazy dog"
    res = hash_text(phrase)
    hashes = res["hashes"]
    assert hashes["md5"]["hash"] == "9e107d9d372bb6826bd81d3542a419d6"
    assert hashes["sha1"]["hash"] == "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
    assert hashes["sha256"]["hash"] == "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"
    assert hashes["sha384"]["hash"] == "ca737f1014a48f4c0b6dd43cb177b0afd9e5169367544c494011e3317dbf9a509cb1e5dc1e85a941bbee3d7f2afbc9b1"
    assert hashes["sha512"]["hash"] == "07e547d9586f6a73f73fbac0435ed76951218fb7d0c8d788a309d785436bbb642e93a252a954f23912547d1e8a3b5ed6e1bfd7097821233fa0538f3db854fee6"


def test_unicode_consistency():
    """Verify non-ASCII characters encode to UTF-8 properly."""
    text = "CyberSec🔐安全Кибербезопасность🔒"
    res1 = hash_text(text)
    res2 = hash_text(text)
    assert res1["hashes"]["sha256"]["hash"] == res2["hashes"]["sha256"]["hash"]
    assert res1["encoding"] == "utf-8"
    assert res1["byte_length"] > res1["input_length"]


def test_legacy_security_warnings():
    res = hash_text("security test")
    md5_info = res["hashes"]["md5"]
    sha1_info = res["hashes"]["sha1"]
    sha256_info = res["hashes"]["sha256"]

    assert md5_info["is_legacy"] is True
    assert "collision" in md5_info["security_warning"].lower()
    assert sha1_info["is_legacy"] is True
    assert sha256_info["is_legacy"] is False


def test_chunked_stream_hashing():
    # Simulate a stream with 256 KB of repeating data
    content = b"LargeStreamChunkBytes1234567890" * 8192
    stream = io.BytesIO(content)

    res = hash_stream(stream, chunk_size=4096)
    assert res["total_bytes"] == len(content)
    assert "sha256" in res["hashes"]

    # Compare with hash_text of same bytes
    import hashlib
    expected_sha256 = hashlib.sha256(content).hexdigest()
    assert res["hashes"]["sha256"]["hash"] == expected_sha256


def test_empty_stream_hashing():
    empty_stream = io.BytesIO(b"")
    res = hash_stream(empty_stream)
    assert res["total_bytes"] == 0
    assert res["hashes"]["md5"]["hash"] == "d41d8cd98f00b204e9800998ecf8427e"


def test_verify_integrity_match_and_normalization():
    calc = "D7A8FBB307D7809469CA9ABCB0082E4F8D5651E46D3CDB762D02D0BF37C9E592"
    ref = "   d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592   \n"

    res = verify_integrity(calc, ref, "sha256")
    assert res["verified"] is True
    assert res["status"] == "MATCH"
    assert "Integrity Match Confirmed" in res["message"]


def test_verify_integrity_mismatch():
    calc = "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"
    ref = "0000000000000000000000000000000000000000000000000000000000000000"

    res = verify_integrity(calc, ref, "sha256")
    assert res["verified"] is False
    assert res["status"] == "MISMATCH"
    assert "Integrity Mismatch" in res["message"]


def test_verify_integrity_length_mismatch_warning():
    """If user selects SHA-256 (64 hex) but inputs 32-char MD5, show helpful length warning."""
    calc = "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"
    ref_md5 = "5f4dcc3b5aa765d61d8327deb882cf99"

    res = verify_integrity(calc, ref_md5, "sha256")
    assert res["verified"] is False
    assert res["status"] == "LENGTH_MISMATCH"
    assert "expected length for SHA-256 (64 characters)" in res["message"]


def test_verify_integrity_invalid_hex_format():
    calc = "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"
    ref_invalid = "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9eZZZ"

    res = verify_integrity(calc, ref_invalid, "sha256")
    assert res["verified"] is False
    assert res["status"] == "INVALID_FORMAT"
    assert "non-hexadecimal" in res["message"]
