from dataclasses import dataclass
from typing import Dict, List
from collections.abc import Callable
import math
import time

@dataclass
class _ExReturn:
    value: ...
    Extype: str

class _Functions:
    @staticmethod
    def length_(values: List[_ExReturn]) -> _ExReturn:
        if len(values) == 1 and (values[0].Extype == "Array" or values[0].Extype == "Map"): return _ExReturn(len(values[0].value), "Number")
        return _ExReturn(0, "Null")
    
    @staticmethod
    def push_(values: List[_ExReturn]) -> _ExReturn:
        if len(values) == 2 and values[0].Extype == "Array":
            values[0].value.append(values[1])
            return values[0]
        return _ExReturn(0, "Null")
    
    @staticmethod
    def pop_(values: List[_ExReturn]) -> _ExReturn:
        if len(values) == 1 and values[0].Extype == "Array" and len(values[0].value): return values[0].value.pop()
        return _ExReturn(0, "Null")
    
    @staticmethod
    def erase_(values: List[_ExReturn]) -> _ExReturn:
        if len(values) == 2 and values[0].Extype == "Map" and values[1].Extype == "String" and (values[1].value in values[0].value):
            result: _ExReturn = values[0].value.get(values[1].value)
            del values[0].value[values[1].value]
            return result
        return _ExReturn(0, "Null")
    
    @staticmethod
    def clock_(values: List[_ExReturn]) -> _ExReturn:
        return _ExReturn(time.time(), "Number")

    @staticmethod
    def sqrt_(values: List[_ExReturn]) -> _ExReturn:
        return _ExReturn(math.sqrt(float(values[0].value)))

builtinFunctionTable: Dict[str, Callable[[List[_ExReturn]], _ExReturn]] = {
    "length": _Functions.length_,
    "push": _Functions.push_,
    "pop": _Functions.pop_,
    "erase": _Functions.erase_,
    "clock": _Functions.clock_,
    "sqrt": _Functions.sqrt_,
}   