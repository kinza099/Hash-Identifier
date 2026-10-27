"""Local Hash Reference Database Module.

Provides local storage and exact-match searching for reference hashes using SQLite:
- Stores hash, algorithm, source/provenance, notes, tag, created_at
- Exact normalized match search
- Add, update, delete operations
- High-performance bulk import via single-transaction executemany()
- Streaming export to CSV and JSON
- Pre-populated with baseline test & reference vectors
"""

import csv
import io
import json
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hash_lookup.db")

SAMPLE_RECORDS = [
    {
        "hash": "d41d8cd98f00b204e9800998ecf8427e",
        "algorithm": "MD5",
        "source": "RFC 1321 Standard Test Vector",
        "notes": "Canonical MD5 digest of an empty string (0 bytes).",
        "tag": "Known Baseline",
    },
    {
        "hash": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
        "algorithm": "SHA-1",
        "source": "FIPS PUB 180-1 Standard Vector",
        "notes": "Canonical SHA-1 digest of an empty string (0 bytes).",
        "tag": "Known Baseline",
    },
    {
        "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "algorithm": "SHA-256",
        "source": "NIST FIPS 180-4 Standard Vector",
        "notes": "Canonical SHA-256 digest of an empty string (0 bytes).",
        "tag": "Known Baseline",
    },
    {
        "hash": "44d88612fea8a8f36de82e1278abb02f",
        "algorithm": "MD5",
        "source": "EICAR Standard Test File",
        "notes": "Standard EICAR Anti-Virus Test File (68 bytes). Used to test AV scanner response safely.",
        "tag": "Test Vector",
    },
    {
        "hash": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
        "algorithm": "SHA-256",
        "source": "EICAR Standard Test File",
        "notes": "Standard EICAR Anti-Virus Test File SHA-256 digest.",
        "tag": "Test Vector",
    },
    {
        "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
        "algorithm": "MD5",
        "source": "Security Dictionary Reference",
        "notes": "MD5 digest of the common dictionary password 'password'.",
        "tag": "Weak Password",
    },
]

_INITIALIZED_DBS: set = set()


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and configure a SQLite connection with WAL mode and normalized row access."""
    target_path = os.path.abspath(db_path or DB_FILE)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables, indexes, and seed sample records once per database path."""
    target_path = os.path.abspath(db_path or DB_FILE)
    if target_path in _INITIALIZED_DBS:
        return

    conn = get_db_connection(target_path)
    try:
        with conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reference_hashes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT NOT NULL,
                    normalized_hash TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    source TEXT NOT NULL,
                    notes TEXT,
                    tag TEXT,
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_normalized_hash ON reference_hashes(normalized_hash);
            """)

            # Check if empty, seed sample records
            cur = conn.execute("SELECT COUNT(*) as cnt FROM reference_hashes;")
            count = cur.fetchone()["cnt"]
            if count == 0:
                now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                for rec in SAMPLE_RECORDS:
                    norm = rec["hash"].strip().lower()
                    conn.execute("""
                        INSERT INTO reference_hashes (hash, normalized_hash, algorithm, source, notes, tag, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (rec["hash"], norm, rec["algorithm"], rec["source"], rec["notes"], rec["tag"], now))

        _INITIALIZED_DBS.add(target_path)
    finally:
        conn.close()


def search_hash(hash_val: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Search for exact matches of a hash string in the local database."""
    init_db(db_path)
    norm = hash_val.strip().lower()
    if not norm:
        return {
            "query": hash_val,
            "found": False,
            "match_count": 0,
            "records": [],
            "disclaimer": "No search query provided.",
        }

    conn = get_db_connection(db_path)
    try:
        cur = conn.execute(
            "SELECT id, hash, algorithm, source, notes, tag, created_at FROM reference_hashes WHERE normalized_hash = ? ORDER BY id DESC;",
            (norm,),
        )
        rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    return {
        "query": hash_val,
        "normalized_query": norm,
        "found": len(rows) > 0,
        "match_count": len(rows),
        "records": rows,
        "disclaimer": (
            "Provenance Notice: Database records reflect local reference knowledge. "
            "A database match is only as reliable as its source and provenance. "
            "Absence from the local database simply means the hash was not previously cataloged locally; "
            "it does NOT imply the file or string is safe, benign, or unknown globally."
        ),
    }


def add_record(
    hash_val: str,
    algorithm: str,
    source: str,
    notes: str = "",
    tag: str = "General",
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new reference record to the local database."""
    init_db(db_path)
    clean_hash = hash_val.strip()
    norm = clean_hash.lower()
    clean_alg = algorithm.strip() or "Unknown"
    clean_source = source.strip() or "Local Entry"
    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    conn = get_db_connection(db_path)
    try:
        with conn:
            cur = conn.execute(
                """
                INSERT INTO reference_hashes (hash, normalized_hash, algorithm, source, notes, tag, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (clean_hash, norm, clean_alg, clean_source, notes, tag, created_at),
            )
            rec_id = cur.lastrowid
    finally:
        conn.close()

    return {
        "id": rec_id,
        "hash": clean_hash,
        "normalized_hash": norm,
        "algorithm": clean_alg,
        "source": clean_source,
        "notes": notes,
        "tag": tag,
        "created_at": created_at,
    }


def delete_record(record_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a reference record by ID."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            cur = conn.execute("DELETE FROM reference_hashes WHERE id = ?;", (record_id,))
            return cur.rowcount > 0
    finally:
        conn.close()


def list_records(limit: int = 100, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """List most recent reference records."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cur = conn.execute(
            "SELECT id, hash, algorithm, source, notes, tag, created_at FROM reference_hashes ORDER BY id DESC LIMIT ?;",
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def export_records_json(limit: Optional[int] = None, db_path: Optional[str] = None) -> str:
    """Export all reference records as a JSON string using streaming cursor."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        query = "SELECT id, hash, algorithm, source, notes, tag, created_at FROM reference_hashes ORDER BY id DESC"
        params: Tuple[Any, ...] = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        cur = conn.execute(query, params)
        records = [dict(r) for r in cur]
        return json.dumps(records, indent=2)
    finally:
        conn.close()


def export_records_csv(limit: Optional[int] = None, db_path: Optional[str] = None) -> str:
    """Export all reference records as CSV using incremental row writing."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        query = "SELECT id, hash, algorithm, source, notes, tag, created_at FROM reference_hashes ORDER BY id DESC"
        params: Tuple[Any, ...] = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        cur = conn.execute(query, params)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "hash", "algorithm", "source", "notes", "tag", "created_at"])
        for r in cur:
            writer.writerow([r["id"], r["hash"], r["algorithm"], r["source"], r["notes"], r["tag"], r["created_at"]])
        return output.getvalue()
    finally:
        conn.close()


def import_records(data_text: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Import reference records from JSON or CSV text in a single bulk transaction."""
    init_db(db_path)
    stripped = data_text.strip()
    if not stripped:
        return {"imported": 0, "errors": ["Input was empty."]}

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    records_to_insert: List[Tuple[str, str, str, str, str, str, str]] = []
    errors: List[str] = []

    # Try JSON format
    if stripped.startswith("["):
        try:
            records = json.loads(stripped)
            for r in records:
                if not isinstance(r, dict):
                    continue
                h_val = str(r.get("hash", "")).strip()
                if not h_val:
                    continue
                alg = str(r.get("algorithm", "Unknown")).strip() or "Unknown"
                src = str(r.get("source", "Imported JSON")).strip() or "Imported JSON"
                notes = str(r.get("notes", "")).strip()
                tag = str(r.get("tag", "Imported")).strip() or "Imported"
                norm = h_val.lower()
                records_to_insert.append((h_val, norm, alg, src, notes, tag, now))
        except Exception as ex:
            errors.append(f"JSON Parse Error: {ex}")

    # If not JSON or JSON parsing produced no records, try CSV format
    if not records_to_insert:
        try:
            reader = csv.reader(io.StringIO(stripped))
            try:
                first_row = next(reader)
            except StopIteration:
                return {"imported": 0, "errors": ["No rows found in CSV."]}

            header = [c.strip().lower() for c in first_row]
            h_idx = 0
            alg_idx = 1 if len(first_row) > 1 else -1
            src_idx = 2 if len(first_row) > 2 else -1
            notes_idx = 3 if len(first_row) > 3 else -1
            tag_idx = 4 if len(first_row) > 4 else -1

            is_header = False
            for i, col in enumerate(header):
                if "hash" in col:
                    h_idx = i
                    is_header = True
                elif "algorithm" in col or "type" in col:
                    alg_idx = i
                elif "source" in col or "provenance" in col:
                    src_idx = i
                elif "note" in col or "desc" in col:
                    notes_idx = i
                elif "tag" in col:
                    tag_idx = i

            if not is_header and any(c in header[0] for c in ["hash", "id", "digest"]):
                is_header = True

            def parse_csv_record(r: List[str]) -> Optional[Tuple[str, str, str, str, str, str, str]]:
                if not r or len(r) <= h_idx:
                    return None
                h_val = r[h_idx].strip()
                if not h_val:
                    return None
                alg = r[alg_idx].strip() if alg_idx != -1 and alg_idx < len(r) else "Unknown"
                src = r[src_idx].strip() if src_idx != -1 and src_idx < len(r) else "Imported CSV"
                notes = r[notes_idx].strip() if notes_idx != -1 and notes_idx < len(r) else ""
                tag = r[tag_idx].strip() if tag_idx != -1 and tag_idx < len(r) else "Imported"
                norm = h_val.lower()
                return (h_val, norm, alg, src, notes, tag, now)

            if not is_header:
                rec = parse_csv_record(first_row)
                if rec:
                    records_to_insert.append(rec)

            for r in reader:
                rec = parse_csv_record(r)
                if rec:
                    records_to_insert.append(rec)
        except Exception as ex:
            errors.append(f"CSV Parse Error: {ex}")

    if not records_to_insert:
        return {"imported": 0, "errors": errors or ["No valid records found in input."]}

    # Execute single batch transaction with executemany
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.executemany("""
                INSERT INTO reference_hashes (hash, normalized_hash, algorithm, source, notes, tag, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, records_to_insert)
        return {"imported": len(records_to_insert), "errors": errors}
    except Exception as ex:
        return {"imported": 0, "errors": [str(ex)]}
    finally:
        conn.close()
