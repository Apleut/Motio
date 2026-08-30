import json
import sys
import threading
import time
import urllib.request
from pathlib import Path

import webview
from flask import Flask, Response, send_from_directory

from motio.capture import generate_frames
from motio.bridge import Api
from motio import virtualcam


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path


UI_DIR = resource_path("ui")
ASSETS_DIR = resource_path("assets")


flask_app = Flask(
    __name__,
    static_folder=str(UI_DIR),
    static_url_path=""
)


@flask_app.route("/")
def index():
    return send_from_directory(str(UI_DIR), "index.html")


@flask_app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(str(ASSETS_DIR), filename)


@flask_app.route("/stream")
def stream():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def start_flask():
    flask_app.run(
        host="127.0.0.1",
        port=5001,
        threaded=True,
        use_reloader=False
    )


def wait_for_flask():
    for _ in range(50):
        try:
            urllib.request.urlopen(
                "http://127.0.0.1:5001/",
                timeout=0.2
            )
            return
        except Exception:
            time.sleep(0.1)

    raise RuntimeError("Flask server failed to start")


def main():
    flask_thread = threading.Thread(
        target=start_flask,
        daemon=True
    )
    flask_thread.start()

    wait_for_flask()

    api = Api()

    window = webview.create_window(
        "Motio",
        "http://127.0.0.1:5001/",
        js_api=api,
        width=1000,
        height=650,
        min_size=(700, 450),
    )

    def on_virtualcam_status_change(status):
        window.evaluate_js(
            f"updateVirtualCamStatus({json.dumps(status)})"
        )

    virtualcam.set_status_callback(
        on_virtualcam_status_change
    )

    webview.start()


if __name__ == "__main__":
    main()