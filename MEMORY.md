# SYSTEM MEMORY

Ongoing internal architectural observations, codebase traits, and design preferences.

## Active Architecture
- **Version:** Synchronized at `0.4.0` defined centrally in `VERSION.md`.
- **Orchestration:** `main.py` serves as the CLI entrypoint, while `src/worker.py` (Celery) serves as the asynchronous task entrypoint for scaled deployments.
- **Rendering Stack:** Enforces `ffmpeg-python` for hardware-accelerated video rendering.
- **Audio/Subtitle Stack:** `edge-tts` handles text-to-speech with streaming `WordBoundary` parsing for subtitle synchronization (.srt), burned directly into the video stream using FFmpeg's `subtitles` filter.
- **Service Management & System Tray:** `src/tray_icon.py` provides a native desktop tray icon using `pystray` and `PIL` with actions to open the dashboard, query health, restart, and cleanly quit servers (`kill_process_by_pattern`). CLI options include `--headless` and `--stop`.
- **Unified Frontend Architecture:** The React dashboard in `/frontend` is consolidated into a single-page operations command center with high-value prioritization (Autonomous Video Studio, Celery Task Execution Monitor, Story Branching Web Player, Cross-Platform Analytics Inspector, ERP Event Simulator, and Dynamic Auth Handshake Modal).
- **Authentication Handshake:** The frontend gracefully intercepts 401 Unauthorized responses and provides an interactive modal allowing dynamic credential/token updates without halting background queue execution.

## Developer Preferences
- **Strict Formatting & Linting:** Codebase adheres strictly to `flake8` and `black`. Frontend follows `oxlint`.
- **Testing:** Always run `PYTHONPATH=. pytest tests/` and Playwright tests in `/frontend`.
- **Logging:** Always use the standard Python `logging` module rather than arbitrary `print()` statements.
