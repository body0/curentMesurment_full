import sys
from subprocess import run


def getPhaseList():
    p = run( [ 'nice -n -19 ./run.out' ] ) 
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
                        "curent_chA": [],
                        "curent_chB": [],
                        "voltage": [],
                        "sTime": int(splitParam[2]),
                        "eTime": int(splitParam[3]),
                        "sCount": int(splitParam[1])
                    })
                curentPhase = phaseId
                
            elif line[0] == '=':
                splitDataPoint = line[1:].split(',')
                phaseList[curentPhase]["curent_chA"].append(int(splitDataPoint[0]))
                phaseList[curentPhase]["curent_chB"].append(int(splitDataPoint[1]))
                phaseList[curentPhase]["voltage"].append(int(splitDataPoint[2]))
    return phaseList
