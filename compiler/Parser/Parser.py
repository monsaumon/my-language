from dataclasses import dataclass
from typing import List, Set

from Scanner.Token import Token
from Parser.Node import *
from Scanner.Kind import Kind

class _Current:
    def __init__(self, tokenList: List[Token]):
        self.tokenList = tokenList
        self.token = self.tokenList[0]
        self.current = 0
    
    def plus(self):
        self.current += 1
        self.token = self.tokenList[self.current]

    def minus(self):
        self.current -= 1
        self.token = self.tokenList[self.current]

@dataclass(repr=False)
class _ParsedExp:
    Expr: Expression
    Extype: str

    def __repr__(self):
        return f"{self.Expr}"

def _skipCurrent(kind: Kind) -> None:
    if current.token.kind != kind:
        raise RuntimeError(f"{kind} 토큰이 필요합니다.")
    current.plus()

def _skipCurrentIf(kind: Kind) -> bool:
    if current.token.kind != kind:
        return False
    current.plus()
    return True

def _parseNullLiteral() -> _ParsedExp:
    _skipCurrent(Kind.NullLiteral)
    result = NullLiteral()
    return _ParsedExp(result, "Null")

def _parseBooleanLiteral() -> _ParsedExp:
    result = BooleanLiteral()
    result.value = current.token.kind == Kind.TrueLiteral
    current.plus()
    return _ParsedExp(result, "Bool")

def _parseNumberLiteral() -> _ParsedExp:
    result = NumberLiteral()
    result.value = float(current.token.string)
    _skipCurrent(Kind.NumberLiteral)
    return _ParsedExp(result, "Number")

def _parseStringLiteral() -> _ParsedExp:
    result = StringLiteral()
    result.value = current.token.string
    _skipCurrent(Kind.StringLiteral)
    return _ParsedExp(result, "String")

def _parseArrayLiteral() -> _ParsedExp:
    result = ArrayLiteral(values = [])
    _skipCurrent(Kind.LeftBracket)
    if current.token.kind != Kind.RightBracket:
        result.values.append(_parseExpression())
        while _skipCurrentIf(Kind.Comma):
            result.values.append(_parseExpression())
    _skipCurrent(Kind.RightBracket)
    return _ParsedExp(result, "Array")

def _parseMapLiteral() -> _ParsedExp:
    result = MapLiteral(values = {})
    _skipCurrent(Kind.LeftBrace)
    def do():
        name = current.token.string
        _skipCurrent(Kind.StringLiteral)
        _skipCurrent(Kind.Colon)
        value = _parseExpression()
        result.values[name] = value
    if current.token.kind != Kind.RightBrace:
        do()
        while _skipCurrentIf(Kind.Comma): do()
    _skipCurrent(Kind.RightBrace)
    return _ParsedExp(result, "Map")

def _parseIdentifier() -> _ParsedExp:
    result = GetVariable()
    result.name = current.token.string
    _skipCurrent(Kind.Identifier)
    return _ParsedExp(result, "Identifier")

def _parseInnerExpression() -> _ParsedExp:
    _skipCurrent(Kind.LeftParen)
    result = _parseExpression()
    _skipCurrent(Kind.RightParen)
    return _ParsedExp(result.Expr, result.Extype)

def _parseCall(sub: _ParsedExp) -> _ParsedExp:
    result = Call(arguments = [])
    result.sub = sub.Expr
    _skipCurrent(Kind.LeftParen)
    if current.token.kind != Kind.RightParen:
        result.arguments.append(_parseExpression())
        while _skipCurrentIf(Kind.Comma):
            result.arguments.append(_parseExpression())
    _skipCurrent(Kind.RightParen)
    return _ParsedExp(result, "Call")

def _parseElement(sub: _ParsedExp) -> _ParsedExp:
    result = GetElement()
    result.sub = sub.Expr
    _skipCurrent(Kind.LeftBracket)
    result.index = _parseExpression().Expr
    _skipCurrent(Kind.RightBracket)
    return _ParsedExp(result, "Element")

def _parsePostfix(sub: _ParsedExp) -> _ParsedExp:
    while True:
        K = current.token.kind
        if K == Kind.LeftParen: sub = _parseCall(sub)
        elif K == Kind.LeftBracket: sub = _parseElement(sub)
        else: return sub

def _parseOperand() -> _ParsedExp:
    K = current.token.kind
    if K == Kind.NullLiteral:                               result = _parseNullLiteral()
    elif K == Kind.TrueLiteral or K == Kind.FalseLiteral:   result = _parseBooleanLiteral()
    elif K == Kind.NumberLiteral:                           result = _parseNumberLiteral()
    elif K == Kind.StringLiteral:                           result = _parseStringLiteral()
    elif K == Kind.LeftBracket:                             result = _parseArrayLiteral()
    elif K == Kind.LeftBrace:                               result = _parseMapLiteral()
    elif K == Kind.Identifier:                              result = _parseIdentifier()
    elif K == Kind.LeftParen:                               result = _parseInnerExpression()
    else:                                                   raise RuntimeError("잘못된 식입니다.")
    return _parsePostfix(result)


def _parseUnary() -> _ParsedExp:
    operators: Set[Kind] = set([
        Kind.Add,
        Kind.Subtract,
    ])
    if current.token.kind in operators:
        result = Unary()
        result.kind = current.token.kind
        current.plus()
        temp = _parseUnary()
        result.sub = temp.Expr
        return _ParsedExp(result, temp.Extype)
    return _parseOperand()

def _parseMulDivMod() -> _ParsedExp:
    operators: Set[Kind] = set([
        Kind.Multiply,
        Kind.Divide,
        Kind.Modulo,
    ])
    result = _parseUnary()
    while current.token.kind in operators:
        temp = Arithmetic()
        temp.kind = current.token.kind
        current.plus()
        temp.left = result.Expr
        temp.right = (temp2 := _parseUnary()).Expr
        if result.Extype == "Identifier" or temp2.Extype == "Identifier": result = _ParsedExp(temp, "Identifier")
        elif result.Extype == "Number" and temp2.Extype == "Number": result = _ParsedExp(temp, "Number")
        elif temp.kind == Kind.Multiply:
            if result.Extype == "Number" and temp2.Extype == "String": result = _ParsedExp(temp, "String")
            elif result.Extype == "String" and temp2.Extype == "Number": result = _ParsedExp(temp, "String")
            else: raise TypeError
    return result

def _parsePlusMinus() -> _ParsedExp:
    operators: Set[Kind] = set([
        Kind.Add,
        Kind.Subtract,
    ])
    result = _parseMulDivMod()
    while current.token.kind in operators:
        temp = Arithmetic()
        temp.kind = current.token.kind
        current.plus()
        temp.left = result.Expr
        temp.right = (temp2 := _parseMulDivMod()).Expr
        if result.Extype == "Identifier" or temp2.Extype == "Identifier": result = _ParsedExp(temp, "identifier")
        elif result.Extype == "Number" and temp2.Extype == "Number": result = _ParsedExp(temp, "Number")
        elif temp.kind == Kind.Add and result.Extype == "String" and temp2.Extype == "String": result = _ParsedExp(temp, "String")
        else: raise TypeError
    return result

def _parseRelational() -> _ParsedExp:
    operators: Set[Kind] = set([
        Kind.Equal,
        Kind.NotEqual,
        Kind.LessThan,
        Kind.LessEqual,
        Kind.GreaterThan,
        Kind.GreaterEqual,
    ])
    result = _parsePlusMinus()
    while current.token.kind in operators:
        temp = Relational()
        temp.kind = current.token.kind
        current.plus()
        temp.left = result.Expr
        temp.right = _parsePlusMinus().Expr
        result = _ParsedExp(temp, "Bool")
    return result
    

def _parseAnd() -> _ParsedExp:
    result = _parseRelational()
    while _skipCurrentIf(Kind.LogicalAnd):
        temp = And()
        temp.left = result.Expr
        temp.right = _parseRelational().Expr
        result = _ParsedExp(temp, "Bool")
    return result

def _parseOr() -> _ParsedExp:
    result = _parseAnd()
    while _skipCurrentIf(Kind.LogicalOr):
        temp = Or()
        temp.left = result.Expr
        temp.right = _parseAnd().Expr
        result = _ParsedExp(temp, "Bool")
    return result

def _parseAssignment() -> _ParsedExp:
    result = _parseOr()
    if current.token.kind != Kind.Assignment:
        return result
    _skipCurrent(Kind.Assignment)
    if result.Extype == "Identifier":
        tempGV: GetVariable = result.Expr
        result = SetVariable()
        result.name = tempGV.name
        result.value = _parseAssignment().Expr
        return _ParsedExp(result, "Identifier")
    if result.Extype == "Element":
        tempGE: GetElement = result.Expr
        result = SetElement()
        result.sub = tempGE.sub
        result.index = tempGE.index
        result.value = (tempV := _parseAssignment()).Expr
        return _ParsedExp(result, tempV.Extype)
    raise RuntimeError("잘못된 대입 연산 식입니다.")

def _parseExpression() -> _ParsedExp:
    return _parseAssignment()

def _parseVariable() -> Variable:
    result: Variable = Variable()
    _skipCurrent(Kind.Variable)
    result.name = current.token.string
    _skipCurrent(Kind.Identifier)
    _skipCurrent(Kind.Assignment)
    result.expression = _parseExpression().Expr
    _skipCurrent(Kind.SemiColon)
    return result

def _parseFor() -> For:
    result: For = For()
    _skipCurrent(Kind.For)
    result.variable = Variable()
    result.variable.name = current.token.string
    _skipCurrent(Kind.Identifier)
    _skipCurrent(Kind.Assignment)
    result.variable.expression = _parseExpression().Expr
    if not result.variable.expression: raise RuntimeError("for문에 초기화 식이 없습니다.")
    _skipCurrent(Kind.Comma)
    result.condition = _parseExpression().Expr
    if not result.condition: raise RuntimeError("for문에 조건식이 없습니다.")
    _skipCurrent(Kind.Comma)
    result.expression = _parseExpression().Expr
    if not result.expression: raise RuntimeError("for문에 증감식이 없습니다.")
    _skipCurrent(Kind.LeftBrace)
    result.block = _parseBlock()
    _skipCurrent(Kind.RightBrace)
    return result

def _parseIf() -> If:
    result: If = If(conditions = [], blocks = [], elseBlock = [])
    _skipCurrent(Kind.If)
    def do():
        condition = _parseExpression().Expr
        if not condition: raise RuntimeError("if문에 조건식이 없습니다.")
        result.conditions.append(condition)
        _skipCurrent(Kind.LeftBrace)
        result.blocks.append(_parseBlock())
        _skipCurrent(Kind.RightBrace)
    do()
    while _skipCurrentIf(Kind.Elif): do()
    if _skipCurrentIf(Kind.Else):
        _skipCurrent(Kind.LeftBrace)
        result.elseBlock = _parseBlock()
        _skipCurrent(Kind.RightBrace)
    return result

def _parsePrint() -> Print:
    result: Print = Print(arguments = [])
    result.lineFeed = current.token.kind == Kind.PrintLine
    current.plus()
    if current.token.kind != Kind.SemiColon:
        result.arguments.append(_parseExpression().Expr)
        while _skipCurrentIf(Kind.Comma): result.arguments.append(_parseExpression().Expr)
    _skipCurrent(Kind.SemiColon)
    return result

def _parseReturn() -> Return:
    result: Return = Return()
    _skipCurrent(Kind.Return)
    result.expression = _parseExpression().Expr
    if not result.expression: result.expression = NullLiteral()
    _skipCurrent(Kind.SemiColon)
    return result

def _parseBreak() -> Break:
    result: Break = Break()
    _skipCurrent(Kind.Break)
    _skipCurrent(Kind.SemiColon)
    return result

def _parseContinue() -> Continue:
    result: Continue = Continue()
    _skipCurrent(Kind.Continue)
    _skipCurrent(Kind.SemiColon)
    return result

def _parseExpressionStatement() -> ExpressionStatement:
    result: ExpressionStatement = ExpressionStatement()
    result.expression = _parseExpression().Expr
    _skipCurrent(Kind.SemiColon)
    return result

def _parseBlock() -> List[Statement]:
    result: List[Statement] = []
    while current.token.kind != Kind.RightBrace:
        K = current.token.kind
        if K == Kind.EndOfList:                         raise RuntimeError(f"{current.token} 잘못된 구문입니다.")
        elif K == Kind.Variable:                        result.append(_parseVariable())
        elif K == Kind.For:                             result.append(_parseFor())
        elif K == Kind.If:                              result.append(_parseIf())
        elif K == Kind.Print or K == Kind.PrintLine:    result.append(_parsePrint())
        elif K == Kind.Return:                          result.append(_parseReturn())
        elif K == Kind.Break:                           result.append(_parseBreak())
        elif K == Kind.Continue:                        result.append(_parseContinue())
        else:                                           result.append(_parseExpressionStatement())
    return result

def _parseFunction() -> Function:
    result: Function = Function(parameters = [])
    _skipCurrent(Kind.Function)
    result.name = current.token.string
    _skipCurrent(Kind.Identifier)
    _skipCurrent(Kind.LeftParen)
    if current.token.kind != Kind.RightParen:
        result.parameters.append(current.token.string)
        _skipCurrent(Kind.Identifier)
        while(_skipCurrentIf(Kind.Comma)):
            result.parameters.append(current.token.string)
            _skipCurrent(Kind.Identifier)
    _skipCurrent(Kind.RightParen)
    _skipCurrent(Kind.LeftBrace)
    result.block = _parseBlock()
    _skipCurrent(Kind.RightBrace)
    return result

def parse(tokens: List[Token]) -> Program:
    global current
    result: Program = Program(functions = [])
    current = _Current(tokens)
    while current.token.kind != Kind.EndOfList:
        K = current.token.kind
        if K == Kind.Function:
            result.functions.append(_parseFunction())
        else:
            raise RuntimeError(f"{current.token} 잘못된 구문입니다.")
    return result