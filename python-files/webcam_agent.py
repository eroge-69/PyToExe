Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> # webcam_agent.py
... import cv2
... from flask import Flask, Response, request
... 
... app = Flask(__name__)
... 
... def generate_frames():
...     cap = cv2.VideoCapture(0)
...     while True:
...         success, frame = cap.read()
...         if not success:
...             break
...         else:
...             _, buffer = cv2.imencode('.jpg', frame)
...             frame = buffer.tobytes()
...             yield (b'--frame\r\n'
...                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
... 
... @app.route('/video')
... def video():
...     if request.args.get('pass') != '1234':  # Parolni xohlaganingizga o‘zgartiring
...         return "Unauthorized", 401
...     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
... 
... if __name__ == '__main__':
...     app.run(host='0.0.0.0', port=5000)
