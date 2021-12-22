from smbus2 import SMBus, i2c_msg
import time
import os.path
import cMesurment
# import logger

BOILER_GPIO_ID = 17
SAMPLE_COUNT = 80

VOLTAGE_CONFIG = [0x00, 0xA0]
#VOLTAGE_CONFIG = [0x04, 0xA0]
CURENT_CONFIG_01 = [0x08, 0xE3]
CURENT_CONFIG_23 = [0x38, 0xE3]
NULL_CONFIG = [0x1, 0x83]

curentBoilerState = False
curBus = SMBus(1)
voltBus = SMBus(0)

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


def parseValuesInList(valList):
    ret = []
    for num in valList:
        shiftedNum = num >> 4
        signNum = shiftedNum
        if (signNum > 0x07FF):
            signNum = signNum - 0x1000
        ret.append(signNum)
    return ret
 
def preProcesPhase(valList): 
    ret = []
    for j in range(len(valList)):
        num = (valList[j][0] << 8) | valList[j][1]
        ret.append(num)
    return ret

""" 
https://www.ti.com/lit/ds/symlink/ads1015.pdf?ts=1637486256575&ref_url=https%253A%252F%252Fwww.google.com%252F

49; vcc; C; A
48; gnd; B; C
4b; scl; A; B

 """   

def mesurePhase(addr_A, addr_B):
    curent_chA = [None] * SAMPLE_COUNT
    curent_chB = [None] * SAMPLE_COUNT
    voltage = [None] * SAMPLE_COUNT
    
    # NO VOLTAGE CONFIG
    curBus.write_i2c_block_data(addr_A, 1, CURENT_CONFIG_01)
    curBus.write_i2c_block_data(addr_B, 1, CURENT_CONFIG_23)
    time.sleep(0.005)
    startTime = time.time()
    for i in range(SAMPLE_COUNT):
        curent_chA[i] = curBus.read_i2c_block_data(addr_A, 0, 2)
        curent_chB[i] = curBus.read_i2c_block_data(addr_B, 0, 2)
        voltage[i] = voltBus.read_i2c_block_data(0x48, 0, 2)
    endTime = time.time()
    return {
      "curent_chA": curent_chA,
      "curent_chB": curent_chB,
      "voltage": voltage,
      "sTime": startTime,
      "eTime": endTime,
    }

def mesureAllPhase():
    phaseList = [None,None,None]

    voltBus.write_i2c_block_data(0x48, 1, VOLTAGE_CONFIG)
    phaseList[1]= mesurePhase(0x4b, 0x49) # SWITCHED!!
    phaseList[0]= mesurePhase(0x48, 0x4b) # SWITCHED!!
    phaseList[2]= mesurePhase(0x49, 0x48)

    curBus.write_i2c_block_data(0x48, 1, NULL_CONFIG)
    curBus.write_i2c_block_data(0x49, 1, NULL_CONFIG)
    curBus.write_i2c_block_data(0x4b, 1, NULL_CONFIG)
    
    for i in range(len(phaseList)):
        phaseList[i]["curent_chA"] = preProcesPhase(phaseList[i]["curent_chA"])
        phaseList[i]["curent_chB"] = preProcesPhase(phaseList[i]["curent_chB"])
        phaseList[i]["voltage"] = preProcesPhase(phaseList[i]["voltage"])
        phaseList[i]["sCount"] = SAMPLE_COUNT
    
    return phaseList

def mesure():
    print('START mesurment')
    phaseList = mesureAllPhase()
    #phaseList = cMesurment.getPhaseList()
    
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