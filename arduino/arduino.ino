#include <DHT.h>


//define sound velocity in cm/uS
#define SOUND_VELOCITY 0.034

#define DHTPIN 10
#define DHTTYPE DHT11

const int trigPin = 12;
const int echoPin = 11;

long duration;
float distanceCm;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  dht.begin();
  Serial.begin(9600); // Starts the serial communication
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  delay(500);
}

void loop() {
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


  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  String output =  
  String(distanceCm) + "," +
  String(temperature) + "," + 
  String(humidity);

  Serial.println(output);
  delay(2000);
}
