from flask import Flask, render_template, Response, request, jsonify
import cv2 as cv
import argparse
import subprocess
import time
import sys

# Questions regarding Flask or other libraries?
# Refer to the library documentation online

rtsp = Flask(__name__)

device = "video0"
width = 1920
height = 1080
verbose = False
START_ADDRESS = 8
MOUSE_INTERPLELATION = 4
JPEG_QUALITY = 75

# Set up PulseAudio in the OS to listen to the capture card
subprocess.call(['sh', './pulseAudio_config.sh'])

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
    # return Response(gen_sound(), mimetype='audio/x-wav; codec=pcm')
    return 0


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


def start_rtsp():
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

    # if (verbose):    
        print("\nDetails:")
        print("--Device: " + "/dev/" + str(device))
        print("--width:  " + str(width))
        print("--height: " + str(height))
        print()

    rtsp.run(ssl_context=('adhoc'), host="0.0.0.0", debug=True)
