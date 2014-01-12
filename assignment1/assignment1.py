###############################################################
# Eli Backer - Jan 2014 - assignment1.py
# This script takes in a WAV file and randomly repeats bits
# of it.  That sound is then rewritten to the source directory
# with "_REWRITE" attached to the end of the file name.
###############################################################

import sys
import math
import wave
import random
import progressbar


REPEAT_VALS   = [2, 3, 4, 6, 8, 12, 16]
RANDOM_CHANCE = .5
RESET_RATE    = 1


if __name__ == '__main__':
    if len(sys.argv) == 2:
    	fileName = sys.argv[1]
	
	inWAV    = wave.open(fileName, 'r')
	wavLen   = inWAV.getnframes()
	sampRate = inWAV.getframerate()
	inLen	 = int(math.floor(wavLen/sampRate))

	outWAV = wave.open(fileName[:-4] + '_REWRITE.wav', 'w')
	outWAV.setnchannels(inWAV.getnchannels())
	outWAV.setframerate(inWAV.getframerate())
	outWAV.setsampwidth(inWAV.getsampwidth())

	bar = progressbar.ProgressBar(maxval=inLen, \
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

	for i in range(0, inLen):
		if (i % RESET_RATE == 0):
			inWAV.setpos(i * sampRate)

		repeatDivision = REPEAT_VALS[random.randint(0, len(REPEAT_VALS) - 1)]
		sampLen        = sampRate/repeatDivision

		for j in range(0,repeatDivision):
			if (random.random() < RANDOM_CHANCE  and  i != 0):
				inWAV.setpos(inWAV.tell() - sampLen)
			outWAV.writeframesraw(inWAV.readframes(sampLen))
		bar.update(i)
    
	outWAV.close()
    bar.finish()