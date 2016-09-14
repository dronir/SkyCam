import socket
from math import pi

class TelescopeHandler:
    def __init__(self, ax, config):
        self.DEBUG = config["main"]["debug_level"]
        if self.DEBUG >= 1:
            print("TelescopeHandler: Initializing...")
        self.address = config["telescope"]["address"]
        self.port = int(config["telescope"]["port"])
        self.color_normal = config["telescope"]["color_normal"]
        self.active = False
        self.ax = ax
        self.position = (1.570796327, 0.0)
        self.visible = False
        self.circle = self.ax.plot([],[], "o")[0]
        self.cross = self.ax.plot([],[], "+")[0]
        self.circle.set_markersize(20)
        self.circle.set_fillstyle("none")
        self.circle.set_markeredgewidth(2)
        self.circle.set_color(self.color_normal)
        self.cross.set_color(self.color_normal)
        self.cross.set_markersize(20)
    
    def update_position(self):
        """Poll control computer for telescope pointing direction."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.visible = True
        try:
            sock.connect((self.address, self.port))
            sock.sendall(bytes("#cybioms.telescope.data\n", encoding="utf-8"))
            data = sock.recv(2048).decode("utf-8")
            self.visible = True
            if self.DEBUG >= 3:
                print("TelescopeHandler: Received position..")
        except Exception as e:
            if self.DEBUG >= 3:
                print("TelescopeHandler: Unable to get position.")
                print(e)
            self.visible = False
            data = ""
        elevation = 0.0
        azimuth = 0.0
        for line in data.split("\n"):
            if "elevation" in line:
                elevation = float(line.split("=")[1])
            if "azimuth" in line:
                azimuth = float(line.split("=")[1]) * pi/180
        self.position = (90-elevation, azimuth)
        
    
    def draw(self):
        """Draw symbol for telescope pointing onto axes."""
        if self.visible:
            alt, az = self.position
            if self.DEBUG >= 2:
                print("TelescopeHandler: Drawing scope at alt={:.2f}°, az={:.2f}°.".format(
                    90-alt, az*180/pi))
            self.circle.set_data([az], [alt])
            self.cross.set_data([az], [alt])
        else:
            pass

    