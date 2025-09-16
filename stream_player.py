import os
import subprocess
from flask import Flask, abort, send_from_directory

# Flask app setup
app = Flask(__name__)

# Original and encoded folders
VIDEO_FOLDER = "/apps/packmat_pwani_updated/Pwani_packmat_/outputs"
ENCODED_FOLDER = "/apps/packmat_pwani_updated/Pwani_packmat_/encoded"
#VIDEO_FOLDER = "/home/dvio/Desktop/packmat/Pwani_packmat_-main/outputs"
#ENCODED_FOLDER = "/home/dvio/Desktop/packmat/Pwani_packmat_-main/encoded"
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(ENCODED_FOLDER, exist_ok=True)


def reencode_video(input_file, output_file):
    """
    Re-encode video into H.264 + AAC and save to encoded folder.
    """
    print(f"[INFO] Re-encoding {os.path.basename(input_file)} -> {output_file}")

    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    return output_file if os.path.exists(output_file) else None


@app.route('/videos/<path:filename>')
def serve_video(filename):
    """
    Re-encode on every request and serve encoded video.
    """
    input_path = os.path.join(VIDEO_FOLDER, filename)
    output_path = os.path.join(ENCODED_FOLDER, filename)

    # Prevent directory traversal
    if not os.path.abspath(input_path).startswith(os.path.abspath(VIDEO_FOLDER)):
        abort(403)

    if not os.path.isfile(input_path):
        abort(404)

    # Always re-encode before serving
    reencode_video(input_path, output_path)

    return send_from_directory(
        ENCODED_FOLDER,
        filename,
        mimetype="video/mp4",
        as_attachment=False
    )


@app.route('/')
def index():
    """
    Show all videos with HTML5 players and download buttons.
    """
    files = [f for f in os.listdir(VIDEO_FOLDER) if f.lower().endswith(".mp4")]

    html = """
    <html>
    <head>
        <title>Video Player</title>
    </head>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <h1>Available Videos (Encoded on Request)</h1>
    """

    if not files:
        html += "<p>No MP4 files found in the folder.</p>"

    for f in files:
        url = f"/videos/{f}"
        html += f"""
        <div style='margin-bottom:40px;'>
            <p><b>{f}</b></p>
            <video width="640" controls>
                <source src="{url}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <br>
            <a href="{url}" download="{f}">
                <button style="margin-top: 10px; padding: 8px 16px; font-size: 14px;">
                    ⬇ Download
                </button>
            </a>
        </div>
        """

    html += "</body></html>"
    return html


if __name__ == "__main__":
    app.run(port=5009, host="192.168.5.82", debug=True)
