import socket
from sys import exit
import time

DATA = b"<MODESMESSAGE><DATETIME>20070622141943</DATETIME><MODES>400F2B</MODES><CALLSIGN>OVW84</CALLSIGN><ALTITUDE>12030</ALTITUDE><GROUNDSPEED>451</GROUNDSPEED><TRACK>234</TRACK><VRATE>0</VRATE><AIRSPEED></AIRSPEED><LATITUDE>60.0</LATITUDE><LONGITUDE>25.0</LONGITUDE></MODESMESSAGE>"

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
        while True:
            try:
                print("Sending...")
                clientsocket.send(DATA)
            except BrokenPipeError:
                print("Lost connection")
                break
            time.sleep(1)

if __name__=="__main__":
    serve()
