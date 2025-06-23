import sys
import types
import importlib

from fastapi.testclient import TestClient

# Prepare dummy modules for torch and whisper before importing server
class DummyModel:
    def transcribe(self, video_path, language="ru"):
        return {"text": "dummy"}

dummy_whisper = types.SimpleNamespace(load_model=lambda name: DummyModel())
dummy_torch = types.SimpleNamespace(set_default_dtype=lambda *args, **kwargs: None, float32="float32")

sys.modules.setdefault("whisper", dummy_whisper)
sys.modules.setdefault("torch", dummy_torch)

server = importlib.import_module("server")

def test_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "UPLOAD_DIR", str(tmp_path), raising=False)
    client = TestClient(server.app)

    files = {"file": ("test.txt", b"hello")}
    response = client.post("/upload", files=files, data={"model": "base"})

    assert response.status_code == 200
    data = response.json()
    assert "text" in data
