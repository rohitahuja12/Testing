import dbclient as db 
from typing import List
from item import Item
import json
import hashlib
import log
logger = log.getLogger()

class ResourceAPI():

    def __init__(self, host, collection, **kwargs):
        self.host = host
        self.collection = collection
        self.filters = kwargs.get('filters', None)
        self.nameField = kwargs.get('nameField', None)

    async def getItemsList(self) -> List[Item]:
        documents = await db.getAll(self.collection, self.filters or {})
        return [
            Item(
                _id = doc['_id'],
                name = self.nameField and doc[self.nameField],
                # hash = hashlib.sha256(str(i).encode('utf-8')).hexdigest(),
                lastModified = doc.get('lastModified', doc['createdOn']),
                error = None
            )
            for doc in documents]

    async def getItemData(self, identifier: str) -> str:
        data = await db.get(self.collection, identifier)
        return data

    async def createItemData(self, name: str, data: str) -> None:
        try:
            await db.update(self.collection, data)
        except Exception as e:
            logger.info(f'failed update with {e}, trying create')
            try: 
                await db.create(self.collection, data) 
            except Exception as e:
                logger.error(f'Failed to synchronize item {data["_id"]} with error {e}')
        
