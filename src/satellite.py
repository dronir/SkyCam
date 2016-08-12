# coding: utf8 
import ephem
import datetime
from numpy import pi

# The SatelliteHandler maintains a list of satellites and their locations, and draws them
# on the given Axes object when requested.


Hovi = ephem.Observer()
Hovi.lat = 60.217165
Hovi.lon = 24.394562
Hovi.elevation = 80


class SatelliteHandler:
    def __init__(self, ax, config, obs=None):
        self.DEBUG = config["main"]["debug_level"]
        if self.DEBUG >= 1:
            print("SatelliteHandler: Initializing.")
        self.names = config["satellite"]["names"]
        self.filenames = config["satellite"]["files"]
        self.color = config["satellite"]["color"]
        self.show_label = config["satellite"]["show_name"]
        self.ax = ax
        if obs is None:
            obs = Hovi
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
                        label = self.ax.text(0.0, 1000.0, "  " + name)
                        point.set_color(self.color)
                        label.set_color(self.color)
                        label.set_fontsize("x-small")
                        output[name] = (sat, point, label)
        self.satellites = output
        if self.DEBUG >= 2:
            sats = ", ".join(sorted(self.satellites.keys()))
            print("SatelliteHandler: following these satellites: {}".format(sats))
    
    def draw(self):
        """Draw the satellites onto the Axes."""
        if self.DEBUG >= 3:
            print("SatelliteHandler: Drawing satellites.")
        self.observer.date = datetime.datetime.now()
        for sat, point, label in self.satellites.values():
            sat.compute(self.observer)
            alt = float(sat.alt)
            az = float(sat.az)
            if alt > 0.0:
                point.set_data([az], [90 - alt*180/pi])
                if self.show_label:
                    label.set_position([az, 90 - alt*180/pi])
            else:
                point.set_data([], [])

    def draw_traces(self):
        pass

