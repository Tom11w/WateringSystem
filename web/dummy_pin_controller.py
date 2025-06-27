PINLIST = {11, 12, 13, 15, 16, 18, 22, 24}

watering_when_GPIO_high = False
# Controlls if active High or if active Low
# e.g if true, the Pin will be set high during watering.


if watering_when_GPIO_high:
    active_pin_state = "HIGH"
    inactive_pin_state = "LOW"
else:
    inactive_pin_state = "HIGH"
    active_pin_state = "LOW"


def enable_all_lines():
    for pin in PINLIST:
        enable_line(pin)


def deactivate_all_lines():
    for every_pin in PINLIST:
        deactivate_line(every_pin)


def enable_line(pin: int):
    if pin not in PINLIST:
        print(f"Error can't enable pin {pin} not in the pin list")
        return
    print(f"Setting up {pin=} as out, inital state = {inactive_pin_state=}")
    print(f"GPIO pin {pin} intitalised")


def activate_line(pin: int):
    if pin not in PINLIST:
        print(f"Error can't activate pin {pin}. not in the pin list")
        return
    for every_pin in PINLIST:
        deactivate_line(every_pin)
    #  GPIO.output(pin, active_pin_state)  # Turn on
    print(f"Activating line on {pin=}, new pin state = {active_pin_state=}")
    print(f"GPIO pin {pin} set line active")


def deactivate_line(pin: int):
    if pin not in PINLIST:
        print(f"Error can't deactivate pin {pin}. not in the pin list")
        return
    #  GPIO.output(pin, inactive_pin_state)  # Turn off
    print(f"Deactivating line on {pin=}, new pin state {inactive_pin_state=}")
    print(f"GPIO pin {pin} set line inactive")
