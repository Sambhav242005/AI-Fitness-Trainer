import sys
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QFrame, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap, QFont
from api import VideoThread

# --- UI LAYER: PYQT6 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO11 AI Fitness Trainer")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left Side: Video Feed
        self.video_label = QLabel("Camera Loading...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #444; background-color: #000; color: #888; font-size: 20px;")
        
        # Right Side: Controls & Stats
        stats_panel = QFrame()
        stats_panel.setFixedWidth(300)
        stats_panel.setStyleSheet("background-color: #333; border-radius: 10px; padding: 10px;")
        stats_layout = QVBoxLayout()
        
        # Title
        title = QLabel("TRAINER DASHBOARD")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Exercise Selector
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Squat", "Bicep Curl", "Push Up"])
        self.combo_box.setFont(QFont("Arial", 12))
        self.combo_box.setStyleSheet("padding: 5px; background-color: #555;")
        self.combo_box.currentTextChanged.connect(self.change_exercise)

        # Exercise Image Guide (New Feature)
        self.exercise_image_label = QLabel("Exercise Guide")
        self.exercise_image_label.setFixedSize(280, 160)
        self.exercise_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exercise_image_label.setStyleSheet("border: 1px dashed #666; background-color: #222; color: #aaa;")
        
        # Rep Counter Display
        self.rep_label = QLabel("0")
        self.rep_label.setFont(QFont("Arial", 80, QFont.Weight.Bold))
        self.rep_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rep_label.setStyleSheet("color: #00ff00;")
        
        rep_text = QLabel("REPS")
        rep_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rep_text.setFont(QFont("Arial", 14))

        # Feedback Display
        self.feedback_label = QLabel("Get Ready")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.feedback_label.setStyleSheet("color: #ffcc00; border: 1px solid #555; padding: 10px;")

        # Assemble Right Panel
        stats_layout.addWidget(title)
        stats_layout.addSpacing(20)
        stats_layout.addWidget(QLabel("Select Exercise:"))
        stats_layout.addWidget(self.combo_box)
        stats_layout.addSpacing(10)
        stats_layout.addWidget(self.exercise_image_label) # Added image
        stats_layout.addSpacing(20)
        stats_layout.addWidget(self.rep_label)
        stats_layout.addWidget(rep_text)
        stats_layout.addSpacing(20)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("QProgressBar {border: 2px solid grey; border-radius: 5px; text-align: center;} QProgressBar::chunk {background-color: #00ff00; width: 20px;}")
        stats_layout.addWidget(QLabel("Rep Progress:"))
        stats_layout.addWidget(self.progress_bar)
        
        stats_layout.addSpacing(20)
        stats_layout.addWidget(QLabel("Live Feedback:"))
        stats_layout.addWidget(self.feedback_label)
        
        stats_layout.addStretch()
        
        # Device Status Label
        self.device_label = QLabel("Loading Model...")
        self.device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.device_label.setStyleSheet("color: #888; font-size: 10px;")
        stats_layout.addWidget(self.device_label)
        
        stats_panel.setLayout(stats_layout)

        # Add to Main Window
        main_layout.addWidget(self.video_label)
        main_layout.addWidget(stats_panel)

        # Init First Image
        self.update_exercise_image("Squat")

        # Start Video Thread
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.stats_signal.connect(self.update_stats)
        self.thread.device_signal.connect(self.update_device_status)
        self.thread.start()

    def change_exercise(self, text):
        self.thread.set_exercise(text)
        self.rep_label.setText("0")
        self.feedback_label.setText("Switching...")
        self.update_exercise_image(text)

    def update_exercise_image(self, exercise_name):
        """Loads an image based on exercise name. Uses placeholder if missing."""
        # Clean name for file path (e.g. "Bicep Curl" -> "bicep_curl")
        filename = exercise_name.lower().replace(" ", "_") + ".png"
        
        # Path to assets folder
        assets_path = os.path.join("assets", filename)
        
        # Attempt to load
        if os.path.exists(assets_path):
            pixmap = QPixmap(assets_path)
            self.exercise_image_label.setPixmap(pixmap.scaled(280, 160, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            # Fallback text if image missing
            self.exercise_image_label.setText(f"Image not found:\n{assets_path}")
            self.exercise_image_label.setStyleSheet("border: 1px dashed #666; background-color: #222; color: #aaa;")

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.video_label.setPixmap(qt_img)
        
    @pyqtSlot(str)
    def update_device_status(self, info):
        self.device_label.setText(info)

    @pyqtSlot(int, str, str, float)
    def update_stats(self, reps, stage, feedback, progress):
        self.rep_label.setText(str(reps))
        self.feedback_label.setText(feedback)
        self.progress_bar.setValue(int(progress * 100))
        
        # Color coding feedback
        if "Good" in feedback:
            self.feedback_label.setStyleSheet("color: #00ff00; border: 1px solid #555; padding: 10px;")
        elif "Deep" in feedback or "Lower" in feedback:
            self.feedback_label.setStyleSheet("color: #ff0000; border: 1px solid #555; padding: 10px;")
        else:
            self.feedback_label.setStyleSheet("color: #ffcc00; border: 1px solid #555; padding: 10px;")

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()
