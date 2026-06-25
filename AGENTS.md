# AI Fitness Trainer — Agent Instructions

## Project Overview

A privacy-focused, locally-run AI fitness trainer combining YOLOv11 pose estimation with a vision-language model (Ollama + Qwen3-VL) for real-time rep counting, form analysis, and AI coaching. Supports Squats, Bicep Curls, and Push Ups.

**Stack**: Python 3.10+, Flask, Flask-SocketIO, PyQt6, Ultralytics YOLOv11, PyTorch, OpenCV, Ollama Vision LLM, pyttsx3 (TTS).

**Two front-end modes**: Web browser (Flask + SocketIO) and native desktop (PyQt6). All processing is on-device.

### Key Architecture

```
Camera → YOLO Pose Inference → Keypoint Extraction → RepCounter (state machine)
                                                          ↓
                                                   Visual Overlays + Stats
                                                          ↓ (every 5 reps)
                                                   Ollama Vision LLM → TTS
```

### Color Scheme

| Usage | Color | Hex |
|---|---|---|
| Background | Dark gray/black | `#1a1a1a`, `#2b2b2b`, `#000` |
| Rep count / Good feedback | Bright green | `#00ff00` |
| Warning / Neutral | Amber | `#ffcc00` |
| Error / "Go Deeper" | Red | `#ff0000` |
| AI Coach text | Cyan | `#00ffff` |
| Panel backgrounds | Medium gray | `#333`, `#444` |
| Text | White | `#ffffff` |

### File Map

- `app.py` — Flask web server + SocketIO routes
- `api.py` — VideoProcessor: YOLO inference, visual overlays, AI trigger
- `engine.py` — PoseMath (angle calcs) + RepCounter (state machines)
- `ai.py` — Ollama OpenAI-compatible vision LLM client
- `tts.py` — pyttsx3 text-to-speech (background thread)
- `ui.py` — PyQt6 desktop UI
- `run.py` — PyQt6 entry point
- `templates/index.html` — Web frontend (single-page)
- `models/` — YOLO pose weights (`yolo11n-pose.pt`, `yolo11x-pose.pt`)
- `assets/` — Exercise guide images (`squat.png`, `bicep_curl.png`, `push_up.png`)

### Rep Counting Logic

- **Squats**: Knee angle via hip-knee-ankle. Hip Y >= 95% of knee Y = rep.
- **Bicep Curls**: Elbow angle via shoulder-elbow-wrist. Dual-arm with hysteresis. < 60° = curl, > 150° = extend.
- **Push Ups**: Arm angle. < 90° = down, > 160° = up.

### Conventions

- Keep all processing local — no cloud dependencies.
- Follow existing naming, typing, and import patterns in each file.
- Dark theme UI with color-coded feedback (green/red/yellow/cyan).
- Use the same `PoseMath.calculate_angle(a, b, c)` utility for any new angle calculations.

## Portfolio Cover Asset

Maintain a project-specific SVG at `docs/portfolio-cover.svg`.

Rules:
- The SVG must be hand-authored/static, not a raster screenshot, AI-generated image, base64 image, or external asset.
- Use `width="1200"`, `height="760"`, `viewBox="0 0 1200 760"`.
- It should visually summarize the real current project: architecture, workflow, UI, model pipeline, or system behavior.
- Update this SVG whenever major project functionality, architecture, or branding changes.
- Keep text minimal and readable at thumbnail size.
- No fake product names, unrelated placeholder visuals, or generic charts.
- The portfolio repo may copy this file into `public/project-assets` as the local backup/rendering copy.
