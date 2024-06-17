from gpiozero import Button, TrafficLights
import os
import serial
import time
from time import sleep
from flask import Flask, request, jsonify, send_from_directory
import logging

########################################################################################
# THIS NEEDS TO BE CHANGED depending on the port that you're using
# Should be the same as what you had in Arduino IDE!
ser = serial.Serial('/dev/ttyUSB0', 9600)
########################################################################################

button = Button(21, hold_time=2)
global res_check
res_check = 0  # used for resetting the Traffic Light (same button that you start it with)

car_lights = TrafficLights(25, 8, 7)
ped_lights = TrafficLights(2, 26, 3)  # GPIO26 will NOT be used since no yellow lights needed for ppl

global car_red  # number of seconds that cars need to wait & pedestrians are allowed to go
c_red = 10

global car_green  # number of seconds that cars can go and pedestrians have to wait
c_green = 10
global data
global nrp
global nrc
global standby

standby = 0
nrc = 0
nrp = 0

temp = 0

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def update_display():
    clear_console()
    if sw == 0:
        print("Number of pedestrians waiting: " + str(nrp) + " <-")
        print("Number of cars waiting: " + str(nrc))
    elif sw == 1:
        print("Number of pedestrians waiting: " + str(nrp))
        print("Number of cars waiting: " + str(nrc) + " <-")

# cars have red light while people have green, with a nice animation when ppl have <5 seconds
def car_red(s):
    car_lights.red.on()
    ped_lights.red.off()
    ped_lights.green.on()
    while (s > 5):
        s = s - 1
        sleep(1)
    while (s < 6 and s != 0):
        sleep(0.5)
        s = s - 0.5
        if (s * 10 % 10 == 5):
            ped_lights.green.on()
        if (s * 10 % 10 != 5):
            ped_lights.green.off()
    ped_lights.green.off()
    ped_lights.red.on()
    sleep(2)
    car_lights.amber.on()


def car_green(s):
    car_lights.red.off()
    car_lights.amber.off()
    car_lights.green.on()
    ped_lights.red.on()
    while (s != 0):
        s = s - 1
        sleep(1)
    car_lights.green.off()
    car_lights.amber.on()
    sleep(2)
    car_lights.amber.off()
    car_lights.red.on()

def normal_cycle():
    res_check=0
    if (button.is_pressed):
        print("Traffic light scheduled stop!\n")
        res_check = 1
    car_red(10)
    if (button.is_pressed):
        print("Traffic light scheduled stop!\n")
        res_check = 1
    car_green(15)
    if (button.is_pressed):
        print("Traffic light scheduled stop!\n")
        res_check = 1
    if (res_check == 0):
        normal_cycle()
    

def cycle():
    global res_check
    global c_green
    global c_red
    global nrp
    global nrc
    global data
    global standby
    # 0 - there are cars / pedestrians, traffic light is enabled
    # 1 - no people, first check
    # 2 - no cars, second check
    # 3 - traffic light disabled
    global temp
    global sw #used for deciding whether cars or pedestrians are activating the system
    #0 -pedestrians
    #1 - cars

    if (standby == 3):
        car_lights.amber.off()
        car_lights.red.off()
        car_lights.green.off()
        ped_lights.red.off()
        ped_lights.green.off()
        temp = 0
        sw=0
        while (temp == 0):
            update_display()
            car_lights.amber.on()
            sleep(0.5)
            car_lights.amber.off()
            sleep(0.5)
            if ser.in_waiting > 0:
                data = ser.read()
                if data == b'1':
                    nrp += 1
                    update_display()
                elif (data == b'2' and nrp != 0):
                    temp = 1
        clear_console()
        sleep(1)

    if (standby != 2):
        if (c_green != 0):
            car_green(c_green)

        if (nrc < c_green):
            nrc = 0
        else:
            nrc = nrc - c_green

    temp = 0
    sw=0
    while (temp == 0):
        update_display()
        data = ser.read()
        if data == b'1':
            nrp += 1
            update_display()
        if data == b'2':
            temp = 1

    if (button.is_pressed):
        print("Traffic light scheduled stop!\n")
        res_check = 1

    if (nrp <= 20 and nrp != 0):
        c_red = 10
        print("Cars waiting 10 seconds!")
        standby = 0
    elif (nrp > 20):
        c_red = 15
        print("Cars waiting 15 seconds!")
        standby = 0
    else:
        print("No people!")
        if (standby !=3):
            if (standby == 2):
                standby = 3
            else:
                standby = 1

    sleep(1)
    clear_console()

    if (standby != 1):
        if (c_red != 0):
            car_red(c_red)

        if (nrp < c_red * 2):
            nrp = 0
        else:
            nrp = nrp - c_red * 2

    temp = 0
    sw=1
    while (temp == 0):
        update_display()
        data = ser.read()
        if data == b'1':
            nrc += 1
            update_display()
        if data == b'2':
            temp = 1

    if (button.is_pressed):
        res_check = 1

    if (nrc < 10 and nrc != 0):
        print("People wait 15 seconds!")
        c_green = 15
        standby = 0
    elif (nrc > 10):
        print("People wait 20 seconds!")
        c_green = 20
        standby = 0
    else:
        print("No cars!")
        if (standby !=3):
            if (standby == 1):
                standby = 3
            else:
                standby = 2

    sleep(1)
    clear_console()

    if (res_check == 0):
        cycle()

    if (res_check != 0):
        car_lights.red.off()
        car_lights.amber.off()
        car_lights.green.off()
        ped_lights.red.off()
        ped_lights.green.off()
        res_check = 1


# Set up Flask app
app = Flask(__name__)

# Disable Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/add', methods=['POST'])
def add():
    global nrp, nrc, standby, temp
    if sw == 0:  # Adding pedestrians
        nrp += 1
    elif sw == 1:  # Adding cars
        nrc += 1
    update_display()
    return jsonify(success=True)

@app.route('/confirm', methods=['POST'])
def confirm():
    temp = 1
    return jsonify(success=True)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


def main():
    global smart # 0 no, 1 yes
    import threading
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False))
    flask_thread.daemon = True
    flask_thread.start()

    while True:
        clear_console()
        print("Waiting for Start button")
        button.wait_for_press()
        if button.is_pressed:
            start_time = time.time()
            while button.is_pressed and (time.time() - start_time) < 2:
                pass  # Wait until the button is released or 2 seconds elapsed

            if not button.is_pressed:  # Short press detected
                print("Button engaged! Starting smart mode...")
                cycle()  # Start smart mode
            else:  # Long press detected
                print("Button held down! Normal mode")
                while button.is_pressed:
                    pass
            normal_cycle()

        time.sleep(0.1)  # Add a small delay to debounce the button and reduce CPU load


if __name__ == "__main__":
    main()
