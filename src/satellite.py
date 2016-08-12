# coding: utf8 
import ephem
import datetime
from numpy import pi

# The SatelliteHandler maintains a list of satellites and their locations, and draws them
# on the given Axes object when requested.

Hovi = ephem.Observer()
Hovi.lat = "60.217165"
Hovi.lon = "24.394562"
Hovi.elevation = 95
Hovi.date = datetime.datetime.utcnow()



print(Hovi)

class SatelliteHandler:
    def __init__(self, ax, config):
        self.DEBUG = config["main"]["debug_level"]
        if self.DEBUG >= 1:
            print("SatelliteHandler: Initializing...")
        self.names = config["satellite"]["names"]
        self.filenames = config["satellite"]["files"]
        self.color = config["satellite"]["color"]
        self.show_label = config["satellite"]["show_names"]
        self.show_trace = config["satellite"]["show_traces"]
        self.trace_interval = config["satellite"]["trace_interval"]
        self.trace_forward = config["satellite"]["trace_forward"]
        self.trace_backward = config["satellite"]["trace_backward"]
        self.trace_show_time = config["satellite"]["trace_show_time"]
        self.min_altitude = config["satellite"]["min_altitude"] * pi/180
        self.ax = ax
        self.observer = Hovi
        self.update()
        
    def update(self):
        """Loads satellite orbit details from file."""
        if self.DEBUG >= 2:
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
                        trace = self.ax.plot([],[], "-")[0]
                        label = self.ax.text(0.0, 1000.0, "  " + name)
                        point.set_color(self.color)
                        point.set_markersize(8)
                        label.set_color(self.color)
                        label.set_fontsize("x-small")
                        trace.set_color(self.color)
                        output[name] = (sat, point, label, trace)
        self.satellites = output
        if self.DEBUG >= 2:
            sats = ", ".join(sorted(self.satellites.keys()))
            print("SatelliteHandler: following these satellites: {}".format(sats))
    
    def draw(self):
        """Draw the satellites onto the Axes."""
        if self.DEBUG >= 3:
            print("SatelliteHandler: Drawing satellites.")
        self.observer.date = datetime.datetime.utcnow()
        for sat, point, label, trace in self.satellites.values():
            sat.compute(self.observer)
            alt = float(sat.alt)
            az = float(sat.az)
            if alt > self.min_altitude:
                point.set_data([az], [90 - alt*180/pi])
                if self.show_label:
                    label.set_position([az, 90 - alt*180/pi])
            else:
                point.set_data([], [])

    def draw_traces(self):
        if self.DEBUG >= 3:
            print("SatelliteHandler: Drawing satellite traces.")
        now = datetime.datetime.utcnow()
        a = -self.trace_backward
        b = self.trace_forward + 1
        dt = self.trace_interval
        times = [now + datetime.timedelta(seconds=i*dt) for i in range(a, b)]
        for sat, point, label, trace in self.satellites.values():
            X = []
            Y = []
            hidden = False
            for i, time in enumerate(times):
                self.observer.date = time
                sat.compute(self.observer)
                alt = float(sat.alt)
                az = float(sat.az)
                if alt > self.min_altitude:
                    X.append(az)
                    Y.append(90 - alt*180/pi)
                # Draw the label next to the trace if the satellite is below horizon
                if i == -a-1 and alt < self.min_altitude:
                    hidden = True
                if (hidden and self.show_label and alt > self.min_altitude):
                    label.set_position([az, 90 - alt*180/pi])
                if i > -a-1 and alt > self.min_altitude:
                    hidden = False
                if hidden and i == len(times) - 1:
                    X = []
                    Y = []
                    label.set_position([0.0, 1000.0])
            trace.set_data(X,Y)
                
