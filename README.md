# StudyPet AI

StudyPet AI is a Vue + FastAPI study companion prototype. It uses an animated desktop-pet style companion as the main entry point for:

- AI companion chat
- AI study plan generation
- Local daily study check-in

## Project Structure

```text
backend/   FastAPI backend, orchestrator, modular agents
frontend/  Vue 3 + TypeScript + Vite frontend
```

## Local Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

Set your real key in `backend/.env`:

```env
LLM_API_KEY=your_key_here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-flash
```

## Local Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend reads the backend URL from:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Deploy

Recommended:

- Backend: Render
- Frontend: Vercel

### Render Backend

This repo includes `render.yaml`.

On Render:

1. Create a new Blueprint or Web Service from this GitHub repo.
2. Use `backend` as root directory if creating manually.
3. Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

4. Add environment variables:

```env
LLM_API_KEY=your_key_here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-flash
```

### Vercel Frontend

On Vercel:

```text
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

Add:

```env
VITE_API_BASE_URL=https://your-render-backend-url/api
```

## Notes

- Do not put API keys in frontend environment variables.
- The check-in module is local-only for now.
- Chat and plan generation call the backend API.
