import numpy as np
from scipy import optimize
import math


def genBatch(phaseList):
    batch = []
    for phaseId in range(len(phaseList)):
        batch.append([])
        ph = phaseList[phaseId]
        for i in range(ph['sCount']):
            batch[phaseId].append([ph['curent_chA'][i], ph['curent_chB'][i], ph['voltage'][i]])
    return batch
        
 # SHIFT START
def getSin(x, y):
    def test_func(x, a, b, c):
        return a * np.sin(((b * x) - c) * 2*math.pi)
    
    # !!! CONSTANT AMPLITUDE !!!
    maxVolt = 0 
    for i, val in enumerate(y):
        if val > maxVolt:
            maxVolt = val
            
    def partial_fun(x, b, c):
        return test_func(x, maxVolt, b, c)
            
    frequencyGuess = 1/20
    phaseShift = 0
    params, params_covariance = optimize.curve_fit(partial_fun, x, y, p0=[frequencyGuess, phaseShift], maxfev=5000)
    #x_sin = x
    #y_sin = [test_func(x, maxVolt, frequencyGuess, phaseShift) for x in x_sin]
    x_sin = np.linspace(0,x[-1],len(x))
    y_sin = [partial_fun(x, params[0], params[1]) for x in x_sin]
    return [x_sin, y_sin, params]


def getShiftedBatch(batch):

    """ 
    #batch(Phase list) (len 3):
    [
        #phase (len cca. 100):
        [
            [inCur, outCur, voltage]
        ]
    ]
    """
    #PHASE_V_SHIFT = [0, 0, 0]
    PHASE_V_SHIFT = [0.333333333, -0.333333333, 0]
    #PHASE_V_SHIFT = [-0.333333333, 0.333333333, 0]
    shiftedBatch = [[],[],[]]
    for phaseId, phase in enumerate(batch):
        
        x = []
        v_y = []
        for i, val in enumerate(phase):
            x.append(i)
            v_y.append(val[2])
            
        voltageSinData = getSin(x, v_y)
        period = 1/voltageSinData[2][0]
        phaseShift = (voltageSinData[2][1])%1
        alingStartSkip = round(period*phaseShift)
        
        loadTimeShift = 0 #1/period/3
        cShift = PHASE_V_SHIFT[phaseId] if PHASE_V_SHIFT[phaseId] < phaseShift else 1-PHASE_V_SHIFT[phaseId]
        cRelativeSkip = period*cShift
        cRelativeSkipRound = math.floor(cRelativeSkip)
        cRelativeSkipPart = cRelativeSkip%1
        alingEndSkip = min(len(phase), len(phase) - cRelativeSkipRound) -1
        
        for i in range(alingStartSkip, alingEndSkip):
            c = phase[i+cRelativeSkipRound]
            n = phase[i+cRelativeSkipRound + 1]
            cA = c[0] + (n[0] - c[0]) *(cRelativeSkipPart-loadTimeShift)
            cB = c[1] + (n[1] - c[1]) *(cRelativeSkipPart-2*loadTimeShift)
            d=[cA, cB, phase[i][2]]
            shiftedBatch[phaseId].append(d)
    return shiftedBatch

def getMax(arr):
    mx = arr[0] 
    for i, val in enumerate(arr):
        if val > mx:
            mx = val
    return mx

def getAvrg(arr):
    sm = 0 
    for i, val in enumerate(arr):
        sm += val
    return sm/len(arr)

def getAvrgPower(shiftedBatch):
    ret = []
    for phaseId, phase in enumerate(shiftedBatch):
        powA = []
        powB = []
        cA = []
        cB = []
        v = []
        for i, val in enumerate(phase):
            print(val)
            powA.append(val[0] * val[2])
            powB.append(val[1] * val[2])
        ret.append([getAvrg(powA), getAvrg(powB)])
    return ret

def scaleBatchToReal(batch):
    for phase in batch:
        for i, val in enumerate(phase):
            phase[i][0] = val[0] / 0x800 * 4.12
            phase[i][1] = val[1] / 0x800 * 4.12
            phase[i][2] = val[2] * 0.282069314

def scaleBatch(batch):
    for phase in batch:
        for i, val in enumerate(phase):
            phase[i][0] = val[0] / 0x800 * 4.12
            phase[i][1] = val[1] / 0x800 * 4.12
            phase[i][2] = val[2] * 0.0008671875
            