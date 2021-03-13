from flask import Flask, request, render_template, jsonify
from flask_scss import Scss
from flask_mqtt import Mqtt
from flask_mongoengine import MongoEngine
import time
# import pymongo

# import RPi.GPIO as GPIO
# import serial
# from os import system
# import multiprocessing
starttime = time.time()

app = Flask(__name__)
app.testing = True

#MongoDB settings
app.config['MONGODB_SETTINGS'] = {
		'db': 'data',
		'host': 'localhost',
		'port': 27017
}

#setting up Mongo client 
DB_URI = "mongodb+srv://iliana:moje@autohome.acegw.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app.config["MONGODB_HOST"] = DB_URI

#setting up DB
db = MongoEngine()
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



#model for room_data to be saved in DB
class DBData(db.Document):
		temperature = db.IntField()
		light = db.IntField()
		gas = db.IntField()
		dust = db.FloatField()
		humidity = db.IntField() 

		def to_json(self):
			return{"temperature": self.temperature, "light": self.light, "gas": self.gas, "dust": self.dust, "humidity": self.humidity}

#class to hold data locally
class Room:
	def __init__(self, temperature, light, gas, dust, humidity): 
		self.temperature = temperature
		self.light = light
		self.gas = gas
		self.dust = dust
		self.humidity = humidity 

	def update(self, temperature, light, gas, dust, humidity): 
		self.temperature = temperature
		self.light = light
		self.gas = gas
		self.dust = dust
		self.humidity = humidity 
	
	def updateTemperature(self, temperature): 
		self.temperature = temperature

	def updateLight(self, light): 
		self.light = light
	
	def updateDust(self, dust): 
		self.dust = dust
	
	def updateGas(self, gas): 
		self.gas = gas

	def updateHumidity(self, humidity): 
		self.humidity = humidity
		
	def convertToPercent(self, var):
		return var*100/4096

	def convertDust(self, var):
		return var*100/0.5

room_info = Room(0, 0, 0, 0, 0)
# print(room_info.gas)

      

#MQTT connection
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
		mqtt.subscribe('room/#')
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
		
		# if(data['topic'] == "room/dust"):
		# 	print(data['payload'])
		# if(data['topic'] == "room/gas"):
		# 	print(data['payload'])
		# if(data['topic'] == "room/light"):
		# 	print(data['payload'])
		# if(data['topic'] == "room/temperature"):
		# 	print(data['payload'])
		# if(data['topic'] == "room/humidity"):
		# 	print(data['payload'])

#main route
@app.route('/')
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
