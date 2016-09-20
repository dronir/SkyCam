import socket
from sys import exit
import time
from datetime import datetime
from math import sin, pi

# This program starts a server on port 7879, sending the same piece of XML
# flight date every second. This can be used as a simple test server for
# aircraft.py

Hlat = 60.217165
Hlon = 24.394562

DATA1 = "<MODESMESSAGE><DATETIME>{}</DATETIME><MODES>400F2B</MODES><CALLSIGN>OVW84</CALLSIGN><ALTITUDE>10000</ALTITUDE><GROUNDSPEED>451</GROUNDSPEED><TRACK>90</TRACK><VRATE>0</VRATE><AIRSPEED></AIRSPEED><LATITUDE>{:.6f}</LATITUDE><LONGITUDE>{:.6f}</LONGITUDE></MODESMESSAGE>"
DATA2 = "<MODESMESSAGE><DATETIME>{}</DATETIME><MODES>400F2C</MODES><CALLSIGN>OVW84</CALLSIGN><ALTITUDE>10000</ALTITUDE><GROUNDSPEED>451</GROUNDSPEED><TRACK>90</TRACK><VRATE>0</VRATE><AIRSPEED></AIRSPEED><LATITUDE>60.217165</LATITUDE><LONGITUDE>24.394562</LONGITUDE></MODESMESSAGE>"



def position(T0):
    dT = time.monotonic() - T0
    T = (dT % 15.0) / 15.0
    lat = Hlat - 0.02
    lon = Hlon + 0.02 * sin(2*pi*T)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return timestamp, lat, lon

def serve():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 7879))
    sock.listen(5)
    print("Listening")
    try:
        while True:
            (clientsocket, address) = sock.accept()
            print("Connection from {}".format(address))
            T0 = time.monotonic()
            while True:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                message1 = bytes(DATA1.format(*position(T0)), "utf-8")
                message2 = bytes(DATA2.format(timestamp), "utf-8")
                try:
                    clientsocket.send(message1)
                    #clientsocket.send(message2)
                except BrokenPipeError:
                    print("Lost connection")
                    break
                time.sleep(0.2)
    except KeyboardInterrupt:
        sock.close()
        exit()

if __name__=="__main__":
    serve()
