"""
build_embeddings.py
-------------------
Scans the `database/` folder for subfolders (each representing a person).
Uses RetinaFace for face detection + alignment and DeepFace (ArcFace) for embeddings.
Averages multiple embeddings per person for robust recognition.
"""

from deepface import DeepFace
from retinaface import RetinaFace
import numpy as np
import cv2
import os
import pickle

# -----------------------------
# CONFIG
# -----------------------------
DATABASE_PATH = "database"
MODEL_NAME = "ArcFace"
EMBED_SAVE_PATH = "models/embeddings.pkl"

# Create models folder if missing
os.makedirs("models", exist_ok=True)

def extract_face_retina(image_path):
    """Detect, align, and crop face using RetinaFace."""
    img = cv2.imread(image_path)
    if img is None:
        print(f"[WARN] Could not read {image_path}")
        return None

    try:
        faces = RetinaFace.detect_faces(img)
        if not isinstance(faces, dict) or len(faces) == 0:
            print(f"[WARN] No face detected in {image_path}")
            return None

        # Pick the largest detected face
        key = max(faces.keys(), key=lambda k: 
                  (faces[k]["facial_area"][2] - faces[k]["facial_area"][0]) *
                  (faces[k]["facial_area"][3] - faces[k]["facial_area"][1]))

        x1, y1, x2, y2 = faces[key]["facial_area"]
        face_crop = img[y1:y2, x1:x2]

        if face_crop.size == 0:
            print(f"[WARN] Empty crop in {image_path}")
            return None

        # Optional: normalize lighting
        face_yuv = cv2.cvtColor(face_crop, cv2.COLOR_BGR2YUV)
        face_yuv[:, :, 0] = cv2.equalizeHist(face_yuv[:, :, 0])
        face_crop = cv2.cvtColor(face_yuv, cv2.COLOR_YUV2BGR)

        return face_crop

    except Exception as e:
        print(f"[ERROR] RetinaFace failed on {image_path}: {e}")
        return None

def get_embedding(face_img):
    """Compute DeepFace embedding for one face."""
    try:
        rep = DeepFace.represent(face_img, model_name=MODEL_NAME,
                                 detector_backend='skip', enforce_detection=False)[0]["embedding"]
        return np.array(rep, dtype=np.float32)
    except Exception as e:
        print(f"[ERROR] Embedding failed: {e}")
        return None

def build_database():
    embeddings_db = {}

    for person in os.listdir(DATABASE_PATH):
        person_path = os.path.join(DATABASE_PATH, person)
        if not os.path.isdir(person_path):
            continue

        print(f"\n[INFO] Processing {person} ...")
        embeddings = []

        for img_file in os.listdir(person_path):
            if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            img_path = os.path.join(person_path, img_file)
            face = extract_face_retina(img_path)
            if face is not None:
                emb = get_embedding(face)
                if emb is not None:
                    embeddings.append(emb)
                    print(f"   ✔ Embedded {img_file}")

        if len(embeddings) > 0:
            avg_emb = np.mean(embeddings, axis=0)
            embeddings_db[person] = avg_emb
            print(f"   → Saved {len(embeddings)} embeddings for {person}")
        else:
            print(f"   ✖ No valid embeddings for {person}")

    with open(EMBED_SAVE_PATH, "wb") as f:
        pickle.dump(embeddings_db, f)

    print(f"\n✅ Embeddings database saved to {EMBED_SAVE_PATH}")
    print(f"🧠 Total registered people: {len(embeddings_db)}")

if __name__ == "__main__":
    build_database()
