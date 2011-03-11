#!/usr/bin/env python
#

# Python script to read a m5b file extracted with disk2file and print the start and stop time.
# The file is read in two steps: the header composed of 4 32 bit words and the body of the frame
# composed of 2500 32 bit words.

# Improvements: now this script does not read _every_ frame in order to get the start and stop
#		times. It simply reads the first and skips to the last.    --Rurik

import sys, string, os, struct

def getTimeString(bcdDay, bcdDay2):
	dayStr = str(hex(bcdDay))
	day = dayStr[2:5]
	secsInDay = int(dayStr[5:10])
	hour = int(secsInDay/3600)
	minute = int( (secsInDay - 3600*hour) / 60)
	second = int( (secsInDay - 3600*hour - 60*minute) )
	strbcdDay2 = "0x%x" %bcdDay2
	fracSecondsStr = strbcdDay2[2:-4]
	if fracSecondsStr == '':
		fracSeconds = 0
	else:
		fracSeconds = int(fracSecondsStr)
	strLine = "%s.%02d:%02d:%02d.%04d" % ( day, hour, minute, second, fracSeconds)
	return strLine, (day, hour, minute, second, fracSeconds)

def main(argv):
	
	if len(sys.argv)<2:
		print "Usage: %s filename" % (sys.argv[0])
		sys.exit()

	fOutName = sys.argv[1]

        try:
		fIn = open(fOutName,'r')
	except:
		print "\nCould not open file %s " % (fOutName)
		sys.exit(-1)

	frameSize = 2500 * 4
	headerSize = 4 * 4

	# Header is composed of 4 words of 32 bits:
	mk5bheaderFormat = 'lllL'	# Originally this read 'llLl' but on long scans
					# the last signed-long wraps around, so I changed it
					# to an unsigned-long   --Rurik

	headerFrame = fIn.read(headerSize)
	if headerFrame == '':
		fIn.close()
		return
	(syncWord, word2, bcdDay, bcdDay2) = struct.unpack(mk5bheaderFormat, headerFrame)
		
	strLine, start = getTimeString(bcdDay, bcdDay2)
	print "Start Time: %s" % ( strLine)

	# Now skip to the last frame, and read the header.
	fIn.seek(0,2)					# Skip to last byte
	rearOffset = fIn.tell()%(headerSize+frameSize)	# find offset of the beginning of the last frame
	fIn.seek(-rearOffset-(headerSize+frameSize),2)	# and move to the frame before it
	lastFrame = fIn.tell()/(headerSize+frameSize) + 1
	headerFrame = fIn.read(headerSize)
	(syncWord, word2, bcdDay, bcdDay2) = struct.unpack(mk5bheaderFormat, headerFrame)
	
	strLine, stop = getTimeString(bcdDay, bcdDay2)
	print " Stop Time: %s" % ( strLine)
	
	fIn.close()

	strLine = 'Total time: '
	if stop[0] <> start[0]:
		strLine += "%i days, " %(stop[0]-start[0])
	if stop[1] <> start[1]:
		strLine += "%i hours, " %(stop[1]-start[1])
	if stop[2] <> start[2]:
		strLine += "%i minutes, " %(stop[2]-start[2])
	strLine += "%i.%04i seconds" %(stop[3]-start[3],stop[4]-start[4])
	print strLine

	print "    Frames: %i" %lastFrame


if __name__ == "__main__":
    main(sys.argv)
