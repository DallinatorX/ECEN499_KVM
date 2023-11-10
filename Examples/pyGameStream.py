import cv2
import pygame
from pygame.locals import *

device = "video0"


def getVideoInputDevice():
    frames_loc = '/dev/'+ str(device)
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
cap = cv2.VideoCapture(getVideoInputDevice()) #'/dev/video2'
cap.set(3,width)
cap.set(4,height)


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()


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
    pygame.display.flip()

cap.release()

