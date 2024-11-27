#!/usr/bin/env python3
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import sys
# My debugging system  D (for debug) = True or False
D = True
if D: print("led_select.py - Debug mode")
#
p = int(sys.argv[1])
mode = sys.argv[2]
if D: print("arguments:", p, mode)
#
PINLIST = {11,12,13,15,16,18,22,24}
if (p not in PINLIST):
    print("Error: Wrong pin")
    exit(1)
#
## Set up pins for output. NB: FOR THE 8 RELAY BOARD OUTPUT IS INVERTED!
GPIO.setwarnings(False) # Not sure what these annoying warnings do
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
if D: print("GPIO  numbering system intitalised")
#
# Set pins to be an output and set initial value to High! (off)
for i in PINLIST:
    GPIO.setup(i, GPIO.OUT, initial=GPIO.HIGH) 
    if D: print("Pin " + str(i) + " set to OUT and off")
if (mode == "on"):
    GPIO.output(p, GPIO.LOW) # Turn on
    if D: print("Pin " + str(p) + " set to on ")
print("Status: ", p, mode)