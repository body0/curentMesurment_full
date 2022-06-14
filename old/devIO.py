from smbus2 import SMBus, i2c_msg
import time
import os.path
# import logger

BOILER_GPIO_ID = 17
SAMPLE_COUNT = 80

curentBoilerState = False
bus = SMBus(1)


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
    mesurmentList = [None, None, None, None, None, None]
    for i in range(len(mesurmentList)):
        mesurmentList[i] = [None] * SAMPLE_COUNT

    bus.write_i2c_block_data(72, 1, [0x08, 0xE3])
    bus.write_i2c_block_data(73, 1, [0x08, 0xE3])
    time.sleep(0.001)
    startTime_A = time.time()
    for i in range(SAMPLE_COUNT):
        msg = bus.read_i2c_block_data(72, 0, 2)
        mesurmentList[0][i] = msg
        msg = bus.read_i2c_block_data(73, 0, 2)
        mesurmentList[1][i] = msg
    endTime_A = time.time()

    bus.write_i2c_block_data(72, 1, [0x38, 0xE3])
    bus.write_i2c_block_data(73, 1, [0x38, 0xE3])
    time.sleep(0.001)
    startTime_B = time.time()
    for i in range(SAMPLE_COUNT):
        msg = bus.read_i2c_block_data(72, 0, 2)
        mesurmentList[2][i] = msg
        msg = bus.read_i2c_block_data(73, 0, 2)
        mesurmentList[3][i] = msg
    endTime_B = time.time()

    bus.write_i2c_block_data(72, 1, [0x1, 0x83]) #?
    bus.write_i2c_block_data(73, 1, [0x1, 0x83]) #?

    print(f'# EXEC TIME: {endTime_A - startTime_A}; {endTime_B - startTime_B}')
    ret = [[], [], [], [], [], []]
    for i in range(len(mesurmentList)):
        if mesurmentList[i][0] == None:
            continue
        for j in range(len(mesurmentList[i])):
            num = (mesurmentList[i][j][0] << 8) | mesurmentList[i][j][1]
            shiftedNum = num >> 4
            signNum = shiftedNum
            if (signNum > 0x07FF):
                signNum = signNum - 0x1000

            ret[i].append(signNum)
        
    print('END mesurment')
    return ret

# INIT
setBoilerState(curentBoilerState)