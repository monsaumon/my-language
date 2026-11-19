from dataclasses import dataclass
from typing import List, Set

from Token import Token
from Node import *

class Current:
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

@dataclass
class ParsedExp:
    Expr: Expression
    Extype: str

def skipCurrent(kind: Kind) -> None:
    if current.token.kind != kind:
        raise RuntimeError(f"{kind} 토큰이 필요합니다.")
    current.plus()

def skipCurrentIf(kind: Kind) -> bool:
    if current.token.kind != kind:
        return False
    current.plus()
    return True

def parseNullLiteral() -> ParsedExp:
    skipCurrent(Kind.NullLiteral)
    result = NullLiteral()
    return ParsedExp(result, "Null")

def parseBooleanLiteral() -> ParsedExp:
    result = BooleanLiteral()
    result.value = current.token.kind == Kind.TrueLiteral
    current.plus()
    return ParsedExp(result, "Bool")

def parseNumberLiteral() -> ParsedExp:
    result = NumberLiteral()
    result.value = float(current.token.string)
    skipCurrent(Kind.NumberLiteral)
    return ParsedExp(result, "Number")

def parseStringLiteral() -> ParsedExp:
    result = StringLiteral()
    result.value = current.token.string
    skipCurrent(Kind.StringLiteral)
    return ParsedExp(result, "String")

def parseArrayLiteral() -> ParsedExp:
    result = ArrayLiteral(values = [])
    skipCurrent(Kind.LeftBracket)
    if current.token.kind != Kind.RightBracket:
        result.values.append(parseExpression())
        while skipCurrentIf(Kind.Comma):
            result.values.append(parseExpression())
    skipCurrent(Kind.RightBracket)
    return ParsedExp(result, "Array")

def parseMapLiteral() -> ParsedExp:
    result = MapLiteral(values = {})
    skipCurrent(Kind.LeftBrace)
    def do():
        name = current.token.string
        skipCurrent(Kind.StringLiteral)
        skipCurrent(Kind.Colon)
        value = parseExpression()
        result.values[name] = value
    if current.token.kind != Kind.RightBrace:
        do()
        while skipCurrentIf(Kind.Comma): do()
    skipCurrent(Kind.RightBrace)
    return ParsedExp(result, "Map")

def parseIdentifier() -> ParsedExp:
    result = GetVariable()
    result.name = current.token.string
    skipCurrent(Kind.Identifier)
    return ParsedExp(result, "Identifier")

def parseInnerExpression() -> ParsedExp:
    skipCurrent(Kind.LeftParen)
    result = parseExpression()
    skipCurrent(Kind.RightParen)
    return ParsedExp(result.Expr, result.Extype)

def parseCall(sub: ParsedExp) -> ParsedExp:
    result = Call(arguments = [])
    result.sub = sub.Expr
    skipCurrent(Kind.LeftParen)
    if current.token.kind != Kind.RightParen:
        result.arguments.append(parseExpression())
        while skipCurrentIf(Kind.Comma):
            result.arguments.append(parseExpression())
    skipCurrent(Kind.RightParen)
    return ParsedExp(result, "Call")

def parseElement(sub: ParsedExp) -> ParsedExp:
    result = GetElement()
    result.sub = sub.Expr
    skipCurrent(Kind.LeftBracket)
    result.index = parseExpression().Expr
    skipCurrent(Kind.RightBracket)
    return ParsedExp(result, "Element")

def parsePostfix(sub: ParsedExp) -> ParsedExp:
    while True:
        K = current.token.kind
        if K == Kind.LeftParen: sub = parseCall(sub)
        elif K == Kind.LeftBracket: sub = parseElement(sub)
        else: return sub

def parseOperand() -> ParsedExp:
    K = current.token.kind
    if K == Kind.NullLiteral:                               result = parseNullLiteral()
    elif K == Kind.TrueLiteral or K == Kind.FalseLiteral:   result = parseBooleanLiteral()
    elif K == Kind.NumberLiteral:                           result = parseNumberLiteral()
    elif K == Kind.StringLiteral:                           result = parseStringLiteral()
    elif K == Kind.LeftBracket:                             result = parseArrayLiteral()
    elif K == Kind.LeftBrace:                               result = parseMapLiteral()
    elif K == Kind.Identifier:                              result = parseIdentifier()
    elif K == Kind.LeftParen:                               result = parseInnerExpression()
    else:                                                   raise RuntimeError("잘못된 식입니다.")
    return parsePostfix(result)


def parseUnary() -> ParsedExp:
    operators: Set[Kind] = set([
        Kind.Plus,
        Kind.Minus,
    ])
    if current.token.kind in operators:
        result = Unary()
        result.kind = current.token.kind
        current.plus()
        temp = parseUnary()
        result.sub = temp.Expr
        return ParsedExp(result, temp.Extype)
    return parseOperand()

def parseMulDivMod() -> ParsedExp:
    operators: Set[Kind] = set([
        Kind.Star,
        Kind.Slash,
        Kind.Modulo,
    ])
    result = parseUnary()
    while current.token.kind in operators:
        temp = Arithmetic()
        temp.kind = current.token.kind
        current.plus()
        temp.left = result.Expr
        temp.right = (temp2 := parseUnary()).Expr
        if result.Extype == "Identifier" or temp2.Extype == "Identifier": result = ParsedExp(temp, "Identifier")
        elif result.Extype == "Number" and temp2.Extype == "Number": result = ParsedExp(temp, "Number")
        elif temp.kind == Kind.Star:
            if result.Extype == "Number" and temp2.Extype == "String": result = ParsedExp(temp, "String")
            elif result.Extype == "String" and temp2.Extype == "Number": result = ParsedExp(temp, "String")
            else: raise TypeError
    return result

def parsePlusMinus() -> ParsedExp:
    operators: Set[Kind] = set([
        Kind.Plus,
        Kind.Minus,
    ])
    result = parseMulDivMod()
    while current.token.kind in operators:
        temp = Arithmetic()
        temp.kind = current.token.kind
        current.plus()
        temp.left = result.Expr
        temp.right = (temp2 := parseMulDivMod()).Expr
        if result.Extype == "Identifier" or temp2.Extype == "Identifier": result = ParsedExp(temp, "identifier")
        elif result.Extype == "Number" and temp2.Extype == "Number": result = ParsedExp(temp, "Number")
        elif temp.kind == Kind.Plus and result.Extype == "String" and temp2.Extype == "String": result = ParsedExp(temp, "String")
        else: raise TypeError
    return result

def parseRelational() -> ParsedExp:
    operators: Set[Kind] = set([
        Kind.EqualEqual,
        Kind.NotEqual,
        Kind.LessThan,
        Kind.LessEqual,
        Kind.GreaterThan,
        Kind.GreaterEqual,
    ])
    result = parsePlusMinus()
    while current.token.kind in operators:
        temp = Relational()
        temp.kind = current.token.kind
        current.plus()
        temp.left = result.Expr
        temp.right = parsePlusMinus().Expr
        result = ParsedExp(temp, "Bool")
    return result
    

def parseAnd() -> ParsedExp:
    result = parseRelational()
    while skipCurrentIf(Kind.LogicalAnd):
        temp = And()
        temp.left = result.Expr
        temp.right = parseRelational().Expr
        result = ParsedExp(temp, "Bool")
    return result

def parseOr() -> ParsedExp:
    result = parseAnd()
    while skipCurrentIf(Kind.LogicalOr):
        temp = Or()
        temp.left = result.Expr
        temp.right = parseAnd().Expr
        result = ParsedExp(temp, "Bool")
    return result

def parseEqual() -> ParsedExp:
    result = parseOr()
    if current.token.kind != Kind.Equal:
        return result
    skipCurrent(Kind.Equal)
    if result.Extype == "Identifier":
        tempGV: GetVariable = result.Expr
        result = SetVariable()
        result.name = tempGV.name
        result.value = parseEqual().Expr
        return ParsedExp(result, "Identifier")
    if result.Extype == "Element":
        tempGE: GetElement = result.Expr
        result = SetElement()
        result.sub = tempGE.sub
        result.index = tempGE.index
        result.value = (tempV := parseEqual()).Expr
        return ParsedExp(result, tempV.Extype)
    raise RuntimeError("잘못된 대입 연산 식입니다.")

def parseExpression() -> ParsedExp:
    return parseEqual()

def parseVariable() -> Variable:
    result: Variable = Variable()
    skipCurrent(Kind.Variable)
    result.name = current.token.string
    skipCurrent(Kind.Identifier)
    skipCurrent(Kind.Equal)
    result.expression = parseExpression().Expr
    skipCurrent(Kind.SemiColon)
    return result

def parseFor() -> For:
    result: For = For()
    skipCurrent(Kind.For)
    result.variable = Variable()
    result.variable.name = current.token.string
    skipCurrent(Kind.Identifier)
    skipCurrent(Kind.Equal)
    result.variable.expression = parseExpression().Expr
    if not result.variable.expression: raise RuntimeError("for문에 초기화 식이 없습니다.")
    skipCurrent(Kind.Comma)
    result.condition = parseExpression().Expr
    if not result.condition: raise RuntimeError("for문에 조건식이 없습니다.")
    skipCurrent(Kind.Comma)
    result.expression = parseExpression().Expr
    if not result.expression: raise RuntimeError("for문에 증감식이 없습니다.")
    skipCurrent(Kind.LeftBrace)
    result.block = parseBlock()
    skipCurrent(Kind.RightBrace)
    return result

def parseIf() -> If:
    result: If = If(conditions = [], blocks = [], elseBlock = [])
    skipCurrent(Kind.If)
    def do():
        condition = parseExpression().Expr
        if not condition: raise RuntimeError("if문에 조건식이 없습니다.")
        result.conditions.append(condition)
        skipCurrent(Kind.LeftBrace)
        result.blocks.append(parseBlock())
        skipCurrent(Kind.RightBrace)
    do()
    while skipCurrentIf(Kind.Elif): do()
    if skipCurrentIf(Kind.Else):
        skipCurrent(Kind.LeftBrace)
        result.elseBlock = parseBlock()
        skipCurrent(Kind.RightBrace)
    return result

def parsePrint() -> Print:
    result: Print = Print(arguments = [])
    result.lineFeed = current.token.kind == Kind.PrintLine
    current.plus()
    if current.token.kind != Kind.SemiColon:
        result.arguments.append(parseExpression())
        while skipCurrentIf(Kind.Comma): result.arguments.append(parseExpression())
    skipCurrent(Kind.SemiColon)
    return result

def parseReturn() -> Return:
    result: Return = Return()
    skipCurrent(Kind.Return)
    result.expression = parseExpression().Expr
    if not result.expression: result.expression = NullLiteral()
    skipCurrent(Kind.SemiColon)
    return result

def parseBreak() -> Break:
    result: Break = Break()
    skipCurrent(Kind.Break)
    skipCurrent(Kind.SemiColon)
    return result

def parseContinue() -> Continue:
    result: Continue = Continue()
    skipCurrent(Kind.Continue)
    skipCurrent(Kind.SemiColon)
    return result

def parseExpressionStatement() -> ExpressionStatement:
    result: ExpressionStatement = ExpressionStatement()
    result.expression = parseExpression().Expr
    skipCurrent(Kind.SemiColon)
    return result

def parseBlock() -> List[Statement]:
    result: List[Statement] = []
    while current.token.kind != Kind.RightBrace:
        K = current.token.kind
        if K == Kind.EndOfList:                         raise RuntimeError(f"{current.token} 잘못된 구문입니다.")
        elif K == Kind.Variable:                        result.append(parseVariable())
        elif K == Kind.For:                             result.append(parseFor())
        elif K == Kind.If:                              result.append(parseIf())
        elif K == Kind.Print or K == Kind.PrintLine:    result.append(parsePrint())
        elif K == Kind.Return:                          result.append(parseReturn())
        elif K == Kind.Break:                           result.append(parseBreak())
        elif K == Kind.Continue:                        result.append(parseContinue())
        else:                                           result.append(parseExpressionStatement())
    return result

def parseFunction() -> Function:
    result: Function = Function(parameters = [])
    skipCurrent(Kind.Function)
    result.name = current.token.string
    skipCurrent(Kind.Identifier)
    skipCurrent(Kind.LeftParen)
    if current.token.kind != Kind.RightParen:
        result.parameters.append(current.token.string)
        skipCurrent(Kind.Identifier)
        while(skipCurrentIf(Kind.Comma)):
            result.parameters.append(current.token.string)
            skipCurrent(Kind.Identifier)
    skipCurrent(Kind.RightParen)
    skipCurrent(Kind.LeftBrace)
    result.block = parseBlock()
    skipCurrent(Kind.RightBrace)
    return result

def parse(tokens: List[Token]) -> Program:
    global current
    result: Program = Program(functions = [])
    current = Current(tokens)
    while current.token != Kind.EndOfList:
        K = current.token.kind
        if K == Kind.Function:
            result.functions.append(parseFunction())
        else:
            raise RuntimeError(f"{current.token} 잘못된 구문입니다.")
    return result