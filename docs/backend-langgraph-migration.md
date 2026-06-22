# StudyPet Backend LangGraph Migration

## Completed Scope

This migration currently completes:

- Phase 1: lightweight LangGraph Orchestrator state machine
- Phase 2: AgentConfig registry
- Phase 3: ProviderManager with per-Agent LLM provider overrides
- Phase 4: SSE chat stream endpoint
- Phase 5: Image Provider endpoint
- Phase 6: TTS / ASR audio endpoints
- Phase 7: Document parsing and plan generation from document

The external API contract for existing features is preserved. Existing endpoints can continue calling:

- `POST /api/chat`
- `POST /api/plan/generate`
- `POST /api/mood/check`
- `POST /api/study/end`

## Phase 1: LangGraph State Machine

Implemented files:

```text
backend/app/graph/
  __init__.py
  state.py
  router.py
  nodes.py
  graph.py
```

Runtime flow:

```text
START
  -> InputNormalizer
  -> IntentRouter
  -> SingleAgentExecutor
  -> SchemaValidator
  -> EventRecorder
  -> END
```

Strict product constraints preserved:

- one request selects only one Agent
- no multi-agent mixed output
- all responses return the Orchestrator envelope
- Agent result is validated against the selected Agent schema

Envelope:

```json
{
  "agent": "companion",
  "result": {},
  "confidence": 0.97
}
```

## Phase 2: AgentConfig Registry

Implemented file:

```text
backend/app/agents/registry.py
```

Each Agent now has:

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

Registered agents:

- `StudyPlannerAgent`: learning plan generation only
- `StudyCoachAgent`: study behavior feedback only
- `CompanionAgent`: emotional companionship only
- `GrowthAgent`: growth and reward system only
- `AnxietyRadarAgent`: risk detection only

## Phase 3: ProviderManager

Implemented files:

```text
backend/app/providers/
  __init__.py
  manager.py
```

The existing `LLMClient` now reads provider details through `ProviderManager`.
Agent-specific provider overrides are supported through `AgentConfig`.

Supported LLM provider ids:

- `legacy`
- `openai`
- `qwen`
- `deepseek`

Environment variables:

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

PLANNER_LLM_PROVIDER=
COACH_LLM_PROVIDER=
COMPANION_LLM_PROVIDER=
GROWTH_LLM_PROVIDER=
RADAR_LLM_PROVIDER=
```

## Phase 4: Streaming Chat

Implemented files:

```text
backend/app/streaming.py
backend/app/api.py
backend/tests/test_streaming.py
```

Endpoint:

```text
POST /api/chat/stream
```

SSE event format:

```json
{"type": "thinking", "agent": "companion"}
{"type": "text_delta", "content": "我知道你今天..."}
{"type": "emotion", "value": "anxious"}
{"type": "pet_action", "value": "comfort"}
{"type": "done"}
```

Current behavior:

- The endpoint still calls the Orchestrator once.
- The Orchestrator still selects exactly one Agent.
- The final Agent output is still schema-validated.
- `text_delta` events are chunked from the validated result text.
- This is an SSE experience stream, not yet native token streaming from the model provider.

## Phase 5: Image Provider

Implemented files:

```text
backend/app/providers/image.py
backend/app/providers/manager.py
backend/app/schemas/api.py
backend/app/api.py
backend/tests/test_image_provider.py
```

Endpoint:

```text
POST /api/media/image/generate
```

Request:

```json
{
  "prompt": "A cute StudyPet avatar",
  "style": "premium cute ai companion",
  "aspect_ratio": "16:9",
  "provider": "image2"
}
```

Response:

```json
{
  "image_url": "https://...",
  "b64_json": null,
  "provider": "image2",
  "status": "success"
}
```

Supported provider ids:

- `openai-image`
- `image2`

## Phase 6: TTS / ASR

Implemented files:

```text
backend/app/providers/audio.py
backend/app/providers/manager.py
backend/app/schemas/api.py
backend/app/api.py
backend/tests/test_audio_document.py
```

Endpoints:

```text
POST /api/audio/tts
POST /api/audio/asr
```

TTS request:

```json
{
  "text": "今天也辛苦了，我们先休息一下。",
  "voice": "alloy",
  "provider": "openai-audio"
}
```

TTS response:

```json
{
  "audio_base64": "...",
  "provider": "openai-audio",
  "status": "success"
}
```

ASR request:

```text
multipart/form-data
file=<audio file>
provider=openai-audio
```

ASR response:

```json
{
  "text": "我今天有点焦虑",
  "provider": "openai-audio",
  "status": "success"
}
```

Audio environment variables:

```env
DEFAULT_AUDIO_PROVIDER=openai-audio
AUDIO_API_KEY=
AUDIO_BASE_URL=
AUDIO_TIMEOUT_SECONDS=60
TTS_MODEL=gpt-4o-mini-tts
TTS_VOICE=alloy
ASR_MODEL=whisper-1
```

Current behavior:

- Uses OpenAI-compatible `/audio/speech` for TTS.
- Uses OpenAI-compatible `/audio/transcriptions` for ASR.
- Returns `503` if no audio provider key is configured.
- Returns `502` if the upstream audio provider fails.
- TTS returns base64 audio; local/object storage is not implemented yet.

## Phase 7: Document Parsing

Implemented files:

```text
backend/app/documents/parser.py
backend/app/schemas/api.py
backend/app/api.py
backend/tests/test_audio_document.py
```

Endpoints:

```text
POST /api/document/parse
POST /api/plan/generate-from-document
```

`POST /api/document/parse` request:

```text
multipart/form-data
file=<txt/md/docx/pdf file>
```

Response:

```json
{
  "filename": "outline.txt",
  "content_type": "text/plain",
  "text": "函数与导数...",
  "word_count": 12,
  "status": "success"
}
```

`POST /api/plan/generate-from-document` request:

```text
multipart/form-data
file=<document>
exam_type=高考数学
target_score=120
days_left=30
current_level=中等
user_id=demo
```

Response:

```json
{
  "agent": "planner",
  "result": {},
  "confidence": 0.96
}
```

Current parser support:

- `.txt`
- `.md`
- `.docx`
- `.pdf` only when optional `pypdf` is installed

## Tests

Run:

```bash
cd backend
python -m pytest -q
```

Current result:

```text
21 passed
```

## Remaining Recommended Work

- Persist generated images/audio/documents to storage instead of only returning base64 or parsed text.
- Add native token streaming from LLM providers.
- Add frontend UI for document import and voice interaction.
- Add database-backed event records for graph execution.
