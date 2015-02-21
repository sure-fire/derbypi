#!/usr/bin/python
# Copyright (c) 2015 Aaron Soto
#   Released under the MIT license
#   Incorporates libraries from AdaFruit, also released under the MIT license

# TODO (BUG): On Raspian, the link keeps coming up on it's own.  Disabling ifplugd doesn't stop it.  I'm stumped.
#                     -- sure-fire, 2015-02-21

import lcd
import core
import sys
import time
import subprocess

def init():
	lcd.clear()
	lcd.setTitle("LINK TESTER")
	lcd.setContent("Hold LEFT to cancel")
	
	time.sleep(2)

	#core.log("LINK TESTER: Stopping ifplugd")
	#p = subprocess.Popen(["/usr/sbin/service","ifplugd","stop"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#p.wait()

	state = "up"
	while True:
		if state == "down":
			state = "up"
			time.sleep(0.7)	# It takes an avaerage of 0.7 seconds longer to bring the link up.  I'm just trying to even things out.
		else:
			state = "down"
		
		core.log("LINK TESTER: GOING " + state)
		p = subprocess.Popen(["/sbin/if" + state,"eth0",state],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		p.wait()
		
		if state == "down": lcd.clear(lcd.RED)
		else: lcd.clear(lcd.GREEN)
		lcd.setTitle("LINK TESTER")
		lcd.setContent(state)
		
		time.sleep(2)
		
		if lcd.checkForButton() > 0:
			core.log("LINK TESTER: USER CANCELLED")
			core.log("LINK TESTER: GOING UP")
			p = subprocess.Popen(["/sbin/ifup","eth0"],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			p.wait()
			
			#core.log("LINK TESTER: Starting ifplugd")
			#p = subprocess.Popen(["/usr/sbin/service","ifplugd","start"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			#p.wait()

			return