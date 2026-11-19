from dataclasses import dataclass
from typing import Self
from collections.abc import Sized

@dataclass
class Address:
    value: int

    def __add__(self, __value: Self | int) -> Self:
        if type(__value) is Self: __value = __value.value
        return Address(self.value + __value)
    
    def __radd__(self, __value: Self | int) -> Self:
        if type(__value) is Self: __value = __value.value
        return Address(self.value + __value)
    
    def __sub__(self, __value: Self | int) -> Self:
        if type(__value) is Self: __value = __value.value
        return Address(self.value - __value)
    
    def __rsub__(self, __value: Self | int) -> Self:
        if type(__value) is Self: __value = __value.value
        return Address(__value - self.value)
    
    def __ne__(self, __value: object) -> bool:
        return self.value != __value
    
    def __eq__(self, __value: object) -> bool:
        return self.value == __value
    
    def __lt__(self, __value: object) -> bool:
        return self.value < __value
    
    def __le__(self, __value: object) -> bool:
        return self.value <= __value
    
    def __gt__(self, __value: object) -> bool:
        return self.value > __value
    
    def __ge__(self, __value: object) -> bool:
        return self.value >= __value
    
    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return repr(self.value)

def size(__obj: Sized) -> Address:
    return Address(len(__obj))