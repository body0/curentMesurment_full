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
eer = None

def startWatcher():
    global pMesScheduler, watcherPeriod, watcherRuning, curEvent
    watcherRuning = True  
    if curEvent != None: 
        pMesScheduler.cancel(curEvent)
    curEvent = pMesScheduler.enter(watcherPeriod, 1, watherTick)
    
def stopWatcher():
    global pMesScheduler, watcherPeriod, watcherRuning, curEvent
    watcherRuning = False  
    if curEvent != None: 
        pMesScheduler.cancel(curEvent)
    
    
def watherTick():
    global pMesScheduler, watcherPeriod, watcherRuning, curEvent
    pow = getPower()
    db.tryAddPow(pow)
    ruleEvaluator.evalRules(analisis.getAvrgFullPower(pow))
    if watcherRuning:
        curEvent = pMesScheduler.enter(watcherPeriod, 1, watherTick)
    