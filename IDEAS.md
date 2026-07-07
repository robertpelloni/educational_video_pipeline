# IDEAS

This document serves as a scratchpad for aggressive pivots, refactoring ideas, re-architecting plans, language porting, and feature expansions.

## 1. Interactive Web Player (Phase 6)
Instead of just rendering flat MP4s for YouTube/TikTok, we can build a custom HTML5 web application.
- **Branching Narratives:** Use the LLM to generate multiple script branches. Render video segments for each. The frontend can allow users to click buttons mid-video to choose which topic to dive deeper into.
- **Mid-Stream Quizzes:** Overlay interactive quizzes using React while the video pauses.

## 2. Real API Publisher Implementations
Currently, the multi-platform syndication uses stubs. Here are the target implementations:
- **TikTok API:** Integrate the TikTok Content Posting API. This requires an OAuth flow and a direct upload POST sequence, sending chunked video data.
- **Instagram Graph API:** Utilize Facebook's Graph API for Instagram Reels publishing. This involves creating a container using `POST /{ig-user-id}/media` and then publishing it using `POST /{ig-user-id}/media_publish`.
- **X (Twitter) API v2:** Use the Twitter API v2 media endpoint. Requires chunked upload (INIT, APPEND, FINALIZE) for videos over 15MB.

## 3. Advanced LLM Generation
- ~~Transition from basic string splitting in `llm_engine.py` to using `instructor` or `langchain` with OpenAI's `gpt-4o` structured JSON outputs. This guarantees perfect adherence to the `src.config.SCHEMA`.~~ (Implemented via `instructor` Pydantic models).
- Integrate a factual verification step (e.g., retrieving actual Wikipedia paragraphs) and cross-referencing them before script generation to completely eliminate hallucinations.

## 4. Rust Rewrite for Core Rendering Engine
- **Aggressive Refactoring:** As the queue scales, the Python orchestrator might become a bottleneck for heavy `ffmpeg` process management. We could port `ffmpeg_engine.py` to a highly concurrent Rust microservice using `ffmpeg-next`, exposed via gRPC to the main Python orchestrator.
