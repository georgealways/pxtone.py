import mmap, struct, os, math

class PTCOP:

    def __init__(self):

        self.units = list()
        self.tempo = 96

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
        # stream.read(6)

        # (totally wrong)

        # ptcop.tempo = vlq(stream) 
        print 'Tempo: ', ptcop.tempo
        print 'Num units:', num_units

        # Make enough units
        while len(ptcop.units) < num_units:
            # todo: actually read from WOIC
            name = 'Track %s'%(len(ptcop.units) + 1)
            ptcop.units.append( Unit(name) )

        # Move to the event block and find out how big it is.
        events_end = seek_block(stream, 'Event V5')

        abs_position = 0
        events_read = 0
        num_events = read_int(stream)
        print 'Num events:', num_events

        # Loop over the event block.
        while events_read < num_events:

            position = vlq(stream)
            unit_id = ord(stream.read_byte())
            event_id = ord(stream.read_byte())
            event_value = vlq(stream)

            # print stream.tell(), '|', abs_position, '|', position, unit_id, event_id, event_value

            if event_id == 0:
                print 'Invalid event!\n'
                continue

            # Increment the absolute position
            abs_position += position
            events_read += 1

            try: 
                unit = ptcop.units[unit_id]
                event = Event(abs_position, event_id, event_value)
                # unit.position += position

                unit.events.append(event)
            except:
                print 'Invalid event!\n'
                print 'Reached the end of the event block before I expected to!'
                break

        # Close up the streams
        stream.close()
        f.close()

        print 'Loaded %s units with %s events.'%(num_units, events_read)

        return ptcop

class Unit:
    def __init__(self, name):
        self.events = list()
        self.name = name
        self.position = 0

    def on(self, position):

        # find latest "on" event before position

        on_events = filter(
            lambda e: e.position <= position and e.type == EventType.ON, 
            self.events)

        if len(on_events) == 0:
            return None

        last_event = on_events[-1]

        if last_event.position + last_event.value >= position:
            return last_event

        return None


    # returns the oldest NOTE before this position that precedes or coincides with an ON
    def note_before(self, position):

        on_events = filter(
            lambda e: e.position < position and e.type == EventType.ON, 
            self.events)

        if len(on_events) == 0:
            return 0x6000

        last_on = on_events[-1]

        note_events = filter(
            lambda e: e.position < position and e.type == EventType.NOTE, 
            self.events)


        for e in reversed(note_events):
            if e.position <= last_on.position:
                return e.value

        return 0x6000

class Event:
    def __init__(self, position, type, value):
        self.position = position
        self.type = type
        self.value = value


# http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

EventType = enum(
    ON = 0x1,
    NOTE = 0x2,
    PAN = 0x3,
    VELOCITY = 0x4,
    VOLUME = 0x5,
    KEY_PORTA = 0x6,
    VOICE = 0xC,
    GROUP = 0xD,
    KEY_CORRECT = 0xE,
    PAN_TIME = 0xF
)

# moves a stream to the beginning of a block's data section and returns the block's end pos
def seek_block(stream, tag):
    stream.seek(stream.find(tag)+8)
    length = read_int(stream)
    end = stream.tell() + length
    print 'Block "%s" is %s bytes long and it ends at byte %s.'%(tag, length, end)
    # todo, this doesn't seem to be reporting proper ending pos
    return end

# Reads an integer out of a byte stream and advances the stream position
def read_int(stream):
    return struct.unpack('<i', stream.read(4))[0]

# function for reading variable-length quantities from a byte stream
def vlq(stream):
    v = ord(stream.read_byte())
    if v > 0x7f:
        return v + 0x80*(vlq(stream)-1)
    else:
        return v
