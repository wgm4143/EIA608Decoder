def decode608(samples):
	
	# Sync pulse variables
	pulses = []
	pulseMax = 0
	pulseMaxPosition = 0
	isPulsePositive = False

	for sampleNumber in range(len(samples)): # We will start by finding our 7 sync pulses
		sample = samples[sampleNumber]
		if len(pulses) < 7:
			if not isPulsePositive and sample > 64: # Sample crossed the vertical shift zero point of sync pulses upwards
				isPulsePositive = True

			elif isPulsePositive and sample > pulseMax: # Sample is local maxima
				pulseMax = sample
				pulseMaxPosition = sampleNumber

			elif isPulsePositive and sample < 64: # Sample crossed the vertical shift zero point of sync pulses downwards
				isPulsePositive = False
				pulses.append(pulseMaxPosition) # We finished a pulse so add the current pulse max and reset
				pulseMax = 0
		else:
			break # End of sync pulses

	dataBits = []
	bitWidth = int(round((pulses[6] - pulses[0]) / 6.0)) # Calculate average samples between each pulse peak

	checkBitOffset = pulses[6] + bitWidth / 2
	# First check bit should be 0
	if getSampleAverage(samples, checkBitOffset, checkBitOffset + 1 * bitWidth) > 64:
		print "Check bit error"
		return
	# Second check bit should be 0
	if getSampleAverage(samples, checkBitOffset + 1 * bitWidth, checkBitOffset + 2 * bitWidth) > 64:
		print "Check bit error"
		return
	# Third check bit should be 1
	if getSampleAverage(samples, checkBitOffset + 2 * bitWidth, checkBitOffset + 3 * bitWidth) < 64:
		print "Check bit error"
		return

	# Fill the data bit array
	dataBitOffset = checkBitOffset + 3 * bitWidth
	for i in range(16):
		if(getSampleAverage(samples, dataBitOffset + i * bitWidth, dataBitOffset + (i + 1) * bitWidth) < 64 ):
			dataBits.append(0)
		else:
			dataBits.append(1)

	# Check parity bits (8th and 16th)
	if sum(dataBits[0:7]) % 2 == dataBits[7]:
		print "Parity bit error"
		return
	if sum(dataBits[8:15]) % 2 == dataBits[15]:
		print "Parity bit error"
		return

	# Extract encoded 7 bit ASCII characters
	charABits = '0' + "".join([str(b) for b in dataBits[6::-1]])
	charBBits = '0' + "".join([str(b) for b in dataBits[14:7:-1]])
	charA = chr(int(charABits, 2))
	charB = chr(int(charBBits, 2))

	return charA + charB



def getSampleAverage(samples,start,end):
	count = end - start
	runningTotal = 0
	for i in range(count):
		runningTotal = runningTotal + samples[start + i]
	return runningTotal / count
		

if __name__ == "__main__":
	# Read the samples file
	# Samples are analog luma value from line 21 of the overscan area of a NTSC video frame and range from 0 to 128
	# Samples start with horizontal sync and color burst but we don't care about those
	# Then 7 pulse sin wave to get sync period
	# Following bits will be length of the sync wave period
	# Then 3 check bits 0, 0, 1
	# Then 16 bits, 2 7-bit characters and their parity bits
	samples = list(map(int, filter(None, open('samples.txt', 'r').read().split(" "))))
	
	# Draw the samples?
	if True:
		import turtle
		turtle.pu()
		turtle.goto(0-len(samples)/2, 0)
		turtle.pd()
		for sampleNumber in range(len(samples)):
			sample = samples[sampleNumber]
			turtle.goto(sampleNumber-len(samples)/2, sample)

	# The included sample line is the letters 't' and 'a'
	print decode608(samples)
