---
contentKind: article
slug: local-vision-llm-pipeline
title: Running a Vision LLM Locally for Real-Time Fitness Form Analysis
type: technical-note
status: published
date: 2026-06-20
summary: How the AI Fitness Trainer triggers Ollama + Qwen3-VL every 5 reps to deliver spoken form coaching — all on-device with no cloud dependencies.
tags:
  - Ollama
  - Qwen3-VL
  - Vision LLM
  - Privacy
  - Python
---

## Motivation

Form feedback in fitness tracking often falls into two extremes: simple heuristics (did the knee angle go below 90°) that miss nuance, or cloud-based AI analysis that streams video to third-party servers. For a privacy-first fitness trainer, neither works. The solution is a locally-hosted vision language model that runs on the same machine as the camera and pose estimation pipeline.

## Architecture

The AI trigger is coordinated by the `VideoProcessor` in `api.py`. Every 5 completed reps, a background thread is spawned to avoid blocking real-time frame processing:

```python
if reps > 0 and reps % self.trigger_interval == 0 and reps != self.last_rep_count:
    self.last_rep_count = reps
    threading.Thread(
        target=self.run_ai_analysis,
        args=(frame.copy(), self.exercise_type, reps)
    ).start()
```

The `run_ai_analysis` method then:
1. Notifies the UI that analysis is beginning
2. Speaks "Analyzing your form, please wait" via pyttsx3
3. Constructs a prompt with the exercise type and current rep count
4. Calls the Ollama API at `localhost:11434/v1`
5. Displays the response in the UI as cyan italic text
6. Speaks the tip aloud

## The Vision LLM Client

The `ai.py` module wraps the OpenAI Python SDK configured to point at Ollama's local API:

```python
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
```

Frames are JPEG-encoded and base64-encoded before being sent inline:

```python
response = client.chat.completions.create(
    model="qwen3-vl:latest",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }},
        ],
    }],
    max_tokens=100,
)
```

The `max_tokens=100` constraint forces short, actionable tips — no rambling. The model is instructed to give "one specific tip" in a single sentence, which keeps TTS latency manageable.

## Error Handling

The client catches connection errors gracefully. If Ollama isn't running or the model isn't loaded, the error message is presented as user-friendly UI text rather than a stack trace:

```python
except Exception as e:
    if "Connection refused" in str(e):
        return "Error: Is Ollama running? Check connection."
    return f"AI Error: {str(e)[:50]}..."
```

## Why Every 5 Reps?

Running vision LLM inference on every frame would be prohibitively slow (Qwen3-VL takes 2-5 seconds per analysis on consumer hardware) and expensive in terms of battery and GPU cycles. The 5-rep interval gives users regular feedback without overwhelming the system:

- At 10 reps, the user gets the first tip
- At 15 reps, a second tip
- And so on

This cadence matches how a human coach would give feedback — not on every rep, but periodically to reinforce good habits.

## Privacy Guarantee

The entire pipeline — camera capture, YOLO inference, angle calculation, LLM call, and TTS — runs on the local machine. The only network traffic is to Ollama's localhost API server. No pixel data, keypoint coordinates, or form analysis results ever leave the device. This makes the system suitable for home use without concerns about video streaming to external services.
