"""
This is the core file for the KVM. Running this will start all needed function.
"""
from Programs.getkeyboardinput import *
import threading
import subprocess
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
import cv2
import pygame_gui
from libraries.sendPowerSwitch import *
import time
from datetime import datetime


#Set Video device info
device = "video0"

#Set the arduino path
arduino_path = "/dev/ttyACM1"

# Turn on Verbose
verbose = False

# Set Screen size
window_width = 1920
window_height = 1080

# Mouse actions
leftMouseDown = False
rightMouseDown = False
wheelMouseDown = False

# Booleans
running = True
paused = False      # Variable to keep track of the pause state
fullscreen = False  # Variable to keep track of the fullscreen state

def yes_button():
    global answer
    answer = True
def no_button():
    global answer
    answer = False

def warning_popup():
    root = Tk()
    root.geometry("250x100")
    
    root.title("Warning Popup")
    
    btn1 = Button(root, text = 'Yes', command=lambda:[yes_button(), root.destroy()]).pack(side = 'left', padx=20)
    btn2 = Button(root, text = 'No', command=lambda:[no_button(), root.destroy()]).pack(side = 'right', padx=20)

    label = Label(root, text ="Are you sure?").pack()

    root.mainloop()
    return answer

def submit_feedback():
    feedback_text = feedback_input.get_text()
    if feedback_text:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('user_feedback.txt', 'a') as file:
            file.write(f"{timestamp}: {feedback_text}\n")
        print("Feedback submitted successfully!")
        feedback_input.hide()
        submit_button.hide()
        feedback_button.show()
        feedback_input.set_text('')

def getVideoInputDevice():
    """
    Given the video device returns the full path
    """
    frames_loc = '/dev/' + str(device)
    return frames_loc

def toggle_pause_mode():
    """
    Toggles pause-state boolean and visibility of local mouse pointer
    """
    global paused
    paused = not paused  # Toggle pause state
    if paused:
        pygame.mouse.set_visible(True)  # Show the mouse when paused
    else:
        pygame.mouse.set_visible(False) # Hide the mouse when not paused

def event_handler():
    """
    This thread handles all PyGame events 
    """
    global leftMouseDown, rightMouseDown, wheelMouseDown, running, fullscreen, paused, screen

    while running:
        for event in pygame.event.get():
            # Exit all functions if Pygame is quit
            if event.type == QUIT:
                pygame.quit()
                cap.release()

            # Start Pause menu if alt+u is pressed    
            elif event.type == KEYDOWN:
                if event.key == K_u and pygame.key.get_mods() & KMOD_ALT:
                    toggle_pause_mode() # Toggles pause state

            elif event.type == MOUSEWHEEL:
                #Record mouse scroll
                print(event.x,event.y)
                sendKeyboardMouseAction("mousescroll",0,event.x, event.y, serial_input)

            # control the GUI
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == resume_button:
                    print("Host - Resuming...")
                    toggle_pause_mode() # Toggles pause state
                
                if event.ui_element == power_button:
                    if(warning_popup()):
                        print("Host - Toggling power button...")
                        click_power_button(serial_input) # Serial to arduino to "toggle" power btn 
                
                if event.ui_element == kill_button:
                    if(warning_popup()):
                        print("Host - Forcing shutdown...")
                        hold_power_button(serial_input) # Serial to arduino to "hold" power btn   

                if event.ui_element == exit_button:
                    if(warning_popup()):
                        print("Disconnecting from Host...")
                        running = False
                        pygame.quit()
                        cap.release()
                        
                
                if event.ui_element == feedback_button:
                    feedback_input.show()
                    submit_button.show()

                if event.ui_element == submit_button:
                    submit_feedback()
                    toggle_pause_mode() # Toggles pause state     

            manager.process_events(event)

def mouse_logger(clock):
    """
    Thread to capture mouse movments 
    """
    global paused, leftMouseDown, rightMouseDown, wheelMouseDown, running

    while running:

        if not paused:

            mouse_dx, mouse_dy = pygame.mouse.get_rel() # Get mouse position
            mouse_left, mouse_wheel, mouse_right = pygame.mouse.get_pressed() # Get mouse buttons pressed

            # check each button to see if the current state is different from the previous state
            # if the states don't match resolve either the up/down action to return to 
            # both states matching
            if mouse_left != leftMouseDown:
                if mouse_left:
                    sendKeyboardMouseAction("mousedown", 0, mouse_dx, mouse_dy, serial_input)
                if not mouse_left:
                    sendKeyboardMouseAction("mouseup", 0, mouse_dx, mouse_dy, serial_input)
                leftMouseDown = mouse_left

            if mouse_wheel != wheelMouseDown:
                if mouse_wheel:
                    sendKeyboardMouseAction("mousedown", 1, mouse_dx, mouse_dy, serial_input)
                if not mouse_wheel:
                    sendKeyboardMouseAction("mouseup", 1, mouse_dx, mouse_dy, serial_input)
                wheelMouseDown = mouse_wheel

            if mouse_right != rightMouseDown:    
                if mouse_right:
                    sendKeyboardMouseAction("mousedown", 2, mouse_dx, mouse_dy, serial_input)
                if not mouse_right:
                    sendKeyboardMouseAction("mouseup", 2, mouse_dx, mouse_dy, serial_input)
                rightMouseDown = mouse_right

            # mouse movement
            if mouse_dx != 0 | mouse_dy != 0:
                sendKeyboardMouseAction("mousemove",0,mouse_dx,mouse_dy,serial_input)
                if verbose:
                    print(mouse_dx,mouse_dy)

            # Center the mouse position
            pygame.mouse.set_pos(window_width // 2, window_height // 2)

            # Limit mouse pull rate to 60 FPS
            clock.tick(240)

def reset_arduino_watchdog():
    """ Send reset code to the arduino """
    data_hex = "\x06" + "a"
    serial_input.write(data_hex.encode())

def keep_arduino_running():
    """ Reset the arduino to keep the program running """
    while running:
        reset_arduino_watchdog()
        time.sleep(5)
        
def load_frame():
    while running:
    # Read a frame from the video stream
        ret, frame = cap.read()
        if not ret:
            print("Error: No Video")
            return 0

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)   # Rotate the frame 90 degrees clockwise
        frame = cv2.flip(frame, 0)                                  # Flip the frame over the y axis
        frame = cv2.resize(frame, (window_height,window_width))     # Resize the frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)              # Convert the frame to RGB (Pygame uses RGB format)
        frame = pygame.surfarray.make_surface(frame)                # Convert the frame to Pygame surface
        screen.blit(frame, (0, 0))                                  # Blit the frame to the Pygame window


if __name__ == '__main__':
    # Set the Serial input
    serial_input = serial.Serial(arduino_path,115200)

    # Set up PulseAudio in the OS to listen to the capture card
    subprocess.call(['sh', './Programs/pulseAudio_config.sh'])

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # Initialize OpenCV for video capture
    cap = cv2.VideoCapture(getVideoInputDevice())
    cap.set(3, window_width)
    cap.set(4, window_height)

    # Initialize Pygame GUI
    manager = pygame_gui.UIManager((window_width, window_height))

    # Create pygame gui buttons
    resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                                text='Resume', manager=manager)
    feedback_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((120, 10), (150, 50)),
                                                text='Submit Feedback', manager=manager)
    power_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((280, 10), (140, 50)), 
                                                text='Power On/Off', manager=manager)
    kill_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((430, 10), (140, 50)), 
                                                text='Force Shutdown', manager=manager)                           
    exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((580, 10), (140, 50)),
                                                text='Disconnect', manager=manager)
    feedback_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((50, 100), (300, 100)),
                                                      manager=manager)
    feedback_input.hide()
    submit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((150, 220), (100, 40)),
                                             text='Submit',
                                             manager=manager)
    submit_button.hide()

    # Create a clock object to control the frame rate
    clock = pygame.time.Clock()

    # Create threads for each function
    keyboard_thread = threading.Thread(target=start_keyboard_input, args=(serial_input, verbose,))
    mouse_thread = threading.Thread(target=mouse_logger,args=(clock,))
    event_thread = threading.Thread(target=event_handler,)
    arduino_thread = threading.Thread(target=keep_arduino_running,)
    video_thread = threading.Thread(target= load_frame,)

    # Start the threads
    keyboard_thread.start()
    mouse_thread.start()
    event_thread.start()
    arduino_thread.start()
    video_thread.start()

    while running:
        
        # Cap the video framerate to 60 FPS - Change .tick(<number>)
        time_delta = pygame.time.Clock().tick(60) / 1000.0

        if paused:
            # Update the Pygame GUI manager
            manager.update(time_delta)
            # Draw the GUI managers
            manager.draw_ui(screen)
        
        pygame.display.flip()