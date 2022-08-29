from scipy import optimize
import math
import numpy as np
import copy

PKEY = ["ci", "co", "vv", "ti", "to", "tv"]

def parseData(path):
    f = open(path, "r")
    data = []
    while True:
        line = f.readline()
        if len(line) == 0: 
            break
        if line[0] == '#':
            pass
            # print(line, end="")
        elif line[0] == '>':
            splitByBatchId = line[1:].split('|')
            indexBatch = int(splitByBatchId[0]) 
            splitByPhaseId = splitByBatchId[1].split('=')
            indexPhase = int(splitByPhaseId[0])
            pData = splitByPhaseId[1].split(',')
            
            while indexBatch > (len(data) -1):
                data.append([])
            while  indexPhase > (len(data[indexBatch]) -1):
                data[indexBatch].append({
                    "ci":[],
                    "co":[],
                    "vv":[],
                    "ti":[],
                    "to":[],
                    "tv":[]
                })
            phase = data[indexBatch][indexPhase]
            phase["ci"].append(float(pData[0]))
            phase["co"].append(float(pData[1]))
            phase["vv"].append(float(pData[2]))
            phase["ti"].append(float(pData[3]))
            phase["to"].append(float(pData[4]))
            phase["tv"].append(float(pData[5]))

    return data

def scaleData(data):
    for batch in data:
        for phase in batch:
            phase["ci"] = list(map(lambda a: a / 0x800 * 25.125, phase["ci"]))
            phase["co"] = list(map(lambda a: a / 0x800 * 25.125, phase["co"]))
            phase["vv"] = list(map(lambda a: a * 0.0008671875, phase["vv"]))

def shiftTimeData(data):
    for batch in data:
        for phase in batch:
            minStartVal = min(phase["ti"][0], phase["to"][0], phase["tv"][0])
            phase["ti"] = list(map(lambda a: a - minStartVal, phase["ti"]))
            phase["to"] = list(map(lambda a: a - minStartVal, phase["to"]))
            phase["tv"] = list(map(lambda a: a - minStartVal, phase["tv"]))
    
                
def cutHead(data, sufixLen):
    for batch in data:
        for phase in batch:
            for vk in PKEY:
                phase[vk]=phase[vk][sufixLen:]                

def cutTail(data, prefixLen):
    for batch in data:
        for phase in batch:
            for vk in PKEY:
                phase[vk]=phase[vk][:-1*prefixLen]  
                
def getMax(arr):
    mx = arr[0] 
    for i, val in enumerate(arr):
        if val > mx:
            mx = val
    return mx

def getMaxAbs(arr):
    mx = abs(arr[0]) 
    for i, val in enumerate(arr):
        valAbs = abs(val)
        if valAbs > mx:
            mx = valAbs
    return mx

def getAvrg(arr):
    return sum(arr)/len(arr)

def getSRM(arr):
    s = 0
    for val in arr:
        s += val * val
    return math.sqrt(s/len(arr))

def getAvrgAbs(arr):
    sm = 0 
    for i, val in enumerate(arr):
        sm += abs(val)
    if (sm == 0):
        return 0
    return sm/len(arr) 

def getDiffList(arr):
    lastval = arr[0]
    difArr = []
    for val in arr:
        difArr.append(val-lastval)
        lastval = val
    return difArr

def getWeightList(arr):
    difArr = [(arr[1]-arr[0])]
    for i in range(1, len(arr)-1):
        difArr.append((arr[i+1]-arr[i-1])/2)
    difArr.append((arr[-1]-arr[-2]))
    return difArr
    
def getWeightedAvrgAbs(arr, weight):
    wSum = 0
    for i in range(len(arr)):
        wSum += abs(arr[i]) * weight[i]
    return wSum / sum(weight)

def getWeightedAvrg(arr, weight):
    wSum = 0
    for i in range(len(arr)):
        wSum += arr[i] * weight[i]
    return wSum / sum(weight)

def sliceArrPair(x, y, start, end):
    skipS = len(list(filter(lambda a: a < start, x)))
    skipE = len(x) - len(list(filter(lambda a: a > end, x)))
    nX = x[skipS:skipE]
    nY = y[skipS:skipE]
    return (nX, nY)

def getLinExivalent(x1, x2, y1, y2):
    a = (y2 - y1) / (x2 - x1)
    b = y2 - (a*x2) 
    return (a, b)

def guessValueAsLinear(xArr, yArr, x):
    trgI = np.searchsorted(xArr, x, side='left')
    la, lb = getLinExivalent(xArr[trgI-1], xArr[trgI], yArr[trgI-1], yArr[trgI])
    return la*x + lb

def sin_fun(x, b, c):
    return np.sin(((b * x) - c) * 2*math.pi)

def getPower(cX, cY, freq, shift, x):
#     trgI = np.searchsorted(cX, x, side='left')
#     la, lb = getLinExivalent(cX[trgI-1], cX[trgI], cY[trgI-1], cY[trgI]) #safe
#     return pow_fun(freq, shift, la, lb, x)
    return sin_fun(x, freq, shift) * guessValueAsLinear(cX, cY, x)

def pow_fun(freq, shift, a, b, x):
    return np.sin((freq*x - shift) * 2*math.pi)*(a*x+b)

def powI_fun(freq, shift, a, b, x):
    pi = math.pi
    sp = 2*pi*(freq*x+shift)
    return (a * np.sin(sp) - 2*pi*freq(a*x+b)*np.cos(sp)) / 4*pi*pi*freq*freq

def getExactSlice(xArr, yArr, start, end):
    sI = np.searchsorted(xArr, start)
    eI = np.searchsorted(xArr, end)
    sV = guessValueAsLinear(xArr, yArr, start)
    eV = guessValueAsLinear(xArr, yArr, end)
    return ([start, *(xArr[sI:eI]), end], [sV, *(yArr[sI:eI]), eV])

def getSinEquivalent(x, y):       
    cross = []
    for i in range(len(y) -1):
        if (y[i] * y[i+1] < 0):
            pSum = abs(y[i]) + abs(y[i+1])
            nVal = x[i]*(abs(y[i+1])/pSum) + x[i+1]*(abs(y[i])/pSum)
            cross.append(nVal)
            
    spaceBetweanCross = getDiffList(cross)[1:]
    frequencyGuess = 0.5 / getAvrg(spaceBetweanCross)
    phaseShift = 0
    params, params_covariance = optimize.curve_fit(sin_fun, x, y, p0=[frequencyGuess, phaseShift], maxfev=500000)
    x_sin = np.linspace(0,x[-1],len(x)*4)
    y_sin = [sin_fun(x, params[0], params[1]) for x in x_sin]
    return [x_sin, y_sin, params, cross, sin_fun]


""" ====================================================================================================================================================== """


def shiftData(bl):
    PHASE_V_SHIFT = [0.333333333, -0.333333333, 0]

    sbl = []
    for batchId, batch in enumerate(bl):
        sbl.append([])
        print(f"({batchId})")
        for phaseId, phase in enumerate(batch):
            phase = bl[batchId][phaseId]
            sbl[batchId].append({
                "ci":phase["ci"],
                "co":phase["co"],
                "vv":phase["vv"],
                "ti":[],
                "to":[],
                "tv":[],
                "cross_zero": [],
                "sinFun": None,
                "meta": {}
            })
            sPhase = sbl[batchId][-1]
            
            voltageSinData = getSinEquivalent( phase["tv"], phase["vv"])
            x_sin = voltageSinData[0]
            y_sin = voltageSinData[1]
            simParam=voltageSinData[2]
            cross=voltageSinData[3]
            period = 1/simParam[0]
            baseShift = simParam[1]
            cShift = PHASE_V_SHIFT[phaseId]
            cFullShift = cShift*period
            
            startXVal = cross[2]
            endXVal = cross[-3]       
#             endXVal = cross[-3 if len(cross)%2 == 0 else -4]       
                
            sPhase["ti"] = list(map(lambda a: a + cFullShift, phase["ti"]))
            inSkip_s = len(list(filter(lambda a: a < startXVal, sPhase["ti"])))
            inSkip_e = len(sPhase["ti"]) - len(list(filter(lambda a: a > endXVal, sPhase["ti"])))
            
            sPhase["to"] = list(map(lambda a: a + cFullShift, phase["to"]))
            outSkip_s = len(list(filter(lambda a: a < startXVal, sPhase["to"])))
            outSkip_e = len(sPhase["to"]) - len(list(filter(lambda a: a > endXVal, sPhase["to"])))
            
            sPhase["tv"] = list(map(lambda a: a, phase["tv"]))
            vSkip_s = len(list(filter(lambda a: a < startXVal, sPhase["tv"])))
            vSkip_e = len(sPhase["tv"]) - len(list(filter(lambda a: a > endXVal, sPhase["tv"])))
                    
            inSkip_s-=1
            inSkip_e+=1
            outSkip_s-=1
            outSkip_e+=1
            
            sPhase["ci"] = sPhase["ci"][inSkip_s:inSkip_e]
            sPhase["ti"] = sPhase["ti"][inSkip_s:inSkip_e]
            sPhase["co"] = sPhase["co"][outSkip_s:outSkip_e]
            sPhase["to"] = sPhase["to"][outSkip_s:outSkip_e]       
            sPhase["vv"] = sPhase["vv"][vSkip_s:vSkip_e]
            sPhase["tv"] = sPhase["tv"][vSkip_s:vSkip_e]
            print(f"RANGE: {inSkip_s} {inSkip_e} | {outSkip_s} {outSkip_e} | {vSkip_s} {vSkip_e} \t LEN: {len(sPhase['ti'])} {len(sPhase['to'])} {len(sPhase['tv'])} \t ({startXVal}-{endXVal})")
            
            sPhase["meta"] = {
                "min_time": min(sPhase["tv"][0], sPhase["ti"][0], sPhase["to"][0]),
                "max_time": max(sPhase["tv"][-1], sPhase["ti"][-1], sPhase["to"][-1]),
                "period": period,
                "shift": baseShift,
                "perLen": len(cross) / 4 -1
            }
                
            phase["sin_x"] = x_sin
            phase["sin_y"] = y_sin
            phase["cross_zero"] = cross
            phase["meta"] = {
                "min_time": 0,
                "max_time": max(phase["tv"][-1], phase["ti"][-1], phase["to"][-1]),
                "period": period,
                "shift": baseShift,
                "perLen": len(cross) / 4
            }
    return sbl 

        
            
def getPhasePow(sPhase):    
    shift = sPhase['meta']['shift']
    period = sPhase['meta']['period']
    freq = 1/period
    startX = sPhase["tv"][0]
    endX = startX + math.floor(sPhase['meta']['perLen']) * period
#     startX = (math.ceil(sPhase["tv"][0]*freq - shift)+shift)*period
#     endX = startX + period

    x_pow = np.linspace(sPhase["tv"][0], sPhase["tv"][-1], len(sPhase["tv"])*4)
#     x_pow = np.linspace(startX, endX, len(sPhase["tv"])*16)
    i_cur = [guessValueAsLinear(sPhase["ti"], sPhase["ci"], x) for x in x_pow]
    o_cur = [guessValueAsLinear(sPhase["to"], sPhase["co"], x) for x in x_pow]
    i_Pow = [getPower(sPhase["ti"], sPhase["ci"], freq, shift, x) * 1.414 for x in x_pow]
    o_Pow = [getPower(sPhase["to"], sPhase["co"], freq, shift, x) * 1.414 for x in x_pow]
        
#     tiSlice, ciSlice = getExactSlice(sPhase['ti'], sPhase['ci'], startX, endX)
#     toSlice, coSlice = getExactSlice(sPhase['to'], sPhase['co'], startX, endX)
#     iAvrgPow = getWeightedAvrgAbs(ciSlice, getWeightList(tiSlice)) * 230
#     oAvrgPow = getWeightedAvrgAbs(coSlice, getWeightList(toSlice)) * 230

    iAvrgPow = getSRM(i_cur) * 230
    oAvrgPow = getSRM(o_cur) * 230
    iRealPow = getAvrg(i_Pow) * 230
    oRealPow = getAvrg(o_Pow) * 230
    iPowFactor = iRealPow / iAvrgPow if iAvrgPow != 0 else 0 
    oPowFactor = oRealPow / oAvrgPow if oAvrgPow != 0 else 0

    # print(f"Avr: {iAvrgPow:0.3f} {oAvrgPow:0.3f}\treal: {iRealPow:0.3f} {oRealPow:0.3f}\tfact: {iPowFactor:0.4f} {oPowFactor:0.4f}")
    # print(f"Avr_c: {iAvrgPow/230:0.3f} {oAvrgPow/2300.3f}\treal_c: {iRealPow/230:0.3f} {oRealPow/230:0.3f}")
    return {
        'ai': iAvrgPow,
        'ao': oAvrgPow,
        'ri': iRealPow,
        'ro': oRealPow,
        'fi': iPowFactor,
        'fo': oPowFactor
    }
            
def getBatchPow(sbl):
    ret = []
    for batchId in range(len(sbl)):
            ret.append([])
            for pId in range(3):
                # print(f"{pId}({batchId})")
                sPhase = copy.deepcopy(sbl[batchId][pId])            
                powerRes = getPhasePow(sPhase)   
                ret[batchId].append(powerRes)
    return ret
            

def getPowMeta(pl):
    ret = {
        'ri':  0,
        'ro': 0,
        'data': pl
    }
    for pId in range(3):
        ret['ri'] += pl[pId]['ri']
        ret['ro'] += pl[pId]['ro']
    return ret
             

            