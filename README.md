# Video Text Project

This project contains a FastAPI backend and a React/Vite frontend for uploading a video and getting the transcribed text.

## Backend (FastAPI)

### Install dependencies

Create and activate a virtual environment and install packages:

```bash
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn whisper torch
```

### Run the server

Run `server.py` directly to start the API on port `8000`:

```bash
python server.py
```

## Frontend (React)

### Install dependencies

All client files reside in the `client` directory. Install dependencies with npm:

```bash
cd client
npm install
```

### Environment variables

The React app expects a `VITE_API_URL` variable pointing to the running FastAPI server. Create a `.env` file inside `client`:

```
VITE_API_URL=http://localhost:8000
```

### Run the development server

Start the Vite development server:

```bash
npm run dev
```

The React app will be available at [http://localhost:5173](http://localhost:5173) by default and will send API requests to the URL configured in `VITE_API_URL`.

