import cv2 as cv
import pyvirtualcam

_cam = None
_cam_width = None
_cam_height = None
_last_error = None
_status_callback = None


def set_status_callback(callback):
    global _status_callback
    _status_callback = callback


def _set_error(error):
    global _last_error
    if error == _last_error:
        return
    _last_error = error
    if _status_callback is not None:
        _status_callback({"ok": error is None, "error": error})


def get_camera(width: int, height: int, fps: int = 30):
    global _cam, _cam_width, _cam_height

    if _cam is not None and (width != _cam_width or height != _cam_height):
        _cam.close()
        _cam = None

    if _cam is None:
        try:
            _cam = pyvirtualcam.Camera(width=width, height=height, fps=fps)
            _cam_width = width
            _cam_height = height
            _set_error(None)
            print(f"[virtualcam] started: {_cam.device} ({width}x{height} @ {fps}fps)")
        except RuntimeError as e:
            # pyvirtualcam raises RuntimeError both when no virtual camera
            # driver is installed at all, and when the OBS device exists
            # but is already claimed by another process (e.g. OBS Studio
            # itself has its own "Start Virtual Camera" active). We can't
            # cleanly distinguish those cases from the exception alone,
            # so the message covers both possibilities.
            _set_error(
                "Couldn't start the virtual camera. If OBS Studio is open, "
                "make sure its own \"Start Virtual Camera\" is stopped, "
                "since Motio and OBS can't use the same virtual camera "
                "device at once. If OBS isn't installed, Motio's virtual "
                "camera output requires the OBS Virtual Camera driver "
                "(install OBS Studio once, then it can stay closed)."
            )
            print(f"[virtualcam] failed to start: {e}")
            return None

    return _cam


def get_last_error():
    return _last_error


def send_frame(frame):
    h, w = frame.shape[:2]
    cam = get_camera(w, h)

    if cam is None:
        return

    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    cam.send(rgb_frame)
    cam.sleep_until_next_frame()


def close():
    global _cam
    if _cam is not None:
        _cam.close()
        _cam = None
        print("[virtualcam] closed")