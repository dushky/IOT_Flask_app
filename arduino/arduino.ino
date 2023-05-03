#include <DHT.h>


//define sound velocity in cm/uS
#define SOUND_VELOCITY 0.034

#define DHTPIN 10
#define DHTTYPE DHT11

const int trigPin = 12;
const int echoPin = 11;

long duration;
float distanceCm;

unsigned long interval=1000;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  dht.begin();
  Serial.begin(9600); // Starts the serial communication
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  delay(500);
}

void loop() {

  if(Serial.available() > 0) {
    int serialData = Serial.parseInt();  
    if (serialData > 100) {              
      interval = serialData;
    }
  }
  
//  currentMillis = millis();
  //Serial.flush();
  //Serial.println(interval);

  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  distanceCm = duration * SOUND_VELOCITY/2;

  if (distanceCm > 300){
    distanceCm = 300;
  }

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  String output =  
  String(distanceCm) + "," +
  String(temperature) + "," + 
  String(humidity);
  
  Serial.println(output);

  delay(interval);

}
