"""Advanced Hash Detection and Analysis Engine.

Provides deep structural analysis of hash strings:
- Character set analysis (Hex, Base64, MCF, ASCII)
- Entropy and bit length estimation
- Known prefix and pattern detection
- Evidence-based confidence scoring and heuristic ranking
- Ambiguity warnings and algorithmic match rationale
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple


# Algorithmic metadata: description, security status, bit length, typical use
ALGORITHM_METADATA: Dict[str, Dict[str, Any]] = {
    "MD5": {
        "bit_length": 128,
        "byte_length": 16,
        "security": "Broken (Collision vulnerable)",
        "summary": "128-bit hash represented as 32 hex chars. Formerly standard for integrity verification; broken by practical collision attacks in 2004.",
        "common_in": "File checksums, legacy web apps, legacy protocols",
    },
    "MD4": {
        "bit_length": 128,
        "byte_length": 16,
        "security": "Broken",
        "summary": "128-bit predecessor to MD5. Highly vulnerable to collision and preimage attacks.",
        "common_in": "Windows NTLM foundation, obsolete software",
    },
    "NTLM": {
        "bit_length": 128,
        "byte_length": 16,
        "security": "Weak (Fast cracking, pass-the-hash)",
        "summary": "Microsoft Windows NT LAN Manager hash. An MD4 digest of the UTF-16LE password without salt.",
        "common_in": "Windows SAM database, Active Directory NTDS.dit",
    },
    "SHA-1": {
        "bit_length": 160,
        "byte_length": 20,
        "security": "Broken (SHAttered collision demonstrated)",
        "summary": "160-bit SHA-1 digest (40 hex chars). Deprecated by NIST, Google, and CISA due to collision vulnerabilities.",
        "common_in": "Git commits (historical), legacy TLS certificates, torrent files",
    },
    "RIPEMD-160": {
        "bit_length": 160,
        "byte_length": 20,
        "security": "Currently collision-resistant",
        "summary": "160-bit European cryptographic hash designed by Hans Dobbertin et al.",
        "common_in": "Bitcoin and cryptocurrency address generation (alongside SHA-256)",
    },
    "SHA-224": {
        "bit_length": 224,
        "byte_length": 28,
        "security": "Secure (NIST approved)",
        "summary": "224-bit truncated variant of SHA-256 designed to match 2-key 3DES security level.",
        "common_in": "Cryptographic protocols, X.509 certificates",
    },
    "SHA3-224": {
        "bit_length": 224,
        "byte_length": 28,
        "security": "Secure (NIST FIPS 202)",
        "summary": "224-bit Keccak sponge-construction hash standard.",
        "common_in": "Modern cryptographic suites, blockchain systems",
    },
    "SHA-256": {
        "bit_length": 256,
        "byte_length": 32,
        "security": "Secure (Current industry standard)",
        "summary": "256-bit SHA-2 digest (64 hex chars). The global standard for file integrity, code signing, and digital signatures.",
        "common_in": "TLS certificates, Bitcoin proof-of-work, software release checksums",
    },
    "SHA3-256": {
        "bit_length": 256,
        "byte_length": 32,
        "security": "Secure (NIST FIPS 202)",
        "summary": "256-bit Keccak-based SHA-3 digest. Completely different internal sponge architecture from SHA-2.",
        "common_in": "Ethereum, modern PKI, next-generation security standards",
    },
    "SHA-384": {
        "bit_length": 384,
        "byte_length": 48,
        "security": "Secure (NIST approved, NSA Suite B)",
        "summary": "384-bit truncated variant of SHA-512 (96 hex chars). High security margin.",
        "common_in": "Top Secret government communications, high-assurance TLS certificates",
    },
    "SHA3-384": {
        "bit_length": 384,
        "byte_length": 48,
        "security": "Secure (NIST FIPS 202)",
        "summary": "384-bit Keccak sponge construction hash.",
        "common_in": "Modern cryptographic protocols, post-quantum research",
    },
    "SHA-512": {
        "bit_length": 512,
        "byte_length": 64,
        "security": "Secure (Current industry standard)",
        "summary": "512-bit SHA-2 digest (128 hex chars). Highly efficient on 64-bit architectures.",
        "common_in": "Linux password shadow files (with salt), high-security integrity manifests",
    },
    "SHA3-512": {
        "bit_length": 512,
        "byte_length": 64,
        "security": "Secure (NIST FIPS 202)",
        "summary": "512-bit Keccak sponge construction hash.",
        "common_in": "Modern cryptographic standards, blockchain networks",
    },
    "bcrypt": {
        "bit_length": 184,
        "byte_length": 23,
        "security": "Secure (Adaptive password hash)",
        "summary": "Blowfish-based key derivation function with adaptive cost parameter ($2a$, $2b$, or $2y$).",
        "common_in": "Web application user authentication (Django, Node.js, Ruby on Rails)",
    },
    "scrypt": {
        "bit_length": "Variable",
        "byte_length": "Variable",
        "security": "Secure (Memory-hard password hash)",
        "summary": "Memory-hard key derivation function designed to thwart custom ASIC/FPGA hardware attacks.",
        "common_in": "Cryptocurrency (Litecoin), password managers, sensitive file encryption",
    },
    "Argon2 (argon2id)": {
        "bit_length": "Variable",
        "byte_length": "Variable",
        "security": "Secure (PHC Winner, State of the Art)",
        "summary": "Password Hashing Competition winner combining data-dependent and data-independent memory access.",
        "common_in": "Modern password hashing (OWASP #1 recommendation, KeePassXC, Bitwarden)",
    },
    "Argon2 (argon2i)": {
        "bit_length": "Variable",
        "byte_length": "Variable",
        "security": "Secure (Side-channel resistant)",
        "summary": "Data-independent memory access variant of Argon2, optimized against side-channel timing attacks.",
        "common_in": "Cryptographic authentication in untrusted hosting environments",
    },
    "Argon2 (argon2d)": {
        "bit_length": "Variable",
        "byte_length": "Variable",
        "security": "Secure (GPU cracking resistant)",
        "summary": "Data-dependent memory access variant of Argon2, offering maximum resistance against GPU mining/cracking.",
        "common_in": "Cryptocurrency proof-of-work, backend services without side-channel exposure",
    },
    "Cisco Type 5 (MD5-based crypt)": {
        "bit_length": 128,
        "byte_length": 16,
        "security": "Deprecated / Weak",
        "summary": "Standard Unix MD5-crypt with '$1$' prefix, 1-8 byte salt, and 1000 iterations.",
        "common_in": "Cisco IOS enable secret, Linux legacy /etc/shadow",
    },
    "MySQL 4.1+ (SHA1 based)": {
        "bit_length": 160,
        "byte_length": 20,
        "security": "Weak (Double-SHA1 without salt)",
        "summary": "MySQL 4.1+ PASSWORD() function: '*' followed by 40 hex chars (SHA1(SHA1(password))).",
        "common_in": "MySQL and MariaDB user tables (mysql.user authentication_string)",
    },
    "LDAP SSHA (Salted SHA-1)": {
        "bit_length": "160 + salt",
        "byte_length": "20 + salt",
        "security": "Weak (SHA-1 based)",
        "summary": "Base64 encoded SHA-1 digest concatenated with a 4-8 byte random salt, prefixed with {SSHA}.",
        "common_in": "OpenLDAP userPassword, Active Directory identity sync",
    },
    "LDAP SHA": {
        "bit_length": 160,
        "byte_length": 20,
        "security": "Broken (Unsalted SHA-1 in Base64)",
        "summary": "Base64 encoded raw SHA-1 digest prefixed with {SHA}. Easily crackable via rainbow tables.",
        "common_in": "Legacy OpenLDAP, directory services",
    },
    "CRC-32": {
        "bit_length": 32,
        "byte_length": 4,
        "security": "Non-cryptographic checksum",
        "summary": "32-bit cyclic redundancy check code (8 hex chars). Designed strictly for accidental error detection, zero security.",
        "common_in": "ZIP archives, Ethernet frames, PNG chunks",
    },
    "Adler-32": {
        "bit_length": 32,
        "byte_length": 4,
        "security": "Non-cryptographic checksum",
        "summary": "32-bit checksum algorithm used by zlib. Faster than CRC-32 with lower collision resistance.",
        "common_in": "zlib compression stream verification",
    },
    "MySQL 3.23": {
        "bit_length": 64,
        "byte_length": 8,
        "security": "Trivially broken",
        "summary": "16 hex character legacy MySQL password hash. Vulnerable to instant algorithmic recovery.",
        "common_in": "Legacy MySQL 3.x/4.0 databases",
    },
    "SHA-256 crypt": {
        "bit_length": 256,
        "byte_length": 32,
        "security": "Secure (Unix shadow standard)",
        "summary": "Modular crypt format with '$5$' prefix, salt, and iterated SHA-256 (default 5000 rounds).",
        "common_in": "Linux /etc/shadow password files",
    },
    "SHA-512 crypt": {
        "bit_length": 512,
        "byte_length": 64,
        "security": "Secure (Unix shadow default)",
        "summary": "Modular crypt format with '$6$' prefix, salt, and iterated SHA-512 (default 5000 rounds).",
        "common_in": "Modern Linux (Ubuntu, Debian, RHEL) /etc/shadow default",
    },
    "JSON Web Token (JWT)": {
        "bit_length": "Variable",
        "byte_length": "Variable",
        "security": "Depends on signing algorithm (HS256/RS256/none)",
        "summary": "Base64URL-encoded three-part structure (Header.Payload.Signature) RFC 7519.",
        "common_in": "Web API authorization, OAuth 2.0 / OpenID Connect tokens",
    },
}


# Enhanced rule definitions:
# (regex pattern, algorithm list, description, confidence, score, rationale, ambiguity_note)
DETECTION_RULES = [
    # --- Prefix / Structured Formats (High Confidence: 90 - 98) ---
    (
        r'^\$2[abyx]\$\d{2}\$[./A-Za-z0-9]{53}$',
        ["bcrypt"],
        "Blowfish-based password hash — starts with $2a$/$2b$/$2y$ with cost factor",
        "high",
        98,
        "Exact Modular Crypt Format match for bcrypt with valid cost factor and 53-character base64-style salt/ciphertext.",
        "Very low ambiguity: this specific 60-character structure with $2[abyx]$ prefix is uniquely defined for bcrypt.",
    ),
    (
        r'^\$argon2id\$(v=\d+\$)?(m=\d+,t=\d+,p=\d+\$)?[A-Za-z0-9+/=]+\$[A-Za-z0-9+/=]+$',
        ["Argon2 (argon2id)"],
        "Hybrid Argon2 variant — resistant to GPU & side-channel attacks",
        "high",
        96,
        "Matches canonical Argon2id string format containing algorithm tag, memory/time/thread parameters, salt, and key.",
        "Unique format identifier ($argon2id$).",
    ),
    (
        r'^\$argon2i\$(v=\d+\$)?(m=\d+,t=\d+,p=\d+\$)?[A-Za-z0-9+/=]+\$[A-Za-z0-9+/=]+$',
        ["Argon2 (argon2i)"],
        "Memory-hard hash, optimized against side-channel attacks",
        "high",
        96,
        "Matches canonical Argon2i format designed for data-independent memory access.",
        "Unique format identifier ($argon2i$).",
    ),
    (
        r'^\$argon2d\$(v=\d+\$)?(m=\d+,t=\d+,p=\d+\$)?[A-Za-z0-9+/=]+\$[A-Za-z0-9+/=]+$',
        ["Argon2 (argon2d)"],
        "Memory-hard hash, optimized against GPU cracking",
        "high",
        96,
        "Matches canonical Argon2d format with data-dependent memory access.",
        "Unique format identifier ($argon2d$).",
    ),
    (
        r'^\$?scrypt\$(ln=\d+,r=\d+,p=\d+\$)?[A-Za-z0-9+/=]+\$[A-Za-z0-9+/=]+$',
        ["scrypt"],
        "Memory-hard KDF — format $scrypt$N,r,p$salt$hash",
        "high",
        95,
        "Matches scrypt modular format containing work parameters N, r, p followed by salt and digest.",
        "Unique format identifier ($scrypt$).",
    ),
    (
        r'^\$1\$[./a-zA-Z0-9]{1,8}\$[./a-zA-Z0-9]{22}$',
        ["Cisco Type 5 (MD5-based crypt)"],
        "Used by Cisco IOS enable secret / Unix MD5 crypt — starts with $1$",
        "high",
        94,
        "Matches standard Unix/Cisco MD5-crypt: $1$ followed by 1-8 byte salt and 22-char base64 digest.",
        "Low ambiguity: the $1$ prefix and length conform specifically to MD5-crypt.",
    ),
    (
        r'^\$5\$(rounds=\d+\$)?[./a-zA-Z0-9]{1,16}\$[./a-zA-Z0-9]{43}$',
        ["SHA-256 crypt"],
        "Unix shadow password hash (SHA-256 based) — starts with $5$",
        "high",
        94,
        "Matches Unix crypt standard for SHA-256 with optional rounds parameter and 43-character digest.",
        "Low ambiguity: specific to SHA-256 crypt format.",
    ),
    (
        r'^\$6\$(rounds=\d+\$)?[./a-zA-Z0-9]{1,16}\$[./a-zA-Z0-9]{86}$',
        ["SHA-512 crypt"],
        "Unix shadow password hash (SHA-512 based) — starts with $6$",
        "high",
        94,
        "Matches modern Unix /etc/shadow standard for SHA-512 with optional rounds and 86-character digest.",
        "Low ambiguity: specific to SHA-512 crypt format.",
    ),
    (
        r'^\*[A-Fa-f0-9]{40}$',
        ["MySQL 4.1+ (SHA1 based)"],
        "MySQL PASSWORD() — '*' followed by 40 hex chars",
        "high",
        92,
        "Matches MySQL 4.1+ authentication string format: leading asterisk followed by 40 hex characters.",
        "Distinctive structure: leading asterisk differentiates from plain 40-char SHA-1.",
    ),
    (
        r'^\{SSHA\}[A-Za-z0-9+/=]{28,}$',
        ["LDAP SSHA (Salted SHA-1)"],
        "LDAP salted SHA-1 — starts with {SSHA}",
        "high",
        90,
        "Matches LDAP userPassword salted SHA-1 scheme with {SSHA} identifier.",
        "Explicit scheme prefix.",
    ),
    (
        r'^\{SHA\}[A-Za-z0-9+/=]{27,28}$',
        ["LDAP SHA"],
        "LDAP SHA-1, Base64 encoded — starts with {SHA}",
        "high",
        90,
        "Matches standard LDAP {SHA} prefix followed by 20 bytes encoded in Base64.",
        "Explicit scheme prefix.",
    ),
    (
        r'^[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}$',
        ["JSON Web Token (JWT)"],
        "JSON Web Token — three Base64URL segments separated by periods",
        "high",
        88,
        "Matches RFC 7519 compact serialization of Header.Payload.Signature.",
        "Distinctive three-part dot-separated base64url structure.",
    ),

    # --- Hex Length Based (Medium Confidence: 55 - 65) ---
    (
        r'^[a-fA-F0-9]{8}$',
        ["CRC-32", "Adler-32"],
        "8 hex characters (32-bit checksum)",
        "medium",
        60,
        "Matches standard 32-bit (4-byte) checksum represented as 8 hexadecimal digits.",
        "High format ambiguity: 8 hex characters is a shared representation for CRC-32, Adler-32, and short truncated hashes.",
    ),
    (
        r'^[a-fA-F0-9]{16}$',
        ["MySQL 3.23"],
        "16 hex characters (64-bit hash)",
        "medium",
        60,
        "Matches 64-bit (8-byte) legacy password or truncated hash represented as 16 hexadecimal characters.",
        "Ambiguous: shared by legacy MySQL 3.23 and 64-bit CRC/checksum algorithms.",
    ),
    (
        r'^[a-fA-F0-9]{32}$',
        ["MD5", "MD4", "NTLM"],
        "32 hex characters (128-bit hash)",
        "medium",
        65,
        "Matches standard 128-bit (16-byte) digest represented as 32 hexadecimal characters.",
        "High format ambiguity: 32 hex characters is structurally identical across MD5, MD4, and Windows NTLM. Without context or rainbow lookup, the specific algorithm cannot be distinguished.",
    ),
    (
        r'^[a-fA-F0-9]{40}$',
        ["SHA-1", "RIPEMD-160"],
        "40 hex characters (160-bit hash)",
        "medium",
        65,
        "Matches standard 160-bit (20-byte) digest represented as 40 hexadecimal characters.",
        "Format ambiguity: 40 hex characters is shared between SHA-1 and RIPEMD-160.",
    ),
    (
        r'^[a-fA-F0-9]{56}$',
        ["SHA-224", "SHA3-224"],
        "56 hex characters (224-bit hash)",
        "medium",
        62,
        "Matches 224-bit (28-byte) digest represented as 56 hexadecimal characters.",
        "Format ambiguity: 56 hex characters is shared between SHA-224 and SHA3-224.",
    ),
    (
        r'^[a-fA-F0-9]{64}$',
        ["SHA-256", "SHA3-256"],
        "64 hex characters (256-bit hash)",
        "medium",
        65,
        "Matches standard 256-bit (32-byte) digest represented as 64 hexadecimal characters.",
        "Format ambiguity: 64 hex characters is shared between SHA-256 and SHA3-256. SHA-256 is significantly more prevalent in contemporary software.",
    ),
    (
        r'^[a-fA-F0-9]{96}$',
        ["SHA-384", "SHA3-384"],
        "96 hex characters (384-bit hash)",
        "medium",
        65,
        "Matches standard 384-bit (48-byte) digest represented as 96 hexadecimal characters.",
        "Format ambiguity: 96 hex characters is shared between SHA-384 and SHA3-384.",
    ),
    (
        r'^[a-fA-F0-9]{128}$',
        ["SHA-512", "SHA3-512"],
        "128 hex characters (512-bit hash)",
        "medium",
        65,
        "Matches standard 512-bit (64-byte) digest represented as 128 hexadecimal characters.",
        "Format ambiguity: 128 hex characters is shared between SHA-512 and SHA3-512. Both produce 512-bit digests.",
    ),

    # --- Base64 Length Based (Low/Medium Confidence: 40 - 55) ---
    (
        r'^[A-Za-z0-9+/]{22}==$',
        ["MD5 (Base64)", "NTLM (Base64)"],
        "24-character Base64 string with double padding (16 bytes / 128-bit)",
        "low",
        45,
        "Matches Base64 representation of a 16-byte (128-bit) raw digest.",
        "Base64 strings may also represent arbitrary binary data.",
    ),
    (
        r'^[A-Za-z0-9+/]{27}=$',
        ["SHA-1 (Base64)", "RIPEMD-160 (Base64)"],
        "28-character Base64 string with single padding (20 bytes / 160-bit)",
        "low",
        45,
        "Matches Base64 representation of a 20-byte (160-bit) raw digest.",
        "Base64 strings may also represent arbitrary binary data.",
    ),
    (
        r'^[A-Za-z0-9+/]{43}=$',
        ["SHA-256 (Base64)"],
        "44-character Base64 string with single padding (32 bytes / 256-bit)",
        "low",
        45,
        "Matches Base64 representation of a 32-byte (256-bit) raw digest.",
        "Base64 strings may also represent arbitrary binary data.",
    ),
    (
        r'^[A-Za-z0-9+/]{86}==$',
        ["SHA-512 (Base64)"],
        "88-character Base64 string with double padding (64 bytes / 512-bit)",
        "low",
        45,
        "Matches Base64 representation of a 64-byte (512-bit) raw digest.",
        "Base64 strings may also represent arbitrary binary data.",
    ),
]


def calculate_entropy(s: str) -> float:
    """Calculate Shannon entropy (bits per character) of a string."""
    if not s:
        return 0.0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)


def analyze_charset(value: str) -> Dict[str, Any]:
    """Analyze the character set, format categories, and entropy of a hash string."""
    length = len(value)
    is_hex_lower = bool(re.match(r'^[0-9a-f]+$', value))
    is_hex_upper = bool(re.match(r'^[0-9A-F]+$', value))
    is_hex_mixed = bool(re.match(r'^[0-9a-fA-F]+$', value)) and not (is_hex_lower or is_hex_upper)
    is_hex = is_hex_lower or is_hex_upper or is_hex_mixed

    is_base64 = bool(re.match(r'^[A-Za-z0-9+/]+={0,2}$', value)) and (length % 4 == 0)
    is_base64url = bool(re.match(r'^[A-Za-z0-9_-]+$', value))
    is_mcf = bool(value.startswith('$'))

    # Estimate underlying bit length for standard hex
    estimated_bits: Optional[int] = None
    estimated_bytes: Optional[int] = None
    if is_hex and length % 2 == 0:
        estimated_bytes = length // 2
        estimated_bits = estimated_bytes * 8

    # Determine primary charset description
    if is_hex_lower:
        charset_desc = "Hexadecimal (lowercase 0-9, a-f)"
    elif is_hex_upper:
        charset_desc = "Hexadecimal (uppercase 0-9, A-F)"
    elif is_hex_mixed:
        charset_desc = "Hexadecimal (mixed case 0-9, a-f, A-F)"
    elif is_mcf:
        charset_desc = "Modular Crypt Format (MCF: $, alphanumeric, salt chars)"
    elif is_base64:
        charset_desc = "Base64 (A-Z, a-z, 0-9, +, /, =)"
    elif is_base64url:
        charset_desc = "Base64URL (A-Z, a-z, 0-9, -, _)"
    else:
        charset_desc = "Custom / Special / Mixed character set"

    entropy = round(calculate_entropy(value), 3)

    return {
        "length": length,
        "is_hex": is_hex,
        "is_hex_lower": is_hex_lower,
        "is_hex_upper": is_hex_upper,
        "is_hex_mixed": is_hex_mixed,
        "is_base64": is_base64,
        "is_base64url": is_base64url,
        "is_mcf": is_mcf,
        "charset_description": charset_desc,
        "entropy": entropy,
        "estimated_bits": estimated_bits,
        "estimated_bytes": estimated_bytes,
    }


def identify_hash(value: str) -> Dict[str, Any]:
    """Identify possible hash algorithms for a given hash string.

    Maintains 100% backward compatibility with the original identify_hash output
    while enriching results with ranked match scores, ambiguity warnings,
    and detailed rationale.
    """
    cleaned = value.strip()
    if not cleaned:
        return {
            "input": value,
            "length": 0,
            "is_hex": False,
            "valid": False,
            "matches": [],
            "match_count": 0,
            "message": "Please enter a hash to identify.",
            "charset_info": {},
            "ambiguity_warning": None,
        }

    charset = analyze_charset(cleaned)
    matches: List[Dict[str, Any]] = []

    for pattern, types, note, confidence, score, rationale, ambiguity in DETECTION_RULES:
        if re.match(pattern, cleaned):
            # Assemble algorithm-specific rationale
            detailed_types = []
            for t in types:
                meta = ALGORITHM_METADATA.get(t, {})
                detailed_types.append({
                    "name": t,
                    "bit_length": meta.get("bit_length"),
                    "security": meta.get("security"),
                    "summary": meta.get("summary"),
                    "common_in": meta.get("common_in"),
                })

            matches.append({
                "types": types,  # backward compatible list of string algorithm names
                "note": note,    # backward compatible string
                "confidence": confidence,  # "high", "medium", "low"
                "score": score,  # evidence-based match score 0-100
                "rationale": rationale,
                "ambiguity_note": ambiguity,
                "algorithm_details": detailed_types,
            })

    # Sort matches by score descending
    matches.sort(key=lambda m: m["score"], reverse=True)

    # Top-level ambiguity assessment
    ambiguity_warning: Optional[str] = None
    if len(matches) > 0:
        total_unique_algorithms = set()
        for m in matches:
            total_unique_algorithms.update(m["types"])

        if len(total_unique_algorithms) > 1 and matches[0]["confidence"] != "high":
            alg_list = ", ".join(sorted(total_unique_algorithms))
            ambiguity_warning = (
                f"Format Ambiguity Warning: Multiple plausible algorithms match this structure ({alg_list}). "
                "Because cryptographic hash functions produce uniform outputs of fixed length, a hash string alone "
                "cannot definitively identify the originating algorithm without system context or dictionary/rainbow lookup."
            )

    result: Dict[str, Any] = {
        "input": cleaned,
        "length": charset["length"],
        "is_hex": charset["is_hex"],
        "valid": True,
        "matches": matches,
        "match_count": len(matches),
        "charset_info": charset,
        "ambiguity_warning": ambiguity_warning,
    }

    if not matches:
        result["message"] = (
            "No known hash format matched this input out of the supported types. "
            "Double-check that the hash was copied completely with no truncated characters, "
            "spurious whitespace, or unsupported encodings."
        )

    return result
