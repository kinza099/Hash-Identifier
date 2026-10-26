"""Tests for Hash Detection & Structural Analysis Engine."""

import pytest
from core.detector import analyze_charset, calculate_entropy, identify_hash


def test_empty_and_whitespace_input():
    res = identify_hash("")
    assert res["valid"] is False
    assert res["length"] == 0
    assert len(res["matches"]) == 0
    assert "Please enter a hash" in res["message"]

    res_spaces = identify_hash("    ")
    assert res_spaces["valid"] is False


def test_backward_compatibility_schema():
    """Verify all original fields from initial app.py exist in response."""
    res = identify_hash("5f4dcc3b5aa765d61d8327deb882cf99")
    assert "input" in res
    assert "length" in res
    assert "is_hex" in res
    assert "valid" in res
    assert "matches" in res
    assert "match_count" in res
    assert res["valid"] is True
    assert res["length"] == 32
    assert res["is_hex"] is True
    assert len(res["matches"]) > 0

    # Verify each match item structure
    first_match = res["matches"][0]
    assert "types" in first_match
    assert "note" in first_match
    assert "confidence" in first_match
    assert isinstance(first_match["types"], list)


def test_md5_ntlm_ambiguity():
    """32 hex chars must identify MD5, MD4, NTLM with medium confidence and ambiguity warning."""
    res = identify_hash("5f4dcc3b5aa765d61d8327deb882cf99")
    types = res["matches"][0]["types"]
    assert "MD5" in types
    assert "NTLM" in types
    assert "MD4" in types
    assert res["matches"][0]["confidence"] == "medium"
    assert res["ambiguity_warning"] is not None
    assert "Format Ambiguity Warning" in res["ambiguity_warning"]
    assert "MD5" in res["ambiguity_warning"]


def test_sha1_ripemd160_ambiguity():
    """40 hex chars must identify SHA-1 and RIPEMD-160 with ambiguity notice."""
    res = identify_hash("2fd4e1c67a2d28fced849ee1bb76e7391b93eb12")
    types = res["matches"][0]["types"]
    assert "SHA-1" in types
    assert "RIPEMD-160" in types
    assert res["length"] == 40
    assert res["is_hex"] is True
    assert res["ambiguity_warning"] is not None


def test_sha256_sha3_256():
    """64 hex chars must identify SHA-256 and SHA3-256."""
    res = identify_hash("d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592")
    types = res["matches"][0]["types"]
    assert "SHA-256" in types
    assert "SHA3-256" in types
    assert res["length"] == 64


def test_sha512_sha3_512():
    """128 hex chars must identify SHA-512 and SHA3-512."""
    val = "07e547d9586f6a73f73fbac0435ed76951218fb7d0c8d788a309d785436bbb642e93a252a954f23912547d1e8a3b5ed6e1bfd7097821233fa0538f3db854fee6"
    res = identify_hash(val)
    types = res["matches"][0]["types"]
    assert "SHA-512" in types
    assert "SHA3-512" in types
    assert res["length"] == 128


def test_bcrypt_prefix_high_confidence():
    """bcrypt string with $2a$ or $2b$ must be high confidence and score >= 90."""
    b = "$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"
    res = identify_hash(b)
    assert res["valid"] is True
    assert len(res["matches"]) == 1
    m = res["matches"][0]
    assert "bcrypt" in m["types"]
    assert m["confidence"] == "high"
    assert m["score"] >= 95
    # High confidence structured formats should have no top-level ambiguity warning
    assert res["ambiguity_warning"] is None


def test_argon2_prefix_high_confidence():
    """Argon2id format detection."""
    a = "$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$RdescudvJCsgqlfreplfluxNYCkGWvHc4INGhWBdDdQ"
    res = identify_hash(a)
    assert res["valid"] is True
    m = res["matches"][0]
    assert "Argon2 (argon2id)" in m["types"]
    assert m["confidence"] == "high"


def test_cisco_type_5():
    """Cisco Type 5 / MD5-crypt."""
    c = "$1$cisco$1234567890123456789012"
    res = identify_hash(c)
    assert res["valid"] is True
    assert "Cisco Type 5 (MD5-based crypt)" in res["matches"][0]["types"]


def test_mysql41_prefix():
    """MySQL 4.1+ leading asterisk + 40 hex."""
    m = "*94BDCEBE19083CE2A1F959FD02F964C7AF4CFC29"
    res = identify_hash(m)
    assert res["valid"] is True
    assert "MySQL 4.1+ (SHA1 based)" in res["matches"][0]["types"]
    assert res["matches"][0]["confidence"] == "high"


def test_charset_analysis():
    # Lowercase hex
    cs1 = analyze_charset("abcdef0123456789")
    assert cs1["is_hex"] is True
    assert cs1["is_hex_lower"] is True
    assert cs1["is_hex_upper"] is False
    assert cs1["estimated_bits"] == 64

    # Uppercase hex
    cs2 = analyze_charset("ABCDEF0123456789")
    assert cs2["is_hex"] is True
    assert cs2["is_hex_upper"] is True
    assert cs2["is_hex_lower"] is False

    # Mixed hex
    cs3 = analyze_charset("abcDEF0123456789")
    assert cs3["is_hex"] is True
    assert cs3["is_hex_mixed"] is True

    # Shannon entropy
    ent = calculate_entropy("aaaa")
    assert ent == 0.0
    ent_varied = calculate_entropy("0123456789abcdef")
    assert ent_varied > 3.5


def test_unsupported_or_malformed_string():
    res = identify_hash("NotAValidHashString$!@#")
    assert res["valid"] is True  # Parsed, but 0 matches
    assert len(res["matches"]) == 0
    assert "No known hash format matched" in res["message"]
