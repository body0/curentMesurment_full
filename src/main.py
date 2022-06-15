from flask import Flask, Response, request
from flask_cors import CORS
import json
import ioControl
import power
import ruleEvaluator
import db

db.connectToDb()
power.startWatcher()

app = Flask(__name__)
CORS(app)

@app.route('/api/', methods=['GET'])
def testApi():
    return 'Hallo'

@app.route('/api/boiler/set', methods=['POST'])
def boilerSet():
    content = request.get_json()
    ruleEvaluator.setEnableEvaluation(not content['overideActive'])
    if content['overideActive']:
        ioControl.setBoilerState(content['state'])
    return json.dumps({
        "state": ioControl.getBoilerState(),
        "overideActive": not ruleEvaluator.getEnableEvaluetion()
    })

@app.route('/api/boiler/get', methods=['POST'])
def boilerGet():
    return json.dumps({
        "state": ioControl.getBoilerState(),
        "overideActive": not ruleEvaluator.getEnableEvaluetion(),
        "controlList": ruleEvaluator.exportRuleList()
    })
    
@app.route('/api/boiler/rule/set', methods=['POST'])
def boilerRuleSet():
    content = request.get_json()
    ruleEvaluator.setRuleLis(content["controlList"])
    return json.dumps({
    })

@app.route('/api/power/outputNow', methods=['POST'])
def powerOutputNow():
    powerList = power.getPower()
    return json.dumps({
        "phase_EA": powerList[0][1],
        "phase_EB": powerList[1][1],
        "phase_EC": powerList[2][1],
        "phase_HA": powerList[0][0],
        "phase_HB": powerList[1][0],
        "phase_HC": powerList[2][0],
        
        "phase_EA_pfac": powerList[0][5],
        "phase_EB_pfac": powerList[1][5],
        "phase_EC_pfac": powerList[2][5],
        "phase_HA_pfac": powerList[0][4],
        "phase_HB_pfac": powerList[1][4],
        "phase_HC_pfac": powerList[2][4]
    }) 

app.run(host='0.0.0.0')