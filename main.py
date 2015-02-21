#!/usr/bin/python
# Copyright (c) 2015 Aaron Soto
#   Released under the MIT license
#   Incorporates libraries from AdaFruit, also released under the MIT license

import core
import lcd
import sys
import time

while True:
	try:
		lcd.clear()
		lcd.showMessage("   DerbyPi 2.0",length=1,color=lcd.GREEN)
		menuList = core.module_scan(".")
		
		lcd.menu("MAIN MENU",menuList)

	# IF THE USER PRESSES CONTROL + C
	except KeyboardInterrupt:
		core.log("USER ABORTED WITH CTRL-C")
		lcd.off()
		sys.exit(0)
	
	# IF THE PROCESS IS KILLED (USUALLY AS PART OF A NORMAL SHUTDOWN)...
	except SystemExit:
		core.log("KILLED")
		lcd.off()
		time.sleep(1.5)
		lcd.message("IT'S NOW SAFE TO\n")
		lcd.message("TURN OFF YOUR PI\n")
		sys.exit(0)
	
	# BLOCK COMMENT THE FOLLOWING LINES TO FORCE CRASHES!
	# UNHANDLED EXCEPTIONS?  WHO WROTE THIS THING ANYWAY?
	except:
		core.log("UNHANDLED FATAL ERROR")
		err = sys.exc_info()[0]
		err = str(err).split("'")[1]
		core.log(err[11:])