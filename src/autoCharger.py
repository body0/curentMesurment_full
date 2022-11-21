import logging
import json
import asyncio
import uvicorn
import asgiref
from enums import OcppMisc as oc
from enums import ConfigurationKey as ck

from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus, ResetType, ResetStatus
from ocpp.v16 import call_result, call
import os
import sys
from datetime import datetime
from fastapi import Body, FastAPI, status, Request, WebSocket, Depends
from chargepoint import ChargePoint

app = FastAPI()
#print(asgiref.__version__)
logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):

    @on(Action.Authorize)
    async def on_auth(self, id_tag, **kwargs):
        if id_tag == "test_cp2" or id_tag == "test_cp5":
            print("authorized")
            #cur.execute("INSERT INTO id(id_tag) VALUES (?)", (id_tag,))
            #con.commit()
            return call_result.AuthorizePayload(
                id_tag_info={oc.status.value: AuthorizationStatus.accepted.value}
            )
        else:
            print("Not Authorized")
            return call_result.AuthorizePayload(
                id_tag_info={oc.status.value: AuthorizationStatus.invalid.value}
            )


    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=1000,
            status=RegistrationStatus.accepted
        )

    @on(Action.Heartbeat)
    def on_heart_beat(self):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )

    @on(Action.StatusNotification)
    def status_notification(self, connector_id, status, error_code, **kwargs):
        global STATUS
        if connector_id == 1:
            print(f"Status of the Charger ==> {status}")

        return call_result.StatusNotificationPayload()

    @on(Action.StartTransaction)
    def start_transaction(self, connector_id, id_tag, timestamp, meter_start, **kwargs):

        return call_result.StartTransactionPayload(
            transaction_id=int(4),
            id_tag_info={
                "status": "Accepted"
            }
        )

    @on(Action.StopTransaction)
    def stop_transaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        return call_result.StopTransactionPayload(
            id_tag_info={
                "status": 'Accepted'
            }
        )

    @on(Action.MeterValues)
    def meter_value(self, connector_id, meter_value, **kwargs):
        # meter_values["connector_id"] = connector_id
        # meter_values["meter_value"] = meter_value
        print(f"this is meter_value payload{meter_value}, {kwargs}")
        return call_result.MeterValuesPayload()


    """
#used remote start with fast api to trigger it
    async def remote_start(self):
        request =   
        response=await  self.call(request)
        print(response)
        return "success" """



class CentralSystem:
    def __init__(self):
        self._chargers = {}

   
    async def start_charger(self, cp, queue):
        try:
            await cp.start()
        except Exception as error:
            print(f"Charger {cp.id} disconnected: {error}")
        finally:
            del self._chargers[cp]
            await queue.put(True)


    def disconnect_charger(self, id: str):
        for cp, task in self._chargers.items():
            if cp.id == id:
                task.cancel()
                print("disconnected")
                return

        raise ValueError(f"Charger {id} not connected.")



usedCharger = None

def register_charger(self, cp: ChargePoint):
    queue = asyncio.Queue(maxsize=1)
    task = asyncio.create_task(self.start_charger(cp, queue))
    self._chargers[cp] = task
    print(self._chargers)
    return queue








class SocketAdapter:
    def __init__(self, websocket: WebSocket):
        self._ws = websocket

    async def recv(self) -> str:
        return await self._ws.receive_text()

    async def send(self, msg) -> str:
        await self._ws.send_text(msg)


@app.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept(subprotocol='ocpp1.6')
    cp_id = websocket.url.path.strip('/')
    cp = ChargePoint(cp_id, SocketAdapter(websocket))
    print(f"charger {cp.id} connected.")

    queue = csms.register_charger(cp)
    await queue.get()


def detRoute():
    return app