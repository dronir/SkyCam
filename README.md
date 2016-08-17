
# Metsähovi skycam software

## To begin

To run this software, run `python src/view.py config.toml` using Python 3.

This requires Matplotlib, NumPy, SciPy, PyEphem and the `toml` package. All of these are
in PyPI so to install them, `pip install matplotlib scipy pyephem toml` should be enough.
Using a `virtualenv` with Python 3 and the required packages might be a good idea.


## Configuration

The configuration file is in the TOML format (a simple and elegant config file standard).
An example file is provided and the configuration options are mostly self-evident.

### Main

The `update_interval` option determines how often the positions of the aircraft,
satellites and telescope are redrawn on the screen. This does not affect the update
interval of the skycam image nor the satellite traces (see below).

The `show_aircraft` etc. options determine which layers are drawn in the image.

The `debug_level` option, between 0 and 3, sets the amount of messages that are printed
while the software is running. The highest level can produce a lot of output and can slow
down the drawing loop in the view, especially if there are several aircraft in the sky.

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

The `files` variable is a list of strings, giving the files which contain the satellite
orbital parameters in TLE (two-line element) form. The `names` variable is a list of
strings that can optionally be empty. Only those satellites are drawn whose name, as it
appears in the orbit files, is found in this list. If the list is empty, all satellites
in the given orbit files are drawn.


### Aircraft

The aircraft information is retrieved in real-time through a socket connection. The
address and port to connect to are given in the config. The system can provide warnings
when aircraft are either close to the zenith, near Metsähovi, or too close to the
telescope pointing direction. They are not drawn if they are lower than `min_altitude` or
farther away than `max_distance`.

If the data stream breaks for some reason, the data listener exists. If this happens, the
software must be restarted in order to begin listening for aircraft again.

### Scope

(Not yet implemented.)


