#!/usr/bin/python
# Copyright (c) 2015 Aaron Soto
#   Released under the MIT license
#   Incorporates libraries from AdaFruit, also released under the MIT license

import lcd
import core
import sys
import time

def shutdown():
	core.log("Shutting down")
	lcd.clear()
	lcd.setTitle("SHUTTING DOWN...")
	time.sleep(1)
	p = subprocess.Popen(["/sbin/halt","-f","-h"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	sys.exit(0)