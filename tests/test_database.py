"""Tests for Local Reference Database Module."""

import gc
import os
import shutil
import tempfile
import pytest
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


@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_lookup.db")
    init_db(db_path)
    yield db_path
    gc.collect()
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_init_and_search_prepopulated(temp_db):
    # Empty string MD5 should be pre-seeded in database
    res = search_hash("d41d8cd98f00b204e9800998ecf8427e", db_path=temp_db)
    assert res["found"] is True
    assert res["match_count"] >= 1
    rec = res["records"][0]
    assert rec["algorithm"] == "MD5"
    assert "RFC 1321" in rec["source"]
    assert "Provenance Notice" in res["disclaimer"]


def test_add_and_delete_record(temp_db):
    test_hash = "11112222333344445555666677778888"
    new_rec = add_record(
        hash_val=test_hash,
        algorithm="MD5",
        source="Custom Security Audit 2026",
        notes="Audit baseline file hash",
        tag="Baseline",
        db_path=temp_db,
    )
    assert new_rec["id"] is not None

    search_res = search_hash(test_hash, db_path=temp_db)
    assert search_res["found"] is True
    assert search_res["records"][0]["source"] == "Custom Security Audit 2026"

    # Delete record
    del_ok = delete_record(new_rec["id"], db_path=temp_db)
    assert del_ok is True

    # Search again
    search_after = search_hash(test_hash, db_path=temp_db)
    assert search_after["found"] is False


def test_export_import_json_and_csv(temp_db):
    # Export JSON
    json_str = export_records_json(db_path=temp_db)
    assert "d41d8cd98f00b204e9800998ecf8427e" in json_str

    # Export CSV
    csv_str = export_records_csv(db_path=temp_db)
    assert "d41d8cd98f00b204e9800998ecf8427e" in csv_str

    # Import new record from CSV
    csv_import_data = "hash,algorithm,source,notes,tag\n99998888777766665555444433332222,SHA-256,ImportTest,TestNotes,ImportedTag"
    imp_res = import_records(csv_import_data, db_path=temp_db)
    assert imp_res["imported"] >= 1

    search_imported = search_hash("99998888777766665555444433332222", db_path=temp_db)
    assert search_imported["found"] is True
    assert search_imported["records"][0]["tag"] == "ImportedTag"
