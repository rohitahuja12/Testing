from datetime import datetime
import sqlite3
import json
import sys
sys.path.insert(0, './common')
import log
logger = log.getLogger("lib_db_task_results.client")



"""
The methods defined in this db client should resemble
the interfaces of methods defined in `common.dbClient`.
"""

def queueResult(taskId, data):
    conn = sqlite3.connect("/readerdata/task_results.db")
    now = datetime.utcnow().isoformat()
    sql_create_attachment = """
        INSERT INTO taskresults 
               (createdAt, taskId, data, uploadStatus) 
        VALUES (?, ?, ?, ?);
    """
    conn.execute(sql_create_attachment, (now, taskId, data, "PENDING"))
    conn.commit()
    conn.close()
    logger.info(f"Result for {taskId} saved locally.")
    conn.close()


def getMany(n):
    conn = sqlite3.connect("/readerdata/task_results.db")
    sql_get_some = """
        SELECT id, createdAt, taskId, data, length(data), uploadStatus, 
            lastAttemptTimestamp, lastAttemptCount, lastAttemptError 
        FROM taskresults
        WHERE uploadStatus = 'PENDING'
        LIMIT ?;
    """
    res = conn.execute(sql_get_some, (int(n),)).fetchall()
    conn.close()
    
    items = [{
        "id": row[0],
        "createdAt": row[1],
        "taskId": row[2],
        "data": row[3],
        "dataSize": row[4],
        "uploadStatus": row[5],
        "lastAttemptTimestamp": row[6],
        "lastAttemptCount": row[7],
        "lastAttemptError": row[8]
    } for row in res]

    return items


def getByTaskId(taskId):
    conn = sqlite3.connect("/readerdata/task_results.db")
    sql_get_one = """
        SELECT data, uploadStatus, 
            lastAttemptTimestamp, lastAttemptCount, lastAttemptError 
        FROM taskresults
        WHERE taskId = ?;
    """
    res = conn.execute(sql_get_one, (taskId,)).fetchall()
    conn.close()
    items = [{
        "data": row[0],
        "uploadStatus": row[1],
        "lastAttemptTimestamp": row[2],
        "lastAttemptCounts": row[3],
        "lastAttemptError": row[4]
    } for row in res]

    return items[0]

def updateTask(itemId, uploadStatus, lastAttemptTimestamp, lastAttemptCount, lastAttemptError):
    conn = sqlite3.connect("/readerdata/task_results.db")
    sql_update_attempt = """
        UPDATE taskresults
        SET uploadStatus = ?,
            lastAttemptTimestamp = ?,
            lastAttemptCount = ?,
            lastAttemptError = ?
        WHERE id = ?;
    """
    conn.execute(
        sql_update_attempt,
        (uploadStatus, lastAttemptTimestamp, lastAttemptCount, lastAttemptError, itemId))
    conn.commit()
    conn.close()
    

def init():
    conn = sqlite3.connect("/readerdata/task_results.db")
    # create the tables if they don't exist
    res = conn.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name='taskresults';
    """)
    result = res.fetchone()
    logger.info(f'does our table exist? : {result}')
    if result is None:
        # create it

        sql_create_table = """
        CREATE TABLE taskresults (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            createdAt TEXT NOT NULL,
            taskId TEXT NOT NULL,
            data BLOB NOT NULL,
            uploadStatus TEXT NOT NULL,
            lastAttemptTimestamp TEXT,
            lastAttemptCount INTEGER,
            lastAttemptError TEXT
        );
        """
        res = conn.execute(sql_create_table)
        conn.commit()
    conn.close()

# initialize db when module is loaded
init()
