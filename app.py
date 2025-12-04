from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import eventlet
import base64
import json
from api import VideoProcessor

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Global Video Processor
processor = None

def on_frame(jpeg_bytes):
    """Callback for video frames."""
    # Convert to base64 for Socket.IO
    # Note: For high FPS, MJPEG stream is often better, but Socket.IO is easier for sync.
    # Let's try base64 first.
    b64_frame = base64.b64encode(jpeg_bytes).decode('utf-8')
    socketio.emit('video_frame', {'image': b64_frame})

def on_stats(reps, stage, feedback, progress):
    """Callback for stats."""
    socketio.emit('stats_update', {
        'reps': reps,
        'stage': stage,
        'feedback': feedback,
        'progress': progress
    })

def on_ai_feedback(text):
    """Callback for AI Coach."""
    socketio.emit('ai_feedback', {'text': text})

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global processor
    print('Client connected')
    if processor is None:
        processor = VideoProcessor(
            callback_stats=on_stats,
            callback_ai=on_ai_feedback
        )

@socketio.on('process_frame')
def handle_process_frame(data):
    global processor
    if processor:
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        
        # Process frame
        annotated_bytes = processor.process_frame(image_data)
        
        if annotated_bytes:
            # Encode back to base64
            b64_annotated = base64.b64encode(annotated_bytes).decode('utf-8')
            emit('annotated_frame', {'image': b64_annotated})

@socketio.on('change_exercise')
def handle_exercise_change(data):
    global processor
    if processor:
        exercise = data.get('exercise', 'Squat')
        print(f"Changing exercise to: {exercise}")
        processor.set_exercise(exercise)

if __name__ == '__main__':
    print("Starting Flask-SocketIO Server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
