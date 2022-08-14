# ThermoPi OS for hydronic heating
# Version: 1.0
# Updated:
# Uses Raspberry Pi, DS18B20 one wire sensors, hydronic heating, 3 zones currently
# Items needed:
# Turn on and off heat
# Tell when heat was turned on and turned off
# Add in Apple Homekit
# log total heating time per day, week month, year
# Create chart of heating times

import glob
import time
import RPi.GPIO as GPIO
import os
import subprocess
#import /home/pi/ThermoPi/homekit.py
#from subprocess import*

#subprocess.call("/home/pi/ThermoPi/homekit", shell=True)
#p = open([r'/home/pi/ThermoPi/homekit.py', "ArcView"])
#output = p.communicate()
#print(output[0])

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

#Sensor Setup
base_dir = '/sys/bus/w1/devices/'
MBR_folder = glob.glob(base_dir + '28-00000de8f995')[0]
MF_folder = glob.glob(base_dir + '28-00000de9525b')[0]
UF_folder = glob.glob(base_dir + '28-00000dea8b78')[0]
MBR_file = MBR_folder + '/w1_slave'
MF_file = MF_folder + '/w1_slave'
UF_file = UF_folder + '/w1_slave'

#Zones
Zone_Name = ["Master Bedroom", "Main Floor", "Upper Floor"]
Zone = [MBR_file, MF_file, UF_file]

# Specifications/ Temps
Zone_high = [73, 73, 74]  #MAX temperature of zone
Zone_low = [68, 69, 70]  #MIN temperature of zone
Zone_time = [900, 900, 900] #seconds of time have per zone will run
Zone_Status = [0, 0, 0] #Status of heating, 0 = not on, 1 = already on
Zone_On_Time = [0,0,0]  # What time did the zone turn on?
Zone_Off_Time = [0,0,0] # What time did the zone turn off?
Zone_Switch = [1, 1, 1] # Is this unit turned on or off? 0 = off, 1 = on
Zone_available = [1,1,1] #Is this unit available or resting?  0 = no, 1 = yes
Zone_Wait = 300 # dwell time between run times
Temp_dwell = 1 #time between measurements 

#Relay setup
Relay = [25, 12, 20]
GPIO.setup(Relay[0], GPIO.OUT) # GPIO Assign mode
GPIO.setup(Relay[1], GPIO.OUT) # GPIO Assign mode
GPIO.setup(Relay[2], GPIO.OUT) # GPIO Assign mode
GPIO.output(Relay[0], GPIO.LOW) # out
GPIO.output(Relay[1], GPIO.LOW) # out
GPIO.output(Relay[2], GPIO.LOW) # out



# Function for reading DS18B20 Sensors, get values
def read_temp(sensor):
    while True: 
        f = open(sensor, 'r')
        lines = f.readlines()
        #print(lines)
        f.close()
        t_value = lines[1].find('t=')
        temp_string = lines[1][t_value+2:]
        #print(temp_string)
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        #print(temp_f)
        round(temp_f, 3)
        return temp_f
        break

    # f = open(sensor, 'r')
    # lines = f.readlines()
    # #print(lines)
    # f.close()

    # if lines[0].strip()[-3:] == 'YES':
    #     #print("good data")
    #     t_value = lines[1].find('t=')
    #     if t_value != -1:
    #         temp_string = lines[1][t_value+2:]
    #         print(temp_string)
    #         temp_c = float(temp_string) / 1000.0
    #         temp_f = temp_c * 9.0 / 5.0 + 32.0
    #         #print(temp_f)
    #         round(temp_f, 3)
    #         return temp_f
    #     else:
    #         print("bad temp data")
    #         read_temp(sensor)
    # else:
    #     print("Sensor says no")
    #     read_temp(sensor)

# Function for turning on or off heat
def hvac(sensor,i):
    # Turn on heating if conditions are met
    if read_temp(sensor) <= Zone_low[i] and Zone_Status[i] == 0 and Zone_Switch[i] == 1 and (time.monotonic() - Zone_Off_Time[i]) >= Zone_Wait:
        GPIO.output(Relay[i], GPIO.HIGH)
        Zone_Status[i] = 1
        Zone_On_Time[i] = time.monotonic()
        print("Heat Turned on for", Zone_Name[i])
        #print (time.ctime())

    # Turn off heating if temperature range has been achieved 
    if read_temp(sensor) >= Zone_high[i] and Zone_Status[i] == 1:
        GPIO.output(Relay[i], GPIO.LOW)
        Zone_Status[i] = 0
        Zone_Off_Time[i] = time.monotonic()
        print("Heat Turned off for", Zone_Name[i],"temperature achieved")
        #print (time.ctime())

    #Turn off heating if run time is greater than desired
    if (time.monotonic() - Zone_On_Time[i]) >= Zone_time[i] :
        GPIO.output(Relay[i], GPIO.LOW)
        Zone_Status[i] = 0
        Zone_Off_Time[i] = time.monotonic()
        #Zone_Switch[i] = 0  #make the unit unavailable 
        print("Heat Turned off for", Zone_Name[i],"for being greater than run time desired")
        #print (time.ctime())

####################### The Loop  ################################
while True:
    # Read temps from sensors and turn on heat if needed and wanted 
    for i in range(3):
        read_temp(Zone[i])
        hvac(Zone[i],i)

    print(time.ctime())
    for i in range(3):
        print(Zone_Name[i],":", read_temp(Zone[i]),"F   Zone Status:", Zone_Status[i])
    print()
    time.sleep(Temp_dwell)



