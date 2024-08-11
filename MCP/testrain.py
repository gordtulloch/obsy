import serial
import time

port = "/dev/ttyUSB1"
bps=9600
ser = serial.Serial(port,bps,timeout=1)
time.sleep(5)
ser.write(b"S#")
time.sleep(5)
ser.flush()
time.sleep(6)
print(ser.readline())

