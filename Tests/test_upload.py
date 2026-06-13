"""Image upload validation tests."""
import io
import pytest


TINY_JPEG = bytes([
    0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
    0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9,
])


def test_upload_valid_jpeg(client, auth_headers):
    res = client.post(
        "/api/upload",
        headers={k: v for k, v in auth_headers.items()},
        files={"file": ("photo.jpg", io.BytesIO(TINY_JPEG), "image/jpeg")},
    )
    assert res.status_code == 200
    data = res.json()
    assert "filename" in data
    assert data["content_type"] == "image/jpeg"
    assert data["size"] == len(TINY_JPEG)


def test_upload_valid_png(client, auth_headers):
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
    res = client.post(
        "/api/upload",
        headers={k: v for k, v in auth_headers.items()},
        files={"file": ("image.png", io.BytesIO(png_bytes), "image/png")},
    )
    assert res.status_code == 200


def test_upload_invalid_type(client, auth_headers):
    res = client.post(
        "/api/upload",
        headers={k: v for k, v in auth_headers.items()},
        files={"file": ("doc.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert res.status_code == 400
    assert "Invalid file type" in res.json()["detail"]


def test_upload_pdf_rejected(client, auth_headers):
    res = client.post(
        "/api/upload",
        headers={k: v for k, v in auth_headers.items()},
        files={"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
    )
    assert res.status_code == 400


def test_upload_too_large(client, auth_headers):
    big = b"X" * (6 * 1024 * 1024)  # 6 MB > 5 MB limit
    res = client.post(
        "/api/upload",
        headers={k: v for k, v in auth_headers.items()},
        files={"file": ("big.jpg", io.BytesIO(big), "image/jpeg")},
    )
    assert res.status_code == 413


def test_upload_without_auth(client):
    res = client.post(
        "/api/upload",
        files={"file": ("photo.jpg", io.BytesIO(TINY_JPEG), "image/jpeg")},
    )
    assert res.status_code == 401
