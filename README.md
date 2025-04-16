# Freezermonitor
########################################################################
#	     This script was written by E. Bentz: ejb345@cornell.edu         #
########################################################################
 
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or any
 later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 Author: Ehren Bentz
 Project: Freezermonitor
 License: GNU General Public License v3.0

 Purpose:
 This script will monitor temperatures and upload them to a web dashboard using Initial State.
 If temperatures exceed user specified thresholds it will send warning emails to specified addresses.


 freezermonitor.py is intended to be run on a Raspberry Pi (or equvalent SBC) with internet connection
 and an installed MAX31865 circuit board with an attached platinum RTD temperature sensor.

 Configuration requires installation of Adafruit Blinka and adafruit-circuitpython-max31865
 Hardware, software, and basic tutorials for these components may be found at: https://www.adafruit.com/

 Settings for temperature thresholds, network and email parameters, Initialstate settings etc. are configured by editing the file "config.ini"
 config.ini must be properly formatted and located in the same directory as freezermonitor.py

 copy SETUP_freezermonitor to home directory (~/ or /home/USERNAME)

 Run the following in order:
mv ~/SETUP_freezermonitor/freezermonitor.py config.ini ~/
sudo apt-get install python3-pip -y

 NOTE: Raspberry pi OS versions based on Debian 13 "Bookworm" do not allow installing packages natively with pip3 by default.
 If you encounter "error: externally-managed-environment", run the following line before installing with pip3
        sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED #<- replace python3.11 with current version if a later version of python3 is installed

This solution is currently safe when installing Freezermonitor on Bookworm, but future updates will set this up in a virtual environment instead.

Continue installation of python packages:
sudo pip3 install --upgrade setuptools
sudo pip3 install --upgrade adafruit-python-shell
sudo pip3 install adafruit-circuitpython-max31865
sudo pip3 install netifaces
sudo pip3 install ISStreamer
sudo python ~/SETUP_freezermonitor/raspi-blinka.py
    -> When promted with 'Would you like a login shell to be acessible over serial?' select 'No'-> Enter (THis will take a while to run on slower  devices like a raspberry pi Zero W)
After reboot run the following to test installation:
Each process should run without errors
sudo python ~/SETUP_freezermonitor/blinkatest.py
sudo python ~/SETUP_freezermonitor/print_ip.py
sudo python ~/SETUP_freezermonitor/test_sensor.py

Edit the config.ini file to set all of the runtime options:
There are many parameters to set here. The "CUSTOM" messages may be left blank, but ALL others must have a value.
For testing purposes, enter rational values for alarm thresholds. The default values are configured for a -80 degree Celsius freezer, this will immediately send alarm emails at room temperture.

sudo nano ~/config.ini
    -> edit paramters
    -> press ctl+o to save after edits

Edit the .service file with the correct username and run directory
sudo nano ~/SETUP_freezermonitor/freezermonitor.service
     -> /home/USERNAME and /home/USERNAME/freezermonitor.py # <- change USERNAME to match the username you configured while installing the OS (The default user is "pi")
     -> press ctl+o to save after edits

Finally run:
sudo cp ~/SETUP_freezermonitor/freezermonitor.service /etc/systemd/system/
sudo systemctl enable freezermonitor.service
sudo reboot

Attach the device to the outside of your freezer.
Feed the RTD probe inside and place in an appropraite location.
NOTE: Platinum RTD sensors are extremely sensitive. It may be useful to place the sensor in a jar of sand or other material to slow its reposnse time slightly. Without this, it is very easy to trigger an alarm by opening the door.
Plug in the device
Wait for temperatures to equilibrate
Use the IP address to ssh into the pi and reconfigure temperature thresholds in the config.ini file to meet your requirements
Finally run:
sudo systemctl restart freezermonitor.service

You're all done!
