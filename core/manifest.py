"""Hash Manifest Generator and Verification Engine.

Generates and verifies cryptographic SHA-256 manifests:
- Standard manifest format (file path, file size, algorithm, SHA-256 digest)
- Verification categorization: Unchanged, Modified, Missing, Newly Added
- Strict accuracy: never marks verification successful if required files are unchecked
- Formats: JSON and CSV support
"""

import csv
import io
import json
import time
from typing import Any, Dict, List, Optional, Set, Tuple


def generate_manifest(files: List[Dict[str, Any]], creator: str = "Hash Identifier Toolkit") -> Dict[str, Any]:
    """Generate a structured manifest from a list of calculated file hash records.

    Expected file entry:
    - path: relative file path or filename
    - size: integer bytes
    - hash: SHA-256 hex string
    """
    entries = []
    total_size = 0

    for f in files:
        rel_path = f.get("path") or f.get("name") or "unknown"
        size = int(f.get("size", 0))
        h = f.get("hash", "").strip().lower()
        total_size += size

        entries.append({
            "path": rel_path.replace("\\", "/"),
            "name": f.get("name") or rel_path.split("/")[-1],
            "size": size,
            "algorithm": "SHA-256",
            "hash": h,
        })

    # Sort deterministically by path
    entries.sort(key=lambda x: x["path"])

    manifest = {
        "version": "1.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "creator": creator,
        "algorithm": "SHA-256",
        "total_files": len(entries),
        "total_bytes": total_size,
        "files": entries,
    }

    return manifest


def manifest_to_csv(manifest: Dict[str, Any]) -> str:
    """Serialize a manifest dictionary to CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["path", "name", "size_bytes", "algorithm", "sha256_hash"])
    for f in manifest.get("files", []):
        writer.writerow([
            f.get("path", ""),
            f.get("name", ""),
            f.get("size", 0),
            f.get("algorithm", "SHA-256"),
            f.get("hash", ""),
        ])
    return output.getvalue()


def parse_manifest(manifest_text: str) -> Dict[str, Any]:
    """Parse a manifest from JSON or CSV text."""
    stripped = manifest_text.strip()
    if not stripped:
        raise ValueError("Manifest content is empty.")

    # Try JSON first
    if stripped.startswith("{"):
        try:
            data = json.loads(stripped)
            if "files" in data and isinstance(data["files"], list):
                return data
        except Exception:
            pass

    # Try CSV parsing
    reader = csv.reader(io.StringIO(stripped))
    rows = list(reader)
    if not rows:
        raise ValueError("Could not parse manifest data as JSON or CSV.")

    header = [c.strip().lower() for c in rows[0]]
    path_idx = 0
    size_idx = -1
    hash_idx = -1

    for i, col in enumerate(header):
        if "path" in col or "file" in col or "name" in col:
            path_idx = i
        elif "size" in col:
            size_idx = i
        elif "hash" in col or "sha" in col or "digest" in col:
            hash_idx = i

    if hash_idx == -1 and len(rows[0]) >= 2:
        hash_idx = len(rows[0]) - 1

    files = []
    for r in rows[1:]:
        if not r or len(r) <= max(path_idx, hash_idx):
            continue
        p = r[path_idx].strip().replace("\\", "/")
        h = r[hash_idx].strip().lower()
        sz = 0
        if size_idx != -1 and size_idx < len(r):
            try:
                sz = int(r[size_idx].strip())
            except ValueError:
                sz = 0
        files.append({
            "path": p,
            "name": p.split("/")[-1],
            "size": sz,
            "algorithm": "SHA-256",
            "hash": h,
        })

    return {
        "version": "1.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "algorithm": "SHA-256",
        "total_files": len(files),
        "files": files,
    }


def verify_manifest(
    manifest_data: Dict[str, Any],
    current_files: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Verify current files against a reference manifest.

    Reports:
    - Unchanged: File present in manifest, hash matches exactly.
    - Modified: File present in manifest, but calculated hash differs.
    - Missing: File listed in manifest, but was NOT provided in verification set.
    - Newly Added: File provided in verification set, but was not present in the manifest.
    """
    manifest_files = manifest_data.get("files", [])
    manifest_map: Dict[str, Dict[str, Any]] = {}
    for mf in manifest_files:
        norm_path = (mf.get("path") or mf.get("name") or "").strip().replace("\\", "/").lower()
        manifest_map[norm_path] = mf

    current_map: Dict[str, Dict[str, Any]] = {}
    for cf in current_files:
        norm_path = (cf.get("path") or cf.get("name") or "").strip().replace("\\", "/").lower()
        current_map[norm_path] = cf

    unchanged: List[Dict[str, Any]] = []
    modified: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    added: List[Dict[str, Any]] = []

    for path, mf in manifest_map.items():
        if path not in current_map:
            missing.append({
                "path": mf.get("path", path),
                "expected_hash": mf.get("hash", ""),
                "size": mf.get("size", 0),
                "status": "MISSING",
                "message": "File was specified in manifest but was not provided for verification.",
            })
        else:
            cf = current_map[path]
            exp_hash = mf.get("hash", "").strip().lower()
            act_hash = cf.get("hash", "").strip().lower()

            if exp_hash == act_hash:
                unchanged.append({
                    "path": mf.get("path", path),
                    "hash": act_hash,
                    "size": cf.get("size", mf.get("size", 0)),
                    "status": "UNCHANGED",
                    "message": "Cryptographic digest matches reference manifest.",
                })
            else:
                modified.append({
                    "path": mf.get("path", path),
                    "expected_hash": exp_hash,
                    "actual_hash": act_hash,
                    "size": cf.get("size", mf.get("size", 0)),
                    "status": "MODIFIED",
                    "message": "Hash mismatch: file contents have been modified or replaced.",
                })

    for path, cf in current_map.items():
        if path not in manifest_map:
            added.append({
                "path": cf.get("path", path),
                "actual_hash": cf.get("hash", ""),
                "size": cf.get("size", 0),
                "status": "NEWLY_ADDED",
                "message": "File is present in target set but was not listed in reference manifest.",
            })

    total_manifest = len(manifest_map)
    total_checked = len(current_map)
    is_fully_intact = (len(modified) == 0 and len(missing) == 0 and len(added) == 0 and total_manifest > 0)

    return {
        "status": "SUCCESS" if is_fully_intact else "DISCREPANCY_DETECTED",
        "fully_intact": is_fully_intact,
        "summary": {
            "total_manifest_entries": total_manifest,
            "total_files_provided": total_checked,
            "unchanged_count": len(unchanged),
            "modified_count": len(modified),
            "missing_count": len(missing),
            "newly_added_count": len(added),
        },
        "unchanged": unchanged,
        "modified": modified,
        "missing": missing,
        "newly_added": added,
        "verification_statement": (
            "Verification Complete: All files strictly match the reference manifest with zero modifications or missing files."
            if is_fully_intact
            else f"Verification Discrepancies: {len(modified)} modified, {len(missing)} missing, {len(added)} new file(s) detected."
        ),
    }
