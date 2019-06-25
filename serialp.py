import serial 
import time

ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/ttyACM0'
ser.open()
time.sleep(2)
ser.write(('A\n').encode('cp1250'))
while 1:
	print(ser.readline())