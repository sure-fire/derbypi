# DerbyPi

The DerbyPi is a Python-based, RasPi thumbdrive wiper running under Raspian Linux.  Perhaps more importantly, it is written in a modular fashion so as to allow anyone to create their own plugin in Python.  The end goal is to create an environment where we can centralize all those nifty edge uses for the RasPi.

Current modules include:
  - **Wipe**: Zeroize a USB device with a one-pass wipe
  - **Clone**: Duplicate one USB device to another via a byte-for-byte copy
  - **Settings**: See your IP address, Enable/disable SSH, Reset the 'pi' user's password, and initiate an adhoc WiFi access point
  - **Shutdown**: Power off the RasPi politely

To create your own module:
  - Make a subfolder under the "modules" folder.  The name of the folder will be what appears on the menu.
  - Create "main.py" in the subfolder.  Feel free to add any other files you'll need.
  - Define init() in your file, which will be called when the user selects your module from the menu.

Check out some of the existing module code for examples on how to interface with the LCD and to perform logging, using the following functions:
  - core.log(message)
  - core.error(message)
  - lcd.setCharacter(row, column, character)
  - lcd.setTitle(string)
  - lcd.setContent(string)
  - lcd.clear([color])
  - lcd.waitForButton([mask])
  - lcd.showError(string)
  - lcd.showMessage(string,delay,color)
  - lcd.menu(title,options,functions)
