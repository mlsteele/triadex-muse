# Python and pyo implementation of the Triadex Muse
# Logic from descriptions by Lenny Foner (http://bella.media.mit.edu/people/foner/) and Paul Geffen (http://trovar.com/index.html)
# Trovar description here: http://web.archive.org/web/20011118181946/http://richter.simplenet.com/muse/musespec.html
# With guidance from Donald Derek Haddad (https://donaldderek.com/)


"""
TO OPERATE:
Change variables under "Use-operated variables" near the bottom of the program
"Interval" (A-D) sliders choose the next note
"Theme" (W-Z) sliders input into a shift register
(Both sets of "sliders" pull values from one of two counters or the shift register)
"pitch" can be set to any tonic
"bpm" can be set to any tempo in beats per minute
"""

import random
import time
from pyo import *

# defining classes

class Clock:
	def __init__(self):
		# intializes as variable with value 0
		self.val = 0

	def __str__(self):
		# prints as current value
		return str(self.val)

	def pulse(self):
		self.val += 1

	def reset(self):
		self.val = 0

timer = Clock()

class Stack:
	# use in Muse: create with 31 bits

	def __init__(self,length):
		# initializes as random 0s and 1s, to specified length
		self.length = length
		self.items = [random.randint(0,1) for i in range(self.length)]

	def __str__(self):
		# prints as a list
		return str(self.items)

	def pulse(self,item):
		# effectively shifts everything down one place
		# add new value at the beginning 
		self.items.insert(0,item)
		# remove and return last item
		self.items.pop()

class BinaryCounter:
	# use in Muse: create with five bits

	def __init__(self,length,clock=timer):
		# initializes as a list of all 0s, to specified length
		self.length = length
		self.digits = [0 for i in range(length)]
		self.clock = clock

	def __str__(self):
		# prints as a list
		return str(self.digits)

	def pulse(self):
		length = self.length # for convenience

		def switch(digit):
			# switch a digit fom 0 to 1 or vice versa
			if digit == 0:
				return 1
			else:
				return 0

		# reset if everything is 1
		if sum(self.digits) == length:
			# reset to all 0s
			self.digits = [0 for i in range(length)]
		else:
			# if not resetting, count up one...
			for location in range(len(self.digits)):
				if self.clock.val % (2**location) == 0:
					self.digits[location] = switch(self.digits[location])
				else:
					pass

class TripleCounter:
	# use in Muse: create with two bits

	def __init__(self,length,clock=timer):
		# initializes as a list of all 0s, to specified length
		self.length = length
		self.digits = [0 for i in range(length)]
		self.clock = clock


	def __str__(self):
		# prints as a list
		return str(self.digits)

	def pulse(self):
		length = self.length # for convenienve

		def switch(digit):
			# switch a digit fom 0 to 1 or vice versa
			if digit == 0:
				return 1
			else:
				return 0

		# now the main activity of the function
		# reset if everything is 1
		for location in range(len(self.digits)):
			if self.clock.val % (3*(location+1)) == 0:
				self.digits[location] = switch(self.digits[location])
			else:
				pass

# creating shift register and binary counter

shiftRegister = Stack(31)
counter1 = BinaryCounter(5)
counter2 = TripleCounter(2)


class Slider:
	# use in Muse: create 'A','B','C','D' (interval),'W','X','Y','Z' (theme) sliders

	def __init__(self,
				val=0,
				binaryCounter=counter1,
				tripleCounter=counter2,
				stack=shiftRegister):
		# initializes as a variable set to 0, i.e. "off"
		# binaryCounter and stack are what the sliders will pull values from
		self.val = val
		self.binaryCounter = binaryCounter
		self.tripleCounter = tripleCounter
		self.stack = stack

	def __str__(self):
		# prints as integer
		return str(self.val)	

	def output(self):
		outputList = [0,1] # off, on
		# append the counters and shift register to create one big list to pull from
		for i in self.binaryCounter.digits:
			outputList.append(i)
		for i in self.tripleCounter.digits:
			outputList.append(i)
		for i in self.stack.items:
			outputList.append(i)
		# pull from list
		return outputList[self.val]

def parityGen(inputList):
	# inputList should be a binary, a list of the values of W through Z sliders
	# parityGen outputs 0 for an even sum and 1 for an odd sum
	summedOuts = sum(inputList)
	output = summedOuts %2
	return output

def getNoteNum(inputList):
	# inputList should be binary, a list of the values of A through D sliders
	# getNote outputs how many notes above the tonic the output note is
	num,exponent = 0,0
	for i in inputList:
		num += i * (2 ** exponent)
		exponent += 1
	return num

def getNoteFrequency(key,noteNum):
	# key = tonic frequency, noteNum = placement in scale (e.g. 0 = tonic, 1 = whole step up)
	# progression of half tone increases in a major scale
	halfTones = [0,2,4,5,7,9,11,12,14,16,17,19,21,23,24,24]
	# convert placement in scale to Hz
	frequency = key * (1.05946882217 ** halfTones[noteNum])
	return frequency

# creating interval and theme sliders, setting initial key

A = Slider()
B = Slider()
C = Slider()
D = Slider()
W = Slider()
X = Slider()
Y = Slider()
Z = Slider()

allSliders = [A,B,C,D,W,X,Y,Z]
pitch = 261.6

# a big function that pulses everything (clock, counters, shift register) "forwards" in time and returns a note

def pulseAll(key=pitch,
			sliderList=allSliders,
			stack=shiftRegister,
			clock=timer,
			binaryCounter=counter1,
			tripleCounter=counter2):
	# sliderList is list of sliders: first four interval, last four theme
	# call all slider values
	sliderVals = []
	for slider in sliderList:
		sliderVals.append(slider.output())
	# pulse all forward
	clock.pulse()
	counter1.pulse()
	counter2.pulse()
	parityIn = [sliderVals[i+4] for i in range(4)]
	parityOut = parityGen(parityIn)
	stack.pulse(parityOut)
	# get note, return in Hz
	noteNum = getNoteNum([sliderVals[i] for i in range(4)])
	noteFrequency = getNoteFrequency(key,noteNum)
	print noteNum
	return noteFrequency

""" User-operated variables """

# interval sliders 
A.val = 17
B.val = 17
C.val = 18
D.val = 19

# theme sliders
W.val = 4
X.val = 19
Y.val = 8
Z.val = 25

# key: middle C = 261.6
pitch = 200

# tempo in beats per minute
bpm = 240

""" End of user-operated variables """

# sound

seconds = 60.0/bpm

s = Server().boot() # booting pyo server
s.start()

while True:
	note = Sine(freq=pulseAll(pitch),mul=0.05).out()
	time.sleep(seconds)




