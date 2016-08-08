from satellite import SatelliteHandler
from scope import TelescopeHandler
from camera import CameraHandler
from aircraft import AircraftHandler, AircraftListener

from numpy import pi
import matplotlib as mpl
from matplotlib.animation import FuncAnimation
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
        self.Aircraft = Aircraft
        self.Camera = Camera
    def __call__(self, i):
        if self.show_aircraft:
            self.Aircraft.draw()
    def init(self):
        if self.show_skycam:
            self.Camera.draw_image()

def create_view(config_filename):
    config = toml.loads(open(config_filename).read())
    
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
    Aircraft = AircraftHandler(ax_symbols, config)
    Scope = TelescopeHandler(ax_symbols, config)
    
    animator = Animator(config, Aircraft, Camera, Satellites, Scope)
    
    PlaneListener = AircraftListener(config, Aircraft)
    thread_AircraftListener = threading.Thread(target=PlaneListener.listen)
    thread_AircraftListener.start()
    
    screen_interval = int(config["main"]["update_interval"] * 1000)
    
    anim = FuncAnimation(fig, animator, init_func=animator.init, 
                         blit=False, interval=screen_interval)
    plt.show()
    


if __name__=="__main__":
    try:
        create_view(argv[1])
    except KeyboardInterrupt:
        exit()


