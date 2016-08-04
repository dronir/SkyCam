import socket
from sys import exit
import time

DATA = b"<MODESMESSAGE><DATETIME>20070622141943</DATETIME><MODES>400F2B</MODES><CALLSIGN>BAW134</CALLSIGN><ALTITUDE>120300</ALTITUDE><GROUNDSPEED>451</GROUNDSPEED> <TRACK>234</TRACK><VRATE>0</VRATE><AIRSPEED></AIRSPEED><LATITUDE>-14.1102</LATITUDE><LONGITUDE>-31.5789</LONGITUDE></MODESMESSAGE>"

def serve():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 7879))
    sock.listen(5)
    print("Listening")
    while True:
        try:
            (clientsocket, address) = sock.accept()
        except KeyboardInterrupt:
            exit()
        while True:
            try:
                clientsocket.send(DATA)
            except BrokenPipeError:
                break
            time.sleep(1)

if __name__=="__main__":
    serve()