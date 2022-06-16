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
    print("Pow, starting watcher")
    watcherRuning = True  
    if curentTimer != None: 
        pMesScheduler.cancel(curentTimer)
    curentTimer = pMesScheduler.enter(watcherPeriod, 1, watherTick)
    pMesScheduler.run()
    
    
def stopWatcher():
    global pMesScheduler, watcherPeriod, watcherRuning, curentTimer
    print("Pow, stopping watcher")
    watcherRuning = False  
    if curentTimer != None: 
        pMesScheduler.cancel(curentTimer)
    curentTimer = None
    
    
def watherTick():
    global pMesScheduler, watcherPeriod, watcherRuning, curentTimer
    print("Pow, TICK")
    pow = getPower()
    db.tryAddPow(pow)
    ruleEvaluator.evalRules(analisis.getAvrgFullPower(pow))
    if watcherRuning:
        curentTimer = pMesScheduler.enter(watcherPeriod, 1, watherTick)
        pMesScheduler.run()
