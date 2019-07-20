import os
import subprocess
import regex as re


def extract_song_snippet(generated_text):
    pattern = '\n\n(.*?)\n\n'
    search_results = re.findall(pattern, generated_text, overlapped=True, flags=re.DOTALL)
    songs = [song for song in search_results]
    print ("Found {} possible songs in generated texts".format(len(songs)))
    return songs

def save_song_to_abc(song, filename="tmp"):
    save_name = "{}.abc".format(filename)
    with open(save_name, "w") as f:
        f.write(song)
    return filename

def abc2wav(abc_file):
    path_to_tool = './abc2wav'
    cmd = "{} {}".format(path_to_tool, abc_file)
    return os.system(cmd)
def abc2midiHarmonize(abc_file):
    path_to_tool = './abc2midiharm'
    cmd = "{} {}".format(path_to_tool, abc_file)
    return os.system(cmd)

def play_wav(wav_file):
    from IPython.display import Audio
    return Audio(wav_file)

def play_generated_song(generated_text):
    songs = extract_song_snippet(generated_text)
    if len(songs) == 0:
        print ("No valid songs found in generated text. Try training the model longer or increasing the amount of generated music to ensure complete songs are generated!")

    for song in songs:
        basename = save_song_to_abc(song)
        ret = abc2wav(basename+'.abc')
        if ret == 0: #did not suceed
            return play_wav(basename+'.wav')
    print ("None of the songs were valid, try training longer to improve syntax.")

def abc2midi(abc_file):
    path_to_tool = './abc2midi'
    cmd = "{} {}".format(path_to_tool, abc_file)
    return os.system(cmd)

def save_song(generated_text, name):
    songs = extract_song_snippet(generated_text)
    n = len(songs)
    if n == 0:
        print ("No valid songs found in generated text. Try training the model longer or increasing the amount of generated music to ensure complete songs are generated!")
    for i in range(n):
        savename = "{}{}".format(name, i)
        basename = save_song_to_abc(songs[i], savename)
        ret = abc2wav(basename+'.abc')
    
def save_midi(generated_text, name):
    songs = extract_song_snippet(generated_text)
    n = len(songs)
    if n == 0:
        print ("No valid songs found in generated text. Try training the model longer or increasing the amount of generated music to ensure complete songs are generated!")
    for i in range(n):
        savename = "{}{}".format(name, i)
        basename = save_song_to_abc(songs[i], savename)
        ret = abc2midi(basename+'.abc')

def save_midi_harmonize(generated_text, name):
    songs = extract_song_snippet(generated_text)
    n = len(songs)
    if n == 0:
        print ("No valid songs found in generated text. Try training the model longer or increasing the amount of generated music to ensure complete songs are generated!")
    for i in range(n):
        savename = "{}{}".format(name, i)
        basename = save_song_to_abc(songs[i], savename)
        ret = abc2midiHarmonize(basename+'.abc')

