# Freezermonitor
########################################################################
#	     This script was written by E. Bentz: ejb345@cornell.edu         #
########################################################################
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any
# later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# Author: Ehren Bentz
# Project: Freezermonitor
# License: GNU General Public License v3.0

# Purpose:
# This script will monitor temperatures and upload them to a web dashboard using Initial State.
# If temperatures exceed user specified thresholds it will send warning emails to specified addresses.
##

# freezermonitor.py is intended to be run on a Raspberry Pi (or equvalent SBC) with internet connection
# and an installed MAX31865 circuit board with an attached platinum RTD temperature sensor.
#
# Configuration requires installation of Adafruit Blinka and adafruit-circuitpython-max31865
# Hardware, software, and basic tutorials for these components may be found at: https://www.adafruit.com/
#
# Settings for temperature thresholds, network and email parameters, Initialstate settings etc. are configured by editing the file "config.ini"
# config.ini must be properly formatted and located in the same directory as freezermonitor.py
