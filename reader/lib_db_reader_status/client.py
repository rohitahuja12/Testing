from datetime import datetime
import sqlite3
import sys
sys.path.insert(0, './common')
import log
logger = log.getLogger("lib_db_reader_status.client")


dbfile = "/readerdata/reader_status.db"
tableNames = ['initialization', 'door', 'laser', 'boardpower', 'boardconnect', 'taskstatus']


def getStatus():
    conn = sqlite3.connect(dbfile)
    sql_get_initialization = "SELECT status, max(timestamp) FROM initialization;"
    sql_get_door = "SELECT status, max(timestamp) FROM door;"
    sql_get_laser = "SELECT status, max(timestamp) FROM laser;"
    sql_get_boardpower = "SELECT status, max(timestamp) FROM boardpower;"
    sql_get_boardconnect = "SELECT status, max(timestamp) FROM boardconnect;"
    sql_get_taskstatus = "SELECT status, max(timestamp) FROM taskstatus;"

    initializationres = conn.execute(sql_get_initialization)
    doorres = conn.execute(sql_get_door)
    laserres = conn.execute(sql_get_laser)
    boardpowerres = conn.execute(sql_get_boardpower)
    boardconnectres = conn.execute(sql_get_boardconnect)
    taskstatusres = conn.execute(sql_get_taskstatus)

    def f(x):
        y = x.fetchone()
        return y[0] if y else None

    return {
        "initialized": f(initializationres),
        "door": f(doorres),
        "laser": f(laserres),
        "boardPower": f(boardpowerres),
        "boardConnect": f(boardconnectres),
        "taskStatus": f(taskstatusres)
    }


def readerUnintialized():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_uninitialized = "INSERT INTO initialization VALUES (?, ?);"
    conn.execute(sql_uninitialized, ("UNINITIALIZED", now))
    conn.commit()
    logger.info("READER_UNINITIALIZED event created")

def readerInitializing():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_initializing = "INSERT INTO initialization VALUES (?, ?);"
    conn.execute(sql_initializing, ("INITIALIZING", now))
    conn.commit()
    logger.info("READER_INITIALIZING event created")

def readerInitialized():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_initialized = "INSERT INTO initialization VALUES (?, ?);"
    conn.execute(sql_initialized, ("INITIALIZED", now))
    conn.commit()
    logger.info("READER_INITIALIZED event created")

def readerInitializationError():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_init_error = "INSERT INTO initialization VALUES (?, ?);"
    conn.execute(sql_init_error, ("ERROR", now))
    conn.commit()
    logger.info("READER_INIT_ERROR event created")

def doorOpen():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_open_door = "INSERT INTO door VALUES (?, ?);"
    conn.execute(sql_open_door, ("OPEN", now))
    conn.commit()
    logger.info("DOOR_OPEN event created")

def doorClosed():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_open_door = "INSERT INTO door VALUES (?, ?);"
    conn.execute(sql_open_door, ("CLOSED", now))
    conn.commit()
    logger.info("DOOR_CLOSED event created")

def doorUnknown():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_unknown_door = "INSERT INTO door VALUES (?, ?);"
    conn.execute(sql_unknown_door, ("UNKNOWN", now))
    conn.commit()
    logger.info("DOOR_UNKNOWN event created")

def laserOn():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_open_door = "INSERT INTO laser VALUES (?, ?);"
    conn.execute(sql_open_door, ("ON", now))
    conn.commit()
    logger.info("LASER_ON event created")

def laserOff():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_open_door = "INSERT INTO laser VALUES (?, ?);"
    conn.execute(sql_open_door, ("OFF", now))
    conn.commit()
    logger.info("LASER_OFF event created")

def boardPowerOn():
    pass

def boardPowerOff():
    pass

def boardConnected():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_board_connected = "INSERT INTO boardConnect VALUES (?, ?);"
    conn.execute(sql_board_connected, ("CONNECTED", now))
    conn.commit()
    logger.info("BOARD_CONNECTED event created")

def boardDisconnected():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_board_disconnected = "INSERT INTO boardConnect VALUES (?, ?);"
    conn.execute(sql_board_disconnected, ("DISCONNECTED", now))
    conn.commit()
    logger.info("BOARD_DISCONNECTED event created")

def taskStatusReady():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_status_ready = "INSERT INTO taskstatus VALUES (?, ?);"
    conn.execute(sql_status_ready, ("READY", now))
    conn.commit()
    logger.info("TASK_STATUS_READY event created")

def taskStatusProcessing():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_status_processing = "INSERT INTO taskstatus VALUES (?, ?);"
    conn.execute(sql_status_processing, ("PROCESSING", now))
    conn.commit()
    logger.info("TASK_STATUS_PROCESSING event created")

def taskStatusDisabled():
    conn = sqlite3.connect(dbfile)
    now = datetime.utcnow().isoformat()
    sql_status_disabled = "INSERT INTO taskstatus VALUES (?, ?);"
    conn.execute(sql_status_disabled, ("DISABLED", now))
    conn.commit()
    logger.info("TASK_STATUS_DISABLED event created")


def init():
    conn = sqlite3.connect(dbfile)
    # create the tables if they don't exist
    for tableName in tableNames:
        res = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name= ? ;", (tableName,))
        result = res.fetchone()
        if result is None:
            # create it
            sql_create_table = f"CREATE TABLE {tableName} (status TEXT NOT NULL, timestamp TEXT NOT NULL);"
            res = conn.execute(sql_create_table)
            conn.commit()

    taskStatusReady()

# initialize db when module is loaded
init()
