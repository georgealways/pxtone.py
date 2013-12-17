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

# integer representing event type
ptcop.units[0].events[0].type

# an enum describing event types
pxtone.EventTypes.ON
pxtone.EventTypes.NOTE
pxtone.EventTypes.PAN

# event value whose meaning depends on event type
ptcop.units[0].events[0].value
```

If you're interested in learning more about the PTCOP format, [check out this thread](http://www.cavestory.org/forums/index.php?/topic/5369-reading-ptcop-data-or-converting-to-midi-gj-say-hi/) where Noxid breaks it down.

MIDI Converter
--------------

Comes with a utility ptcop2midi.py for converting ptcop files to midi.

```shell
$ python ptcop2midi.py mysong.ptcop
```

This command will output mysong.ptcop.mid with one track for each unit. 

Currently, the only interpreted values are:

- ON
- VELOCITY
- NOTE
- KEY PORTA

**For KEY PORTA to be interpreted correctly, the pitch bend range for your MIDI device must be +-12 semitones**. Any pitch bends in a PTCOP that would have the sample bend more than an octave in either direction can't be interpreted.

todo
----

~~- MIDI Converter: Haven't yet figured out how to send 14-bit values like PITCH BEND.~~
- Unit Names
- Tempo
- Volume
- Pan

Thanks
------

This would not have been possible without the generous help of [Noxid](http://noxid.ca/) who reverse engineered the PTCOP format. Andrew Reitano for helping me patch the midiutil lib. Plus all of George & Jonathan's fans who came out of the wood work to help scour the web.

