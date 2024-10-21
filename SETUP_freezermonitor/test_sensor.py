#! /usr/bin/python3
import board
import time
import digitalio
import adafruit_max31865

import time
import board
import digitalio
import adafruit_max31865

# Create sensor object, communicating over the board's default SPI bus
# Edit the lines below to match the installation of your sensor hardware
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
sensor = adafruit_max31865.MAX31865(spi, cs, wires=4)

# Note you can optionally provide the thermocouple RTD nominal, the reference
# resistance, and the number of wires for the sensor (2 the default, 3, or 4)
# with keyword args:
# sensor = adafruit_max31865.MAX31865(spi, cs, rtd_nominal=100, ref_resistor=430.0, wires=2)

# Main loop to print the temperature every second.
while True:
    temp = sensor.temperature
    print("Sensor Temperature: {0:0.3f}C".format(temp)+"\n\n")
    time.sleep(1.0)

