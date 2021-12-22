import sys
from subprocess import run


def getPhaseList():
    p = run( [ './run.out' ] ) 
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
                phaseId = int(line[1])
                while phaseId+1 > len(phaseList):
                    phaseList.append([])
                curentPhase = phaseId
            elif line[0] == '=':
                splitDataPoint = line[1:].split(',')
                phaseList[curentPhase].append({
                    "curent_chA": int(splitDataPoint[0]),
                    "curent_chB": int(splitDataPoint[1]),
                    "voltage": int(splitDataPoint[2]),
                    "sTime": 0,
                    "eTime": 0,
                })
    return phaseList
