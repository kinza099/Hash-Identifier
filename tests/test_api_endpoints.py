"""Integration tests for all Flask API endpoints."""

import io
import json
import pytest
import app


@pytest.fixture
def client():
    app.app.config["TESTING"] = True
    with app.app.test_client() as client:
        yield client


def test_index_and_author_routes(client):
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert b"Hash Identifier" in res_index.data
    assert b"File Hash Calculator" in res_index.data

    res_author = client.get("/author")
    assert res_author.status_code == 200
    assert b"Kinza" in res_author.data
    assert b"Salman Mallah" in res_author.data

    res_authors = client.get("/authors")
    assert res_authors.status_code == 200
    assert b"Kinza" in res_authors.data
    assert b"Salman Mallah" in res_authors.data

    res_api_authors = client.get("/api/authors")
    assert res_api_authors.status_code == 200
    api_data = res_api_authors.get_json()
    assert api_data["count"] == 2
    author_names = [a["name"] for a in api_data["authors"]]
    assert "Kinza" in author_names
    assert "Salman Mallah" in author_names


def test_api_identify_endpoint(client):
    payload = {"hash": "5f4dcc3b5aa765d61d8327deb882cf99"}
    res = client.post("/api/identify", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert data["length"] == 32
    assert "MD5" in data["matches"][0]["types"]
    assert "score" in data["matches"][0]


def test_api_batch_endpoint(client):
    text = "5f4dcc3b5aa765d61d8327deb882cf99\n2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
    res = client.post("/api/batch-identify", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_entries"] == 2
    assert data["valid_count"] == 2


def test_api_generate_endpoint(client):
    res = client.post("/api/generate", json={"text": "hello world"})
    assert res.status_code == 200
    data = res.get_json()
    assert "md5" in data["hashes"]
    assert "sha256" in data["hashes"]
    assert data["hashes"]["sha256"]["hash"] == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_api_hash_file_endpoint(client):
    file_bytes = b"Sample File Content For Hashing 123456789"
    data = {
        "file": (io.BytesIO(file_bytes), "sample.txt"),
        "algorithm": "all",
    }
    res = client.post("/api/hash-file", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data["total_bytes"] == len(file_bytes)
    assert res_data["filename"] == "sample.txt"
    assert "sha256" in res_data["hashes"]


def test_api_verify_integrity_endpoint(client):
    calc = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    ref = "B94D27B9934D3E08A52E52D7DA7DABFAC484EFE37A5380EE9088F7ACE2EFCDE9"
    res = client.post("/api/verify-integrity", json={
        "calculated_hash": calc,
        "reference_hash": ref,
        "algorithm": "sha256"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["verified"] is True
    assert data["status"] == "MATCH"


def test_api_duplicates_endpoint(client):
    text = "hash1\nhash2\nhash1"
    res = client.post("/api/duplicates", json={"text": text})
    assert res.status_code == 200
    data = res.get_json()
    assert data["duplicate_groups_count"] == 1
    assert data["repeated_occurrences_count"] == 1


def test_api_diff_endpoint(client):
    res = client.post("/api/diff", json={"list_a": "h1\nh2", "list_b": "h2\nh3"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["summary"]["common_count"] == 1
    assert data["summary"]["added_count"] == 1
    assert data["summary"]["removed_count"] == 1


def test_api_manifest_generate_and_verify(client):
    files = [{"path": "file1.txt", "size": 100, "hash": "abcd"}]
    res_gen = client.post("/api/manifest/generate", json={"files": files})
    assert res_gen.status_code == 200
    manifest = res_gen.get_json()

    res_ver = client.post("/api/manifest/verify", json={
        "manifest": manifest,
        "current_files": files,
    })
    assert res_ver.status_code == 200
    data = res_ver.get_json()
    assert data["fully_intact"] is True


def test_api_db_routes(client):
    # Add
    add_res = client.post("/api/db/records", json={
        "hash": "testapihash1234567890123456789012",
        "algorithm": "SHA-256",
        "source": "API Test",
        "notes": "Testing notes",
        "tag": "Test",
    })
    assert add_res.status_code == 201
    rec = add_res.get_json()["record"]
    rec_id = rec["id"]

    # List records
    list_res = client.get("/api/db/records?limit=50")
    assert list_res.status_code == 200
    list_data = list_res.get_json()
    assert "records" in list_data
    assert list_data["count"] >= 1

    # Search
    search_res = client.get("/api/db/search?hash=testapihash1234567890123456789012")
    assert search_res.status_code == 200
    assert search_res.get_json()["found"] is True

    # Export JSON
    exp_json = client.get("/api/db/export?format=json")
    assert exp_json.status_code == 200
    assert exp_json.mimetype == "application/json"
    assert b"testapihash1234567890123456789012" in exp_json.data

    # Export CSV
    exp_csv = client.get("/api/db/export?format=csv")
    assert exp_csv.status_code == 200
    assert "text/csv" in exp_csv.mimetype

    # Import
    import_payload = {
        "data": json.dumps([
            {
                "hash": "importedapihash1234567890123456",
                "algorithm": "MD5",
                "source": "Test Import",
                "notes": "Imported via test",
                "tag": "Import",
            }
        ])
    }
    imp_res = client.post("/api/db/import", json=import_payload)
    assert imp_res.status_code == 200
    assert imp_res.get_json()["imported"] >= 1

    # Delete
    del_res = client.delete(f"/api/db/records/{rec_id}")
    assert del_res.status_code == 200


def test_api_benchmark_endpoint(client):
    res = client.post("/api/benchmark", json={"size_bytes": 65536, "iterations": 2})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "COMPLETED"
    assert len(data["results"]) == 5


def test_api_endpoints_error_and_edge_cases(client):
    # 1. /api/identify with empty/whitespace string
    res_id_empty = client.post("/api/identify", json={"hash": "   "})
    assert res_id_empty.status_code == 200
    assert res_id_empty.get_json()["valid"] is False

    # 2. /api/batch-identify with empty text
    res_batch_empty = client.post("/api/batch-identify", json={"text": ""})
    assert res_batch_empty.status_code == 200
    assert res_batch_empty.get_json()["total_entries"] == 0

    # 3. /api/generate with empty text
    res_gen_empty = client.post("/api/generate", json={"text": ""})
    assert res_gen_empty.status_code == 200
    assert res_gen_empty.get_json()["hashes"]["md5"]["hash"] == "d41d8cd98f00b204e9800998ecf8427e"

    # 4. /api/hash-file with no file uploaded
    res_file_err = client.post("/api/hash-file", data={})
    assert res_file_err.status_code == 400
    assert "error" in res_file_err.get_json()

    # 5. /api/verify-integrity mismatch
    res_ver_mismatch = client.post("/api/verify-integrity", json={
        "calculated_hash": "a" * 64,
        "reference_hash": "b" * 64,
        "algorithm": "sha256",
    })
    assert res_ver_mismatch.status_code == 200
    assert res_ver_mismatch.get_json()["verified"] is False
    assert res_ver_mismatch.get_json()["status"] == "MISMATCH"

    res_ver_len_mismatch = client.post("/api/verify-integrity", json={
        "calculated_hash": "a" * 64,
        "reference_hash": "b" * 10,
        "algorithm": "sha256",
    })
    assert res_ver_len_mismatch.status_code == 200
    assert res_ver_len_mismatch.get_json()["verified"] is False
    assert res_ver_len_mismatch.get_json()["status"] == "LENGTH_MISMATCH"

    # 6. /api/duplicates with no duplicates
    res_dup_none = client.post("/api/duplicates", json={"text": "hash1\nhash2\nhash3"})
    assert res_dup_none.status_code == 200
    assert res_dup_none.get_json()["duplicate_groups_count"] == 0

    # 7. /api/diff with identical lists
    res_diff_same = client.post("/api/diff", json={"list_a": "h1\nh2", "list_b": "h1\nh2"})
    assert res_diff_same.status_code == 200
    assert res_diff_same.get_json()["summary"]["common_count"] == 2
    assert res_diff_same.get_json()["summary"]["added_count"] == 0
    assert res_diff_same.get_json()["summary"]["removed_count"] == 0

    # 8. /api/db/search for nonexistent hash
    res_search_404 = client.get("/api/db/search?hash=nonexistenthash00000000000000000000")
    assert res_search_404.status_code == 200
    assert res_search_404.get_json()["found"] is False
