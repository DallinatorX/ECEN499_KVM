import pygame
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Set screen dimensions
screen_width, screen_height = 1920, 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.mouse.set_visible(False)

# Set the initial camera position
camera_x, camera_y = 0, 0

# Set the initial mouse position to the center of the screen
pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

running = True

this = 0

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    

    # Get the relative mouse movement
    mouse_dx, mouse_dy = pygame.mouse.get_rel()
    
    sendKeyboardMouseAction("mousemove",0,mouse_dx,mouse_dy)
    if this == 1:
        print(mouse_dx,mouse_dy)
    else:
        if this == 100:
            this = 0
    this += 1
    

    # Update the camera position based on mouse movement
    camera_x += mouse_dx
    camera_y += mouse_dy

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the world with the camera offset
    # Replace this with your game graphics or rendering logic
    pygame.draw.rect(screen, (255, 0, 0), (200 - camera_x, 200 - camera_y, 50, 50))

    # Update the display
    pygame.display.flip()

    # Center the mouse position
    pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

    # Limit frame rate to 60 FPS
    clock.tick(60)

pygame.quit()
