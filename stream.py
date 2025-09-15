import cv2
import os
from flask import Flask, Response, jsonify

# Flask app setup
app = Flask(__name__)

VIDEO_FOLDER = "/apps/packmat_pwani_updated/Pwani_packmat_/outputs"
os.makedirs(VIDEO_FOLDER, exist_ok=True)


def resize_frame(frame, target_height):
    h, w = frame.shape[:2]
    aspect_ratio = w / h
    new_w = int(target_height * aspect_ratio)
    return cv2.resize(frame, (new_w, target_height), interpolation=cv2.INTER_AREA)


def generate_frames(video_path):
    """Video streaming generator function."""
    print(f"[DEBUG] Opening video: {video_path}")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {video_path}")
        return  # Stop generator if video can't be opened

    print(f"[INFO] Streaming started for: {video_path}")

    while True:
        ret, img = cap.read()
        if not ret:
            print(f"[DEBUG] Rewinding video: {video_path}")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Encode as JPEG
        success, buffer = cv2.imencode('.jpg', img)
        if not success:
            print(f"[ERROR] Frame encoding failed for {video_path}")
            continue

        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Dynamically register routes for all .mp4 files in folder
for file in os.listdir(VIDEO_FOLDER):
    if file.lower().endswith(".mp4"):
        filename = os.path.splitext(file)[0]  # Remove .mp4
        video_path = os.path.join(VIDEO_FOLDER, file)

        def make_route(path):
            def route():
                print(f"[DEBUG] Route hit for: {path}")
                return Response(generate_frames(path),
                                mimetype='multipart/x-mixed-replace; boundary=frame')
            return route

        # Register endpoint like /cam_5
        app.add_url_rule(f"/{filename}", endpoint=filename, view_func=make_route(video_path))
        print(f"[INFO] Added route: /{filename} -> {video_path}")


@app.route('/')
def index():
    """Show all available routes."""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule))
    return jsonify({"available_routes": routes})


@app.route('/test')
def hello_world():
    return jsonify({"Hello": "World"})


# Debug route: test if OpenCV can open one video
@app.route('/video')
def video_check():
    test_file = os.path.join(VIDEO_FOLDER, "cam_5_2025-09-11_15-30-23_output.mp4")
    cap = cv2.VideoCapture(test_file)
    opened = cap.isOpened()
    cap.release()
    return jsonify({"opened": opened, "path": test_file})


# Fallback manual stream for debugging
@app.route('/stream')
def stream():
    test_file = os.path.join(VIDEO_FOLDER, "cam_5_2025-09-11_15-30-23_output.mp4")
    print(f"[DEBUG] /stream requested for {test_file}")
    return Response(generate_frames(test_file),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(port=5009, host="0.0.0.0", debug=True)
