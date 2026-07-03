# ROADMAP

## Long-Term Structural Milestones

### Phase 1: Core Content Pipeline
- [x] Basic programmatic TTS voice generation via `edge-tts`.
- [x] Dynamic audio ducking of background music over vocals using `moviepy`.
- [x] Static image assembly to dynamic MP4 with basic Ken Burns zoom effects.
- [x] Resumable chunked uploads to YouTube Data API v3.

### Phase 2: Enhanced Rendering & Animation
- [ ] Transition from CPU-bound `moviepy` rendering to a hardware-accelerated pipeline (e.g. raw `ffmpeg` via bindings or `ffmpeg-python`) to speed up execution.
- [ ] Introduce advanced transitions between scene boundaries (fade, cross-dissolve, swipe).
- [ ] Support overlaying generated `.srt`/`.vtt` captions onto the video in real-time.
- [ ] Create multi-layout rendering outputs concurrently (1080x1920 for YouTube Shorts / TikTok vs. 1920x1080 for standard YouTube).

### Phase 3: Content Ingestion Automation
- [x] Connect the pipeline to public APIs (e.g. Wikipedia, Open Library) for raw text content gathering.
- [x] Integrate local or hosted LLM endpoints to structure raw text into the `script.json` schema.
- [ ] Interface with ComfyUI or Stable Diffusion WebUI API to generate the scene images automatically via prompts.

### Phase 4: CI/CD, Containerization & Orchestration
- [ ] Dockerize the entire application (`Dockerfile`, `docker-compose.yml`) ensuring FFmpeg and dependencies are cleanly packaged.
- [ ] Deploy via Kubernetes or asynchronous queue managers (like Celery/RabbitMQ) for batch video processing at scale.
- [ ] Build a React-based interactive web frontend for previewing generated videos before triggering the YouTube publisher.

### Phase 5: Multi-Platform Syndication
- [ ] Expand publisher engines to support TikTok, Instagram Reels, and X (Twitter) natively.
- [ ] Implement analytics polling to track performance across networks and feedback loop into the content generator LLM.
