# Needed imports
import serial
import time

# Initialize Keyboard Dictionary
KEY_CODES = {   
'Alt': 2,
'Backspace': 4,
'Control': 6,
'Delete': 8,
'ArrowDown': 10,
'End': 12,
'Enter': 14,
'Escape': 16,
'F1': 18,
'F2': 20,
'F3': 22,
'F4': 24,
'F5': 26,
'F6': 28,
'F7': 30,
'F8': 32,
'F9': 34,
'F10': 36,
'F11': 38,
'F12': 40,
'Home': 42,
'ArrowLeft': 44,
'PageDown': 46,
'PageUp': 48,
'ArrowRight': 50,
'Shift': 52,
'space': 54,
'Tab': 56,
'ArrowUp': 58,
#'AltRight': 60,
#'ControlRight': 62,
'OS': 64,
'Meta': 64,
#'OSRight': 66,
'a': 68,
'A': 68,
'b': 70,
'B': 70,
'c': 72,
'C': 72,
'd': 74,
'D': 74,
'e': 76,
'E': 76,
'f': 78,
'F': 78,
'g': 80,
'G': 80,
'h': 82,
'H': 82,
'i': 84,
'I': 84,
'j': 86,
'J': 86,
'k': 88,
'K': 88,
'l': 90,
'L': 90,
'm': 92,
'M': 92,
'n': 94,
'N': 94,
'o': 96,
'O': 96,
'p': 98,
'P': 98,
'q': 100,
'Q': 100,
'r': 102,
'R': 102,
's': 104,
'S': 104,
't': 106,
'T': 106,
'u': 108,
'U': 108,
'v': 110,
'V': 110,
'w': 112,
'W': 112,
'x': 114,
'X': 114,
'y': 116,
'Y': 116,
'z': 118,
'Z': 118,
'`': 120,
'~': 120,
'1': 122,
'!': 122,
'2': 124,
'@': 124,
'3': 126,
'#': 126,
'4': 128,
'$': 128,
'5': 130,
'%': 130,
'6': 132,
'^': 132,
'7': 134,
'&': 134,
'8': 136,
'*': 136,
'9': 138,
'(': 138,
'0': 140,
')': 140,
'-': 142,
'_': 142,
'=': 144,
'+': 144,
'[': 146,
'{': 146,
']': 148,
'}': 148,
'\\': 150,
'|': 150,
'CapsLock': 152,
';': 154,
':': 154,
'\'': 156,
'\"': 156,
',': 158,
'<': 158,
'.': 160,
'>': 160,
'/': 162,
'?': 162,
'Insert': 164,
'F13': 166,
'F14': 168,
'F15': 170,
'F16': 172,
'F17': 174,
'F18': 176,
'F19': 178,
'F20': 180,
#'ShiftRight': 182
}

# Initialize Mouse Dictionary
MOUSE_CODES = {
    "0": 0, # Left Click
    "2": 2, # Right Click
    "1": 4  # Scroll Click
}


# Select Serial port (needs to be updated to auto find port)
# ser1 = serial.Serial("/dev/ttyACM2",9600)

def int_to_2sComp(num):
    """
    Converts a normal python number to 2 complement 
    """
    if num < -128:
        return 0
    elif num > 127:
        return 255
    elif num >= 0:
        return num
    return (1 << 8) + num

def sendKeyboardMouseAction(in_type, key, mouseX, mouseY, serial_input):
    """
    This Function recives the type of input
    in_type = 'keydown'; Press the key
    in_type = 'keyup'; relase key
    in_type = 'mousemove'; move the mouse
    in_type = 'mousedown'; click mouse button
    in_type = 'mouseup'; release mouse button
    in_type = 'mousescroll'; scroll mouse

    key: It the mosue or keyboard button pressed or released, use the titles lited above (Ex.F12 not f12 or 40)
    mouseX and mouseY: tell the computer how much to move its mouse or how much to scroll
    """
    if (in_type == 'keydown' or in_type == 'keyup'): # Keyboard down/up
        key_code = KEY_CODES.get(str(key))
        if in_type == 'keydown':
            key_code += 1
        data_hex = "\x01" +  chr(key_code)

    elif (in_type == 'mousemove'): # Mouse Move
        # abs() to prevent negative bits from passing
        data_hex = "\x02" + chr(abs(int_to_2sComp(int(mouseX)))) + chr(abs(int_to_2sComp(int(mouseY))))

    elif (in_type == 'mousedown' or in_type == 'mouseup'): # Mouse Buttons
        key_code = MOUSE_CODES.get(str(key))
        if in_type == 'mousedown':
            key_code += 1
        data_hex = "\x03" + hex(key_code)

    elif (in_type == 'mousescroll'): # Mouse Scroll
        data_hex = "\x04" + hex(abs(int_to_2sComp(int(mouseX)))) + hex(abs(int_to_2sComp(int(mouseY))))
    
    else:
        print("Error: Improper command sent, ignored.")

    serial_input.write(data_hex.encode())
    
    print(data_hex)

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
