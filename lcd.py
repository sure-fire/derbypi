#!/usr/bin/python
# Copyright (c) 2015 Aaron Soto
#   Released under the MIT license
#   Incorporates libraries from AdaFruit, also released under the MIT license

import Adafruit_CharLCDPlate	# to interface with the Adafruit i2c 16x2 RGB LCD Pi Plate
import os						# to check UID for root
import sys						# to exit with error status code
import time						# to sleep while waiting for user action (i.e. awaiting button press)
import core

SELECT                  = 1
RIGHT                   = 2
DOWN                    = 4
UP                      = 8
LEFT                    = 16
ANY						= 255

OFF                     = 0x00
RED                     = 0x01
GREEN                   = 0x02
BLUE                    = 0x04
YELLOW                  = RED + GREEN
TEAL                    = GREEN + BLUE
VIOLET                  = RED + BLUE
WHITE                   = RED + GREEN + BLUE
ON                      = RED + GREEN + BLUE

currentColor = ON
currentText = ['                ','                ']
charLCD = None

def setColor(color):
	charlcd.backlight(color)
	currentColor = color

def setCharacter(row,col,char):
	currentText[row] = currentText[row][:col] + char[0] + currentText[row][col:]
	output()
	
def setString(row,col,string):
	currentText[row] = currentText[row][:col] + string
	output()
	
def setTitle(string):
	currentText[0] = string
	output()

def setContent(string):
	currentText[1] = " " + string
	output()

def showError(string,redraw=True):
	clear()
	charlcd.backlight(RED)
	charlcd.message("ERROR\n")
	charlcd.message(" " + string)
	if redraw:
		waitForButton()
		output()

def showMessage(string,length=2,color=None):
	# Wipe screen and fill with provided message and color
	clear()
	if color:
		charlcd.backlight(color)
	charlcd.message(string)
	time.sleep(length)

	# Reset to previous screen
	if color:
		charlcd.backlight(currentColor)
	clear()
	output()

def off():
	charlcd.clear()
	setColor(OFF)

def clear(color=None):
	# Wipes the screen and resets the color, but doesn't touch currentText
	global currentColor
	charlcd.clear()

	charlcd.home()
	if color:
		setColor(color)
	elif currentColor:
		setColor(currentColor)

def redraw():
	output()
		
def output():
	clear()
	charlcd.message(currentText[0])
	charlcd.message("\n")
	charlcd.message(currentText[1])

def waitForButton(maskList=ANY):
	# Delay to wait for the user to release the previous button.
	while charlcd.buttons() != 0:
		time.sleep(0.05)
	
	# Excellent.  Now, let's just wait for someone to push a button.
	currentButton = 0
	while True:
		time.sleep(0.05)
		currentButton = charlcd.buttons()
		if currentButton > 0:
			if maskList == ANY: return currentButton
			try:
				if currentButton in maskList:
					return currentButton
			except TypeError:
				if currentButton == maskList:
					return currentButton
				else:
					# USER PRESSED THE WRONG BUTTON.  Keep waiting
					pass

def checkForButton(maskList=ANY):
	return (charlcd.buttons() & maskList)

def menu(title, options, funcs=None):
	optionNumber = 0
	clear()
	if funcs==None:
		# This is the main menu.
		main=True
	else :
		# This is a submenu.
		main=False

		options.append("<- BACK")
	
	while True:
		setTitle(title)
		setContent(options[optionNumber])
		button = waitForButton((ANY))
		if button == DOWN:
			if optionNumber < len(options)-1: optionNumber += 1
		if button == UP:
			if optionNumber > 0: optionNumber -= 1
		if button == LEFT and not main:
			return
		if button == RIGHT or button == SELECT:
			if main:
				core.module_run(options[optionNumber])
			elif not main and optionNumber == len(options)-1:
				return
			else:
				funcs[optionNumber]()

if os.getuid() != 0:
	print "MUST RUN AS ROOT!"
	sys.exit(-1)
charlcd = Adafruit_CharLCDPlate.Adafruit_CharLCDPlate()