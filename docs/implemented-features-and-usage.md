# StudyPet Implemented Features and Usage

## Overview

This document summarizes the current implementation after the LangGraph, provider, streaming, media, document, frontend integration, and persistence work.

## Implemented Backend Features

### 1. LangGraph Orchestrator

The old keyword-only Orchestrator has been upgraded into a lightweight LangGraph state machine:

```text
START
  -> InputNormalizer
  -> IntentRouter
  -> SingleAgentExecutor
  -> SchemaValidator
  -> EventRecorder
  -> END
```

Files:

```text
backend/app/graph/
backend/app/core/orchestrator.py
```

Preserved constraints:

- One request calls only one Agent.
- No mixed multi-Agent output.
- Agent output is schema-validated.
- Public response shape remains:

```json
{
  "agent": "companion",
  "result": {},
  "confidence": 0.97
}
```

### 2. Agent Registry

Agent metadata is now centralized:

```text
backend/app/agents/registry.py
```

Each Agent has:

```text
id
name
role
persona
allowed_actions
output_schema
confidence
priority
llm_provider
```

### 3. ProviderManager

Provider configuration is centralized:

```text
backend/app/providers/manager.py
```

Supported provider categories:

- LLM
- Image
- Audio

Per-Agent LLM provider overrides are supported:

```env
PLANNER_LLM_PROVIDER=
COACH_LLM_PROVIDER=
COMPANION_LLM_PROVIDER=
GROWTH_LLM_PROVIDER=
RADAR_LLM_PROVIDER=
```

### 4. Streaming Chat

Endpoint:

```text
POST /api/chat/stream
```

SSE events:

```json
{"type": "thinking", "agent": "companion"}
{"type": "text_delta", "content": "我知道你今天..."}
{"type": "emotion", "value": "anxious"}
{"type": "pet_action", "value": "comfort"}
{"type": "done"}
```

The frontend chat panel now consumes this stream.

### 5. Image Provider

Endpoint:

```text
POST /api/media/image/generate
```

Example request:

```json
{
  "prompt": "A cute StudyPet avatar",
  "style": "premium cute ai companion",
  "aspect_ratio": "1:1",
  "provider": "image2"
}
```

Supported provider ids:

```text
openai-image
image2
```

### 6. TTS / ASR

Endpoints:

```text
POST /api/audio/tts
POST /api/audio/asr
```

TTS returns base64 audio:

```json
{
  "audio_base64": "...",
  "provider": "openai-audio",
  "status": "success"
}
```

ASR accepts uploaded audio and returns recognized text.

### 7. Document Parsing

Endpoints:

```text
POST /api/document/parse
POST /api/plan/generate-from-document
```

Supported document formats:

- `.txt`
- `.md`
- `.docx`
- `.pdf` if optional `pypdf` is installed

`/api/plan/generate-from-document` parses the document and routes the extracted text to `StudyPlannerAgent`.

### 8. Database Persistence

Implemented a lightweight SQLAlchemy persistence layer:

```text
backend/app/db.py
```

Default database:

```env
DATABASE_URL=sqlite:///./studypet.db
```

Persisted event types include:

- `chat.message`
- `chat.stream`
- `plan.generate`
- `plan.generate_from_document`
- `study.start`
- `study.end`
- `growth.update`
- `mood.check`
- `media.image.generate`
- `audio.tts`
- `audio.asr`
- `document.parse`
- `report.daily`
- `report.weekly`

Event query endpoint:

```text
GET /api/events?user_id=demo&limit=20
```

## Implemented Frontend Features

### 1. Streaming Chat UI

The home chat panel now displays real chat history:

- user message on the right
- StudyPet reply on the left
- `text_delta` events append progressively
- `emotion` and `pet_action` events update pet state

Files:

```text
frontend/src/services/api.ts
frontend/src/stores/useStudyStore.ts
frontend/src/App.vue
frontend/src/styles.css
```

### 2. Document Import in Planning Page

Location:

```text
Planning page -> AI Planner panel -> Import Study Document
```

Use:

1. Open the Planning page.
2. Upload `.txt`, `.md`, `.docx`, or supported `.pdf`.
3. Frontend calls `/api/plan/generate-from-document`.
4. Study plan and weekly plan update from the returned Planner result.

### 3. Growth Page Media Tools

Location:

```text
Growth page -> center panel
```

Buttons:

- `Generate Pet Concept`
- `Speak Current Reply`
- `Load Saved Events`

Behavior:

- `Generate Pet Concept` calls `/api/media/image/generate`.
- `Speak Current Reply` calls `/api/audio/tts` and renders an audio player.
- `Load Saved Events` calls `/api/events` and displays persisted event records.

## Environment Variables

### Database

```env
DATABASE_URL=sqlite:///./studypet.db
```

### LLM

```env
DEFAULT_LLM_PROVIDER=legacy

LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-flash
LLM_TIMEOUT_SECONDS=20

OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

QWEN_API_KEY=
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

### Image

```env
DEFAULT_IMAGE_PROVIDER=openai-image
IMAGE_API_KEY=
IMAGE_BASE_URL=
IMAGE_MODEL=
IMAGE_TIMEOUT_SECONDS=60
IMAGE_DEFAULT_SIZE=1024x1024
IMAGE_DEFAULT_QUALITY=medium

OPENAI_IMAGE_API_KEY=
OPENAI_IMAGE_BASE_URL=https://api.openai.com/v1
OPENAI_IMAGE_MODEL=gpt-image-2

IMAGE2_API_KEY=
IMAGE2_BASE_URL=https://imgapi.zjapi.com/v1
IMAGE2_MODEL=gpt-image-2
```

### Audio

```env
DEFAULT_AUDIO_PROVIDER=openai-audio
AUDIO_API_KEY=
AUDIO_BASE_URL=
AUDIO_TIMEOUT_SECONDS=60
TTS_MODEL=gpt-4o-mini-tts
TTS_VOICE=alloy
ASR_MODEL=whisper-1
```

## How To Run

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Health check:

```text
GET http://localhost:8000/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Default frontend API base:

```text
http://localhost:8000/api
```

Override:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Verification

Backend tests:

```bash
cd backend
python -m pytest -q
```

Current result:

```text
22 passed
```

Frontend build:

```bash
cd frontend
npm run build
```

Current result:

```text
build passed
```

Known build warnings:

- Vite reports large chunk size.
- Some third-party comments are stripped by Rollup.

These warnings do not block running the app.

## Current Limits

- Generated image/audio files are not yet saved to object storage.
- TTS returns base64 audio directly.
- SQLite is the default local database; PostgreSQL can be used by changing `DATABASE_URL`.
- PDF parsing requires optional `pypdf`.
- Native token streaming from the LLM provider is not implemented yet; current stream chunks validated final text.
