from datetime import datetime, timedelta

ruleList = []
enableEvaluation = True

def setRuleLis(newList):
    global ruleList, activeRule
    activeRule = -1
    newRuleList = []
    for rule in newList:
        newRuleList.append(_parseRule(rule))
    ruleList = newRuleList
    
def _parseRule(rule):
    parsedVal = None
    cType = rule["type"]
    pld = rule["value"]
    negate = bool(cType == "timeOFF" or cType == "powInOFF" or cType == "powDiffOFF")
    shoftType = "other"
    if cType == "timeON" or cType == "timeOFF":
        parsedVal = {
            "startH": pld["startH"],
            "startM": pld["startM"],
            "endH": pld["endH"],
            "endM": pld["endM"]
        }
        shoftType = "time"
    elif cType == "powInON" or cType == "powInOFF" or cType == "powDiffON" or cType == "powDiffOFF":
        parsedVal = {
            "powVal": pld["powVal"],
            "phase": pld["phase"],
            "holdFor_H": pld["holdFor_H"],
            "holdFor_M": pld["holdFor_M"]
        }
        shoftType = "poIn" if (cType == "powInON" or cType == "powInOFF") else "powDiff"
    else :
        print("=====================\n     WRONG PARM      \n=====================")
        return
    return {
        "enable": rule["enable"],
        "type": cType,
        "pld": parsedVal,
        "meta": {
            "trgToSet": 3,
            "shortType":  shoftType,
            "negateTriger":  negate
        },
        "din":{
            "trgCount": 0,
            "reverseTrgCount": 0,
            "lastSet": datetime.datetime(1970, 1, 1) 
        }
    }
    
    
def exportRuleList():
    global ruleList
    newRuleList = []
    for rule in ruleList:
        newRuleList.append(_exportRule(rule))
    return newRuleList
    
def _exportRule(rule):
    parsedVal = None
    cType = rule["type"]
    pld = rule["pld"]
    if cType == "timeON" or cType == "timeOFF":
        parsedVal = {
            "startH": pld["startH"],
            "startM": pld["startM"],
            "endH": pld["endH"],
            "endM": pld["endM"]
        }
    elif cType == "powInON" or cType == "powInOFF" or cType == "powDiffON" or cType == "powDiffOFF":
        parsedVal = {
            "powVal": pld["powVal"],
            "phase": pld["phase"],
            "holdFor_H": pld["holdFor_H"],
            "holdFor_M": pld["holdFor_M"]
        }
    else :
        print("=====================\n     WRONG PARM     \n=====================")
        
    return {
        "enable": rule["enable"],
        "type": cType,
        "value": parsedVal
    }

def evalRules(fullPowerList):
    global enableEvaluation, activeRule, ruleList
    if not enableEvaluation:
        return
    (rId, res) = _evalRules(fullPowerList)
    print(f"[rule result]: {rId}, {res}")
    # if rId == -1:
    #     ruleList[rId]["trigerCount"] = 0
    #     return res
    # else if 
    # ruleList[rId]["trigerCount"] += 1
    # if (ruleList[rId]["trigerCount"] == 3):
    #     activeRule = rId
    ruleList[rId]["lastTrigeTs"] = datetime.now()
    return res                  
             
def _evalRules(fullPowerList):
    global activeRule, ruleList
    for rId, rule in enumerate(ruleList):
        if not rule["enable"]:
            continue
        cType = rule["type"]
        resVal = rule["resultVal"]
        pld = rule["pld"]
        print(f"[testing rule]: {cType}, {resVal}, {pld}")
        if cType == "timeON" or cType == "timeOFF":
            if inRange(pld["startH"], pld["startM"], pld["endH"], pld["endM"]):
                return (rId, resVal)
                     
        if cType == "powInON" or cType == "powInOFF" or cType == "powDiffON" or cType == "powDiffOFF":
            minTrigetTime = datetime.now() - timedelta(minutes=pld["holdFor_M"], hours=pld["holdFor_M"])
            trgPhase = pld["phase"] -1
            inPow = fullPowerList['data'][trgPhase]["ai"]
            outPow = fullPowerList['data'][trgPhase]["ro"]
            if rId == activeRule and rule["lastTrigeTs"] != None and rule["lastTrigeTs"] > minTrigetTime:
                return (-1, resVal)
            print(f"{pld['powVal']}, {inPow}")
            if cType == "powInON":
                if pld["powVal"] > inPow:
                    return (rId, resVal)
            elif cType == "powInOFF":
                if pld["powVal"] < inPow:
                    return (rId, resVal)
            elif cType == "powDiffON":
                if pld["powVal"] > outPow:
                    return (rId, resVal)
            elif cType == "powDiffOFF":
                if pld["powVal"] < outPow:
                    return (rId, resVal)
    activeRule = -1 #TODO (bad flow)
    return (-1, False)

    
    
def inRange(startH, startM, endH, endM):
    if startH == endH and startM == endM:
        return False
    currentFull = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
    startFull = startH * 60 + startM
    endFull = endH * 60 + endM
    # if startH > endH or (startH == endH and startM > endM):
        # return True if curentH > endH or (curentH == endH and curentM > endM) or curentH < startH or (curentH == startH and curentM and) 
    if startFull > endFull:
        return True if currentFull > startFull or endFull > currentFull else False 
    return True if startFull < currentFull and currentFull < endFull else False
 