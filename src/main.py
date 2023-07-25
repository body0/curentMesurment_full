#!/bin/python3


import json
import os
import asyncio
import envVar
import uvicorn

import ioControl
import cMesurment
import power
import ruleEvaluator
import db
import mqtt
import autoCP
import api



print("INIT, start init")
cMesurment.init()
autoCP.init()
mqtt.init()
db.connectToDb()
power.startWatcher()
print(f"INIT, start api on {envVar.API_PORT}")


# app.run(host='0.0.0.0', port=usedPort)

# def startServer():
#     done, pending = await asyncio.wait(
#         [
#             create_webserver(8000),
#             create_webserver(8001),
#         ],
#         return_when=asyncio.FIRST_COMPLETED,
#     )


async def startServer():
    config = uvicorn.Config(api.getRoute(), host="0.0.0.0", port=envVar.API_PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    # asyncio.run(startServer())
    uvicorn.run(api.getRoute(), host="0.0.0.0", port=envVar.API_PORT, log_level="error")
    