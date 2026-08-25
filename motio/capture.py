import atexit
import cv2 as cv
from motio.tracking import track_face
from motio.settings import settings

cap = cv.VideoCapture(0)

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
            frame = track_face(frame)
        # frame = adjust_lowlight(frame)
        # frame = blur_background(frame)

        ret2, buffer = cv.imencode('.jpg', frame)
        if not ret2:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')