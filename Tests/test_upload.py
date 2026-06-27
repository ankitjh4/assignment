"""Tests for image upload validation: file type, file size, and path safety."""

import io


TINY_JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08"
    b"\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e"
    b"\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1e"
    b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00"
    b"\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00"
    b"\x08\x01\x01\x00\x00?\x00\xfb\xd0\xff\xd9"
)


def test_upload_requires_auth(client):
    resp = client.post(
        "/api/upload",
        files={"file": ("photo.jpg", io.BytesIO(TINY_JPEG), "image/jpeg")},
    )
    assert resp.status_code == 401


def test_upload_valid_jpeg(auth_client):
    client, _ = auth_client
    resp = client.post(
        "/api/upload",
        files={"file": ("photo.jpg", io.BytesIO(TINY_JPEG), "image/jpeg")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Image uploaded successfully."
    assert data["original_name"] == "photo.jpg"
    assert data["content_type"] == "image/jpeg"
    assert data["size_bytes"] > 0
    # Stored filename must be different (UUID-based) — prevents path traversal
    assert data["filename"] != "photo.jpg"


def test_upload_valid_png(auth_client):
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20  # minimal PNG header
    client, _ = auth_client
    resp = client.post(
        "/api/upload",
        files={"file": ("image.png", io.BytesIO(png_bytes), "image/png")},
    )
    assert resp.status_code == 200


def test_upload_invalid_type_pdf(auth_client):
    client, _ = auth_client
    resp = client.post(
        "/api/upload",
        files={"file": ("document.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
    )
    assert resp.status_code == 415


def test_upload_invalid_type_text(auth_client):
    client, _ = auth_client
    resp = client.post(
        "/api/upload",
        files={"file": ("script.js", io.BytesIO(b"alert(1)"), "text/javascript")},
    )
    assert resp.status_code == 415


def test_upload_oversized_file(auth_client):
    client, _ = auth_client
    big_data = b"x" * (6 * 1024 * 1024)  # 6 MB > 5 MB limit
    resp = client.post(
        "/api/upload",
        files={"file": ("big.jpg", io.BytesIO(big_data), "image/jpeg")},
    )
    assert resp.status_code == 413


def test_upload_wrong_extension(auth_client):
    client, _ = auth_client
    resp = client.post(
        "/api/upload",
        files={"file": ("malicious.exe", io.BytesIO(b"MZ"), "image/jpeg")},
    )
    # Extension .exe is not in ALLOWED_IMAGE_EXTENSIONS
    assert resp.status_code == 415


def test_upload_path_traversal_filename(auth_client):
    """Uploaded file must be stored with a safe UUID name, not the attacker-controlled filename."""
    client, _ = auth_client
    resp = client.post(
        "/api/upload",
        files={"file": ("../../etc/passwd.jpg", io.BytesIO(TINY_JPEG), "image/jpeg")},
    )
    if resp.status_code == 200:
        # If accepted, stored name must NOT contain path separators
        stored = resp.json()["filename"]
        assert "/" not in stored
        assert "\\" not in stored
        assert ".." not in stored
