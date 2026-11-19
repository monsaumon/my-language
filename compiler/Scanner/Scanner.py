from typing import List
from enum import Enum, auto

from Scanner.Token import Token
from Scanner.Kind import Kind, toKind

class _CharType(Enum):
    Unknown = auto()
    WhiteSpace = auto()
    NumberLiteral = auto()
    StringLiteral = auto()
    IdentifierAndKeyword = auto()
    OperatorAndPunctuator = auto()

class _Current:
    def __init__(self, sourceCode: str):
        self.sourceCode = sourceCode
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < len(self.sourceCode):
            return self.sourceCode[self.index]
        else:
            raise StopIteration
    
    def __add__(self, other):
        self.index += other
        return iter(self)
    
    def __sub__(self, other):
        self.index -= other
        return iter(self)

_current: _Current

def _isCharBetween(lhs: str, center: str, rhs: str) -> bool:
    if len(lhs) != 1 or len(center) != 1 or len(rhs) != 1:
        raise TypeError
    return ord(lhs) <= ord(center) <= ord(rhs)

def _scanNumberLiteral() -> Token:
    global _current
    string: str = ''
    while _isCharType(ch := next(_current), _CharType.NumberLiteral):
        string += ch
        _current += 1
    if next(_current) == '.':
        string += next(_current)
        _current += 1
        while _isCharType(ch := next(_current), _CharType.NumberLiteral):
            string += ch
            _current += 1
    return Token(Kind.NumberLiteral, string)

def _scanStringLiteral() -> Token:
    global _current
    string: str = ''
    _current += 1
    while _isCharType(ch := next(_current), _CharType.StringLiteral):
        string += ch
        _current += 1
    if next(_current) != '\'':
        raise SyntaxError("string not completed")
    _current += 1
    return Token(Kind.StringLiteral, string)

def _scanIdentifierAndKeyword() -> Token:
    global _current
    string: str = ''
    while _isCharType(ch := next(_current), _CharType.IdentifierAndKeyword):
        string += ch
        _current += 1
    kind = toKind(string)
    if kind == Kind.Unknown:
        kind = Kind.Identifier
    return Token(kind, string)

def _scanOperatorAndPunctuator() -> Token:
    global _current
    string: str = ''
    while _isCharType(ch := next(_current), _CharType.OperatorAndPunctuator):
        string += ch
        _current += 1
    while string and toKind(string) == Kind.Unknown:
        string = string[:-1]
        _current -= 1
    if not string:
        raise RuntimeError(f"character not allowed: {next(_current)}")
    return Token(toKind(string), string)

def _getCharType(c: str) -> _CharType:
    if c == ' ' or c == '\t' or c == '\r' or c == '\n':
        return _CharType.WhiteSpace
    if _isCharBetween('0', c, '9'):
        return _CharType.NumberLiteral
    if c == '\'':
        return _CharType.StringLiteral
    if _isCharBetween('a', c, 'z') or _isCharBetween('A', c, 'Z'):
        return _CharType.IdentifierAndKeyword
    if 33 <= ord(c) <= 47 and c != '\'' or \
       58 <= ord(c) <= 64 or \
       91 <= ord(c) <= 96 or \
       123 <= ord(c) <= 126:
        return _CharType.OperatorAndPunctuator
    return _CharType.Unknown

def _isCharType(c: str, type_: _CharType) -> bool:
    if type_ == _CharType.NumberLiteral:
        return _isCharBetween('0', c, '9')
    elif type_ == _CharType.StringLiteral:
        return 32 <= ord(c) <= 126 and c != '\''
    elif type_ == _CharType.IdentifierAndKeyword:
        return _isCharBetween('0', c, '9') or \
               _isCharBetween('a', c, 'z') or \
               _isCharBetween('A', c, 'Z')
    elif type_ == _CharType.OperatorAndPunctuator:
        return 33 <= ord(c) <= 47 and c != '\'' or \
               58 <= ord(c) <= 64 or \
               91 <= ord(c) <= 96 or \
               123 <= ord(c) <= 126
    else:
        return False

def scan(sourceCode: str) -> List[Token]:
    global _current
    result: List[Token] = []
    sourceCode += '\000'
    _current = iter(_Current(sourceCode))
    while (ch := next(_current)) != '\000':
        if (charType := _getCharType(ch)) == _CharType.WhiteSpace:
            _current += 1
        elif charType == _CharType.NumberLiteral:
            result.append(_scanNumberLiteral())
        elif charType == _CharType.StringLiteral:
            result.append(_scanStringLiteral())
        elif charType == _CharType.IdentifierAndKeyword:
            result.append(_scanIdentifierAndKeyword())
        elif charType == _CharType.OperatorAndPunctuator:
            result.append(_scanOperatorAndPunctuator())
        else:
            raise RuntimeError(f"character not allowed: {ch}")
    result.append(Token(Kind.EndOfList, '\000'))
    return result