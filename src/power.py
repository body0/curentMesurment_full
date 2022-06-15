import sched
import time

import ioControl
import analisis
import db
import ruleEvaluator



def getPower():
    phaseList = ioControl.mesure()
    batch = analisis.genBatch(phaseList)
    sBatch = analisis.getShiftedBatch(batch)
    ssBatch = analisis.scaleBatchToReal(sBatch)
    powerList = analisis.getAvrgPower(ssBatch)
    return powerList


pMesScheduler = sched.scheduler(time.time, time.sleep)
watcherPeriod = 100
watcherRuning = False
curentTimer = None

def startWatcher():
    global pMesScheduler, watcherPeriod, watcherRuning, curentTimer
    watcherRuning = True  
    if curentTimer != None: 
        pMesScheduler.cancel(curentTimer)
    curentTimer = pMesScheduler.enter(watcherPeriod, 1, watherTick)
    
def stopWatcher():
    global pMesScheduler, watcherPeriod, watcherRuning, curentTimer
    watcherRuning = False  
    if curentTimer != None: 
        pMesScheduler.cancel(curentTimer)
    
    
def watherTick():
    global pMesScheduler, watcherPeriod, watcherRuning, curentTimer
    pow = getPower()
    db.tryAddPow(pow)
    ruleEvaluator.evalRules(analisis.getAvrgFullPower(pow))
    if watcherRuning:
        curentTimer = pMesScheduler.enter(watcherPeriod, 1, watherTick)
    