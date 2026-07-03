# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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