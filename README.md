# Проект «Video Text»

Этот проект содержит backend на FastAPI и frontend на React/Vite для загрузки видео и получения расшифрованного текста.

## Backend (FastAPI)

### Установка зависимостей

Создайте и активируйте виртуальное окружение, затем установите пакеты:

```bash
python -m venv venv

### MacOS:
source venv/bin/activate
pip install --upgrade pip

### Windows
venv\Scripts\activate
python.exe -m pip install --upgrade pip

pip install fastapi uvicorn whisper torch numpy python-multipart
```

### Запуск сервера

Запустите `server.py` напрямую, чтобы запустить API на порту `8000`:

```bash
python server.py
```

### Возможная ошибка на Windows (библиотека whisper)

При запуске `server.py` на Windows может возникнуть ошибка:

```
TypeError: argument of type 'NoneType' is not iterable
```

Это связано с тем, что оригинальная библиотека `whisper` пытается загрузить `libc`, которая присутствует в Linux/macOS, но отсутствует на Windows.

#### Решение:

Удалите стандартную версию whisper и установите исправленную напрямую с GitHub:

```bash
pip uninstall -y whisper
pip install git+https://github.com/m-bain/whisper.git
```
```bash
python server.py
```
После этого сервер будет работать корректно и на Windows.

## Frontend (React)

### Установка зависимостей

Все файлы клиента находятся в директории `client`. Установите зависимости через npm:

```bash
cd client  
npm install
```

При установке npm может показать предупреждение о найденных уязвимостях. Чтобы их автоматически исправить, выполните:

```bash
npm audit fix
```

После этого можно повторно выполнить:

```bash
npm install
```

### Переменные окружения

Приложение React ожидает переменную `VITE_API_URL`, указывающую на работающий сервер FastAPI. Создайте файл `.env` внутри `client`:

```
VITE_API_URL=http://localhost:8000
```

### Запуск сервера разработки

Запустите сервер разработки Vite:

```bash
npm run dev
```

По умолчанию React-приложение будет доступно по адресу [http://localhost:5173](http://localhost:5173) и будет отправлять API-запросы на адрес, указанный в `VITE_API_URL`.
