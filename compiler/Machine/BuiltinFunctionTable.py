from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Callable
import math
import time

def _length(values: List[Any]) -> Any:
    if len(values) == 1 and (type(values[0]) is list or type(values[0]) is dict):
        return len(values[0])
    return None

def _push(values: List[Any]) -> Any:
    if len(values) == 2 and type(values[0]) is list:
        values[0].append(values[1])
        return values[0]
    return None

def _pop(values: List[Any]) -> Any:
    if len(values) == 1 and type(values[0]) is list and values[0]: return values[0].pop()
    return None

def _erase(values: List[Any]) -> Any:
    if len(values) == 2 and type(values[0]) is dict and type(values[1]) is str and values[1] in values[0]:
        result: Any = values[0].get(values[1])
        del values[0][values[1]]
        return result
    return None

def _clock(_: List[Any]) -> Any:
    return time.time()

def _sqrt(values: List[Any]) -> Any:
    return math.sqrt(float(values[0]))

builtinFunctionTable: Dict[str, Callable[[List[Any]], Any]] = {
    "length": _length,
    "push": _push,
    "pop": _pop,
    "erase": _erase,
    "clock": _clock,
    "sqrt": _sqrt,
}   