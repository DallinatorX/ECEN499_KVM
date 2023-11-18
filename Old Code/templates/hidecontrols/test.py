import serial  # used for communication with computer
import time # used for sleep function
from flask import Flask, render_template, request 

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index_v2.html') #tells the program to find "index.html" in the templates folder and display it in the webpage
    
if __name__ == '__main__':
 
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()

