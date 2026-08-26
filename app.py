"""
Hash Identifier Tool
Author: Kinza
GitHub: https://github.com/kinza099
Email: kinzapython@gmail.com

A Flask-based web tool that takes a hash string as input and identifies
the most likely hash algorithm(s) it belongs to, based on length,
character set, and known prefix/format patterns.
"""

import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

AUTHOR_INFO = {
    "name": "Kinza",
    "github": "https://github.com/kinza099",
    "email": "kinzapython@gmail.com",
    "project": "Hash Identifier Tool",
}


# ---------------------------------------------------------------------------
# Hash detection engine — tuned to the 20 supported hash types
# ---------------------------------------------------------------------------
# Each rule: (regex pattern, list of possible hash types, short note, confidence)
# confidence: "high" = unique/near-unique match, "medium" = shared with other
# algorithms of the same output length.
HASH_RULES = [
    # --- Prefix / format based (unique, high confidence) ---
    (r'^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$', ["bcrypt"], "Blowfish-based password hash — starts with $2a$/$2b$/$2y$", "high"),
    (r'^\$argon2id\$', ["Argon2 (argon2id)"], "Hybrid Argon2 variant — resistant to GPU & side-channel attacks", "high"),
    (r'^\$argon2i\$', ["Argon2 (argon2i)"], "Memory-hard hash, optimized against side-channel attacks", "high"),
    (r'^\$argon2d\$', ["Argon2 (argon2d)"], "Memory-hard hash, optimized against GPU cracking", "high"),
    (r'^\$?scrypt\$', ["scrypt"], "Memory-hard KDF — format $scrypt$N,r,p$salt$hash", "high"),
    (r'^\$1\$', ["Cisco Type 5 (MD5-based crypt)"], "Used by Cisco IOS enable secret / Unix MD5 crypt — starts with $1$", "high"),
    (r'^\*[A-Fa-f0-9]{40}$', ["MySQL 4.1+ (SHA1 based)"], "MySQL PASSWORD() — '*' followed by 40 hex chars", "high"),
    (r'^\{SSHA\}', ["LDAP SSHA (Salted SHA-1)"], "LDAP salted SHA-1 — starts with {SSHA}", "high"),
    (r'^\{SHA\}', ["LDAP SHA"], "LDAP SHA-1, Base64 encoded — starts with {SHA}", "high"),

    # --- Hex length based (ambiguous — multiple algorithms share this length) ---
    (r'^[a-fA-F0-9]{32}$', ["MD5", "MD4", "NTLM"], "32 hex characters", "medium"),
    (r'^[a-fA-F0-9]{40}$', ["SHA-1", "RIPEMD-160"], "40 hex characters", "medium"),
    (r'^[a-fA-F0-9]{56}$', ["SHA-224", "SHA3-224"], "56 hex characters", "medium"),
    (r'^[a-fA-F0-9]{64}$', ["SHA-256", "SHA3-256"], "64 hex characters", "medium"),
    (r'^[a-fA-F0-9]{96}$', ["SHA-384", "SHA3-384"], "96 hex characters", "medium"),
    (r'^[a-fA-F0-9]{128}$', ["SHA-512", "SHA3-512"], "128 hex characters", "medium"),
]


def identify_hash(value: str):
    value = value.strip()
    if not value:
        return {"input": value, "valid": False, "matches": [], "message": "Please enter a hash to identify."}

    matches = []
    for pattern, types, note, confidence in HASH_RULES:
        if re.match(pattern, value):
            matches.append({"types": types, "note": note, "confidence": confidence})

    length = len(value)
    is_hex = bool(re.match(r'^[a-fA-F0-9]+$', value))

    result = {
        "input": value,
        "length": length,
        "is_hex": is_hex,
        "valid": True,
        "matches": matches,
        "match_count": len(matches),
    }

    if not matches:
        result["message"] = (
            "No known hash format matched this input out of the 20 supported types. "
            "Double-check the hash was copied completely (no missing characters, "
            "extra spaces, or line breaks)."
        )
    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", author=AUTHOR_INFO)


@app.route("/author")
def author():
    return render_template("author.html", author=AUTHOR_INFO)


@app.route("/api/identify", methods=["POST"])
def api_identify():
    data = request.get_json(silent=True) or {}
    hash_value = data.get("hash", "")
    result = identify_hash(hash_value)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
