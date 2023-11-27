from pynput.keyboard import Key, Listener
from libraries.sendKeyboardMouse import *
import serial


# Keep track of keys that are currently held down
current_keys = set()

# Define functions for keypress and key release events

# On Key Press
def on_press(key, serial_input):
    if key not in current_keys:
        current_keys.add(key)
        
        # Remove "Key." prefix and single quotes, if present
        key_str = str(key).replace("Key.", "").strip("'")
        
        if verbose:
            print(f"Key {key_str} pressed")
        
        sendKeyboardMouseAction('keydown',key_str,0,0,serial_input)

# On key release
def on_release(key, serial_input):
    if key in current_keys:
        current_keys.remove(key)

        # Remove "Key." prefix and single quotes, if present
        key_str = str(key).replace("Key.", "").strip("'")
        if verbose:
            print(f"Key {key_str} released")
        sendKeyboardMouseAction('keyup',key_str,0,0,serial_input)
        

# Create keyboard listeners
def start_keyboard_input(serial_input):
    stop_flag = False  # Flag to signal listener to stop

    def on_press_wrapper(key):
        nonlocal stop_flag
        if stop_flag:
            return False  # Stop the listener
        return on_press(key, serial_input)

    def on_release_wrapper(key):
        nonlocal stop_flag
        if stop_flag:
            return False  # Stop the listener
        return on_release(key, serial_input)

    with Listener(on_press=on_press_wrapper, on_release=on_release_wrapper) as listener:
        listener.join()
