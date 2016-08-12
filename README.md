
# Metsähovi skycam software

## Requirements

Python 3, Matplotlib, Numpy, SciPy, PyEphem, the `toml` package.

## Configuration

The configuration file is in the TOML format (a simple and elegant config file standard).
An example file is provided and the configuration options are mostly self-evident.

### Main

The `update_interval` option determines how often the positions of the aircraft,
satellites and telescope are redrawn on the screen. This does not affect the update
interval of the skycam image nor the satellite traces (see below).

The `show_aircraft` etc. options determine which layers are drawn in the image.

The `debug_level` option sets the amount of messages that are printed while the software
is running. The highest level can produce a lot of output and can slow down the drawing
loop in the view, especially if there are several aircraft in the sky.

0. No messages are printed.
1. Initialization and finalization messages.
2. Above, plus temporary object creation and deletion messages and other less important 
   information.
3. Above, plus real-time debug messages. This can mean several lines per second.

### Sky camera

The `update_interval` is tells how often the image is read from disk and redrawn on the
screen. The software will not update the image if a file called `lock.txt` is present in
the image directory. This can be used to ensure that a read/write collision does not
happen, which could cause an incomplete image to be drawn.

The `north_offset` sets the coordinate system north direction. This is needed so that
everything else is drawn in the correct places on the image. Zero offset means that north
is towards the right in the view.

### Satellites

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

### Scope

(Not yet implemented.)


