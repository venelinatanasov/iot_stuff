import paho.mqtt.client as mqtt
import time

mqttBroker = "192.168.100.253"
client = mqtt.Client("raspberry")
client.connect(mqttBroker)

client.publish("lights/google_on_off", "0")