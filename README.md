
# Metsähovi skycam software

## To begin

To run this software, run `python src/main.py config.toml` using Python 3.

This requires Matplotlib, NumPy, SciPy, Pillow, PyEphem and the `toml` package. All of
these are in PyPI so to install them, `pip install matplotlib scipy pyephem toml` should
be enough. Using a `virtualenv` with Python 3 and the required packages might be a good
idea.

If you want to plot satellites, you first need to fetch fresh orbital elements from
[Space-Track](www.space-track.com). This is done by running `python src/spacetrack.py
config.toml`. Note that you need to put your username and password into the config file.

## Configuration

The configuration file is in the TOML format. An example file, `config.toml` is provided.

### Main

The `update_interval` option determines how often the positions of the aircraft,
satellites and telescope are redrawn on the screen. This does not affect the update
interval of the skycam image nor the satellite traces (see below).

The `show_aircraft` etc. options determine which layers are drawn in the image.

The `debug_level` option, between 0 and 3, sets the amount of messages that are printed
while the software is running. The highest level can produce a lot of output and can slow
down the drawing loop in the view, especially if there are several aircraft in the sky.

### Location

The coordinates and elevation of the observer are set here, for computing the sky
positions of aircraft and satellites.

### Sky camera

The `update_interval` is tells how often the image is read from disk and redrawn on the
screen. The software will not update the image if a file called `lock.txt` is present in
the image directory. This can be used to ensure that a read/write collision does not
happen, which could cause an incomplete image to be drawn.

The `image_path` and `image_name` tell where to look for the skycam image. If that image
is not found, the image given in `default_image` (in the same path) is used instead. If
this is not found either, a black screen is drawn.

The `north_offset` sets the coordinate system north direction. This is needed so that
everything else is drawn in the correct places on the image. Zero offset means that north
is towards the right in the view.

### Satellites

Satellites that are lower in the sky than `min_altitude` or farther away from Metsähovi
than `max_range` are not drawn (this can cause satellites to disappear mid-pass if they
move past `max_range` for example). These limits also apply to the orbit traces.

Traces of the satellite orbits are drawn if `draw_traces` is `true`. The `trace_interval`
sets the length of one step in the trace, as well as how often the traces are redrawn.
The full length of the trace is set with `trace_forward` and `trace_backward`, which
determine the number of steps backwards and forwards the trace is drawn.

Satellite orbital elements are fetched from [Space-Track](www.space-track.com) with the
`spacetrack.py` program. The username and password for the service must be provided in
the configuration file.

The satellites to be downloaded and shown are given in the `[satellite.list.name]`
blocks, where `name` is an arbitrary string that will be used as the filename. These
blocks have a variable `show`, which determines whether that list of satellites is drawn
on screen by default, and `numbers`, which is a list of satellites ID numbers to fetch
from the [Space-Track](www.space-track.com) database. The `numbers` list is used only by
`spacetrack.py`. The main program only searches for orbital elements in the files given
by the `name` strings.

### Aircraft

The aircraft information is retrieved in real-time through a socket connection. The
address and port to connect to are given in the config. The system can provide warnings
when aircraft are either close to the zenith, near Metsähovi, or too close to the
telescope pointing direction. They are not drawn if they are lower than `min_altitude` or
farther away than `max_distance`.

If the data stream breaks for some reason, the data listener dies. If this happens, the
software must be restarted in order to begin listening for aircraft again.

The `data_timeout` parameter is a time limit (in seconds). After this time, aircraft
whose data has not been updated, will turn grey, and after twice that time, they will be
deleted.

### Scope

The program can ask the SLR telescope control computer for the pointing of the scope and
draw that on the screen. The address and port of the control computer are given here, as
well as the colours to use for the symbol.


