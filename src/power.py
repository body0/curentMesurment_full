import schedule
import threading
import time

import ioControl
import analisis
import db
import mqtt
import ruleEvaluator



def getPower():
    return getPowerAndMeta()[0][0]

def getPowerAndMeta():
    tries = 3
    while (tries > 0):
        tries-=1
        phaseList = ioControl.mesure()
        analisis.scaleData([phaseList])
        sbl = analisis.shiftData([phaseList])
        if (sbl != None): break
    # print(sbl) 
    pbl = analisis.getBatchPow(sbl)
    return (pbl, sbl, phaseList)


watcherPeriod = 40
curentTimer = None



def startWatcher():
    global watcherPeriod, curentTimer
    print("Pow, starting watcher")
    clearWatcher()
    curentTimer = run_continuously() 
    
    
def stopWatcher():
    global watcherPeriod
    print("Pow, stopping watcher")
    clearWatcher()
    
    
def clearWatcher():
    global curentTimer
    """ if curentTimer != None: 
        pMesScheduler.cancel(curentTimer) """
    """ if curentTimer != None: 
        schedule.cancel_job(curentTimer) """
    if curentTimer != None: 
        curentTimer.set()
    curentTimer = None
    

def run_continuously(interval=1):
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run
    
""" def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start() """
    
def watherTick():
    global pMesScheduler, watcherPeriod, watcherRuning, curentTimer
    print("Pow, TICK")
    (pbl, sbl, phaseList) = getPowerAndMeta()
    pl = pbl[0]
    phaseList = ioControl.mesure()
    db.tryAddPow(pl)
    mqtt.publish(phaseList)
    # ruleEvaluator.evalRules(analisis.getPowMeta(pl))
    """ if watcherRuning:
        curentTimer = pMesScheduler.enter(watcherPeriod, 1, watherTick)
        pMesScheduler.run() """

# def init():
    # pass
    # schedule.every(watcherPeriod).seconds.do(watherTick)
    