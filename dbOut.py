import time
import ioControl
import analisis
import db

def mesureAndPublish():
    phaseList = ioControl.mesure()
    batch = analisis.genBatch(phaseList)
    sBatch = analisis.getShiftedBatch(batch)
    powerList = analisis.getAvrgPower(sBatch)
    db.addPowRes(powerList)
        

while True:
    mesureAndPublish()
    time.sleep(90)