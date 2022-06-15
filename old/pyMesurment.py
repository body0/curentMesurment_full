from smbus2 import SMBus, i2c_msg
import math
import time


SAMPLE_COUNT = 100

VOLTAGE_CONFIG = [0x00, 0xA0]
#VOLTAGE_CONFIG = [0x04, 0xA0]
CURENT_CONFIG_01 = [0x08, 0xE3]
CURENT_CONFIG_23 = [0x38, 0xE3]
NULL_CONFIG = [0x1, 0x83]
curBus = SMBus(0)
voltBus = SMBus(1)


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

def mesurePhase_PY(addr_A, addr_B):
    curent_chA = [None] * SAMPLE_COUNT
    curent_chB = [None] * SAMPLE_COUNT
    voltage = [None] * SAMPLE_COUNT
    
    # NO VOLTAGE CONFIG
    curBus.write_i2c_block_data(addr_A, 1, CURENT_CONFIG_01)
    curBus.write_i2c_block_data(addr_B, 1, CURENT_CONFIG_23)
    time.sleep(0.005)
    startTime = math.floor(time.time() * 1000)
    for i in range(SAMPLE_COUNT):
        curent_chA[i] = curBus.read_i2c_block_data(addr_A, 0, 2)
        curent_chB[i] = curBus.read_i2c_block_data(addr_B, 0, 2)
        voltage[i] = voltBus.read_i2c_block_data(0x48, 0, 2)
    endTime = math.floor(time.time() * 1000)
    return {
      "curent_chA": curent_chA,
      "curent_chB": curent_chB,
      "voltage": voltage,
      "sTime": startTime,
      "eTime": endTime,
    }

def mesureAllPhase_PY():
    phaseList = [None,None,None]

    voltBus.write_i2c_block_data(0x48, 1, VOLTAGE_CONFIG)
    # 0x4b 0x48 0x49
    phaseList[0]= mesurePhase(0x4b, 0x49) # SWITCHED!!
    phaseList[1]= mesurePhase(0x48, 0x4b) # SWITCHED!!
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

