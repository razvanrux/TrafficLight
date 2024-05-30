# TrafficLight

This project was created in 2 days using a Raspberry Pi 5 combined with Arduino Nano for managing a Smart Traffic light, both for cars and pedestrians.

Time wasted: 14 hours

Neurons lost: I also lost count of the neurons lost, so it's a lot.

<!-- Project replication -->
## How to replicate this project?

You will need the following components:

- Raspberry Pi (you can use any model, I used RPi 5 with 8GB RAM)
- Arduino Nano
- Colored LEDs, resistors, wires (You can use a Plusivo Kit or buy its contents piece by piece)

<!-- Programs used -->
## Programs Used

- Thonny (Python - already installed on my RPi)
- Arduino IDE

<!-- Connection tutorial -->
## Connection Guide

### Raspberry Pi:
![Raspberry Pi Connection Diagram](RPI5.png)

- **Ground1** (1st board, for all LEDs/Buttons)
- **GPIO14 TXD** (Arduino RX)
- **GPIO15 RXD** (Arduino TX)
- **GPIO25** (Red LED CAR)
- **GPIO8** (Yellow LED CAR)
- **GPIO7** (Green LED CAR)
- **GPIO21** (Start Button)
- **GPIO2** (Red LED PED)
- **GPIO3** (Green LED PED)

### Arduino Nano:
![Arduino Nano Connection Diagram](Arduino_Nano.jpg)

- **D12** (Blue counter LED)
- **D11** (White confirmation LED)
- **D4** (Counter Button)
- **D3** (Confirmation Button)
- **RX** (RPi TX)
- **TX** (RPi RX)
- **GND** (2nd board, for Arduino/Buttons/LEDs)

![Components Used](Stuff_Used.jpg)

More information can be found in the code comments, where you'll find the project configurations, etc.
