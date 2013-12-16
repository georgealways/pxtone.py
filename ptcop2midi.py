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
PITCH_BEND_SEMITONES = 2

# pxtone "positions" per pitch bend frame
PITCH_BEND_DETAIL = 10

def ptcop2midi(ptcop, outfile):

    midi = MIDIFile(len(ptcop.units))

    for i, unit in enumerate(ptcop.units):

        channel = 0

        midi.addTrackName(i, channel, unit.name)
        midi.addTempo(i, channel, ptcop.tempo)

        # set pitch bend range
        midi.addControllerEvent(i, channel, 0, 101, 0)
        midi.addControllerEvent(i, channel, 0, 100, 0)
        midi.addControllerEvent(i, channel, 0, 6, PITCH_BEND_SEMITONES)
        midi.addControllerEvent(i, channel, 0, 101, 127)
        midi.addControllerEvent(i, channel, 0, 100, 127)

        note = 80
        velocity = 127
        porta = 0

        for e in unit.events:

            beat = ptcop2midi_beat(e.position)
            print e.position, beat

            if e.type == pxtone.EventType.ON:
                
                midi.addNote(i, 
                             channel,
                             note,
                             beat,
                             ptcop2midi_beat(e.value),
                             velocity)

            elif e.type == pxtone.EventType.VELOCITY:
                velocity = e.value

            elif e.type == pxtone.EventType.NOTE:

                note = ptcop2midi_note(e.value)

                on = unit.on(e.position)

                if on:

                    if on.position == e.position:

                        # reset pitch bend
                        midi.addPitchBendEvent(i, channel, beat, 0x3FFF/2);

                    else:

                        # glissando
                    
                        # on what note did the "on" begin?
                        old_note = unit.note_at(e.position)
                        old_note = ptcop2midi_note(old_note)

                        # semitones to travel
                        diff = note - old_note

                        # where the pitch bend should wind up
                        target = 0x3FFF/2 - diff * 0x3FFF / (PITCH_BEND_SEMITONES*2) 

                        midi.addPitchBendEvent(i, channel, beat, 0x3FFF/2);
                        midi.addPitchBendEvent(i, channel, beat + ptcop2midi_beat(porta), target);
                        
            elif e.type == pxtone.EventType.KEY_PORTA:

                porta = e.value

            # elif e.type == pxtone.EventType.VOLUME:

            #     midi.addControllerEvent(i,
            #                             channel,
            #                             beat,
            #                             MIDIEvents.VOLUME,
            #                             e.value)

            # elif e.type == pxtone.EventType.PAN:


            #     midi.addControllerEvent(i,
            #                             channel,
            #                             beat,
            #                             MIDIEvents.PAN,
            #                             e.value)



    out = open(outfile, 'wb')
    midi.writeFile(out)
    out.close()


def ptcop2midi_cc(value):
    return int(value / 127.0 * 0x3FFF)

def ptcop2midi_beat(value):
    return value / 480.0

def ptcop2midi_note(value):
    
    # wtf are these numbers even ...
    note = 60 + (value - 15888) / 160
    
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
    ptcop2midi(p, path + '.mid')