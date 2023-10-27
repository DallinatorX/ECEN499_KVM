from flask import Flask, render_template, Response, request, jsonify
import cv2 as cv
import pyaudio
import argparse
import subprocess
import time
import sys
#from ./libraries/sendKeyboardMouse import *

import libraries.sendKeyboardMouse

# Michael was here

# Questions regarding Flask or other libraries?
# Refer to the library documentation online

rtsp = Flask(__name__)

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
ROPEN = True # From an online example
# CHUNK = 1024
CHUNK = int(RATE/20) # From online example
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
