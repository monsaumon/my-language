from dataclasses import dataclass
from abc import *
from typing import List, Dict

from Kind import Kind
from BuiltinFunctionTable import builtinFunctionTable

#Expression(식)의 반환형
@dataclass
class ExReturn:
    value: ...
    Extype: str

#Return, Break, Continue 처리를 위한 커스텀 에러
@dataclass
class ReturnException(Exception):
    result: ExReturn

class BreakException(Exception): ...
class ContinueException(Exception): ...

#모든 문 노드의 부모 노드
@dataclass
class Statement(metaclass = ABCMeta):
    def __nonzero__(self) -> bool:
        return any(vars(self).values())
    
    #실행 시 노드 순회를 위한 함수
    @abstractmethod
    def visit(self) -> None: ...

#모든 식 노드의 부모 노드
@dataclass
class Expression(metaclass = ABCMeta):
    
    def __nonzero__(self) -> bool:
        return any(vars(self).values())

    #실행 시 노드 순회를 위한 함수
    @abstractmethod
    def visit(self) -> ExReturn: ...

#함수 노드
@dataclass
class Function(Statement):
    name: str = ...
    parameters: List[str] = ...
    block: List[Statement] = ...

    def visit(self) -> None:
        for node in self.block:
            node.visit()

#프로그램 전체의 노드
@dataclass
class Program:
    functions: List[Function] = ...

#Parser(어휘 분석기)의 반환형
@dataclass
class ParsedExp:
    Expr: Expression
    Extype: str

#메모리에 저장되는 변수값 객체
@dataclass
class Value:
    Value: ... = ...
    Vtype: str = ...
    Vloc: str = ...

#변수 저장 메모리 객체
class Containers:
    def __init__(self):
        self.globalv: Dict[str, ExReturn] = {}
        self.localv: List[List[Dict[str, ExReturn]]] = []
        self.functionTable: Dict[str, Function] = {}
        self.builtinFunctionTable = builtinFunctionTable

    def clear(self):
        self.globalv = {}
        self.localv = []
        self.functionTable = {}
    
    def getValue(self, name: str) -> Value:
        if name in self.localv[-1][0].keys():
            v = self.localv[-1][0][name]
            return Value(v.value, v.Extype, "Local")
        if name in self.globalv.keys():
            v = self.globalv[name]
            return Value(v.value, v.Extype, "Global")
        return Value(0, "Null", "None")

#메모리
C = Containers()

#Identifier(이름)을 받아 그 이름으로 저장된 메모리의 값을 반환하는 함수
def getIdentifierValue(identifier: str) -> Value:
    global C
    return C.getValue(identifier)

#Identifier(이름)은 실질적인 자료형이 저장되어있지 않아 자료형을 바꿔 반환하는 함수
def processExp(exrt: ExReturn) -> ExReturn:
    if exrt.Extype == "Identifier":
        v = getIdentifierValue(exrt.value)
        return ExReturn(v.Value, v.Vtype)
    return exrt
        
#return문 노드
@dataclass
class Return(Statement):
    expression: Expression = ...

    def visit(self) -> None:
        raise ReturnException(self.expression.visit())

#변수 선언 노드
@dataclass
class Variable(Statement):
    name: str = ...
    expression: Expression = ...

    def visit(self) -> None:
        global C
        C.localv[-1][0][self.name] = self.expression.visit()

#for문 노드
@dataclass
class For(Statement):
    variable: Variable = ...
    condition: Expression = ...
    expression: Expression = ...
    block: List[Statement] = ...

    def visit(self) -> None:
        global C
        C.localv[-1].insert(0, {})
        self.variable.visit()
        while True:
            result = self.condition.visit().value
            if not result: break
            try:
                for node in self.block:
                    node.visit()
            except ContinueException:
                pass
            except BreakException:
                break
            self.expression.visit()
        C.localv[-1].pop(0)

#break문 노드
@dataclass
class Break(Statement):
    def visit(self) -> None: raise BreakException

#continue문 노드
@dataclass
class Continue(Statement):
    def visit(self) -> None: raise ContinueException

#if문 노드
@dataclass
class If(Statement):
    conditions: List[Expression] = ...
    blocks: List[List[Statement]] = ...
    elseBlock: List[Statement] = ...

    def visit(self) -> None:
        for i in range(len(self.conditions)):
            if not self.conditions[i].visit().value:
                continue
            C.localv[-1].insert(0, {})
            for node in self.blocks[i]:
                node.visit()
            C.localv[-1].pop(0)
            return
        if not self.elseBlock:
            return
        C.localv[-1].insert(0, {})
        for node in self.elseBlock:
            node.visit()
        C.localv[-1].pop(0)

#print문 노드
@dataclass
class Print(Statement):
    lineFeed: bool = False
    arguments: List[ParsedExp] = ...

    def visit(self) -> None:
        def _processExrt(exrt: ExReturn) -> str:
            if exrt.Extype == "Null":
                return ''
            if exrt.Extype == "Bool":
                return str(exrt.value)
            if exrt.Extype == "Number":
                return str(exrt.value)
            if exrt.Extype == "String":
                return exrt.value
            if exrt.Extype == "Array":
                return '['+', '.join(map(lambda x:str(x.value), exrt.value))+']'
            if exrt.Extype == "Map":
                ...
            if exrt.Extype == "Identifier":
                exrt = processExp(exrt)
                return _processExrt(exrt)
        
        args: List[str] = []
        for pexp in self.arguments:
            args.append(_processExrt(pexp.Expr.visit()))

        print(' '.join(args), end='')
        if self.lineFeed: print()

#사용되지 않은 식(그냥 1+2; 같은 것)을 처리하기 위한 노드
@dataclass
class ExpressionStatement(Statement):
    expression: Expression = ...

    def visit(self) -> None:
        self.expression.visit()

#or 노드
@dataclass
class Or(Expression):
    left: Expression = ...
    right: Expression = ...

    def visit(self) -> ExReturn:
        if self.left.visit().value:
            return self.left.visit()
        else:
            return self.right.visit()

#and 노드
@dataclass
class And(Expression):
    left: Expression = ...
    right: Expression = ...

    def visit(self) -> ExReturn:
        if not self.left.visit().value:
            return self.left.visit()
        else:
            return self.right.visit()

#관계연산자 노드
@dataclass
class Relational(Expression):
    kind: Kind = ...
    left: Expression = ...
    right: Expression = ...

    def visit(self) -> ExReturn:
        lValue = self.left.visit()
        rValue = self.right.visit()

        lValue = processExp(lValue)
        rValue = processExp(rValue)

        if self.kind == Kind.EqualEqual:
            if lValue.Extype == "Null" and rValue.Extype == "Null":
                return ExReturn(True, "Bool")
            if lValue.Extype == "Bool" and rValue.Extype == "Bool":
                return ExReturn(bool(lValue.value == rValue.value), "Bool")
            if lValue.Extype == "Number" and rValue.Extype == "Number":
                return ExReturn(bool(lValue.value == rValue.value), "Bool")
            if lValue.Extype == "String" and rValue.Extype == "String":
                return ExReturn(bool(lValue.value == rValue.value), "Bool")
        if self.kind == Kind.NotEqual:
            if lValue.Extype == "Null" and rValue.Extype == "Null":
                return ExReturn(False, "Bool")
            if lValue.Extype == "Null" or rValue.Extype == "Null":
                return ExReturn(True, "Bool")
            if lValue.Extype == "Bool" and rValue.Extype == "Bool":
                return ExReturn(bool(lValue.value != rValue.value), "Bool")
            if lValue.Extype == "Number" and rValue.Extype == "Number":
                return ExReturn(bool(lValue.value != rValue.value), "Bool")
            if lValue.Extype == "String" and rValue.Extype == "String":
                return ExReturn(bool(lValue.value != rValue.value), "Bool")
        if lValue.Extype == "Number" and rValue.Extype == "Number":
            if self.kind == Kind.LessThan:
                return ExReturn(bool(lValue.value < rValue.value), "Bool")
            if self.kind == Kind.LessEqual:
                return ExReturn(bool(lValue.value <= rValue.value), "Bool")
            if self.kind == Kind.GreaterThan:
                return ExReturn(bool(lValue.value > rValue.value), "Bool")
            if self.kind == Kind.GreaterEqual:
                return ExReturn(bool(lValue.value >= rValue.value), "Bool")
        raise TypeError

#산술연산자 노드
@dataclass
class Arithmetic(Expression):
    kind: Kind = ...
    left: Expression = ...
    right: Expression = ...

    def visit(self) -> ExReturn:
        lValue = self.left.visit()
        rValue = self.right.visit()

        lValue = processExp(lValue)
        rValue = processExp(rValue)

        if lValue.Extype == "Bool":
            if lValue.value: lValue = ExReturn(1, "Number")
            else: lValue = ExReturn(0, "Number")
        if rValue.Extype == "Bool":
            if rValue.value: rValue = ExReturn(1, "Number")
            else: rValue = ExReturn(0, "Number")

        if self.kind == Kind.Plus:
            if lValue.Extype == "Number" and rValue.Extype == "Number":
                return ExReturn(lValue.value + rValue.value, "Number")
            if lValue.Extype == "String" and rValue.Extype == "String":
                return ExReturn(lValue.value + rValue.value, "String")
        if self.kind == Kind.Minus and lValue.Extype == "Number" and rValue.Extype == "Number":
            return ExReturn(lValue.value - rValue.value, "Number")
        if self.kind == Kind.Star and lValue.Extype == "Number" and rValue.Extype == "Number":
            return ExReturn(lValue.value * rValue.value, "Number")
        if self.kind == Kind.Star and lValue.Extype == "String" and rValue.Extype == "Number":
            return ExReturn(lValue.value * rValue.value, "String")
        if self.kind == Kind.Star and lValue.Extype == "Number" and rValue.Extype == "String":
            return ExReturn(lValue.value * rValue.value, "String")
        if self.kind == Kind.Slash and lValue.Extype == "Number" and rValue.Extype == "Number":
            return ExReturn(lValue.value / rValue.value, "Number")
        if self.kind == Kind.Modulo and lValue.Extype == "Number" and rValue.Extype == "Number":
            return ExReturn(lValue.value % rValue.value, "Number")
        raise RuntimeError("Arithmetic not variable")

#단항연산자 노드
@dataclass
class Unary(Expression):
    kind: Kind = ...
    sub: Expression = ...

    def visit(self) -> ExReturn:
        value = self.sub.visit()
        if self.kind == Kind.Plus and value.Extype == "Number": return ExReturn(abs(value.value), "Number")
        if self.kind == Kind.Minus and value.Extype == "Number": return ExReturn(value.value * -1, "Number")
        return ExReturn(0, "Null")

#함수 호출 노드
@dataclass
class Call(Expression):
    sub: Expression = ...
    arguments: List[ParsedExp] = ...

    def visit(self) -> ExReturn:
        global C
        value = self.sub.visit()
        if value.Extype == "BuiltinFunction":
            values: List[ExReturn] = [arg.Expr.visit() for arg in self.arguments]
            return value.value(values)
        if value.Extype != "Function":
            raise NameError
        parameters: Dict[str, ExReturn] = {name: exr for name, exr in map(lambda x, y: (x, y.Expr.visit()), value.value.parameters, self.arguments)}
        C.localv.append([])
        C.localv[-1].insert(0, parameters)
        try:
            value.value.visit()
        except ReturnException as e:
            C.localv.pop()
            return e.result
        C.localv.pop()
        return ExReturn(0, "Null")

#원소 값 참조(사용) 노드
@dataclass
class GetElement(Expression):
    sub: Expression = ...
    index: Expression = ...

    def visit(self) -> ExReturn:
        obj = self.sub.visit()
        idx = self.index.visit()
        if obj.Extype == "Array" and idx.Extype == "Number":
            if '.' in str(idx.value).rstrip('.0'): raise TypeError
            return obj.value[int(idx.value)]
        if obj.Extype == "Map" and idx.Extype == "String":
            return obj.value[idx.value]
        raise TypeError

#원소 수정 노드
@dataclass
class SetElement(Expression):
    sub: Expression = ...
    index: Expression = ...
    value: Expression = ...

    def visit(self) -> ExReturn:
        obj = self.sub.visit()
        idx = self.index.visit()
        val = self.value.visit()
        if obj.Extype == "Array" and idx.Extype == "Number":
            obj.value[int(idx.value)] = val
            return val
        if obj.Extype == "Map" and idx.Extype == "String":
            obj.value[idx.value] = val
            return val
        raise TypeError

#변수 값 참조(사용) 노드
@dataclass
class GetVariable(Expression):
    name: str = ...

    def visit(self) -> ExReturn:
        global C
        for vars in C.localv[-1]:
            if self.name in vars.keys():
                return vars[self.name]
        if self.name in C.globalv.keys():
            return C.globalv[self.name]
        if self.name in C.functionTable.keys():
            return ExReturn(C.functionTable[self.name], "Function")
        if self.name in C.builtinFunctionTable.keys():
            return ExReturn(builtinFunctionTable[self.name], "BuiltinFunction")
        raise NameError

#변수 수정 노드
@dataclass
class SetVariable(Expression):
    name: str = ...
    value: Expression = ...

    def visit(self) -> ExReturn:
        global C
        for i in range(len(C.localv[-1])):
            if self.name in C.localv[-1][i]:
                C.localv[-1][i][self.name] = self.value.visit()
                return C.localv[-1][i][self.name]
        C.globalv[self.name] = self.value.visit()
        return C.globalv[self.name]

#NULL 노드
@dataclass
class NullLiteral(Expression):
    def visit(self) -> ExReturn:
        return ExReturn(0, "Null")

#bool 노드
@dataclass
class BooleanLiteral(Expression):
    value: bool = False

    def visit(self) -> ExReturn:
        return ExReturn(self.value, "Bool")

#숫자 노드
@dataclass
class NumberLiteral(Expression):
    value: float = 0.0

    def visit(self) -> ExReturn:
        return ExReturn(self.value, "Number")

#문자열 노드
@dataclass
class StringLiteral(Expression):
    value: str = ""

    def visit(self) -> ExReturn:
        return ExReturn(self.value, "String")

#배열 노드
@dataclass
class ArrayLiteral(Expression):
    values: List[ParsedExp] = ...

    def visit(self) -> ExReturn:
        result: List[ExReturn] = []
        for pexp in self.values:
            result.append(pexp.Expr.visit())
        return ExReturn(result, "Array")

#맵 노드
@dataclass
class MapLiteral(Expression):
    values: Dict[str, ParsedExp]

    def visit(self) -> ExReturn:
        result: Dict[str, ExReturn] = {}
        for key, value in self.values.items():
            result[key] = value.Expr.visit()
        return ExReturn(result, "Map")