import mqtt
import ioControl
import time

mqtt.init()

while True:
    phaseList = ioControl.mesure()
    mqtt.publish(phaseList)
    time.sleep(10)
