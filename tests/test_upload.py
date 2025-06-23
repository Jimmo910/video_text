import sys
import types
import importlib
import os
import asyncio
from fastapi import UploadFile
import io

# Prepare dummy modules for torch and whisper before importing server
class DummyModel:
    def transcribe(self, video_path, language="ru"):
        return {"text": "dummy"}

dummy_whisper = types.SimpleNamespace(load_model=lambda name, device=None: DummyModel())
dummy_torch = types.SimpleNamespace(
    set_default_dtype=lambda *args, **kwargs: None,
    float32="float32",
    cuda=types.SimpleNamespace(is_available=lambda: False),
)
dummy_multipart_sub = types.SimpleNamespace(parse_options_header=lambda *a, **k: None)
dummy_multipart = types.SimpleNamespace(__version__="0.0", multipart=dummy_multipart_sub)

sys.modules.setdefault("whisper", dummy_whisper)
sys.modules.setdefault("torch", dummy_torch)
sys.modules.setdefault("multipart", dummy_multipart)
sys.modules.setdefault("multipart.multipart", dummy_multipart_sub)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

server = importlib.import_module("server")

def test_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "UPLOAD_DIR", str(tmp_path), raising=False)
    file_obj = io.BytesIO(b"hello")
    upload_file = UploadFile(filename="test.txt", file=file_obj)
    response = asyncio.run(server.upload_video(upload_file, model="base"))

    assert response.status_code == 200
    data = response.body.decode()
    assert "text" in data
