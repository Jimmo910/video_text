from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import os
import torch
import whisper
import platform
import time
import subprocess
import sys
import json
import urllib.request


def update_whisper_model():
    """Check PyPI for a new version of whisper and update if necessary."""
    try:
        from importlib.metadata import version, PackageNotFoundError
    except ImportError:  # pragma: no cover - for Python <3.8
        from importlib_metadata import version, PackageNotFoundError

    try:
        current_version = version("whisper")
    except PackageNotFoundError:
        return

    latest_version = None
    try:
        with urllib.request.urlopen("https://pypi.org/pypi/whisper/json", timeout=3) as resp:
            data = json.load(resp)
            latest_version = data.get("info", {}).get("version")
    except Exception:
        return

    if latest_version and latest_version != current_version:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "whisper"], check=False)
        cache_dir = os.path.join(os.path.expanduser(os.getenv("XDG_CACHE_HOME", "~/.cache")), "whisper")
        shutil.rmtree(cache_dir, ignore_errors=True)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с любых доменов (если нужно ограничить, укажи http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Директория для сохранения загруженных файлов
UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    model: str = Form("base")
):
    # Создание уникальной папки с таймштампом
    timestamp = str(int(time.time()))
    save_dir = os.path.join(UPLOAD_DIR, timestamp)
    os.makedirs(save_dir, exist_ok=True)

    # Сохранение видеофайла в новую папку
    video_path = os.path.join(save_dir, file.filename)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    torch.set_default_dtype(torch.float32)
    # Сохранение имени модели
    model_name = model

    # Определяем устройство для вычислений
    if platform.system() == "Windows" and torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    # Загрузка модели Whisper на выбранное устройство
    model = whisper.load_model(model_name, device=device)
    
    # Распознавание речи из видео
    result = model.transcribe(video_path, language="ru")
    text = result["text"]
    
    # Сохраняем результат в текстовый файл с именем модели
    txt_path = os.path.join(save_dir, f"{model_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    return JSONResponse(content={"text": text})

if __name__ == "__main__":
    update_whisper_model()
    uvicorn.run(app, host="0.0.0.0", port=8000)
