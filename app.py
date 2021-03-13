from flask import Flask, request, render_template, jsonify
from flask_scss import Scss
from flask_mqtt import Mqtt

# import RPi.GPIO as GPIO
# import serial
# from os import system
# import time
# import multiprocessing

app = Flask(__name__)
app.testing = True

Scss(app, static_dir='static', asset_dir='assets')

app.config['MQTT_BROKER_URL'] = '192.168.100.253'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'web'
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
		mqtt.subscribe('room/#')
		print("connected")
		# mqtt.subscribe('room/gas')
		# mqtt.subscribe('room/light')
		# mqtt.subscribe('room/dust')
		# mqtt.subscribe('room/temperature')
		# mqtt.subscribe('room/humidity')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
		data = dict(
				topic=message.topic,
				payload=message.payload.decode()
		)
		# print(data['topic'])


@app.route('/')
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
