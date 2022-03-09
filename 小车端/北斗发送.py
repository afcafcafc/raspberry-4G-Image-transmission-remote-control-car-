#!/usr/bin/env python
# -*- coding: utf-8 -*-
from json.tool import main
import serial
import socket
serialPort = "/dev/ttyUSB2"
baudRate = 38400
ser = serial.Serial(serialPort, baudRate, timeout=0.5)
print("serial port is %s ,baudRate is %d" % (serialPort, baudRate))
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip_port = ('你的服务器ip', 3392)
while True:
    try:
        data=ser.readline()
        print(data.decode())
        client.sendto(data, ip_port)
    except:
        print('error')