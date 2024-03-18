#include <SoftwareSerial.h>


// C++ code
//
float sensorPin = A0;

void setup()
{
  pinMode(A0, INPUT);
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  
  //Print header once
  Serial.print("Time(ms), ");
  Serial.print("Sensor Data(raw data), ");
  Serial.print("Sensor Data(smoothed)");
  Serial.println();

}

void loop()
{
  //Print measured reading of strain gauge
  float sensorValue1;
  sensorValue1 = analogRead(sensorPin);
  
  Serial.print(millis());
  Serial.print(" ");
  Serial.print(sensorValue1);
  Serial.print(" ");
  
  int avg[10] = {0};
  int i = 0;
  float currentAvg = 0;
  
  for (i=0;i<10;i++) {
   	avg[i] = analogRead(sensorPin);
  }
  
  float sum = 0;
  for (i=0;i<10;i++) {
   	sum = sum + avg[i];
  }
  
  currentAvg = sum / 10;
  Serial.print(currentAvg);
  Serial.println();
 
}