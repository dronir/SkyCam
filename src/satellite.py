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

class SatelliteHandler:
    def __init__(self, ax, config):
        self.DEBUG = config["main"]["debug_level"]
        if self.DEBUG >= 1:
            print("SatelliteHandler: Initializing...")
        self.lists = config["satellite"]["list"]
        self.color = config["satellite"]["color"]
        self.show_label = config["satellite"]["show_names"]
        self.show_trace = config["satellite"]["show_traces"]
        self.trace_interval = config["satellite"]["trace_interval"]
        self.trace_forward = config["satellite"]["trace_forward"]
        self.trace_backward = config["satellite"]["trace_backward"]
        self.trace_show_time = config["satellite"]["trace_show_time"]
        self.min_altitude = config["satellite"]["min_altitude"] * pi/180
        self.show_eclipsed = config["satellite"]["show_eclipsed"]
        self.max_range = config["satellite"]["max_range"] * 1000.0
        self.ax = ax
        self.observer = Hovi
        self.update()
        
    def update(self):
        """Loads satellite orbit details from file."""
        for listname in self.lists:
            filename = "{}.txt".format(listname)
            if self.DEBUG >= 2:
                print("SatelliteHandler: Updating satellite list from '{}'.".format(filename))
            output = {}
            with open(filename) as f:
                while True:
                    name = f.readline()
                    if name == "":
                        break
                    name = name[2:].strip()
                    line1 = f.readline().strip()
                    line2 = f.readline().strip()
                    sat = ephem.readtle(name, line1, line2)
                    point = self.ax.plot([],[], "o")[0]
                    trace = self.ax.plot([],[], "-")[0]
                    label = self.ax.text(0.0, 0.0, "  " + name)
                    label.set_visible(False)
                    point.set_color(self.color)
                    point.set_markersize(8)
                    label.set_color(self.color)
                    label.set_fontsize("x-small")
                    trace.set_color(self.color)
                    output[name] = (sat, point, label, trace)
            self.lists[listname]["satellites"] = output
            if self.DEBUG >= 2:
                sats = ", ".join(sorted(output.keys()))
                print("SatelliteHandler: added these satellites: {}".format(sats))
    
    def draw(self):
        """Draw the satellites onto the Axes."""
        if self.DEBUG >= 3:
            print("SatelliteHandler: Drawing satellites.")
        self.observer.date = datetime.datetime.utcnow()
        for sat_list in self.lists.values():
            if not sat_list["show"]:
                continue
            for sat, point, label, trace in sat_list["satellites"].values():
                sat.compute(self.observer)
                alt = float(sat.alt)
                az = float(sat.az)
                show = self.show_eclipsed or not sat.eclipsed
                if show and alt > self.min_altitude and sat.range < self.max_range:
                    point.set_data([az], [90 - alt*180/pi])
                    if self.show_label:
                        label.set_visible(True)
                        label.set_position([az, 90 - alt*180/pi])
                else:
                    point.set_data([], [])
                    continue
                if sat.eclipsed:
                    point.set_color = "gray"
                    label.set_color = "gray"
                else:
                    point.set_color = self.color
                    label.set_color = self.color
            

    def draw_traces(self):
        """Compute and draw the satellite traces."""
        if self.DEBUG >= 3:
            print("SatelliteHandler: Drawing satellite traces.")
        now = datetime.datetime.utcnow()
        a = -self.trace_backward
        b = self.trace_forward + 1
        dt = self.trace_interval
        times = [now + datetime.timedelta(seconds=i*dt) for i in range(a, b)]
        sat_idx = -a-1 # index corresponding to actual satellite location below
        for sat_list in self.lists.values():
            if not sat_list["show"]:
                continue
            for sat, point, label, trace in sat_list["satellites"].values():
                X = []
                Y = []
                draw_label_later = False
                for i, time in enumerate(times):
                    self.observer.date = time
                    sat.compute(self.observer)
                    alt = float(sat.alt)
                    az = float(sat.az)
                    show_eclipse = self.show_eclipsed or not sat.eclipsed
                    visible = (alt > self.min_altitude and sat.range < self.max_range 
                               and show_eclipse)
                    if visible:
                        X.append(az)
                        Y.append(90 - alt*180/pi)
                    # Is the satellite itself below minimum altitude
                    if i == sat_idx and not visible:
                        draw_label_later = True
                    # Draw the label at first visible point
                    if (draw_label_later and visible and self.show_label):
                        label.set_visible(True)
                        label.set_position([az, 90 - alt*180/pi])
                        draw_label_later = False
                if draw_label_later:
                    label.set_visible(False)
                trace.set_data(X,Y)
                    
