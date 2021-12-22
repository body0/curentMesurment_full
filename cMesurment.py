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
                phaseList[curentPhase].append({
                    "curent_chA": [],
                    "curent_chB": [],
                    "voltage": [],
                    "sTime": 0,
                    "eTime": 0,
                })
            elif line[0] == '=':
                splitDataPoint = line[1:].split(',')
                phaseList[curentPhase]["curent_chA"].append(int(splitDataPoint[0]))
                phaseList[curentPhase]["curent_chB"].append(int(splitDataPoint[1]))
                phaseList[curentPhase]["voltage"].append(int(splitDataPoint[2]))
    return phaseList
