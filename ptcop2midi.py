import sys

import pxtone
from pxtone import enum

from midiutil.MidiFile import MIDIFile

MIDIEvents = enum(
    PITCH_BEND = 1,
    VOLUME = 7,
    PAN = 10
)

# means pitchwheel must be set to +-12 semitones
PITCH_BEND_SEMITONES = 12

# pxtone "positions" per pitch bend frame
PITCH_BEND_DETAIL = 10

def ptcop2midi(ptcop, outfile):

    midi = MIDIFile(len(ptcop.units))
    channel = 0

    for i, unit in enumerate(ptcop.units):

        midi.addTrackName(i, channel, unit.name)
        midi.addTempo(i, channel, ptcop.tempo)

        note = 80
        velocity = 127
        porta = 0

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

                # is the track currently on?
                # if so, let's glissando
                if unit.is_on(e.position):
                
                    # on what note did the "on" begin?
                    old_note = unit.note_at(e.position)
                    old_note = ptcop2midi_note(old_note)

                    # semitones to travel
                    diff = note - old_note

                    # where the pitch bend should wind up
                    target = diff * 0x3FFF / (PITCH_BEND_SEMITONES*2) 

                    # how many frames of porta to add?
                    frames = porta / PITCH_BEND_DETAIL + 1

                    for f in range(frames):
                        
                        bend = 0x3FFE/2 + f/float(frames) * target
                        bend = int(bend)

                        offset = ptcop2midi_beat(f * PITCH_BEND_DETAIL)
                        offset += beat

                        data = midi_14bit(bend, channel, MIDIEvents.PITCH_BEND)

                        # midi.addControllerEvent(i,
                        #                         data['channel'],
                        #                         beat + offset,
                        #                         data['type'],
                        #                         data['value'])

            elif e.type == pxtone.EventType.KEY_PORTA:
                porta = e.value

            elif e.type == pxtone.EventType.VOLUME:

                midi.addControllerEvent(i,
                                        channel,
                                        beat,
                                        MIDIEvents.VOLUME,
                                        e.value)

            elif e.type == pxtone.EventType.PAN:

                val = ptcop2midi_cc(e.value)

                data = midi_14bit(bend, channel, MIDIEvents.PAN)

            #     midi.addControllerEvent(i,
            #                             data['channel'],
            #                             beat + offset,
            #                             data['type'],
            #                             data['value'])



    out = open(outfile, 'wb')
    midi.writeFile(out)
    out.close()

def midi_14bit(value, channel, type):
    # todo, pack 14 bit value in to [127, 127, 127]
    return dict(channel=achannel, type=atype, value=avalue)

def ptcop2midi_cc(value):
    return int(value / 127.0 * 0x3FFF)

def ptcop2midi_beat(value):
    return value / 384.0

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