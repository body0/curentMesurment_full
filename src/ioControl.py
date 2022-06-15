import os.path
import cMesurment

BOILER_GPIO_ID = 17

curentBoilerState = False


def getBoilerState():
    global curentBoilerState
    return curentBoilerState

def setBoilerState(targetState):
    global curentBoilerState
    # logger.log(f'boiler set to: {targetState}')
    writeGPIO(BOILER_GPIO_ID, not targetState)
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
        #print(f"/sys/class/gpio/gpio{portID}/value")
        file.write('1' if value else '0')



def mesure():
    print('START mesurment')
    #phaseList = mesureAllPhase()
    phaseList = cMesurment.getPhaseList()
    
    for i in range(len(phaseList)):
        phaseList[i]["curent_chA"] = parseValuesInList(phaseList[i]["curent_chA"])
        phaseList[i]["curent_chB"] = parseValuesInList(phaseList[i]["curent_chB"])
        phaseList[i]["voltage"] = parseValuesInList(phaseList[i]["voltage"])
        phaseList[i]["diffTime"] = phaseList[i]["eTime"] - phaseList[i]["sTime"]

    print(f"# EXEC TIME: {phaseList[0]['diffTime']}; {phaseList[1]['diffTime']}; {phaseList[2]['diffTime']}; ({phaseList[i]['sCount']})")
    
        
    print('END mesurment')
    return phaseList

# INIT
setBoilerState(curentBoilerState)