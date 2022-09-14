from fastapi import Body, FastAPI, status, Request, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware

import json
import os
import ioControl
import power
import ruleEvaluator




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.route('/api', methods=['GET'])
def testApi(request: Request):
    print('Hallo api route')
    return 'Hallo'

@app.route('/api/boiler/set', methods=['POST'])
async def boilerSet(request: Request):
    content = await request.json()
    ruleEvaluator.setEnableEvaluation(not content['overideActive'])
    if content['overideActive']:
        ioControl.setBoilerState(content['state'])
    return json.dumps({
        "state": ioControl.getBoilerState(),
        "overideActive": not ruleEvaluator.getEnableEvaluetion()
    })

@app.route('/api/boiler/get', methods=['POST'])
def boilerGet(request: Request):
    return json.dumps({
        "state": ioControl.getBoilerState(),
        "overideActive": not ruleEvaluator.getEnableEvaluetion(),
        "controlList": ruleEvaluator.exportRuleList()
    })
    
@app.route('/api/boiler/rule/set', methods=['POST'])
def boilerRuleSet(request: Request):
    content = request.json()
    ruleEvaluator.setRuleLis(content["controlList"])
    return json.dumps({
    })

@app.route('/api/power/outputNow', methods=['POST'])
def powerOutputNow(request: Request):
    powerList = power.getPower()
    return json.dumps({
        "phase_EA": powerList[0]['ai'],
        "phase_EB": powerList[1]['ai'],
        "phase_EC": powerList[2]['ai'],
        # "phase_HA": powerList[0]['ao'],
        # "phase_HB": powerList[1]['ao'],
        # "phase_HC": powerList[2]['ao'],
        
        # "phase_EA": powerList[0]['ri'],
        # "phase_EB": powerList[1]['ri'],
        # "phase_EC": powerList[2]['ri'],
        "phase_HA": powerList[0]['ro'],
        "phase_HB": powerList[1]['ro'],
        "phase_HC": powerList[2]['ro'],
        
        "phase_EA_pfac": powerList[0]['fi'],
        "phase_EB_pfac": powerList[1]['fi'],
        "phase_EC_pfac": powerList[2]['fi'],
        "phase_HA_pfac": powerList[0]['fo'],
        "phase_HB_pfac": powerList[1]['fo'],
        "phase_HC_pfac": powerList[2]['fo']
    })

def getRoute():
    return app