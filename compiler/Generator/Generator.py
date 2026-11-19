from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from abc import *

from Scanner.Kind import Kind
from Parser.Node import *
from Parser.Parser import _ParsedExp
from Generator.Address import Address, size
from Generator.Code import Code
from Generator.Instruction import Instruction

_codeList: List[Code] = []
_functionTable: Dict[str, Address] = {}
_symbolStack: List[Dict[str, Address]] = []
_offsetStack: List[Address] = []
_localSize: Address
_continueStack: List[List[Address]] = []
_breakStack: List[List[Address]] = []

def _writeCode(instruction: Instruction, operand: Optional[Any] = None) -> Address:
    global _codeList
    _codeList.append(Code(instruction, operand))
    return size(_codeList) - 1

def _patchAddress(codeIndex: Address) -> None:
    global _codeList
    _codeList[codeIndex.value].operand = size(_codeList)

def _patchOperand(codeIndex: Address, operand: Address) -> None:
    _codeList[codeIndex.value].operand = operand

def _initBlock() -> None:
    global _localSize, _offsetStack, _symbolStack
    _localSize = Address(0)
    _offsetStack.append(Address(0))
    _symbolStack.insert(0, {})

def _pushBlock() -> None:
    global _offsetStack, _symbolStack
    _symbolStack.insert(Address(0), {})
    _offsetStack.append(_offsetStack[-1])

def _popBlock() -> None:
    global _offsetStack, _symbolStack
    _offsetStack.pop()
    _symbolStack.pop(0)

def _setLocal(name: str) -> None:
    global _localSize, _offsetStack, _symbolStack
    _symbolStack[0][name] = _offsetStack[-1]
    _offsetStack[-1] += 1
    _localSize = max(_localSize, _offsetStack[-1])

def _getLocal(name: str) -> Address:
    for symbolTable in _symbolStack:
        if name in symbolTable:
            return symbolTable[name]
    return Address(-1)

@dataclass
class Statement_(metaclass = ABCMeta):
    def __nonzero__(self) -> bool:
        return any(vars(self).values())

    @abstractmethod
    def generate(self) -> None: ...

@dataclass
class Expression_(metaclass = ABCMeta):
    def __nonzero__(self) -> bool:
        return any(vars(self).values())
    
    @abstractmethod
    def generate(self) -> None: ...

@dataclass
class Function_(Statement_):
    name: str = ...
    parameters: List[str] = ...
    block: List[Statement_] = ...

    def generate(self) -> None:
        global _codeList, _functionTable
        _functionTable[self.name] = size(_codeList)
        temp = _writeCode(Instruction.Alloc)
        _initBlock()
        for name in self.parameters:
            _setLocal(name)
        for node in self.block:
            node.generate()
        _popBlock()
        _patchOperand(temp, _localSize)
        _writeCode(Instruction.Return)

@dataclass
class Program_:
    functions: List[Function_] = ...

@dataclass
class Variable_(Statement_):
    name: str = ...
    expression: Expression_ = ...
    
    def generate(self) -> None:
        _setLocal(self.name)
        self.expression.generate()
        _writeCode(Instruction.SetLocal, _getLocal(self.name))
        _writeCode(Instruction.PopOperand)

@dataclass
class For_(Statement_):
    variable: Variable_ = ...
    condition: Expression_ = ...
    expression: Expression_ = ...
    block: List[Statement_] = ...

    def generate(self) -> None:
        global _breakStack, _continueStack
        _breakStack.append([])
        _continueStack.append([])
        _pushBlock()
        self.variable.generate()
        jumpAddress: Address = size(_codeList)
        self.condition.generate()
        conditionJump: Address = _writeCode(Instruction.ConditionJump)
        for node in self.block:
            node.generate()
        continueAddress: Address = size(_codeList)
        self.expression.generate()
        _writeCode(Instruction.PopOperand)
        _writeCode(Instruction.Jump, jumpAddress)
        _patchAddress(conditionJump)
        _popBlock()
        for jump in _continueStack[-1]:
            _patchOperand(jump, continueAddress)
        _continueStack.pop()
        for jump in _breakStack[-1]:
            _patchAddress(jump)
        _breakStack.pop()

@dataclass
class Break_(Statement_):
    def generate(self) -> None:
        global _breakStack
        if not _breakStack: return
        jumpCode: Address = _writeCode(Instruction.Jump)
        _breakStack[-1].append(jumpCode)

@dataclass
class Continue_(Statement_):
    def generate(self) -> None:
        global _continueStack
        if not _continueStack: return
        jumpCode: Address = _writeCode(Instruction.Jump)
        _continueStack[-1].append(jumpCode)

@dataclass
class If_(Statement_):
    conditions: List[Expression_] = ...
    blocks: List[List[Statement_]] = ...
    elseBlock: List[Statement_] = ...
    
    def generate(self) -> None:
        jumpList: List[Address] = []
        for i in range(len(self.conditions)):
            self.conditions[i].generate()
            conditionJump: Address = _writeCode(Instruction.ConditionJump)
            _pushBlock()
            for node in self.blocks[i]:
                node.generate()
            _popBlock()
            jumpList.append(_writeCode(Instruction.Jump))
            _patchAddress(conditionJump)
        if self.elseBlock:
            _pushBlock()
            for node in self.elseBlock:
                node.generate()
            _popBlock()
        for jump in jumpList:
            _patchAddress(jump)

@dataclass
class Print_(Statement_):
    lineFeed: bool = False
    arguments: List[Expression_] = ...

    def generate(self) -> None:
        for i in range(len(self.arguments), 0, -1):
            self.arguments[i-1].generate()
        _writeCode(Instruction.Print, size(self.arguments))
        if self.lineFeed: _writeCode(Instruction.PrintLine)

@dataclass
class Return_(Statement_):
    expression: Expression_ = ...
    
    def generate(self) -> None:
        self.expression.generate()
        _writeCode(Instruction.Return)

@dataclass
class ExpressionStatement_(Statement_):
    expression: Expression_ = ...
    
    def generate(self) -> None:
        self.expression.generate()
        _writeCode(Instruction.PopOperand)

@dataclass
class Or_(Expression_):
    left: Expression_ = ...
    right: Expression_ = ...
    
    def generate(self) -> None:
        self.left.generate()
        or_: Address = _writeCode(Instruction.LogicalOr)
        self.right.generate()
        _patchAddress(or_)

@dataclass
class And_(Expression_):
    left: Expression_ = ...
    right: Expression_ = ...
    
    def generate(self) -> None:
        self.left.generate()
        and_: Address = _writeCode(Instruction.LogicalAnd)
        self.right.generate()
        _patchAddress(and_)

@dataclass
class Relational_(Expression_):
    kind: Kind = ...
    left: Expression_ = ...
    right: Expression_ = ...
    
    def generate(self) -> None:
        instructions: Dict[Kind, Instruction] = {
            Kind.Equal:        Instruction.Equal,
            Kind.NotEqual:     Instruction.NotEqual,
            Kind.LessThan:     Instruction.LessThan,
            Kind.GreaterThan:  Instruction.GreaterThan,
            Kind.LessEqual:    Instruction.LessEqual,
            Kind.GreaterEqual: Instruction.GreaterEqual,
        }
        self.left.generate()
        self.right.generate()
        _writeCode(instructions[self.kind])

@dataclass
class Arithmetic_(Expression_):
    kind: Kind = ...
    left: Expression_ = ...
    right: Expression_ = ...
    
    def generate(self) -> None:
        instructions: Dict[Kind, Instruction] = {
            Kind.Add:      Instruction.Add,
            Kind.Subtract: Instruction.Subtract,
            Kind.Multiply: Instruction.Multiply,
            Kind.Divide:   Instruction.Divide,
            Kind.Modulo:   Instruction.Modulo,
        }
        self.left.generate()
        self.right.generate()
        _writeCode(instructions[self.kind])

@dataclass
class Unary_(Expression_):
    kind: Kind = ...
    sub: Expression_ = ...
    
    def generate(self) -> None:
        instructions: Dict[Kind, Instruction] = {
            Kind.Add:      Instruction.Absolute,
            Kind.Subtract: Instruction.ReverseSign,
        }
        self.sub.generate()
        _writeCode(instructions[self.kind])

@dataclass
class Call_(Expression_):
    sub: Expression_= ...
    arguments: List[Expression_] = ...
    
    def generate(self) -> None:
        for arg in self.arguments[::-1]:
            arg.generate()
        self.sub.generate()
        _writeCode(Instruction.Call, size(self.arguments))

@dataclass
class GetElement_(Expression_):
    sub: Expression_ = ...
    index: Expression_ = ...
    
    def generate(self) -> None:
        self.sub.generate()
        self.index.generate()
        _writeCode(Instruction.GetElement)

@dataclass
class SetElement_(Expression_):
    sub: Expression_ = ...
    index: Expression_ = ...
    value: Expression_ = ...

    def generate(self) -> None:
        self.value.generate()
        self.sub.generate()
        self.index.generate()
        _writeCode(Instruction.SetElement)

@dataclass
class GetVariable_(Expression_):
    name: str = ...
    
    def generate(self) -> None:
        if (temp := _getLocal(self.name)) == -1:
            _writeCode(Instruction.GetGlobal, self.name)
        else:
            _writeCode(Instruction.GetLocal, temp)

@dataclass
class SetVariable_(Expression_):
    name: str = ...
    value: Expression_ = ...

    def generate(self) -> None:
        self.value.generate()
        if (temp := _getLocal(self.name)) == -1:
            _writeCode(Instruction.SetGlobal, self.name)
        else:
            _writeCode(Instruction.SetLocal, temp)

@dataclass
class NullLiteral_(Expression_):
    def generate(self) -> None:
        _writeCode(Instruction.PushNull)

@dataclass
class BooleanLiteral_(Expression_):
    value: bool = False

    def generate(self) -> None:
        _writeCode(Instruction.PushBoolean, self.value)

@dataclass
class NumberLiteral_(Expression_):
    value: float = 0.0

    def generate(self) -> None:
        _writeCode(Instruction.PushNumber, self.value)

@dataclass
class StringLiteral_(Expression_):
    value: str = ""

    def generate(self) -> None:
        _writeCode(Instruction.PushString, self.value)

@dataclass
class ArrayLiteral_(Expression_):
    values: List[Expression_] = ...

    def generate(self) -> None:
        for value in self.values[::-1]:
            value.generate()
        _writeCode(Instruction.PushArray, size(self.values))

@dataclass
class MapLiteral_(Expression_):
    values: Dict[NullLiteral_ | BooleanLiteral_ | NumberLiteral_ | StringLiteral_, Any] = ...

    def generate(self) -> None:
        for k, v in self.values.items():
            _writeCode(Instruction.PushString, k)
            v.generate()
        _writeCode(Instruction.PushMap, size(self.values))

_nodeNames: Dict[str, object] = {
    'Statement':           Statement_,
    'Expression':          Expression_,
    'Function':            Function_,
    'Program':             Program_,
    'Return':              Return_,
    'Variable':            Variable_,
    'For':                 For_,
    'Break':               Break_,
    'Continue':            Continue_,
    'If':                  If_,
    'Print':               Print_,
    'ExpressionStatement': ExpressionStatement_,
    'Or':                  Or_,
    'And':                 And_,
    'Relational':          Relational_,
    'Arithmetic':          Arithmetic_,
    'Unary':               Unary_,
    'Call':                Call_,
    'GetElement':          GetElement_,
    'SetElement':          SetElement_,
    'GetVariable':         GetVariable_,
    'SetVariable':         SetVariable_,
    'NullLiteral':         NullLiteral_,
    'BooleanLiteral':      BooleanLiteral_,
    'NumberLiteral':       NumberLiteral_,
    'StringLiteral':       StringLiteral_,
    'ArrayLiteral':        ArrayLiteral_,
    'MapLiteral':          MapLiteral_,
}
def _cast(node: Any) -> Any:
    if type(node) is list:
        return [_cast(i) for i in node]
    if type(node) is dict:
        return {_cast(k): _cast(v) for k, v in node.items()}
    if type(node) is _ParsedExp:
        return _cast(node.Expr)
    if (name := node.__class__.__name__) not in _nodeNames:
        return node
    node_: Any = _nodeNames[name]()
    for k, v in node.__dict__.items():
        node_.__setattr__(k, _cast(v))
    return node_

@dataclass()
class _objectCode:
    codeList: List[Code]
    functionTable: Dict[str, Address]

    def __repr__(self):
        return '\n'.join([f"{i:>3d} {self.codeList[i].__repr__()}" for i in range(len(self.codeList))]) +\
               '\n\n' +\
               '\n'.join([f"'{k}': {v}" for k, v in self.functionTable.items()])

def generate(program: Program) -> _objectCode:
    global _codeList, _functionTable
    _codeList.clear()
    _functionTable.clear()
    _writeCode(Instruction.GetGlobal, 'main')
    _writeCode(Instruction.Call, Address(0))
    _writeCode(Instruction.Exit)
    program_: Program_ = _cast(program)
    for node in program_.functions:
        node.generate()
    return _objectCode(_codeList, _functionTable)