#include <AHT10.h>

#include <AHT10.h>

#define gas_pin 34
#define light_pin 35
#define esp_name ESP1
#define door_pin 
void callback(char* topic, byte* message, unsigned int length);

#define particles_pin 32
#define led_power 33
#define particles_sampling 280

#define lightbulb 26

#define GAS_TOLERANCE 10
#define DUST_TOLERANCE 10

int freq = 2000;
int channel = 0;
int resolution = 8;

#include <WiFi.h>
#include <PubSubClient.h>
#include <AHT10.h>
//setup
const char *ssid =  "HackTues";   // name of your WiFi network
const char *password =  "029925042"; // password of the WiFi network
const char *ID = "esp_name";  // Name of our device, must be unique
const char *TOPIC_GAS = "room/gas";  // TOPIC_GAS to subcribe to
const char *TOPIC_LIGHT = "room/light"; //TOPIC_LIGHT for light sensor
const char *TOPIC_DUST = "room/dust"; //TOPIC_DUST for dust sensor
const char *TOPIC_TEMPERATURE = "room/temperature";
const char *TOPIC_HUMIDITY = "room/humidity";


const char *TOPIC_GOOGLE_ON_OFF = "lights/google_on_off";
const char *TOPIC_ON_OFF = "lights/on_off";
const char *TOPIC_AUTO = "lights/auto";


IPAddress broker(192,168,100,253);
WiFiClient wclient;
PubSubClient mqttclient(wclient); // Setup MQTT client
//void light_control(char* topic, char* message, unsigned int lenght);


AHT10 myAHT10(AHT10_ADDRESS_0X38);
int aht_timeout;


int auto_light=0;


void setup() {

  aht_timeout=millis(); //read aht eveery two seconds so it won't overheat


  
  Serial.begin(115200);

  
  setup_wifi(); // Connect to network

  
  mqttclient.setServer(broker, 1883);
  mqttclient.setCallback(callback);
  
  pinMode(led_power, OUTPUT);
  digitalWrite(led_power, HIGH);

  
  ledcSetup(channel, freq, resolution);
  ledcAttachPin(25, channel);

  
  pinMode(lightbulb, OUTPUT);
  digitalWrite(lightbulb, LOW);


  while (myAHT10.begin() != true)
  {
    Serial.println("AHT10 not connected or fail to load calibration coefficient"); //(F()) save string to flash & keeps dynamic memory free
    delay(5000);
  }
  




  
}


int dust_error = 0; //times to measure before buzz, stability issues
int gas_error = 0;


void loop() {
  
  
  if (!mqttclient.connected())  // Reconnect if connection is lost
  {
    reconnect();
  }
  mqttclient.loop();
  //gas
  int gas_val=read_gas(gas_pin);
  char gas[7];
  to_char_array(gas_val, gas);
  
  mqttclient.publish(TOPIC_GAS, gas);
  //Serial.println((String)TOPIC_GAS);
  //Serial.println(gas);

  delay(100);
  
  //light
  int light_val = read_light(light_pin);
  char light[7];
  to_char_array(light_val, light);
  mqttclient.publish(TOPIC_LIGHT, light);
  if(auto_light&&light_val>900){
    lightbulb_on();
  }
  if(auto_light&&light_val<700){
    lightbulb_off();
  }
  //Serial.println((String)TOPIC_LIGHT);
  //Serial.print(light);
  //Serial.println(light);

  
  float dust_val = read_particles(particles_pin, led_power);
  char dust[7];
  to_char_array(dust_val,dust);
  //Serial.println(dust_val);
  //Serial.println(dust);
  mqttclient.publish(TOPIC_DUST, dust);
 
  if(dust_val>0.3){
    dust_error++;
    if(dust_error>DUST_TOLERANCE){
      buzz();
      dust_error=0;
    }
  }
  if(gas_val>1300){
    gas_error++;
    if(gas_error>GAS_TOLERANCE){
      buzz();
      gas_error=0;
    }
  } 

  //Serial.println(read_temperature());
  //Serial.println(read_humidity());
  int aht_temp=millis();
  if(aht_temp>aht_timeout+2000){
  //takes a whole lotta time, ~200ms!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  float temperature_val = read_temperature();
  char temperature[7];
  to_char_array(temperature_val, temperature);
  //Serial.println(read_temperature());
  mqttclient.publish(TOPIC_TEMPERATURE, temperature);

  float humidity_val = read_humidity();
  char humidity[7];
  to_char_array(humidity_val, humidity);
  //Serial.println(read_humidity());
  mqttclient.publish(TOPIC_HUMIDITY, humidity);

  aht_timeout=millis();
  }
  
}


void callback(char* topic, byte* message, unsigned int length){
  Serial.println("callback");
  Serial.println(topic);
  //message[length]='\0';
  char a = message[0];
  if(!strcmp(topic, "lights/google_on_off")){
    Serial.println("google");
    Serial.println((char *)message);
    
    Serial.println(a);
    if(a=='1'){
      Serial.println("on");
      lightbulb_on();
    }
    if(a=='0'){
      lightbulb_off();
    }
    return;
  }
  if(!strcmp(topic, "lights/on_off")){
    Serial.println(a);
    if(a=='1'){
      lightbulb_on();
    }
    if(a=='0'){
      lightbulb_off();
    }
    return;
  }
  if(!strcmp(topic, "lights/auto")){
    Serial.println(a);
    if(a=='1'){
      auto_light=1;
    }
    if(a=='0'){
      auto_light=0;
    }
    return;
  }
  
}






float read_temperature(){
  return myAHT10.readTemperature();
}

float read_humidity(){
  
  return myAHT10.readHumidity();
  
}


void lightbulb_on(){
  digitalWrite(lightbulb, HIGH);
}

void lightbulb_off(){
  digitalWrite(lightbulb, LOW);
}



void buzz(){
  for(int i=0;i<3;i++){
    ledcWrite(channel, 125);
    lightbulb_on();
    delay(500);
    ledcWrite(channel, 90);
    lightbulb_off();
    delay(500);
  }
  ledcWrite(channel, 0);
}





/*int read_door_switch()
{
  
}*/
float read_particles(int analog_pin, int power_pin){
  float voMeasured;
  float calcVoltage;
  float dustDensity;
  //float dustDensity_temp = 0;
  
    digitalWrite(power_pin, LOW);
    delayMicroseconds(particles_sampling);
    voMeasured=analogRead(analog_pin);
    delayMicroseconds(40);
    digitalWrite(power_pin, HIGH);
    calcVoltage = (voMeasured*(3.3/4096))*(5/3.3);
    dustDensity = 0.17*calcVoltage-0.1;
    if(dustDensity<0){
      dustDensity=0;
    }
    




  
  /*Serial.println("Raw Signal Value: ");
  Serial.println(voMeasured);
  
  Serial.println("Voltage:");
  Serial.println(calcVoltage);
  */
  //Serial.println("Dust Density:");
  //Serial.println(dustDensity);
  return dustDensity;
  
}

int read_light(int analog_pin){
  int k=0;
  for(int i=0;i<50;i++){
    k+=analogRead(analog_pin);
  }
  k/=50;
  return k;
}










int read_gas(int analog_pin){
  int k=0;
  for(int i=0;i<50;i++){
    k+=analogRead(analog_pin);
  }
  
  k/=50;
  //Serial.println(k);
  return k;
}






void to_char_array(float a, char * b){
  dtostrf(a, 1, 2, b);
  //String str;
  //str=String(a,2);
  //Serial.println(str);
  //delay(800);
  //str.toCharArray(b,5);
}





void setup_wifi() {
  Serial.print("\nConnecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password); // Connect to network

  while (WiFi.status() != WL_CONNECTED) { // Wait for connection
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}







// Reconnect to client
void reconnect() {
  // Loop until we're reconnected
  while (!mqttclient.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (mqttclient.connect(ID)) {
      Serial.println("connected");
      Serial.print("Publishing to: ");
      Serial.println(TOPIC_GAS);
      Serial.println('\n');
      mqttclient.subscribe("lights/#");

    } else {
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
