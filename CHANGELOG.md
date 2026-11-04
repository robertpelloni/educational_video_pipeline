# CHANGELOG

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-11-04
### Added
- **Unified Single-Page Operations Dashboard**: Redesigned `/frontend` UI into a consolidated high-value command center featuring live status ribbon, autonomous generation studio, story branching web player, task execution monitor, cross-platform analytics inspector, and ERP order event simulator.
- **Interactive Auth Handshake Modal**: Phase 7 token-refresh handshake intercepting 401s smoothly without terminating active background Celery processors.
- **Desktop System Tray Daemon (`src/tray_icon.py`)**: Persistent system tray icon with context menu actions (Open Dashboard, Check Status, Restart Services, and Graceful Server Teardown) with headless fallback mode.
- **REST API Endpoints**:
  - `GET /status` for live health checks.
  - `POST /auth/verify` for credential validation.
  - `GET /tasks/{task_id}` for polling asynchronous Celery task status and outputs.
  - `POST /orders` and `GET /orders/{order_id}` for ERP order state transition simulations.
  - `POST /validate-config` for schema validation dry-runs.
  - `GET /analytics/{project_id}` for cross-platform analytics metrics.
- **Service Management Scripts**: Modernized `start_services.sh` and created `stop_services.sh` with process cleanup and nondestructive backup `start_services.sh.bak`.
- **Unit and Integration Tests**: Added test coverage in `tests/test_tray.py` and expanded `tests/test_api.py`, achieving 71 passing backend tests.

## [0.3.0] - 2026-07-16
### Added
- Initial modular pipeline architecture with moviepy to ffmpeg-python migration.
- Edge-TTS speech and subtitle generation with WordBoundary parsing.
- Multi-platform publisher modules (YouTube, TikTok, Instagram, Twitter).
- Asynchronous Celery worker and Redis broker integration.
- Playwright E2E testing framework.
