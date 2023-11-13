import pygame
from pygame.locals import *
from libraries.sendKeyboardMouse import *
import serial



def start_mouse_input(serial_input):
    # Initialize Pygame
    pygame.init()

    # Set screen dimensions
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.mouse.set_visible(False)

    # Set the initial camera position
    camera_x, camera_y = 0, 0

    # Set the initial mouse position to the center of the screen
    pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

    # Create a clock object to control the frame rate
    clock = pygame.time.Clock()

    leftMouseDown = False
    rightMouseDown = False
    wheelMouseDown = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            # mouse wheel event to track wheel movement
            if event.type == MOUSEWHEEL:
                print(event.x,event.y)
                sendKeyboardMouseAction("mousescroll",0,event.x, event.y, serial_input)



        # Get the relative mouse movement and current state of mouse buttons
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

    pygame.quit()
