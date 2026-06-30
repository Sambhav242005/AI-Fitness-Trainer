---
contentKind: case-study
title: "AI Fitness Trainer"
slug: "ai-fitness-trainer"
summary: "A privacy-first, locally-run AI fitness coach combining YOLOv11 pose estimation with a vision-language model for real-time rep counting, form analysis, and AI coaching."
status: published
order: 1
featured: true
updatedAt: 2026-06-30
tags:
  - Computer Vision
  - Pose Estimation
  - YOLOv11
  - Ollama
  - Flask
  - PyQt6
---

## Problem

Most fitness tracking applications count repetitions using timers or accelerometer heuristics — they cannot evaluate whether the user is performing an exercise correctly. Good form feedback traditionally requires a human coach, which is expensive, inaccessible, and not available on demand. Meanwhile, cloud-based AI pose estimation services raise privacy concerns around streaming bedroom or living-room video to third-party servers.

## Approach

I built a browser-based and desktop-local fitness assistant that runs entirely on-device, with no cloud dependencies. The system uses a webcam feed, YOLOv11 pose estimation, exercise-specific geometric logic, and a local vision language model to provide form-aware rep counting and coaching.

The architecture is split into four layers:

- **Capture**: Camera input via browser `getUserMedia` (web) or OpenCV (desktop) streams frames to a Flask-SocketIO backend or directly to a PyQt6 video thread.
- **Pose Inference**: YOLOv11 extracts 17 body keypoints from each frame. The system automatically selects the full-accuracy `yolo11x-pose.pt` model when CUDA is available, and falls back to the fast `yolo11n-pose.pt` for CPU-only systems.
- **Logic**: `RepCounter` state machines use 2D vector geometry — computing joint angles via dot-product — to detect rep transitions and flag form issues for squats, bicep curls, and push ups. Dual-arm tracking for curls includes hysteresis logic to prevent flickering between arms.
- **AI Coaching**: Every 5 completed reps, the current frame is sent to a locally-hosted Ollama instance running Qwen3-VL, which returns a one-sentence form tip. Feedback is spoken aloud via pyttsx3 text-to-speech.

## Technical Decisions

- **Flask + SocketIO** serves the web frontend with real-time bidirectional frame exchange. The browser captures frames at ~10 FPS via canvas snapshots, sends them as base64 JPEGs, and receives annotated frames with skeleton overlays, depth target lines, and a progress bar.
- **PyQt6** provides an alternative native desktop UI sharing the same `VideoProcessor` backend, with exercise selector dropdown, large rep counter display, and live feedback labels.
- **Dual-arm hysteresis** for bicep curls uses a ±20° bias toward the last active arm, preventing rapid toggling when both arms are visible and at similar angles.
- **Privacy by design**: camera feed, YOLO inference, angle calculations, LLM calls, and TTS all stay on the local machine. No data leaves the device.

## Result

The project demonstrates practical integration of CV inference, local LLM calls, browser camera workflows, and real-time user feedback — all within a privacy-preserving local architecture. The codebase supports two front-end modes, automatic GPU/CPU model selection, and three exercises with distinct state-machine rep counting logic.

**Tech stack**: Python 3.10+, Ultralytics YOLOv11, PyTorch, OpenCV, Flask, Flask-SocketIO, PyQt6, Ollama + Qwen3-VL, pyttsx3.
