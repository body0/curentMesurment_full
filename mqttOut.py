
from paho.mqtt import client as mqtt_client
import time
import os.path
import mesure from ioControl
# https://www.ti.com/lit/ds/symlink/ads1113.pdf?ts=1632622221919&ref_url=https%253A%252F%252F$

broker = 'localhost'
port = 1883
client_id = 'rockPI'
# username = 'emqx'
# password = 'public'

relePortID = '68'

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)
client = mqtt_client.Client(client_id)
#client.username_pw_set(username, password)
#client.on_connect = on_connect
client.connect(broker, port)

def getCurentTopic(id=0):
    return f'/curent_now/{id}'
def getVoltageTopic(id=0):
    return f'/voltage_now/{id}'


def mesureAndPublish():
    phaseList = mesure()
    for phaseId in range(len(phaseList)):
        for val in [i]["curent_chA"]:
            client.publish(getCurentTopic(phaseId), val)
        for val in [i]["curent_chB"]:
            client.publish(getCurentTopic(phaseId+1), val)
        for val in [i]["voltage"]:
            client.publish(getVoltageTopic(phaseId), val)


while True:
    mesureAndPublish()
    time.sleep(5)
