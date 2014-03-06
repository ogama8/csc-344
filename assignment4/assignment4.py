################################################################################
# Eli Backer - CSC 344 - Project 4 - Winter 2014
# DESCRIPTION
################################################################################

import os
import sys
import random

from midiutil.MidiFile import MIDIFile

# Define "constants"

# Constants for all the notes
TRACK = 0
CHANNEL = 0
VOLUME = 127
DURATION = 1
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]

CHORD_HARMONIZATION = [[1, 4],    # Chords for a note of scale degree 1
                       [5, 2],
                       [1],
                       [4, 2],    # Chords for a note of scale degree 4
                       [1, 5],    # Chords for a note of scale degree 5
                       [4, 2],
                       [5]]

MAJOR_CHORDS = [True, False, False, True, True, False, False]


# NEED TO ADD: NO MOTION-  V -> IV, ii -> IV, V -> ii, ii -> I


# These are all functions used in the main of the code.  They are here because
# python does not have function prototypes.
def name_to_num(string):
    """
    Given the name of a note (C is natural, c is sharp, etc) and an octave
    returns the corrisponding note number.  Ex. C4 -> 60
    """
    letters = ["C", "c", "D", "d", "E", "F", "f", "G", "g", "A", "a", "B"]
    for i in range(len(letters)):
        if string[0] == letters[i]:
            return (int(string[1:])+2)*12 +i

def major_chord(midiNoteNumber):
    """
    Given a midi NN, returns an array, representing the notes in the major chord
    Ex. 60 -> [60, 64, 67]
    """
    return [midiNoteNumber, midiNoteNumber+4, midiNoteNumber+7]

def minor_chord(midiNoteNumber):
    """
    Given a midi NN, returns an array, representing the notes in the minor chord
    Ex. 60 -> [60, 63, 67]
    """
    return [midiNoteNumber, midiNoteNumber+3, midiNoteNumber+7]

def write_chord(midiFile, chordArray, currentTime, chordDuration):
    """
    THIS FUNCTION MUTATES midiFile!!  It adds the cords from chordArray to the 
    sequence of notes.
    """
    for note in chordArray:
        midiFile.addNote(TRACK, CHANNEL, note, currentTime, 
                         chordDuration, VOLUME)


# The main code is here.
if __name__ == '__main__':
    if len(sys.argv) == 2:      # If there is a file name after the code 
        textFile = sys.argv[1]  # is run, use it.
    else:                       # Otherwise just use this one.
        textFile = 'sopranoLine.txt'
    
    # Figuring out MELODY
    scaleDegreeList = open(textFile, 'r').readlines()[0].split(' ')
    key_full = scaleDegreeList[0]
    
    scaleDegreeList.remove(key_full)
    scaleDegreeList = [int(i) for i in scaleDegreeList]
    
    melodyList = [MAJOR_SCALE[(deg-1)%7] + int((deg-1)/7)*12 
                        for deg in scaleDegreeList]


    # Figuring out CHORDS
    chordRNList = [CHORD_HARMONIZATION[(deg-1)%7][random.randint(0, len(CHORD_HARMONIZATION[(deg-1)%7])-1)] 
                        for deg in scaleDegreeList]
    
    # >>Eventually, chord progressions will be considered here<<

    chordList = [major_chord(MAJOR_SCALE[rn-1]+48) if MAJOR_CHORDS[rn-1] 
                        else minor_chord(MAJOR_SCALE[rn-1]+48) 
                        for rn in chordRNList]



    # Create the MIDIFile Object
    myMIDI = MIDIFile(1)
    
    # Add track name and tempo. The first argument to addTrackName and
    # addTempo is the time to write the event.
    
    myMIDI.addTrackName(TRACK, 0, "CSC-344_AlgComp")
    myMIDI.addTempo(TRACK, 0, 110)

    time = 0
    for note in melodyList:
        myMIDI.addNote(TRACK, CHANNEL, note+60, time, DURATION, VOLUME)
        time += DURATION


    time = 0
    for chord in chordList:
        write_chord(myMIDI, chord, time, DURATION)
        time += DURATION

    # Write it to disk.
    binfile = open("output.mid", 'wb')
    myMIDI.writeFile(binfile)
    binfile.close()
