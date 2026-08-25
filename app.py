from flask import Flask, Response
from motio.capture import generate_frames

app = Flask(__name__)

@app.route('/stream')
def stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(port=5001, threaded=True, use_reloader=False)