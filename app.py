"""Hash Identifier — Advanced Hash Analysis Toolkit.

Authors:
- Kinza (GitHub: https://github.com/kinza099, Email: kinzapython@gmail.com)
- Salman Mallah (GitHub: https://github.com/salmanmallah)

An advanced cybersecurity utility and analysis toolkit featuring:
1. Advanced Hash Identification & Structural Analysis (ranked scores & ambiguity alerts)
2. Batch Hash Scanner (multiline & CSV/TXT upload with sorting/filtering)
3. Multi-Algorithm Hash Generator (MD5, SHA-1, SHA-256, SHA-384, SHA-512 with Unicode support)
4. File Hash Calculator & Integrity Verifier (chunked streaming, live preview, match/mismatch verification)
5. Duplicate Hash Detection (grouping, line numbers, occurrence counts)
6. Hash List Diff Analyzer (List A vs List B common, added, removed, unique)
7. Hash Manifest Generator & Verifier (SHA-256 integrity manifests)
8. Local Reference Database (SQLite search, import, export, provenance tracking)
9. Hash Performance Benchmark (measured timing and throughput)
"""

import io
import json
from typing import Any, Dict, List

from flask import Flask, Response, jsonify, render_template, request

from core.batch import find_duplicates, process_batch
from core.benchmark import run_benchmark
from core.database import (
    add_record,
    delete_record,
    export_records_csv,
    export_records_json,
    import_records,
    init_db,
    list_records,
    search_hash,
)
from core.detector import DETECTION_RULES, identify_hash
from core.diff import analyze_diff
from core.hasher import (
    SUPPORTED_ALGORITHMS,
    hash_stream,
    hash_text,
    verify_integrity,
)
from core.manifest import (
    generate_manifest,
    manifest_to_csv,
    parse_manifest,
    verify_manifest,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024 * 1024  # 256MB max upload limit for backend file hasher

AUTHORS: List[Dict[str, Any]] = [
    {
        "name": "Kinza",
        "github_username": "kinza099",
        "github_url": "https://github.com/kinza099",
        "avatar_url": "https://github.com/kinza099.png",
        "role": "Security Researcher & Software Engineer",
        "email": "kinzapython@gmail.com",
        "affiliation": "Cybersecurity & Software Engineering",
        "bio": (
            "Security researcher and software engineer specializing in cryptographic systems, "
            "vulnerability assessment, and secure full-stack software development. "
            "Co-creator of the Hash Identifier structural analysis engine and toolkit architecture."
        ),
        "skills": [
            "Cryptography",
            "Software Engineering",
            "Application Security",
            "Python / Flask",
            "Threat Analysis",
            "Full-Stack Development",
        ],
        "tags": [
            "Security Researcher",
            "Software Engineer",
            "Cryptography",
            "Core Architect",
        ],
        "github": "https://github.com/kinza099",
        "project": "Hash Identifier — Advanced Hash Analysis Toolkit",
    },
    {
        "name": "Salman Mallah",
        "github_username": "salmanmallah",
        "github_url": "https://github.com/salmanmallah",
        "avatar_url": "https://github.com/salmanmallah.png",
        "role": "Cyber Security Engineer & Malware Analyst",
        "email": "",
        "affiliation": "Mehran University of Engineering and Technology (MUET)",
        "bio": (
            "Cybersecurity engineer and malware analyst specializing in reverse engineering, "
            "binary triage, digital forensics, and threat research at MUET. "
            "Co-creator focusing on hash identification rules, cryptographic integrity, and forensic workflows."
        ),
        "skills": [
            "Malware Analysis",
            "Reverse Engineering",
            "Cyber Security Engineering",
            "Binary Analysis",
            "Digital Forensics",
            "Security Tooling",
        ],
        "tags": [
            "Cyber Security Engineer",
            "Malware Analyst",
            "MUET",
            "Security Tooling",
        ],
        "github": "https://github.com/salmanmallah",
        "project": "Hash Identifier — Advanced Hash Analysis Toolkit",
    },
]

# Backward compatibility alias for any component expecting single author dictionary
AUTHOR_INFO = AUTHORS[0]

# Backward compatibility alias for any external code importing HASH_RULES
HASH_RULES = [
    (r[0], r[1], r[2], r[3]) for r in DETECTION_RULES
]

# Initialize local reference database on startup
init_db()


@app.context_processor
def inject_metadata() -> Dict[str, Any]:
    """Inject author and project metadata into all templates."""
    return {
        "authors": AUTHORS,
        "author": AUTHOR_INFO,
        "project_name": "Hash Identifier — Advanced Hash Analysis Toolkit",
    }


# ---------------------------------------------------------------------------
# View Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Main toolkit dashboard with all integrated hash tools."""
    return render_template("index.html", authors=AUTHORS, author=AUTHOR_INFO)


@app.route("/author")
@app.route("/authors")
def author():
    """Authors and project information page."""
    return render_template("author.html", authors=AUTHORS, author=AUTHOR_INFO)


@app.route("/api/authors", methods=["GET"])
@app.route("/api/author", methods=["GET"])
def api_authors():
    """Return JSON metadata for toolkit authors and project."""
    return jsonify({
        "project": "Hash Identifier — Advanced Hash Analysis Toolkit",
        "authors": AUTHORS,
        "count": len(AUTHORS),
    })


# ---------------------------------------------------------------------------
# API Routes: 1. Hash Identifier & Advanced Analysis
# ---------------------------------------------------------------------------
@app.route("/api/identify", methods=["POST"])
def api_identify():
    """Identify possible hash algorithms for a single input string.

    Maintains 100% backward compatibility with original API schema
    while providing enriched confidence scores, ambiguity warnings, and rationale.
    """
    data = request.get_json(silent=True) or {}
    hash_value = data.get("hash", "")
    result = identify_hash(hash_value)
    return jsonify(result)


# ---------------------------------------------------------------------------
# API Routes: 2. Batch Hash Scanner
# ---------------------------------------------------------------------------
@app.route("/api/batch-identify", methods=["POST"])
def api_batch_identify():
    """Analyze a batch of hashes from multiline text or CSV."""
    compact = request.args.get("compact", "false").lower() == "true"
    if request.is_json:
        data = request.get_json(silent=True) or {}
        raw_text = data.get("text", "")
        is_csv = data.get("is_csv", False)
        csv_column = data.get("column", None)
        compact = compact or data.get("compact", False)
    elif "file" in request.files:
        uploaded_file = request.files["file"]
        filename = uploaded_file.filename or ""
        is_csv = filename.lower().endswith(".csv")
        raw_text = uploaded_file.stream.read().decode("utf-8", errors="replace")
        csv_column = request.form.get("column", None)
        compact = compact or (request.form.get("compact", "false").lower() == "true")
    else:
        raw_text = request.form.get("text", "")
        is_csv = request.form.get("is_csv", "false").lower() == "true"
        csv_column = request.form.get("column", None)
        compact = compact or (request.form.get("compact", "false").lower() == "true")

    results = process_batch(raw_text, is_csv=is_csv, csv_column=csv_column, compact=compact)
    return jsonify(results)


# ---------------------------------------------------------------------------
# API Routes: 3. Multi-Algorithm Hash Generator
# ---------------------------------------------------------------------------
@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Generate MD5, SHA-1, SHA-256, SHA-384, SHA-512 hashes from input text."""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    encoding = data.get("encoding", "utf-8")
    try:
        result = hash_text(text, encoding=encoding)
        return jsonify(result)
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400


# ---------------------------------------------------------------------------
# API Routes: 4. File Hash Calculator & Integrity Verifier
# ---------------------------------------------------------------------------
@app.route("/api/hash-file", methods=["POST"])
def api_hash_file():
    """Calculate cryptographic hashes of an uploaded file stream.

    Processes files in streaming chunks without loading full file into memory.
    Files are never executed and never written to disk.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    uploaded_file = request.files["file"]
    if not uploaded_file.filename:
        return jsonify({"error": "No file selected."}), 400

    algorithm = request.form.get("algorithm", "all").lower()
    algorithms = None if algorithm == "all" else [algorithm]

    try:
        res = hash_stream(uploaded_file.stream, algorithms=algorithms)
        res["filename"] = uploaded_file.filename
        return jsonify(res)
    except Exception as ex:
        return jsonify({"error": f"File hashing failed: {str(ex)}"}), 500


@app.route("/api/verify-integrity", methods=["POST"])
def api_verify_integrity():
    """Verify calculated hash against a reference hash."""
    data = request.get_json(silent=True) or {}
    calc_hash = data.get("calculated_hash", "")
    ref_hash = data.get("reference_hash", "")
    algorithm = data.get("algorithm", "sha256")

    res = verify_integrity(calc_hash, ref_hash, algorithm)
    return jsonify(res)


# ---------------------------------------------------------------------------
# API Routes: 5. Duplicate Hash Detection
# ---------------------------------------------------------------------------
@app.route("/api/duplicates", methods=["POST"])
def api_duplicates():
    """Detect and group repeated hash values."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
        raw_text = data.get("text", "")
        case_sensitive = data.get("case_sensitive", False)
    elif "file" in request.files:
        uploaded_file = request.files["file"]
        raw_text = uploaded_file.stream.read().decode("utf-8", errors="replace")
        case_sensitive = request.form.get("case_sensitive", "false").lower() == "true"
    else:
        raw_text = request.form.get("text", "")
        case_sensitive = request.form.get("case_sensitive", "false").lower() == "true"

    res = find_duplicates(raw_text, case_sensitive=case_sensitive)
    return jsonify(res)


# ---------------------------------------------------------------------------
# API Routes: 6. Hash List Diff Analyzer
# ---------------------------------------------------------------------------
@app.route("/api/diff", methods=["POST"])
def api_diff():
    """Compare Hash List A and Hash List B."""
    data = request.get_json(silent=True) or {}
    text_a = data.get("list_a", "")
    text_b = data.get("list_b", "")
    case_sensitive = data.get("case_sensitive", False)

    res = analyze_diff(text_a, text_b, case_sensitive=case_sensitive)
    return jsonify(res)


# ---------------------------------------------------------------------------
# API Routes: 7. Hash Manifest Generator & Verifier
# ---------------------------------------------------------------------------
@app.route("/api/manifest/generate", methods=["POST"])
def api_manifest_generate():
    """Generate SHA-256 manifest from list of files."""
    data = request.get_json(silent=True) or {}
    files = data.get("files", [])
    creator = data.get("creator", "Hash Identifier Toolkit")
    manifest = generate_manifest(files, creator=creator)
    return jsonify(manifest)


@app.route("/api/manifest/verify", methods=["POST"])
def api_manifest_verify():
    """Verify target files against a reference manifest."""
    data = request.get_json(silent=True) or {}
    manifest_data = data.get("manifest", {})
    current_files = data.get("current_files", [])

    if isinstance(manifest_data, str):
        try:
            manifest_data = parse_manifest(manifest_data)
        except Exception as ex:
            return jsonify({"error": f"Invalid manifest format: {str(ex)}"}), 400

    result = verify_manifest(manifest_data, current_files)
    return jsonify(result)


# ---------------------------------------------------------------------------
# API Routes: 8. Local Hash Lookup Database
# ---------------------------------------------------------------------------
@app.route("/api/db/search", methods=["GET"])
def api_db_search():
    """Search for exact hash in local reference database."""
    query = request.args.get("hash", "")
    result = search_hash(query)
    return jsonify(result)


@app.route("/api/db/records", methods=["GET", "POST"])
def api_db_records():
    """List or add reference records."""
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        try:
            rec = add_record(
                hash_val=data.get("hash", ""),
                algorithm=data.get("algorithm", "Unknown"),
                source=data.get("source", "User Entry"),
                notes=data.get("notes", ""),
                tag=data.get("tag", "General"),
            )
            return jsonify({"status": "SUCCESS", "record": rec}), 201
        except Exception as ex:
            return jsonify({"error": str(ex)}), 400
    else:
        limit = int(request.args.get("limit", 100))
        records = list_records(limit=limit)
        return jsonify({"records": records, "count": len(records)})


@app.route("/api/db/records/<int:record_id>", methods=["DELETE"])
def api_db_delete(record_id: int):
    """Delete a reference record by ID."""
    success = delete_record(record_id)
    return jsonify({"success": success})


@app.route("/api/db/export", methods=["GET"])
def api_db_export():
    """Export reference records in JSON or CSV format."""
    fmt = request.args.get("format", "json").lower()
    if fmt == "csv":
        csv_data = export_records_csv()
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=reference_hashes.csv"},
        )
    else:
        json_data = export_records_json()
        return Response(
            json_data,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment;filename=reference_hashes.json"},
        )


@app.route("/api/db/import", methods=["POST"])
def api_db_import():
    """Import reference records from JSON or CSV text."""
    if "file" in request.files:
        uploaded_file = request.files["file"]
        data_text = uploaded_file.stream.read().decode("utf-8", errors="replace")
    elif request.is_json:
        data = request.get_json(silent=True) or {}
        data_text = data.get("data", "")
        if isinstance(data_text, (list, dict)):
            data_text = json.dumps(data_text)
    else:
        data_text = request.form.get("data", "")

    result = import_records(data_text)
    return jsonify(result)


# ---------------------------------------------------------------------------
# API Routes: 9. Hash Performance Benchmark
# ---------------------------------------------------------------------------
@app.route("/api/benchmark", methods=["POST"])
def api_benchmark():
    """Execute hash performance benchmark on server with bounded parameter limits."""
    data = request.get_json(silent=True) or {}
    try:
        size_bytes = int(data.get("size_bytes", 1024 * 1024))
    except (ValueError, TypeError):
        size_bytes = 1024 * 1024
    try:
        iterations = int(data.get("iterations", 5))
    except (ValueError, TypeError):
        iterations = 5

    res = run_benchmark(size_bytes=size_bytes, iterations=iterations)
    return jsonify(res)



@app.errorhandler(404)
def page_not_found(e):
    """Custom branded 404 error page."""
    return render_template("404.html", authors=AUTHORS, author=AUTHOR_INFO), 404

# Pre-initialize local database schema at startup to avoid per-request overhead
try:
    init_db()
except Exception as _db_err:
    app.logger.warning("Startup database initialization: %s", _db_err)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
