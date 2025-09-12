import cv2
import os
from flask import Flask, Response, jsonify
from dotenv import load_dotenv

# ---------------- Load Environment Variables ---------------- #
load_dotenv()

VIDEO_FOLDER = os.getenv("VIDEO_FOLDER")
HOST = os.getenv("FLASK_HOST")  # fallback localhost
PORT = int(os.getenv("FLASK_PORT"))

# ---------------- Flask App Setup ---------------- #
app = Flask(__name__)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

def resize_frame(frame, target_height):
    h, w = frame.shape[:2]
    aspect_ratio = w / h
    new_w = int(target_height * aspect_ratio)
    return cv2.resize(frame, (new_w, target_height), interpolation=cv2.INTER_AREA)

def generate_frames(video_path):
    """Video streaming generator function."""
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, img = cap.read()
        if ret:
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video

# ---------------- Register Routes Dynamically ---------------- #
for file in os.listdir(VIDEO_FOLDER):
    if file.lower().endswith(".mp4"):
        filename = os.path.splitext(file)[0]
        video_path = os.path.join(VIDEO_FOLDER, file)

        def make_route(path=video_path):
            return lambda: Response(
                generate_frames(path),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )

        app.add_url_rule(f"/{filename}", filename, make_route())

@app.route('/test')
def hello_world():
    return jsonify({"Hello": "World"})

if __name__ == "__main__":
    app.run(port=PORT, host=HOST)
