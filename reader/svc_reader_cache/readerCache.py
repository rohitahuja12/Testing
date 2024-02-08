from datetime import datetime, timedelta
import sqlite3
import log
import json

logger = log.getLogger("svc_reader_cache.readerCache")
conn = sqlite3.connect("/readercache/reader_cache.db")
conn.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, expiry_date TEXT);")
conn.commit()

class ReaderCache:
    def __init__(self):
        pass

    def _createTableIfNotExists(self) -> bool:
        conn.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, expiry_date TEXT);")
        conn.commit()
        return True
    
    def deleteCachedValue(self, key:str) -> bool:
        self._createTableIfNotExists()
        logger.info(f"deleting expired cache entry for key {key}")
        sql_delete = """
            DELETE FROM cache WHERE key = ?;
        """
        conn.execute(sql_delete, (key,))
        conn.commit()
        return True

    def getAllKeys(self) -> str:
        self._createTableIfNotExists()
        sql_get = """
            SELECT key FROM cache;
        """
        res = conn.execute(sql_get).fetchall()
        conn.commit()
        return res

    
    def deleteTable(self) -> bool:
        self._createTableIfNotExists()
        conn.execute("DROP TABLE cache;")
        conn.commit()
        return True
    
    def clearCache(self) -> bool:
        self._createTableIfNotExists()
        conn.execute("DELETE FROM cache;")
        conn.commit()
        return True
    
    def getCachedValue(self, key:str) -> str:
        self._createTableIfNotExists()
        sql_get = """
            SELECT value, expiry_date FROM cache WHERE key = ?;
        """
        res = conn.execute(sql_get, (key,)).fetchone()

        # delete the entry if it has expired, but still return the value
        if res and datetime.now() > datetime.fromisoformat(res[1]):
            self.deleteCachedValue(key)
        if res:
            data = json.loads(res[0])
            return data
        else:
            logger.info(f"no cached value found for key {key}")
            return ''
        
    # expiry date is datetime but gui does not support the type
    def updateCachedValue(self, key:str, value:str, expiry_date:str) -> bool:
        self._createTableIfNotExists()
        try:
            logger.info(f"updating cache entry for key {key}")
            sql_update = """
                UPDATE cache SET value = ?, expiry_date = ? WHERE key = ?;
            """
            json_value = json.dumps(value)
            conn.execute(sql_update, (json_value, expiry_date, key))
            conn.commit()
            return True
        except sqlite3.Error as er:
            logger.error(f"update cache entry failed: {er}")
            return False

    def cacheValue(self, key:str, value:str, expiryHours:int = 0) -> bool:
        try:
            self._createTableIfNotExists()
            if expiryHours > 0:
                expiry_date = datetime.now() + timedelta(hours=expiryHours)
            else:
                expiry_date = datetime.now() + timedelta(days=365000)
            sql_insert = """
                INSERT INTO cache (key, value, expiry_date) VALUES (?, ?, ?);
            """
            json_value = json.dumps(value)
            conn.execute(sql_insert, (key, json_value, expiry_date))
            conn.commit()
            logger.info(f"cached value for key {key}")
            return True
        except sqlite3.Error as er:
            # key probably already exists, try to update the value
            if er.__class__.__name__ == "IntegrityError":
                updateResult = self.updateCachedValue(key, value, expiry_date)
                return updateResult
