import os
import stat
import json
from datetime import datetime, timezone
from typing import List
from item import Item
import log
logger = log.getLogger()

class FileSystem():

    def __init__(self, path):
        self.path = path
        self.items = []

    async def getItemsList(self) -> List[Item]:
        files = os.listdir(self.path)
        for fname in files:
            matches = self._lookupItems(name=fname)
            if len(matches) == 0:
                index = self._indexItem(fname)
                self.items.append(index)
            else:
                fullPath = os.path.join(self.path, fname)
                lastModified = self._getLastModified(fullPath)
                match = matches[0]
                # compare last modified, if newer, update index
                if lastModified > match.lastModified:
                    self.items.remove(match)
                    self.items.append(self._indexItem(fname))
        self.items = [i for i in self.items if i.name in files]
        return self.items

    async def getItemData(self, identifier: str) -> str:
        item = self._lookupItems(_id=identifier)[0]
        fname = item.name
        with open(os.path.join(self.path, fname)) as f:
            data = json.load(f)
        return data

    async def createItemData(self, name: str, data: str) -> None:
        name = f"{data['_id']}_{name}" if name else data['_id']
        fullpath = os.path.join(self.path, name)
        with open(fullpath, 'w') as f:
            json.dump(data, f, indent=4)
        os.chmod(fullpath, stat.S_IROTH | stat.S_IWOTH) # other can read/write
        

    def _indexItem(self, name: str) -> None:
        fullPath = os.path.join(self.path, name)
        with open(fullPath) as f:
            raw = f.read()
            error = None
            data = None
            _id = None
            try:
                data = json.loads(raw)
                _id = data.get('_id')
                if _id == None:
                    error = "Item has no field _id, cannot sync."
            except Exception as e:
                error = e

        it = Item(
            _id = _id,
            name = name,
            lastModified = self._getLastModified(fullPath),
            error = error if error else None
        )
        return it

    def _getLastModified(self, path) -> str:
        return datetime.fromtimestamp(
            os.stat(path).st_mtime, 
            tz=timezone.utc
        ).isoformat()



    def _lookupItems(self, **kwargs) -> List[Item]:
        _id = kwargs.get('_id', None)
        name = kwargs.get('name', None)
        if _id:
            return [i for i in self.items if i._id==_id]
        if name:
            return [i for i in self.items if i.name==name]
