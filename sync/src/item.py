from dataclasses import dataclass

@dataclass
class Item():
    """Class for tracking a synchronizable item (document in db or file)"""
    _id: str
    name: str
    lastModified: int
    error: str
