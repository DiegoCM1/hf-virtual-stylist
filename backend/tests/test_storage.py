from app.services import storage


def test_save_bytes_uses_local_storage(tmp_path, monkeypatch):
    monkeypatch.delenv("PUBLIC_BASE_URL", raising=False)
    monkeypatch.setenv("LOCAL_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("STORAGE_DRIVER", "local")
    storage._reset_storage_cache()

    url = storage.save_bytes(b"demo", "generated/family/color/image.jpg")

    expected_path = tmp_path / "generated" / "family" / "color" / "image.jpg"
    assert expected_path.read_bytes() == b"demo"
    assert url == "http://localhost:8000/files/generated/family/color/image.jpg"


def test_save_bytes_respects_public_base_url(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCAL_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://api.example.com")
    monkeypatch.setenv("STORAGE_DRIVER", "local")
    storage._reset_storage_cache()

    url = storage.save_bytes(b"demo", "generated/family/color/image.jpg")

    assert url == "https://api.example.com/files/generated/family/color/image.jpg"
