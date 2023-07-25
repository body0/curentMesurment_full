import sys
import os
from subprocess import run


enable = False
mockLen = 10
mockData = {
    "ci": [0 for i in range(mockLen)],
    "co": [0 for i in range(mockLen)],
    "vv": [0 for i in range(mockLen)],
    "ti": [0 for i in range(mockLen)],
    "to": [0 for i in range(mockLen)],
    "tv": [0 for i in range(mockLen)],
    "sTime": 0,
    "eTime": 0,
    "sCount": mockLen
}
    
def init():
    global enable
    # if (os.geteuid() == 0): 
        # raise Exception("Roor priv required")
    enable = True

def getPhaseList(dpCount):
    if not enable:
        return mockData
    p = run( [ './run.out', str(dpCount) ] ) 
    if p.returncode != 0 :
        sys.exit("Eroor in subprogram (getting power)")  
    return loadData()

def loadData():
    phaseList = []
    curentPhase = 0
    with open('/tmp/phase', 'r') as f:
        while True:
            line = f.readline()
            if len(line) == 0: 
                break
            if line[0] == '>':
                splitParam = line[1:].split(',')
                phaseId = int(splitParam[0])
                while phaseId+1 > len(phaseList):
                    phaseList.append({
                        "ci": [],
                        "co": [],
                        "vv": [],
                        "ti": [],
                        "to": [],
                        "tv": [],
                        "sTime": int(splitParam[2]),
                        "eTime": int(splitParam[3]),
                        "sCount": int(splitParam[1])
                    })
                curentPhase = phaseId
                
            elif line[0] == '=':
                parts = line[1:].split(',')
                phaseList[curentPhase]["ci"].append(int(parts[1])) # TMP FIX !!!!!!!!
                phaseList[curentPhase]["co"].append(int(parts[0])) # TMP FIX !!!!!!!! 
                # phaseList[curentPhase]["ci"].append(int(parts[0]))
                # phaseList[curentPhase]["co"].append(int(parts[1]))
                phaseList[curentPhase]["vv"].append(int(parts[2]))
                phaseList[curentPhase]["ti"].append(float(parts[3]))
                phaseList[curentPhase]["to"].append(float(parts[4]))
                phaseList[curentPhase]["tv"].append(float(parts[5]))

    return phaseList
