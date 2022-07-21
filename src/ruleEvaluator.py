import datetime

ruleList = []
activeRule = -1
enableEvaluation = False


def setEnableEvaluation(newVal):
    global activeRule, enableEvaluation
    if enableEvaluation != newVal:
         activeRule = -1
    enableEvaluation = newVal
    
def getEnableEvaluetion():
    return enableEvaluation

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
            "holdFor_H": pld["holdFor_H"],
            "holdFor_M": pld["holdFor_M"]
        }
    else :
        print("=====================\n     WRONG PARM      \n=====================")
        return
    return {
        "enable": rule["enable"],
        "type": cType,
        "pld": parsedVal,
        "resultVal": negate,
        "lastTrigeTs": None,
        "trigerCount": 0
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
            "holdFor_H": pld["holdFor_H"],
            "holdFor_M": pld["holdFor_M"]
        }
    else :
        print("=====================\n     WRONG PARM      \n=====================")
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
    print(rId, res)
    if rId == -1:
        return res
    activeRule = rId
    ruleList[rId]["trigerCount"] += 1
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
        print(cType, resVal, pld)
        if cType == "timeON" or cType == "timeOFF":
            if inRange(pld["startH"], pld["startM"], pld["endH"], pld["endM"]):
                return (rId, resVal)
                     
        if cType == "powInON" or cType == "powInOFF" or cType == "powDiffON" or cType == " ":
            minTrigetTime = datetime.now() - datetime.timedelta(minutes=pld["holdFor_M"], hours=pld["holdFor_M"])
            inPow = fullPowerList[0]
            outPow = fullPowerList[1]
            diff = inPow - outPow
            if rId == activeRule and  rule["lastTrigeTs"] != None and rule["lastTrigeTs"] > minTrigetTime:
                return (-1, resVal)
            if cType == "powInON":
                if pld["powVal"] < inPow:
                    return (rId, resVal)
            elif cType == "powInOFF":
                if pld["powVal"] > inPow:
                    return (rId, resVal)
            elif cType == "powDiffON":
                if pld["powVal"] < diff:
                    return (rId, resVal)
            elif cType == "powDiffOFF":
                if pld["powVal"] > diff:
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
 