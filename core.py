#!/usr/bin/python
# Copyright (c) 2015 Aaron Soto
#   Released under the MIT license
#   Incorporates libraries from AdaFruit, also released under the MIT license

# TODO functions:
#    display_progress(percentage,[title])            - display a progress bar (0-1,1-100) / check for float
#    display_error(message,[timeout],[title])        - change backlight color, display error

import glob						# module_scan(): to find files
import imp						# module_run(): to load and run plugin modules
import traceback				# module_run(): to gather a traceback during exceptions
import lcd						# module_run(): to print fatal errors to the screen
import time						# log(): to print the epoch time in log messages
import os						# main(): to check UID for root
import sys						# main(): to exit with status code
import subprocess				# shutdown(): to call the 'halt' command

def module_scan(path):
	# Identify all modules, and sort by time modified (newest first)
	#    NOTE TO FUTURE SELF: Use "touch -m" to re-order the menu
	modules = sorted(glob.glob("modules/*/main.py"), key=os.path.getmtime)
	modules.reverse()

	moduleList = []
	for module in modules:
		log("FOUND MODULE: " + module)
		moduleList.append(module.split('/')[1])
	return moduleList

def module_run(path):
	# Accepts path as "modules/[name]/main.py", "modules/[name]/", or "[name]"
	#     where [name] is the name of the module to run.
	# Imports [name] and runs the init() function within 'modules/[name]/main.py'
	if path.find('/') > 0:
		name = path.split('/')[1]
	else: 
		name = path
		path = "./modules/" + name + "/main.py"
		
	try:
		log("LOADING MODULE: " + name + "(" + path + ")")
		module = imp.load_source(name, path)
		module.init()
	except:
		log("ERROR: SOMETHING HAPPENED IN THE " + name + " MODULE!")
		trace = traceback.format_exc()
		log(trace)
		
		err = sys.exc_info()[0]
		err = str(err).split("'")[1].split('.')[1]
		lcd.showError(err,redraw=False)
		
		sys.exit(-1)
	
def log(text):
	print str(time.time()) + ": " + text
	f = open('/var/log/wiper', 'a+')
	f.write(str(time.time()) + ": " + text + "\r\n")
	f.flush()
	f.close()

def error(text):
	log("ERROR:" + text)

if __name__=="__main__":
	if "wipe" in module_scan("."):
		module_run("modules/wipe2/main.py")