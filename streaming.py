import cv2
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import os

app = FastAPI()

# Folder containing saved videos
VIDEO_FOLDER = "/apps/packmat_pwani_updated/Pwani_packmat_/outputs"

os.makedirs(VIDEO_FOLDER, exist_ok=True)


def generate_frames(video_path):
    """Generator that streams frames from a saved video file."""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    while True:
        ret, img = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        )


@app.get("/{video_filename}")
async def stream_video(video_filename: str):
    """
    Stream frames from any video file in VIDEO_FOLDER.
    No restart required when new files are added.
    """
    video_path = os.path.join(VIDEO_FOLDER, video_filename)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    return StreamingResponse(
        generate_frames(video_path),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/list_videos")
async def list_videos():
    """List all available MP4 files."""
    files = [f for f in os.listdir(VIDEO_FOLDER) if f.lower().endswith(".mp4")]
    return {"videos": files}


@app.get("/test")
async def test():
    return JSONResponse({"Hello": "World"})

 
