from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Object:
    isMarked: bool = False

@dataclass
class Array(Object):
    values: List[Any] = field(default_factory=list)

@dataclass
class Map(Object):
    values: Dict[str, Any] = field(default_factory=dict)