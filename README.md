# YOLO11 AI Fitness Trainer

An AI-powered fitness trainer application that uses computer vision to track exercises, count reps, and provide real-time form feedback.

## Features

- **Real-time Pose Estimation**: Uses YOLO11-pose for accurate body tracking.
- **Exercise Tracking**: Supports Squats, Bicep Curls, and Push Ups.
- **Form Feedback**: Provides visual and text feedback on form (e.g., "Go Deeper", "Extend Fully").
- **Rep Counting**: Automatically counts repetitions based on movement mechanics.
- **Active Arm Detection**: Automatically detects which arm is being used for single-arm exercises like curls.

## Project Structure

- `run.py`: Entry point of the application.
- `ui.py`: Handles the User Interface (PyQt6).
- `engine.py`: Contains the core logic for exercise analysis and rep counting.
- `api.py`: Manages the video processing thread and AI inference.
- `assets/`: Contains image resources.
- `models/`: Contains the YOLO model files.

## Setup

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Run the application:

    ```bash
    python run.py
    ```

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended for performance)
