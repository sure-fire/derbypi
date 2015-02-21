#!/usr/bin/python
# Copyright (c) 2015 Aaron Soto
#   Released under the MIT license
#   Incorporates libraries from AdaFruit, also released under the MIT license

import lcd
import subprocess		# Used by ip, settings, and password
import random			# Used by password

def init():
	lcd.menu("SETTINGS",['IP Address','SSH Server','Reset Password','Setup Wifi'],(settings_ip,settings_ssh,settings_password,settings_wifi))

def settings_ip():
	lcd.clear()
	lcd.setTitle("IP ADDRESS")
	
	p = subprocess.Popen(["/sbin/ifconfig","-s"],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	p.wait()
	
	ifaces = []
	
	try:
		for line in p.stdout.readlines():
			if line.startswith("Iface") or line.startswith("lo"): continue
			else:
				iface_name = line.split()[0].strip()
				ifaces.append(iface_name)
	except:
		pass
		
	for iface in ifaces:
		p = subprocess.Popen(["/sbin/ifconfig",iface], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		p.wait()
	
		ip = "NONE (via DHCP)"
		try:
			for line in p.stdout.readlines():
				if line.startswith("          inet addr:"):
					line = line[20:]
					line = line.split(" ")
					ip = line[0]
		except:
			ip = "ERROR!"
	
		lcd.clear()
		lcd.setTitle("IP ADDRESS:" + iface)
		lcd.setContent(ip)
		lcd.waitForButton()
	return

def settings_ssh():
	while True:
		lcd.clear()
		lcd.setTitle("SSH SERVER")
		
		# Use the process list to determine if SSH is actually running
		p = subprocess.Popen(["/bin/ps","-ef"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		p.wait()
		
		sshRunning = False
		if "/usr/sbin/sshd" in p.stdout.read():
			sshRunning = True
		
		if sshRunning:
			lcd.setContent("ENABLED")
		else:
			lcd.setContent("DISABLED")
		
		button = lcd.waitForButton()
		
		# User pressed UP/DOWN to change the SSH state
		if button==lcd.UP or button==lcd.DOWN:
			lcd.clear()
			lcd.setTitle("SSH SERVER")
			
			if sshRunning:
				lcd.setContent("STOPPING...")
				newState = "stop"
			else:
				lcd.setContent("STARTING...")
				newState = "restart"
			
			p = subprocess.Popen(["/usr/sbin/service","ssh",newState], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			retval = p.wait()
			
		else:  #button==LEFT or button==RIGHT or button==SELECT
			return
		
	return
	
def settings_password():
	lcd.clear()
	lcd.setTitle("RESET PASSWORD")
	lcd.setContent("User: pi")

	newPass = ""
	for x in range(8):
		newPass += chr(random.randint(65,90))
	
	lcd.waitForButton()
	
	lcd.clear()
	lcd.setTitle("RESET PASSWORD")
	lcd.setContent("Pass: " + newPass)
	
	# USE CHPASSWD TO RESET THE PASSWORD FOR THE 'PI' USER
	p = subprocess.Popen(["/usr/sbin/chpasswd"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	p.communicate(input="pi:"+newPass+"\n")

	lcd.waitForButton()
	return
	
def settings_wifi():
	lcd.clear()
	lcd.setTitle("SETUP WIFI")
	
	wifi_ssid = "DerbyPi"
	for x in range(3):
		wifi_ssid += chr(random.randint(48,57))

	wifi_key = ""
	for x in range(8):
		wifi_key += chr(random.randint(65,90))
	
	print "Setup SSID (",wifi_ssid,") with key",wifi_key

	hostapd_conf = ""
	hostapd_conf +=   "interface=wlan0"
	hostapd_conf += "\ndriver=rtl871xdrv"
	hostapd_conf += "\nssid=" + wifi_ssid
	hostapd_conf += "\nhw_mode=g"
	hostapd_conf += "\nchannel=11"
	hostapd_conf += "\nmacaddr_acl=0"
	hostapd_conf += "\nauth_algs=1"
	hostapd_conf += "\nignore_broadcast_ssid=0"
	hostapd_conf += "\nwpa=2"
	hostapd_conf += "\nwpa_passphrase=" + wifi_key
	hostapd_conf += "\nwpa_key_mgmt=WPA-PSK"
	hostapd_conf += "\nwpa_pairwise=TKIP"
	hostapd_conf += "\nrsn_pairwise=CCMP\n"

	print hostapd_conf

	hostapd = open('hostapd.conf', 'w')
	hostapd.write(hostapd_conf)
	hostapd.close()

	print "Configuring interface..."
	p = subprocess.Popen(["/sbin/ifconfig","wlan0","192.168.42.1","255.255.255.0"],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	p.wait()

	print "Starting DHCP..."
	p = subprocess.Popen(["/etc/init.d/isc-dhcp-server","restart"],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	p.wait()

	print "Configuring access point..."
	p = subprocess.Popen(["/home/pi/wiper/hostapd","-B","hostapd.conf"],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	p.wait()

	time.sleep(5)
	print p.stdout.read()

	print "Configured."
	lcd.clear()
	lcd.message("SSID: ")
	lcd.message(wifi_ssid)
	lcd.message("\n KEY: ")
	lcd.message(wifi_key)
	pause()

	return