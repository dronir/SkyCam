# coding: utf8 
import ephem
import datetime
from numpy import pi

# The SatelliteHandler maintains a list of satellites and their locations, and draws them
# on the given Axes object when requested.

def get_Hovi():
    """Returns a PyEphem observer for Metsähovi."""
    Hovi = ephem.Observer()
    Hovi.lat = 60.217165
    Hovi.lon = 24.394562
    Hovi.elevation = 80
    return Hovi

class SatelliteHandler:
    def __init__(self, ax, config, obs=None):
        self.DEBUG = config["main"]["debug_level"]
        if self.DEBUG >= 1:
            print("SatelliteHandler: Initializing.")
        self.names = config["satellite"]["names"]
        self.filenames = config["satellite"]["files"]
        self.color = config["satellite"]["color"]
        self.ax = ax
        if obs is None:
            obs = get_Hovi()
        self.observer = obs
        self.update()
        
    def update(self):
        """Loads satellite orbit details from file."""
        if self.DEBUG >= 1:
            print("SatelliteHandler: Updating satellite list from files: {}".format(
              ", ".join(self.filenames)
            ))
        output = {}
        for filename in self.filenames:
            with open(filename) as f:
                while True:
                    name = f.readline().strip()
                    if name == "":
                        break
                    line1 = f.readline().strip()
                    line2 = f.readline().strip()
                    if name in self.names or not self.names:
                        sat = ephem.readtle(name, line1, line2)
                        point = self.ax.plot([],[], "o")[0]
                        point.set_color(self.color)
                        output[name] = (sat, point)
        self.satellites = output
        if self.DEBUG >= 2:
            sats = ", ".join(sorted(self.satellites.keys()))
            print("SatelliteHandler: following these satellites: {}".format(sats))
    
    def draw(self):
        if self.DEBUG >= 3:
            print("SatelliteHandler: Drawing satellites.")
        self.observer.date = datetime.datetime.now()
        for sat, point in self.satellites.values():
            sat.compute(self.observer)
            alt = float(sat.alt)
            az = float(sat.az)
            if alt > 0.0:
                point.set_data([az], [90 - alt*180/pi])
            else:
                point.set_data([], [])


