#!/usr/bin/env python3
import serial
from threading import *
import socket
import time
import json

SPLIT_CHAR = "|"
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 10001        # Websocket port

if __name__ == '__main__':
    dict_of_temps = {}
    # daemon
    def scanReadAndParseSerial():
        SERIAL_CONNECT = False
        
        # reads port on which arduino is connected
        with open('serial_tty.txt', 'r') as tty_read:
            tty = tty_read.read()[:-1]
        
        # waits for arduino to connect        
        while not SERIAL_CONNECT:        
            # opens serial connection with arduino
            try:    
                ser = serial.Serial(tty, 9600, timeout=1)
                ser.reset_input_buffer()
            except:
                print("Arduino not connected or wrong serial device supplied. Retrying in 5 seconds...")
                time.sleep(5)
                continue
                
            SERIAL_CONNECT = True
        
        # init global variables
        global dict_of_temps
        
        # main loop
        while True:
            if ser.in_waiting > 0:
                # reads data from usb serial, gets header, content, and checksum
                msg = ser.readline().decode('utf-8').rstrip()
                header = msg[0]
                content = msg.split("C")[0][1:]
                chksum = msg.split("C")[1]
                
                # calculate checksum
                ch = 0
                for x in (header + content):
                    ch ^= ord(x)
                        
                print(ch)
                    
                # throw out data if checksum ddoen't match
                if ch == chksum:
                    if header == "T":
                        content_divider_split = content.split(SPLIT_CHAR)
                        dict_of_temps = dict(zip((x[0] for x in content_divider_split), (x[1:] for x in content_divider_split)))
                        print(dict_of_temps)
    
    # spawns read code as daemon        
    s_daemon = Thread(target=scanReadAndParseSerial)
    s_daemon.start()
    
    # start socket
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    conn.sendall(str(json.dumps(dict_of_temps, indent = 4)).encode())
                    time.sleep(5)
            
