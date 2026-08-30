import sys
import cv2 as cv
from motio.settings import Settings, settings as _settings_module
import motio.settings as settings_mod
try:
    from pygrabber.dshow_graph import FilterGraph
    _HAS_PYGRABBER = sys.platform == "win32"
except ImportError:
    _HAS_PYGRABBER = False


def _get_device_names():
    if not _HAS_PYGRABBER:
        return None
    try:
        return FilterGraph().get_input_devices()
    except Exception as e:
        print(f"[bridge] pygrabber device lookup failed: {e}")
        return None


class Api:
    def get_settings(self):
        return settings_mod.settings.model_dump()

    def update_setting(self, key: str, value):
        current = settings_mod.settings.model_dump()

        if key not in current:
            print(f"[bridge] ignoring unknown setting: {key}")
            return {"ok": False, "error": f"unknown setting '{key}'"}

        current[key] = value

        try:
            validated = Settings(**current)
        except Exception as e:
            print(f"[bridge] rejected invalid value for {key}={value}: {e}")
            return {"ok": False, "error": str(e)}

        for field_name, field_value in validated.model_dump().items():
            setattr(settings_mod.settings, field_name, field_value)

        settings_mod.settings.save()
        return {"ok": True}

    def reset_settings(self):
        defaults = Settings()
        for field_name, field_value in defaults.model_dump().items():
            setattr(settings_mod.settings, field_name, field_value)

        settings_mod.settings.save()
        return settings_mod.settings.model_dump()

    def list_cameras(self, max_check: int = 5):
        device_names = _get_device_names()
        current = settings_mod.settings.camera_device

        available = []
        for index in range(max_check):
            if index == current:
                is_present = True
            else:
                cap = cv.VideoCapture(index)
                is_present = cap.isOpened()
                cap.release()

            if not is_present:
                continue

            if device_names and index < len(device_names):
                name = device_names[index]
            else:
                name = f"Camera {index}"

            available.append({"index": index, "name": name})

        return available

    def set_camera_device(self, index: int):
        settings_mod.settings.camera_device = index
        settings_mod.settings.save()

        from motio import capture
        capture.switch_camera(index)

        return {"ok": True}