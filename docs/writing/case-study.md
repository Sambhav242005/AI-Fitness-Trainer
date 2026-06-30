---
contentKind: case-study
---

## Problem

Workout apps often count reps without understanding form, while good form feedback usually requires a human coach.

## Approach

I built a browser-based local assistant that uses camera input, YOLOv11 pose estimation, exercise-specific geometry, and a local vision LLM to provide feedback.

## Technical Decisions

- Flask serves the web interface and backend routes.
- YOLOv11 pose estimation tracks squats, bicep curls, and pushups.
- Geometry logic evaluates depth, extension, and rep transitions.
- Ollama vision analysis periodically reviews captured form.
- Text-to-speech turns corrections into real-time coaching.

## Result

The project demonstrates practical AI product integration: CV inference, local LLM calls, browser camera workflow, privacy-preserving local processing, and user feedback loops.
