#include <Wire.h>

void setup() {
  Wire.begin(); // Initialize I2C as Master
  Serial.begin(115200); // Initialize Serial communication
}

void loop() {
  // Read data from Serial and send it over I2C
  if (Serial.available()) {
    
    Wire.beginTransmission(9); // Address of the receiver Arduino
    while (Serial.available()){
      char data = Serial.read();
      Wire.write(data);
    }
    Wire.endTransmission();
  }
}