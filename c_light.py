# Made by Razvan Ruxandari for SM Project
# This code is provided AS IS, not responsible if you brick your device as I *almost* did a few times

# Before running the python script MAKE SURE that the Arduino Script IS RUNNING without errors!
# But also you will need to change some parts of this code as it follows:


from gpiozero import Button, TrafficLights
import os
import serial
import time
from time import sleep

########################################################################################
# THIS NEEDS TO BE CHANGED depending on the port that you're using
# Should be the same as what you had in Arduino IDE!
ser = serial.Serial('/dev/ttyUSB0', 9600)
########################################################################################

button=Button(21)
global res_check
res_check=0 # used for resetting the Traffic Light (same button that you start it with)

car_lights = TrafficLights(25, 8, 7)
ped_lights = TrafficLights(2, 26, 3) #GPIO26 will NOT be used since no yellow lights needed for ppl

global car_red # number of seconds that cars need to wait & pedestrians are allowed to go
c_red=10

global car_green # number of seconds that cars can go and pedestrians have to wait
c_green=10
global data
global nrp
global nrc
global standby

standby=0
nrc=0
nrp=0

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# cars have red light while people have green, with a nice animation when ppl have <5 seconds
def car_red(s):
    car_lights.red.on()
    ped_lights.red.off()
    ped_lights.green.on()
    while (s>5):
        s=s-1
        sleep(1)
    while (s<6 and s!=0):
        sleep(0.5)
        s=s-0.5
        if (s*10%10==5):
            ped_lights.green.on()
        if (s*10%10!=5):
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
    while (s!=0):
        s=s-1
        sleep(1)
    car_lights.green.off()
    car_lights.amber.on()
    sleep(2)
    car_lights.amber.off()
    car_lights.red.on()


def cycle():
    # DA GLOBAAALS I don't even know if what I wrote here is 100% corect but hey this is not C#
    # Si nu suntem la IP cu Corina sa ne scada 2 puncte
    global res_check
    global c_green
    global c_red
    global nrp
    global nrc
    global data
    global standby
    
    # standby is 3, meaning that there are no ppl or cars, and so the stoplight is not needed,
    # so it will blink yellow until ppl appear. Cars can pass, the lights won't change
    if (standby==3):
        car_lights.amber.off()
        car_lights.red.off()
        car_lights.green.off()
        ped_lights.red.off()
        ped_lights.green.off()
        temp=0
        while(temp==0):
            clear_console()
            print("Number of pedestrians waiting: "+ str(nrp))
            car_lights.amber.on()
            sleep(0.5)
            car_lights.amber.off()
            sleep(0.5)
            # The way that ppl increase here is so funny, you hold the button pressed and they
            # increase once every second. Not wrong, right? no? okay..
            if ser.in_waiting > 0:
                data = ser.read()
                if data == b'1':
                        nrp += 1
                elif (data == b'2' and nrp!=0):
                        temp = 1
        print("Number of pedestrians waiting: "+ str(nrp))
        sleep(1)
    
    
    # cars start first, then pedestrians
    # ONE CAR PER SECOND!
    
    # standby being 2 means that there are no cars - people will always have green
    # (with a small bug that will change the light to red, but immidiately revert)
    if (standby!=2):
        if (c_green!=0):
            car_green(c_green)
        
        if (nrc<c_green):
            nrc=0
        else:
            nrc=nrc-c_green
    
    temp=0
    while (temp==0):
        clear_console()
        print("Number of pedestrians waiting: "+ str(nrp))
        data = ser.read()
        if data == b'1':
            nrp+=1
        if data == b'2':
            temp=1
            
    # Reset attempt nr.1
    if (button.is_pressed):
        print("Traffic light scheduled stop!\n")
        res_check=1
    
    # How much time will cars have to wait
    if (nrp <= 20 and nrp!=0):
        c_red = 10
        print("Few people. Cars will wait 10 seconds!")
        standby=0
    elif (nrp>20):
        print("A lot of people. Cars will wait 15 seconds!")
        c_red = 15
        standby=0
    else:
        print("No people!")
        if (standby==2):
            standby=3
        else:
            standby=1
        
    sleep(1)
    clear_console()
    # standby being 1 means that there are no ppl - cars will always have green
    # (with a small bug that will change the light to red, but immidiately revert)
    if (standby!=1):
        if (c_red!=0):
            car_red(c_red)
        
        #TWO HOOMAN PER SECOND!
        if (nrp<c_red*2):
            nrp=0
        else:
            nrp=nrp-c_red*2
    
    temp=0
    while (temp==0):
        clear_console()
        print("Number of cars waiting: "+ str(nrc))
        data = ser.read()
        if data == b'1':
            nrc+=1
        if data == b'2':
            temp=1
            
    # Reset attempt nr.2
    if (button.is_pressed):
        print("Traffic light scheduled stop!\n")
        res_check=1
        
    #How much time will pedestrians have to wait    
    if (nrc < 10 and nrc!=0):
        print("Few cars. People will wait 15 seconds!")
        c_green = 15
        standby=0
    elif (nrc>10):
        print("A lot of cars. People will wait 20 seconds!")
        c_green = 20
        standby=0
    else:
        print("No cars!")
        if (standby==1):
            standby=3
        else:
            standby=2
        
    sleep(1)
    clear_console()
    
    # Resetting will stop the Traffic Light until you press it again
    if (res_check==0):
        cycle()
    
    # Reset was a success, and so all lights stop and we get back to main() function
    if (res_check!=0):
        car_lights.red.off()
        car_lights.amber.off()
        car_lights.green.off()
        ped_lights.red.off()
        ped_lights.green.off()
        res_check=1
        
    
def main():
    while (True):
        clear_console()
        print("Waiting for Start button")
        button.wait_for_press()
        print("Button engaged! Starting...")
        cycle()

if __name__ == "__main__":
    main()
