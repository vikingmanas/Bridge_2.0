import os
import re
import base64
import cv2
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO
from PIL import Image
from io import BytesIO
import eventlet  # Required for async server

# =========================
# FLASK + SOCKETIO SETUP
# =========================
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "bridge-hackathon-secret"
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    """Serve frontend HTML."""
    return render_template("index.html")

# =========================
# SOCKET HANDLERS
# =========================
@socketio.on("connect")
def handle_connect():
    print("✅ Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("❌ Client disconnected")

@socketio.on("text_to_sign")
def handle_text_to_sign(text):
    """
    Handle text → sign request.
    For MVP: returns a list of avatar animations or videos.
    Later: connect to 3D avatar renderer.
    """
    print(f"[TEXT_TO_SIGN] Received: {text}")
    words = re.sub(r"[^\w\s]", "", text).lower().split()

    # For now: just send back video paths stored in /static/signs
    video_paths = []
    signs_dir = os.path.join("static", "signs")

    for word in words:
        for ext in [".mp4", ".webm", ".gif"]:
            file_path = os.path.join(signs_dir, f"{word}{ext}")
            if os.path.exists(file_path):
                video_paths.append(f"/static/signs/{word}{ext}")
                break

    if video_paths:
        socketio.emit("sign_video_sequence", video_paths)
    else:
        socketio.emit("sign_video_sequence", [])

@socketio.on("video_frame")
def handle_video_frame(data_url):
    """
    Handle camera frames → recognition.
    For now: just receives frames.
    Later: connect ML model for sign recognition.
    """
    try:
        image_data = base64.b64decode(data_url.split(",")[1])
        frame = cv2.cvtColor(np.array(Image.open(BytesIO(image_data))), cv2.COLOR_RGB2BGR)

        # Placeholder recognition (replace with ML)
        dummy_prediction = "hello"
        socketio.emit("translation", dummy_prediction)

    except Exception as e:
        print(f"[ERROR processing frame] {e}")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("🚀 Starting Bridge backend on http://127.0.0.1:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
