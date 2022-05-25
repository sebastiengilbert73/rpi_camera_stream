# Adapted from https://github.com/EbenKouao/pi-camera-stream-flask/blob/master/main.py
import os
from flask import Flask, Response
from imutils.video.pivideostream import PiVideoStream
import cv2


app = Flask(__name__)

video_stream = PiVideoStream().start()

@app.route('/')
def index():
	return "Base service address"
	
def gen(vid_stream):
	while True:
		frame = vid_stream.read()
		ret, jpeg = cv2.imencode('.jpg', frame)
		frame = jpeg.tobytes()
		yield(b'--frame\r\n'
		      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
		      
@app.route('/video_feed')
def video_feed():
	return Response(gen(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')

	
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)
