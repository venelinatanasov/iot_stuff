import paho.mqtt.client as mqtt
import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735  
#MQTT client setup:
mqttBroker = "192.168.100.253"
client = mqtt.Client("raspberry")
client.connect(mqttBroker)


global gas
global light
global dust
global temperature
global humidity

global gas_outside
global humidity_outside
global temperature_outside
global light_outside


global gas_room2
global humidity_room2
global temperature_room2

gas='0'
light='0'
dust='0'
temperature='0'
humidity='0'
gas_outside='0'
humidity_outside='0'
temperature_outside='0'
light_outside='0'
gas_room2='0'
humidity_room2='0'
temperature_room2='0'
#def on_message(client, userdata, message):
 #   global= MQTTdata = str(message.payload.decode("utf-8"))
    
def on_gas_room(client, userdata, message):
    global gas
    val = message.payload.decode("utf-8")
    val=float(val)
    val/=4096
    val*=100
    gas = "%.2f" %val + "%"

    gas = "Gas: " + gas

    #print(gas)

def on_light_room(client, userdata, message):# currently not displayed, found it useless
    global light
    val = message.payload.decode("utf-8")
    val = float(val)
    val=4096-val
    val/=4096
    val*=100
    #light = "Light: " + str(message.payload.decode("utf-8"))
    light = "Light 2: " + str(val) + "%"
    #print(light)

def on_dust_room(client, userdata, message):
    global dust
    dust = "Dust 1: " + str(message.payload.decode("utf-8")) + " mg/m3"
    #print(dust)

def on_temperature_room(client, userdata, message):
    global temperature
    temperature = "Temperature 1: " + str(message.payload.decode("utf-8")) + " C"
    #print(temperature)

def on_humidity_room(client, userdata, message):
    global humidity
    humidity = "Humidity 1: " + str(message.payload.decode("utf-8")) + "%"
    #print(humidity)



def on_gas_outside(client, userdata, message):
    global gas_outside
    gas_outside = "Gas outside: " + str(message.payload.decode("utf-8")) + "%"
    #print(gas_outside)

def on_humidity_outside(client, userdata, message):
    global humidity_outside
    humidity_outside = "Humidity outside: " + str(message.payload.decode("utf-8")) + "%"
    print(humidity_outside)

def on_temperature_outside(client, userdata, message):
    global temperature_outside
    temperature_outside = "T outside: " + str(message.payload.decode("utf-8")) + " C"
    print(temperature_outside)

def on_light_outside(client, userdata, message):
    global light_outside
    light_outside = "Light outside: " + str(message.payload.decode("utf-8")) + "lux"
    print(light_outside)


def on_gas_room2(client, userdata, message):
    global gas_room2
    #gas_room2="Gas 2" + str(message.payload.decode("utf-8"))
    val = message.payload.decode("utf-8")
    val=float(val)
    val/=4096
    val*=100
    gas_room2 = "%.2f" %val + "%"
    gas_room2 = "Gas 2: " + gas_room2

def on_humidity_room2(client, userdata, message):
    global humidity_room2
    humidity_room2="Humidity 2: "+ str(message.payload.decode("utf-8")) + "%"

def on_temperature_room2(client, userdata, message):
    global temperature_room2
    temperature_room2="Temperature 2: " + str(message.payload.decode("utf-8")) + "%"

cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D26)
reset_pin = digitalio.DigitalInOut(board.D16)
 

BAUDRATE = 24000000
 
# Setup SPI bus using hardware SPI:
spi = board.SPI()
 

disp = st7735.ST7735R(spi, rotation=90,                          
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height
 
image = Image.new("RGB", (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
 
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)
 
# First define some constants to allow easy positioning of text.
padding = -2
x = 0
 

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

#try:
client.subscribe("room/#", 0)
client.message_callback_add("room/gas", on_gas_room)
client.message_callback_add("room/light", on_light_room)
client.message_callback_add("room/dust", on_dust_room)
client.message_callback_add("room/temperature", on_temperature_room)
client.message_callback_add("room/humidity", on_humidity_room)

client.subscribe("outside/#",0)
client.message_callback_add("outside/gas", on_gas_outside)
client.message_callback_add("outside/light", on_light_outside)
client.message_callback_add("outside/temperature", on_temperature_outside)
client.message_callback_add("outside/humidity", on_humidity_outside)
client.subscribe("room2/#",0)
client.message_callback_add("room2/humidity", on_humidity_room2)
client.message_callback_add("room2/temperature", on_temperature_room2)
client.message_callback_add("room2/gas", on_gas_room2)
#client.on_message=on_message
client.loop_start()
while(True):
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    


    t_end=time.time() + 5
    while(time.time()<t_end):
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
            
        #cmd = "hostname -I | cut -d' ' -f1"
        #IP = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        #cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
        #Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"  
        Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
        # Write four lines of text.
        y = padding
        #draw.text((x, y), IP, font=font, fill="#FFFFFF")
        #y += font.getsize(IP)[1]
        draw.text((x, y), CPU, font=font, fill="#FFFF00")
        y += font.getsize(CPU)[1]
        draw.text((x, y), MemUsage, font=font, fill="#00FF00")
        y += font.getsize(MemUsage)[1]
        #draw.text((x, y), Disk, font=font, fill="#0000FF")
        #y += font.getsize(Disk)[1]
        draw.text((x, y), Temp, font=font, fill="#FF00FF")
        y += font.getsize(Temp)[1]
        draw.text((x, y), temperature, font=font, fill="#0000FF")
        y += font.getsize(temperature)[1]
        draw.text((x, y), humidity, font=font, fill="#F5A442")
        y += font.getsize(humidity)[1]
        draw.text((x, y), gas, font=font, fill="#23C2AA")
        y += font.getsize(gas)[1]
        draw.text((x, y), dust, font=font, fill="#0073E6")
        y += font.getsize(dust)[1]
        #draw.text((x, y), light, font=font, fill="#00F7FF")
        #y += font.getsize(light)[1]
        
        # Display image.
        disp.image(image)
        time.sleep(0.1)
    #cmd = "hostname -I | cut -d' ' -f1"
    #IP = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
    y=padding


    t_end=time.time()+5
    while(time.time()<t_end):
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        y = padding
        #cmd = "hostname -I | cut -d' ' -f1"
        #IP = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        #cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
        #Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"  
        Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
        # Write four lines of text.
        
        #draw.text((x, y), IP, font=font, fill="#FFFFFF")
        #y += font.getsize(IP)[1]
        draw.text((x, y), CPU, font=font, fill="#FFFF00")
        y += font.getsize(CPU)[1]
        draw.text((x, y), MemUsage, font=font, fill="#00FF00")
        y += font.getsize(MemUsage)[1]
        #draw.text((x, y), Disk, font=font, fill="#0000FF")
        #y += font.getsize(Disk)[1]
        draw.text((x, y), Temp, font=font, fill="#FF00FF")
        y += font.getsize(Temp)[1]
        #draw.rectangle((0, 0, width, height), outline=0, fill=0)
        
        draw.text((x, y), gas_room2, font=font, fill="#23C2AA")
        y += font.getsize(gas_room2)[1]
        #draw.text((x, y), light_outside, font=font, fill="#FFFF00")
        #y += font.getsize(light_outside)[1]
        draw.text((x, y), humidity_room2, font=font, fill="#F5A442")
        y += font.getsize(humidity_room2)[1]
        draw.text((x, y), temperature_room2, font=font, fill="#0000FF")
        y += font.getsize(temperature_room2)[1]
        disp.image(image)
        time.sleep(0.1)






    
    t_end=time.time() + 5
    while(time.time()<t_end):
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        y = padding
        #cmd = "hostname -I | cut -d' ' -f1"
        #IP = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        #cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
        #Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"  
        Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
        # Write four lines of text.
        
        #draw.text((x, y), IP, font=font, fill="#FFFFFF")
        #y += font.getsize(IP)[1]
        draw.text((x, y), CPU, font=font, fill="#FFFF00")
        y += font.getsize(CPU)[1]
        draw.text((x, y), MemUsage, font=font, fill="#00FF00")
        y += font.getsize(MemUsage)[1]
        #draw.text((x, y), Disk, font=font, fill="#0000FF")
        #y += font.getsize(Disk)[1]
        draw.text((x, y), Temp, font=font, fill="#FF00FF")
        y += font.getsize(Temp)[1]
        #draw.rectangle((0, 0, width, height), outline=0, fill=0)
        
        draw.text((x, y), gas_outside, font=font, fill="#23C2AA")
        y += font.getsize(gas_outside)[1]
        #draw.text((x, y), light_outside, font=font, fill="#FFFF00")
        #y += font.getsize(light_outside)[1]
        draw.text((x, y), humidity_outside, font=font, fill="#F5A442")
        y += font.getsize(humidity_outside)[1]
        draw.text((x, y), temperature_outside, font=font, fill="#0000FF")
        y += font.getsize(temperature_outside)[1]
        disp.image(image)
        time.sleep(0.1)
    pass

client.loop_stop()
#except:
   # print("Exception occured")