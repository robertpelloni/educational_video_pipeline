# HANDOFF

## Session Summary & Context
This document serves as the primary context restoration point for the next AI agent session.
We have successfully built the foundation for an **Automated Educational Video Composition and YouTube Publishing Pipeline** built entirely in Python (3.12+). The project's goal is to aggregate public domain data into JSON schemas and automatically compile them into YouTube Shorts or standard videos.

### What Was Accomplished During This Session
- **Core Architecture Built:** `src/config.py`, `src/audio_engine.py`, `src/video_engine.py`, `src/youtube_publisher.py`, and `main.py` entrypoint.
- **Phase 3 (Content Ingestion) Complete:**
  - `src/ingestion_engine.py`: Scrapes public domain text from the Wikipedia REST API using native `urllib`.
  - `src/llm_engine.py`: Structurally parses text into the rigid `script.json` schema.
  - `src/image_engine.py`: Generates PNG visual assets via HTTP POST requests to a local Stable Diffusion / AUTOMATIC1111 endpoint.
- **End-to-End Orchestration:** `main.py` now supports `--topic <string>` which sequentially links ingestion, LLM structuring, image generation, TTS, and video rendering autonomously without human intervention.
- **Audio Engineering:** Integrated `edge-tts` for programmatic text-to-speech generation. It simultaneously extracts `WordBoundary` byte streams to output exact-match `.srt` subtitle files natively.
- **Video Compositing (MoviePy v2.x):**
  - Dynamic aspect ratio resizing via `clip.resized()` (1080x1920 portrait / 1920x1080 landscape).
  - Basic "Ken Burns" zoom loop via `clip.image_transform()`.
  - Ducking background music tracks mathematically (`global_music_volume_db`) via `MultiplyVolume` and `AudioLoop` effects.
- **YouTube Headless Upload:** Implementation of chunked resumable file transfers to the YouTube Data API v3 (`resumable=True`).
- **QA & Testing:** Complete unit and integration testing via `pytest` (including heavy `--topic` logic mocks). CI/CD implemented via GitHub Actions. Asset boundary checking implemented.
- **Containerization:** Built a lightweight `python:3.12-slim` Docker image loaded with system `ffmpeg` binaries to standardize deployments.
- **Frontend UI & API Routing:** Initialized a React application in `/frontend` providing an interactive UI to manually trigger topic queries. Constructed a lightweight `FastAPI` server (`src/api_router.py`) providing a REST `POST /generate` endpoint that dynamically dispatches the video generation logic as a non-blocking background task.
- **Documentation Complete:** Established `ROADMAP.md`, `TODO.md`, `VISION.md`, `DEPLOY.md`, `CHANGELOG.md`, and `VERSION.md`. Linter (`flake8`) initialized.

## Architectural Notes & "Gotchas" (System Memories)
1. **MoviePy v2.x Strictness:** The repository relies on the modern MoviePy v2 architecture. Do **not** hallucinate or revert back to `moviepy.editor` v1.x methodologies. Operations must use the top-level imports (`from moviepy import ...`). Chained clip functions use `clip.with_duration(...)` or `clip.with_audio(...)` rather than `set_duration()`. Audio and video effects are explicitly passed as classes (e.g., `clip.with_effects([MultiplyVolume(factor)])`).
2. **Audio Ducking Math:** The configuration uses `global_music_volume_db` instead of raw multipliers to calculate attenuation. The math used inside `video_engine.py` is `multiplier = 10 ^ (dB / 20.0)`.
3. **Asset Safety:** `config.py` explicitly throws an `os.path.exists` validation check early on all required image files to prevent the underlying FFmpeg wrapper from returning vague `AttributeError` exceptions mid-render.

## Next Steps for Successor Model
1. Parse the `ROADMAP.md`. Phase 1, Phase 2, and Phase 3 are now fully complete.
2. Review Phase 4 (CI/CD): We have basic testing, containerization, a React frontend, and FastAPI background task routing. Kubernetes deployment and Celery/RabbitMQ batch queue management remain unbuilt for high-volume scale.
3. Phase 5 calls for implementing multi-platform syndication engines (e.g. TikTok, X).

Resume executing recommendations sequentially and autonomously based on the `ROADMAP.md`!