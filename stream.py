import cv2
from flask import Flask, Response, jsonify
import os

app = Flask(__name__)

# 📂 Folder containing your saved videos
VIDEO_FOLDER = "/apps/packmat_pwani_updated/Pwani_packmat_/outputs"
os.makedirs(VIDEO_FOLDER, exist_ok=True)


def generate_frames(video_path):
    """Generator that streams frames from a saved video file."""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    while cap.isOpened():
        ret, img = cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # 🔁 Loop the video
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


def add_video_route(video_filename):
    """
    Adds a streaming route for the given video file.
    Route will look like: http://<ip>:5006/<video_filename>
    """
    video_path = os.path.join(VIDEO_FOLDER, video_filename)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    route_path = f"/{video_filename}"

    # Define the Flask route dynamically
    def route_func(path=video_path):
        return Response(generate_frames(path),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    # Avoid duplicate route registration
    if route_path not in [rule.rule for rule in app.url_map.iter_rules()]:
        app.add_url_rule(route_path, video_filename, route_func)

    return f"http://192.168.5.82:5006{route_path}"


@app.route('/test')
def hello_world():
    return jsonify({"Hello": "World"})


if __name__ == "__main__":
    # Example: Register all videos inside "videos" folder automatically
    for file in os.listdir(VIDEO_FOLDER):
        if file.lower().endswith(".mp4"):
            link = add_video_route(file)
            print(f"🎥 Streaming URL: {link}")

    app.run(port=5009, host='0.0.0.0')
