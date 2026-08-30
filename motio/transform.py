import cv2 as cv
import numpy as np

_smoothed_crop = None

def _clamp_crop(x, y, w, h, frame_w, frame_h):
    x = max(0, min(x, frame_w - w))
    y = max(0, min(y, frame_h - h))
    return int(x), int(y), int(w), int(h)

def apply_framing(frame, face_box, zoom_margin: float = 0.6, smoothing: float = 0.15):
    global _smoothed_crop

    frame_h, frame_w = frame.shape[:2]

    if face_box is None:
        if _smoothed_crop is None:
            return frame
        x, y, w, h = _smoothed_crop
    else:
        fx, fy, fw, fh = face_box

        margin_x = fw * zoom_margin
        margin_y = fh * zoom_margin

        target_w = fw + (2 * margin_x)
        target_h = fh + (2 * margin_y)

        frame_aspect = frame_w / frame_h
        if target_w / target_h > frame_aspect:
            target_h = target_w / frame_aspect
        else:
            target_w = target_h * frame_aspect

        target_x = fx + (fw / 2) - (target_w / 2)
        target_y = fy + (fh / 2) - (target_h / 2)

        target_x, target_y, target_w, target_h = _clamp_crop(
            target_x, target_y, target_w, target_h, frame_w, frame_h
        )

        if _smoothed_crop is None:
            _smoothed_crop = (target_x, target_y, target_w, target_h)
        else:
            px, py, pw, ph = _smoothed_crop
            _smoothed_crop = (
                (smoothing * px) + ((1 - smoothing) * target_x),
                (smoothing * py) + ((1 - smoothing) * target_y),
                (smoothing * pw) + ((1 - smoothing) * target_w),
                (smoothing * ph) + ((1 - smoothing) * target_h),
            )

        x, y, w, h = _smoothed_crop

    x, y, w, h = _clamp_crop(x, y, w, h, frame_w, frame_h)

    cropped = frame[y:y + h, x:x + w]

    if cropped.size == 0:
        return frame

    resized = cv.resize(cropped, (frame_w, frame_h), interpolation=cv.INTER_LINEAR)

    return resized


def reset():
    global _smoothed_crop
    _smoothed_crop = None