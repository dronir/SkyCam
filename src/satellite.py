# coding: utf8 
import ephem
import datetime

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
    def __init__(self, config, ax, obs=None):
        """Initialize satellite handler with names.
        
        'names' is a list of the names of the desired satellites, 'filename' gives the
        file containing the orbit information in Two-Line Element format."""
        
        self.names = config["satellite"]["names"]
        self.filenames = config["satellite"]["files"]
        if obs is None:
            obs = get_Hovi()
        self.observer = obs
        self.update()
        
    def update(self):
        """Loads satellite orbit details from file."""
        output = []
        with open(self.filename) as f:
            while True:
                name = f.readline().strip()
                if name == "":
                    break
                line1 = f.readline().strip()
                line2 = f.readline().strip()
                if name in self.names or not self.names:
                    sat = ephem.readtle(name, line1, line2)
                    output.append(sat)
        self.satellites = output
        
    def trace(self, idx, date=None, interval=1, N=7, offset=-1):
        """Returns the sky path of the ith satellite in the handler.
        
        Date defaults to now, interval is in minutes, N is the number of points and
        offset is a shift in time. The defaults produce time points from -2 to +14
        minutes from now."""
        
        if data is None:
            date = datetime.datetime.now()
        date = date - datetime.timedelta(seconds=date.second)
        loc = []
        sat = self.satellites[idx]
        for i in range(N):
            self.observer.date = date + datetime.timedelta(minutes=interval*(i+offset))
            t = self.observer.date.tuple()
            timestamp = "{:d}:{:0d}".format(t[3], t[4])
            sat.compute(self.observer)
            loc.append((timestamp, float(sat.alt), float(sat.az)))
        return loc
        
    def loc(self, idx, date=None):
        """Get the position of the ith satellite at a given time."""
        if date is None:
            date = datetime.datetime.now()
        self.observer.date = date
        sat = self.satellites[idx]
        sat.compute(self.observer)
        return (float(sat.alt), float(sat.az))
        
    def add_satellite(self, name):
        """Add a new satellite to the list."""
        self.names.append(name)
        self.update()
    
    def list_visible(self, date=None):
        """Return a list with the names and positions of all visible satellites."""
        if date is None:
            date = datetime.datetime.now()
        self.observer.date = date
        output = []
        for sat in self.satellites:
            sat.compute(self.observer)
            alt = float(sat.alt)
            az = float(sat.az)
            if alt > 0:
                output.append((sat.name, alt, az))
        return output
    
if __name__=="__main__":
    H = SatelliteHandler("geodetic.txt")
    print(H.list_visible())


