from os import kill
import cv2
import pygame
import pygame_gui
import serial
import tkinter as tk
from pygame.locals import *
from tkinter import *
from tkinter.ttk import *
from datetime import datetime
import sys

# MACROS/PARAMETERS
device = "video0"
power_code = "p"
shutdown_code = "k"


#serial_input = serial.Serial("/dev/ttyACM0",115200)


def getVideoInputDevice():
    frames_loc = '/dev/' + str(device)
    return frames_loc

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
    
    btn1 = Button(root, text = 'Yes', command=lambda:[yes_button(), root.destroy()]).pack(side = 'left')
    btn2 = Button(root, text = 'No', command=lambda:[no_button(), root.destroy()]).pack(side = 'right')

    label = Label(root, text ="Are you sure?").pack()

    root.mainloop()
    return answer


# Initialize Pygame
pygame.init()

# Set the dimensions of the Pygame window
window_width = 1600
window_height = 900
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

fullscreen_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((120, 10), (120, 50)),
                                                 text='Fullscreen',
                                                 manager=manager)

feedback_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 10), (150, 50)),
                                               text='Submit Feedback',
                                               manager=manager)

power_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((410, 10), (140, 50)), 
                                            text='Power On/Off', manager=manager)

kill_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((560, 10), (140, 50)), 
                                            text='Force Shutdown', manager=manager)
                                            
exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((710, 10), (140, 50)),
                                            text='Disconnect', manager=manager)
        
feedback_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((50, 100), (300, 100)),
                                                      manager=manager)
feedback_input.hide()

submit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((150, 220), (100, 40)),
                                             text='Submit',
                                             manager=manager)
submit_button.hide()


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
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
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
                    feedback_input.show()
                    submit_button.show()
            elif event.ui_element == submit_button:
                    submit_feedback()
                    paused = not paused
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
