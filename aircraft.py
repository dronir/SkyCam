import socket
import xml.etree.ElementTree as ET
from datetime import datetime
from ephem import separation
from numpy import sqrt, sin, cos, array, cross, eye, dot
from scipy.linalg import expm3, norm

# The AircraftHandler maintains a list of nearby aircraft, from data given by an
# AircraftListener, and draws the aircraft on the given Axes object when
# requested.

# The AircraftListener listens to the AirNav RadarBox XML stream, parsing and
# sending the aircraft updates to an AircraftHandler whenever they arrive.

# Degrees to radians conversion factor
RAD = 0.017453293
KNOTS = 1.94384449 # knots to m/s
FEET = 3.28084 # feet/s to m/s


# The data fields we want to read for each aircraft
USED_DATA_FIELDS = [
    "DATETIME", "MODES", "CALLSIGN", "ALTITUDE", "VRATE",
    "GROUNDSPEED", "TRACK", "LATITUDE","LONGITUDE"
]

# Some Metsähovi coordinates that are needed later
HOVI_LAT = 60.217165
HOVI_LON = 24.394562
HOVI_COORD_RAD = (HOVI_LON*RAD, HOVI_LAT*RAD)

# Construct a matrix to rotate geocentric positions to Metsähovi-centric by rotating
# Metsähovi "to the north pole".
HOVI_ROT = (HOVI_LON + 90)*RAD
HOVI_AXIS = array([cos(HOVI_ROT), sin(HOVI_ROT), 0.0])
HOVI_MATRIX = expm3(cross(eye(3), HOVI_AXIS* ((-90+HOVI_LAT)*RAD)))
HOVI_CART = array([cos(HOVI_LAT*RAD)*cos(HOVI_LON*RAD), 
                   cos(HOVI_LAT*RAD)*sin(HOVI_LON*RAD), 
                   sin(HOVI_LAT*RAD)]) * 6371.0
HOVI_POLE = dot(HOVI_MATRIX, HOVI_CART)


class Aircraft:
    def __init__(self, data):
        self.last_updated = datetime(year=1903, month=12, day=17)
        self.update(data)
        
    def update(self, data):
        """Update aircraft status with received data.
        Give default values for non-critical parameters, if they are missing from
        the broadcast. For critital parameters, mark the aircraft as not 'ok'."""
        update_time = datetime.strptime(data["DATETIME"], "%Y%m%d%H%M%S")
        if update_time <= self.last_updated:
            return
        self.ok = True
        self.modes = data["MODES"]
        self.callsign = data.get("CALLSIGN", "?")
        self.vrate = float(data.get("VRATE", 0.0))
        self.speed = float(data.get("GROUNDSPEED", 0.0))
        self.last_updated = update_time
        self.heading = data.get("TRACK", None) 
        if not self.heading is None:
            self.heading = float(self.heading) * RAD
        try:
            self.lat = float(data["LATITUDE"]) * RAD
            self.lon = float(data["LONGITUDE"]) * RAD
            self.alt = float(data["ALTITUDE"]) * 0.0003048
        except KeyError:
            self.ok = False
            
    def distance(self):
        """Return ground distance from Metsähovi in km."""
        sep = float(separation(HOVI_COORD_RAD, (self.lon, self.lat)))
        return sep * 6371.0
    
    def velocity(self):
        """Return velocity vector in airplace-centric system where X is east."""
        if self.heading is None:
            return (0.0, 0.0, 0.0)
        hoz = self.speed / KNOTS
        vz = self.vrate / FEET
        vx = sin(self.heading) * hoz
        vy = cos(self.heading) * hoz
        return (vx,vy,vz)
    
    def cartesian(self): 
        """Return position in a Metsähovi-centric cartesian system. 
        In the coordinate system X is east, Y is north, and Z is up."""
        R = array([
            cos(self.lon)*cos(self.lat),
            sin(self.lon)*cos(self.lat),
            sin(self.lat)
        ]) * (6371.0 + self.alt)
        return dot(HOVI_MATRIX, R) - HOVI_POLE


class AircraftHandler:
    def __init__(self, ax, config):
        self.max_distance = config["aircraft"]["max_distance"]
        self.aircraft_list = {}
        
    def handle(self, events):
        for event_type, element in events:
            if event_type == "start":
                if element.tag == "MODESMESSAGE":
                    new_data = {}
                elif element.tag in USED_DATA_FIELDS:
                    new_data[element.tag] = element.text
            # When the MODESMESSAGE element ends, update the corresponding aircraft in
            # the list, or make a new one if necessary.
            elif event_type == "end" and element.tag == "MODESMESSAGE":
                ID = new_data["MODES"]
                print(new_data)
                if ID in self.aircraft_list:
                    self.aircraft_list[ID].update(new_data)
                else:
                    new_plane = Aircraft(new_data)
                    if new_plane.distance() <= self.max_distance:
                        self.aircraft_list[ID] = Aircraft(new_data)
    
    def cull(self):
        """Remove aircraft that are too low or too far away."""
        for ID, aircraft in self.aircraft_list.iteritems():
            if aircraft.distance() > self.max_distance:
                self.aircraft_list.pop(ID, None)
        

class AircraftListener:
    """This object will listen to the XML stream broadcast by the AirnNav RadarBox,
    parse the XML into a series of element start/end events, and send those to the
    given handler object."""
    
    def __init__(self, config, handler):
        self.handler = handler
        self.port = config["aircraft"]["port"]
        self.address = config["aircraft"]["address"]
        self.parser = ET.XMLPullParser(["start", "end"])
        self.connected = False

    def listen(self):
        source = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        source.connect((self.address, self.port))
        print("Start aircraft data listener.")
        self.connected = True
        self.parser.feed("<DATASTREAM>")
        while(1):
            data = source.recv(1024)
            if not data:
                print("AircraftListener: End of stream received.")
                source.close()
                break
            self.parser.feed(data)
            self.handler.handle(self.parser.read_events())
        self.parser.feed("</DATASTREAM>")
        self.handler.close()
        self.connected = False
        print("AircraftListener: Shutting down.")

if __name__=="__main__":
    conf = {"aircraft": {"port":7879, "address":"localhost"}}
    AH = AircraftHandler()
    AL = AircraftListener(conf, AH)
    AL.listen()
        