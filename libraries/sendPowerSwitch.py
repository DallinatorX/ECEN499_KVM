"""
This will run the command to either kill or turn on the computer
"""


def click_power_button(serial_input):
    """
    #Clicks the power button for .5 seconds
    """
    data_hex = "\x05" + chr(1)
    serial_input.write(data_hex.encode())


def hold_power_button(serial_input):
    """
    Hold the power button for 10 seconds
    """
    data_hex = "\x05" + chr(2)
    serial_input.write(data_hex.encode())
