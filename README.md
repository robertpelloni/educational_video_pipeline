# educational_video_pipeline

An automated pipeline (v0.3.0) that turns public-domain / Creative Commons knowledge into AI-generated educational videos and publishes them to YouTube, TikTok, Instagram, and X. The intended flow: ingest a topic, script it with an LLM, generate voiceover and images, assemble the video with FFmpeg, and upload.

## Status

**Active, early-stage.** Last significant activity: **2026-11-12** — merge of a unified-dashboard/tray-manager feature branch (Protocol #281). Nov 9–11 work focused on visual prompt synthesis (camera motion, depth of field, subject-consistency tags), subtitle calibration, and reading-level adaptation.

No released videos, no deployment record, and no evidence in the repo that the full pipeline has run end-to-end to a published upload. Treat it as a working prototype, not a proven factory.

## What's in here

- `main.py` — entry point; `src/worker.py` — job worker; `src/config.py` — configuration
- `src/ingestion_engine.py` — topic/content ingestion; `src/llm_engine.py` — script generation
- `src/audio_engine.py` — voiceover/TTS; `src/image_engine.py` — visual asset generation
- `src/ffmpeg_engine.py` — video assembly; `src/api_router.py` — API routes
- `src/youtube_publisher.py`, `src/tiktok_publisher.py`, `src/instagram_publisher.py`, `src/twitter_publisher.py` — platform publishers
- `src/analytics_engine.py`, `src/tray_icon.py` — analytics and desktop tray manager
- `frontend/` — dashboard UI; `tests/` — test suite (see `TEST_GAPS_SUMMARY.md` for known coverage gaps); `k8s/` — Kubernetes manifests; `Dockerfile`
- `openapi.json`, `postman_collection.json` — API contract; `start_services.sh` / `stop_services.sh` — service wrappers

## Running

```bash
pip install -r requirements.txt
./start_services.sh
```

See `DEPLOY.md` for deployment notes and `HANDOFF.md` for the current state of the work.
