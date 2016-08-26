from satellite import SatelliteHandler
from scope import TelescopeHandler
from camera import CameraHandler
from aircraft import AircraftHandler, AircraftListener

from numpy import pi
import matplotlib as mpl
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from matplotlib import pyplot as plt

import toml
import threading
from sys import argv, exit

# Remove bottom toolbar from Matplotlib window
mpl.rcParams["toolbar"] = "None"

class Animator:
    def __init__(self, config, Aircraft, Camera, Sat, Scope):
        self.show_skycam = config["main"]["show_skycam"]
        self.show_aircraft = config["main"]["show_aircraft"]
        self.show_satellites = config["main"]["show_satellites"]
        self.show_satellite_traces = config["satellite"]["show_traces"]
        self.Aircraft = Aircraft
        self.Camera = Camera
        self.Satellites = Sat
        interval = config["main"]["update_interval"]
        self.trace_interval = int(config["satellite"]["trace_interval"] / interval)
        self.skycam_interval = int(config["skycam"]["update_interval"] / interval)
    def __call__(self, i):
        if self.show_aircraft:
            self.Aircraft.draw()
        if self.show_skycam and (i % self.skycam_interval == 0):
            self.Camera.update_image()
            self.Camera.draw_image()
        if self.show_satellites:
            self.Satellites.draw()
        if self.show_satellite_traces and (i % self.trace_interval == 0):
            self.Satellites.draw_traces()
            
    def init(self):
        if self.show_skycam:
            self.Camera.draw_image()

def main(config_filename):
    config = toml.loads(open(config_filename).read())
    
    # Prettier debug lines with this closure
    def DEBUG(level, message):
        if config["main"]["debug_level"] >= level:
            print(message)
    
    DEBUG(1, "Main: Greating graphics window...")
    width = config["main"]["window_width"]
    fig = plt.figure(figsize=(width, 9/16*width))
    fig.patch.set_color("black")
    
    # Create the different Axes for skycam image, aircraft/sat/scope symbols and texts
    ax_skycam = fig.add_subplot(311)
    ax_symbols = fig.add_subplot(312, polar=True)
    ax_texts = fig.add_subplot(313)
    ax_skycam.set_position((0.01, 0.02, 0.73, 0.96))
    
    wx,wy = 1.0, 1.01
    cx = 0.347
    cy = 0.487
    x, y = cx - wx/2, cy - wy/2
    ax_symbols.set_position((x, y, wx, wy))
    ax_texts.set_position((0.75, 0.02, 0.2, 0.96))

    # Set up the Axes object for the skycam
    ax_skycam.patch.set_color("black")
    ax_symbols.set_axis_bgcolor("red")
    ax_symbols.patch.set_alpha(0.0)

    # Set up the Axes object for planes, satellites and scope
    north_offset = config["skycam"]["north_offset"] * pi/180
    ax_symbols.set_ylim(0, 90)
    ax_symbols.set_theta_offset(north_offset)
    ax_symbols.tick_params(axis='x', colors='white')
    ax_symbols.tick_params(axis='y', colors='white')
    ax_symbols.set_xticklabels(['N','NE','E','SE','S','SW','W','NW'])
    if not config["main"]["show_skycam"]:
        ax_symbols.xaxis.grid(color="white")
        ax_symbols.yaxis.grid(color="white")
        [l.set_color("white") for l in ax_symbols.spines.values()]
    
    horizon_ring = config["skycam"]["draw_horizon"]
    if horizon_ring > 0.0:
        ax_symbols.add_artist(
            Circle((0,0), 90 - horizon_ring, transform=ax_symbols.transData._b,
                  color="white", fill=False))
    
    # Set up the Axes for texts
    ax_texts.patch.set_color("black")
    ax_texts.set_xticks([])
    ax_texts.set_yticks([])
    
    # Set up the handler objects for the different drawings
    Camera = CameraHandler(ax_skycam, config)
    Satellites = SatelliteHandler(ax_symbols, config)
    if config["main"]["show_aircraft"]:
        Aircraft = AircraftHandler(ax_symbols, config)
    else:
        Aircraft = None
    Scope = TelescopeHandler(ax_symbols, config)
    
    animator = Animator(config, Aircraft, Camera, Satellites, Scope)
    
    # Create the thread that listens for aircraft updates
    end_signal = threading.Event()
    if config["main"]["show_aircraft"]:
        DEBUG(1, "Main: Creating AircraftListener thread...")
        PlaneListener = AircraftListener(config, Aircraft, end_signal)
        thread_AircraftListener = threading.Thread(target=PlaneListener.listen)
        thread_AircraftListener.start()
    
    frame_interval = int(config["main"]["update_interval"] * 1000)
    
    DEBUG(1, "Main: Creating view animator...")
    anim = FuncAnimation(fig, animator, init_func=animator.init, 
                         blit=False, interval=frame_interval)

    DEBUG(1, "Main: Starting up view...")
    plt.show()
    DEBUG(1, "Main: Closed view.")
    DEBUG(1, "Main: Telling other threads to shut down...")
    end_signal.set()
    


if __name__=="__main__":
    try:
        main(argv[1])
    except KeyboardInterrupt:
        exit()


