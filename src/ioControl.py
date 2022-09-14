import os.path
import cMesurment
import envVar



curentBoilerState = False


def getBoilerState():
    global curentBoilerState
    return curentBoilerState

def setBoilerState(targetState):
    global curentBoilerState
    writeGPIO(envVar.BOILER_GPIO_ID, not targetState)
    curentBoilerState = targetState

def setGPIO(portID):
    with open("/sys/class/gpio/export", 'w') as file:
        file.write(str(portID))
    with open(f"/sys/class/gpio/gpio{portID}/direction", 'w') as file:
        file.write("out")

def writeGPIO(portID, value):
    if not os.path.isdir(f"/sys/class/gpio/gpio{portID}"):
       setGPIO(portID) 
    with open(f"/sys/class/gpio/gpio{portID}/value", 'w') as file:
        file.write('1' if value else '0')



def parseValuesInList(valList):
    ret = []
    for pair in valList:
        shiftedNum = pair >> 4
        signNum = shiftedNum
        if (signNum > 0x07FF):
            signNum = signNum - 0x1000
        ret.append(signNum)
    return ret
 
def mesure():
    print('START mesurment')
    #phaseList = mesureAllPhase()
    phaseList = cMesurment.getPhaseList(envVar.DATA_POINT_TAKEN)
    
    for i in range(len(phaseList)):
        phaseList[i]["ci"] = parseValuesInList(phaseList[i]["ci"])
        phaseList[i]["co"] = parseValuesInList(phaseList[i]["co"])
        phaseList[i]["vv"] = parseValuesInList(phaseList[i]["vv"])
        phaseList[i]["diffTime"] = phaseList[i]["eTime"] - phaseList[i]["sTime"]

    print(f"# EXEC TIME: {phaseList[0]['diffTime']}; {phaseList[1]['diffTime']}; {phaseList[2]['diffTime']}; ({phaseList[i]['sCount']})")
    
    # print('END mesurment')
    return phaseList

# INIT
setBoilerState(curentBoilerState)