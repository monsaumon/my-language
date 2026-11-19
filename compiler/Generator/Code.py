from dataclasses import dataclass
from typing import Any

from Generator.Instruction import Instruction

@dataclass
class Code:
    instruction: Instruction
    operand: Any | None

    def __repr__(self) -> str:
        if type(self.operand) == str: self.operand = f"'{self.operand}'"
        elif type(self.operand) == int: self.operand = f"[{self.operand}]"
        elif type(self.operand) == float and self.operand % 1 == 0: self.operand = f" {int(self.operand)}"
        elif self.operand == None: return f"{self.instruction}"
        return f"{self.instruction:26s}{self.operand}"