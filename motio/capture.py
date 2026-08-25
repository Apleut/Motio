# motio/capture.py
from flask import Flask, Response
import cv2 as cv
import threading

app = Flask(__name__)
cap = cv.VideoCapture(0)

def generate():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # pipeline hooks will go here

        ret2, buffer = cv.imencode('.jpg', frame)
        if not ret2:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/stream')
def stream():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_stream_server(port=5001):
    app.run(port=port, threaded=True, use_reloader=False)

def start_in_background(port=5001):
    thread = threading.Thread(target=start_stream_server, args=(port,), daemon=True)
    thread.start()
    return thread