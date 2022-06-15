import datetime

ruleList = []
activeRule = False
enableEvaluation = False


def setEnableEvaluation(newVal):
    global activeRule
    if enableEvaluation == newVal:
         activeRule = False
    enableEvaluation = newVal
    
def getEnableEvaluetion():
    return enableEvaluation

def setRuleLis(newList):
    global ruleList, activeRule
    activeRule = False
    newRuleList = []
    for rule in newList:
        newRuleList.append(_parseRule(rule))
    ruleList = newRuleList
    
def _parseRule(rule):
    parsedVal = None
    cType = rule["type"]
    pld = rule["val"]
    negate = bool(cType == "timeOFF" or cType == "powInOFF" or cType == "powDiffOFF")
    if cType == "timeON" or cType == "timeOFF":
        val = {
            "startH": pld["startH"],
            "startM": pld["startM"],
            "endH": pld["endH"],
            "endM": pld["endM"]
        }
    elif cType == "powInON" or cType == "powInOFF" or cType == "powDiffON" or cType == "powDiffOFF":
        val = {
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
        return {
            "startH": pld["startH"],
            "startM": pld["startM"],
            "endH": pld["endH"],
            "endM": pld["endM"]
        }
    elif cType == "powInON" or cType == "powInOFF" or cType == "powDiffON" or cType == "powDiffOFF":
        return {
            "powVal": pld["powVal"],
            "holdFor_H": pld["holdFor_H"],
            "holdFor_M": pld["holdFor_M"]
        }
    else :
        print("=====================\n     WRONG PARM      \n=====================")
    return {
        "enable": rule["enable"],
        "type": cType,
        "val": parsedVal
    }

def evalRules(fullPowerList):
    global enableEvaluation, activeRule, ruleList
    if not enableEvaluation:
        return
    (rId, res) = evalRules(fullPowerList)
    if rId == -1:
        return res
    activeRule = rId
    ruleList[rId]["trigerCount"] += 1
    ruleList[rId]["lastTrigeTs"] = datetime.now()
    return res                  
             
def evalRules(fullPowerList):
    global activeRule, ruleList
    inPow = fullPowerList[1][0]
    outPow = fullPowerList[1][1]
    diff = inPow - outPow
    for rId, rule in enumerate(ruleList):
        if not rule["enable"]:
            continue
        cType = rule["type"]
        resVal = rule["resultVal"]
        if cType == "timeON" or cType == "timeOFF":
            if inRange(rule["val"]["startH"], rule["val"]["startM"], rule["val"]["endH"], rule["val"]["endM"]):
                return (rId, resVal)
                     
        if cType == "powInON" or cType == "powInOFF" or cType == "powDiffON" or cType == "powDiffOFF":
            minTrigetTime = datetime.now() - datetime.timedelta(minutes=rule["val"]["holdFor_M"], hours=rule["val"]["holdFor_M"])
            if rId == activeRule and  rule["lastTrigeTs"] != None and rule["lastTrigeTs"] > minTrigetTime:
                return (-1, resVal)
            if cType == "powInON":
                if rule["val"]["powVal"] < inPow:
                    return (rId, resVal)
            elif cType == "powInOFF":
                if rule["val"]["powVal"] > inPow:
                    return (rId, resVal)
            elif cType == "powDiffON":
                if rule["val"]["powVal"] < diff:
                    return (rId, resVal)
            elif cType == "powDiffOFF":
                if rule["val"]["powVal"] > diff:
                    return (rId, resVal)
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
 