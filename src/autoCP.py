# import orjson
# import urllib3

# changePowerUrl="https://192.168.1.169/api/configuration-updates"

# def getName(maxPower):
#     encoded_data = orjson.dumps({
#         "configurationFieldUpdateType": "number-configuration-field-update",
#         "fieldKey": "operator-current-limit",
#         "value": maxPower
#     })
#     resp = urllib3.request(method="POST", url="http://httpbin.org/post", body=encoded_data)

from pyModbusTCP.client import ModbusClient
from enum import Enum


class AUTO_CP_STATE(Enum):
    ANY = 0
    DISCONNECTED = 1
    CONNECTED = 2
    CHARGING = 3

conn = None

def init():
    global conn
    conn = ModbusClient(host="192.168.1.169", auto_open=True, auto_close=True)

def getState():
    reg = conn.read_holding_registers(1000, 1)
    if (not reg):
        return AUTO_CP_STATE.ANY
    val = reg[0]
    if (val == 0):
        return AUTO_CP_STATE.DISCONNECTED
    if (val == 1 or val == 4):
        return AUTO_CP_STATE.CONNECTED
    if (val == 3):
        return AUTO_CP_STATE.CHARGING
    return AUTO_CP_STATE.ANY

def setState(state):
    conn.write_multiple_registers(5006, [1 if state else 2])
    # return getState()
    
def setPower(pow):
     conn.write_multiple_registers(5000, [pow >> 8, pow & 0xff])