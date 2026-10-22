# educational_video_pipeline

**This repository contains no code.** Its only file is the document that
used to be this README: a chat transcript designing an automated pipeline
for AI-generated educational YouTube videos. No pipeline was built; the
transcript is the deliverable.

## The concept (from the document)

A content factory answering the questions kids, teens, and young adults
actually search for, as short animated info-videos — narrated explainers
with generated visuals and the creator's psytrance tracks ducked under the
voiceover. An early idea in the thread (AI-generating the "What Is My Body
Doing?"-style books sold at Five Below) was dropped in favor of building
from **public-domain knowledge only**, for copyright reasons the document
itself walks through.

## The design in the transcript

Five stages:

1. **Data** — pull public-domain source material (Wikipedia API, Open
   Library, Project Gutenberg) on trending question topics.
2. **Script** — an LLM formats the material into a timed `script.json`:
   title, background music track, and scenes with narration text,
   `visual_prompt`, and `duration_seconds` (worked example included:
   "How the Human Heart Works").
3. **Assets** — voiceover via edge-tts; scene images via Stable
   Diffusion/Flux (ComfyUI API).
4. **Render** — MoviePy/FFmpeg assembly: Ken Burns pan/zoom on stills,
   durations matched to the voice track, background music ducked
   (−dB under narration) via `CompositeAudioClip`/`volumex`. A complete
   foundational `create_automated_video()` script is included inline.
5. **Upload** — YouTube API with metadata tagging.

The transcript also covers the interactivity idea (web players with
mid-video quizzes/branching instead of linear YouTube video) and the
content-strategy guardrails (original scripting from public sources,
medically/scientifically accurate, no cloning of copyrighted books).

## Status

Design document only, written in one session on 2026-07-03 (two commits).
The foundational assembly script exists solely as a code block inside the
transcript in git history; a real implementation would start by extracting
it and wiring stages 1–3 and 5 around it.
