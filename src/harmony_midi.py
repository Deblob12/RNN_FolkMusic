
"""Create's a harmony at a fixed diatonic interval for any midi file which does
not contain accidental notes.  If an acidental is encountered, the harmony will
be P8 or -P8."""

from __future__ import print_function
import music21 as m21
import os
def parentdir(path_, n=1):
    for i in range(n):
        path_ = os.path.dirname(path_)
    return path_

KEY = ''
INTERVAL = -5  # can be -7, -6, ..., -1, 1, 2, ..., or 7
# FIN = os.path.join(os.path.dirname(__file__), 'test.mid')
# FOUT = os.path.join(os.path.dirname(__file__), 'test_harmony.mid')
FIN = os.path.join(os.path.dirname(__file__), 'lightning-bugs-midi-track.mid')
FOUT = os.path.join(os.path.dirname(__file__), 'lightning-bugs-midi-track_harmony_' + str(INTERVAL) +'.mid')
FIX_OCTAVE = True  # use to retain the octave 


m21.defaults.ticksPerQuarter = 1024*16

def sgn(x):
    return cmp(x, 0)


def nzint(interval_):
    """converts a diatonic degree/interval to be a unit with a natural 0.
    I.e. 1, -1 notes become 0; 2, -2 become 1, etc."""
    return sgn(interval_)*(abs(interval_) - 1)


def harmonize_pitch_in_place(p, interval, key, fix_octave=False):
    """Create's a harmony with pitch `p` with a distance determined by the 
    input diatonic interval, `interval` and key.
    If p is not in the input key, the harmony will
    be P8 or -P8 (match the sign of `interval')."""
    key_notes = [kp.midi % 12 for kp in key.pitches]
    try:
        degree = key_notes.index(p.midi % 12) + 1
    except ValueError:
        p.transpose(sgn(interval)*12, inPlace=True)
        return
    new_degree = degree + nzint(interval)

    if fix_octave:
        octave_adjustment = 0
    else:
        octave_adjustment = nzint(new_degree)//6
    new_pitch = key.pitchFromDegree(new_degree)
    adjustment = (new_pitch.midi - p.midi) % 12 + 12*octave_adjustment
    # from pdb import set_trace; set_trace()
    p.transpose(adjustment, inPlace=True)


# Parse input and user args
mf = m21.midi.MidiFile()
mf.open(FIN)
mf.read()
mf.close()
score = m21.midi.translate.midiFileToStream(mf, quantizePost=False)
# score = m21.converter.parse(FIN)
if not KEY:
    try:
        key = score.analyze('key')
    except:
        raise Exception("Having difficulty determining key.  "
                        "Please specify a key.")
else:
    key = m21.key.Key(KEY)
print("Using key:", key)

# Harmonize the score
for part in score.parts:
    for p in part.pitches:
        print(p, end=' -> ')
        # print ''
        # score.show('t')
        harmonize_pitch_in_place(p, interval=INTERVAL, 
                                    key=key, 
                                    fix_octave=FIX_OCTAVE)
        # print ''
        # score.show('t')
        # print ''
        print(p)
        # raw_input()

m = m21.midi.translate.streamToMidiFile(score)
m.open(FOUT, 'wb')
m.write()
m.close()

