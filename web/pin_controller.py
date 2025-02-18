import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library

debug = True

PINLIST = {11, 12, 13, 15, 16, 18, 22, 24}

watering_when_GPIO_high = False
# Controlls if active High or if active Low
# e.g if true, the Pin will be set high during watering.

# Set up pins for output. NB: FOR THE 8 RELAY BOARD OUTPUT IS INVERTED!
GPIO.setwarnings(False)  # Not sure what these annoying warnings do
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering


if watering_when_GPIO_high:
    active_pin_state = GPIO.HIGH
    inactive_pin_state = GPIO.LOW
else:
    inactive_pin_state = GPIO.HIGH
    active_pin_state = GPIO.LOW


def enable_line(pin: int):
    if pin not in PINLIST:
        print(f"Error can't enable pin {pin} not in the pin list")
        return
    GPIO.setup(pin, GPIO.OUT, initial=inactive_pin_state)
    if debug:
        print(f"GPIO pin {pin} intitalised")


def activate_line(pin: int):
    if pin not in PINLIST:
        print(f"Error can't activate pin {pin}. not in the pin list")
        return
    for every_pin in PINLIST:
        deactivate_line(every_pin)
    GPIO.output(pin, active_pin_state)  # Turn on
    if debug:
        print(f"GPIO pin {pin} set line active")


def deactivate_line(pin: int):
    if pin not in PINLIST:
        print(f"Error can't deactivate pin {pin}. not in the pin list")
        return
    GPIO.output(pin, inactive_pin_state)  # Turn off
    if debug:
        print(f"GPIO pin {pin} set line inactive")
