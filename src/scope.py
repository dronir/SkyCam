import socket

class TelescopeHandler:
    def __init__(self, ax, config):
        self.address = config["telescope"]["address"]
        self.port = int(config["telescope"]["port"])
        self.active = False
        self.ax = ax
        self.position = (1.570796327, 0.0)
        #self.update_position()
    
    def update_position(self):
        """Poll control computer for telescope pointing direction."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.address, self.port))
        message = "#\n"
        sock.sendall(message)
        data = sock.recv(2048)
        # TODO: parse message for telescope position
    
    def draw(self):
        """Draw symbol for telescope pointing onto axes."""
        pass
                