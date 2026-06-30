---
contentKind: article
slug: dual-arm-hysteresis-bicep-curl
title: Preventing Flicker with Dual-Arm Hysteresis in Bicep Curl Tracking
type: technical-note
status: published
date: 2026-06-15
summary: How a ±20° hysteresis bias stabilizes rep counting when both arms are visible during alternating bicep curl sets.
tags:
  - Hysteresis
  - State Machine
  - Pose Estimation
  - Bicep Curl
  - Computer Vision
---

## The Problem

During bicep curls, users frequently alternate arms between reps. When both arms are visible to the camera, a naive "pick the smaller angle" heuristic causes the tracked arm to flicker rapidly — both elbows hover around similar angles near full extension, and tiny pose estimation jitter flips the active selection back and forth. This produces phantom reps and erratic feedback that ruins the user experience.

## The Solution: Hysteresis Bias

The `RepCounter._process_curl` method in `engine.py` implements a hysteresis mechanism: a ±20° bias toward the last active arm. The rule is simple:

- If the right arm was active last, the left arm must be **at least 20° more curled** to take over.
- If the left arm was active last, the right arm needs the same margin.

This creates a dead zone around the switching point — small fluctuations in joint angle won't cross the hysteresis barrier, so the active arm stays stable.

## Implementation Details

```python
self.last_side = None  # Tracks which arm was last used

# Both arms visible
if l_visible and r_visible:
    angle_l = PoseMath.calculate_angle(l_sh, l_el, l_wr)
    angle_r = PoseMath.calculate_angle(r_sh, r_el, r_wr)

    bias = 20

    if self.last_side == "Right":
        if angle_l < angle_r - bias:
            # Left significantly more curled — switch
            active_side = "Left"
        else:
            # Stay with right
            active_side = "Right"
    else:
        if angle_r < angle_l - bias:
            active_side = "Right"
        else:
            active_side = "Left"
```

The bias value of 20° was tuned empirically. Too small (< 10°) and flickering returns on slow concentric movements. Too large (> 30°) and the system feels sluggish when the user genuinely switches arms between sets. At 20°, the dead zone is wide enough to absorb YOLO keypoint jitter (~5-8° at 640×480 resolution with `yolo11n-pose`) but narrow enough that a deliberate arm switch crossing a full range of motion (~100° change) gets picked up within one or two frames.

## Single-Arm Fallback

When only one arm is visible (side-on camera angle, partial occlusion), the hysteresis logic is bypassed entirely — the system tracks whichever arm it can see. This makes the dual-arm tracking robust to varied camera setups while only adding complexity when it's needed.

## Why This Matters for AI Fitness

Rep counting is a state machine problem at heart, but the real-world challenge is sensor noise and ambiguous input. Hysteresis is a simple, stateless fix that avoids more expensive solutions like temporal smoothing filters or Kalman predictors. It keeps the codebase small (`engine.py` is 243 lines total) and the logic transparent — every rep transition is explainable from the raw keypoint angles and the last known state.
