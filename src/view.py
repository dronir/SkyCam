from satellite import SatelliteHandler
from scope import TelescopeHandler
from camera import CameraHandler
from aircraft import AircraftHandler, AircraftListener
from debug import print_debug

from numpy import pi
import matplotlib as mpl
from matplotlib.animation import FuncAnimation
from matplotlib import pyplot as plt
import toml
import threading
from sys import argv, exit

# Remove bottom toolbar from Matplotlib window
mpl.rcParams["toolbar"] = "None"

# This makes for prettier debug lines
def print_debug(DEBUG, level, message):
    if DEBUG >= level:
        print(message)

class Animator:
    def __init__(self, config, Aircraft, Camera, Sat, Scope):
        self.show_skycam = config["main"]["show_skycam"]
        self.show_aircraft = config["main"]["show_aircraft"]
        self.show_satellites = config["main"]["show_satellites"]
        self.Aircraft = Aircraft
        self.Camera = Camera
        self.Satellites = Sat
        if self.show_skycam:
            # How many frames between skycam updates
            self.skycam_interval = int(config["skycam"]["update_interval"] 
                                 / config["main"]["update_interval"])
    def __call__(self, i):
        if self.show_aircraft:
            self.Aircraft.draw()
        if self.show_skycam and (i % self.skycam_interval) == 0:
            self.Camera.update_image()
            self.Camera.draw_image()
        if self.show_satellites:
            self.Satellites.draw()
    def init(self):
        if self.show_skycam:
            self.Camera.draw_image()

def create_view(config_filename):
    config = toml.loads(open(config_filename).read())
    
    def DEBUG(level, message):
        print_debug(config["main"]["debug_level"], level, message)
    
    DEBUG(1, "Main: Greating graphics window...")
    fig = plt.figure(figsize=(16,9))
    ax_skycam = fig.add_subplot(111)
    ax_symbols = fig.add_subplot(111, polar=True)
    ax_skycam.set_position((0.0, 0.0, 0.75, 1.0))
    ax_symbols.set_position((-0.023, -0.01, 0.75, 1.0))

    # Set up the axes object for drawing planes, satellites and scope
    north_offset = config["skycam"]["north_offset"] * pi/180
    ax_symbols.patch.set_alpha(0)
    ax_symbols.set_ylim(0, 90)
    ax_symbols.set_theta_offset(north_offset)
    #ax_symbols.tick_params(axis='x', colors='white')
    #ax_symbols.tick_params(axis='y', colors='white')
    
    Camera = CameraHandler(ax_skycam, config)
    Satellites = SatelliteHandler(ax_symbols, config)
    if config["main"]["show_aircraft"]:
        Aircraft = AircraftHandler(ax_symbols, config)
    else:
        Aircraft = None
    Scope = TelescopeHandler(ax_symbols, config)
    
    animator = Animator(config, Aircraft, Camera, Satellites, Scope)
    
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
    # Set the Event which will tell other threads to end themselves.
    end_signal.set()
    


if __name__=="__main__":
    try:
        create_view(argv[1])
    except KeyboardInterrupt:
        exit()


