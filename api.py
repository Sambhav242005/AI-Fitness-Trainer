import cv2
import numpy as np
import torch
from PyQt6.QtCore import QThread, pyqtSignal
from ultralytics import YOLO
from engine import RepCounter

# --- WORKER THREAD: YOLO INFERENCE ---
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    stats_signal = pyqtSignal(int, str, str, float) # Reps, Stage, Feedback, Progress
    device_signal = pyqtSignal(str) # New signal for device info

    def __init__(self):
        super().__init__()
        self._run_flag = True
        
        # Check for GPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        
        # Select model based on device
        if self.device == 'cuda':
            model_path = 'models/yolo11x-pose.pt'
            self.model_info = "CUDA (GPU) - Model: X (High Acc)"
            print("CUDA available: Using Extra Large model (X) for maximum accuracy.")
        else:
            model_path = 'models/yolo11n-pose.pt'
            self.model_info = "CPU - Model: Nano (Fast)"
            print("CUDA not available: Using Nano model (N) for speed.")
            
        self.model = YOLO(model_path)
        self.model.to(self.device)
        self.exercise_type = "Squat"
        self.counter = RepCounter("Squat")

    def set_exercise(self, exercise):
        self.exercise_type = exercise
        self.counter = RepCounter(exercise)

    def run(self):
        # Emit device info once at start
        self.device_signal.emit(self.model_info)
        
        # Capture from webcam (0)
        cap = cv2.VideoCapture(0)
        
        while self._run_flag:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Run YOLO Inference
            # verbose=False prevents console spam
            results = self.model(frame, verbose=False, conf=0.5)
            
            # Annotate frame
            annotated_frame = results[0].plot(boxes=False) # Draw skeleton only
            
            # Extract Keypoints for Logic
            try:
                # keypoints.data is shape (1, 17, 3) -> Batch, Points, (x,y,conf)
                keypoints = results[0].keypoints.data[0].cpu().numpy()
                
                # Convert to dict for easier access {index: (x,y)}
                # Map: 5=L_Shoulder, 7=L_Elbow, 9=L_Wrist, 11=L_Hip, 13=L_Knee, 15=L_Ankle
                lm_dict = {}
                for idx, kp in enumerate(keypoints):
                    x, y, conf = kp
                    if conf > 0.5: # Only trust confident points
                        lm_dict[idx] = (int(x), int(y))
                
                # Process Reps
                reps, stage, feedback, progress = self.counter.process(lm_dict)
                self.stats_signal.emit(reps, stage, feedback, progress)
                
                # Visual Overlays specific to form
                if self.exercise_type == "Squat" and 13 in lm_dict:
                    # Draw "Depth Line" at knee height
                    knee_y = lm_dict[13][1]
                    # Use the threshold to show where the hip needs to be
                    target_y = int(knee_y * self.counter.squat_depth_thresh)
                    
                    cv2.line(annotated_frame, (0, target_y), (frame.shape[1], target_y), (0, 255, 255), 2)
                    cv2.putText(annotated_frame, "Target Depth", (10, target_y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                # Draw Progress Bar on Video
                # Bottom of screen
                h, w, _ = annotated_frame.shape
                bar_x = 50
                bar_y = h - 40
                bar_w = w - 100
                bar_h = 20
                
                # Background
                cv2.rectangle(annotated_frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
                # Fill
                fill_w = int(bar_w * progress)
                cv2.rectangle(annotated_frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (0, 255, 0), -1)

            except Exception as e:
                # Usually happens if no person is detected
                pass
            
            self.change_pixmap_signal.emit(annotated_frame)
            
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()
