import os
import cv2
import base64
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE = os.getenv("LM_STUDIO_API_BASE", "http://localhost:11434/v1")
API_KEY = os.getenv("LM_STUDIO_API_KEY", "ollama")
MODEL_NAME = os.getenv("AI_MODEL", "qwen3-vl:latest")

# Initialize OpenAI Client (LM Studio compatibility)
client = OpenAI(base_url=API_BASE, api_key=API_KEY)

def encode_image(frame):
    """Encodes an OpenCV frame to a base64 string."""
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")

def analyze_frame(frame, prompt="Describe what you see in this image. Is the person exercising?"):
    """Sends the frame to the Vision Model for analysis."""
    base64_image = encode_image(frame)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME, # Use configured model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=100,
        )
        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg or "404" in error_msg:
            return "Error: Is Ollama running? Check connection."
        return f"AI Error: {error_msg[:50]}..."

if __name__ == "__main__":
    print(f"Connecting to Vision Model at: {API_BASE}")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print("Press 'Space' to capture and analyze. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("AI Vision Feed", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '): # Space bar
            print("Analyzing frame...")
            # Resize for faster transmission (optional)
            resized_frame = cv2.resize(frame, (640, 480))
            description = analyze_frame(resized_frame)
            print(f"\nAI Analysis:\n{description}\n")
            
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
