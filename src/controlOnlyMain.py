from flask import Flask, Response, request
from flask_cors import CORS
import json
import ioControl

app = Flask(__name__)
CORS(app)

@app.route('/api/', methods=['GET'])
def testApi():
    return 'Hallo'

@app.route('/api/boiler/set', methods=['POST'])
def boilerSet():
    content = request.get_json()
    #print(content)
    ioControl.setBoilerState(content['targetState'])
    return json.dumps({
        "curentState": ioControl.getBoilerState()
    })

@app.route('/api/boiler/get', methods=['POST'])
def boilerGet():
    return json.dumps({
        "curentState": ioControl.getBoilerState()
    })

@app.route('/api/power/outputNow', methods=['POST'])
def powerOutputNow():
    return json.dumps({
        "phase_EA": 0,
        "phase_EB": 0,
        "phase_EC": 0,
        "phase_HA": 0,
        "phase_HB": 0,
        "phase_HC": 0,
    })


app.run(host='0.0.0.0')