import socket
import xml.etree.ElementTree as ET

class AircraftHandler:
    def __init__(self):
        pass
    def handle(self, events):
        for event_type, element in events:
            if event_type == "start":
                print("{}: {}".format(element.tag, element.text))
        

class AircraftListener:
    def __init__(self, config, handler):
        self.handler = handler
        self.port = config["aircraft"]["port"]
        self.address = config["aircraft"]["address"]
        self.parser = ET.XMLPullParser(["start", "end"])

    def listen(self):
        source = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        source.connect((self.address, self.port))
        print("Start aircraft data listener.")
        self.parser.feed("<DATASTREAM>")
        while(1):
            data = source.recv(1024)
            if not data:
                source.close()
                break
            self.parser.feed(data)
            self.handler.handle(self.parser.read_events())
        self.parser.feed("</DATASTREAM>")
        self.handler.close()
        print("Exit aircraft listener.")

if __name__=="__main__":
    conf = {"aircraft": {"port":7879, "address":"localhost"}}
    AH = AircraftHandler()
    AL = AircraftListener(conf, AH)
    AL.listen()
        