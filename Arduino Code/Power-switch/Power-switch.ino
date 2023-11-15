int testPin = 9; // This is the pin that you will connet the brown wire to
// The black wire goes to the ground of the arduino
char serial_data; // When data is read from serial, it will be put here

void setup() {
  // initialize digital pin
  
  pinMode(testPin, OUTPUT);
  digitalWrite(testPin, LOW);   
  Serial.begin(9600);  //Baud rate
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
    if(serial_data == 'p') // If P was sent, turn on/off the computer
    {
      digitalWrite(testPin, HIGH);  // Act as if you are pushing down the button
      digitalWrite(LED_BUILTIN_RX,LOW); //Turn on Board LED while pressing button
      delay(500); // Hold it for half a second
      digitalWrite(testPin, LOW); // Release the Button
      digitalWrite(LED_BUILTIN_RX,HIGH);
    }
    if(serial_data == 'k') // If k was sent then hold the power button for 10 seconds to kill the computer
    {
      digitalWrite(LED_BUILTIN_RX,LOW);
      digitalWrite(testPin, HIGH);  
      delay(5000);
      digitalWrite(testPin, LOW);
      digitalWrite(LED_BUILTIN_RX,HIGH);
    }
  }
  else
  {
    digitalWrite(testPin, LOW); //If the pin is on, turn it off
    digitalWrite(LED_BUILTIN_TX,HIGH); //Turns off both of the LEDs
    digitalWrite(LED_BUILTIN_RX,HIGH);
  }
}
