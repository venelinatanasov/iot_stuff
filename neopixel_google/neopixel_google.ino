#include <Adafruit_NeoPixel.h>

#include <Adafruit_NeoPixel.h>

// the data pin for the NeoPixels
int neoPixelPin = 8;//Change the pin numbers according to your board

int numPixels = 30; //Change it according to the number of pixels in your neopixel
#define BUTTON_PIN1   2 //Change the pin numbers according to your board
#define BUTTON_PIN2   3 //Change the pin numbers according to your board
// Instatiate the NeoPixel from the ibrary
Adafruit_NeoPixel strip = Adafruit_NeoPixel(numPixels, neoPixelPin, NEO_GRB + NEO_KHZ800);

//Starting pixels for the Google's 4 colours
int start1 = 0; // Same value for Neopixels of all sizes
int start2 = 6; // 2 for 8 neopixel ring, 6 for 24 neopixel ring and so on
int start3 = 12; // 4 for 8 neopixel ring, 12 for 24 neopixel ring and so on
int start4 = 18; // 6 for 8 neopixel ring, 18 for 24 neopixel ring and so on

int brightness = 150;
int brightDirection = -15;
#define DELAY_TIME (50)

unsigned long startTime;

void setup() {
  pinMode(BUTTON_PIN1, INPUT_PULLUP);
  pinMode(BUTTON_PIN2, INPUT_PULLUP);
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
  startTime = millis();
  activatecircle();
  activateblink();
}

void loop() {
  bool but1 = digitalRead(BUTTON_PIN1);
  bool but2 = digitalRead(BUTTON_PIN2);
  if (but1 == HIGH) {
    // Short delay to debounce button.
    delay(10);
    if ( startTime + DELAY_TIME < millis() ) {
      activateblink();
      startTime = millis();

    }

  }
  else if (but2 == HIGH) {
    delay(10);
    if ( startTime + DELAY_TIME < millis() ) {
      activatecircle();
      startTime = millis();
    }
  }
  else {
    allOff();
  }

}


void allOff() {
  for ( int i = 0; i < numPixels; i++ ) {
    strip.setPixelColor(i, 0, 0, 0 );
  }
  strip.show();
}
//Circling effect
void activatecircle() {
  adjustStarts();

 // first 3 pixels = color set #1
  for ( int i = start1; i < start1 + 1; i++ ) {
    strip.setPixelColor(i, 23, 107, 239 );
  }

  // next 3 pixels = color set #2
  for ( int i = start2; i < start2 + 1 ; i++ ) {
    strip.setPixelColor(i, 255, 62, 48 );
  }

  // next 3 pixels = color set #3
  for ( int i = start3; i < start3 + 1; i++ ) {
    strip.setPixelColor(i, 247, 181, 41 );
  }
  // last 3 pixels = color set #3
  for ( int i = start4; i < start4 + 1; i++ ) {
    strip.setPixelColor(i, 23, 156, 82 );
  }

  strip.show();
}
//Blinking Effect. The RGB Colours are based on the Google's Logo
void activateblink() {

  for ( int i = start1; i < start1 + 1; i++ ) {
    strip.setPixelColor(i, 23, 107, 239 );
    strip.setBrightness(brightness);
    strip.show();

    adjustBrightness();
  }

  for ( int i = start2; i < start2 + 1 ; i++ ) {
    strip.setPixelColor(i, 255, 62, 48 );
    strip.setBrightness(brightness);
    strip.show();

    adjustBrightness();
  }

  for ( int i = start3; i < start3 + 1; i++ ) {
    strip.setPixelColor(i, 247, 181, 41 );
    strip.setBrightness(brightness);
    strip.show();

    adjustBrightness();
  }
  for ( int i = start4; i < start4 + 1; i++ ) {
    strip.setPixelColor(i, 23, 156, 82 );
    strip.setBrightness(brightness);
    strip.show();

    adjustBrightness();
  }

  strip.show();
}

void adjustStarts() {
  start1 = incrementStart(start1);
  start2 = incrementStart(start2);
  start3 = incrementStart(start3);
  start4 = incrementStart(start4);
}


int incrementStart(int startValue) {
  startValue = startValue + 1;
  if ( startValue == numPixels  )//Change it according to the number of pixels in your neopixel
    startValue = 0;

  return startValue;
}

void adjustBrightness() {
  brightness = brightness + brightDirection;
  if ( brightness < 0 ) {
    brightness = 0;
    brightDirection = -brightDirection;
  }
  else if ( brightness > 255 ) {
    brightness = 255;
    brightDirection = -brightDirection;
  }

  // output the serial
  Serial.println( brightness );
}
