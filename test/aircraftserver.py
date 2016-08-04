import socket
from sys import exit
import time

DATA = b"<MODESMESSAGE><DATETIME>20080214203621</DATETIME><MODES>400618</MODES><ALTITUDE>26000</ALTITUDE><VRATE>0</VRATE><LATITUDE>52.6305</LATITUDE><LONGITUDE>-3.0139</LONGITUDE></MODESMESSAGE>"

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