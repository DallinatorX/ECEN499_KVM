from flask import Flask, render_template, Response, request, jsonify
import cv2 as cv
import pyaudio
import argparse
import subprocess
import time
import sys

# Michael was here

# Questions regarding Flask or other libraries?
# Refer to the library documentation online

rtsp = Flask(__name__)

ENABLE_DEBUG = False

device = "video0"
width = 1280
height = 720
verbose = False
START_ADDRESS = 8
MOUSE_INTERPLELATION = 4
JPEG_QUALITY = 75

# Code for Audio recording:
# https://stackoverflow.com/questions/51079338/audio-livestreaming-with-python-flask

# Audio Parameters
AUDIO_DEVICE = 0
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
BITS_PER_SAMPLE = 16
audio1 = pyaudio.PyAudio()

# Communication to Arduino Parameters
#baudrate = 9600 #make sure baudrate is same as arduino
#port = '/dev/ttyACM0'  #make sure to change the com port based on where it is plugged in
#arduino = serial.Serial(port, baudrate, timeout = 0.1)
time.sleep(0.5)
power_code = "p"
shutdown_code = "k"

# Misc Action Dictionary
MISC_CODES = {
    'poweron': 'python3 power_on.py', # TODO: Add commands for shutdown etc
    'poweroff': 'python3 power_off.py'
}

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
' ': 54,
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



@rtsp.route('/process_data', methods=['POST'])
def process_km_data():
    data = request.get_json()
    if False:
        print('Data Recieved! : ' + str(data))

    type   = data['event']
    key    = data['button']
    mouseX = data['deltaX']
    mouseY = data['deltaY']

    if type == 'misc':
        sendMiscAction(key)
    else:
        sendKeyboardMouseAction(type, key, mouseX, mouseY)

    return jsonify({'type': type, 'key': key, 'mouseX': mouseX, 'mouseY': mouseY, 'result': 'success'})


@rtsp.route("/audio_feed")
def audio_feed():
    return Response(gen_sound(), mimetype='audio/x-wav; codec=pcm')


@rtsp.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@rtsp.route('/')
def index():
    return render_template('index_v2.html')

@rtsp.route('/execute/<action>')
def exec_command(action):
    if action == "tglPower":
        result = togglePower()
    elif action == "forceShutdown":
        result = forceShutdown()
    else:
        print("No function of that name")
    return result

def gen_frames():
    camera = cv.VideoCapture(getVideoInputDevice())
    camera.set(3,width)
    camera.set(4,height)

    start = 0
    end = 0
    
    while True:
        
        if (verbose):
            start = time.time()
        
        success, frame = camera.read()
        if not success:
            break
        
        ret, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        if (verbose):
            end = time.time()
            print('Total time (in ms): ', (end - start) * 1000)


def getVideoInputDevice():
    frames_loc = '/dev/'+ str(device)
    return frames_loc


def gen_sound():
        global FORMAT, CHANNELS, CHUNK, RATE, BITS_PER_SAMPLE, AUDIO_DEVICE

        # Set to Audio-In of capture card, etc

        wav_header = generateAudioHeader(RATE, BITS_PER_SAMPLE, CHANNELS)
        stream = audio1.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, input_device_index=AUDIO_DEVICE,
                        frames_per_buffer=CHUNK)

        # if quiet:
        #     print("recording...")

        # Send header only once, or else audio bugs
        first_run = True
        while True:
           if first_run:
               print("Sound POST: Sent Header Chunk")
               data = wav_header + stream.read(CHUNK)
               first_run = False
           else:
               print("Sound POST: Sent", str(CHUNK), " to POST.")
               data = stream.read(CHUNK)
           yield(data)


def generateAudioHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               
# (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o


# Adapted from: https://stackoverflow.com/questions/36894315/how-to-select-a-specific-input-device-with-pyaudio
# TODO
# Command in Ubuntu to display devices: 'pacmd list-sources'
def getAudioInputDevice():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))


def sendKeyboardMouseAction(in_type, key, mouseX, mouseY):
    global ENABLE_DEBUG
    i2c_command_start = "i2ctransfer -y"
    if ENABLE_DEBUG:
        i2c_command_start += " -v"
    i2c_command_start += " 0 w"
    data_len = 0

    if (in_type == 'keydown' or in_type == 'keyup'): # Keyboard down/up
        # val1 = isPressed, val2 = key_pressed
        data_len = 2
        key_code = KEY_CODES.get(str(key))
        if in_type == 'keydown':
            key_code += 1
        data_hex = " 0x01 " + hex(key_code)

    elif (in_type == 'mousemove'): # Mouse Move
        # val1 = mouse_x, val2 = mouse_y
        data_len = 3
        # abs() to prevent negative bits from passing to kernel
        data_hex = " 0x02 " + hex(abs(int_to_2sComp(int(mouseX)))) + " " + hex(abs(int_to_2sComp(int(mouseY))))

    elif (in_type == 'mousedown' or in_type == 'mouseup'): # Mouse Buttons
        # val1 = isPressed, val2 = button
        data_len = 2
        key_code = MOUSE_CODES.get(str(key))
        if in_type == 'mousedown':
            key_code += 1
        data_hex = " 0x03 " + hex(key_code)

    elif (in_type == 'mousescroll'): # Mouse Scroll
         # val1 = scroll_x, val2 = scroll_y
        data_len = 3
        data_hex = " 0x04 " + hex(abs(int_to_2sComp(int(mouseX)))) + " " + hex(abs(int(int_to_2sComp(mouseY))))

    else:
        print("Error: Improper command sent, ignored.")

    # Send command to I2C
    # Build I2C transfer line
    if data_len != 0 and START_ADDRESS > 0:
        i2c_command = i2c_command_start + str(data_len) + "@" + hex(START_ADDRESS) + data_hex
        subprocess.run(i2c_command, shell=True)


def int_to_2sComp(num):
    if num < -128:
        return 0
    elif num > 127:
        return 255
    elif num >= 0:
        return num
    return (1 << 8) + num


def sendMiscAction(key):
    command = MISC_CODES.get(key)
    if command != None:
        print("Command: ", str(key), " would be sent...")
        # subprocess.run(command, shell=True)

# Tell the Arduino via serial to run togglePower operation
def togglePower(): 
    print("test toggle power button...")
    arduino.write(power_code.encode())

# Tell the Arduino via serial to run forceShutdown operation
def forceShutdown():
    print("powering down gaming pc...")
    arduino.write(shutdown_code.encode())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--device",     "-d", default="video0",                     help="File within the /dev/ directory to use as video feed")
    parser.add_argument("--width",      "-W", default=1920,                         help="Width for video capture")
    parser.add_argument("--height",     "-H", default=1080,                         help="Height for video capture")
    parser.add_argument("--verbose",    "-v", default=False, action="store_true",   help="Run in debug mode")
    args = parser.parse_args()

    if args.device:
        device = str(args.device)
    else:
        sys.exit("video device not found!!! Please use format: --device")

    if args.width:
        width = args.width

    if args.height:
        height = args.height

    if args.verbose:
        verbose = True

    if (verbose):    
        print("\nDetails:")
        print("--Device: " + "/dev/" + str(device))
        print("--width:  " + str(width))
        print("--height: " + str(height))
        print()

    rtsp.run(ssl_context=('adhoc'), host="0.0.0.0", debug=True)
