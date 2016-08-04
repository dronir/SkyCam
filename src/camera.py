from os import path
from sys import exit
import matplotlib.pyplot as plt
import toml

# The CameraHandler keeps an up-to-date version of the fullsky image and draws it on the 
# given Axes object when requested.

class CameraHandler:
    def __init__(self, ax, config):
        self.ax = ax
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        try:
            self.interval = config["skycam"]["update_interval"]
            img_path = config["skycam"]["image_path"]
            img_name = config["skycam"]["image_name"]
        except KeyError as e:
            print("Error in config file: unknown key {}".format(str(e)))
            exit()
        self.filename = path.join(img_path, img_name)
        self.lockfile = path.join(img_path, "lock.txt")
        self.has_image = False
        self.update_image()
        
    def update_image(self):
        """Load the image from the file."""
        if path.exists(self.filename) and not path.exists(self.lockfile):
            self.image = plt.imread(self.filename)
            self.has_image = True
    
    def draw_image(self):
        """Draw the stored image onto the axes."""
        if self.has_image:
            self.ax.imshow(self.image)
        else:
            self.ax.set_axis_bgcolor("black")
    
if __name__=="__main__":
    with open("config.toml") as f:
        conf = toml.loads(f.read())
        fig = plt.figure(figsize=(15,10))
        fig.patch.set_facecolor("white")
        ax = fig.add_subplot(111)
    
        C = CameraHandler(ax, conf)
        C.draw_image()
        plt.show()
