
"""Create's a harmony at a fixed diatonic interval for any midi file which does
not contain accidental notes.  If an acidental is encountered, the harmony will
be P8 or -P8."""

from __future__ import print_function
import music21 as m21
import os
import argparse

def cmp(a, b):
    return (a > b) - (a < b) 

def get_parser():
    """Get parser for command line arguments."""
    parser = argparse.ArgumentParser(description="Harmonize-With-Midi")
    parser.add_argument(
        "input_midi",
        help="Input midi file."
    )
    parser.add_argument(
        'interval',
        type=int,
        help="The interval (use positive integer ascending and negative for "
             "descending).  "
             "Can be ..., -7, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6,  or 7, ..."
    )
    parser.add_argument(
        "-k",
        "--key",
        help=('(Optional) The Key. Use capital for major, lowercase for minor, '
              'e.g. "C#" for C# Major and "c#" for C# Minor.  If no key is '
              'chosen, the code will attempt to key find the key automatically.'
              '\n\n'

              'Note: Midi files containing key changes are not currently '
              'supported.\n\n'

              'Note: non-diatonic notes will always be harmonized using P8.'),
        default=None,
    )
    parser.add_argument(
        "-o",
        "--output_midi",
        default=None,
        help="Name for output midi file.  Defaults to the name of you input "
             "file with '_harmony_<interval>' before the extension.  "
             "E.g. 'test.mid' could output 'test_harmony_3.mid'"
    )
    parser.add_argument(
        "-t",
        "--fix_timing",
        action='store_true',
        default=False,
        help="OK, so using `music21` to make this was maybe a bad choice.  "
             "Turns out there's automatic quantization.  This flag will up the "
             "`ticksPerQuarter` default in `music21` to 2^14, which should "
             "help prevent too much quantization. This is not a perfect fix."
    )
    parser.add_argument(
        "-f",
        "--fixed_octave",
        action='store_true',
        default=False,
        help="Use to force harmony to stay a one octave range."
    )
    return parser


def parentdir(path_, n=1):
    for i in range(n):
        path_ = os.path.dirname(path_)
    return path_


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


if __name__ == '__main__':

    # Parse input and user args
    args = get_parser().parse_args()

    if args.output_midi:
        output_file = args.output_midi
    else:
        name, ext = os.path.splitext(args.input_midi)
        output_file = name + '_' + 'harmony' + '_' + str(args.interval) + '.mid'

    if args.fix_timing:
        m21.defaults.ticksPerQuarter = 1024*16

    # read the midi into music21
    mf = m21.midi.MidiFile()
    mf.open(args.input_midi)
    mf.read()
    mf.close()
    score = m21.midi.translate.midiFileToStream(mf, quantizePost=False)
    #score = m21.converter.parse(args.input_midi)

    # figure out the key (if use didn't suggest it)
    if not args.key:
        try:
            key = score.analyze('key')
        except:
            raise Exception("Having difficulty determining key.  "
                            "Please specify a key.")
    else:
        key = m21.key.Key(args.key)
    print("Using key:", key)

    # Harmonize the score
    for part in score.parts:
        for p in part.pitches:
            print(p, end=' -> ')
            # print ''
            # score.show('t')
            harmonize_pitch_in_place(p, interval=args.interval,
                                        key=key,
                                        fix_octave=args.fixed_octave)
            # print ''
            # score.show('t')
            # print ''
            print(p)
            # raw_input()

    m = m21.midi.translate.streamToMidiFile(score)
    m.open(output_file, 'wb')
    m.write()
    m.close()

