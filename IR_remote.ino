//Simple script that will make some LEDs blink that confirm the fact that the buttons work
//Arduino will send two signals - 1 or 2 - depending on what button was pressed
//Made by Razvan Ruxandari for SM Project

// HOW TO CONFIG:
// Considering that you're working in Arduino IDE like I did, 
// the following settings need to be done:
// 
// Tools -> Board -> Arduino Nano
// Tools -> Processor -> ATMega328(old bootloader) 
//-the new one won't work without external programmer
// Tools -> Port -> /dev/ttyUSB[port_number]

#define BUTTON_PIN_1 4
#define BUTTON_PIN_2 3
#define LED_PIN_1 12
#define LED_PIN_2 11

int button1PressCount = 0;
int button2PressCount = 0;

void setup() {
  Serial.begin(9600);
  pinMode(BUTTON_PIN_1, INPUT_PULLUP);
  pinMode(BUTTON_PIN_2, INPUT_PULLUP);
  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
}

void loop() {
  // Button 1 handling
  if (digitalRead(BUTTON_PIN_1) == LOW) {
    digitalWrite(LED_PIN_1, !digitalRead(LED_PIN_1)); // Toggle LED 1
    button1PressCount++; // Increment button 1 press count
    Serial.write('1'); // Send signal to Raspberry Pi
    delay(100); // Debounce delay
  }

  // Button 2 handling
  if (digitalRead(BUTTON_PIN_2) == LOW) {
    digitalWrite(LED_PIN_2, !digitalRead(LED_PIN_2)); // Toggle LED 2
    button2PressCount++; // Increment button 2 press count
    Serial.write('2'); // Send signal to Raspberry Pi
    delay(100); // Debounce delay
  }
}
