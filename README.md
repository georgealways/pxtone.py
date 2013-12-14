pxtone.py
=========

Python utility for reading data from Pixel's PTCOP format.

Usage
-----

Comes with a class pxtone.PTCOP which can load PTCOP files given a path.

```python

ptcop = pxtone.PTCOP.load('mysong.ptcop')

# list of Unit objects representing tracks
ptcop.units 

# list of Event objects in order of increasing position
ptcop.units[0].events

# integer representing time in "ptcop beats"
ptcop.units[0].events[0].position

# integer representing time in "ptcop beats"
ptcop.units[0].events[0].position

# event value, meaning depends on event type
ptcop.units[0].events[0].value



```

MIDI Converter
--------------

Comes with a utility ptcop2midi.py for converting ptcop files to midi.

You'll first need need to install a library called [midiutil](http://code.google.com/p/midiutil/)

```shell
$ python ptcop2midi.py mysong.ptcop
```

This command will output mysong.ptcop.mid with one track for each unit. 

Currently, the only interpreted values are:

- ON
- VELOCITY
- NOTE
- VOLUME

TODO
----

- MIDI Converter: Haven't yet figured out how to send 14-bit values like PAN or PITCH_BEND. 
- Unit names are currently ignored.
- Tempo isn't read correctly.

Thanks
------

This would not have been possible without the generous help of [Noxid](http://noxid.ca/) who reverse engineered the PTCOP format. Plus all of George & Jonathan's fans who came out of the wood work to help scour the web. 

If you're interested in learning more about the PTCOP format, check out this thread where Noxid breaks it down:
[http://www.cavestory.org/forums/index.php?/topic/5369-reading-ptcop-data-or-converting-to-midi-gj-say-hi/]
