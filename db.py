import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path('upstream.env'))

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port = os.getenv('DB_PORT'),
    database="apiuser",
    user="postgres",
    password=os.getenv('DB_PASS'))
print("DB, connected")

def addPowRes(powerList):
    cur = conn.cursor()
    for pPhase in powerList:
        [powA, powB] = powerList[pPhase]
        cur.execute('insert into avrg_pow (phId, powA, powB) values (%s, %s, %s)', [pPhase, powA, powB])
    conn.commit()
    conn.close()