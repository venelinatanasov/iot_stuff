from flask import Flask, request, render_template, jsonify
from flask_scss import Scss


# import RPi.GPIO as GPIO
# import serial
# from os import system
# import time
# import multiprocessing

app = Flask(__name__)
app.testing = True
Scss(app, static_dir='static', asset_dir='assets')

@app.route('/')
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
