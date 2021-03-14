from flask import Flask, request, render_template, jsonify
from flask_scss import Scss
from flask_mqtt import Mqtt
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO
import time, threading, requests
import datetime as dt

# import pymongo
# from flask_pymongo import PyMongo
# from model.pymongo_model import SimpleModel, DiffHistoryModelV1, DiffHistoryModelV2
# from pymongo_document import documents
# from pymodm import MongoModel, fields

# import RPi.GPIO as GPIO
# import serial
# from os import system
# import multiprocessing
starttime = time.time()

app = Flask(__name__)
app.testing = True

#MongoDB settings + client
DB_URI = "mongodb+srv://iliana:moje@autohome.acegw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app.config['MONGODB_SETTINGS'] = {
		'db': 'data',
		'host': DB_URI,
		'port': 27017
}

#setting up Mongo client 
# DB_URI = "mongodb+srv://iliana:moje@autohome.acegw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
# app.config["MONGO_URI"] = DB_URI

#setting up DB
db = MongoEngine()
# db = PyMongo(app)
db.init_app(app)

#setting up sass
scss = Scss(app, static_dir='static', asset_dir='assets')

#setting up mqtt
app.config['MQTT_BROKER_URL'] = '192.168.100.253'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'web'
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)

#setting up socketio
app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app, async_mode="threading")

#model for room_data to be saved in DB
class DB_data(db.Document):
		temperature = db.FloatField()
		light = db.FloatField()
		gas = db.FloatField()
		dust = db.FloatField()
		humidity = db.FloatField() 
		timestamp = db.DateTimeField()

		def getTemp(self):
			return self.temperature

		def to_json(self):
			return{"temperature": self.temperature, "light": self.light, "gas": self.gas, "dust": self.dust, "humidity": self.humidity, "timestamp": self.timestamp}

#class to hold data locally
class Room:
	def __init__(self, temperature, light, gas, dust, humidity): 
		self.temperature = temperature
		self.light = light
		self.gas = gas
		self.dust = dust
		self.humidity = humidity 
		self.timestamp = dt.datetime.utcnow

	def update(self, temperature, light, gas, dust, humidity): 
		self.temperature = temperature
		self.light = light
		self.gas = gas
		self.dust = dust
		self.humidity = humidity 
		self.timestamp = dt.datetime.utcnow
	
	def update_temperature(self, temperature): 
		self.temperature = temperature

	def update_light(self, light): 
		self.light = light
	
	def update_dust(self, dust): 
		self.dust = dust
	
	def update_gas(self, gas): 
		self.gas = gas

	def update_humidity(self, humidity): 
		self.humidity = humidity
		
	def convert_to_percent(self, var):
		return float(var)*100/4096

	def convert_dust(self, var):
		return float(var)*100/0.5

	def convert_light(self, var):
		return 100.0 - float(var)*100/3000

room_info = Room(0, 0, 0, 0, 0)
# print(room_info.gas) 

#MQTT connection
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
		mqtt.subscribe('room/#')
		mqtt.subscribe('lights/#')
		print("connected")
		# mqtt.subscribe('room/gas')	 #230/4096
		# mqtt.subscribe('room/light') #546/4096
		# mqtt.subscribe('room/dust')	 #0/0.5 mg/m^3
		# mqtt.subscribe('room/temperature') #celsius
		# mqtt.subscribe('room/humidity') #40%
		
#MQTT events
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
		data = dict(
				topic=message.topic,
				payload=message.payload.decode()
		)

		print(data['topic'] + data['payload'])
		
		if(data['topic'] == "room/dust"):
			room_info.update_dust(room_info.convert_dust(data['payload']))
		if(data['topic'] == "room/gas"):
			room_info.update_gas(room_info.convert_to_percent(data['payload']))
		if(data['topic'] == "room/light"):
			room_info.update_light(room_info.convert_light(data['payload']))
		if(data['topic'] == "room/temperature"):
			room_info.update_temperature(data['payload'])
		if(data['topic'] == "room/humidity"):
			room_info.update_humidity(data['payload'])

		
		if(data['topic'] == "lights/google_on_off"):
			print("in")
			if(data['payload'] == '1'):
				data = {'lights' : 1}
				return jsonify({'lights' : 1})
			elif(data['payload'] == '0'):
				print("turns")
				data = {'lights' : 0}
				requests.post('http://localhost:5000/off', data=data)
		# if(data['topic'] == "lightgoogle/auto"):
		# 	return jsonify({'lights' : 2})


# while True:
# 	print("latching data to database")
	# time.sleep(30.0 - ((time.time() - starttime) % 30.0))

def send_data_to_DB():
		# print(time.ctime())
		print("latching data to database")
		data = DB_data(temperature=room_info.temperature, light=room_info.light, gas=room_info.gas, dust=room_info.dust, humidity=room_info.humidity, timestamp=dt.datetime.utcnow	)
		data.save()
		
		try:
			t = threading.Timer(10, send_data_to_DB)
			t.daemon = True
			t.start()
		except KeyboardInterrupt:
			print("Goodbye!")

send_data_to_DB();

#main route
@app.route('/', methods = ['POST', 'GET'])
def index():

	return render_template('index.html')

@app.route('/on', methods = ['POST', 'GET'])
def turn_light_on():
	if request.method == 'POST':
		mqtt.publish('lights/auto', 0)
		mqtt.publish('lights/on_off', 1)	
	return jsonify({'lights' : 1})

@app.route('/off', methods = ['POST', 'GET'])
def turn_light_off():
	print("light off")
	if request.method == 'POST':
		mqtt.publish('lights/auto', 0)
		mqtt.publish('lights/on_off', 0)
	return jsonify({'lights' : 0})

@app.route('/auto', methods = ['POST', 'GET'])
def turn_light_auto():
	if request.method == 'POST':
		# mqtt.publish('lights/on_off', 0)
		mqtt.publish('lights/auto', 1)
	return jsonify({'lights' : 2})

@app.route('/temp', methods = ['POST', 'GET'])
def get_temperature_stats():
	if request.method == 'POST':
		# temp = request.args.get('temp')
		temp = []
		queries = DB_data.objects()
		# temps = db.d_b_data.find({}, {temperature:1, timestamp:1})

		for i in queries:
			temp.append(i.getTemp())
		print(temp)
		return jsonify({'temp' : temp})


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
