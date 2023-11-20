from os import kill
import cv2
import pygame
import pygame_gui
import serial
import tkinter as tk
from tkinter import simpledialog
from pygame.locals import *

# MACROS/PARAMETERS
device = "video0"
power_code = "p"
shutdown_code = "k"


#serial_input = serial.Serial("/dev/ttyACM0",115200)


def getVideoInputDevice():
    frames_loc = '/dev/' + str(device)
    return frames_loc

def warning_popup():
    popup = pygame_gui.UIManager((500, 500))
    yes_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                            text='Yes', manager=popup)
    no_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((130, 10), (100, 50)),
                                            text='No', manager=popup)
    while True:
        time_delta = pygame.time.Clock().tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == yes_button:
                        return 1
                    elif event.ui_element == no_button:
                        return 0 
            popup.process_events(event)
            popup.update(time_delta)
            popup.draw_ui(screen)
        popup.process_events(event)
        pygame.display.flip()


# Initialize Pygame
pygame.init()

# Set the dimensions of the Pygame window
window_width = 1920
window_height = 1080
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
width = 1920
height = 1080

pygame.display.set_caption("Welcome to KVM!")


# Initialize OpenCV for video capture
cap = cv2.VideoCapture(getVideoInputDevice())
cap.set(3, width)
cap.set(4, height)

paused = False  # Variable to keep track of the pause state
fullscreen = False # Variable to keep track of the fullscreen state

# Initialize Pygame GUI
manager = pygame_gui.UIManager((window_width, window_height))

# Create a button
resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                            text='Resume', manager=manager)

power_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((230, 10), (140, 50)), 
                                            text='Power On/Off', manager=manager)

kill_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((380, 10), (140, 50)), 
                                            text='Force Shutdown', manager=manager)
                                            
exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((530, 10), (140, 50)),
                                            text='Disconnect', manager=manager)
        
fullscreen_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((680, 10), (140, 50)),
                                                 text='Fullscreen',
                                                 manager=manager)

feedback_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((830, 10), (150, 50)),
                                               text='Submit Feedback',
                                               manager=manager)

while True:
    time_delta = pygame.time.Clock().tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == QUIT:
            print("Disconnecting from Host...")
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_u and pygame.key.get_mods() & KMOD_LALT:
                paused = not paused  # Toggle pause state
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen  # Toggle fullscreen state
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((window_width, window_height))     
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == resume_button:
                    print("Host - Resuming...")
                    paused = not paused  # Toggle pause state  
                if event.ui_element == power_button:
                    if(warning_popup()):
                        print("Host - Toggling power button...")
                        #serial_input.write(power_code.encode())
                if event.ui_element == kill_button:
                    if (warning_popup()):
                        print("Host - Forcing shutdown...")
                        #serial_input.write(shutdown_code.encode())
                if event.ui_element == exit_button:
                    if(warning_popup()):
                        print("Disconnecting from Host...")
                        pygame.quit()
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

        manager.process_events(event)

    if not paused:
        # Read a frame from the video stream
        ret, frame = cap.read()
        if not ret:
            break

        # Rotate the frame 90 degrees clockwise
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # Flip the frame over the y axis
        frame = cv2.flip(frame, 0)

        # Resize the frame to double the size
        #frame = cv2.resize(frame, (frame.shape[1] * 2, frame.shape[0] * 2))

        # Convert the frame to RGB (Pygame uses RGB format)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to Pygame surface
        frame = pygame.surfarray.make_surface(frame)

        # Blit the frame to the Pygame window
        screen.blit(frame, (0, 0))
    else:
        # Update the Pygame GUI manager
        manager.update(time_delta)
        # Draw the GUI manager
        manager.draw_ui(screen)

    pygame.display.flip()

cap.release()
pygame.quit()
