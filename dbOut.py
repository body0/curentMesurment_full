import time
import ioControl
import analisis
import db
import sys

def mesureAndPublish():
    phaseList = ioControl.mesure()
    batch = analisis.genBatch(phaseList)
    sBatch = analisis.getShiftedBatch(batch)
    ssBatch = analisis.scaleBatchToReal(sBatch)
    powerList = analisis.getAvrgPower(ssBatch)
    db.addPowRes(powerList)
            

itarval = 10
if __name__ == "__main__":
    if len(sys.argv) == 2:
        itarval = float(sys.argv[1])
    
    
print(f'Starting with interval: {itarval}')
while True:
    mesureAndPublish()
    time.sleep(itarval)
    
    