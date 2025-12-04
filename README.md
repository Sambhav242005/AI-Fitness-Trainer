# AI Fitness Trainer

A smart fitness assistant that uses Computer Vision (YOLOv11) and Generative AI (Ollama) to track your reps and analyze your form in real-time.

## Features

- **Real-time Rep Counting**: Tracks Squats, Bicep Curls, and Pushups.
- **Form Analysis**: Uses YOLOv11 Pose Estimation to check depth and extension.
- **AI Coach**: Periodically captures your form and asks a Vision LLM (via Ollama) for specific advice.
- **Voice Feedback**: Speaks corrections and encouragement aloud.
- **Web Interface**: Runs in your browser with client-side camera access.
- **Privacy Focused**: All processing runs locally on your machine.

## Prerequisites

1. **Python 3.10+**
2. **Ollama**: For the AI Vision features.
    - Download from [ollama.com](https://ollama.com)
    - Pull the vision model:

        ```bash
        ollama pull qwen3-vl:latest
        ```

3. **CUDA (Optional)**: For faster YOLO inference on NVIDIA GPUs.

## Installation

1. Clone the repository.
2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Start Ollama** (if not running).
2. **Run the App**:

    ```bash
    python app.py
    ```

3. **Open Browser**:
    Go to `http://localhost:5000`
4. **Start Workout**:
    - Click **"Start Camera"**.
    - Select your exercise from the dropdown.
    - Step back and start moving!

## Troubleshooting

- **"Error: Is Ollama running?"**: Make sure Ollama is started and listening on port 11434.
- **Camera not working**: Ensure you allowed camera permissions in your browser.
- **Slow Performance**:
  - If you have an NVIDIA GPU, ensure you installed the CUDA version of PyTorch.
  - The app automatically switches to a faster "Nano" model if no GPU is found.

## Project Structure

- `app.py`: Flask Web Server.
- `api.py`: Core logic (Video Processing, AI Trigger).
- `engine.py`: Exercise counting and geometry logic.
- `ai.py`: Interface for Ollama (Vision API).
- `tts.py`: Text-to-Speech handler.
- `templates/index.html`: Web Frontend.
