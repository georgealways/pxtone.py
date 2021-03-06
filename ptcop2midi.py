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
PITCH_BEND_SEMITONES = 12

def ptcop2midi(ptcop, outfile):

    midi = MIDIFile(len(ptcop.units))

    for i, unit in enumerate(ptcop.units):

        channel = 0

        midi.addTrackName(i, channel, unit.name)
        midi.addTempo(i, channel, ptcop.tempo)

        note = 80
        velocity = 104
        porta = 0

        bend = 0x4000/2

        for e in unit.events:

            beat = ptcop2midi_beat(e.position)

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
                        if bend != 0x4000/2:
                            bend = 0x4000/2
                            midi.addPitchBendEvent(i, channel, beat, bend);

                    else:

                        # glissando
                    
                        # on what note did the "on" begin?
                        old_note = unit.note_before(e.position)
                        old_note = ptcop2midi_note(old_note)

                        # semitones to travel
                        diff = note - old_note

                        # where the pitch bend should wind up
                        target = 0x4000/2 + diff * 0x4000 / (PITCH_BEND_SEMITONES*2) 

                        print porta, target

                        midi.addPitchBendEvent(i, channel, beat, bend);
                        midi.addPitchBendEvent(i, channel, beat + ptcop2midi_beat(porta), target);

                        bend = target
                        
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
    ptcop2midi(p, path + '.mid')