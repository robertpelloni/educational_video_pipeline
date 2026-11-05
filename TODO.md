# TODO

## Immediate Action Items

### Completed Items
- [x] **Caption Generation**: Generate text subtitles (`.srt` files) natively alongside the TTS output to pass to YouTube, or bake them visually into the video feed.
- [x] **Canvas Layout Fix**: Update `video_engine.py` to enforce crop/resize metrics depending on `canvas_format` (portrait vs landscape) instead of relying on the source image size directly.
- [x] **Audio Mix Customization**: Abstract the hard-coded `0.15` and `0.12` ducking volumes into a mathematically sound decibel attenuation curve to prevent peaking.
- [x] **Desktop System Tray Daemon**: Implemented `src/tray_icon.py` supporting Open Dashboard, Service Health check, Restart Services, and Graceful Server Teardown.
- [x] **Unified Dashboard UI**: Re-architected `/frontend` into a consolidated single-page operations hub featuring real-time health ribbon, autonomous generation studio, story branching web player, task execution monitor, cross-platform analytics inspector, and ERP simulator.
- [x] **Dynamic Auth Handshake**: Phase 7 token-refresh handshake intercepting 401s smoothly without terminating active background Celery processors.
- [x] **REST API Expansion**: Implemented `/status`, `/auth/verify`, `/tasks/{task_id}`, `/orders`, `/validate-config`, and `/analytics/{project_id}` endpoints.
- [x] **Service Automation Scripts**: Created modern `start_services.sh` and `stop_services.sh` with process cleanup and nondestructive backups.

### Future Enhancements & Optimization Items
- [ ] **Streaming Progress Websockets**: Upgrade task status polling from HTTP interval requests to a bidirectional FastAPI WebSocket endpoint.
- [ ] **Audio Preview Synthesis**: Add a quick 3-second audio snippet audition in the UI before full video compilation.
- [ ] **Custom Watermarking Node**: Add configurable PNG logo overlay position in the FFmpeg filter graph.
