"""Unit and integration tests for dual-author structure, pages, and API endpoints."""

import pytest
import app


@pytest.fixture
def client():
    """Create a configured Flask test client."""
    app.app.config["TESTING"] = True
    with app.app.test_client() as client:
        yield client


def test_author_endpoint_status_and_dual_authors(client):
    """Verify /author endpoint returns HTTP 200 and both authors with avatars."""
    res = client.get("/author")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    # Verify both authors are present
    assert "Kinza" in html
    assert "Salman Mallah" in html

    # Verify both author cards exist
    assert 'id="author-card-kinza"' in html
    assert 'id="author-card-salman-mallah"' in html

    # Verify avatar rendering for both authors (images and fallback initials)
    assert "https://github.com/kinza099.png" in html
    assert "https://github.com/salmanmallah.png" in html
    assert "avatar-img" in html
    assert ">K<" in html
    assert ">S<" in html

    # Verify professional roles and bios
    assert "Creator &amp; Lead Security Developer" in html or "Security" in html
    assert "Malware Analyst" in html
    assert "Final-year B.S. Cyber Security student at MUET" in html

    # Verify GitHub profile links
    assert "https://github.com/kinza099" in html
    assert "https://github.com/salmanmallah" in html


def test_authors_plural_alias_endpoint(client):
    """Verify /authors route alias functions equivalently to /author."""
    res = client.get("/authors")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Kinza" in html
    assert "Salman Mallah" in html
    assert "https://github.com/kinza099.png" in html
    assert "https://github.com/salmanmallah.png" in html


def test_api_authors_json_endpoint(client):
    """Verify /api/authors returns expected JSON metadata for both authors."""
    res = client.get("/api/authors")
    assert res.status_code == 200
    assert res.is_json
    data = res.get_json()

    assert data["count"] == 2
    assert "project" in data
    authors = data["authors"]
    assert len(authors) == 2

    # Verify Kinza metadata
    kinza = authors[0]
    assert kinza["name"] == "Kinza"
    assert kinza["github_username"] == "kinza099"
    assert kinza["avatar_url"] == "https://github.com/kinza099.png"

    # Verify Salman Mallah metadata
    salman = authors[1]
    assert salman["name"] == "Salman Mallah"
    assert salman["github_username"] == "salmanmallah"
    assert salman["avatar_url"] == "https://github.com/salmanmallah.png"


def test_api_author_single_alias_json_endpoint(client):
    """Verify /api/author singular endpoint returns identical metadata."""
    res = client.get("/api/author")
    assert res.status_code == 200
    assert res.is_json
    data = res.get_json()
    assert data["count"] == 2
    assert data["authors"][0]["name"] == "Kinza"
    assert data["authors"][1]["name"] == "Salman Mallah"


def test_author_data_structure():
    """Verify app.AUTHORS data structure and backward compatibility aliases."""
    assert isinstance(app.AUTHORS, list)
    assert len(app.AUTHORS) == 2

    names = [a["name"] for a in app.AUTHORS]
    assert "Kinza" in names
    assert "Salman Mallah" in names

    for author in app.AUTHORS:
        assert "name" in author
        assert "github_username" in author
        assert "github_url" in author
        assert "avatar_url" in author
        assert "role" in author

    # Test backward compatibility AUTHOR_INFO
    assert hasattr(app, "AUTHOR_INFO")
    assert "name" in app.AUTHOR_INFO


def test_author_cards_in_grid(client):
    """Ensure exactly 2 author cards render inside the authors-grid."""
    res = client.get("/author")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert 'class="authors-grid"' in html
    grid_section = html.split('class="authors-grid"')[1]
    assert 'id="author-card-kinza"' in grid_section
    assert 'id="author-card-salman-mallah"' in grid_section
    card_count = html.count('class="author-card"')
    assert card_count == 2


def test_base_template_footer_includes_both_authors(client):
    """Verify root index page renders both authors in the footer."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "Kinza" in html
    assert "Salman Mallah" in html
