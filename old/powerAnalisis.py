import math


def scaleValues(data):
    for sensor in data:
        for i, val in enumerate(sensor):
            sensor[i] = val / 0x8FF * 25 # * 0.512 
    return data

def run(data, targetSensorIndex):
    targetSensorData = data[targetSensorIndex]
    
    x = []
    y = []
    dcCurent = 0
    for i, dataPoint in enumerate(targetSensorData):
        x.append(i)
        y.append(dataPoint)
        dcCurent = dcCurent + abs(dataPoint)
        
     # DC EQUVIVALENT
    dcCurent = dcCurent / len(y) # /1.414213562

        
    x_peek = []
    y_peek = []
    zeroLevel = 0
    cutOffThreashold = 0.6
    
    
    # PEEK SEARCH TOP
    def searchTopPeeks():
        peekStackLocal = [
            [targetSensorData[0], 0]
        ]
        minPeekDistance = 7
        for i in range(len(targetSensorData)):
            lastMax = peekStackLocal[len(peekStackLocal)-1]
            if lastMax[1] + minPeekDistance < i:
                peekStackLocal.append([targetSensorData[i], i])
            if  lastMax[0] < targetSensorData[i]:
                peekStackLocal[len(peekStackLocal)-1] = [targetSensorData[i], i]
                
        # MAX PEEKS
        #peekMaxStackLength = 3 if len(peekStackLocal) > 3 else len(peekStackLocal)
        peekMaxStackStartOfset = 2
        peekMaxStackLength = math.floor(len(peekStackLocal) /2.5) + peekMaxStackStartOfset
        peekMaxStack = []
        for peek in peekStackLocal:
            peekMaxStack.append(abs(peek[0]))
        peekMaxStack.sort(reverse=True)
        peekMaxStack = peekMaxStack[peekMaxStackStartOfset:peekMaxStackLength]
        peekMaxAvrg = 0
        for peekMax in peekMaxStack:
            peekMaxAvrg = peekMaxAvrg + peekMax
        peekMaxAvrg = peekMaxAvrg / len(peekMaxStack)
        
        # DROP NOT MAX PEEKS
        peekCutOff = peekMaxAvrg * (cutOffThreashold if peekMaxAvrg > 0 else 1/cutOffThreashold)
        i = 0
        while i < len(peekStackLocal):
            peek = peekStackLocal[i]
            if peek[0] < peekCutOff:
                del peekStackLocal[i]
            else:
                i = i +1
        
        #return [peekStackLocal[:2], 0]
        return [peekStackLocal, peekCutOff]

    def searchBottomPeeks():
        peekStackLocal = [
            [targetSensorData[0], 0]
        ]
        minPeekDistance = 7
        for i in range(len(targetSensorData)):
            lastMax = peekStackLocal[len(peekStackLocal)-1]
            if lastMax[1] + minPeekDistance < i:
                peekStackLocal.append([targetSensorData[i], i])
            if  lastMax[0] > targetSensorData[i]:
                peekStackLocal[len(peekStackLocal)-1] = [targetSensorData[i], i]
        
        # MAX PEEKS
        #peekMaxStackLength = 3 if len(peekStackLocal) > 3 else len(peekStackLocal)
        peekMaxStackStartOfset = 2
        peekMaxStackLength = math.floor(len(peekStackLocal) /2.5) + peekMaxStackStartOfset
        peekMaxStack = []
        for peek in peekStackLocal:
            peekMaxStack.append(peek[0])
        peekMaxStack.sort()
        peekMaxStack = peekMaxStack[peekMaxStackStartOfset:peekMaxStackLength]
        peekMaxAvrg = 0
        for peekMax in peekMaxStack:
            peekMaxAvrg = peekMaxAvrg + peekMax
        peekMaxAvrg = peekMaxAvrg / len(peekMaxStack)

        # DROP NOT MAX PEEKS
        peekCutOff = peekMaxAvrg * (cutOffThreashold if peekMaxAvrg < 0 else 1/cutOffThreashold)
        i = 0
        while i < len(peekStackLocal):
            peek = peekStackLocal[i]
            if peek[0] > peekCutOff:
                del peekStackLocal[i]
            else:
                i = i +1
        return [peekStackLocal, peekCutOff]
    
    
    
    # FIND ALL PEEKS
    peekStack = []
    peekCutOffTop = 0
    peekCutOffBottom = 0
    peekStackTop, peekCutOffTop = searchTopPeeks()
    peekStackBottom, peekCutOffTop = searchBottomPeeks()
    peekStack = peekStackTop + peekStackBottom
    def sortFun(element):
        return element[1]
    peekStack.sort(key=sortFun)



    
    # PEEK AVERAGE
    peekAvrg = 0
    for i in range(len(peekStack)-1):
        peekAvrg = peekAvrg + abs(peekStack[i][0])
    peekAvrg = peekAvrg / (len(peekStack))
    midZeroLevel = (zeroLevel + dcCurent) /2

    # PARSING TO GRAPH
    for i in range(len(peekStack)):
        y_peek.append(peekStack[i][0])
        x_peek.append(peekStack[i][1])


    # TODO simplify math exp
    # PHASE SHIFT
    phaseLengthAvrg = 0
    for xPeekValIndex in range(1, len(x_peek)):
        phaseLengthAvrg = phaseLengthAvrg + x_peek[xPeekValIndex] - x_peek[xPeekValIndex-1]
    phaseLengthAvrg = phaseLengthAvrg / (len(x_peek) -1) 
    phaseLengthAvrg = phaseLengthAvrg *2  

    # min 2 points in x_peek
    phaseShift = x_peek[0]/phaseLengthAvrg
    if y_peek[0] < zeroLevel:
        phaseShift = phaseShift + 0.5
    phaseShift = phaseShift %1

    return dcCurent