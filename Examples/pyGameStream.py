import cv2
import pygame
import pygame_gui
from pygame.locals import *

device = "video0"


def getVideoInputDevice():
    frames_loc = '/dev/' + str(device)
    return frames_loc


# Initialize Pygame
pygame.init()

# Set the dimensions of the Pygame window
window_width = 1920
window_height = 1080
screen = pygame.display.set_mode((window_width, window_height))
width = 1920
height = 1080

# Initialize OpenCV for video capture
cap = cv2.VideoCapture(getVideoInputDevice())
cap.set(3, width)
cap.set(4, height)

paused = False  # Variable to keep track of the pause state

# Initialize Pygame GUI
manager = pygame_gui.UIManager((window_width, window_height))

# Create a button
pause_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                            text='Pause',
                                            manager=manager)

hi_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((120, 10), (100, 50)),
                                            text='Hi',
                                            manager=manager)

while True:
    time_delta = pygame.time.Clock().tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_TAB and pygame.key.get_mods() & KMOD_SHIFT:
                paused = not paused  # Toggle pause state
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == pause_button:
                    paused = not paused  # Toggle pause state
                if event.ui_element == hi_button:
                    print("Hi")  # Toggle pause state

        manager.process_events(event)

    if not paused:
        # Read a frame from the video stream
        ret, frame = cap.read()
        if not ret:
            break

        # Rotate the frame 90 degrees clockwise
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

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
