import atexit
import cv2 as cv
from motio.tracking import track_face
from motio.transform import apply_framing
from motio.settings import settings

cap = cv.VideoCapture(0)

def switch_camera(index: int):
    global cap
    cap.release()
    cap = cv.VideoCapture(index)

@atexit.register
def cleanup():
    print("Releasing camera...")
    cap.release()

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        if settings.face_tracking:
            face_box = track_face(frame, smoothing=settings.tracking_smoothing_alpha)
            frame = apply_framing(frame, face_box, zoom_margin=settings.zoom_margin, smoothing=settings.tracking_smoothing_alpha,)

        ret2, buffer = cv.imencode('.jpg', frame)
        if not ret2:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')