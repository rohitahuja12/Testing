from marshmallow_dataclass import dataclass
from dataclasses import field
from marshmallow import EXCLUDE
from typing import List, Union, Optional

@dataclass
class Point:
    x: Union[float, int]
    y: Union[float, int]
    z: Optional[Union[float, None]]

@dataclass
class PointRegion:
    point: Point = field(metadata=dict(unknown=EXCLUDE))

@dataclass
class Feature:
    key: List[str]
    region: List[PointRegion] = field(metadata=dict(unknown=EXCLUDE))

@dataclass
class Product:
    productName: str
    exposures: Optional[List[int]]
    features: List[Feature] = field(metadata=dict(unknown=EXCLUDE))

