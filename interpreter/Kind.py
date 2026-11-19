from enum import Enum, auto
from typing import Dict

#토큰의 종류(Kind)를 나열한 객체(열거체)
class Kind(Enum):
    Unknown = auto()
    EndOfList = auto()
    NullLiteral = auto()
    TrueLiteral = auto()
    FalseLiteral = auto()
    NumberLiteral = auto()
    StringLiteral = auto()
    Identifier = auto()

    Function = auto()
    Return = auto()
    Variable = auto()
    For = auto()
    Break = auto()
    Continue = auto()
    If = auto()
    Elif = auto()
    Else = auto()
    Print = auto()
    PrintLine = auto()

    LogicalAnd = auto()
    LogicalOr = auto()
    Equal = auto()
    Plus = auto()
    Minus = auto()
    Star = auto()
    Slash = auto()
    Modulo = auto()
    EqualEqual = auto()
    NotEqual = auto()
    LessThan = auto()
    LessEqual = auto()
    GreaterThan = auto()
    GreaterEqual = auto()

    Dot = auto()
    Comma = auto()
    Colon = auto()
    SemiColon = auto()
    LeftParen = auto()
    RightParen = auto()
    LeftBrace = auto()
    RightBrace = auto()
    LeftBracket = auto()
    RightBracket = auto()

#문자열 Kind의 딕셔너리
stringToKind: Dict[str, Kind] = {
    "#unknown": Kind.Unknown,
    "#EndOfList": Kind.EndOfList,

    "null": Kind.NullLiteral,
    "true": Kind.TrueLiteral,
    "false": Kind.FalseLiteral,
    "#Number": Kind.NumberLiteral,
    "#String": Kind.StringLiteral,
    "#identifier": Kind.Identifier,

    "function": Kind.Function,
    "return": Kind.Return,
    "var": Kind.Variable,
    "for": Kind.For,
    "break": Kind.Break,
    "continue": Kind.Continue,
    "if": Kind.If,
    
    "elif": Kind.Elif,
    "else": Kind.Else,
    "print": Kind.Print,
    "printLine": Kind.PrintLine,

    "and": Kind.LogicalAnd,
    "or": Kind.LogicalOr,

    "=": Kind.Equal,

    "+": Kind.Plus,
    "-": Kind.Minus,
    "*": Kind.Star,
    "/": Kind.Slash,
    "%": Kind.Modulo,
    
    "==": Kind.EqualEqual,
    "!=": Kind.NotEqual,
    ">": Kind.GreaterThan,
    ">=": Kind.GreaterEqual,
    "<": Kind.LessThan,
    "<=": Kind.LessEqual,

    ".": Kind.Dot,
    ",": Kind.Comma,
    ":": Kind.Colon,
    ";": Kind.SemiColon,
    "(": Kind.LeftParen,
    ")": Kind.RightParen,
    "{": Kind.LeftBrace,
    "}": Kind.RightBrace,
    "[": Kind.LeftBracket,
    "]": Kind.RightBracket,
}

#문자열을 받아 Kind를 반환하는 함수
def toKind(string: str) -> Kind:
    if string in stringToKind:
        return stringToKind[string]
    return Kind.Unknown