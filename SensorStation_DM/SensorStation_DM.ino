#include <Adafruit_AHTX0.h>
#include <MAX44009.h>
#include <Wire.h>

Adafruit_AHTX0 aht;
MAX44009 Lux(0x4A);

void setup() {
  Lux.Begin(0, 188000);
  Wire.begin();
  delay(1000);
  
  Serial.begin(9600);
  if (!aht.begin()) {
    Serial.println("Could not find AHT? Check wiring");
    while (1){delay(10);}
  }
  Serial.println("--AHT10 or AHT20 found--");
}

void loop() {
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
  
  Serial.print("\nTemperature:   "); Serial.print(temp.temperature); Serial.println("C");//print Temperature
  Serial.print("Humidity:      "); Serial.print(humidity.relative_humidity); Serial.println("%RH");//print Relative Humidity
  Serial.print("Ambient light: "); Serial.print(Lux.GetLux()); Serial.println("lux");//print Ambient light
  Serial.print("Gas: "); Serial.print((analogRead(A3)*100)/1024);Serial.println("%");
  
  delay(5000);
}
