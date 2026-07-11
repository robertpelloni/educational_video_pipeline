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
