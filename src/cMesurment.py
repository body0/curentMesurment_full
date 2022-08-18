import sys
import os
from subprocess import run

rootPriv=False
if (os.geteuid() == 0): 
    rootPriv=True

def getPhaseList():
    # p = run( [ f'  {-19 if rootPriv else 0} ./run.out' ] ) 
    p = run( [ './run.out', "200" ] ) 
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
                        "t_curent_chA": [],
                        "t_curent_chB": [],
                        "t_voltage": [],
                        "sTime": int(splitParam[2]),
                        "eTime": int(splitParam[3]),
                        "sCount": int(splitParam[1])
                    })
                curentPhase = phaseId
                
            elif line[0] == '=':
                parts = line[1:].split(',')
                phaseList[curentPhase]["curent_chA"].append(int(parts[0]))
                phaseList[curentPhase]["curent_chB"].append(int(parts[1]))
                phaseList[curentPhase]["voltage"].append(int(parts[2]))
                phaseList[curentPhase]["t_curent_chA"].append(int(parts[3]))
                phaseList[curentPhase]["t_curent_chB"].append(int(parts[4]))
                phaseList[curentPhase]["t_voltage"].append(int(parts[5]))

    return phaseList
