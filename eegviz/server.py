from flask import Flask, request, render_template, redirect
import time
import simplejson as json

app = Flask(__name__)
#app.debug = True

current_data = {}
has_new_data = False

@app.route("/")
def index():
    return render_template('index.html'), 200


@app.route("/mind_sumo")
def mind_sumo():
    return render_template('mind_sumo.html'), 200

@app.route("/data", methods=['GET'])
def data():
    global has_new_data
    resp = json.dumps(current_data)
    has_new_data = False
    return resp, 200

@app.route("/update_data", methods=['POST'])
def update_data():
    global last_data_update
    global has_new_data

    if('update' not in request.args):
        error = "must post data as update url argument"
        resp = json.dumps({'results': error})
        return resp, 500

    data = request.args["update"]

    data = json.loads(data)

    has_new_data = True
    current_data.update(data)

    return json.dumps({}), 200

@app.route("/new_data")
def new_data():
    global has_new_data
    resp = json.dumps({'new_data': has_new_data})
    return resp, 200

if __name__ == "__main__":
    app.run(host='172.31.32.38', port=8000)
