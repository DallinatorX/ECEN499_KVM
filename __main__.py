"""
This is the core file for the KVM. Running this will start all needed function.
"""
# from Programs.rtsp_v2 import *
from Programs.getkeyboardinput import *
from Programs.getMouseInput import *
import threading
import pygame
from pygame.locals import *
import cv2



#Set Video device info
device = "video0"
window_width = 1920
window_height = 1080

#Set the arduino path
arduino_path = "/dev/ttyACM0"


if __name__ == '__main__':
    serial_input = serial.Serial(arduino_path,115200)

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.mouse.set_visible(False)


    # Initialize OpenCV for video capture
    cap = cv2.VideoCapture(getVideoInputDevice())
    cap.set(3, width)
    cap.set(4, height)



    paused = False  # Variable to keep track of the pause state

    # Initialize Pygame GUI
    manager = pygame_gui.UIManager((window_width, window_height))


    # Create a buttons
    pause_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                                text='Pause',
                                                manager=manager)

    hi_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((120, 10), (100, 50)),
                                                text='Hi',
                                                manager=manager)


    # Create threads for each function
    keyboard_thread = threading.Thread(target=start_keyboard_input, args=(serial_input,))
    # mouse_thread = threading.Thread(target=start_mouse_input, args=(serial_input,))
    # rtsp_thread = threading.Thread(target=start_rtsp)

    # Start the threads
    keyboard_thread.start()
    # mouse_thread.start()
    # rtsp_thread.start()

    # Wait for all threads to finish (if needed)
    keyboard_thread.join()
    # mouse_thread.join()
    # rtsp_thread.join()



    #Set up pyGame for mouse input
    camera_x, camera_y = 0, 0

    # Set the initial mouse position to the center of the screen
    pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

    # Create a clock object to control the frame rate
    clock = pygame.time.Clock()

    leftMouseDown = False
    rightMouseDown = False
    wheelMouseDown = False
    running = True



    while True:
        time_delta = pygame.time.Clock().tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_TAB and pygame.key.get_mods() & KMOD_SHIFT:
                    paused = not paused  # Toggle pause state
                    pygame.mouse.set_visible(True) #Show the mouse when paused

            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == pause_button:
                        paused = not paused  # Toggle pause state
                    if event.ui_element == hi_button:
                        print("Hi")  # Toggle pause state

            elif event.type == MOUSEWHEEL:#Recored mouse scroll
                print(event.x,event.y)
                sendKeyboardMouseAction("mousescroll",0,event.x, event.y, serial_input)

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

            # Hide the mouse when unpasued
            pygame.mouse.set_visible(False)





            mouse_dx, mouse_dy = pygame.mouse.get_rel()
            mouse_left, mouse_wheel, mouse_right = pygame.mouse.get_pressed()

            # Get the current state of keyboard keys: Michael was here
            # keys = pygame.key.get_pressed()

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

            #mouse movement
            if mouse_dx != 0 | mouse_dy != 0:
                sendKeyboardMouseAction("mousemove",0,mouse_dx,mouse_dy,serial_input)

            # #keyboard press: Michael was here
            # if keys[pygame.K_LALT]:
            #     sendKeyboardMouseAction('keydown',KEY_CODES.get('alt'),0,0,serial_input)



            # Update the camera position based on mouse movement
            camera_x += mouse_dx
            camera_y += mouse_dy

            # Clear the screen
            screen.fill((0, 0, 0))

            # Draw the world with the camera offset
            # Replace this with your game graphics or rendering logic
            #pygame.draw.rect(screen, (255, 0, 0), (200 - camera_x, 200 - camera_y, 50, 50))

            # Update the display
            pygame.display.flip()

            # Center the mouse position
            pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

            # Limit frame rate to 60 FPS
            clock.tick(60)

        else:
            # Update the Pygame GUI manager
            manager.update(time_delta)
            # Draw the GUI manager
            manager.draw_ui(screen)

        pygame.display.flip()

    cap.release()
    pygame.quit()