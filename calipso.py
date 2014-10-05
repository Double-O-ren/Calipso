from flask import Flask
import flask
import serial

app = Flask(__name__)
app.debug = True

def event_barcode():
    ser = serial.Serial(address = "/dev/tty.MindWaveMobile-DevA")
    ser.port = 1
    ser.baudrate = 9600
    ser.bytesize = 8
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.open()
    s = ser.read(7)
    yield 'data: %s\n\n' % s

@app.route('/barcode')
def barcode():
    newresponse = flask.Response(event_barcode(), mimetype="text/event-stream")
    newresponse.headers.add('Access-Control-Allow-Origin', '*')
    return newresponse

if __name__ == '__main__':
    app.run(port=8080, threaded=True)