import io


PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 24
JPEG_MAGIC = b"\xff\xd8\xff" + b"\x00" * 64
TEXT_BYTES = b"this is not an image"


def test_upload_requires_auth(client):
    response = client.post(
        "/api/upload",
        files={"file": ("a.png", io.BytesIO(PNG_MAGIC), "image/png")},
    )
    assert response.status_code == 401


def test_upload_accepts_png(authed_client):
    response = authed_client.post(
        "/api/upload",
        files={"file": ("sample.png", io.BytesIO(PNG_MAGIC), "image/png")},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["content_type"] == "image/png"
    assert body["filename"].endswith(".png")


def test_upload_rejects_text_file(authed_client):
    response = authed_client.post(
        "/api/upload",
        files={"file": ("evil.png", io.BytesIO(TEXT_BYTES), "image/png")},
    )
    assert response.status_code in (400, 415)


def test_upload_rejects_unsupported_content_type(authed_client):
    response = authed_client.post(
        "/api/upload",
        files={"file": ("doc.txt", io.BytesIO(TEXT_BYTES), "text/plain")},
    )
    assert response.status_code == 415


def test_upload_enforces_size_limit(authed_client):
    payload = PNG_MAGIC + b"\x00" * (6 * 1024 * 1024)
    response = authed_client.post(
        "/api/upload",
        files={"file": ("big.png", io.BytesIO(payload), "image/png")},
    )
    assert response.status_code == 413
