import paho.mqtt.client as mqtt
import serial
import time

#MQTT client setup:
mqttBroker = "192.168.100.253"
client = mqtt.Client("DMstation")
client.connect(mqttBroker)

#Serial connection properties:
ser = serial.Serial(
    port = '/dev/ttyS0',
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)


#Loop for reading from serial and publishing to MQTT:
while True:
    #Read from Serial and convert binary data to string:
    ZBdata = str(ser.readline().rstrip())
    ZBdata = ZBdata[2:-1]#removes b''

#Publishing all data to a common "all" topic:
    client.publish("All", ZBdata)
    print ("Published " + ZBdata + " to \"All\"")

#Check what data is being sent and publish it to a respective MQTT topic:
    if ("Temperature" in ZBdata):
        client.publish("outside/temperature", ZBdata)
        print("Published " + ZBdata + " to \"outside/temperature\"")
    elif ("Humidity" in ZBdata):
        client.publish("outside/humidity", ZBdata)
        print("Published " + ZBdata + " to \"outside/humidity\"")
    elif ("Ambient light" in ZBdata):
        client.publish("outside/light", ZBdata)
        print("Published " + ZBdata + " to \"outside/light\"")
    elif("Gas" in ZBdata):
        client.publish("outside/gas", ZBdata)
        print("Published " + ZBdata + " to \"outside/light\"\n")


    time.sleep(0.25)