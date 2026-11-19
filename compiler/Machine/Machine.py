from dataclasses import dataclass
from typing import List, Dict, Any, Callable

from Generator.Address import Address
from Generator.Code import Code
from Generator.Generator import _objectCode
from Generator.Instruction import Instruction
from Machine.BuiltinFunctionTable import builtinFunctionTable
from Machine.Type import Array, Map, Object

@dataclass
class _StackFrame:
    variables: List[Any]
    operandStack: List[Any]
    instructionPointer: Address

_objects: List[Object] = []
_global: Dict[str, Any] = {}
_callStack: List[_StackFrame] = []

def _pushOperand(value: Any) -> None:
    global _callStack
    _callStack[-1].operandStack.append(value)

def _peekOperand() -> Any:
    global _callStack
    return _callStack[-1].operandStack[-1]

def _popOperand() -> Any:
    global _callStack
    return _callStack[-1].operandStack.pop()

def _collectGarbage() -> None:
    global _callStack
    for i in range(len(_callStack)):
        for j in range(len(_callStack[i].variables)):
            _markObject(_callStack[i].variables, j)
        for j in range(len(_callStack[i].operandStack)):
            _markObject(_callStack[i].operandStack, j)
    for i in range(len(_global.values())):
        _markObject(_global.values(), i)
    _sweepObject()

def _markObject(container: list, index: int) -> None:
    if type(container[index]) is Array:
        if container[index].isMarked: return
        container[index].isMarked = True
        for i in range(len(container[index].values)):
            _markObject(container[index].values, i)
    elif type(container[index]) is Map:
        if container[index].isMarked: return
        container[index].isMarked = True
        for i in range(len(container[index].values.values())):
            _markObject(container[index].values.values(), i)

def _sweepObject() -> None:
    global _objects
    emptyObjectIndex = []
    for i in range(len(_objects)):
        if _objects[i].isMarked:
            _objects[i].isMarked = False
            continue
        emptyObjectIndex.append(i)
    for i in emptyObjectIndex[::-1]:
        del _objects[i]

def _executeExit(_: Code) -> None:
    '''
    _callStack.pop()
    exit()
    '''
    pass

def _executeCall(code: Code) -> None:
    global _callStack
    operand = _popOperand()
    if type(operand) is Address:
        stackFrame: _StackFrame = _StackFrame([], [], operand)
        for _ in range(operand.value):
            stackFrame.variables.append(_callStack[-1].operandStack.pop())
        _callStack.append(stackFrame)
        _callStack[-1].instructionPointer -= 1
        return
    if type(operand) is str and operand in builtinFunctionTable:
        arguments: List[Any] = []
        for _ in range(code.operand.value):
            arguments.append(_popOperand())
        _pushOperand(builtinFunctionTable[operand](arguments))
        return
    raise RuntimeError
        
def _executeAlloc(_: Code) -> None:
    pass

def _executeReturn(_: Code) -> None:
    global _callStack
    result = None
    if _callStack[-1].operandStack:
        result = _callStack[-1].operandStack[-1]
    _callStack.pop()
    if not _callStack: exit()
    _callStack[-1].operandStack.append(result)
    _collectGarbage()
    
def _executeJump(code: Code) -> None:
    global _callStack
    _callStack[-1].instructionPointer = Address(code.operand-1)

def _executeConditionJump(code: Code) -> None:
    global _callStack
    condition = _popOperand()
    if condition: return
    _callStack[-1].instructionPointer = Address(code.operand-1)

def _executePrint(code: Code) -> None:
    for _ in range(int(code.operand)):
        value = _popOperand()
        print(value, end='')

def _executePrintLine(_: Code) -> None:
    print()

def _executeLogicalOr(code: Code) -> None:
    global _callStack
    value = _popOperand()
    if value:
        _pushOperand(value)
        _callStack[-1].instructionPointer = Address(code.operand-1)

def _executeLogicalAnd(code: Code) -> None:
    global _callStack
    value = _popOperand()
    if not value:
        _pushOperand(value)
        _callStack[-1].instructionPointer = Address(code.operand-1)

def _executeAdd(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    if type(rValue) is float and type(lValue) is float:
        _pushOperand(lValue + rValue)
    elif type(rValue) is str and type(lValue) is str:
        _pushOperand(lValue + rValue)
    else:
        raise RuntimeError

def _executeSubtract(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    if type(rValue) is float and type(lValue) is float:
        _pushOperand(lValue - rValue)
    else:
        raise RuntimeError
    
def _executeMultiply(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    if type(rValue) is float and type(lValue) is float:
        _pushOperand(lValue * rValue)
    else:
        raise RuntimeError
    
def _executeDivide(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    if type(rValue) is float and type(lValue) is float and rValue != 0:
        _pushOperand(lValue / rValue)
    else:
        raise RuntimeError
    
def _executeModulo(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    if type(rValue) is float and type(lValue) is float and rValue != 0:
        _pushOperand(lValue % rValue)
    else:
        raise RuntimeError
    
def _executeEqual(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    _pushOperand(lValue == rValue)

def _executeNotEqual(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    _pushOperand(lValue != rValue)

def _executeLessThan(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    if type(rValue) is float and type(lValue) is float:
        _pushOperand(lValue < rValue)
    else:
        raise RuntimeError
    
def _executeGreaterThan(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    if type(rValue) is float and type(lValue) is float:
        _pushOperand(lValue > rValue)
    else:
        raise RuntimeError
    
def _executeLessEqual(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    if type(rValue) is float and type(lValue) is float:
        _pushOperand(lValue <= rValue)
    else:
        raise RuntimeError
    
def _executeGreaterEqual(_: Code) -> None:
    rValue = _popOperand()
    lValue = _popOperand()
    if type(rValue) is float and type(lValue) is float:
        _pushOperand(lValue >= rValue)
    else:
        raise RuntimeError
   
def _executeAbsolute(_: Code) -> None:
    value = _popOperand()
    if type(value) is float:
        _pushOperand(abs(value))
    else:
        raise RuntimeError

def _executeReverseSign(_: Code) -> None:
    value = _popOperand()
    if type(value) is float:
        _pushOperand(value * -1)
    else:
        raise RuntimeError

def _executeGetElement(_: Code) -> None:
    index = _popOperand()
    sub = _popOperand()
    if type(sub) is list and type(index) is int:
        _pushOperand(sub[index])
    elif type(sub) is dict and type(index) is str:
        _pushOperand(sub[index])
    else:
        raise RuntimeError

def _executeSetElement(_: Code) -> None:
    index = _popOperand()
    sub = _popOperand()
    if type(sub) is Array and type(index) is int:
        sub.values[index] = _peekOperand()
    elif type(sub) is Map and type(index) is str:
        sub.values[index] = _peekOperand()

def _executeGetGlobal(code: Code) -> None:
    global _global, functionTable
    name = str(code.operand)
    if name in functionTable:
        _pushOperand(functionTable[name])
    elif name in builtinFunctionTable:
        _pushOperand(builtinFunctionTable[name])
    elif name in  _global:
        _pushOperand(_global[name])
    else:
        raise RuntimeError

def _executeSetGlobal(code: Code) -> None:
    global _global
    name = code.operand
    _global[name] = _peekOperand()

def _executeGetLocal(code: Code) -> None:
    global _callStack
    index = Address(code.operand)
    _pushOperand(_callStack[-1].variables[index])

def _executeSetLocal(code: Code) -> None:
    global _callStack
    index = Address(code.operand)
    _callStack[-1].variables[index] = _peekOperand()

def _executePushNull(_: Code) -> None:
    _pushOperand(None)

def _executePushBoolean(code: Code) -> None:
    _pushOperand(code.operand)

def _executePushNumber(code: Code) -> None:
    _pushOperand(code.operand)

def _executePushString(code: Code) -> None:
    _pushOperand(code.operand)

def _executePushArray(code: Code) -> None:
    global _objects
    result = Array()
    size = code.operand
    for _ in range(size, 0, -1):
        result.values.append(_popOperand())
    _pushOperand(result)
    _objects.append(result)

def _executePushMap(code: Code) -> None:
    global _objects
    result = Map()
    for _ in range(code.operand):
        value = _popOperand()
        key = str(_popOperand())
        result.values[key] = value
    _pushOperand(result)
    _objects.append(result)

def _executePopOperand(_: Code) -> None:
    _popOperand()

_executeTable: Dict[Instruction, Callable[[Code], None]] = {
    Instruction.Exit          : _executeExit,
    Instruction.Call          : _executeCall,
    Instruction.Alloc         : _executeAlloc,
    Instruction.Return        : _executeReturn,
    Instruction.Jump          : _executeJump,
    Instruction.ConditionJump : _executeConditionJump,
    Instruction.Print         : _executePrint,
    Instruction.PrintLine     : _executePrintLine,
    Instruction.LogicalOr     : _executeLogicalOr,
    Instruction.LogicalAnd    : _executeLogicalAnd,
    Instruction.Add           : _executeAdd,
    Instruction.Subtract      : _executeSubtract,
    Instruction.Multiply      : _executeMultiply,
    Instruction.Divide        : _executeDivide,
    Instruction.Modulo        : _executeModulo,
    Instruction.Equal         : _executeEqual,
    Instruction.NotEqual      : _executeNotEqual,
    Instruction.LessThan      : _executeLessThan,
    Instruction.GreaterThan   : _executeGreaterThan,
    Instruction.LessEqual     : _executeLessEqual,
    Instruction.GreaterEqual  : _executeGreaterEqual,
    Instruction.Absolute      : _executeAbsolute,
    Instruction.ReverseSign   : _executeReverseSign,
    Instruction.GetElement    : _executeGetElement,
    Instruction.SetElement    : _executeSetElement,
    Instruction.GetGlobal     : _executeGetGlobal,
    Instruction.SetGlobal     : _executeSetGlobal,
    Instruction.GetLocal      : _executeGetLocal,
    Instruction.SetLocal      : _executeSetLocal,
    Instruction.PushNull      : _executePushNull,
    Instruction.PushBoolean   : _executePushBoolean,
    Instruction.PushNumber    : _executePushNumber,
    Instruction.PushString    : _executePushString,
    Instruction.PushArray     : _executePushArray,
    Instruction.PushMap       : _executePushMap,
    Instruction.PopOperand    : _executePopOperand,
}
def execute(objectCode: _objectCode) -> None:
    global _callStack, functionTable
    _callStack.append(_StackFrame([], [], Address(0)))
    codeList = objectCode.codeList
    functionTable = objectCode.functionTable
    while True:
        code: Code = codeList[_callStack[-1].instructionPointer.value]
        _executeTable[code.instruction](code)
        _callStack[-1].instructionPointer += 1