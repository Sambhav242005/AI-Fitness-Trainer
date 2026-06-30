---
contentKind: article
slug: fitness-coach-yolov11
title: Building a Local AI Fitness Coach with YOLOv11 and Ollama
type: technical-note
status: published
date: 2026-05-28
summary: Breaking down the keypoint extraction math, state machine rep counting, and local Vision LLM feedback loop behind a privacy-first fitness tracker.
tags:
  - YOLOv11
  - Ollama
  - Pose Estimation
  - Computer Vision
  - Python
---

Fitness applications typically count repetitions based on simple timers or accelerometer changes, which fail to evaluate if a user is performing the exercise correctly. I built a local fitness coach that combines real-time coordinate math with a Vision LLM for detailed form correction.

## Keypoint Extraction & Joint Geometry

Using YOLOv11-pose, the application extracts 17 body keypoints from the webcam stream. We calculate joint angles in real time using 2D vector geometry. For instance, the knee flex angle is calculated by taking keypoints for the hip (A), knee (B), and ankle (C):

- Vector BA = (xA - xB, yA - yB)
- Vector BC = (xC - xB, yC - yB)
- Angle = arccos( (BA · BC) / (|BA| * |BC|) )

The `PoseMath.calculate_angle()` utility in `engine.py` implements this with `numpy` — computing dot products, norms, and a safe clip to [-1.0, 1.0] before `arccos`. This single function drives all three exercise state machines.

## State Machine Rep Counting

To avoid false counts due to jitter, the system uses a two-threshold state machine per exercise:

| Exercise | Joints | Down Threshold | Up Threshold |
|---|---|---|---|
| Squat | Hip(11) / Knee(13) / Ankle(15) | Hip Y >= 95% of Knee Y | Knee angle > 160° |
| Bicep Curl | Shoulder(5/6) / Elbow(7/8) / Wrist(9/10) | Angle < 60° (curled) | Angle > 150° (extended) |
| Push Up | Shoulder(5) / Elbow(7) / Wrist(9) | Angle < 90° | Angle > 160° |

The squat uses an unusual approach for depth detection: instead of relying purely on knee angle, it compares the pixel Y-coordinates of hip and knee. Since Y increases downward in image coordinates, a hip Y value above 95% of the knee Y value means the hip has descended past the knee — a reliable depth signal that works across camera angles.

## Dual-Arm Hysteresis for Bicep Curls

Bicep curls are unique in that users may alternate arms between reps. When both arms are visible, the system picks the "more curled" arm (smaller elbow angle) as active. To prevent flickering when angles are nearly equal, a ±20° bias is applied toward whichever arm was last tracked:

```python
bias = 20
if last_side == "Right":
    # Left must be significantly more curled to switch
    if angle_l < angle_r - bias: switch to Left
else:
    # Right must be significantly more curled to switch
    if angle_r < angle_l - bias: switch to Right
```

This keeps the rep counter stable during normal alternating curl sets while still responsive when the user clearly switches arms.

## Local Vision LLM Feedback Loop

Every 5 completed reps, the `VideoProcessor` captures the current frame and launches a background thread that calls the Ollama API at `localhost:11434` with Qwen3-VL. The prompt asks for one specific, short form tip:

> "I am doing Squat. I just finished 10 reps. Look at my form in this image. Give me one specific tip to improve. Keep it short (1 sentence)."

The response is displayed as cyan italic text in the UI and spoken aloud via pyttsx3 TTS. Errors like "Ollama not running" are caught and surfaced as user-friendly messages.

## GPU-Aware Model Loading

The system checks `torch.cuda.is_available()` at startup to select the appropriate YOLO model:

- **CUDA available**: `yolo11x-pose.pt` — Extra Large model for maximum accuracy
- **CPU only**: `yolo11n-pose.pt` — Nano model for speed on modest hardware

This lets the same codebase run on a gaming desktop with a GPU or on a laptop with integrated graphics, adapting automatically.
