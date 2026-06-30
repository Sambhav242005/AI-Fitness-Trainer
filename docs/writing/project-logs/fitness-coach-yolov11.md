---
contentKind: article
slug: fitness-coach-yolov11
title: Local AI Fitness Coaching with YOLOv11
type: project-log
status: published
date: 2026-05-28
summary: Building a privacy-first fitness tracker utilizing browser camera feeds, keypoint math, and local Vision LLM feedback.
tags:
  - YOLOv11
  - Ollama
  - Pose Estimation
---

Fitness applications typically count repetitions based on simple timers or accelerometer changes, which fail to evaluate if a user is performing the exercise correctly. I built a local fitness coach that combines real-time coordinate math with a Vision LLM for detailed form correction.

## Keypoint Extraction & Joint Geometry

Using YOLOv11-pose, the application extracts 17 body keypoints from the webcam stream. We calculate joint angles in real time using 2D vector geometry. For instance, the knee flex angle is calculated by taking keypoints for the hip (A), knee (B), and ankle (C):

- Vector BA = (xA - xB, yA - yB)
- Vector BC = (xC - xB, yC - yB)
- Angle = arccos( (Vector BA dot Vector BC) / (norm(BA) * norm(BC)) )

## State Machine Rep Counting

To avoid false counts due to jitter, the system uses a two-threshold state machine. For squats, a rep is initiated when the knee angle drops below 90 degrees (deep squat) and completes only when it returns above 160 degrees (full extension).

## Form Feedback Loop via local Vision LLMs

When keypoint calculations detect a form error (e.g. knees passing toes during squats), the flask backend captures the video frame and feeds it to a local `qwen3-vl:latest` model via Ollama. The model analyzes the form and returns concrete correction advice, which is spoken aloud using the browser's Web Speech API.
