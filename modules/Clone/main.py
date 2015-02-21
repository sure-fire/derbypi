#!/usr/bin/python
# Copyright (c) 2015 Aaron Soto
#   Released under the MIT license
#   Incorporates libraries from AdaFruit, also released under the MIT license

import core
import lcd
import subprocess
import time
import os

device_blacklist = ['/dev/mmcblk0']

def calcSizeInGB(bytes):
	bytes = int(bytes)
	gb = bytes/1073741824.0
	return str(round(gb,1))

def runDD(inParam,outParam,outDisk):
	core.log("Running DD from " + inParam + " to " + outParam + "(" + str(outDisk))
	bytesTotal = float(outDisk['size'])

	p = subprocess.Popen(["/bin/dd","conv=sync,noerror",inParam,outParam], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	time.sleep(0.25)
	
	while p.poll() == None:
		subprocess.call(["/bin/kill", "-USR1",str(p.pid)])
		time.sleep(0.25)
		p.stdout.flush()
				
		line = p.stdout.readline()	# DISCARD THIS LINE ("records in")
		line = p.stdout.readline()	# DISCARD THIS LINE ("records out")
		line = p.stdout.readline()	# KEEP THIS LINE ("XXXXXXXXX bytes (XXX kB) copied, XX.XXXXX s, X.X MB/s"
		
		if line and bytesTotal:
			try:
				bytesCopied = float(line.split(" ")[0])
				percent = (bytesCopied / bytesTotal) * 100.0
				bars = int( round(percent,0) / 10 )
				core.log("STATUS: " + str(bytesCopied) + " / " + str(bytesTotal) + " (" + str(percent) + " = " + str(bars) + "/10)")
				bar = "   ["
				bar += "\xFF"*bars
				bar += " "*(10-bars)
				bar += "]"
			
			except:
				# WE JUST CAUGHT THE DD SUMMARY OUTPUT.  THIS HAPPENS WHEN DD IS FINISHED.
				if "records out" in line:
					bytesCopied = bytesTotal
				
				# UNHANDLED EXCEPTION?  LET'S GET MORE INFO.
				else:
					core.log("UNKNOWN BYTE COUNTER")
					core.log(line)
					bar=""
					raise
		
		else: # This happens (about 1/40 times) when we can't get the size of the device.
			bar = "IN PROGRESS  "
			# Sorry.
		
		lcd.setContent(bar)
		
		# IF THE USER PRESSES THE LEFT BUTTON, ABORT!
		if lcd.checkForButton(lcd.LEFT) == lcd.LEFT:
			core.log("ABORT!")
			subprocess.call(["/bin/kill", "-9",str(p.pid)])
		
		subprocess.call(["/bin/sync"])

	core.log("DD RETURNED " + str(p.returncode))
	if p.returncode == 1:
		lcd.clear(lcd.GREEN)
		lcd.setContent("DONE!")
	elif p.returncode == -9:
		lcd.clear(lcd.BLUE)
		lcd.setContent("ABORTED!")
	else:
		lcd.clear(lcd.YELLOW)
		lcd.setContent("FAILED!")
		
	return p

def init():
	lcd.clear()
	lcd.setTitle("CLONE")
	lcd.setContent("SCANNING...")
	
	disks = scanDisk()
	if disks == None:
		return
	
	selection = 0
	while True:
		disk = disks[selection]
		bytes = int(disk['size'])
		size = calcSizeInGB(disk['size'])
		dev = disk['dev'][5:]
		
		lcd.clear()
		lcd.setTitle("CLONE SOURCE\n  ")
		lcd.setContent(dev + " (" + size + "G" + ")")		# PRINT DEVICE / SIZE
		
		# WAIT FOR NEW USER INPUT
		button = lcd.waitForButton()
		
		if button==lcd.DOWN:
			if selection < len(disks)-1: selection += 1
		
		if button==lcd.UP:
			if selection > 0: selection -= 1
		
		if button==lcd.LEFT:
			return
		
		if button==lcd.RIGHT or button==lcd.SELECT:
			inParam = "if="+disk['dev']
			
			while True:
				disk = disks[selection]
				size = calcSizeInGB(disk['size'])
				dev = disk['dev'][5:]
				
				lcd.clear(lcd.YELLOW)
				lcd.setTitle("CLONE DEST\n  ")
				lcd.setContent(dev + " (" + size + "G)")		# PRINT DEVICE / SIZE
				
				# WAIT FOR NEW USER INPUT
				button = lcd.waitForButton()
				
				if button==lcd.DOWN:
					if selection < len(disks)-1: selection += 1
				
				if button==lcd.UP:
					if selection > 0: selection -= 1
				
				if button==lcd.LEFT:
					return
				
				if button==lcd.RIGHT or button==lcd.SELECT:
					lcd.clear(lcd.RED)
					lcd.setTitle("IMAGING "+dev+"...\n")
					lcd.setContent("   [          ]")
					
					outParam = "of="+disk['dev']
					
					p = runDD(inParam,outParam,disk)
										
					lcd.clear(lcd.GREEN)
					lcd.waitForButton()
					return

def findDiskSize(dev):
	fd = os.open(dev, os.O_RDONLY)
	
	# SEEK TO THE END OF THE DEVICE AND RECORD THE CURSOR LOCATION (IN BYTES)
	try: size = long(os.lseek(fd, 0, os.SEEK_END))
	except:
		# TODO: FIGURE OUT WHY 1/100 TIMES, THE DEVICE ISN'T SEEKABLE.
		#   IF YOU CAN FIGURE THIS OUT, SERIOUSLY...
		#   I WILL BUY YOU A DRINK.  EMAIL asoto@telecomsys.com.
		size = 0
		core.log("UNABLE TO READ SIZE OF " + dev)
	finally:
		os.close(fd)
	
	return size
	
def scanDisk():
	global debug
	# CHECK FOR A LIST OF DRIVES
	#   IF NO DRIVES ARE FOUND -- WAIT UNTIL SOMEONE PLUGS IT IN
	#   ALTERNATIVELY, THE USER PRESSES THE LEFT BUTTON TO ABORT.
	
	disks=[]
	
	while disks == []:
		core.log("SCANNING FOR DISKS")
		# USE "parted -l -m" TO FIND ALL DRIVES.  UNFORTUNATELY, THIS TAKES A SECOND OR TWO.
		p = subprocess.Popen(["/sbin/parted","-l","-m"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		p.wait()
		
		# IF THE USER PRESSES THE LEFT BUTTON, ABORT!
		if lcd.checkForButton(lcd.LEFT) == lcd.LEFT:
			core.log("USER ABORTED")
			return
		
		for line in p.stdout.readlines():
			device = {}
			line = line.strip()
			if line.startswith("/dev/"):
				line = line.split(":")
				device['dev'] = "/dev/"+line[0][5:]
				
				# MAKE SURE THE DEVICE ISN'T ON THE BLACKLIST (FOR EXAMPLE, THE BOOTABLE SD CARD)
				if device['dev'] in device_blacklist: continue
				
				# DETERMINE THE SIZE OF THE DEVICE
				device['size'] = findDiskSize(device['dev'])
				
				disks.append(device)
				core.log("FOUND DISK: " + device['dev'] + "(" + str(findDiskSize(device['dev'])) + " bytes)")
			
			elif line.startswith("Error"):
				line = line.split(":")
				device['dev'] = line[1][1:]
				
				# MAKE SURE THE DEVICE ISN'T ON THE BLACKLIST (FOR EXAMPLE, THE BOOTABLE SD CARD)
				if device['dev'] in device_blacklist: continue
				
				# DETERMINE THE SIZE OF THE DEVICE
				device['size'] = findDiskSize(device['dev'])
				
				disks.append(device)
				core.log("FOUND DISK: " + device['dev'] + "(" + str(findDiskSize(device['dev'])) + " bytes)")
		
	disks.sort()
	core.log("FOUND " + str(len(disks)) + " DISKS")
	return disks