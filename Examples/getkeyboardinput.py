from pynput.keyboard import Key, Listener
import serial

# Keep track of keys that are currently held down
current_keys = set()

# Define functions for keypress and key release events
def on_press(key):
    if key not in current_keys:
        current_keys.add(key)
        # Remove "Key." prefix and single quotes, if present
        key_str = str(key).replace("Key.", "").strip("'")
        print(f"Key {key_str} pressed")

def on_release(key):
    if key in current_keys:
        current_keys.remove(key)
        # Remove "Key." prefix and single quotes, if present
        key_str = str(key).replace("Key.", "").strip("'")
        print(f"Key {key_str} released")
        

# Create keyboard listeners
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
