
from paho.mqtt import client as mqtt_client
import time
import os.path
import ioControl
# https://www.ti.com/lit/ds/symlink/ads1113.pdf?ts=1632622221919&ref_url=https%253A%252F%252F$

broker = 'localhost'
port = 1883
client_id = 'rockPI'
# username = 'emqx'
# password = 'public'

relePortID = '68'
client = None

def init():
    global client
    print("MQTT, init")
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)

def getCurentTopic(id=0):
    return f'/curent_now/{id}'
def getVoltageTopic(id=0):
    return f'/voltage_now/{id}'

def formatPhaseData(pd, i):
    return f"{pd['ci'][i]},{pd['co'][i]},{pd['vv'][i]},{pd['ti'][i]},{pd['to'][i]},{pd['tv'][i]}"
    # return f"{0},{pd['co'][i]},{pd['vv'][i]},{pd['ti'][i]},{pd['to'][i]},{pd['tv'][i]}"

def publish(phaseList):
    global client
    for phaseId in range(len(phaseList)):
        # print(phaseList[phaseId]["sCount"])
        for sampleId in range(phaseList[phaseId]["sCount"]):
            #print(f"/phase_now/{phaseId}", f"{phaseList[phaseId]['curent_chA'][sampleId]},{phaseList[phaseId]['curent_chB'][sampleId]},{phaseList[phaseId]['voltage'][sampleId]}")
            client.publish(f"/phase_now/{phaseId}", formatPhaseData(phaseList[phaseId], sampleId))
    client.publish("/new_mesurment", "")

