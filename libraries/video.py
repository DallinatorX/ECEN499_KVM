import cv2


def getVideoInputDevice(device):
    """
    Given the Device name returns the full path
    """
    frames_loc = '/dev/' + str(device)
    return frames_loc



class KVM:
    """

    """

    def __init__(self,window_width,window_height,pygame,video_device):
        """
        
        """
        self._screen = pygame.display.set_mode((window_width, window_height))
        self._pygame = pygame
        self._cap = cv2.VideoCapture(getVideoInputDevice(video_device))
        