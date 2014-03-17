################################################################################
# Eli Backer - CSC 344 - Project 5 - Winter 2014
# A "poem accompanyment" tool of sorts..
################################################################################

import os
import sys
import random
import string

from midiutil.MidiFile import MIDIFile

# Define "constants"
SYL_FILE = "mhyph.txt"
HYPH_CHARS = ["\xa5", "-", " "]

SYL_DURATION = .29
CHORD_DURATION = 8

COMMA_REST_TIME = SYL_DURATION
PERIOD_REST_TIME = 3*SYL_DURATION

SPEECH_DELAY_START = int(60.0/170.0 * 4*CHORD_DURATION * 1000)
START_DELAY = 8
GREETING = "hello"


# Constants for all the notes
TRACK = 0
CHANNEL = 0
VOLUME = 127
DRUM_MIDI_NN = 36

# Pretty Chords
PRETTY_CHORDS = [['C3','E3','A3','D4'],
                ['A2','E3','G3','C4'],
                ['G2','D3','G3','C4'],
                ['A2','C3','G3','A3'],
                ['C3','E3','A3','E4'],
                ['A2','E3','A3','B3'],
                ['G2','D3','A3','D4'],
                ['G2','C3','G3','B3']]



# These are all functions used in the main of the code.  They are here because
# python does not have function prototypes.
def parse_hyphens(inputFileName):
    """
    This function takes in a file name and, from that file parses it to a
    dictionary, mapping words to syllables.  It is dependant on a global
    definition of HYPH_CHARS, an array of characters that denote hyphenation.
    """
    inputFileString = open(inputFileName, 'r').readlines()
    wordArray = [inString[:-2] for inString in inputFileString]
    dictionary = {}
    for word in wordArray:
        sylCount = 1
        for delimChar in HYPH_CHARS:
            sylCount += word.count(delimChar)
        dictionary[filter(lambda x: x in string.printable, word).lower()] = sylCount

    return dictionary

def name_to_num(noteNameString):
    """
    Given the name of a note (C is natural, c is sharp, etc) and an octave
    returns the corrisponding note number.  Ex. C4 -> 60
    """
    letters = ["C", "c", "D", "d", "E", "F", "f", "G", "g", "A", "a", "B"]
    for i in range(len(letters)):
        if noteNameString[0] == letters[i]:
            return (int(noteNameString[1:])+2)*12 +i

def write_chord(midiFile, chordArray, currentTime, chordDuration, chordVolume):
    """
    THIS FUNCTION MUTATES midiFile!!  It adds the cords from chordArray to the
    sequence of notes.
    """
    for note in chordArray:
        midiFile.addNote(TRACK, CHANNEL, name_to_num(note), currentTime,
                         chordDuration, chordVolume)



################################################################################
# The main code is here.
if __name__ == '__main__':
    if len(sys.argv) == 2:      # If there is a file name after the code
        textFile = sys.argv[1]  # is run, use it.
    else:                       # Otherwise just use this one.
        textFile = 'iam.txt'

    # Parsing the hyphen file to a dictionary
    hyphenDict = parse_hyphens(SYL_FILE)
    
    # Reading in the text file to be parsed
    textArray = filter(None, [line.strip('\n') 
                                for line in open(textFile, 'r').readlines()])
    fullString = ''
    for line in textArray:
        fullString += line.replace("'", "") + ' [[slnc 2000]] '

    # Generating the text-to-speech file
    os.system("say -v ralph -o poem_READ.aiff {greeting}[[slnc {delayTime}]] {toSay}".format(greeting=GREETING, delayTime=SPEECH_DELAY_START, toSay=fullString))


    # Create the MIDIFile Object
    beatMIDI = MIDIFile(1)
    chordMIDI = MIDIFile(1)
    arpMIDI = MIDIFile(1)

    # Add track name and tempo. The first argument to addTrackName and
    # addTempo is the time to write the event.

    beatMIDI.addTrackName(TRACK, 0, "poem_DRUMS")
    beatMIDI.addTempo(TRACK, 0, 170)

    chordMIDI.addTrackName(TRACK, 0, "poem_CHORDS")
    chordMIDI.addTempo(TRACK, 0, 170)

    arpMIDI.addTrackName(TRACK, 0, "poem_ARP")
    arpMIDI.addTempo(TRACK, 0, 170)

    # This writes the drum track
    time = 3*CHORD_DURATION + START_DELAY
    for i in range(0,2):    # a hackish way to get this to run longer
        for line in [line.split() for line in textArray]:
            for word in line:
                wordStripped = word.strip(",").strip(".").lower()
                if len(wordStripped.strip("'")) <= 2:
                    beatMIDI.addNote(TRACK, CHANNEL, DRUM_MIDI_NN, time, SYL_DURATION, VOLUME)
                    time += SYL_DURATION
                else:
                    for i in range(0, hyphenDict[wordStripped[:-1] if wordStripped not in hyphenDict else wordStripped]):
                        beatMIDI.addNote(TRACK, CHANNEL, DRUM_MIDI_NN, time, SYL_DURATION, VOLUME)
                        time += SYL_DURATION
                if word[-1:] == ",":
                    time += COMMA_REST_TIME
                elif word[-1:] == ".":
                    time += PERIOD_REST_TIME
                else:
                    time += SYL_DURATION
            time = int(time/CHORD_DURATION)*CHORD_DURATION + CHORD_DURATION

    finalTime = time



    # This handles the Chords and Arps
    presentChord = 0
    presentArp = 0
    pastChord = -1
    pastArp = -1

    for time in range(START_DELAY,finalTime):
        if (time%CHORD_DURATION == 0):
            while (presentChord == pastChord):
                presentChord = random.randint(0, len(PRETTY_CHORDS)-1)
            write_chord(chordMIDI, PRETTY_CHORDS[presentChord], time, CHORD_DURATION, VOLUME)
            pastChord = presentChord

        arpDuration = int(CHORD_DURATION/len(PRETTY_CHORDS[pastChord]))
        if (time%arpDuration == 0):
            while (presentArp == pastArp):
                presentArp = random.randint(0, len(PRETTY_CHORDS[pastChord])-1)
            arpMIDI.addNote(TRACK, CHANNEL, name_to_num(PRETTY_CHORDS[pastChord][presentArp])+12, time, arpDuration, VOLUME)
            pastArp = presentArp




    # Write it to disk.
    beatBINFile = open("poem_DRUMS.mid", 'wb')
    beatMIDI.writeFile(beatBINFile)
    beatBINFile.close()

    chordBINFile = open("poem_CHORDS.mid", 'wb')
    chordMIDI.writeFile(chordBINFile)
    chordBINFile.close()

    arpBINFile = open("poem_ARP.mid", 'wb')
    arpMIDI.writeFile(arpBINFile)
    arpBINFile.close()

