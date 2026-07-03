# TODO

## Immediate Action Items

### Code Refactoring & Logic Expansion
- [x] **Caption Generation**: Generate text subtitles (`.srt` files) natively alongside the TTS output to pass to YouTube, or bake them visually into the video feed.
- [x] **Canvas Layout Fix**: Update `video_engine.py` to enforce crop/resize metrics depending on `canvas_format` (portrait vs landscape) instead of relying on the source image size directly.
- [x] **Audio Mix Customization**: Abstract the hard-coded `0.15` and `0.12` ducking volumes into a mathematically sound decibel attenuation curve to prevent peaking.

### Testing & Quality Assurance
- [ ] **Integration Tests**: Expand `tests/` with a full mock run of the `main.py` entrypoint.
- [ ] **Asset Validation Check**: Ensure image bounds/aspect ratios are verified during the `config.py` schema checks.
- [ ] **Linting & Formatting**: Integrate `flake8` or `black` for standardized codebase formatting and PEP8 adherence.

### CI/CD & Orchestration (Near-Term)
- [x] **GitHub Actions Setup**: Create `.github/workflows/tests.yml` to automatically run `pytest` upon PRs.
- [x] **Logging Hooks**: Replace standard `print()` statements throughout the engines with the Python `logging` module. Configure different log levels (INFO, DEBUG, ERROR) to pipe logs to file storage or DataDog.
- [x] **Containerization**: Create an initial `Dockerfile` setting up Python 3.12, system dependencies (like FFmpeg headers), and copying `src/` to ensure isolated execution runs.

### Documentation Governance
- [x] Initialize `VISION.md` to break down the user-satisfaction design per the autonomy directive.
- [x] Initialize `DEPLOY.md` outlining API key procurement for local environments.
- [x] Initialize `CHANGELOG.md` to track global version string increments.
