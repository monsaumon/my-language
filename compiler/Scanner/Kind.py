from enum import Enum, auto
from typing import Dict

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
    Assignment = auto()
    Add = auto()
    Subtract = auto()
    Multiply = auto()
    Divide = auto()
    Modulo = auto()
    Equal = auto()
    NotEqual = auto()
    LessThan = auto()
    LessEqual = auto()
    GreaterThan = auto()
    GreaterEqual = auto()
    
    Comma = auto()
    Colon = auto()
    SemiColon = auto()
    LeftParen = auto()
    RightParen = auto()
    LeftBrace = auto()
    RightBrace = auto()
    LeftBracket = auto()
    RightBracket = auto()

_stringToKind: Dict[str, Kind] = {
    "#Unknown": Kind.Unknown,
    "#EndOfList": Kind.EndOfList,

    "null": Kind.NullLiteral,
    "true": Kind.TrueLiteral,
    "false": Kind.FalseLiteral,
    "#Number": Kind.NumberLiteral,
    "#String": Kind.StringLiteral,
    "#Identifier": Kind.Identifier,

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
    "printline": Kind.PrintLine,

    "and": Kind.LogicalAnd,
    "or": Kind.LogicalOr,

    "=": Kind.Assignment,

    "+": Kind.Add,
    "-": Kind.Subtract,
    "*": Kind.Multiply,
    "/": Kind.Divide,
    "%": Kind.Modulo,

    "==": Kind.Equal,
    "!=": Kind.NotEqual,
    "<": Kind.LessThan,
    ">": Kind.GreaterThan,
    "<=": Kind.LessEqual,
    ">=": Kind.GreaterEqual,

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

_kindToString: Dict[Kind, str] = {v:k for k,v in _stringToKind.items()}

def toKind(string: str) -> Kind:
    if string in _stringToKind.keys():
        return _stringToKind.get(string)
    return Kind.Unknown

def toString(type_: Kind) -> str:
    if type_ in _kindToString.keys():
        return _kindToString.get(type_)
    return ""