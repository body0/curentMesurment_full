import sched
import time

from sqlalchemy import true

import ioControl
import analisis


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
    if watcherRuning:
        curEvent = pMesScheduler.enter(watcherPeriod, 1, watherTick)
    