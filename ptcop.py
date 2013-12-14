import mmap, struct, os, math
from midiutil.MidiFile import MIDIFile

class PTCOP:

    def __init__(self):

        self.units = list()
        self.tempo = 120

    @staticmethod
    def load(path):

        # Make a new ptcop object
        ptcop = PTCOP()

        # Open the ptcop file
        f = open(path, 'r+b')

        # Use a memory mapped file, because ptcops are big.
        stream = mmap.mmap(f.fileno(), 0)
        stream.seek(0)

        # Find out how many units there are
        seek_block(stream, 'num UNIT')
        num_units = read_int(stream)

        # Find out the tempo
        seek_block(stream, 'MasterV5')
        stream.seek(5, os.SEEK_CUR)

        # (totally wrong)
        ptcop.tempo = read_int(stream) 

        print 'Tempo: ', ptcop.tempo
        print 'Num units:', num_units

        # Make enough units
        while len(ptcop.units) < num_units:
            ptcop.units.append( Unit() )

        # Move to the event block and find out how big it is.
        events_end = seek_block(stream, 'Event V5')

        abs_position = 0
        num_events = 0

        # Loop over the event block.
        while stream.tell() < events_end:

            position = vlq(stream)
            unit_id = ord(stream.read_byte())
            event_id = ord(stream.read_byte())
            event_value = vlq(stream)

            print stream.tell(), '|', abs_position, '|', position, unit_id, event_id, event_value

            if event_id == 0:
                print 'Invalid event!\n'
                continue

            # Increment the absolute position
            abs_position += position
            num_events += 1

            try: 
                unit = ptcop.units[unit_id]
                event = Event(abs_position, event_id, event_value)
                unit.events.append(event)
            except:
                print 'Invalid event!\n'
                print 'Reached the end of the event block before I expected to!'
                break

        # Close up the streams
        stream.close()
        f.close()

        print 'Loaded %s units with %s events.'%(num_units, num_events)

        return ptcop

class Unit:
    def __init__(self):
        self.events = list()

class Event:
    def __init__(self, position, type, value):
        self.position = position
        self.type = type
        self.value = value

# moves a stream to the beginning of a block's data section and returns the block's end pos
def seek_block(stream, tag):
    stream.seek(stream.find(tag)+8)
    length = read_int(stream)
    end = stream.tell() + length
    print 'Block "%s" is %s bytes long and it ends at byte %s.'%(tag, length, end)
    return end

# Reads an integer out of a byte stream and advances the stream position
def read_int(stream):
    return struct.unpack('<i', stream.read(4))[0]

# function for reading variable-length quantities from a byte stream
def vlq(stream):
    v = ord(stream.read_byte())
    if v > 0x7f:
        return v + 80*(vlq(stream) - 1)
    else:
        return v


######## woooo!~!~!!!

ptcop = PTCOP.load('file.ptcop')
midi = MIDIFile(len(ptcop.units))

for i, unit in enumerate(ptcop.units):

    midi.addTrackName(i, 0, 'Track %s'%(i+1))
    # midi.addTempo(i, 0, ptcop.tempo)
    midi.addTempo(i, 0, 120)

    note = 80

    for e in unit.events:
        if e.type == 1:
            midi.addNote(i, 0, note, e.position/384.0, 0.1, 127)
        elif e.type == 2:

            # I think this is probably wrong ....
            note = 48 + (e.value - 15888) / 160

            if note > 127:
                note = 127
            if note < 0:
                note = 0
            print note, e.value



out = open('output.mid', 'wb')
midi.writeFile(out)
out.close()
