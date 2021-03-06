import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path('../upstream.env'))
conn = None
dbPowLogEnabled = True

def tryAddPow(powerList):
    global conn
    if conn == None or not dbPowLogEnabled:
        return
    addPowRes(powerList)

def addPowRes(powerList):
    global conn
    cur = conn.cursor()
    for pPhaseId in range(len(powerList)):
        powA = powerList[pPhaseId][0]
        powB = powerList[pPhaseId][1]
        powAalt = powerList[pPhaseId][2]
        powBalt = powerList[pPhaseId][3]
        cur.execute('insert into avrg_pow (phId, powA, powB,  powAalt, powBalt) values (%s, %s, %s, %s, %s)',
                    [pPhaseId, powA, powB, powAalt, powBalt])
    conn.commit()
    #conn.close()
    
def selectTest():
    cur = conn.cursor()
    cur.execute('''
    SELECT
    ts AS "time",
    powA
    FROM avrg_pow
    WHERE
    phId = 0
    ''')
    conn.commit()
    rows = cur.fetchall()
    print("DB, test select")
    print(rows)


def connectToDb():
    global conn
    _host = os.getenv('DB_HOST')
    _port = os.getenv('DB_PORT')
    print(f'DB, config: {_host}:{_port}')
    
    conn = psycopg2.connect(
    host=_host,
    port=_port,
    database="record",
    user="apiuser",
    password=os.getenv('DB_PASS'))
    print("DB, connected")