# VISION

## Ultimate Goal
To build a fully automated, scalable, and self-sufficient media generation pipeline that aggregates public-domain knowledge and transforms it into engaging, high-quality, interactive educational videos tailored for young adults and teens on platforms like YouTube and TikTok.

## Core Foundational Concepts
- **Autonomy:** The system must function with minimal human intervention, automatically ingesting content, generating assets (TTS, images), compositing, and publishing.
- **Accuracy & Safety:** Content must be strictly sourced from verified public domain/creative commons repositories (e.g., Wikipedia) to ensure scientific and educational accuracy while avoiding copyright infringement.
- **Engagement:** Videos will utilize expressive text-to-speech, dynamic visual compositing (e.g., Ken Burns scaling), and carefully ducked background music (e.g., psytrance) to maintain audience retention without overwhelming the core educational message.

## User-Satisfaction Design
- **Frictionless Consumption:** Delivering complex topics through short, visually dynamic, and auditorily pleasing formats.
- **Accessibility:** Future iterations will support multi-language TTS and baked-in `.srt` subtitle generation to accommodate all viewers.
- **Iterative Improvement:** The pipeline architecture is decoupled (config, audio, video, publisher) to allow rapid swapping of underlying engines (e.g., moving from CPU `moviepy` to hardware-accelerated `ffmpeg` or integrating LLMs for better script structuring) without breaking the core workflow.