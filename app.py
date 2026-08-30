import threading
import webview
from flask import Flask, Response, send_from_directory
from motio.capture import generate_frames
from motio.bridge import Api

flask_app = Flask(__name__, static_folder='ui', static_url_path='')

@flask_app.route('/')
def index():
    return send_from_directory('ui', 'index.html')

@flask_app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('assets', filename)

@flask_app.route('/stream')
def stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_flask():
    flask_app.run(port=5001, threaded=True, use_reloader=False)


def main():
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    api = Api()
    window = webview.create_window(
        'Motio',
        'http://127.0.0.1:5001/',
        js_api=api,
        width=1000,
        height=650,
        min_size=(700, 450),
    )

    webview.start()


if __name__ == '__main__':
    main()