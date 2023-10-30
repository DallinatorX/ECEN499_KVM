#include <Wire.h>   
#include <Mouse.h>  
#include <Keyboard.h>
#include <KeyboardLayout.h>
#include <Keyboard_da_DK.h>
#include <Keyboard_de_DE.h> 
#include <Keyboard_es_ES.h>
#include <Keyboard_fr_FR.h>
#include <Keyboard_it_IT.h>
#include <Keyboard_sv_SE.h>


byte key_array[200];
uint8_t type_in, key_in, action;
// char type_in, key_in, action;
int8_t mouse_x, mouse_y, recieved_data;


void setup()
{
  // Debug LED
  pinMode(LED_BUILTIN, OUTPUT);
  recieved_data = 0;
  
  // Set associated array for keypresses to their corresponding Hex for the HID to read.
  // https://www.arduino.cc/reference/en/language/functions/usb/keyboard/keyboardmodifiers/
  key_array[2] = 0x82;    // Left Alt
  key_array[4] = 0xB2;    // Backspace
  key_array[6] = 0x80;    // Left Ctrl
  key_array[8] = 0xD4;    // Delete
  key_array[10] = 0xD9;   // Down Arrow
  key_array[12] = 0xD5;   // End
  key_array[14] = 0xB0;   // Enter
  key_array[16] = 0xB1;   // Esc
  key_array[18] = 0xC2;   // F1
  key_array[20] = 0xC3;   // F2
  key_array[22] = 0xC4;   // F3
  key_array[24] = 0xC5;   // F4
  key_array[26] = 0xC6;   // F5
  key_array[28] = 0xC7;   // F6
  key_array[30] = 0xC8;   // F7
  key_array[32] = 0xC9;   // F8
  key_array[34] = 0xCA;   // F9
  key_array[36] = 0xCB;   // F10
  key_array[38] = 0xCC;   // F11
  key_array[40] = 0xCD;   // F12
  key_array[42] = 0xD2;   // Home
  key_array[44] = 0xD8;   // Left Arrow
  key_array[46] = 0xD6;   // Page Down
  key_array[48] = 0xD3;   // Page Up
  key_array[50] = 0xD7;   // Right Arrow
  key_array[52] = 0x81;   // Left Shift
  key_array[54] = 0x20;   // Space
  key_array[56] = 0xB3;   // Tab
  key_array[58] = 0xDA;   // Up Arrow
  key_array[60] = 0x86;   // Right Alt
  key_array[62] = 0x84;   // Right Ctrl
  key_array[64] = 0x83;   // Left Command (Windows Key)
  key_array[66] = 0x87;   // Right Command (Varies, but Windows Key Right)
  key_array[68] = 0x61;   // A
  key_array[70] = 0x62;   // B
  key_array[72] = 0x63;   // C
  key_array[74] = 0x64;   // D
  key_array[76] = 0x65;   // E
  key_array[78] = 0x66;   // F
  key_array[80] = 0x67;   // G
  key_array[82] = 0x68;   // H
  key_array[84] = 0x69;   // I
  key_array[86] = 0x6A;   // J
  key_array[88] = 0x6B;   // K
  key_array[90] = 0x6C;   // L
  key_array[92] = 0x6D;   // M
  key_array[94] = 0x6E;   // N
  key_array[96] = 0x6F;   // O
  key_array[98] = 0x70;   // P
  key_array[100] = 0x71;  // Q
  key_array[102] = 0x72;  // R
  key_array[104] = 0x73;  // S
  key_array[106] = 0x74;  // T
  key_array[108] = 0x75;  // U
  key_array[110] = 0x76;  // V
  key_array[112] = 0x77;  // W
  key_array[114] = 0x78;  // X
  key_array[116] = 0x79;  // Y
  key_array[118] = 0x7A;  // Z
  key_array[120] = 0x60;  // `
  key_array[122] = 0x31;  // 1
  key_array[124] = 0x32;  // 2
  key_array[126] = 0x33;  // 3
  key_array[128] = 0x34;  // 4
  key_array[130] = 0x35;  // 5
  key_array[132] = 0x36;  // 6
  key_array[134] = 0x37;  // 7
  key_array[136] = 0x38;  // 8
  key_array[138] = 0x39;  // 9
  key_array[140] = 0x30;  // 0
  key_array[142] = 0x2D;  // -
  key_array[144] = 0x3D;  // =
  key_array[146] = 0x5B;  // [
  key_array[148] = 0x5D;  // ]
  key_array[150] = 0x5C;  // '\'
  key_array[152] = 0xC1;  // Caps Lock
  key_array[154] = 0x3B;  // ;
  key_array[156] = 0x27;  // '
  key_array[158] = 0x2C;  // ,
  key_array[160] = 0x2E;  // .
  key_array[162] = 0x2F;  // /
  key_array[164] = 0xD1;  // Insert
  key_array[166] = 0xF0;  // F13
  key_array[168] = 0xF1;  // F14
  key_array[170] = 0xF2;  // F15
  key_array[172] = 0xF3;  // F16
  key_array[174] = 0xF4;  // F17
  key_array[176] = 0xF5;  // F18
  key_array[178] = 0xF6;  // F19
  key_array[180] = 0xF7;  // F20
  key_array[182] = 0x85;  // Right Shift


  // Begin Mouse and Keyboard Movement
  Mouse.begin();
  Keyboard.begin();

  Serial.begin(9600);


  // Begin I2C Bus
  Wire.begin(9);             // join i2c bus with address #4
  Wire.onReceive(receiveEvent); // register event
}


void loop()
{
  // Allow for a little time to process between data inputs
  switch (action) {
    case 1: // Keyboard Key Pressed
      if (recieved_data) {
        Serial.print("Keyboard Key Pressed: ");
        Serial.println(key_in);
      }
      Keyboard.press(key_array[key_in]);
      break;
    case 2: // Keyboard Key Released
      if (recieved_data) {
        Serial.print("Keyboard Key Released: ");
        Serial.println(key_in);
      }
      Keyboard.release(key_array[key_in]);
      break;
    case 3: // Mouse Moved
      if (recieved_data) {
        Serial.print("Mouse Moved: ");
        Serial.print(mouse_x);
        Serial.print(", ");
        Serial.println(mouse_y);
      }
      Mouse.move(mouse_x, mouse_y, 0);
      break;
    case 4: // Mouse Click Pressed
      if (key_in > 1) { // Edge case for Left click
        key_in -= 1;
      }
      if (recieved_data) {
        Serial.print("Mouse Click Pressed: ");
        Serial.println(key_in);
      }
      Mouse.press(key_in);
      break;
    case 5: // Mouse Click Released
      if (key_in == 0) { // Edge case for Left click
          key_in += 1;
      }
      if (recieved_data) {
        Serial.print("Mouse Click Released: ");
        Serial.println(key_in);
      }
      Mouse.release(key_in);
      break;
    case 6: // Mouse Scroll
      if (recieved_data) {
        Serial.print("Mouse Scroll: ");
        Serial.println(mouse_y);
      }
      Mouse.move(0, 0, mouse_y);
      break;
    default:
      break;
  }
  recieved_data = 0;
  key_in = 0;
  mouse_x = 0;
  mouse_y = 0;
  delay(10);
}


// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(int howMany)
{
  while(Wire.available() > 0) // loop through all avaliable
  {
    // Get Object Type
    action = 0;
    char test = Wire.read();
    // char trash;
    // trash = Wire.read();
    // Wire.read();

    type_in = static_cast<uint8_t>(test); // receive byte
    Serial.print("I just got in unit_8: ");
    Serial.println(type_in);
    // Serial.print("I just got in char: ");

    // Serial.println(test);


    // Print Serial Debug
    //recieved_data = 1;


    // Keyboard Events
    if (type_in == 1) {
      key_in = static_cast<uint8_t>(Wire.read());
      action = 2;
      Serial.print("Key in is");
      Serial.println(key_in);

      if (key_in & 0x01 == 1) { // If odd, Key is pressed
        action -= 1;
        key_in -= 1;
      }
    }
    // Mouse Move Events
    else if (type_in == 2) {
        mouse_x = Wire.read();
        mouse_y = Wire.read();
        action = 3;
    }
    // Mouse Click Events
    // Arduino codes for Mouse clicks:  Left=1, Right=2, Middle=4.
    else if (type_in == 3) {
      key_in = Wire.read();
      action = 5;
      if (key_in & 0x01 == 1) { // If odd, Key is pressed.
        action -= 1;
      }
    }
    // Mouse Scroll Events
    else if (type_in == 4) {
        mouse_y = Wire.read();
        action = 6;
    Wire.read();
    }
  }
}
