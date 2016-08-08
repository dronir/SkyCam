import socket
from sys import exit
import time
from datetime import datetime

# This program starts a server on port 7879, sending the same piece of XML
# flight date every second. This can be used as a simple test server for
# aircraft.py

DATA = "<MODESMESSAGE><DATETIME>{}</DATETIME><MODES>400F2B</MODES><CALLSIGN>OVW84</CALLSIGN><ALTITUDE>10000</ALTITUDE><GROUNDSPEED>451</GROUNDSPEED><TRACK>90</TRACK><VRATE>0</VRATE><AIRSPEED></AIRSPEED><LATITUDE>{:.6f}</LATITUDE><LONGITUDE>{:.6f}</LONGITUDE></MODESMESSAGE>"



def position(T0):
    dT = time.monotonic() - T0
    T = (dT % 120) / 120
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    lat = 60.21716
    lon = 24.39 + T * 0.1
    return timestamp, lat, lon

def serve():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 7879))
    sock.listen(5)
    print("Listening")
    while True:
        try:
            (clientsocket, address) = sock.accept()
            print("Connection from {}".format(address))
        except KeyboardInterrupt:
            exit()
        T0 = time.monotonic()
        while True:
            message = bytes(DATA.format(*position(T0)), "utf-8")
            try:
                clientsocket.send(message)
            except BrokenPipeError:
                print("Lost connection")
                break
            time.sleep(1)

if __name__=="__main__":
    serve()
