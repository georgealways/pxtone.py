import sys

import pxtone
from pxtone import enum

from MidiFile import MIDIFile

MIDIEvents = enum(
    PITCH_BEND = 1,
    VOLUME = 7,
    PAN = 10
)

# means pitchwheel must be set to +-12 semitones
PITCH_BEND_SEMITONES = 48


def ptcop2midi(ptcop, outfile):

    midi = MIDIFile(200)

    print ptcop2midi_beat(8160)


    for i, unit in enumerate(ptcop.units):

        channel = 0
        track = i

        midi.addTrackName(i, channel, unit.name)
        midi.addTempo(i, channel, int(sys.argv[2]))

        note = 80
        velocity = 104
        porta = 0

        bend = 0x4000/2

        for e in unit.events:

            beat = ptcop2midi_beat(e.position)

            if e.type == pxtone.EventType.VOICE:

                # track = e.value
                velocity = e.value

            elif e.type == pxtone.EventType.ON:
                

                # find all note events in the range of 
                # (beat, ptcop2midi_beat(e.value))

                notes = unit.notes_between(e.position, e.position + e.value)


                if not notes:
                    midi.addNote(track, 
                                 channel,
                                 note,
                                 beat,
                                 max(ptcop2midi_beat(e.value)-0.001, 0.001),
                                 velocity)
                else:
                    
                    if notes[0].position != e.position:
                        midi.addNote(track, 
                                 channel,
                                 note,
                                 beat,
                                 ptcop2midi_beat(notes[0].position - e.position),
                                 velocity)

                    j = 0;
                    l = len(notes)-1

                    while j < l:

                        midi.addNote(track,
                                 channel,
                                 ptcop2midi_note(notes[j].value),
                                 ptcop2midi_beat(notes[j].position),
                                 ptcop2midi_beat(notes[j+1].position - notes[j].position),
                                 velocity)

                        j += 1

                    midi.addNote(track,
                                 channel,
                                 ptcop2midi_note(notes[-1].value),
                                 ptcop2midi_beat(notes[-1].position),
                                 max(ptcop2midi_beat(e.position + e.value - notes[-1].position)-0.001, 0.001),
                                 velocity)

            elif e.type == pxtone.EventType.VELOCITY:

                # velocity = e.value
                pass
                
            elif e.type == pxtone.EventType.NOTE:

                note = ptcop2midi_note(e.value)
                        
            elif e.type == pxtone.EventType.KEY_PORTA:

                midi.addPitchBendEvent(track, channel, beat, e.value);


            # elif e.type == pxtone.EventType.VOLUME:

            #     midi.addControllerEvent(track,
            #                             channel,
            #                             beat,
            #                             MIDIEvents.VOLUME,
            #                             e.value)

            # elif e.type == pxtone.EventType.PAN:


            #     midi.addControllerEvent(track,
            #                             channel,
            #                             beat,
            #                             MIDIEvents.PAN,
            #                             e.value)



    out = open(outfile, 'wb')
    midi.writeFile(out)
    out.close()

def map( num, minA, maxA, minB, maxB ):
    return ( num - minA ) / ( maxA - minA ) * ( maxB - minB ) + minB

def ptcop2midi_cc(value):
    return int(value / 127.0 * 0x3FFF)

def ptcop2midi_beat(value):
    return value / 480.0

def midi2ptcop_beat(value):
    return value * 480.0

def ptcop2midi_note(value):
    
    note = 69 + (value - 0x6000)/0x100
    
    if note > 127:
        print 'Interpreted invalid note from:', value, note
        note = 127
    
    if note < 0:
        print 'Interpreted invalid note from:', value, note
        note = 0

    return note


if __name__ == "__main__":
    path = sys.argv[1]
    p = pxtone.PTCOP.load(path)
    ptcop2midi(p, '../site/mid/'+path.replace('.ptcop', '').replace('ptcop/','') + '.mid')