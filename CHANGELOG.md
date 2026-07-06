# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Unreleased

### Added
- Phase 2: Hardware-accelerated rendering utilizing `ffmpeg-python` (replacing `moviepy`).
- Phase 2: Implemented advanced video and audio crossfade transitions via `xfade` and `acrossfade`.
- Phase 2: Implemented real-time subtitle overlays (`.srt`) in the FFmpeg render chain.
- Phase 2: Added multi-layout rendering support, allowing generation of both landscape and portrait aspect ratios sequentially.
- Phase 3: Content Ingestion Automation (`ingestion_engine`, `llm_engine`, `image_engine`).
- Phase 4: CI/CD, Containerization, and Orchestration (`Dockerfile`, FastAPI server, Celery/Redis background worker).
- Kubernetes deployment manifests (`k8s/`).
- Phase 5: Multi-Platform Syndication Initialized.
- Phase 5: Integrated real `requests` implementation for TikTok automated media uploading via the Content Posting API.
- Phase 5: Integrated real `requests` implementation for Instagram Reels automated media uploading via the Facebook Graph API.
- Phase 5: Integrated real `tweepy` implementation for X (Twitter) automated chunked media uploading.
- Phase 5: Implemented analytics polling and LLM feedback loop to dynamically adjust generated scripts based on simulated cross-platform engagement metrics.
- Added `IDEAS.md` and `MEMORY.md` to complete the core documentation governance standard.

## [0.1.0] - 2024-05-24

### Added
- Automated pipeline orchestration via `main.py`.
- `src/config.py` for parsing JSON job schemas via `jsonschema`.
- `src/audio_engine.py` wrapper for `edge-tts` text-to-speech generation.
- `src/video_engine.py` utilizing `moviepy` for visual asset mapping, background audio ducking, and MP4 compositing.
- `src/youtube_publisher.py` for resumable chunked video uploads via the YouTube Data API v3.
- Comprehensive `tests/` directory covering schema validation and compilation logic.
- Documentation mapping (`ROADMAP.md`, `TODO.md`, `VISION.md`, `DEPLOY.md`, `CHANGELOG.md`, `VERSION.md`).
- GitHub Actions CI workflow (`.github/workflows/tests.yml`) to automatically test the pipeline on push/PR to `main`.