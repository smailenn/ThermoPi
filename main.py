import glob
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

#Zones
MBR = "Master Bedroom"
MF = "Main Floor"
UF = "Upper Floor"

#Sensor Setup
base_dir = '/sys/bus/w1/devices/'
MBR_folder = glob.glob(base_dir + '28-00000de8f995')[0]
MF_folder = glob.glob(base_dir + '28-00000de9525b')[0]
UF_folder = glob.glob(base_dir + '28-00000dea8b78')[0]
MBR_file = MBR_folder + '/w1_slave'
MF_file = MF_folder + '/w1_slave'
UF_file = UF_folder + '/w1_slave'

#Relay setup
Relay_MBR = 17
GPIO.setup(Relay_MBR, GPIO.OUT) # GPIO Assign mode


# Specifications
Temp_high = 71 # Deg F
Temp_low = 68
Run_time = 20 #Minutes

def read_temp(sensor):
    f = open(sensor, 'r')
    lines = f.readlines()
    f.close()
    #lines = read_temp_raw(MBR_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f

def MBR_heat():
    GPIO.output(Relay_MBR, GPIO.LOW) # out
    GPIO.output(Relay_MBR, GPIO.HIGH) # on

while True:
    print("Master = ", read_temp(MBR_file), "Main Floor =", read_temp(MF_file), "Upper Floor =", read_temp(UF_file))
    #print(read_temp(MF_file))
    #print(read_temp(UF_file))
    time.sleep(1)