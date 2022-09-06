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
from ds18b20 import DS18B20
import os
import subprocess
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#from itertools import count

#import homekit

#Homekit setup 
from subprocess import*
subprocess.call("/home/pi/ThermoPi/homekit", shell=True)
p = open([r'/home/pi/ThermoPi/homekit.py', "ArcView"])
output = p.communicate()
print(output[0])

#Sensor Setup and zones
#base_dir = '/sys/bus/w1/devices/'
#MBR_folder = glob.glob(base_dir + '28-00000de8f995')[0]
#MF_folder = glob.glob(base_dir + '28-00000de9525b')[0]
#UF_folder = glob.glob(base_dir + '28-00000dea8b78')[0]
#MBR_file = MBR_folder + '/w1_slave'
#MF_file = MF_folder + '/w1_slave'
#UF_file = UF_folder + '/w1_slave'
Zone = [DS18B20("00000de8f995"), DS18B20("00000de9525b"), DS18B20("00000dea8b78")]
Zone_Name = ["Master Bedroom", "Main Floor", "Upper Floor"]
#Zone = [MBR_file, MF_file, UF_file]

# Specifications/ Temps
Zone_temp = [ 68, 68, 68] #zone temps
Zone_high = [73, 73, 74]  #MAX temperature of zone
Zone_low = [68, 69, 70]  #MIN temperature of zone
Zone_time = [40, 20, 9] #seconds of time have per zone will run
Zone_Status = [0, 0, 0] #Status of heating, 0 = not on, 1 = already on
Zone_On_Time = [0,0,0]  # What time did the zone turn on?
Zone_Off_Time = [0,0,0] # What time did the zone turn off?
Zone_Switch = [1, 1, 1] # Is this unit turned on or off? 0 = off, 1 = on
Zone_available = [1,1,1] #Is this unit available or resting?  0 = no, 1 = yes
Zone_Wait = 30 # dwell time between run times
Temp_dwell = 15 #time between measurements 

#Plot data live
#plt.ion()
x = []  #time
y = []  #zone temp 0
z = []  #zone temp 1
v = []  #zone temp 2 
zs0 = []    #zone status 0
zs1 = []    #zone status 1
zs2 = []    #zone status 2 

# fig = plt.subplots(figsize =(12,6))
# ax1 = plt.subplot(121)
# ax2 = plt.subplot(122)

fig, ax = plt.subplots()





#index = count()

# Create a blank line. We will update the line in animate
#line, = ax1.plot(x, y)

# This function is called periodically from FuncAnimation
# def animate(i):

#     # Limit y list to set number of items
#     y = y[-30:]

#     ax1.clear()
#     ax1.plot(x, y, label= Zone_Name[0], color='m')
#     ax1.plot(x,z, label= Zone_Name[1], color='r')
#     ax1.plot(x, v, label= Zone_Name[2], color='g')
#     ax2.plot(x, zs0, label= Zone_Name[0], color='y')
#     ax2.plot(x,zs1, label= Zone_Name[1], color='k')
#     ax2.plot(x, zs2, label= Zone_Name[2], color='c')
#     ax1.set_title('Temps')
#     ax1.set_xlabel('Time') 
#     ax1.set_ylabel('Temperature (F)')
#     ax1.legend()
#     ax1.grid()
#     ax2.set_title('Run Time')
#     ax2.set_xlabel('Time')
#     ax2.set_ylabel('Zone Status')
#     ax2.set_ylim(-1,2)
#     ax2.legend()
#     ax2.grid()  

#plt.style.use('fivethirtyeight')
# Set up plot to call animate() function periodically
#ani = animation.FuncAnimation(fig, animate, fargs=(y,), interval=50, blit=True)
#plt.show()
# def animate(i):
    #data = pd.read_csv('ThermoPi2022.csv')
    #x_values = data['Time']
    #y_values = data['Price']
    # plt.cla()
    # plt.plot(x, y)
    # plt.xlabel('Time')
    # plt.ylabel('Price')
    # plt.title('Infosys')
    # plt.gcf().autofmt_xdate()
    # plt.tight_layout()

# ani = FuncAnimation(plt.gcf(), animate, 5000)

# Pi board setup
GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

#Relay setup
Relay = [25, 12, 20]
GPIO.setup(Relay[0], GPIO.OUT) # GPIO Assign mode
GPIO.setup(Relay[1], GPIO.OUT) # GPIO Assign mode
GPIO.setup(Relay[2], GPIO.OUT) # GPIO Assign mode
GPIO.output(Relay[0], GPIO.LOW) # out
GPIO.output(Relay[1], GPIO.LOW) # out
GPIO.output(Relay[2], GPIO.LOW) # out


# Function for reading DS18B20 Sensors, get values
#def read_temp(sensor):
    #while True:
        #f = open(sensor, 'r')
        #lines = f.readlines()
        #print(lines)
        #f.close()
        #if len(lines) > 1:
        #    t_value = lines[1].find('t=')
        #else:
        #    time.sleep(1)
        #    read_temp(sensor)
        #print("t value failed trying again")
        #temp_string = lines[1][t_value+2:]
        #read_temp(sensor)
        #print("temp_string failed trying again")
        #print(temp_string)
        #temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        #temp_f = 55
        #print(temp_f)
        #round(temp_f, 3)
        #return temp_f
        #break

# Function for turning on or off heat
def hvac(sensor,i):
    # Turn on heating if conditions are met
    if Zone_temp[i] <= Zone_low[i] and Zone_Status[i] == 0 and Zone_Switch[i] == 1 and (time.monotonic() - Zone_Off_Time[i]) >= Zone_Wait:
        GPIO.output(Relay[i], GPIO.HIGH)
        Zone_Status[i] = 1
        Zone_On_Time[i] = time.monotonic()
        print("Heat Turned on for", Zone_Name[i],"at",Zone_On_Time[i])
        #print (time.ctime())

    # Turn off heating if temperature range has been achieved 
    if Zone_temp[i] >= Zone_high[i] and Zone_Status[i] == 1:
        GPIO.output(Relay[i], GPIO.LOW)
        Zone_Status[i] = 0
        Zone_Off_Time[i] = time.monotonic()
        print("Heat Turned off for", Zone_Name[i],"temperature achieved","at",Zone_Off_Time[i])
        #print (time.ctime())

    #Turn off heating if run time is greater than desired
    if Zone_Status[i] == 1 and (time.monotonic() - Zone_On_Time[i]) >= Zone_time[i]:
        GPIO.output(Relay[i], GPIO.LOW)
        Zone_Status[i] = 0
        Zone_Off_Time[i] = time.monotonic()
        #Zone_Switch[i] = 0  #make the unit unavailable 
        print("Heat Turned off for", Zone_Name[i],"for being greater than run time desired at",Zone_Off_Time[i])
        #print (time.ctime())

    #Make unit available again 
    if (time.monotonic() - Zone_Off_Time[i]) >= Zone_Wait:
        Zone_available[i] = 1

####################### The Loop  ################################
# Create CSV to log ThermoPi Data
header = ['Time',"Zone Name","Zone Temp (f)","Status","Zone Name","Zone Temp (f)","Status","Zone Name","Zone Temp (f)","Status"]
with open("/home/pi/ThermoPi/ThermoPi2022.csv","w") as log:
    writer = csv.writer(log)
    writer.writerow(header)

    while True:
        # Read temps from sensors and turn on heat if needed and wanted 
        for i in range(3):
            #read_temp(Zone[i])
            try:
                Zone_temp[i] = Zone[i].get_temperature(DS18B20.DEGREES_F)
                pass
            except IndexError:
                print("Bad Value, try again . . . ")
                time.sleep(5)
            hvac(Zone[i],i)

        #Serial print for debug
        print(time.ctime())
        for i in range(3):
            print(Zone_Name[i],":", Zone_temp[i],"F   Zone Status:", Zone_Status[i])
        print()

        #Matplot for live viewing
        #clear previous plot
        
        y.append(Zone_temp[0])
        z.append(Zone_temp[1])
        v.append(Zone_temp[2])
        x.append(time.ctime())
        zs0.append(Zone_Status[0])
        zs1.append(Zone_Status[1])
        zs2.append(Zone_Status[2])

        
        line, = ax.plot(x, y)
            
        def animate(i):
            line.set_ydata(y)
            return line,
        #plt.tight_layout()
        #plt.show()
        ani = animation.FuncAnimation(
            fig, animate, interval = 20, blit=True, save_count=50)

        plt.pause(0.05)
        #plt.draw()
        plt.show()



        #Saving data to file or database
        data = [time.ctime(),Zone_Name[0],Zone_temp[0],Zone_Status[0],Zone_Name[1],Zone_temp[1],Zone_Status[1],Zone_Name[2],Zone_temp[2],Zone_Status[2]]
        writer.writerow(data)
        log.flush()

        #Dwell between measurements
        time.sleep(Temp_dwell)



