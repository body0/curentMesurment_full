import time
import ioControl
import analisis
import db

def mesureAndPublish():
    phaseList = ioControl.mesure()
    batch = analisis.genBatch(phaseList)
    sBatch = analisis.getShiftedBatch(batch)
    ssBatch = analisis.scaleBatchToReal(sBatch)
    powerList = analisis.getAvrgPower(ssBatch)
    db.addPowRes(powerList)
        

while True:
    mesureAndPublish()
    time.sleep(10)