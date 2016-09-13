import telnetlib
import xml.etree.ElementTree as ET
from datetime import datetime
from ephem import separation
from numpy import sqrt, sin, cos, array, cross, eye, dot, pi
from numpy import arctan2 as atan2
from scipy.linalg import expm3, norm
from matplotlib.lines import Line2D

# The AircraftHandler maintains a list of nearby aircraft, from data given by an
# AircraftListener, and draws the aircraft on the given Axes object when
# requested.

# The AircraftListener listens to the AirNav RadarBox XML stream, parsing and
# sending the aircraft updates to an AircraftHandler whenever they arrive.

# Degrees to radians conversion factor
RAD = pi/180
KNOTS = 1.94384449 # knots to m/s
FEET = 3.28084 # feet/s to m/s


# The data fields we want to read for each aircraft
USED_DATA_FIELDS = [
    "DATETIME", "MODES", "CALLSIGN", "ALTITUDE", "VRATE",
    "GROUNDSPEED", "TRACK", "LATITUDE","LONGITUDE"
]
CRITICAL_FIELDS = ["DATETIME", "ALTITUDE", "LATITUDE", "LONGITUDE"]

def verify_fields(data):
    for field in CRITICAL_FIELDS:
        if not field in data:
            return False
    return True

# Some Metsähovi coordinates that are needed later
HOVI_LAT = 60.217165 * RAD
HOVI_LON = 24.394562 * RAD
HOVI_COORD_RAD = (HOVI_LON, HOVI_LAT)
EARTH_RADIUS = 6371.0

# Construct a matrix to rotate geocentric positions to Metsähovi-centric by rotating
# Metsähovi "to the north pole". This only needs to be done once.

MatZ = array([
    [cos(HOVI_LON), -sin(HOVI_LON), 0],
    [sin(HOVI_LON),  cos(HOVI_LON), 0],
    [0, 0, 1]
])
MatX = array([
    [1, 0, 0],
    [0, cos(pi/2-HOVI_LAT), -sin(pi/2-HOVI_LAT)],
    [0, sin(pi/2-HOVI_LAT),  cos(pi/2-HOVI_LAT)]
])
HOVI_MATRIX = dot(MatX, MatZ)
HOVI_CART = array([cos(HOVI_LAT)*sin(HOVI_LON), 
                   cos(HOVI_LAT)*cos(HOVI_LON), 
                   sin(HOVI_LAT)]) * (EARTH_RADIUS + 0.08)
HOVI_POLE = array([0.0, 0.0, EARTH_RADIUS + 0.08])


class Aircraft:
    def __init__(self, ax, config, data):
        self.last_updated = datetime(year=1903, month=12, day=17)
        self.ax = ax
        self.marker = ax.plot([], [], "D")[0]
        self.vector = Line2D([], [])
        self.vector.set_linewidth(2)
        self.vector.set_alpha(0.5)
        self.config = config
        self.color = config["aircraft"]["color"]
        self.color_warn = config["aircraft"]["color_warning"]
        self.timeout = config["aircraft"]["data_timeout"]
        self.DEBUG = config["main"]["debug_level"]
        self.callsign = ""
        self.marker.set_alpha(1.0)
        ax.add_line(self.vector)
        self.ok = True
        self.update(data)
        self.label = ax.text(0.0, 1000.0, self.callsign)
        self.label.set_size("small")
        
        
    def update(self, data):
        """Update aircraft status with received data.
        Give default values for non-critical parameters, if they are missing from
        the broadcast. For critital parameters, mark the aircraft as not 'ok'."""
        update_time = datetime.strptime(data["DATETIME"], "%Y%m%d%H%M%S")
        if update_time < self.last_updated:
            return
        self.ok = True
        self.modes = data["MODES"]
        self.callsign = data.get("CALLSIGN", "?")
        self.vrate = float(data.get("VRATE", 0.0)) / KNOTS
        self.speed = float(data.get("GROUNDSPEED", 0.0)) / FEET
        self.last_updated = update_time
        self.heading = data.get("TRACK", None) 
        if not self.heading is None:
            self.heading = float(self.heading) * RAD
        self.lat = float(data["LATITUDE"]) * RAD
        self.lon = float(data["LONGITUDE"]) * RAD
        self.alt = float(data["ALTITUDE"]) * 0.0003048 # feet to km
        self.alt, self.az, self.valt, self.vaz = self.sky_position()
            
    def distance(self):
        """Return ground distance from Metsähovi in km."""
        sep = float(separation(HOVI_COORD_RAD, (self.lon, self.lat)))
        return sep * EARTH_RADIUS
    
    def velocity(self):
        """Return velocity vector in airplace-centric system where X is east."""
        if self.heading is None:
            return (0.0, 0.0, 0.0)
        # heading is 0 for north
        vx = sin(self.heading) * self.speed
        vy = cos(self.heading) * self.speed
        return 0.002 * array([vx, vy, self.vrate])
    
    def cartesian(self): 
        """Return position in a Metsähovi-centric cartesian system. 
        In the coordinate system X is east, Y is north, and Z is up."""
        R = array([
            sin(self.lon)*cos(self.lat),
            cos(self.lon)*cos(self.lat),
            sin(self.lat)
        ]) * (EARTH_RADIUS + self.alt)
        return dot(HOVI_MATRIX, R) - HOVI_POLE 
    
    def sky_position(self):
        R = self.cartesian()
        alt = atan2(R[2], sqrt(R[0]**2 + R[1]**2))
        az = atan2(R[0], -R[1])
        
        V = R + self.velocity()
        valt = atan2(V[2], sqrt(V[0]**2 + V[1]**2))
        vaz = atan2(V[0], -V[1])
        return pi/2-alt, az, pi/2-valt, vaz
    
    def draw(self):
        """Update the marker for this aircraft."""
        now = datetime.now()
        delta = now - self.last_updated
        timeout = 60
        if delta.seconds > self.timeout:
            self.ok = False
        if delta.seconds > 2*self.timeout:
            return True
        if not self.ok:
            self.marker.set_color("gray")
            self.vector.set_color("gray")
            self.label.set_color("gray")
        elif (self.config["aircraft"]["warn_nearby"]
                and self.distance() < self.config["aircraft"]["nearby_distance"]):
            self.marker.set_color(self.color_warn)
            self.vector.set_color(self.color_warn)
            self.label.set_color(self.color_warn)
        else:
            self.marker.set_color(self.color)
            self.vector.set_color(self.color)
            self.label.set_color(self.color)
        alt, az, valt, vaz = self.alt, self.az, self.valt, self.vaz
        self.marker.set_data([az], [alt/RAD])
        if self.config["aircraft"]["show_vectors"]:
            self.vector.set_xdata([az, vaz])
            self.vector.set_ydata([alt/RAD, valt/RAD])
        self.label.set_position((az, alt/RAD))
        return False
    
    def clear(self):
        """Clear the marker for this aircraft. Used when it's deleted from the list."""
        self.marker.remove()
        self.vector.remove()
        self.label.remove()
    


class AircraftHandler:
    def __init__(self, ax, config, data_lock):
        self.config = config
        self.DEBUG = config["main"]["debug_level"]
        if self.DEBUG >= 1:
            print("AircraftHandler: Initializing...")
        self.ax = ax
        self.max_distance = config["aircraft"]["max_distance"]
        self.max_zenith = pi/2 - config["aircraft"]["min_altitude"] * RAD
        self.color = config["aircraft"]["color"]
        self.data_lock = data_lock
        self.aircraft_list = {}
        self.new_data = {}
        
    def update(self, events):
        """Receive a data update from the Listener and update the aircraft list."""
        if self.DEBUG >= 3:
            print("AircraftHandler: Received data update.")
        for event_type, element in events:
            if event_type == "start":
                if element.tag == "MODESMESSAGE":
                    self.new_data = {}
                elif element.tag in USED_DATA_FIELDS:
                    self.new_data[element.tag] = element.text
            # When the MODESMESSAGE element ends, update the corresponding aircraft in
            # the list, or make a new one if necessary.
            elif event_type == "end" and element.tag == "MODESMESSAGE":
                if not verify_fields(self.new_data):
                    return
                ID = self.new_data["MODES"]
                if ID in self.aircraft_list:
                    ac = self.aircraft_list[ID]
                    ac.update(self.new_data)
                    if ac.distance() > self.max_distance or ac.alt > self.max_zenith:
                        if self.DEBUG >= 2:
                            print("AircraftHandler: Deleting aircraft {}.".format(ID))
                        self.data_lock.acquire()
                        ac.clear()
                        self.aircraft_list.pop(ID, None)
                        self.data_lock.release()
                else:
                    ac = Aircraft(self.ax, self.config, self.new_data)
                    if ac.distance() <= self.max_distance and ac.alt < self.max_zenith:
                        if self.DEBUG >= 2:
                            print("AircraftHandler: Creating aircraft {}.".format(ID))
                        self.data_lock.acquire()
                        self.aircraft_list[ID] = ac
                        self.data_lock.release()

    def draw(self):
        """Draw all of the aircraft onto the Axes."""
        if self.DEBUG >= 3:
            print("AircraftHandler: Drawing aircraft.")
        to_delete = []
        self.data_lock.acquire()
        for ID in self.aircraft_list:
            aircraft = self.aircraft_list[ID]
            delete = aircraft.draw()
            if delete:
                aircraft.clear()
                to_delete.append(ID)
        for ID in to_delete:
            self.aircraft_list.pop(ID, None)
        self.data_lock.release()
        

class AircraftListener:
    """This object will listen to the XML stream broadcast by the AirnNav RadarBox,
    parse the XML into a series of element start/end events, and send those to the
    given handler object."""
    
    def __init__(self, config, handler, end_signal):
        self.DEBUG = config["main"]["debug_level"]
        self.handler = handler
        self.port = int(config["aircraft"]["port"])
        self.address = config["aircraft"]["address"]
        self.parser = ET.XMLPullParser(["start", "end"])
        self.end_signal = end_signal
        self.connected = False

    def listen(self):
        if self.DEBUG >= 1:
            print("AircraftListener: Initializing...")
        try:
            source = telnetlib.Telnet(self.address, self.port)
        except:
            print("AircraftListener: Error, unable to connect to source.")
            return
        self.connected = True
        self.parser.feed("<DATASTREAM>")
        while(1):
            # Get data and pass it to the AircraftHandler until the shutdown signal is
            # received or the data stream ends for some reason.
            if self.end_signal.is_set():
                if self.DEBUG >= 1:
                    print("AircraftListener: Received shutdown signal.")
                source.close()
                break
            data = source.read_until(b"</MODESMESSAGE>")
            if not data:
                print("AircraftListener: Error: end of stream received.")
                source.close()
                break
            self.parser.feed(data)
            self.handler.update(self.parser.read_events())
        self.parser.feed("</DATASTREAM>")
        self.connected = False
        if self.DEBUG >= 1:
            print("AircraftListener: Shutting down.")

if __name__=="__main__":
    conf = {"aircraft": {"port":7879, "address":"localhost", "max_distance":100}}
    AH = AircraftHandler(None, conf)
    AL = AircraftListener(conf, AH)
    AL.listen()
        