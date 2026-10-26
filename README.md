# Hash Identifier — Advanced Cryptographic Analysis Toolkit

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?style=flat-square&logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![Tests](https://img.shields.io/badge/Tests-47%20Passed-brightgreen?style=flat-square&logo=pytest&logoColor=white)](#testing-and-quality-assurance)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![Security](https://img.shields.io/badge/Privacy-Zero%20Server%20Uploads-success?style=flat-square)](#4-file-hash-calculator--integrity-verifier)
[![Status](https://img.shields.io/badge/Status-Active%20Production-brightgreen?style=flat-square)](#)

A professional, privacy-first cybersecurity utility and cryptographic analysis toolkit built with **Python (Flask)** and **vanilla JavaScript**. Designed for security analysts, penetration testers, forensic investigators, and developers, this toolkit provides deep structural hash identification, batch processing, multi-algorithm digest generation, zero-upload streaming file hashing, cryptographic verification, list diff analysis, SHA-256 manifests, a local SQLite reference catalog, and empirical performance benchmarking.

---

## Table of Contents

- [Overview](#overview)
- [Core Features](#core-features)
  - [1. Advanced Hash Identification](#1-advanced-hash-identification)
  - [2. Batch Hash Scanner](#2-batch-hash-scanner)
  - [3. Multi-Algorithm Hash Generator](#3-multi-algorithm-hash-generator)
  - [4. File Hash Calculator & Integrity Verifier](#4-file-hash-calculator--integrity-verifier)
  - [5. Duplicate Hash Detection](#5-duplicate-hash-detection)
  - [6. Hash List Diff Analyzer](#6-hash-list-diff-analyzer)
  - [7. Hash Manifest Generator & Verifier](#7-hash-manifest-generator--verifier)
  - [8. Backend Reference Database API](#8-backend-reference-database-api)
  - [9. Hash Performance Benchmark](#9-hash-performance-benchmark)
  - [10. Professional Cyber GUI with Google Material Symbols](#10-professional-cyber-gui-with-google-material-symbols)
- [Supported Cryptographic and Structural Formats](#supported-cryptographic-and-structural-formats)
- [Project Architecture](#project-architecture)
- [Installation and Setup](#installation-and-setup)
- [Usage Guide](#usage-guide)
- [Security, Privacy, and Integrity Guarantees](#security-privacy-and-integrity-guarantees)
- [Testing and Quality Assurance](#testing-and-quality-assurance)
- [REST API Reference](#rest-api-reference)
- [Authors and Contributors](#authors-and-contributors)
- [License](#license)

---

## Overview

In cybersecurity operations, reverse engineering, and digital forensics, quickly identifying and verifying hashes is critical. Standard hash identification utilities frequently suffer from:
1. False certainty, claiming an arbitrary 32-character hexadecimal string is definitely MD5 when it could just as easily be NTLM or MD4.
2. Insecure file uploads, requiring sensitive binaries or proprietary files to be transmitted over networks to remote servers.
3. Rigid interfaces, lacking support for batch triage, manifest generation, list comparisons, and empirical performance measurements.

**Hash Identifier** solves these challenges by combining a client-side chunked streaming engine with a rigorous heuristic detection backend. It scores candidate algorithms using multi-factor evidence (length, charset, entropy, and structural prefix signatures) while clearly displaying format ambiguity notices. All file hashing operations run locally within the user's browser, ensuring zero data transmission across the wire.

---

## Core Features

| Feature | Capability | Execution Model |
|---|---|---|
| **1. Advanced Hash Identification** | Identifies 20+ hash formats using bit-length, character sets, Shannon entropy, and prefix signatures. Delivers weighted confidence scores with explicit format ambiguity warnings. | Client / REST API |
| **2. Batch Hash Scanner** | Ingests hundreds of hashes via multiline text or TXT/CSV uploads. Retains exact line numbering, tracks duplicates, and exports structured reports. | Client / REST API |
| **3. Multi-Algorithm Hash Generator** | Computes MD5, SHA-1, SHA-256, SHA-384, and SHA-512 concurrently with full UTF-8 encoding support and copy utilities. | Client / REST API |
| **4. File Hash Calculator & Integrity Verifier** | High-speed, non-blocking 2MB chunked streaming hashing entirely in browser memory. Verifies against reference digests with format pre-validation and normalization. | Local Browser / Zero Uploads |
| **5. Duplicate Hash Detection** | Identifies repeated hash strings, counts frequencies, tracks line indexes, and generates sanitized unique or duplicate-only lists. | Client / REST API |
| **6. Hash List Diff Analyzer** | Compares baseline (List A) against target (List B) to isolate common hashes, newly introduced entries, removed entries, and internal duplicates. | Client / REST API |
| **7. Hash Manifest Generator & Verifier** | Generates SHA-256 manifest records for directories or filesets. Verifies integrity by categorizing files into Unchanged, Modified, Missing, and Newly Added. | Local Browser / REST API |
| **8. Backend Reference Database API** | Pre-seeded SQLite catalog with RFC 1321 test vectors, EICAR signatures, and provenance tracking. Supports custom record addition, exact lookup, and JSON/CSV import/export via REST API. | Local SQLite / REST API |
| **9. Hash Performance Benchmark** | Executes controlled micro-benchmarks with selectable payload sizes (64KB to 16MB) and iterations. Measures execution time and throughput (MB/s). | Client & Server Engines |
| **10. Professional Cyber GUI** | Modern cyber-styled responsive interface with dark/light themes, custom CSS tokens, and vector-rendered Google Material Symbols. | Browser / Responsive UI |

### 1. Advanced Hash Identification
- **Deep Structural Analysis:** Evaluates input bit-length, character sets, and distinct prefix signatures.
- **Shannon Entropy Calculation:** Computes information entropy (bits/character) to evaluate randomness and distinguish cryptographic digests from encoded structures.
- **Character Set Profiling:** Analyzes whether the string conforms strictly to Hexadecimal (lowercase/uppercase), Base64, ASCII, or Unix crypt salt alphabets.
- **Heuristic Confidence Scoring:** Allocates weighted scores (e.g., 98% for distinct prefix matches like `$2b$` or `$argon2id$`, 65% for shared-length hex digests).
- **Format Ambiguity Warnings:** Explicitly alerts users when a string matches multiple potential algorithms (e.g., MD5 vs. NTLM vs. MD4).
- **Recent Lookups History:** Caches previous lookups in a local session tray for quick review, reloading, and copy actions.

### 2. Batch Hash Scanner
- **Multiline & File Ingestion:** Accepts direct multiline paste or drag-and-drop file uploads (.txt and .csv).
- **Exact Line Tracking:** Preserves the original file line index for every hash entry to streamline audit workflows.
- **Duplicate Counting:** Flags repeated hashes in the batch and displays individual occurrence counts.
- **Dynamic Filtering:** Filter results by validation state (Valid, Invalid), confidence level (High, Medium, Low), or substring search.
- **Structured Export:** Export complete batch assessment tables directly to CSV or JSON formats.

### 3. Multi-Algorithm Hash Generator
- **Concurrent Computation:** Generates MD5, SHA-1, SHA-256, SHA-384, and SHA-512 hashes simultaneously in real time.
- **Full UTF-8 Encoding:** Handles multi-byte characters, international symbols, non-ASCII text, and arbitrary password strings without truncation.
- **Canonical Empty Digest Support:** Accurately outputs canonical empty string digests (e.g., MD5 `d41d8cd98f00b204e9800998ecf8427e`).
- **Clipboard Integration:** Copy individual hashes with a single click or export all generated digests in a formatted block.

### 4. File Hash Calculator & Integrity Verifier
- **Zero Server Uploads:** Complete client-side hashing executed locally in the browser via `crypto_engine.js`. File data never leaves the client workstation.
- **Non-Blocking Chunked Streaming:** Reads files in 2MB slices using FileReader and Web Cryptography APIs, preventing UI freezes and browser memory exhaustion on large files.
- **Algorithm Selection:** Compute individual digests (MD5, SHA-1, SHA-256, SHA-384, SHA-512) or calculate all algorithms in a unified pass.
- **Reference Hash Normalization:** Automatically trims leading/trailing whitespace and normalizes case differences between reference and computed digests.
- **Defensive Pre-Validation:** Warns the user if the reference hash length does not match the chosen algorithm's expected output, preventing false mismatch diagnoses.
- **Integrity Badging:** Renders clear visual MATCH (green) and MISMATCH (red) status badges with matching byte length confirmations.

### 5. Duplicate Hash Detection
- **Frequency Clustering:** Groups identical hash strings across large sets into consolidated records with total occurrence metrics.
- **Source Line Mapping:** Lists all line numbers where each duplicate was discovered in the source input.
- **Configurable Normalization:** Supports case-insensitive matching (standard for hexadecimal digests) and case-sensitive matching (for Base64 and salt strings).
- **Audit Filtering:** Switch views between All Entries, Duplicates Only, and Unique Only.
- **Sanitized Export:** Download deduplicated lists or duplicate-only audit records as CSV or JSON.

### 6. Hash List Diff Analyzer
- **Comparative Set Differential:** Performs set-difference analysis between Baseline (List A) and Target (List B).
- **Four-Way Classification:** Categorizes hashes into:
  - Common Hashes (present in both List A and List B)
  - Added in B (present in target List B, missing from baseline List A)
  - Removed from A (present in baseline List A, missing from target List B)
  - Internal In-List Duplicates (repeated hashes within either list)
- **Deployment Auditing:** Rapidly detect unauthorized file modifications or artifact discrepancies between software releases.
- **Export Capabilities:** Save comprehensive diff reports to CSV or JSON.

### 7. Hash Manifest Generator & Verifier
- **Manifest Generation:** Calculate SHA-256 integrity digests across multiple files or entire directory trees (`webkitdirectory`).
- **Standardized Schema:** Outputs manifest records containing file path, byte size, and SHA-256 checksum in JSON or CSV format.
- **Automated Directory Verification:** Verifies directory state against a previously exported manifest and classifies each entry into:
  - Unchanged: File signature matches reference manifest exactly.
  - Modified: File exists, but calculated checksum differs.
  - Missing: File specified in manifest was not found in the target directory.
  - Newly Added: File present in local directory but not cataloged in manifest.
- **Audit Export:** Download complete verification audit reports for compliance documentation.

### 8. Backend Reference Database API
- **Zero-Configuration SQLite Storage:** Embedded database (`hash_lookup.db`) initialized automatically on startup.
- **Pre-Seeded Cryptographic Vectors:** Contains standard RFC test vectors (RFC 1321 MD5 empty string, SHA family baselines), EICAR antivirus test signatures, and common baseline hashes.
- **REST Endpoints:** Search (`GET /api/db/search?hash=...`), create records (`POST /api/db/records`), export (`GET /api/db/export`), and import (`POST /api/db/import`) without cluttering the main UI.
- **Provenance & Metadata:** Records store algorithm name, source origin, classification tags, and contextual security notes.
- **Database Management:** Search exact hash signatures, insert new verified records, delete obsolete entries, and bulk import/export via CSV or JSON.

### 9. Hash Performance Benchmark
- **High-Resolution Micro-Benchmarking:** Measures precise execution time using `performance.now()` in browser runtimes and `time.perf_counter()` in Python.
- **Dual-Engine Execution:** Compare Client Browser performance (JavaScript Web Cryptography API) against Backend Server execution (Python hashlib / native C).
- **Configurable Workloads:** Run benchmarks across 64 KB, 1 MB, 8 MB, or 16 MB payload sizes with 3, 5, or 10 iterations.
- **Throughput Metrics:** Eliminates cold-start anomalies via warm-up runs, reporting average latency (ms) and effective throughput in **MB/s**.
- **Interactive Visualization:** Renders relative performance comparison bar charts with CSV and JSON data export.

### 10. Professional Cyber GUI with Google Material Symbols
- **Cybersecurity Design Language:** Modern interface featuring dark and light theme palettes built with CSS design tokens.
- **Google Material Symbols:** Crisp vector-rendered iconography integrated across navigation tabs, buttons, status indicators, and result cards.
- **Responsive Navigation:** Smooth tabbed layout allowing instant transitions between all 9 operational panels without full-page reloads.
- **Accessibility & Feedback:** Interactive copy buttons, clear validation banners, micro-interactions, and toast alerts.

---

## Supported Cryptographic and Structural Formats

| Category | Algorithms / Formats | Structural Signature / Bit-Length |
|---|---|---|
| **Cryptographic Hex Digests** | MD5, MD4, NTLM | 32 hex characters (128-bit) |
| | SHA-1, RIPEMD-160 | 40 hex characters (160-bit) |
| | SHA-224, SHA3-224 | 56 hex characters (224-bit) |
| | SHA-256, SHA3-256 | 64 hex characters (256-bit) |
| | SHA-384, SHA3-384 | 96 hex characters (384-bit) |
| | SHA-512, SHA3-512 | 128 hex characters (512-bit) |
| **Password KDFs & Salted Hashes** | bcrypt | `$2a$`, `$2b$`, `$2y$`, `$2x$` + cost + 53 base64 characters |
| | Argon2 (`argon2id`, `argon2i`, `argon2d`) | `$argon2id$`, `$argon2i$`, `$argon2d$` + version, memory, time, lanes |
| | scrypt | `$scrypt$` / `scrypt$` + parameters + salt + digest |
| | Unix crypt (SHA-256) | `$5$` + salt + 43 characters |
| | Unix crypt (SHA-512) | `$6$` + salt + 86 characters |
| **System & Directory Hashes** | Cisco Type 5 (MD5 crypt) | `$1$` + salt + 22 characters |
| | MySQL 4.1+ | `*` + 40 hex characters (`PASSWORD()`) |
| | MySQL 3.23 | 16 hex characters (legacy authentication) |
| | LDAP SSHA & SHA | `{SSHA}` (salted), `{SHA}` (Base64 encoded) |
| **Tokens & Checksums** | JSON Web Token (JWT) | RFC 7519 `header.payload.signature` (Base64URL) |
| | CRC-32 & Adler-32 | 8 hex characters (32-bit non-cryptographic checksum) |

> **Format Ambiguity Notice:** Cryptographic digests do not encode algorithm metadata within their raw hexadecimal representation. Multiple algorithms produce identical output lengths (for example, MD5, MD4, and NTLM all produce 32 hexadecimal characters). This toolkit tags length-based matches with heuristic confidence ratings and explicit ambiguity warnings rather than claiming false certainty.

---

## Project Architecture

```
Hash-Identifier/
├── app.py                      # Flask application and REST API endpoints
├── requirements.txt            # Python dependencies (Flask, pytest)
├── README.md                   # Complete toolkit documentation
├── hash_lookup.db              # SQLite reference database (auto-initialized)
├── core/                       # Modular backend engines
│   ├── __init__.py
│   ├── detector.py             # Structural analysis, charset & ambiguity engine
│   ├── hasher.py               # Text hashing, streaming chunked file hasher, integrity verifier
│   ├── batch.py                # Multiline and CSV batch scanner & duplicate detector
│   ├── diff.py                 # Hash list diff analyzer (List A vs List B)
│   ├── manifest.py             # SHA-256 manifest generator and verification engine
│   ├── database.py             # SQLite reference database with provenance tracking
│   └── benchmark.py            # High-resolution benchmark execution engine
├── static/
│   ├── css/
│   │   └── style.css           # Modern Dark/Light theme, responsive layout, cyber styling
│   └── js/
│       ├── script.js           # Theme toggle, tab router, and URL hash navigation
│       ├── crypto_engine.js    # Standalone pure JS streaming hasher (MD5, SHA-1/256/384/512)
│       ├── hash_tool.js        # Single hash identification UI & history
│       ├── batch_tool.js       # Batch scanner UI, filtering, and exports
│       ├── generator_tool.js   # Multi-algorithm plaintext hash generator
│       ├── file_hasher_tool.js # File hash calculator & integrity verifier
│       ├── duplicates_tool.js  # Duplicate hash detection UI
│       ├── diff_tool.js        # List diff analyzer UI
│       ├── manifest_tool.js    # Manifest generator and verifier UI
│       ├── database_tool.js    # Reference database search, add, import/export UI
│       └── benchmark_tool.js   # Real-time benchmark runner & chart visualization
├── templates/
│   ├── base.html               # Shared layout, navbar, subnav tabs, theme toggle, footer
│   ├── index.html              # Main integrated toolkit dashboard (9 tools)
│   └── author.html             # Author profile and project metadata
└── tests/                      # Automated test suite (47 tests)
    ├── __init__.py
    ├── test_detector.py        # Detection rules, entropy, charset, and ambiguity tests
    ├── test_hasher.py          # Hash generation, stream hashing, and integrity validation
    ├── test_batch_duplicates.py# Batch scanner, line numbers, CSV parsing, duplicates
    ├── test_diff.py            # Set difference, added, removed, common hashes
    ├── test_manifest.py        # Manifest generation, parsing, and strict verification
    ├── test_database.py        # SQLite catalog search, add, delete, import, export
    ├── test_benchmark.py       # Benchmark execution and throughput verification
    ├── test_api_endpoints.py   # Integration tests for all Flask API endpoints
    └── test_crypto_engine_js.py# Client-side crypto test vectors verification
```

---

## Installation and Setup

### Prerequisites

- **Python 3.8+** (compatible with Python 3.8 through 3.14+)
- **pip** package manager
- Modern standards-compliant web browser (Google Chrome, Mozilla Firefox, Apple Safari, Microsoft Edge)
- *(Optional)* Node.js for client-side JavaScript unit testing

### Step-by-Step Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kinza099/Hash-Identifier.git
   cd Hash-Identifier
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On Windows (PowerShell / Command Prompt):
   python -m venv venv
   venv\Scripts\activate

   # On Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   python app.py
   ```

5. **Access the web interface:**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## Usage Guide

### 1. Single Hash Identification
1. Navigate to the **Identifier** tab.
2. Enter or paste a hash string (e.g., `5f4dcc3b5aa765d61d8327deb882cf99` or `$2b$12$e8KERgfl6vQ...`).
3. Click **Identify** or press `Enter`.
4. Review bit length, character set, Shannon entropy (bits/char), and ranked candidate algorithms.
5. If the hash length is ambiguous, inspect the provided ambiguity notice detailing overlapping algorithms.
6. Access prior queries in the **Recent Lookups** history tray.

### 2. Batch Hash Scanning
1. Open the **Batch Scanner** tab.
2. Paste a list of hashes (one per line) or drag and drop a `.txt` or `.csv` file.
3. Click **Scan Hashes**.
4. Examine the results table displaying line numbers, detected algorithms, confidence scores, and duplicate flags.
5. Filter by validation status, confidence level, or substring query.
6. Click **Export CSV** or **Export JSON** to save the triage report.

### 3. Multi-Algorithm Hash Generation
1. Switch to the **Generator** tab.
2. Type or paste your plaintext input into the text area.
3. View the live character and UTF-8 byte counter.
4. Review the concurrently generated digests for MD5, SHA-1, SHA-256, SHA-384, and SHA-512.
5. Click **Copy** on any individual card or use **Copy All Hashes** for a unified summary.

### 4. File Hash Calculation and Integrity Verification
1. Open the **File Hasher** tab.
2. Drag and drop any file (e.g., binary, executable, ISO, archive, document) into the upload zone, or click to browse.
3. The file name and human-readable byte size (e.g., `firmware.bin (14.2 MB)`) are displayed immediately.
4. Select the target algorithm (`MD5`, `SHA-1`, `SHA-256`, `SHA-384`, `SHA-512`, or `All Algorithms`).
5. Click **Generate Hash**. The file is sliced into 2MB chunks and hashed in memory with a progress bar.
6. To verify integrity against a known reference, paste the expected digest into the **Reference Hash** box.
7. The verifier normalizes whitespace and letter casing, displays length pre-validation warnings if mismatched, and returns a verified MATCH or MISMATCH status.
8. Export results to `.txt` or `.csv`.

### 5. Duplicate Hash Detection
1. Open the **Duplicates** tab.
2. Paste a list of hashes or upload a file.
3. Choose whether to enable case-sensitive matching.
4. Click **Find Duplicates**.
5. Inspect grouped duplicates, total occurrence counts, and line mappings.
6. Filter the view to All, Duplicates Only, or Unique Only.
7. Export sanitized unique lists or duplicate audit reports.

### 6. Hash List Diff Analysis
1. Navigate to the **Diff Analyzer** tab.
2. Paste baseline hashes into **List A** and comparison hashes into **List B** (or load from files).
3. Click **Compare Lists**.
4. The analyzer compares List B against List A and displays:
   - Common Hashes (present in both lists)
   - Added in B (new hashes in List B)
   - Removed from A (hashes in List A but absent from List B)
   - In-List Duplicates (internal repetitions within either list)
5. Search the comparison tables and export results as CSV or JSON.

### 7. Hash Manifest Generation and Verification
1. Navigate to the **Manifest** tab.
2. **Generate Manifest:** Select multiple files or a whole directory folder (`webkitdirectory`). The tool computes SHA-256 checksums across all files and provides download links for `manifest_sha256.json` and `manifest_sha256.csv`.
3. **Verify Manifest:** Upload an existing manifest file and select the corresponding target directory.
4. The verification engine checks every file and flags:
   - Unchanged (intact digest)
   - Modified (content altered)
   - Missing (specified in manifest but not found)
   - Newly Added (found in folder but unlisted in manifest)
5. Export the verification report to CSV or JSON.

### 8. Backend Reference Database Operations (REST API)
1. Query known hash records via `GET /api/db/search?hash=<hash_string>`.
2. View exact-match results including algorithm, source provenance, tags, and notes.
3. Add new verified records by sending `POST /api/db/records` with JSON `{hash, algorithm, source, notes, tags}`.
4. Export the database catalog as CSV or JSON via `GET /api/db/export?format=json|csv`.
5. Import external datasets via `POST /api/db/import`.

### 9. Hash Performance Benchmarking
1. Open the **Benchmark** tab.
2. Select payload size (64 KB, 1 MB, 8 MB, 16 MB).
3. Select the number of test iterations (3, 5, 10).
4. Select the execution engine: **Client Browser** (JavaScript Web Cryptography API) or **Backend Server** (Python hashlib).
5. Click **Start Benchmark**.
6. Review min/max/average execution times and effective throughput in **MB/s**, along with an interactive comparison bar chart.
7. Export benchmark data to CSV or JSON.

---

## Security, Privacy, and Integrity Guarantees

1. **Client-Side Data Privacy:** File hashing operations run 100% locally inside the client browser using Web Cryptography APIs and chunked streaming. File contents are never transmitted across the network to any server.
2. **Zero Code Execution:** Uploaded files and analyzed strings are strictly processed as raw binary byte streams. Files are never executed, decompressed, or evaluated.
3. **Memory Exhaustion Protection:** Chunked streaming reads files in discrete 2MB slices, preventing memory overflow and browser tab crashes even on large multi-gigabyte files.
4. **Input Sanitization and XSS Prevention:** All user-supplied inputs, file names, and parsed attributes are sanitized and safely inserted into the DOM using strict text-node binding.
5. **Cryptographic Collision Warnings:** MD5 and SHA-1 outputs feature persistent security warnings informing users of known collision vulnerabilities and discouraging their use for digital signatures or security-critical validation.

---

## Testing and Quality Assurance

The project includes an automated test suite containing **47 test cases** covering every module, algorithm, edge case, and REST endpoint.

### Running Automated Tests

```bash
# Execute the full test suite with verbose output
pytest -v
```

### Test Suite Execution Output

```
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
collected 47 items

tests/test_api_endpoints.py::test_index_and_author_routes PASSED         [  2%]
tests/test_api_endpoints.py::test_api_identify_endpoint PASSED           [  4%]
tests/test_api_endpoints.py::test_api_batch_endpoint PASSED              [  6%]
tests/test_api_endpoints.py::test_api_generate_endpoint PASSED           [  8%]
tests/test_api_endpoints.py::test_api_hash_file_endpoint PASSED          [ 10%]
tests/test_api_endpoints.py::test_api_verify_integrity_endpoint PASSED   [ 12%]
tests/test_api_endpoints.py::test_api_duplicates_endpoint PASSED         [ 14%]
tests/test_api_endpoints.py::test_api_diff_endpoint PASSED               [ 17%]
tests/test_api_endpoints.py::test_api_manifest_generate_and_verify PASSED [ 19%]
tests/test_api_endpoints.py::test_api_db_routes PASSED                   [ 21%]
tests/test_api_endpoints.py::test_api_benchmark_endpoint PASSED          [ 23%]
tests/test_batch_duplicates.py::test_batch_line_numbers_and_empties PASSED [ 25%]
tests/test_batch_duplicates.py::test_batch_csv_parsing PASSED            [ 27%]
tests/test_batch_duplicates.py::test_find_duplicates_grouping PASSED     [ 29%]
tests/test_batch_duplicates.py::test_duplicate_case_normalization PASSED [ 31%]
tests/test_benchmark.py::test_benchmark_execution PASSED                 [ 34%]
tests/test_crypto_engine_js.py::test_crypto_engine_js_vectors PASSED     [ 36%]
tests/test_database.py::test_init_and_search_prepopulated PASSED         [ 38%]
tests/test_database.py::test_add_and_delete_record PASSED                [ 40%]
tests/test_database.py::test_export_import_json_and_csv PASSED           [ 42%]
tests/test_detector.py::test_empty_and_whitespace_input PASSED           [ 44%]
tests/test_detector.py::test_backward_compatibility_schema PASSED        [ 46%]
tests/test_detector.py::test_md5_ntlm_ambiguity PASSED                   [ 48%]
tests/test_detector.py::test_sha1_ripemd160_ambiguity PASSED             [ 51%]
tests/test_detector.py::test_sha256_sha3_256 PASSED                      [ 53%]
tests/test_detector.py::test_sha512_sha3_512 PASSED                      [ 55%]
tests/test_detector.py::test_bcrypt_prefix_high_confidence PASSED        [ 57%]
tests/test_detector.py::test_argon2_prefix_high_confidence PASSED        [ 59%]
tests/test_detector.py::test_cisco_type_5 PASSED                         [ 61%]
tests/test_detector.py::test_mysql41_prefix PASSED                       [ 63%]
tests/test_detector.py::test_charset_analysis PASSED                     [ 65%]
tests/test_detector.py::test_unsupported_or_malformed_string PASSED      [ 68%]
tests/test_diff.py::test_diff_basic_sets PASSED                          [ 70%]
tests/test_diff.py::test_diff_case_normalization PASSED                  [ 72%]
tests/test_hasher.py::test_empty_string_test_vectors PASSED              [ 74%]
tests/test_hasher.py::test_known_phrase_test_vectors PASSED              [ 76%]
tests/test_hasher.py::test_unicode_consistency PASSED                    [ 78%]
tests/test_hasher.py::test_legacy_security_warnings PASSED               [ 80%]
tests/test_hasher.py::test_chunked_stream_hashing PASSED                 [ 82%]
tests/test_hasher.py::test_empty_stream_hashing PASSED                   [ 85%]
tests/test_hasher.py::test_verify_integrity_match_and_normalization PASSED [ 87%]
tests/test_hasher.py::test_verify_integrity_mismatch PASSED              [ 89%]
tests/test_hasher.py::test_verify_integrity_length_mismatch_warning PASSED [ 91%]
tests/test_hasher.py::test_verify_integrity_invalid_hex_format PASSED    [ 93%]
tests/test_manifest.py::test_generate_and_parse_manifest PASSED          [ 95%]
tests/test_manifest.py::test_verify_manifest_all_cases PASSED            [ 97%]
tests/test_manifest.py::test_verify_manifest_fully_intact PASSED         [100%]

============================= 47 passed in 0.95s ==============================
```

---

## REST API Reference

The Flask backend provides a modular RESTful JSON API for automation scripts, CLI utilities, and CI/CD security pipelines.

| Endpoint | Method | Description | Request Payload / Parameters |
|---|---|---|---|
| `/api/identify` | `POST` | Identifies hash structure, calculates entropy, and ranks candidates | `{"hash": "5f4dcc3b5aa765d61d8327deb882cf99"}` |
| `/api/batch-identify` | `POST` | Scans multiple hashes from multiline text or CSV data | `{"text": "hash1\nhash2", "is_csv": false}` |
| `/api/generate` | `POST` | Generates MD5, SHA-1, SHA-256, SHA-384, SHA-512 from text | `{"text": "sample_input", "encoding": "utf-8"}` |
| `/api/hash-file` | `POST` | Calculates digests of uploaded file via multipart stream | `multipart/form-data` with `file` and optional `algorithm` |
| `/api/verify-integrity` | `POST` | Validates calculated digest against reference hash | `{"calculated_hash": "...", "reference_hash": "...", "algorithm": "sha256"}` |
| `/api/duplicates` | `POST` | Detects and groups duplicate hashes with line indexes | `{"text": "...", "case_sensitive": false}` |
| `/api/diff` | `POST` | Compares List A (baseline) against List B (target) | `{"list_a": "...", "list_b": "...", "case_sensitive": false}` |
| `/api/manifest/generate`| `POST` | Generates standardized SHA-256 manifest JSON | `{"files": [{"path": "relative/file.txt", "size": 1024, "hash": "..."}]}` |
| `/api/manifest/verify`  | `POST` | Validates current file set against reference manifest | `{"manifest": {...}, "current_files": [...]}` |
| `/api/db/search` | `GET` | Searches exact hash match in local SQLite catalog | Query string: `?hash=5f4dcc3b5aa765d61d8327deb882cf99` |
| `/api/db/records` | `GET` | Retrieves all cataloged reference database records | None |
| `/api/db/records` | `POST` | Inserts a new reference hash record | `{"hash": "...", "algorithm": "...", "source": "...", "tag": "...", "notes": "..."}` |
| `/api/db/records/<id>` | `DELETE` | Deletes a reference record by numeric identifier | URL path parameter: `<id>` |
| `/api/db/export` | `GET` | Exports database records as JSON or CSV | Query string: `?format=json` or `?format=csv` |
| `/api/db/import` | `POST` | Imports records from JSON or CSV string/upload | `{"data": "..."}` or file upload |
| `/api/benchmark` | `POST` | Executes server-side hashing performance benchmark | `{"size_bytes": 1048576, "iterations": 5}` |

---

## Authors and Contributors

This project is developed and maintained by:

<table align="center" width="100%">
  <tr>
    <td align="center" width="50%" valign="top">
      <a href="https://github.com/kinza099">
        <img src="https://github.com/kinza099.png" width="120" height="120" alt="Kinza" style="border-radius: 50%;">
        <br />
        <sub><b>Kinza</b></sub>
      </a>
      <br />
      <sub>Project Creator & Core Developer</sub>
      <br /><br />
      <p align="center">
        <a href="https://github.com/kinza099">GitHub: @kinza099</a><br />
        <a href="mailto:kinzapython@gmail.com">Email: kinzapython@gmail.com</a>
      </p>
    </td>
    <td align="center" width="50%" valign="top">
      <a href="https://github.com/salmanmallah">
        <img src="https://github.com/salmanmallah.png" width="120" height="120" alt="Salman Mallah" style="border-radius: 50%;">
        <br />
        <sub><b>Salman Mallah</b></sub>
      </a>
      <br />
      <sub>Cyber Security Engineer & Malware Analyst</sub>
      <br /><br />
      <p align="center">
        <a href="https://github.com/salmanmallah">GitHub: @salmanmallah</a>
      </p>
    </td>
  </tr>
</table>

- **Kinza** ([@kinza099](https://github.com/kinza099))
  - Project architecture, cryptographic detection rules, Flask REST API endpoints, client-side streaming engine, and test suite implementation.
  - Contact: [kinzapython@gmail.com](mailto:kinzapython@gmail.com)

- **Salman Mallah** ([@salmanmallah](https://github.com/salmanmallah))
  - Cyber Security Engineer & Malware Analyst.
  - Threat vector analysis, reference hash catalogs, forensic manifest verification workflows, and security audit guidelines.
  - GitHub: [https://github.com/salmanmallah](https://github.com/salmanmallah)

---

## License

This project is licensed under the [MIT License](LICENSE).
