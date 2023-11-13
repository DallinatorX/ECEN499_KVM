"""
This is the core file for the KVM. Running this will start all needed function.
"""
# from Programs.rtsp_v2 import *
from Programs.getkeyboardinput import *
from Programs.getMouseInput import *
import threading



if __name__ == '__main__':
    serial_input = serial.Serial("/dev/ttyACM0",115200)

    # Create threads for each function
    keyboard_thread = threading.Thread(target=start_keyboard_input, args=(serial_input,))
    mouse_thread = threading.Thread(target=start_mouse_input, args=(serial_input,))
    # rtsp_thread = threading.Thread(target=start_rtsp)

    # Start the threads
    keyboard_thread.start()
    mouse_thread.start()
    # rtsp_thread.start()

    # Wait for all threads to finish (if needed)
    keyboard_thread.join()
    mouse_thread.join()
    # rtsp_thread.join()



    # p1 = Process(target=start_keyboard_input)
    # p1.start()
    # p2 = Process(target=start_mouse_input)
    # p2.start()
    # # p3 = Process(target=start_rtsp)
    # # p3.start()
    # p1.join()
    # p2.join()
    # # p3.join()

    # start_keyboard_input(serial_input)
    # start_mouse_input(serial_input)
    # start_rtsp()
