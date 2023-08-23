import os
import urllib
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)
UPLOAD_DIRECTORY = "uploaded_files"

Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)


def test_upload_file():
    with open("test_file.txt", "w") as f:
        f.write("test file")

    with open("test_file.txt", "rb") as f:
        response = client.post("/files/", files={"file": ("test_file.txt", f)})
        assert response.status_code == 200
        assert response.json() == {"filename": "test_file.txt"}


def test_download_file():
    try:
        response = client.get("/files/test_file.txt")
        assert response.status_code == 200
    finally:
        os.remove(f"{UPLOAD_DIRECTORY}/test_file.txt")


def test_get_file_info():
    file_id = "тест.txt"

    test_file_path = os.path.join(UPLOAD_DIRECTORY, file_id)

    with open(test_file_path, "w") as f:
        f.write("test file")

    expected_size = os.path.getsize(test_file_path)

    try:
        response = client.head(f"/files/{urllib.parse.quote(file_id)}")

        assert response.status_code == 200
        assert response.headers["Content-Length"] == str(expected_size)

        expected_content_disposition = f'attachment; filename="{urllib.parse.quote(file_id)}"'
        assert response.headers[
                   "Content-Disposition"] == expected_content_disposition
    finally:
        os.remove(test_file_path)


def test_file_not_found():
    response = client.get("/files/non_existent_file.txt")
    assert response.status_code == 404

    response = client.head("/files/non_existent_file.txt")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main()
