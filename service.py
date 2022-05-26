# Adapted from https://github.com/EbenKouao/pi-camera-stream-flask/blob/master/main.py
import os
from flask import Flask, Response
from imutils.video.pivideostream import PiVideoStream
import cv2
import xml.etree.ElementTree as ET
import ast
from datetime import datetime


def ExtractConfig(filepath):
	config_dict = dict()
	tree = ET.parse(filepath)
	root_elm = tree.getroot()
	for level1_elm in root_elm:
		if level1_elm.tag == 'VideoFeedName':
			config_dict['VideoFeedName'] = level1_elm.text
		elif level1_elm.tag == 'Resolution':
			config_dict['Resolution'] = ast.literal_eval(level1_elm.text)
		elif level1_elm.tag == 'WriteTimestamp':
			config_dict['WriteTimestamp'] = ast.literal_eval(level1_elm.text)
		elif level1_elm.tag == 'Flip':
			config_dict['Flip'] = ast.literal_eval(level1_elm.text)
	return config_dict
	
def WriteTimestamp(image):
	timestamp = datetime.now().strftime("%Y-%b-%d %H:%M:%S")
	text_origin = (image.shape[1] - 400, image.shape[0] - 30)
	cv2.putText(image, timestamp, text_origin, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
	



app = Flask(__name__)

config = ExtractConfig("./service_config.xml")

video_stream = PiVideoStream(resolution=config['Resolution']).start()

@app.route('/')
def index():
	return f"Base service address. Append /{config['VideoFeedName']} to get the video feed"
	
def gen(vid_stream):
	while True:
		frame = vid_stream.read()
		if config['Flip'] == True:
			frame = cv2.flip(frame, 0)
		if config['WriteTimestamp'] == True:
			WriteTimestamp(frame)
		ret, jpeg = cv2.imencode('.jpg', frame)
		frame = jpeg.tobytes()
		yield(b'--frame\r\n'
		      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
		      
@app.route(f"/{config['VideoFeedName']}")
def video_feed():
	return Response(gen(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')



	
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)
