"""
This will run the command to either kill or turn on the computer
"""


def click_power_button(serial_input):
    """
    #Clicks the power button for .5 seconds
    """
    data_hex = "\x05" + "p"
    serial_input.write(data_hex.encode())


def hold_power_button(serial_input):
    """
    Hold the power button for 10 seconds
    """
    data_hex = "\x05" + "k"
    serial_input.write(data_hex.encode())
