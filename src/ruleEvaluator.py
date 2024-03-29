from datetime import datetime, timedelta
from enum import Enum
import ioControl, autoCP


class WallbocWalOperation(Enum):
    FIXED = 1
    LESS_THAN_DIFF_MIN = 2

class TargetType(Enum):
    BOILER_SWITCH = "boiler"
    WALLBOX_SWITCH = "wallbox"
    WALLBOX_VAL = "wallbox_set"
    
class CheckType(Enum):
    # TIME = "time"
    # TARGET_VAL = "pow_diff"
    POW_IN = "pow_in"
    # POW_OUT = "pow_out"
    POW_DIFF = "pow_diff"
    DEF = "def"
    

    
class ConfigNode:
    # def __init__(self, target: TargetType, value: int, check: CheckType, checkParam, checkToTrig = 1):
        # ConfigNode(rule["target"], rule["value"], rule["check"], rule["checkParam"], 1 if rule["check"]==CheckType.DEF else rule["checkToTrig"])
    def __init__(self, rule):
        self.target = rule["target"]
        self.value = rule["value"]
        self.check = rule["check"]
        self.checkParam = rule["checkParam"]
        self.checkToTrig =  rule["checkToTrig"] if "checkToTrig" in rule else 1
        self.checkCount =  0
        self.lastTrig = datetime.datetime(1970, 1, 1) 
        self.trigCount = 0
        self.enable = True
        
    def toDic(self):
        return {
            "target": self.target,
            "value": self.value,
            "check": self.check,
            "checkParam": self.checkParam,
            # "lastTrig": self.target
        }
    

ruleList = []

nextTrigEnable = {
    TargetType.BOILER_SWITCH:  datetime.datetime(1970, 1, 1), 
    TargetType.WALLBOX_SWITCH:  datetime.datetime(1970, 1, 1), 
    TargetType.WALLBOX_VAL:  datetime.datetime(1970, 1, 1), 
}
trigEnable = {
    TargetType.BOILER_SWITCH: False, 
    TargetType.WALLBOX_SWITCH: False, 
    TargetType.WALLBOX_VAL: False, 
}
trigDelta = {
    TargetType.BOILER_SWITCH: timedelta(minutes=1),
    TargetType.WALLBOX_SWITCH: timedelta(minutes=5),
    TargetType.WALLBOX_VAL: timedelta(seconds=30), 
}

def setBoilerEnable(value):
    # nextTrigEnable[TargetType.BOILER_SWITCH] = datetime.datetime(1970, 1, 1)
    trigEnable[TargetType.BOILER_SWITCH] = value
    for rule in ruleList:
        if rule["target"] == TargetType.BOILER_SWITCH:
            rule["checkCount"] = 0
            
    
def setWallboxEnable(value):
    # nextTrigEnable[TargetType.WALLBOX_SWITCH] = datetime.datetime(1970, 1, 1)
    # nextTrigEnable[TargetType.WALLBOX_VAL] = datetime.datetime(1970, 1, 1)
    trigEnable[TargetType.WALLBOX_SWITCH] = value
    trigEnable[TargetType.WALLBOX_VAL] = value
    for rule in ruleList:
        if rule["target"] == TargetType.WALLBOX_SWITCH or rule["target"] == TargetType.WALLBOX_VAL:
            rule["checkCount"] = 0

def getBoilerExable():
    return trigEnable[TargetType.BOILER_SWITCH]

def setRuleLis(newList):
    global ruleList
    newRuleList = []
    for rule in newList:
        newRuleList.append(ConfigNode(rule))
    ruleList = newRuleList

# def setEvalEnable(target, val):
#     global ruleList
#     for rule in ruleList:
#         if (target == rule.target): rule.enable = val
    
def exportRuleList():
    global ruleList
    newRuleList = []
    for rule in ruleList:
        newRuleList.append(rule.toDic())
    return newRuleList


def evalRules(fullPowerList):
    global ruleList, nextTrigEnable, trigEnable, trigDelta
    now = datetime.now()
    powIn = [fullPowerList['data'][i]['ri'] for i in range(3)] + [fullPowerList['ri']]
    powDif = [fullPowerList['data'][i]['ro'] for i in range(3)] + [fullPowerList['ro']]
    for rule in ruleList:
        target = rule.target
        check = rule.check
        checkParam = rule.checkParam
        if (not trigEnable[target] or nextTrigEnable[target] < now or not rule.enable): continue
        print('=================')
        print(powDif)
        print(powIn)
        print(rule)
        if((
            (TargetType.BOILER_SWITCH == target or TargetType.WALLBOX_SWITCH == target) and (
                (CheckType.POW_DIFF == check and checkParam['less'] and powDif[checkParam['phase']] > checkParam['power']) or
                (CheckType.POW_DIFF == check and not checkParam['less'] and powDif[checkParam['phase']] < checkParam['power']) or
                (CheckType.POW_IN == check and checkParam['less'] and powIn[checkParam['phase']] > checkParam['power']) or
                (CheckType.POW_IN == check and not checkParam['less'] and powIn[checkParam['phase']] < checkParam['power']) ))or
            CheckType.DEF == check):
            # todo, incrementd
            value = rule.value
            if (TargetType.BOILER_SWITCH == target):
                ioControl.setBoilerState(value)
            elif (TargetType.WALLBOX_SWITCH == target):
                autoCP.setState(value)
            elif (TargetType.WALLBOX_VAL == target):
                trgPow = 0
                if (value[0] == WallbocWalOperation.FIXED):
                    trgPow = value[1]
                elif (value[0] == WallbocWalOperation.LESS_THAN_DIFF_MIN):
                    trgPow = -min(powDif[0], powDif[1], powDif[2]) -value[1]
                autoCP.setPower(trgPow)
            nextTrigEnable[target] = datetime.now() + trigDelta[target]
            rule["lastTrig"] = datetime.now()
            rule["checkCount"] = 0
            rule["trigCount"] += 1
            return True
    return False
    
def inRange(startH, startM, endH, endM):
    if startH == endH and startM == endM:
        return False
    currentFull = datetime.now().hour * 60 + datetime.now().minute
    startFull = startH * 60 + startM
    endFull = endH * 60 + endM
    # if startH > endH or (startH == endH and startM > endM):
        # return True if curentH > endH or (curentH == endH and curentM > endM) or curentH < startH or (curentH == startH and curentM and) 
    if startFull > endFull:
        return True if currentFull > startFull or endFull > currentFull else False 
    return True if startFull < currentFull and currentFull < endFull else False
 