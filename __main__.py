"""
This is the core file for the KVM. Running this will start all needed function.
"""
# from Programs.rtsp_v2 import *
from Programs.getkeyboardinput import *
from Programs.getMouseInput import *
import threading
import subprocess
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import simpledialog
import cv2
import pygame_gui

#Set Video device info
device = "video0"

# Other constants
power_code = "p"
shutdown_code = "k"

window_width = 1920
window_height = 1080
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)


#Set the arduino path
arduino_path = "/dev/ttyACM0"


# Mouse actions
leftMouseDown = False
rightMouseDown = False
wheelMouseDown = False
running = True
paused = False  # Variable to keep track of the pause state
fullscreen = False # Variable to keep track of the fullscreen state

def getVideoInputDevice():
    frames_loc = '/dev/' + str(device)
    return frames_loc

def toggle_pause_mode():
    """Toggles pause-state boolean and visibility of local mouse pointer"""
    global paused
    paused = not paused  # Toggle pause state
    if paused:
        pygame.mouse.set_visible(True)  # Show the mouse when paused
    else:
        pygame.mouse.set_visible(False) # Hide the mouse when not paused


#Set the arduino path
arduino_path = "/dev/ttyACM1"


if __name__ == '__main__':
    serial_input = serial.Serial(arduino_path,115200)

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.mouse.set_visible(False)


    # Initialize OpenCV for video capture
    cap = cv2.VideoCapture(getVideoInputDevice())
    cap.set(3, window_width)
    cap.set(4, window_height)



    paused = False  # Variable to keep track of the pause state

    # Initialize Pygame GUI
    manager = pygame_gui.UIManager((window_width, window_height))


    # Create a buttons
    resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                                text='Resume', manager=manager)

    power_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((230, 10), (140, 50)), 
                                                text='Power On/Off', manager=manager)

    kill_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((380, 10), (140, 50)), 
                                                text='Force Shutdown', manager=manager)
                                                
    exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((530, 10), (140, 50)),
                                                text='Disconnect', manager=manager)        


    # Create threads for each function
    keyboard_thread = threading.Thread(target=start_keyboard_input, args=(serial_input,))
    # mouse_thread = threading.Thread(target=start_mouse_input, args=(serial_input,))
    # rtsp_thread = threading.Thread(target=start_rtsp)

    # Start the threads
    keyboard_thread.start()
    # mouse_thread.start()
    # rtsp_thread.start()

    # Wait for all threads to finish (if needed)
    # keyboard_thread.join()
    # mouse_thread.join()
    # rtsp_thread.join()



    #Set up pyGame for mouse input
    camera_x, camera_y = 0, 0

    # Set the initial mouse position to the center of the screen
    pygame.mouse.set_pos(window_width // 2, window_height // 2)

    # Create a clock object to control the frame rate
    clock = pygame.time.Clock()

    leftMouseDown = False
    rightMouseDown = False
    wheelMouseDown = False
    running = True



    while True:
        time_delta = pygame.time.Clock().tick(60) / 1000.0

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                keyboard_thread.join()
            elif event.type == KEYDOWN:
                if event.key == K_u and pygame.key.get_mods() & KMOD_ALT:
                    toggle_pause_mode() # Toggles pause state

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == resume_button:
                    print("Host - Resuming...")
                    toggle_pause_mode() # Toggles pause state
                if event.ui_element == power_button:
                    print("Host - Toggling power button...")
                    serial_input.write(power_code.encode())
                if event.ui_element == kill_button:
                    print("Host - Forcing shutdown...")
                    serial_input.write(shutdown_code.encode())
                if event.ui_element == exit_button:
                    print("Disconnecting from Host...")
                    running = False
                if event.ui_element == fullscreen_button:
                    fullscreen = not fullscreen  # Toggle fullscreen state
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((window_width, window_height))
                if event.ui_element == feedback_button:
                    # Open a dialog to get user feedback
                    root = tk.Tk()
                    root.withdraw()
                    feedback = simpledialog.askstring("Feedback", "Enter your feedback:")
                    
                    # Write feedback to a text file
                    if feedback:
                        with open('user_feedback.txt', 'a') as file:
                            file.write(feedback + '\n')   

            elif event.type == MOUSEWHEEL:#Recored mouse scroll
                print(event.x,event.y)
                sendKeyboardMouseAction("mousescroll",0,event.x, event.y, serial_input)

            manager.process_events(event)

def mouse_logger(clock):
    global paused, leftMouseDown, rightMouseDown, wheelMouseDown, running
    while running:
        if not paused:

            mouse_dx, mouse_dy = pygame.mouse.get_rel()
            mouse_left, mouse_wheel, mouse_right = pygame.mouse.get_pressed()

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
                print(mouse_dx,mouse_dy)

            # Center the mouse position
            pygame.mouse.set_pos(window_width // 2, window_height // 2)

            # Limit frame rate to 60 FPS
            clock.tick(60)

if __name__ == '__main__':
    serial_input = serial.Serial(arduino_path,115200)

    # Set up PulseAudio in the OS to listen to the capture card
    # subprocess.call(['sh', './Programs/pulseAudio_config.sh'])


    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
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
    fullscreen_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((120, 10), (120, 50)),
                                                    text='Fullscreen', manager=manager)
    feedback_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 10), (150, 50)),
                                                text='Submit Feedback', manager=manager)
    power_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((410, 10), (140, 50)), 
                                                text='Power On/Off', manager=manager)
    kill_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((560, 10), (140, 50)), 
                                                text='Force Shutdown', manager=manager)                           
    exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((710, 10), (140, 50)),
                                                text='Disconnect', manager=manager)

    # Create a clock object to control the frame rate
    clock = pygame.time.Clock()

    # Create threads for each function
    keyboard_thread = threading.Thread(target=start_keyboard_input, args=(serial_input,))
    mouse_thred = threading.Thread(target=mouse_logger,args=(clock,))
    event_thread = threading.Thread(target=event_handler,)

    # Start the threads
    keyboard_thread.start()
    event_thread.start()
    mouse_thred.start()

    while running:
        time_delta = pygame.time.Clock().tick(60) / 1000.0

	    # Read a frame from the video stream
        ret, frame = cap.read()
        if not ret:
            break

        # Rotate the frame 90 degrees clockwise
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # Flip the frame over the y axis
        frame = cv2.flip(frame, 0)

    	# Resize the frame to double the size
    	# frame = cv2.resize(frame, (frame.shape[1] * 2, frame.shape[0] * 2))
        frame = cv2.resize(frame, (window_height,window_width) )
        
        
        # Convert the frame to RGB (Pygame uses RGB format)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert the frame to Pygame surface
        frame = pygame.surfarray.make_surface(frame)

    	# Blit the frame to the Pygame window
        screen.blit(frame, (0, 0))

        if not paused:
            pass
        else:
        	
            # Update the Pygame GUI manager
            manager.update(time_delta)
            # Draw the GUI manager
            manager.draw_ui(screen)

        pygame.display.flip()
    
    cap.release()
    pygame.quit()