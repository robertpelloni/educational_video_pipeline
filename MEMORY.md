# SYSTEM MEMORY

Ongoing internal architectural observations, codebase traits, and design preferences.

## Active Architecture
- **Orchestration:** `main.py` serves as the CLI entrypoint, while `src/worker.py` (Celery) serves as the asynchronous task entrypoint for scaled deployments.
- **Rendering Stack:** We enforce the use of `ffmpeg-python` for hardware-accelerated video rendering. `moviepy` has been fully deprecated and should not be reintroduced.
- **Audio/Subtitle Stack:** `edge-tts` handles text-to-speech. Crucially, it generates byte-stream WordBoundaries which are parsed into exact `.srt` files. These `.srt` files are subsequently burned directly into the video stream using FFmpeg's `subtitles` filter.
- **Data Schemas:** All jobs are validated strictly against the JSON schema defined in `src/config.py` using `jsonschema`.
- **Transitions:** We utilize `xfade` for video and `acrossfade` for audio transitions within the FFmpeg filter graph.

## Developer Preferences
- **Strict Linting:** We use `flake8` and `black`. Code should always adhere to PEP8.
- **Logging:** Always use the standard Python `logging` module rather than arbitrary `print()` statements.
- **Safe Pathing:** Path traversal is mitigated via regex. Missing assets must be aggressively validated (`os.path.exists`) in Python before passing paths into FFmpeg bindings to prevent cryptic C-level crashes.
