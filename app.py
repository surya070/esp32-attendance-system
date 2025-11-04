"""
app.py — ESP32-CAM Face Attendance WebApp (Enhanced)
---------------------------------------------------
• ESP32 posts images to /upload
• RetinaFace + DeepFace for detection & recognition
• Flask frontend: live feed + attendance viewer
• Shows best match name + distance on frame
"""

from flask import Flask, request, Response, render_template, send_file
from deepface import DeepFace
from retinaface import RetinaFace
import cv2, numpy as np, pickle, csv, os, time
from datetime import datetime
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
MODEL_NAME = "ArcFace"
EMBEDDINGS_PATH = "models/embeddings.pkl"
LOG_FILE = "attendance_log.csv"
THRESHOLD = 4.0  # smaller = stricter

# -----------------------------
# FLASK SETUP
# -----------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")

# Load embeddings
with open(EMBEDDINGS_PATH, "rb") as f:
    embeddings_db = pickle.load(f)
print(f"[INFO] Loaded embeddings for {len(embeddings_db)} people")

# Ensure attendance file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["Name", "Date", "Time"])
logged_today = set()

latest_frame = None  # store latest processed frame for preview


# -----------------------------
# HELPERS
# -----------------------------
def find_best_match(emb):
    best_name, best_dist = "Unknown", float("inf")
    for name, ref_emb in embeddings_db.items():
        dist = np.linalg.norm(emb - np.array(ref_emb, dtype=np.float32))
        if dist < best_dist:
            best_dist, best_name = dist, name
    return (best_name if best_dist <= THRESHOLD else "Unknown"), best_dist


def log_attendance(name):
    today = datetime.now().strftime("%Y-%m-%d")
    if (name, today) in logged_today or name == "Unknown":
        return
    time_now = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([name, today, time_now])
    logged_today.add((name, today))
    print(f"[ATTEND] {name} at {time_now}")


# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def index():
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        today = datetime.now().strftime("%Y-%m-%d")
        count_today = len(df[df["Date"] == today])
    else:
        count_today = 0
    return render_template("index.html", count_today=count_today)


@app.route("/upload", methods=["POST"])
def upload():
    """Receive image from ESP32-CAM via HTTP POST."""
    global latest_frame
    try:
        file_bytes = request.data
        np_arr = np.frombuffer(file_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            return "Invalid image", 400

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        try:
            faces = RetinaFace.detect_faces(rgb)
        except Exception as e:
            print(f"[WARN] Detection failed: {e}")
            faces = {}

        if isinstance(faces, dict):
            for _, face_data in faces.items():
                x1, y1, x2, y2 = face_data["facial_area"]
                face_crop = rgb[y1:y2, x1:x2]
                if face_crop.size == 0:
                    continue

                rep = DeepFace.represent(
                    face_crop,
                    model_name=MODEL_NAME,
                    detector_backend="skip",
                    enforce_detection=False,
                )[0]["embedding"]

                emb = np.array(rep, dtype=np.float32)
                name, dist = find_best_match(emb)
                log_attendance(name)

                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                label = f"{name} ({dist:.2f})"
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                )

        latest_frame = frame
        return "OK", 200

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return "Error", 500


@app.route("/video_feed")
def video_feed():
    """Live preview of the latest processed frame."""
    def gen():
        global latest_frame
        while True:
            if latest_frame is not None:
                ret, buffer = cv2.imencode(".jpg", latest_frame)
                frame_bytes = buffer.tobytes()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
            time.sleep(0.1)

    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/attendance")
def attendance():
    """Display attendance table."""
    if not os.path.exists(LOG_FILE):
        return render_template("attendance.html", records=[])
    df = pd.read_csv(LOG_FILE)
    records = df.to_dict(orient="records")
    return render_template("attendance.html", records=records)


@app.route("/download")
def download():
    """Download the attendance CSV."""
    return send_file(LOG_FILE, as_attachment=True)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 Flask server running at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
