import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import cv2 as cv

from motio.settings import settings

base_options = mp_python.BaseOptions(model_asset_path='assets/blaze_face_short_range.tflite')
options = vision.FaceDetectorOptions(base_options=base_options)
detector = vision.FaceDetector.create_from_options(options)

_smoothed_box = None

def track_face(frame):
    global _smoothed_box

    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = detector.detect(mp_image)

    if result.detections:
        bbox = result.detections[0].bounding_box
        raw_box = (bbox.origin_x, bbox.origin_y, bbox.width, bbox.height)

        if settings.smooth_tracking:
            if _smoothed_box is None:
                _smoothed_box = raw_box
            else:
                alpha = 0.3
                _smoothed_box = tuple(
                    int(alpha * new + (1 - alpha) * old)
                    for new, old in zip(raw_box, _smoothed_box)
                )

            x, y, bw, bh = _smoothed_box
        else:
            x, y, bw, bh = raw_box
        cv.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

    return frame