import schedule
import threading
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


watcherPeriod = 10
watcherRuning = False
curentTimer = None



def startWatcher():
    global watcherPeriod, watcherRuning, curentTimer
    print("Pow, starting watcher")
    watcherRuning = True  
    clearWatcher()
    curentTimer = run_continuously() 
    
    
def stopWatcher():
    global watcherPeriod, watcherRuning
    print("Pow, stopping watcher")
    watcherRuning = False  
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
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
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
    pow = getPower()
    db.tryAddPow(pow)
    ruleEvaluator.evalRules(analisis.getAvrgFullPower(pow))
    """ if watcherRuning:
        curentTimer = pMesScheduler.enter(watcherPeriod, 1, watherTick)
        pMesScheduler.run() """

def init():
    # schedule.every(watcherPeriod).seconds.do(run_threaded, watherTick)
    schedule.every(watcherPeriod).seconds.do(watherTick)
    
init()