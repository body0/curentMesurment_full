import mqtt
import ioControl
import cMesurment
import time

cMesurment.init()
mqtt.init()

while True:
    phaseList = ioControl.mesure()
    mqtt.publish(phaseList)
    time.sleep(10)
