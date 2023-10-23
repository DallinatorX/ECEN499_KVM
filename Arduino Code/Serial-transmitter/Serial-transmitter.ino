int testPin = 9; // This is the pin that you will connet the brown wire to
// The black wire goes to the ground of the arduino
char serial_data; // When data is read from serial, it will be put here

void setup() {
  // initialize digital pin
  
  pinMode(testPin, OUTPUT);
  digitalWrite(testPin, LOW);   
  Serial.begin(9600);  //Baud rate
  Serial1.begin(9600);  //Baud rate

}

// the loop function runs over and over again forever
void loop() {
  if(serial_data != 0) //Clear the data read from the serial port
  {
    serial_data = 0;
  }
  if(Serial.available())
  {
    
    serial_data = Serial.read();
    Serial1.write(serial_data);
  }
}
