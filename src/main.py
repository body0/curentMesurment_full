#!/bin/python3


import json
import os
import asyncio
import envVar
import uvicorn

import ioControl
import power
import ruleEvaluator
import db
import mqtt
import api



print("INIT, start init")
db.connectToDb()
mqtt.init()
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
    asyncio.run(startServer())
    
    