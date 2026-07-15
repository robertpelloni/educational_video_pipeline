# Test Matrix Gaps Summary

While the core functionality of the educational video pipeline is heavily tested using mocked unit and integration tests across 32 individual assertions, there are several edge cases and external boundaries that currently lack robust coverage.

## 1. Rate Limiting Middleware
- ~~**Gap:** The FastAPI router does not have explicit token bucket or sliding window rate-limiting middleware configured.~~ (Resolved)
- **Risk:** Without an active rate limiter, the `/generate` endpoint could be subject to denial-of-service (DoS) by an authenticated user spamming the Celery queue.
- ~~**Action Required:** Introduce an IP/Auth-token based rate limiter (e.g., using `slowapi`) and write test cases simulating `HTTP 429 Too Many Requests`.~~ (Resolved)

## 2. API Token Expiration
- ~~**Gap:** The current Basic Auth implementation relies on static environment passwords (`secrets.compare_digest`). It does not handle temporary session states (like JWTs) or OAuth 2.0.~~ (Resolved)
- **Risk:** If the architecture pivots to using OAuth (e.g., passing TikTok or YouTube API tokens through the UI instead of standard basic auth), the tests do not assert what happens when those third-party tokens expire mid-execution in the Celery worker.
- ~~**Action Required:** As multi-platform publishing scales, tests must be added to the publisher scripts simulating HTTP 401s from Google/TikTok and catching those exceptions gracefully without killing the queue.~~ (Resolved)

## 3. Celery Timeout and Memory Leaks
- ~~**Gap:** Celery workers lack integration tests validating timeouts if `ffmpeg` hangs on a corrupted asset.~~ (Resolved)
- **Risk:** Hardware-accelerated tasks can sometimes freeze. If `ffmpeg.run()` stalls forever, the worker node will bottleneck.
- ~~**Action Required:** Write tests passing `soft_time_limit` parameters into the task mock and asserting that a `SoftTimeLimitExceeded` exception is caught.~~ (Resolved)

## 4. Frontend E2E Playwright Tests
- ~~**Gap:** The newly scaffolded React application (`frontend/`) contains a `useDataFetch.js` hook and `App.jsx`, but lacks a Playwright or Cypress suite to test the user interface end-to-end.~~ (Resolved)
- **Risk:** React states, loading spinners, and network latency fallback paths might regress.
- ~~**Action Required:** Introduce Playwright testing to boot the mock Vite server and test DOM element states.~~ (Resolved)

These gaps should be flagged with a `priority: medium` label in the project's issue tracker for the next sprint iteration.

## 5. OpenAPI Specification Mismatch vs Live Application
- **Gap:** The `openapi.json` generated from the FastAPI application does not document the `HTTP 400 Bad Request` or `HTTP 401 Unauthorized` responses that the API endpoint actually returns under validation and authentication failures. It only surfaces `HTTP 200 OK` and `HTTP 422 Validation Error`.
- **Risk:** Clients relying strictly on the OpenAPI schema for SDK generation or integrations will lack proper error-handling awareness for authentication limits and bad payload types.
- **Action Required:** Update the FastAPI `@app.post("/generate", responses={...})` decorator to explicitly document `400` and `401` status codes.

## 6. Input Parser Boundary Tests
- ~~**Gap:** The CLI parser (`main.py`) does not explicitly test boundary conditions for malformed input topics.~~ (Resolved)
- **Risk:** End-users running the pipeline via terminal could pass empty strings or strings consisting entirely of whitespace, crashing the underlying Wikipedia ingestion engine down the stack.
- ~~**Action Required:** Implement negative path testing in `tests/test_main.py` explicitly asserting that an empty string provided to `--topic` raises a safe `SystemExit(1)` inside `main.py` without leaking stack traces or crashing worker nodes.~~ (Resolved)

## 8. Async Generation Tests
- ~~**Gap:** `src/audio_engine.py` generates voiceovers and subtitles using `asyncio` streams (`_generate_audio_async`), but no unit tests specifically mocked and verified this asynchronous data flow and byte-writing sequence.~~ (Resolved)
- **Risk:** Without asserting that the `WordBoundary` data stream properly maps to the `.srt` SubMaker output, timing mismatches in generated subtitles could go undetected.
- ~~**Action Required:** Implement a targeted mock test for the `edge_tts.Communicate.stream()` generator, verifying that `audio` chunks trigger file writes and `WordBoundary` chunks trigger `sub_maker.feed()` calls.~~ (Resolved)
