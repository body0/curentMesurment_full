from fastapi import Body, FastAPI, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
    return Response(content="Hello", media_type="application/json")

@app.route('/api/boiler/set', methods=['POST'])
async def boilerSet(request: Request):
    content = await request.json()
    ruleEvaluator.setEnableEvaluation(not content['overideActive'])
    if content['overideActive']:
        ioControl.setBoilerState(content['state'])
    return JSONResponse(content={
        "state": ioControl.getBoilerState(),
        "overideActive": not ruleEvaluator.getEnableEvaluetion()
    })

@app.route('/api/boiler/get', methods=['POST'])
def boilerGet(request: Request):
    return JSONResponse(content={
        "state": ioControl.getBoilerState(),
        "overideActive": not ruleEvaluator.getEnableEvaluetion(),
        "controlList": ruleEvaluator.exportRuleList()
    })
    
@app.route('/api/boiler/rule/set', methods=['POST'])
async def boilerRuleSet(request: Request):
    content = await request.json()
    ruleEvaluator.setRuleLis(content["controlList"])
    return JSONResponse(content={})

@app.route('/api/power/outputNow', methods=['POST'])
def powerOutputNow(request: Request):
    powerList = power.getPower()
    return JSONResponse(content={
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